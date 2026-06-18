# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i2c.c

Purpose: I2C transport module for ICM45600-family devices.

Important APIs and functions: `inv_icm45600_probe()` checks block I2C functionality, fetches `struct inv_icm45600_chip_info` from firmware match data, initializes an 8-bit regmap over I2C, and calls `inv_icm45600_core_probe(regmap, chip_info, true, NULL)`. Match tables cover all supported 456xx variants and pass chip-info pointers.

Control flow and state: no private runtime state. It asks the core to reset the chip on probe and uses no bus-specific setup callback.

Dependencies and integration: Linux I2C core, regmap-I2C, OF/I2C module tables, shared core PM ops, and `IIO_ICM45600` namespace. Module name is `inv-icm45600-i2c`.

Risks and tests: missing match data or unsupported adapter functionality aborts probe. Since the core requires `int1`, board descriptions must provide an interrupt. Test signals include OF/I2C autoload, chip-info pointer correctness, successful reset/WHOAMI in core, runtime PM through shared ops, and block-transfer functionality rejection.
