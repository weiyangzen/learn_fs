# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_dsc_helper.h

## Purpose
Provides a shared MSM helper for Display Stream Compression line-size calculations used by DSI, DP, and timing-engine code.

## Important APIs, types, and functions
- `msm_dsc_get_bytes_per_line(const struct drm_dsc_config *dsc)` returns `slice_count * slice_chunk_size`.

## Control flow
Single inline arithmetic helper; no branching.

## State and persistence
No state.

## Dependencies and integration points
Depends on `drm/display/drm_dsc_helper.h` and `struct drm_dsc_config`. Callers convert this byte count into interface-specific timing values such as pclk-per-interface.

## Risks
The helper assumes `slice_chunk_size` is already computed correctly by DRM DSC helpers. Widebus or interface division must be handled by callers, not here.

## Test signals
Compile coverage and caller tests comparing DSI/DP timing math against expected DSC slice counts and chunk sizes.
