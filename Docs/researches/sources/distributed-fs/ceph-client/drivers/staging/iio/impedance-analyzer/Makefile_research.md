# sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Makefile

## Purpose
Builds the AD5933/AD5934 staging impedance analyzer driver.

## Important Entries and Integration
`obj-$(CONFIG_AD5933) += ad5933.o` maps the Kconfig symbol to the driver object.

## Risks and Test Signals
Compile tests should cover module and built-in forms and ensure selected IIO buffer dependencies are available.
