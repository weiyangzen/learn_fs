# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Makefile

## Purpose
Builds the shared ADT7316 family core and optional SPI/I2C bus glue.

## Important Entries and Integration
`obj-$(CONFIG_ADT7316) += adt7316.o`, `obj-$(CONFIG_ADT7316_SPI) += adt7316-spi.o`, and `obj-$(CONFIG_ADT7316_I2C) += adt7316-i2c.o` mirror the split Kconfig symbols.

## Risks and Test Signals
Compile tests should ensure transport modules resolve the exported `adt7316_probe()` and `adt7316_pm_ops` symbols from the core.
