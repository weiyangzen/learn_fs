# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Makefile

## Purpose
Builds the PL111 DRM driver objects and conditionally includes variant/debugfs support.

## Important APIs, Types, and Functions
Defines `pl111_drm-y` with `pl111_display.o`, `pl111_versatile.o`, and `pl111_drv.o`. Adds `pl111_nomadik.o` when `CONFIG_ARCH_NOMADIK` is enabled and `pl111_debugfs.o` when `CONFIG_DEBUG_FS` is enabled. Connects `obj-$(CONFIG_DRM_PL111)` to `pl111_drm.o`.

## Control Flow
Kbuild collects the listed objects into the `pl111_drm` built-in or module target depending on `CONFIG_DRM_PL111`. Optional objects are compiled only when their config symbols are enabled.

## State and Persistence
No runtime state. Build state is encoded in generated object composition and module output.

## Dependencies and Integration Points
Integrates Kconfig with Kbuild. The required objects provide core driver, display pipe, and Versatile variant behavior; optional objects add Nomadik variant and debugfs register dump support.

## Risks and Edge Cases
Missing optional config guards would cause unresolved symbols or dead code. Debugfs support is excluded unless enabled, so declarations must match conditional build behavior elsewhere.

## Test Signals
Build matrix with `CONFIG_DRM_PL111=y/m`, `CONFIG_DEBUG_FS=y/n`, and `CONFIG_ARCH_NOMADIK=y/n` should produce the expected object composition without link errors.
