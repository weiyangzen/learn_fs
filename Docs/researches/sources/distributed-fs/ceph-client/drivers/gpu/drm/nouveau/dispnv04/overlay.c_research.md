<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/overlay.c

## Purpose
This file implements legacy overlay planes for NV04 and NV10-NV40 hardware, exposing YUV overlay formats and color-control properties through DRM planes.

## Important APIs, Types, and Functions
It defines `struct nouveau_plane`, supported formats `YUYV`, `UYVY`, `NV12`, and `NV21`, plane callbacks for NV10 (`nv10_update_plane`, `nv10_disable_plane`) and NV04 (`nv04_update_plane`, `nv04_disable_plane`), property handling through `nv_set_property`, and the public `nouveau_overlay_init`.

## Control Flow
Overlay init selects NV04 or NV10 implementation by chipset, allocates a plane, registers a universal overlay plane with CRTC masks and supported formats, creates range properties, attaches defaults, initializes color controls, and force-disables the plane. Update paths convert 16.16 source coordinates to integer pixels, validate scaling limits and offsets, pin the framebuffer BO into VRAM, program PVIDEO registers for source, destination, scaling, format, color key, color encoding, and luminance/chrominance controls, flip buffer selection where supported, and unpin the previously active BO. Disable stops the overlay and unpins the current BO.

## State and Persistence Behavior
Per-plane state stores current BO, buffer flip bit, color key, contrast, brightness, hue, saturation, color encoding, and DRM property objects. The active overlay BO remains pinned while displayed and is released on update/disable/destroy.

## Dependencies and Integration Points
It depends on DRM plane APIs, Nouveau GEM/BO pinning, NVIF MMIO writes, CRTC index state, `nvreg.h` PVIDEO registers, and the display constructor in `disp.c`.

## Risks
Scaling validation is hardware-specific and rejects offsets for NV04. NV04 step-size math divides by `crtc_w - 1` and `crtc_h - 1`, so degenerate sizes must be filtered by DRM callers. Pin failures abort updates. Programming lacks explicit vblank synchronization in the NV10 path. Property updates modify live registers and must match the currently programmed buffer index.

## Test Signals
Signals include plane creation on NV04 and NV10/NV30/NV40, format coverage for packed and planar YUV where supported, scaling rejection, color key enable/disable, brightness/contrast/hue/saturation changes, BT.601/BT.709 switching, repeated updates with BO pin accounting, disable/destroy cleanup, and suspend/resume with overlays active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/overlay.c -->
