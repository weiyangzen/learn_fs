# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.c

## Purpose

`rockchip_rgb.c` implements an optional internal RGB output helper used by VOP/VOP2 when the display controller directly exposes an RGB/DPI-style panel or bridge. It creates a simple DRM encoder, attaches a panel/bridge connector, and fills Rockchip CRTC output mode during atomic checks.

## Important APIs, Types, and Functions

- `struct rockchip_rgb` stores device/DRM pointers, bridge, embedded `rockchip_encoder`, connector storage, and output mode.
- `rockchip_rgb_encoder_atomic_check` maps connector bus formats to P666, P565, or P888 and sets Rockchip output state.
- `rockchip_rgb_init()` scans an OF graph port, ignores endpoints owned by subdrivers, resolves a panel or bridge, creates a simple encoder, attaches helper funcs, wraps panels, attaches a bridge connector, records `crtc_endpoint_id`, and returns the helper object.
- `rockchip_rgb_fini()` removes the panel bridge and cleans connector/encoder state.

## Control Flow

VOP or VOP2 calls `rockchip_rgb_init` when internal RGB output may exist. The helper scans the selected video port endpoints; if no non-subdriver child exists, it returns NULL. If a panel/bridge is found, it builds encoder and connector objects attached to the supplied CRTC. During atomic check, the encoder maps display bus format to Rockchip output mode.

## State and Persistence Behavior

The allocated object is devm-managed by the display controller device and persists until controller unbind. The bridge pointer may be a panel bridge created here or an existing bridge. `crtc_endpoint_id` persists in the embedded Rockchip encoder for VOP2 output mux selection.

## Dependencies and Integration Points

The file depends on DRM bridge, panel, bridge connector, simple encoder, OF graph, media bus formats, and Rockchip endpoint helpers. It integrates with legacy VOP and VOP2 optional RGB paths.

## Risks and Edge Cases

The atomic check sets `output_type` to `DRM_MODE_CONNECTOR_LVDS` even for RGB/DPI-style output. `rgb->connector` is embedded, but `drm_bridge_connector_init` returns a connector pointer that is reassigned locally; `rockchip_rgb_fini` cleanup should be reviewed. Panel bridge cleanup on attach failures also deserves attention.

## Test Signals

Test no-endpoint, deferred-probe, panel, and bridge cases; endpoint filtering; bus format mapping; VOP2 endpoint ID muxing; connector cleanup under unbind; and probe/remove leak detection.
