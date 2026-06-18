## sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_spi.c

Purpose: SPI transport wrapper for BMI323. It supplies a SPI regmap configuration and delegates the common IIO implementation to `bmi323_core_probe()`.

Important APIs, types, and functions: `bmi323_regmap_spi_read()` uses `spi_write_then_read()` with regmap-provided padding/read flag handling. `bmi323_regmap_spi_write()` mutates the regmap buffer by copying the register byte into the second byte, then sends from `data_buff + 1`; this accounts for the regmap pad byte used by the BMI323 SPI format. `bmi323_spi_regmap_config` uses 8-bit registers, 16-bit little-endian values, 8 pad bits, read flag bit 7, and max `BMI323_CFG_RES_REG`.

Control flow: SPI probe initializes the custom regmap on the SPI device, calls common probe, and device matching uses SPI ID `bmi323` plus OF compatible `bosch,bmi323`.

State and persistence behavior: no independent runtime state is kept in this file; runtime PM is inherited from `bmi323_core_pm_ops`.

Dependencies and integration points: depends on Linux SPI, regmap, module device tables, and the core BMI323 namespace. The SPI regmap contract must match the core's 16-bit register accesses and FIFO no-increment reads.

Risks and edge cases: the write callback edits the regmap-provided data buffer in place; this depends on regmap passing a mutable buffer with the expected pad byte layout. Any change in regmap formatting or BMI323 SPI command layout would break writes. Reads rely on `pad_bits` to handle the device dummy byte.

Test signals: probe over SPI, raw/config register reads and writes, FIFO burst reads, and runtime suspend/resume should be compared against I2C behavior. A focused SPI write test should confirm the address/payload bytes on the bus.
