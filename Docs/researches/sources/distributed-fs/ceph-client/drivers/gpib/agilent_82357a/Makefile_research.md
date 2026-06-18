# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/Makefile

## Purpose
This Kbuild file builds the Agilent 82357A/B USB GPIB driver.

## Important Entries
`obj-$(CONFIG_GPIB_AGILENT_82357A) += agilent_82357a.o` maps the Kconfig symbol to the module object.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on USB and the GPIB common core selected by Kconfig.

## Risks and Test Signals
Build tests should verify USB and GPIB symbols resolve for modular and built-in configurations.
