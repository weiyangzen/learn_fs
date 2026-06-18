# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Makefile

## Purpose
This Makefile connects the PXP MEI client driver object to the `CONFIG_INTEL_MEI_PXP` build option.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_INTEL_MEI_PXP) += mei_pxp.o`.

## Control flow and state
There is no runtime flow. The kernel build includes `mei_pxp.o` when the Kconfig option is enabled as built-in or module.

## State and persistence behavior
No runtime or persistent state exists.

## Dependencies and integration points
It depends on the Kbuild system and the `INTEL_MEI_PXP` Kconfig symbol. It integrates the local `mei_pxp.c` source into the MEI PXP subdirectory build.

## Risks and test signals
Risks are limited to object naming and Kconfig mismatch. Test signals include module/built-in builds and verifying that `mei_pxp.ko` is produced when configured as `m`.
