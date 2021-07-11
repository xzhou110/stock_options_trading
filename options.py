from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

from varname import nameof
import math

class Options:
    def __init__(self, ticker, expiration, action, strike, premium, curr_price, imp_vol, min_price=0, max_price=100):
        
        # extract key info from experiration date
        self.exp_date = datetime.strptime(expiration, '%Y-%m-%d')
        self.exp_date_yr = self.exp_date.year
        self.exp_date_mon = self.exp_date.month
        self.exp_date_day = self.exp_date.day
        
        # format month and date as double digits
        if self.exp_date_mon < 10:
            self.exp_date_mon = '0' + str(self.exp_date_mon)
        if self.exp_date_day < 10:
            self.exp_date_day = '0' + str(self.exp_date_day)
        
        # calculate month from now
        curr_date = datetime.now()
        self.days_from_now = (self.exp_date - curr_date).days
        self.months_from_now = (self.exp_date.year - curr_date.year)*12 + (self.exp_date.month - curr_date.month)
        
        self.ticker = ticker
        self.expiration = expiration
        self.exp_date_trans = str(self.exp_date_yr)[-2:] + str(self.exp_date_mon) + str(self.exp_date_day)
        self.action = action
        self.strike = strike
        self.premium = premium
        self.curr_price = curr_price
        self.imp_vol = imp_vol
        self.min_price = min_price
        self.max_price = max_price
        self.payoff = [] 
        self.weighted_payoff = []
        self.return_ = []
        self.price_prob = {}
        self.pred_price_min = -99
        self.pred_price_max = -99
        self.breakeven =  -99
        self.payoff_min = -99
        self.payoff_max = -99
        self.return_min = -99
        self.return_max = -99
        self.avg_return = -99
             
        if action == 'buy':
            self.cost = round(premium, 1)
        elif action == 'sell':
            self.cost = round(-premium,1)

    def predict_price(self):

        self.std_dev = self.curr_price * self.imp_vol * np.sqrt(self.months_from_now/12)

        num_reps = 1000
        num_iter = 1000
        possible_prices = []

        # Generate all possible prices
        for i in range(num_iter):
            prices = np.random.normal(self.curr_price, self.std_dev, num_reps)
            prices = [int(x) if x>=0 else x for x in prices ]
            possible_prices.extend(prices)

        # count all the prices and create a dictionary
        price_counter = {}
        for price in possible_prices:
            if price_counter.get(price):
                price_counter[price]+=1
            else:
                price_counter[price] = 1 

        # Create a list of probabilities
        total_count = len(possible_prices)
        self.pred_price_min = round(max(min(possible_prices),0),1)
        self.pred_price_max = round(max(possible_prices),1)

        price_prob = [] 

        for price in range(self.min_price, self.max_price+1):
            if price_counter.get(price):
                prob = price_counter[price]/total_count
                price_prob.append(prob)
                self.price_prob[price] = prob
            else:
                price_prob.append(0)
                self.price_prob[price] = 0
        
    def calc_payoff(self):
        for price in range (self.min_price, self.max_price+1):
            earn = self.calc_profit(price)
            weighted_earn = earn * self.price_prob[price]
            self.payoff.append(earn)
            self.weighted_payoff.append(weighted_earn)
        
        try: self.breakeven = list(self.payoff).index(0)
        except: 
            minimum = min(self.payoff, key = abs)
            self.breakeven = list(self.payoff).index(minimum)
            
        self.breakeven  = round(self.breakeven,1)
        self.payoff_min = round(min(self.payoff),1)
        self.payoff_max = round(max(self.payoff),1)
        self.avg_payoff = round(sum(self.weighted_payoff),3)
        
    def calc_return(self):
        for payoff in self.payoff:
            return_ = round(payoff/self.cost,3)
            self.return_.append(return_)
        self.return_min = round(self.payoff_min/self.cost,3)
        self.return_max = round(self.payoff_max/self.cost,3)
        self.avg_return = round(self.avg_payoff/self.cost,3)
        self.avg_annualized_return = round(pow(1 + self.avg_return, 365/self.days_from_now)-1, 3)
    
    def create_graph(self):

        max_x = self.max_price
        min_x = self.min_price
        interval = (max_x - min_x)/10
        
        max_y = self.payoff_max + interval
        min_y = self.payoff_min - 5*interval
        
        x = np.arange(min_x, max_x +1, 1)
        y = self.payoff
        
        print('Strategy:', self.name, 
#               '\nPrice Range:[', self.pred_price_min, ',', self.pred_price_max,
              '\nPayoff Range:[', self.payoff_min, ',', self.payoff_max, 
              '];Breakeven Price:', self.breakeven,
              ';Cost:', self.cost,
               ';Return Range:[', "{:.1%}".format(self.return_min), ',', "{:.1%}".format(self.return_max), ']',
              '; Avg. Return:',"{:.1%}".format(self.avg_return),
              '; Avg. Annual Return:',"{:.1%}".format(self.avg_annualized_return),
              '\n'
             )
        
        plt.xlabel('Stock Price at Expiration')
        plt.ylabel('Payoff')
        plt.xticks(np.arange(min_x, max_x+interval, interval))
        plt.yticks(np.arange(min_y, max_y, interval))
        
        plt.xlim (min_x, max_x) # limit range of x to show
        plt.ylim (min_y, max_y)
    #     plt.legend(loc = 'upper left')
        plt.plot(x, y, label = self.name )
        plt.legend()
        
    def create_graph_stock_only(self):
        max_x = self.max_price
        min_x = self.min_price
        interval = (max_x - min_x)/10
        
        max_y = self.payoff_max + interval
        min_y = self.payoff_min - 5*interval
        
        current_price = round(self.curr_price,1)
        
        x = np.arange(min_x, max_x+1, 1)
        y = [a - current_price for a in x]
        
        payoff_min = round(min(x) - current_price,1)
        payoff_max = round(max(x) - current_price, 1)
        cost = round(current_price,1)
        return_min = round(payoff_min/cost,3)
        return_max = round(payoff_max/cost,3)
        

        print('Strategy: Stock Only', 
              '\nPrice Range:[', self.pred_price_min, ',', self.pred_price_max,
              '];Payoff Range:[', payoff_min, ',', payoff_max, 
              '];Breakeven Price:', current_price,
              'Cost:', cost,
              ';Return Range:[', "{:.1%}".format(return_min), ',', "{:.1%}".format(return_max), ']'
#               '; Average Return:',"{:.1%}".format(self.avg_return)
             )
        plt.xticks(np.arange(0, max_x+interval, interval))
        plt.yticks(np.arange(min_y , max_y, interval))
    #     plt.legend(loc = 'upper left')
        plt.xlim (min_x, max_x)
        plt.ylim (min_y, max_y)
        plt.plot(x, y, label = 'Stock Only' )
        plt.legend()
        

        
class Call(Options):
    def __init__(self, ticker, expiration, action, strike, premium, curr_price, imp_vol, min_price=0, max_price=100):
        super().__init__(ticker, expiration, action, strike, premium, curr_price, imp_vol, min_price, max_price)
        self.name = self.ticker + self.exp_date_trans + 'C'+ str(self.strike)
        self.type = 'call'
        self.predict_price()
        self.calc_payoff()
        self.calc_return()
        
        
    def calc_profit(self, price):
        if self.action == 'buy':
            if price <= self.strike:
                profit =  -self.premium
            elif price > self.strike:
                profit = price - self.strike - self.premium
            
        elif self.action == 'sell':
            if price <= self.strike:
                profit = self.premium
            elif price > self.strike:
                profit = - price + self.strike + self.premium
                
        return profit
    


class Put(Options):
    def __init__(self, ticker, expiration, action, strike, premium, curr_price, imp_vol, min_price=0, max_price=100):
        super().__init__(ticker, expiration, action, strike, premium, curr_price, imp_vol, min_price, max_price)
        self.name = self.ticker + self.exp_date_trans + 'P'+ str(self.strike)
        self.type = 'put'
        self.predict_price()
        self.calc_payoff()
        self.calc_return()
        
    def calc_profit(self, price):
        if self.action == 'buy':
            if price <= self.strike:
                profit = self.strike - price - self.premium
            elif price > self.strike:
                profit = - self.premium
            
        elif self.action == 'sell':
            if price <= self.strike:
                profit = - self.strike + price + self.premium
            elif price > self.strike:
                profit = self.premium
        return profit
    
    

class OptionsStrategy:
    def __init__(self, options_list, coefficients = []):
        self.ticker = options_list[0].ticker
        self.exp_date_trans = options_list[0].exp_date_trans
        self.min_price = options_list[0].min_price
        self.max_price = options_list[0].max_price
        self.pred_price_min = options_list[0].pred_price_min
        self.pred_price_max = options_list[0].pred_price_max
        self.days_from_now = options_list[0].days_from_now
        self.months_from_now = options_list[0].months_from_now
        self.curr_price = options_list[0].curr_price
        self.options_list = options_list
        self.coefficients = coefficients
        
        self.payoff = []
        self.weighted_payoff = []
        self.return_ = []
        self.breakeven = -99
        self.payoff_min = -99
        self.payoff_max = -99
        self.return_min = -99
        self.return_max = -99
        self.avg_return = -99
        self.avg_payoff = -99

        self.create_name()
        self.calc_payoff()
        self.calc_return()
    
    def create_name(self):
        self.name = self.ticker + self.exp_date_trans
        for option in self.options_list:
            # Add action, option type, strike price to combo name
            if option.action == 'buy':
                self.name+='_B'
            elif option.action == 'sell':
                self.name+='_S'
                
            if option.type == 'call':
                self.name+='C'
            elif option.type == 'put':
                self.name+='P'
            
            self.name+=str(option.strike)
            
    def calc_payoff(self):
        self.cost = 0
        data_shape = len(self.options_list[0].payoff)
        if len(self.coefficients) == 0:
            self.coefficients = np.ones(data_shape)
            
        for index, option in enumerate(self.options_list):
            self.cost+=self.coefficients[index] * option.cost
            if len(self.payoff)==0:
                self.payoff = self.coefficients[index] * np.array(option.payoff) 
                self.weighted_payoff = self.coefficients[index] * np.array(option.weighted_payoff) 
            else:
                self.payoff = np.add(self.payoff, 
                                     self.coefficients[index] * np.array(option.payoff)
                                    )
                self.weighted_payoff = np.add(self.weighted_payoff, 
                                     self.coefficients[index] * np.array(option.weighted_payoff)
                                    )
        self.cost = round(self.cost, 1)
            
        
        # calculate breakeven, payoff_min, payoff_max
        try: self.breakeven = list(self.payoff).index(0)
        except: 
            minimum = min(self.payoff, key = abs)
            self.breakeven = list(self.payoff).index(minimum)
            
        self.breakeven  = round(self.breakeven,1)
        self.payoff_min = round(min(self.payoff),1)
        self.payoff_max = round(max(self.payoff),1)
        self.avg_payoff = round(sum(self.weighted_payoff),3)
        
    
    def calc_return(self):
        for payoff in self.payoff:
            return_ = round(payoff/self.cost,3)
            self.return_.append(return_)
        self.return_min = round(self.payoff_min/self.cost,3)
        self.return_max = round(self.payoff_max/self.cost,3)
        self.avg_return = round(self.avg_payoff/self.cost,3)
        self.avg_annualized_return = round(pow(1 + self.avg_return, 365/self.days_from_now)-1, 3)
        
    
    def create_graph(self):

        max_x = self.max_price
        min_x = self.min_price
        interval = (max_x - min_x)/10
        
        max_y = self.payoff_max + interval
        min_y = self.payoff_min - 5*interval
        
        x = np.arange(min_x, max_x +1, 1)
        y = self.payoff
        
        print('Strategy:', self.name, 
#               '\nPrice Range:[', self.pred_price_min, ',', self.pred_price_max,
              '\nPayoff Range:[', self.payoff_min, ',', self.payoff_max, 
              '];Breakeven Price:', self.breakeven,
              ';Cost:', self.cost,
               ';Return Range:[', "{:.1%}".format(self.return_min), ',', "{:.1%}".format(self.return_max), ']',
              '; Avg. Return:',"{:.1%}".format(self.avg_return),
              '; Avg. Annual Return:',"{:.1%}".format(self.avg_annualized_return),
              '\n'
             )
        
        plt.xlabel('Stock Price at Expiration')
        plt.ylabel('Payoff')
        plt.xticks(np.arange(min_x, max_x+interval, interval))
        plt.yticks(np.arange(min_y, max_y, interval))
        
        plt.xlim (min_x, max_x) # limit range of x to show
        plt.ylim (min_y, max_y)
    #     plt.legend(loc = 'upper left')
        plt.plot(x, y, label = self.name )
        plt.legend()
        
    def create_graph_stock_only(self):
        max_x = self.max_price
        min_x = self.min_price
        interval = (max_x - min_x)/10
        
        max_y = self.payoff_max + interval
        min_y = self.payoff_min - 5*interval
        
        current_price = round(self.curr_price,1)
        
        x = np.arange(min_x, max_x+1, 1)
        y = [a - current_price for a in x]
        
        payoff_min = round(min(x) - current_price,1)
        payoff_max = round(max(x) - current_price, 1)
        cost = round(current_price,1)
        return_min = round(payoff_min/cost,3)
        return_max = round(payoff_max/cost,3)
        

        print('Strategy: Stock Only', 
              '\nPrice Range:[', self.pred_price_min, ',', self.pred_price_max,
              '];Payoff Range:[', payoff_min, ',', payoff_max, 
              '];Breakeven Price:', current_price,
              'Cost:', cost,
              ';Return Range:[', "{:.1%}".format(return_min), ',', "{:.1%}".format(return_max), ']'
#               '; Average Return:',"{:.1%}".format(self.avg_return)
             )
        plt.xticks(np.arange(0, max_x+interval, interval))
        plt.yticks(np.arange(min_y , max_y, interval))
    #     plt.legend(loc = 'upper left')
        plt.xlim (min_x, max_x)
        plt.ylim (min_y, max_y)
        plt.plot(x, y, label = 'Stock Only' )
        plt.legend()