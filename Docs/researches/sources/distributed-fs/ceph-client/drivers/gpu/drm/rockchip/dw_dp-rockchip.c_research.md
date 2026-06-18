# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_dp-rockchip.c

## Purpose
Provides Rockchip glue for Synopsys DesignWare DisplayPort controllers on RK3576 and RK3588.

## Important APIs, Types, And Functions
Defines `struct rockchip_dw_dp`, the encoder atomic check callback, component bind ops, platform probe/remove, and per-SoC `dw_dp_plat_data` entries for maximum link rate and pixel mode.

## Control Flow
Probe registers a component. Bind allocates runtime state, finds platform data from DT match, creates a DRM encoder, records CRTC endpoint ID, binds the DW DP bridge core, creates a bridge connector, and attaches the connector to the encoder. Atomic check reads the first bridge input bus format and maps it to Rockchip output mode, bus format, bus flags, and color space.

## State And Persistence
State is small: the DW DP core handle, device pointer, and embedded Rockchip encoder. Hardware persistence is delegated to the DW DP bridge core.

## Dependencies And Integration Points
Integrates with `drm/bridge/dw_dp`, bridge connector helpers, media bus format definitions, V4L2 color space constants, DRM OF graph, and Rockchip encoder endpoint metadata.

## Risks
Atomic check expects bridge state and first bridge to exist. Unsupported bus formats fall back to `ROCKCHIP_OUT_MODE_AAAA`, which may hide mismatches. Remove retrieves driver data that is only set during bind, so lifecycle ordering depends on component behavior.

## Test Signals
RK3576/RK3588 probe, connector creation, each supported RGB/YUV bus format, endpoint ID mapping, and bridge-state availability during atomic check.
