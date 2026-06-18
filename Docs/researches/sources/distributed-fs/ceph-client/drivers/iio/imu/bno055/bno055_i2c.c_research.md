## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_i2c.c

Purpose: I2C bus wrapper for BNO055.

Important APIs, types, and functions: `bno055_i2c_probe()` initializes an I2C regmap using the common `bno055_regmap_config`, then calls `bno055_probe()` with `BNO055_I2C_XFER_BURST_BREAK_THRESHOLD` set to 3 and `sw_reset=true`. Match tables include I2C ID `bno055` and OF compatible `bosch,bno055`.

Control flow: I2C core matches a client, the wrapper creates regmap, then common probe handles all reset, calibration, IIO, buffer, and debugfs setup.

State and persistence behavior: no independent state; all persistent state is in `struct bno055_priv`.

Dependencies and integration points: depends on I2C and `REGMAP_I2C`, imports the common `IIO_BNO055` namespace, and advertises the I2C interface module.

Risks and edge cases: I2C burst threshold is low, so buffered sparse masks may split transfers more often than serial. Software reset is enabled for I2C, so reset command failure affects probe and fusion-mode transitions.

Test signals: successful I2C regmap setup, probe with hardware reset absent using software reset, OF/I2C matching, and buffered scan performance/correctness with gaps above and below threshold 3.
