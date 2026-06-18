# sources/distributed-fs/ceph-client/drivers/input/misc/pwm-vibra.c

## Purpose
`pwm-vibra.c` implements a force-feedback rumble device driven by one required PWM, an optional direction PWM, an optional enable GPIO, and a `vcc` regulator.

## Important APIs, Types, and Functions
`struct pwm_vibrator` tracks the input device, enable GPIO, main and direction PWMs, regulator, work item, current magnitude, direction duty cycle, and regulator state. `pwm_vibrator_start()` enables power/GPIO and applies PWM duty from rumble strength. `pwm_vibrator_stop()` disables direction/main PWM, GPIO, and regulator. `pwm_vibrator_play_effect()` selects strong or weak rumble magnitude and schedules work. `pwm_vibrator_probe()` configures hardware resources and creates a memless FF device.

## Control Flow
Probe allocates state and input, gets `vcc`, optional `enable` GPIO, main `enable` PWM, initializes it off, optionally obtains a `direction` PWM, initializes it off, and reads `direction-duty-cycle-ns` or defaults to half the direction period. It registers `FF_RUMBLE` through `input_ff_create_memless()`. Playback stores the selected magnitude and schedules work. The worker starts hardware if level is nonzero and stops it otherwise. Close cancels work and stops hardware. Suspend stops active vibration; resume restarts if a nonzero level remains.

## State and Persistence Behavior
The last requested `level` persists in memory and is used to restart after resume. `vcc_on` tracks regulator balance. Hardware PWM duty, enable GPIO, and regulator state persist until `start`, `stop`, suspend, close, or removal changes them.

## Dependencies and Integration Points
The driver depends on PWM, regulator, GPIO descriptor, platform/OF properties, and input force-feedback core. Board integration names the main PWM `enable`, optional PWM `direction`, optional GPIO `enable`, and regulator `vcc`. Userspace sees a memless `pwm-vibrator` FF rumble device.

## Risks and Edge Cases
If applying the main PWM fails after the regulator and GPIO are enabled, `pwm_vibrator_start()` returns without unwinding those resources. If direction PWM apply fails, only the main PWM is disabled, while GPIO/regulator remain on until a later stop. Direction PWM absence is treated as `-ENODATA`; other errors fail probe except defer. Strength updates are not mutex-protected against suspend/close, relying on input and workqueue ordering.

## Test Signals
Tests should cover strong/weak rumble selection, zero stop, optional direction PWM present/absent/deferred, direction duty property, enable GPIO polarity, regulator and PWM error injection, suspend/resume during active rumble, close while work is pending, and repeated playback cycles for regulator balance.
