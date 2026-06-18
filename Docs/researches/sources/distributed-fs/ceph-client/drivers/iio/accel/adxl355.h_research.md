# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355.h

Purpose: shared declarations for ADXL355/ADXL359 IIO accelerometer core and I2C/SPI frontends.

Important APIs/types: `enum adxl355_device_type`, `struct adxl355_fractional_type`, and `struct adxl355_chip_info` describe device variant, part ID, acceleration scale, and temperature offset. Exports are readable/writeable regmap access tables, `adxl35x_chip_info[]`, and `adxl355_core_probe()`.

Control flow: bus frontends select chip info from match data, initialize a protocol-specific regmap using the access tables, then call the core probe.

State and persistence: this header defines no runtime state, but its chip-info constants drive persistent IIO scale/offset behavior and part-ID validation.

Dependencies and integration: includes regmap declarations and is included by `adxl355_core.c`, `adxl355_i2c.c`, and `adxl355_spi.c`.

Risks: ADXL355 and ADXL359 differ in part ID, acceleration range/scale, and temperature offset; incorrect match data produces wrong units even if register access works.

Test signals: namespace export/import, chip-info selection for both variants, I2C/SPI probe, raw/scale/offset sysfs, and triggered buffer setup.
