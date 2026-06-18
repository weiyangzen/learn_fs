# sources/distributed-fs/ceph-client/include/linux/led-lm3530.h

Purpose: provides platform data and register-value constants for the National/TI LM3530 backlight LED controller.

Important APIs and types: constants encode full-scale current, ALS averaging time, ramp times, and ALS input impedance choices. `enum lm3530_mode` selects manual, ALS, or PWM operation; `enum lm3530_als_mode` selects ALS input combination. `struct lm3530_pwm_data` contains PWM intensity callbacks. `struct lm3530_platform_data` carries mode, ALS setup, current, PWM polarity, ramp law/rates, resistor selectors, ALS voltage calibration, initial brightness, and PWM hooks.

Control flow: board/platform code passes this data to the LM3530 driver, which converts fields to device register programming and optional PWM callbacks.

State and persistence: the header defines boot/configuration state only. Runtime brightness and ALS behavior live in driver state and hardware registers.

Dependencies and integration points: integrates board files or platform data users with the LM3530 LED/backlight driver.

Risks and test signals: risks are invalid enum/register constants, missing PWM callbacks in PWM mode, and bad ALS calibration causing inverted brightness. Test manual/ALS/PWM modes, ramp settings, current limits, ALS threshold behavior, and suspend/resume restoration.
