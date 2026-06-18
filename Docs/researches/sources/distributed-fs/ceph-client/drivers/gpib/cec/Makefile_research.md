# sources/distributed-fs/ceph-client/drivers/gpib/cec/Makefile

## Purpose
This Kbuild file builds the CEC PCI GPIB driver.

## Important Entries
`obj-$(CONFIG_GPIB_CEC_PCI) += cec_gpib.o` maps the Kconfig symbol to the implementation object.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on GPIB common and NEC7210 helpers selected by Kconfig.

## Risks and Test Signals
Build tests should cover `GPIB_CEC_PCI=m` with PCI, IO port, and NEC7210 support enabled.
