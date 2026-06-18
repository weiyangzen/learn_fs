# sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiehrpwm.c

## Purpose

`pwm-tiehrpwm.c` drives TI EHRPWM modules with two outputs sharing one time-base period. It supports normal/inverted polarity, action-qualifier output control, TBCLK gating, and suspend context.

## APIs, control flow, and state

`struct ehrpwm_pwm_chip` stores clock rate, MMIO, per-channel requested period cycles, TBCLK, and saved registers. `set_prescale_div()` searches prescaler encodings. `ehrpwm_pwm_config()` enforces equal period across channels, computes cycles, programs TBCTL/TBPRD/CMPA/CMPB/AQCTL, and handles over-period duty as constant output. Enable releases software force and enables TBCLK; disable force-lows output and disables TBCLK/runtime PM. `.free` clears period ownership.

`period_cycles[]` enforces sharing; suspend context restores registers.

## Dependencies and integration points

It binds `ti,am3352-ehrpwm` and `ti,am33xx-ehrpwm`, uses `fck`, `tbclk`, runtime PM, MMIO, and PWM core.

## Risks and test signals

Outputs must share period. The legacy clock fallback checks `ti,am33xx-ecap`, likely a copy/paste typo in this EHRPWM driver. Runtime PM and TBCLK refcounts are subtle. Test same/conflicting periods, `.free`, polarity, full duty, suspend/resume, and clock-binding paths.
