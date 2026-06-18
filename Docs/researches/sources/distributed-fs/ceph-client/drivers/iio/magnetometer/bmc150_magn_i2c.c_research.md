<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_i2c.c

Purpose: I2C bus front-end for the Bosch BMC150/BMC156/BMM150 magnetometer core.

Important APIs/types/functions: `bmc150_magn_i2c_probe()` creates an I2C regmap using the shared `bmc150_magn_regmap_config`, resolves the I2C id name when present, and calls `bmc150_magn_probe()`. `bmc150_magn_i2c_remove()` delegates to `bmc150_magn_remove()`. Match tables cover I2C ids `bmc150_magn`, `bmc156_magn`, `bmm150_magn` and OF compatibles `bosch,bmc150_magn`, `bosch,bmc156_magn`, deprecated `bosch,bmm150_magn`, and `bosch,bmm150`.

Control flow: module registration installs an `i2c_driver`; probe initializes regmap, forwards device/IRQ/name to the core, and remove tears down via the core. PM operations are the shared core PM ops.

State/persistence: this wrapper owns no sensor state beyond the devm regmap; core state is stored on the device by `bmc150_magn_probe()`.

Dependencies/integration: depends on I2C, regmap-I2C, the shared BMC150 core, and module namespace `IIO_BMC150_MAGN`. It is selected by `CONFIG_BMC150_MAGN_I2C`.

Risks: firmware-node probing can produce `name = NULL` when no I2C id is available, so user-visible `indio_dev->name` depends on enumeration path. The `MODULE_AUTHOR` string is missing a closing angle bracket, a metadata issue only.

Test signals: compile as module and built-in, probe each I2C id/OF compatible, verify IRQ forwarding to core, and confirm PM namespace/modpost checks are clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_i2c.c -->
