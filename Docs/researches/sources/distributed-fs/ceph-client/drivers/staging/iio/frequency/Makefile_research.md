# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Makefile

## Purpose
Builds staging DDS drivers.

## Important Entries and Integration
`obj-$(CONFIG_AD9832) += ad9832.o` and `obj-$(CONFIG_AD9834) += ad9834.o` map the Kconfig symbols to their driver objects.

## Risks and Test Signals
Build tests should cover each symbol independently and as modules.
