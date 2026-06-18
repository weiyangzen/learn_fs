# sources/distributed-fs/ceph-client/drivers/fwctl/pds/Makefile

## Purpose
This Kbuild file builds the AMD/Pensando PDS fwctl provider.

## Important Entries
`obj-$(CONFIG_FWCTL_PDS) += pds_fwctl.o` and `pds_fwctl-y += main.o` map the Kconfig symbol to the provider implementation.

## Control Flow and State
No runtime behavior or state is defined in this Makefile.

## Dependencies and Integration Points
The provider object depends on the PDS core auxiliary bus infrastructure and fwctl namespace exports.

## Risks and Test Signals
Build test the object with PDS core enabled as module and built-in, and confirm Kconfig dependency prevents unresolved PDS symbols.
