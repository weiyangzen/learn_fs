# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Makefile

## Purpose
Defines the object list for the mgag200 DRM driver.

## Important APIs, types, and functions
- `mgag200-y` includes shared core files, DDC/BMC support, all chip-specific G200 variants, mode-setting code, and VGA/BMC connector files.
- `obj-$(CONFIG_DRM_MGAG200) += mgag200.o` links the composite object when configured.

## Control flow
Build-system control flow only. Kbuild compiles every listed object into `mgag200.o` when `DRM_MGAG200` is enabled.

## State and persistence
No runtime state. The file determines which source modules are present in the final kernel object.

## Dependencies and integration points
Pairs with `Kconfig` and with prototypes in `mgag200_drv.h`; every chip factory referenced by `mgag200_drv.c` must have an object listed here.

## Risks
Omitting a variant object would create link failures or unsupported PCI IDs. Adding new chip support requires updating this file, the PCI ID table, and shared declarations together.

## Test signals
Build coverage for `CONFIG_DRM_MGAG200=m` and `=y` is the primary signal.
