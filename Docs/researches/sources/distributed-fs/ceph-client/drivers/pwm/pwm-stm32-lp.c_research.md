# sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32-lp.c

## Purpose

`pwm-stm32-lp.c` drives STM32 low-power timer PWM outputs. It supports single-output LPTIMERs and instances with dedicated capture/compare channels, where channels share prescaler and ARR.

## APIs, control flow, and state

`struct stm32_pwm_lp` stores parent clock, regmap, and CC channel count. `stm32_pwm_lp_update_allowed()` checks whether shared enable/prescaler/ARR can change. `stm32_pwm_lp_compare_channel_apply()` changes CC enable/polarity and observes required delays. Apply computes prescaler/ARR/CMP, enforces sharing constraints, enables clock/timer, writes registers, polls write-complete flags, enables CC output, and starts continuous mode. `get_state()` reads CR/CFGR/ARR/CMP/CCMR1 and syncs clock refcount for active boot state.

No shadow state is kept; parent LPTIMER registers are source of truth.

## Dependencies and integration points

It is an `stm32-lptimer` MFD child using parent regmap/clock, pinctrl PM states, and the PWM core.

## Risks and test signals

Multiple CC outputs cannot independently change ARR/prescaler. Boundary behavior for 0%/100% needs hardware validation. Suspend refuses active outputs. Test single vs multi-CC, polarity changes with delay, `-EBUSY`, write-poll timeout, boot get_state, and suspend/resume.
