# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345.h

Purpose: shared register and API header for ADXL345/ADXL375 IIO accelerometer core and I2C/SPI frontends.

Important APIs/types: register macros cover device ID, tap timing, activity/inactivity/free-fall thresholds, bandwidth, power, interrupt map/source, data format, axis data, and FIFO. Interrupt bit macros define overrun, watermark, free-fall, inactivity, activity, double tap, single tap, and data-ready. `struct adxl345_chip_info` carries name and scale. Exports are `adxl345_is_volatile_reg()` and `adxl345_core_probe()`.

Control flow: bus frontends create regmap instances and call `adxl345_core_probe()` with optional SPI setup and FIFO delay information.

State and persistence: header-defined hardware registers persist offsets, event thresholds, tap timing, bandwidth/range, power mode, interrupt routing, and FIFO configuration. Runtime state is private to the core C file.

Dependencies and integration: consumed by `adxl345_core.c`, `adxl345_i2c.c`, and `adxl345_spi.c`. It intentionally avoids including transport-specific headers.

Risks: ADXL345 and ADXL375 share much of the register model but use different scale constants. Compatible sharing with the older input driver is handled in Kconfig and must remain aligned with match tables.

Test signals: compile/link coverage, raw/scale/sample-frequency sysfs, tap/free-fall/activity events, FIFO buffer capture, and I2C/SPI probe.
