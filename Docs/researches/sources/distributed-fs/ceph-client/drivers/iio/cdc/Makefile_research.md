# sources/distributed-fs/ceph-client/drivers/iio/cdc/Makefile

## Purpose
This Makefile connects CDC Kconfig symbols to object files.

## Important APIs, Types, And Functions
`obj-$(CONFIG_AD7150) += ad7150.o` and `obj-$(CONFIG_AD7746) += ad7746.o` are the only build rules.

## Control Flow
There is no runtime behavior; Kbuild selects objects according to configuration.

## State And Persistence
The file persists the build mapping and has no runtime state.

## Dependencies And Integration Points
It integrates with `drivers/iio/cdc/Kconfig`, the I2C driver source files, and kernel module naming.

## Risks
Wrong object mapping causes missing modules or link failures. New CDC drivers must update both Kconfig and this Makefile.

## Test Signals
Run kernel builds with `CONFIG_AD7150` and `CONFIG_AD7746` as `m` and `y`, verifying expected modules are generated.
