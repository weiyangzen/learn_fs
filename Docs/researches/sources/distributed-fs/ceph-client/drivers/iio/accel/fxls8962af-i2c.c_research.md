# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-i2c.c

Purpose: I2C transport wrapper for NXP FXLS8962AF-family accelerometers. It sets up I2C regmap access and delegates all behavior to the shared core.

Important APIs and flow: `fxls8962af_probe()` initializes `devm_regmap_init_i2c()` with `fxls8962af_i2c_regmap_conf` and calls `fxls8962af_core_probe(&client->dev, regmap, client->irq)`. The I2C ID table includes four enum values, while the OF table lists `nxp,fxls8962af` and `nxp,fxls8964af`. PM ops are imported from the core.

State, dependencies, risks, and tests: this file has no local persistent state. Dependencies are I2C, regmap, OF/I2C matching, and namespace `IIO_FXLS8962AF`. Core chip identification, not ID driver data, decides the exact variant, so table enum values are currently used for module metadata rather than passed to probe. Risks include OF coverage lagging the I2C ID table and I2C-specific FIFO erratum behavior depending on `i2c_verify_client()` in the core. Test signals include regmap creation, module autoload from I2C/OF IDs, IRQ propagation, core WHO_AM_I matching, and PM callback linkage.
