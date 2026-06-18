# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_i2c.c

Purpose: provides the I2C transport glue for ICM42600-family devices. It matches I2C/OF IDs, creates an 8-bit regmap using the shared ICM42600 regmap config, performs I2C-specific bus register setup, and enters `inv_icm42600_core_probe()`.

Important APIs and functions: `inv_icm42600_probe()` checks `I2C_FUNC_SMBUS_I2C_BLOCK`, extracts the chip enum from firmware match data, initializes regmap, and calls the core. `inv_icm42600_i2c_bus_setup()` configures interface registers: attempts to enable I3C spike filter without checking the return value because ACK can be affected, clears I3C-only mode, sets I2C/SPI slew rates to 12-36 ns, and disables the SPI side of the serial interface.

Control flow and state: no private persistent state is stored here. Probe delegates all runtime state to the core. The bus setup callback mutates hardware interface registers through `st->map` after core state exists.

Dependencies and integration: Linux I2C core, module device tables, device properties, regmap-I2C, and the exported ICM42600 core namespace. The driver registers as `inv-icm42600-i2c` and imports `IIO_ICM42600`.

Risks and tests: main risks are missing firmware match data, inadequate adapter functionality, and bus setup register writes that can leave the part inaccessible if wrong for the physical bus. Test signals include module autoload by OF/I2C IDs, probe rejection on adapters without block transfers, successful WHOAMI/core probe after bus setup, and absence of SPI contention after I2C setup.
