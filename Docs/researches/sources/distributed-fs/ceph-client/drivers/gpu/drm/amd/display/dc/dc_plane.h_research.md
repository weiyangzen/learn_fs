# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane.h

## Purpose
`dc_plane.h` declares the public plane-state lifecycle and utility API for DC. It is the interface for creating, retaining, releasing, querying status, disabling DCC/tiling, and copying plane configuration.

## Important APIs
`dc_create_plane_state` allocates a new plane state for a `dc`. `dc_plane_state_retain` and `dc_plane_state_release` manage reference lifetime. `dc_plane_get_status` returns a `dc_plane_status` with requested update flags from `union dc_plane_status_update_flags`, currently address and histogram. `dc_plane_force_dcc_and_tiling_disable` mutates a plane state to disable DCC and optionally clear tiling. `dc_plane_copy_config` copies plane configuration from one state to another.

## Control Flow And State
The header contains no implementation. Plane state objects are persistent, reference-counted DC objects whose configuration is attached to streams through `dc_state` operations and committed later to hardware.

## Dependencies And Integration Points
It includes `dc_hw_types.h`, using plane address, format, tiling, and related hardware types. It integrates with DC state management, stream updates, resource validation, scaler programming, flip handling, and histogram/status queries.

## Risks
The API mutates shared plane state, so callers must respect retain/release and locking conventions. Disabling DCC/tiling can alter bandwidth and memory interpretation, so it should be used only for fallback or compatibility paths. Status update flags may trigger hardware reads in implementation and should be kept narrow.

## Test Signals
Plane lifecycle tests, attach/detach through `dc_state`, DCC/tiling fallback modes, flips with dirty rects, histogram status reads, and refcount leak checks are the key signals.
