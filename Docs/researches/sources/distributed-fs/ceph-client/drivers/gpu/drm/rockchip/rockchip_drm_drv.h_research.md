# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.h

## Purpose

`rockchip_drm_drv.h` is the shared Rockchip DRM driver contract used by the VOP, VOP2, GEM, framebuffer, RGB, LVDS, HDMI, MIPI, DP, and component binding code. It defines display output mode constants, common Rockchip CRTC and encoder state, DMA/IOMMU helper prototypes, platform-driver declarations, and container helpers used across the Rockchip DRM subsystem.

## Important APIs, Types, and Functions

- `ROCKCHIP_OUT_MODE_*` encodes hardware output bus packing such as P888, P666, P565, BT.656/1120, serial RGB, YUV420, and 10-bit `AAAA`.
- `struct rockchip_crtc_state` extends `drm_crtc_state` with output connector type, output mode, bpc, output flags, AFBC enablement, YUV overlay flag, bus format, bus flags, and color space.
- `struct rockchip_drm_private` stores the shared IOMMU domain, IOMMU device, `drm_mm` allocator, and `mm_lock` used by GEM IOVA mapping.
- `struct rockchip_encoder` wraps `drm_encoder` with `crtc_endpoint_id`, allowing VOP2 to select an output interface from device-tree endpoint IDs.
- `rockchip_drm_dma_attach_device`, `rockchip_drm_dma_detach_device`, `rockchip_drm_dma_init_device`, and `rockchip_drm_wait_vact_end` are cross-file services.

## Control Flow

This header has no executable control flow beyond `to_rockchip_encoder`. Its main flow is contractual: encoders set `rockchip_crtc_state` fields during atomic checks, display controllers read those fields during atomic enable, and GEM/VOP code coordinate through private DMA/IOMMU structures and helper prototypes.

## State and Persistence Behavior

The persistent state declared here lives inside `drm_device->dev_private`, `drm_crtc->state`, and Rockchip encoder instances. `rockchip_crtc_state` is duplicated/reset by VOP/VOP2 CRTC hooks, while `rockchip_drm_private` persists for the DRM device lifetime and protects shared `drm_mm` state with `mm_lock`.

## Dependencies and Integration Points

The header depends on DRM atomic/GEM types, Linux component binding, I2C, modules, bits, and platform-driver declarations. It is included by framebuffer, GEM, VOP, VOP2, LVDS, RGB, and other Rockchip encoder drivers.

## Risks and Edge Cases

The output-mode constants are ABI-like hardware contracts; accidental renumbering would break register programming. `ROCKCHIP_OUT_MODE_P888` and `ROCKCHIP_OUT_MODE_BT1120` intentionally share value 0. `rockchip_crtc_state` fields are not self-validating, so bridge atomic checks must populate consistent combinations.

## Test Signals

Build tests should cover all Rockchip DRM configurations. Atomic modeset tests should confirm encoder atomic checks populate `rockchip_crtc_state` correctly for RGB, LVDS, HDMI, DSI, eDP, DP, and YUV bus formats. GEM stress should exercise concurrent IOMMU allocations under `mm_lock`.
