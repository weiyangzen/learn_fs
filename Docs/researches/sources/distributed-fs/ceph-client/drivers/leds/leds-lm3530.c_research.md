# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3530.c

Purpose: legacy I2C LED/backlight driver for LM3530 with manual, ALS, and PWM operating modes supplied through platform data.

Important APIs/types/functions: `struct lm3530_data` stores classdev, I2C client, platform data, current mode, regulator, brightness, and enable state. `lm3530_init_registers()` builds the full register initialization image, including ALS zone boundaries and ramp settings. `lm3530_brightness_set()` handles manual/PWM brightness. `mode_show/store` expose a sysfs mode switch.

Control flow: probe requires platform data and I2C functionality, gets `vin`, optionally initializes registers if `brt_val` is nonzero, and registers `lcd-backlight`. Manual brightness lazily initializes registers and disables regulator at zero. ALS brightness requests are ignored because hardware controls brightness. PWM mode calls the platform PWM intensity hook.

State and persistence: software caches mode, last brightness, and regulator enable state. Hardware configuration is rewritten on mode changes. Platform data values may be normalized in ALS configuration.

Dependencies/integration: platform data header `led-lm3530.h`, regulator framework, optional PWM callback, sysfs LED groups, I2C SMBus writes.

Risks: no locking around sysfs mode changes and brightness callbacks. Platform data is mandatory. ALS configuration mutates platform data fields. PWM mode depends entirely on board callback behavior.

Test signals: manual ON/OFF regulator sequencing, mode sysfs parsing for `man/als/pwm`, ALS zone calculations, PWM callback invocation, I2C failure handling during register initialization, and remove-time regulator disable.
