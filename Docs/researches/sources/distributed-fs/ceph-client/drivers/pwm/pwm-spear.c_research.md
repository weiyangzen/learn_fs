# sources/distributed-fs/ceph-client/drivers/pwm/pwm-spear.c

## Purpose

`pwm-spear.c` drives ST SPEAr PWM controllers with four channels. Each channel has control, duty, and period registers; SPEAr1340 also needs a master enable bit.

## APIs, control flow, and state

`struct spear_pwm_chip` stores MMIO and prepared clock. `spear_pwm_config()` searches prescalers until 16-bit period and duty counts fit, temporarily enables the clock, and writes prescale/duty/period. Enable sets `PWMCR_PWM_ENABLE` and leaves the clock enabled; disable clears it and disables the clock. Apply supports only normal polarity.

No software shadow exists and no `.get_state` is implemented.

## Dependencies and integration points

It binds `st,spear320-pwm` and `st,spear1340-pwm`, uses MMIO, a clock, and the PWM framework.

## Risks and test signals

Enabled 0% duty is rejected because duty count must be at least 1. Boot state is invisible. Test all channels, SPEAr1340 master enable, min/max counts, polarity rejection, clock balance, and prescaler transitions.
