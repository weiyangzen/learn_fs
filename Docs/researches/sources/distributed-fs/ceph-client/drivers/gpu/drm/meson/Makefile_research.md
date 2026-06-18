# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Makefile

## Purpose
Builds the Meson DRM driver core and optional HDMI/DSI bridge modules from their source objects.

## Important APIs, types, and functions
`meson-drm-y` aggregates core objects: driver, plane, CRTC, CVBS/HDMI/DSI encoders, VIU, VPP, VENC, VCLK, overlay, RDMA, and AFBCD. `obj-$(CONFIG_DRM_MESON)` builds the aggregate, while HDMI and DSI configs build `meson_dw_hdmi.o` and `meson_dw_mipi_dsi.o`.

## Control flow
There is no runtime control flow. Kbuild includes object files according to the Kconfig symbols.

## State and persistence
No state is stored. Build outputs depend on selected config symbols.

## Dependencies and integration points
Ties the Kconfig options to compilation units. The core object list mirrors the initialization sequence in `meson_drv.c`, where encoders, planes, overlays, CRTC, VIU/VPP/VENC/VCLK/RDMA, and AFBCD code are all used.

## Risks
Adding a new core source without updating `meson-drm-y` causes link or missing-feature failures. Optional HDMI/DSI objects are separate modules/objects and must match Kconfig dependencies.

## Test signals
Signals are successful kernel builds for `DRM_MESON=y/m`, optional HDMI/DSI combinations, and no unresolved symbols from the aggregate object list.
