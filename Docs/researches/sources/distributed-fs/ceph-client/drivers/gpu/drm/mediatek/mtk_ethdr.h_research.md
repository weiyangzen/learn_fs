# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.h

## Purpose
Declares the ETHDR component interface consumed by MediaTek display pipeline code.

## Important APIs, types, and functions
The header declares lifecycle hooks (`mtk_ethdr_start()`, `mtk_ethdr_stop()`, clock enable/disable), mode configuration (`mtk_ethdr_config()`), blend-mode discovery (`mtk_ethdr_get_blend_modes()`), layer programming (`mtk_ethdr_layer_config()`), and vblank callback registration/control helpers.

## Control flow
There is no runtime control flow in this header. It exposes a narrow procedural API around an opaque `struct device *` so callers do not need access to `struct mtk_ethdr`.

## State and persistence
No state is stored here. The declared functions mutate ETHDR hardware and internal callback state in `mtk_ethdr.c`.

## Dependencies and integration points
The declarations reference `struct cmdq_pkt`, `struct mtk_plane_state`, and Linux/DRM scalar types through transitive includes. The integration point is MediaTek CRTC/DDP component orchestration.

## Risks
Because the API is device-pointer based, incorrect device routing will not be caught by type checking. Header changes have build impact on MediaTek display component users.

## Test signals
Build coverage catches signature drift. Runtime validation belongs to ETHDR CRTC integration, especially blend modes, layer programming, vblank enable/disable, and clock sequencing.
