# sources/distributed-fs/ceph-client/drivers/gpib/pc2/Makefile

## Purpose
This Kbuild file builds the PCII/PCIIa GPIB driver object when `CONFIG_GPIB_PC2` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_GPIB_PC2) += pc2_gpib.o`. There are no runtime APIs in the Makefile itself.

## Control flow
Kbuild includes or omits `pc2_gpib.o` based entirely on the `CONFIG_GPIB_PC2` symbol.

## State and persistence behavior
The file has build-time state only and no runtime persistence.

## Dependencies and integration points
It depends on the kernel Kbuild system and the `CONFIG_GPIB_PC2` Kconfig option. The resulting object registers the `pcII`, `pcIIa`, `pcIIa_cb7210`, and `pcII_IIa` Linux-GPIB interfaces.

## Risks and edge cases
Renaming the C file or config symbol without updating this Makefile would silently drop or break the module build.

## Test signals
Build with `CONFIG_GPIB_PC2=y` and `CONFIG_GPIB_PC2=m`; verify `pc2_gpib.o` is compiled and links against the NEC7210/GPIB core helpers.
