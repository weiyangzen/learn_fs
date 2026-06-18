<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.h -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.h

Purpose: private shared header connecting BMC150 magnetometer bus wrappers to the common core implementation.

Important APIs/types/functions: declares exported `bmc150_magn_regmap_config`, exported `bmc150_magn_pm_ops`, `bmc150_magn_probe(struct device *dev, struct regmap *regmap, int irq, const char *name)`, and `bmc150_magn_remove(struct device *dev)`.

Control flow: no executable flow exists. I2C/SPI wrapper modules include this header, initialize a bus-specific regmap, and call the common probe/remove and PM ops declared here.

State/persistence: no state is stored in the header. It defines the compile-time contract for sharing the core's device-managed IIO state via `dev_set_drvdata()`.

Dependencies/integration: depends on `struct regmap_config`, `struct dev_pm_ops`, `struct device`, and `struct regmap` being available through included kernel headers in users of the header. It pairs with namespace exports/imports under `IIO_BMC150_MAGN`.

Risks: because this is a narrow internal ABI, any signature change must be applied to both wrappers and the core. The header does not include `<linux/device.h>` explicitly, so it relies on includers or included regmap headers for type declarations.

Test signals: compile both BMC150 I2C and SPI modules as built-ins and modules, and run modpost to ensure exported symbols and namespace imports resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.h -->
