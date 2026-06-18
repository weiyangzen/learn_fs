# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_i2c.c

## Purpose

`bma400_i2c.c` is the I2C transport wrapper for the BMA400 core. It creates the I2C regmap and passes the client IRQ and device name into `bma400_probe()`.

## Important APIs, Types, and Functions

`bma400_i2c_probe()` obtains the I2C device ID, initializes `devm_regmap_init_i2c()` with the shared `bma400_regmap_config`, and calls `bma400_probe()`. The file declares I2C ID and OF compatible tables for `bosch,bma400`.

## Control Flow

Probe fails early if regmap creation fails. Otherwise all chip validation, regulator setup, event support, trigger setup, and IIO registration are performed by the common core.

## State and Persistence Behavior

The wrapper stores no private state. It forwards the name from the I2C ID to the core for `indio_dev->name`.

## Dependencies and Integration Points

It depends on I2C, regmap, module tables, and the `IIO_BMA400` namespace. The file comments document I2C address selection by SDO.

## Risks

`i2c_client_get_device_id()` assumes ID-table backed binding; OF-only binding behavior should be verified because the returned ID name is used. Regmap error reporting uses `dev_err()` plus raw `PTR_ERR()` rather than `dev_err_probe()`.

## Test Signals

Validation includes OF/I2C binding, regmap initialization, name propagation, common-probe chip ID validation, IRQ/no-IRQ operation, and sysfs/buffer/event behavior inherited from the core.
