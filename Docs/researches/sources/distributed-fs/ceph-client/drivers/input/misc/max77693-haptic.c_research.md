# sources/distributed-fs/ceph-client/drivers/input/misc/max77693-haptic.c

Purpose: ff-memless haptic driver for MAX77693/MAX77705/MAX77843, converting rumble magnitudes to PWM duty and PMIC haptic control.

Important APIs/types/functions: MFD regmaps, PWM, regulator, workqueue, and input FF. `struct max77693_haptic` tracks variant, regmaps, input, PWM, regulator, enable/suspend flags, magnitude/duty, motor type, pulse mode, and work. Key routines configure duty, bias, haptic registers, low-system bit, enable/disable, work, FF callback, open/close, probe, and PM.

Control flow: probe selects variant regmap, gets PWM and `haptic` regulator, creates EV_FF/FF_RUMBLE memless input, registers it, and stores state. Open enables MAX77843 bias and regulator. FF callback stores strong or weak magnitude, computes PWM duty from period, and schedules work. Work stops on zero, updates duty if active, or enables PWM, low-system bit, and haptic config. Close cancels work and powers down. Suspend disables active haptics and resume restores if needed.

State/persistence: `enabled`, `suspend_state`, `magnitude`, and `pwm_duty` are runtime state; hardware is programmed on enable/update.

Dependencies/integration: platform/OF IDs for all variants, parent MFD data, PWM/regulator resources, input FF.

Risks: limited locking around work state. Disable failures can leave hardware enabled. Duty computation centers around half period and needs hardware validation.

Test signals: all variants, resource failures, open/close sequence, strong/weak/zero rumble, repeated updates, suspend/resume, and FF registration.
