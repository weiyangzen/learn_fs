# sources/distributed-fs/ceph-client/drivers/mfd/lm3533-core.c

Purpose: I2C MFD core for TI LM3533 lighting controller. It provides shared register helpers, configures boost/output routing, enables the chip through GPIO, creates ALS/backlight/LED children from platform data, and exposes output routing sysfs attributes.

Important APIs/types/functions: exported `lm3533_read()`, `lm3533_write()`, `lm3533_update()`, `lm3533_i2c_probe()`, `lm3533_device_init()`, `lm3533_set_boost_freq()`, `lm3533_set_boost_ovp()`, and output route setters for HVLED/LVLED.

Control flow: probe allocates core state, initializes I2C regmap, stores IRQ/device, then `lm3533_device_init()` validates platform data, obtains HWEN GPIO, enables the chip, configures boost settings, registers optional ALS/backlight/LED MFD children, and creates sysfs attributes. Remove removes sysfs/children and disables HWEN.

State and persistence: stores child availability flags, regmap, IRQ, and hardware-enable GPIO. Hardware brightness/routing/boost registers persist only while powered. Sysfs visibility depends on child availability.

Dependencies and integration: depends on platform data (`struct lm3533_platform_data`), GPIO descriptors, regmap, MFD child drivers `lm3533-als`, `lm3533-backlight`, and `lm3533-leds`.

Risks: no platform data is fatal. Child init return values are not all propagated before sysfs creation, so partial child failures can be easy to miss. Platform data counts are clamped by modifying the pdata counts.

Test signals: platform-data variants with ALS/backlights/LEDs, HWEN GPIO behavior, boost register values, sysfs output route reads/writes, child probing, and remove cleanup.
