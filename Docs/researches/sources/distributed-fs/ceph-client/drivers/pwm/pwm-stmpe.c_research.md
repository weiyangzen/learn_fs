# sources/distributed-fs/ceph-client/drivers/pwm/pwm-stmpe.c

## Purpose

`pwm-stmpe.c` drives three PWM outputs on STMPE2401/STMPE2403 expanders by writing instruction programs into PWM instruction registers. STMPE1601 is rejected.

## APIs, control flow, and state

`struct stmpe_pwm` stores the parent STMPE device and `last_duty`. Enable/disable toggle bits in `STMPE24XX_PWMCS`. `stmpe_24xx_pwm_config()` disables active PWM, sets alternate pin function, maps duty to 8 bits, emits STMPE2403 direct `LOAD` programs or STMPE2401 ramp/branch programs, writes three 16-bit instructions bytewise, re-enables if needed, and sleeps 200 ms.

Persistent state is in STMPE registers plus `last_duty`, which is shared across all channels.

## Dependencies and integration points

The driver depends on STMPE MFD helpers for register access, block enable, and alternate functions, and registers with the PWM core using `module_platform_driver_probe()`.

## Risks and test signals

`last_duty` is not per-channel and can couple unrelated outputs. Apply is slow and disables output during reprogramming. Period support is only approximate. Test both parts, all channels, cross-channel duty changes, 0%/100%, altfunc setup, partial write failures, and remove block disable.
