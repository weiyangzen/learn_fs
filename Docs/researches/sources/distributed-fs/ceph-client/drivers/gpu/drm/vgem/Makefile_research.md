<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Makefile

## Purpose
`vgem/Makefile` builds the virtual GEM provider module from its driver and fence implementation.

## Important APIs, Types, and Functions
It defines `vgem-y := vgem_drv.o vgem_fence.o` and `obj-$(CONFIG_DRM_VGEM) += vgem.o`.

## Control Flow
Kbuild links VGEM core and fence files into one module when the Kconfig symbol is enabled.

## State and Persistence Behavior
There is no runtime state in the Makefile.

## Dependencies and Integration Points
It is controlled by `DRM_VGEM` and must stay synchronized with VGEM source file names.

## Risks
Missing objects cause unresolved VGEM ioctl or lifecycle symbols.

## Test Signals
Module and built-in builds validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Makefile -->
