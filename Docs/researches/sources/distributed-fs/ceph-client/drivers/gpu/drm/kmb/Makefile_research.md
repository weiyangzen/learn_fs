<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Makefile

## Purpose
Defines the object composition for the Intel Keem Bay DRM display driver.

## Important APIs, types, and functions
`kmb-drm-y` links `kmb_crtc.o`, `kmb_drv.o`, `kmb_plane.o`, and `kmb_dsi.o`; `obj-$(CONFIG_DRM_KMB_DISPLAY)` emits the module or built-in object.

## Control flow
There is no runtime flow. Build-time object ordering pulls together CRTC, platform driver, plane, and DSI/bridge code into one DRM driver.

## State and persistence
No state is stored here.

## Dependencies and integration points
The Makefile matches the Kconfig module name `kmb-drm` and must stay synchronized with source-file splits.

## Risks
Omitting one object can compile-link fail or remove runtime functionality such as DSI bridge setup or plane programming.

## Test signals
Kernel build and module link tests are sufficient for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/Makefile -->
