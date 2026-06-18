# sources/distributed-fs/ceph-client/drivers/pwm/pwm-samsung.c

## Purpose

`pwm-samsung.c` supports Samsung S3C/S5P/Exynos timer PWM blocks. It exposes channels declared output-capable by variant data or DT and coordinates with the Samsung clocksource driver through a shared lock.

## APIs, control flow, and state

`struct samsung_pwm_chip` stores variant data, inverter and disabled masks, MMIO, clocks, and per-channel caches. `pwm_samsung_calc_tin()` selects external TCLK or divided base clock. `__pwm_samsung_config()` writes down-counter `TCNTB/TCMPB`, handles the missing 0% duty by forcing at least one tick, and manually updates after 100% transitions. Apply disables for polarity changes, rejects periods above one second, configures, and enables if needed. Resume restores cached period/duty, inverter, and disabled state.

State is split between hardware registers and cached channel/inverter/disabled data required for resume.

## Dependencies and integration points

The driver uses `<clocksource/samsung_pwm.h>`, OF compatibles, optional `samsung,pwm-outputs`, `timers` clock, optional `pwm-tclk0/1`, and the PWM core.

## Risks and test signals

Hardware polarity is inverted relative to logical normal. 0% is approximated, and only <=1s periods are accepted. Shared timer registers require locking. Test variant widths, TCON channel gap, output mask validation, polarity toggles, 0%/100%, external clock fallback, and resume.
