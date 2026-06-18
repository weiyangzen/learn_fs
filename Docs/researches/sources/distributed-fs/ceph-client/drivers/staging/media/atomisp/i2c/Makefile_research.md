# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Makefile

## Purpose
Builds AtomISP I2C sensor drivers.

## Important Entries and Integration
`obj-$(CONFIG_VIDEO_ATOMISP_GC2235) += atomisp-gc2235.o` and `obj-$(CONFIG_VIDEO_ATOMISP_OV2722) += atomisp-ov2722.o` map sensor symbols to modules.

## Risks and Test Signals
Compile tests should cover each sensor symbol independently and confirm the modules link against AtomISP platform helper interfaces.
