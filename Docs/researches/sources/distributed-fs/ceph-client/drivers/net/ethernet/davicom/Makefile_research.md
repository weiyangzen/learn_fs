# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/Makefile

## Purpose
`davicom/Makefile` maps Davicom Ethernet Kconfig symbols to their driver object files.

## Important APIs, types, and functions
- `obj-$(CONFIG_DM9000) += dm9000.o` builds the DM9000 driver when selected.
- `obj-$(CONFIG_DM9051) += dm9051.o` builds the DM9051 SPI driver when selected.

## Control flow and state
Kbuild expands object lists according to the selected Kconfig symbols. No runtime state exists in this file.

## Dependencies and integration points
It connects `davicom/Kconfig` options to the kernel build system and source files in the same directory.

## Risks and test signals
The main risks are stale object names or missing Kconfig wiring. Test by building `CONFIG_DM9000=y/m` and `CONFIG_DM9051=y/m`.
