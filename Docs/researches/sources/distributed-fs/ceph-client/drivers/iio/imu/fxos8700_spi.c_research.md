## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_spi.c

Purpose: SPI wrapper for NXP FXOS8700.

Important APIs, types, and functions: `fxos8700_spi_probe()` initializes a SPI regmap with the common `fxos8700_regmap_config`, reads the SPI ID name, and calls `fxos8700_core_probe()` with `use_spi=true`. Match tables include SPI ID `fxos8700`, ACPI `FXOS8700`, and OF compatible `nxp,fxos8700`.

Control flow: SPI core matches the device, regmap is created, then the common core handles chip init and IIO registration.

State and persistence behavior: no independent state in the wrapper.

Dependencies and integration points: depends on SPI, regmap_spi, ACPI/OF matching, and common FXOS8700 core exports.

Risks and edge cases: the core currently ignores `use_spi`, so any FXOS8700 SPI-specific addressing/transfer quirks must be fully handled by generic regmap SPI or added later. Probe logs regmap failures with `dev_err`.

Test signals: SPI probe via ID/OF/ACPI, register access through regmap SPI, and parity with I2C for raw reads and config writes.
