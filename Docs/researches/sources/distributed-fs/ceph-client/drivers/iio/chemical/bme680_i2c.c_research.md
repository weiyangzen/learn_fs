# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_i2c.c

## Purpose
`bme680_i2c.c` is the I2C transport driver for the BME680 core.

## Important APIs, Types, And Functions
`bme680_i2c_probe()` initializes an I2C regmap with `bme680_regmap_config`, chooses the I2C ID name when available, and calls `bme680_core_probe()`. The driver declares I2C and OF match tables for `"bme680"` and `"bosch,bme680"`.

## Control Flow
The I2C bus matches a device, probe builds regmap, and all sensor setup is delegated to the core. Runtime PM operations are the shared `bme680_dev_pm_ops`.

## State And Persistence
No transport-specific runtime state is kept. The regmap is device-managed and owned by the core after probe delegation.

## Dependencies And Integration Points
It depends on I2C, regmap-I2C, the shared BME680 header, and imports the `IIO_BME680` namespace.

## Risks
If `i2c_client_get_device_id()` returns NULL for an OF-only device, the core receives a NULL name and the IIO device name may be absent or less useful. Regmap errors are logged and propagated.

## Test Signals
Test I2C and OF matching, regmap init failure, namespace/module builds, and runtime PM callback linkage.
