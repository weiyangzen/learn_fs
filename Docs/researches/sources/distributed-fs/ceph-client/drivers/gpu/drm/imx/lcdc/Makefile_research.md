# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Makefile

## Purpose
Connects the `DRM_IMX_LCDC` Kconfig symbol to the `imx-lcdc.o` driver object.

## Important APIs, types, and functions
- `obj-$(CONFIG_DRM_IMX_LCDC) += imx-lcdc.o` is the only build rule.

## Control flow
No runtime flow. Kbuild includes or omits the LCDC driver according to the Kconfig symbol.

## State and persistence
No runtime state exists; the build rule persists as the module composition contract.

## Dependencies and integration points
Ties the standalone LCDC DRM driver source to the kernel build system.

## Risks
Because the Makefile has one object, renaming or splitting `imx-lcdc.c` requires updating this rule.

## Test signals
Build coverage should produce `imx-lcdc.o` when `CONFIG_DRM_IMX_LCDC` is enabled and omit it when disabled.
