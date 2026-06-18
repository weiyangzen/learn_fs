# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_spi.c

Purpose: SPI transport wrapper for BMI260/BMI270 core, including custom regmap bus operations to handle the device's dummy byte on reads.

Important APIs, types, and functions: `bmi270_regmap_spi_read()` uses `spi_write_then_read()`. `bmi270_regmap_spi_write()` removes the pad byte used by regmap read framing before writing. `bmi270_regmap_bus` plugs these callbacks into `devm_regmap_init()`. `bmi270_spi_regmap_config` uses 8-bit regs/values, 8 pad bits, and read flag bit 7. `bmi270_spi_probe()` obtains chip info, creates regmap, and calls core.

Control flow: SPI match data selects BMI260/BMI270; custom regmap bus adapts transfer framing; core handles validation, firmware upload, IIO setup, and triggers.

State and persistence: no private state beyond managed regmap. The write callback mutates the regmap-provided transfer buffer to shift out the pad byte.

Dependencies and integration: depends on SPI, regmap, BMI270 core namespace/PM ops, and OF/SPI IDs. Unlike I2C, only OF and SPI IDs are declared in this file.

Risks: the write callback casts away const and modifies the data buffer, which is acceptable only if regmap passes mutable scratch. Dummy-byte handling must match BMI270 SPI timing; off-by-one framing would corrupt all register writes. `MODULE_DEVICE_TABLE` is absent for the SPI and OF tables in the inspected snippet, which may affect module autoload metadata.

Test signals: SPI read/write framing with dummy byte, regmap init failure, OF/SPI ID matching and autoload, firmware upload through SPI, and PM callback wiring.
