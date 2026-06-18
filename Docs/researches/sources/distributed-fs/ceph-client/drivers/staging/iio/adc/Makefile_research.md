# sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Makefile

## Purpose
Builds the AD7816 family staging ADC driver.

## Important Entries and Integration
`obj-$(CONFIG_AD7816) += ad7816.o` binds the driver object to the Kconfig symbol.

## Risks and Test Signals
Compile with `CONFIG_AD7816=m/y` should produce the module and pull required SPI/GPIO dependencies from Kconfig.
