# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3533.c

Purpose: LM3533 MFD child LED driver for low-voltage control banks, with brightness, hardware blink pattern generator, ALS controls, PWM/current setup, and sysfs attributes.

Important APIs/types/functions: `struct lm3533_led` contains parent MFD pointer, `lm3533_ctrlbank`, classdev, id, mutex, and pattern flag. `lm3533_led_set/get()` wrap ctrlbank brightness. `lm3533_led_blink_set()` maps delays to hardware pattern registers and enables pattern output. Attribute handlers expose id, rise/fall time, ALS channel/enabled, linear mapping, and PWM. Probe consumes `lm3533_led_platform_data`.

Control flow: platform probe validates parent and id, initializes ctrlbank id `pdev->id + 2`, registers LED on parent, then applies max current/PWM and enables ctrlbank. Blink requests program high/low times, clamp to supported ranges, update requested delays, then set pattern-enable bits. Shutdown disables ctrlbank and turns LED off.

State and persistence: pattern-enable state is cached in a bit flag under mutex. Brightness/PWM/current/ALS settings reside in LM3533 registers. Sysfs attributes directly read/write hardware.

Dependencies/integration: LM3533 MFD helpers `lm3533_read/write/update` and ctrlbank APIs, platform data, LED class, sysfs groups, optional parent ALS capability.

Risks: returns negative error values through `enum led_brightness` getter on read failure. Attribute visibility depends on parent `have_als`. Delay quantization is complex and hardware-limited. Manual classdev unregister is required.

Test signals: brightness and blink delay quantization, pattern enable idempotence, ALS attribute visibility, sysfs input validation, shutdown OFF behavior, and ctrlbank enable/disable errors.
