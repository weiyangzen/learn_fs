# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.h

## Purpose
Defines MediaTek DRM plane state extensions and AFBC layout constants, and declares plane initialization.

## Important APIs, types, and functions
- AFBC constants define 32x8 data blocks, 16-byte header blocks, and 1024-byte header alignment.
- `struct mtk_plane_pending_state` carries configuration to be consumed by CRTC/display components.
- `struct mtk_plane_state` embeds `struct drm_plane_state` plus pending state.
- `to_mtk_plane_state()` provides container conversion.
- `mtk_plane_init()` is the exported initializer.

## Control flow
Only the inline `to_mtk_plane_state()` helper executes code; it maps a DRM plane state pointer to the MediaTek wrapper.

## State and persistence
The pending state fields persist across atomic state duplication and are copied in `mtk_plane_duplicate_state()`. Dirty flags indicate whether CRTC code must program new state, including async updates.

## Dependencies and integration points
Depends on DRM CRTC types and Linux scalar types. The header is consumed by MediaTek plane, CRTC, ETHDR, RDMA, and other display component code that reads pending plane configuration.

## Risks
The pending state is a cross-module contract; adding fields or changing semantics requires updating every component that consumes it. The `config` and `async_config` fields are declared here but not managed in `mtk_plane.c`, so their meaning is owned elsewhere.

## Test signals
Build coverage catches struct layout/prototype changes. Runtime signals are correct CRTC consumption of pending enable, dirty, async_dirty, address, format, modifier, geometry, rotation, blend, and color-encoding fields.
