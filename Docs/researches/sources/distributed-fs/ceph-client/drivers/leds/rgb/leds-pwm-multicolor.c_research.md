# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-pwm-multicolor.c

Purpose: generic platform driver for PWM-backed multicolor LEDs. It expects a `multi-led` child node containing PWM-backed monochrome color channels and exposes them as one multicolor LED class device.

Important APIs, types, and functions: `struct pwm_led` stores per-channel PWM device, cached state, and active-low flag. `struct pwm_mc_led` stores multicolor class device, mutex, and flexible channel array. `led_pwm_mc_set()` calculates subled brightness, scales each to PWM duty, applies active-low inversion, and calls `pwm_apply_might_sleep()`. `iterate_subleds()` acquires PWMs and color properties for child nodes. `led_pwm_mc_probe()` parses the group node and registers the multicolor LED.

Control flow: probe obtains the named `multi-led` node, counts channels, allocates state and subled array, reads group `max-brightness`, parses each child PWM/color, registers the multicolor LED, applies initial brightness, and stores driver data. Brightness writes lock the channel array and program all PWMs in order.

State and persistence: cached PWM states hold period, duty, enabled flag, and polarity for each channel. As with the single-color PWM driver, PWMs are kept enabled unless the LED core marks the device suspended.

Dependencies and integration points: PWM framework, LED multicolor class, fwnode parsing, platform driver, compatible `pwm-leds-multicolor`, and LED suspend/resume flag handling.

Risks and test signals: test missing `multi-led`, missing `max-brightness`, child PWM/color errors and fwnode release, active-low duty inversion, partial `pwm_apply` failure across channels, and suspend behavior. Hardware validation should verify color mixing and off-state electrical levels.
