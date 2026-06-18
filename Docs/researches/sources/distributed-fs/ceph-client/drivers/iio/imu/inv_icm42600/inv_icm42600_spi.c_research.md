# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_spi.c

Purpose: provides SPI transport glue for the ICM42600 family. It identifies supported SPI/OF devices, creates the SPI-specific regmap, configures bus interface registers, and delegates all sensor behavior to the shared core.

Important APIs and functions: `inv_icm42600_probe()` obtains chip match data, initializes `inv_icm42600_spi_regmap_config`, and calls `inv_icm42600_core_probe()`. `inv_icm42600_spi_bus_setup()` enables I3C-related interface bits, clears I3C-only mode, programs I2C/SPI slew rates for SPI operation, and disables the I2C bus path.

Control flow and state: this file is stateless beyond static match tables and module metadata. Hardware state is updated only during the bus setup callback. Runtime PM and IIO devices are owned by the core and children.

Dependencies and integration: Linux SPI core, regmap-SPI, OF/SPI module tables, and `IIO_ICM42600` namespace imports. It registers as `inv-icm42600-spi` with shared `inv_icm42600_pm_ops`.

Risks and tests: SPI has no ACK, so bus setup correctness and WHOAMI validation in the core are the main sanity checks. Test signals include OF/SPI module autoload, successful regmap reads through SPI, I2C path disabled after probe, slew-rate programming, and suspend/resume using the shared PM ops.
