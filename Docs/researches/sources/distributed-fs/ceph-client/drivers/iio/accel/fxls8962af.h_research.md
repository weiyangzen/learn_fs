# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af.h

Purpose: internal shared header for FXLS8962AF-family bus wrappers and core. It defines variant enum constants and declares exported core probe, PM ops, and bus-specific regmap configs.

Important contract: the anonymous enum lists `fxls8962af`, `fxls8964af`, `fxls8967af`, and `fxls8974cf` for ID-table driver data. The core probe does not currently take this enum, instead identifying the device from `WHO_AM_I`. The header also declares both I2C and SPI regmap configs because SPI requires extra pad bits.

Integration and risks: this header is the namespace boundary for `IIO_FXLS8962AF`. Since wrappers may expose variants not present in all match tables, table updates should be synchronized with core chip-info entries and this enum. Test signals are successful compilation of both wrappers, namespace import/export, regmap config linkage, and PM op use by bus drivers.
