# sources/distributed-fs/ceph-client/drivers/hsi/controllers/Makefile

## Purpose
Builds the OMAP SSI controller module from its controller-level and port-level implementation files.

## Important APIs, Types, and Functions
The Makefile defines `omap_ssi-objs += omap_ssi_core.o omap_ssi_port.o` and attaches the composed object to `obj-$(CONFIG_OMAP_SSI)`.

## Control Flow
Kbuild includes both implementation files in one module/object when `CONFIG_OMAP_SSI` is enabled. This lets `omap_ssi_core.c` register both the controller platform driver and the externally declared `ssi_port_pdriver` from `omap_ssi_port.c`.

## State and Persistence
No runtime state. Build state is controlled by Kconfig and Kbuild.

## Dependencies and Integration Points
Integrates with `drivers/hsi/controllers/Kconfig` and the Linux Kbuild object aggregation model. The split object layout matches shared declarations in `omap_ssi.h`.

## Risks and Test Signals
Risk is link-time coupling between the two objects; missing either object breaks `ssi_port_pdriver` or controller callbacks. Test signals are successful `CONFIG_OMAP_SSI=m` and `=y` builds.
