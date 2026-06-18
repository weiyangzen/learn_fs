# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-i2c.c

Purpose: I2C transport wrapper for the Kionix KXSD9 accelerometer common driver. It creates a small 8-bit regmap and delegates probe/remove/PM behavior to shared KXSD9 common code in `kxsd9.h`/its companion implementation.

Important APIs and flow: `kxsd9_i2c_probe()` builds a local `regmap_config` with max register `0x0e`, initializes `devm_regmap_init_i2c()`, and calls `kxsd9_common_probe(&i2c->dev, regmap, i2c->name)`. Remove calls `kxsd9_common_remove()`. OF and I2C ID tables expose `kionix,kxsd9` and `kxsd9`; PM ops are `kxsd9_dev_pm_ops`.

State, dependencies, risks, and tests: this wrapper stores no persistent state; the common KXSD9 driver owns IIO state and hardware behavior. Dependencies are I2C, regmap, the KXSD9 common namespace `IIO_KXSD9`, OF matching, and PM ops. Risks include transport/common contract drift, max-register mismatch with common code expectations, and regmap init failure. Test signals include I2C/OF autoload, regmap creation, common probe success with the passed device name, remove delegation, and PM callback linkage.
