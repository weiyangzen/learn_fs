# sources/distributed-fs/ceph-client/drivers/video/backlight/pwm_bl.c

Purpose: generic PWM backlight driver used by DT and legacy platform-data boards. It converts logical backlight brightness into PWM duty cycle and sequences optional regulator and enable GPIO resources.

Important APIs/types/functions: `struct pwm_bl_data` holds PWM, regulator, GPIO, brightness tables, scale, delays, and legacy notify hooks. Core functions are `pwm_backlight_update_status()`, `compute_duty_cycle()`, `pwm_backlight_power_on/off()`, `pwm_backlight_parse_dt()`, `pwm_backlight_brightness_default()`, `pwm_backlight_initial_power_state()`, and PM/remove/shutdown handlers. It registers `struct backlight_ops` with `backlight_device_register()`.

Control flow: probe obtains platform data or parses DT, runs optional init, acquires GPIO/regulator/PWM, applies initial PWM state, builds brightness scaling from explicit levels, a generated CIE1931 table, or plain max brightness, registers the backlight, sets default brightness, infers initial power from hardware state and phandle presence, and calls `backlight_update_status()`. Runtime updates call legacy notifiers, apply PWM duty, then enable or disable power resources. Suspend powers off and disables PWM; resume replays backlight state.

State and persistence: runtime `enabled` tracks regulator/GPIO ownership rather than raw hardware state. Brightness tables are devm-managed. Hardware PWM/regulator/GPIO state persists outside the driver until changed.

Dependencies and integration: Linux backlight, PWM, GPIO descriptor, regulator, OF properties `brightness-levels`, `default-brightness-level`, delays, and optional interpolation.

Risks: `pwm_apply_might_sleep()` return values in update/suspend/shutdown are ignored. Bad DT can create surprising scales or interpolation tables, though parse checks memory and minimum interpolation input length. Tests should cover generated brightness tables, nonlinear/linear scale detection, bootloader-enabled backlights, regulator/GPIO sequencing delays, suspend/resume, and invalid defaults.
