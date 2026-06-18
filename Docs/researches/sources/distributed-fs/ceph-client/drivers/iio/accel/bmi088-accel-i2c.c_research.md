# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-i2c.c

Purpose: I2C wrapper for BMI085/BMI088/BMI090L accelerometer core. It only handles bus regmap creation, match tables, and delegation to the shared core.

Important APIs and flow: `bmi088_accel_probe()` reads the I2C ID table entry with `i2c_client_get_device_id()`, initializes `devm_regmap_init_i2c()` with `bmi088_regmap_conf`, then calls `bmi088_accel_core_probe(&i2c->dev, regmap, i2c->irq, id->driver_data)`. Remove calls `bmi088_accel_core_remove()`. OF compatibles and I2C IDs map the supported chip names to `enum bmi_device_type`, and the driver attaches `bmi088_accel_pm_ops`.

State, dependencies, risks, and tests: no bus-local persistent state is stored. Dependencies are I2C, regmap, OF matching, PM ops, and namespace `IIO_BMI088`. Risk is mostly match-data correctness; unlike OF entries, the probe assumes an I2C ID is present and uses its driver data. Test signals include module autoload from I2C/OF IDs, regmap creation failure path, core chip-ID validation, runtime PM callback linkage, and remove power-down.
