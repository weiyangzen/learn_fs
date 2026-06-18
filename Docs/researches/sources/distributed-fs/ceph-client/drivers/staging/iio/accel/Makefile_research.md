# sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Makefile

## Purpose
Builds the ADIS16203 staging accelerometer/inclinometer driver.

## Important Entries and Integration
`obj-$(CONFIG_ADIS16203) += adis16203.o` ties the C file to the Kconfig symbol.

## Risks and Test Signals
Compile coverage for `CONFIG_ADIS16203=m/y` should produce the expected object/module without building it when the symbol is disabled.
