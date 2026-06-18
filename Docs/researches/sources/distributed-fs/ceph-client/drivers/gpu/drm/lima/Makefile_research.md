<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Makefile

## Purpose
Defines the object list for the Lima DRM driver.

## Important APIs, types, and functions
`lima-y` links driver, device, PMU, L2 cache, MMU, GP, PP, GEM, VM, scheduler, context, DLBU, broadcast, trace, and devfreq objects. `obj-$(CONFIG_DRM_LIMA)` emits `lima.o`.

## Control flow
No runtime control flow. Build composition mirrors the driver's runtime split between platform/IOCTL, memory management, scheduling, hardware IP blocks, and power management.

## State and persistence
No state is stored here.

## Dependencies and integration points
Must stay synchronized with the inter-file dependencies in `lima_device.c`, scheduler code, GP/PP pipe setup, GEM/VM, and devfreq.

## Risks
Missing any object can cause link failures or runtime NULL callback paths.

## Test signals
Kernel build and module load tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/Makefile -->
