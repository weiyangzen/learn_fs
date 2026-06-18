# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313.h

Purpose: shared declarations for the ADXL312/ADXL313/ADXL314 IIO accelerometer core and its I2C/SPI frontends.

Important APIs/types: register macros define ID, soft reset, offsets, activity/inactivity thresholds, bandwidth, power, interrupt, data format, data axes, and FIFO registers. `enum adxl313_device_type`, `struct adxl313_data`, and `struct adxl313_chip_info` describe chip variants and runtime state. Exports include regmap access tables, `adxl313_is_volatile_reg()`, `adxl31x_chip_info[]`, and `adxl313_core_probe()`.

Control flow: bus drivers choose a chip info entry, create a regmap using exported access tables and volatile callback, then call `adxl313_core_probe()` with optional bus setup.

State and persistence: `struct adxl313_data` keeps the regmap, chip information, mutex-protected transfer buffer, watermark, and FIFO buffer. Hardware persists offsets, threshold/event configuration, ODR, power mode, interrupt mapping, and FIFO mode.

Dependencies and integration: depends on IIO type declarations and regmap users in the C files. It is the ABI between `adxl313_core.c`, `adxl313_i2c.c`, and `adxl313_spi.c`.

Risks: register definitions are shared by three variants with different ID/reset/range behavior, so chip info and access tables must remain synchronized. Buffer alignment matters for DMA-safe IIO transfers.

Test signals: compile/link namespace exports, I2C and SPI probe for all three variants, debugfs register access, raw reads, calibration bias, event configuration, and FIFO capture when interrupts exist.
