# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.h

## Purpose
`amdgpu_dm_ism.h` declares AMDGPU DM idle state-management states, events, configuration, history records, per-CRTC storage, and lifecycle/event functions.

## Important APIs, types, and functions
It defines `enum amdgpu_dm_ism_state`, `enum amdgpu_dm_ism_event`, `STATE_EVENT()`, `struct amdgpu_dm_ism_config`, `struct amdgpu_dm_ism_record`, and `struct amdgpu_dm_ism`. Public functions are `amdgpu_dm_ism_init()`, `amdgpu_dm_ism_fini()`, `amdgpu_dm_ism_commit_event()`, `amdgpu_dm_ism_disable()`, and `amdgpu_dm_ism_enable()`.

## Control flow
The header defines the event vocabulary for idle enter/exit, cursor begin/end, timer elapsed, SSO timer elapsed, and immediate internal progression. The C file implements the FSM.

## State and persistence behavior
Declared structures are per-CRTC runtime state with a fixed 16-entry idle history and delayed work items. Nothing persists across teardown or reboot.

## Dependencies and integration points
It depends on Linux workqueues and forward declarations for AMDGPU CRTC/display-manager types. `ism_to_amdgpu_crtc()` requires the ISM object to be embedded in `struct amdgpu_crtc` as `ism`.

## Risks and edge cases
Enum ordering and sentinel values must stay aligned with implementation string tables and loop termination. Config values are frame counts, not milliseconds. The container macro is unsafe for standalone allocations.

## Test signals
Build coverage, CRTC embedding, initialization/finalization, event delivery from vblank/cursor paths, work enable/disable, and zero/nonzero config edge cases validate this header.
