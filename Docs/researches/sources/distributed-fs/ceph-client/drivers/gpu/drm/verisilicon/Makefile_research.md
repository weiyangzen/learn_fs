<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Makefile

## Purpose
`verisilicon/Makefile` builds the VeriSilicon DC DRM module from bridge, CRTC, DC platform, DRM core, hardware database, common plane, and primary-plane sources.

## Important APIs, Types, and Functions
The important build variables are `verisilicon-dc-objs` and `obj-$(CONFIG_DRM_VERISILICON_DC)`. The object list is `vs_bridge.o`, `vs_crtc.o`, `vs_dc.o`, `vs_drm.o`, `vs_hwdb.o`, `vs_plane.o`, and `vs_primary_plane.o`.

## Control Flow
When `CONFIG_DRM_VERISILICON_DC` is enabled, Kbuild links the listed objects into `verisilicon-dc.o` and then into either the kernel image or a loadable module.

## State and Persistence Behavior
There is no runtime state. The Makefile fixes the compilation and link order contract for the driver module.

## Dependencies and Integration Points
It is driven by the Kconfig symbol and expects every listed source file to compile against the selected DRM/regmap/clock helper APIs. It intentionally excludes register-only headers because they are included by the C files.

## Risks
Adding a new source file without updating this list can produce missing-symbol link failures. Removing or renaming files without this update breaks the module build.

## Test Signals
Kbuild tests for built-in and module configurations, plus `modinfo verisilicon-dc` after a module build, validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Makefile -->
