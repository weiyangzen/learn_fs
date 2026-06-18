# sources/distributed-fs/ceph-client/drivers/gpib/cb7210/Makefile

## Purpose
This Kbuild file builds the Measurement Computing/CB7210 GPIB driver.

## Important Entries
`obj-$(CONFIG_GPIB_CB7210) += cb7210.o` maps the Kconfig symbol to the module object.

## Control Flow and State
No runtime behavior is defined in this file.

## Dependencies and Integration Points
The object depends on GPIB common and NEC7210 helpers selected by Kconfig.

## Risks and Test Signals
Build tests should cover PCI/ISA and optional PCMCIA configurations so conditional code compiles.
