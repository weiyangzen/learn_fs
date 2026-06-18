# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_spi.c

Purpose: SPI transport module for ICM45600-family devices.

Important APIs and functions: `inv_icm45600_probe()` obtains chip-info match data from SPI/OF tables, initializes an 8-bit SPI regmap, and calls core probe with reset enabled plus `inv_icm45600_spi_bus_setup()`. The bus setup callback writes `DRIVE_CONFIG0` to select a 5 ns SPI slew rate.

Control flow and state: stateless bus glue. Transport-specific hardware mutation is limited to the slew-rate setup callback invoked from the core before/after reset.

Dependencies and integration: Linux SPI core, regmap-SPI, OF/SPI module tables, shared PM ops, exported chip-info objects, and `IIO_ICM45600` namespace. Module registers as `inv-icm45600-spi`.

Risks and tests: SPI probe relies on match data and has no bus ACK beyond regmap reads/WHOAMI in the core. Slew-rate settings can affect signal integrity. Test signals include SPI ID and OF autoload, successful WHOAMI after reset and bus setup, correct namespace imports, runtime PM cycles, and FIFO interrupts over SPI.
