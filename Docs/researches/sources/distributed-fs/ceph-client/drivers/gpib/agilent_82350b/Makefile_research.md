# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/Makefile

## Purpose
This Kbuild file builds the Agilent 82350B family GPIB PCI driver.

## Important Entries
`obj-$(CONFIG_GPIB_AGILENT_82350B) += agilent_82350b.o` maps the Kconfig symbol to the module object.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on the GPIB common core and TMS9914 helper selected by Kconfig.

## Risks and Test Signals
Test modular builds with `GPIB_AGILENT_82350B=m` and ensure helper symbols resolve.
