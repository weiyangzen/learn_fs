# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state_priv.h

## Purpose
`dc_state_priv.h` declares internal state helpers for stream lookup, SubVP/MALL classification, phantom stream/plane lifecycle, FAMS2 detection, and cursor-limit bookkeeping.

## Important APIs
Lookup and classification APIs include `dc_state_get_stream_from_id`, `dc_state_get_pipe_subvp_type`, `dc_state_get_stream_subvp_type`, and `dc_state_get_paired_subvp_stream`.

Phantom resource APIs include `dc_state_create_phantom_stream`, `dc_state_create_phantom_plane`, release functions, add/remove phantom stream and plane functions, bulk add/remove for phantom planes, `dc_state_remove_phantom_streams_and_planes`, and `dc_state_release_phantom_streams_and_planes`.

Feature/status helpers include `dc_state_is_fams2_in_use`, cursor/SubVP limit setters/getters, `dc_state_can_clear_stream_cursor_subvp_limit`, and `dc_state_is_subvp_in_use`.

## Control Flow And State
The header describes the internal flow for SubVP: create phantom stream/plane paired with a main stream/plane, add them to state with metadata, later remove and release them. Cursor-limit functions persist per-stream constraints in state so SubVP and hardware cursor support can coordinate. FAMS2 and SubVP detection inspect current resource assignments.

## Dependencies And Integration Points
It includes `dc_state.h` and `dc_stream.h`. It integrates with SubVP, MALL, FAMS2, resource validation, phantom pipe allocation, cursor programming constraints, and commit cleanup.

## Risks
Phantom resources have paired lifetimes with main resources; leaks or double releases can corrupt state. Removing phantom streams without releasing planes, or vice versa, can leave stale pointers in stream statuses. Cursor-limit flags are stateful constraints and must be cleared only when safe.

## Test Signals
SubVP enable/disable scenarios, phantom stream/plane allocation failures, cleanup after validation failure, cursor size limit transitions, FAMS2 state detection, and state copy/release stress are the relevant signals.
