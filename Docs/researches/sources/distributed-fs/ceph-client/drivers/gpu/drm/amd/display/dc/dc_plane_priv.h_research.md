# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane_priv.h

## Purpose
`dc_plane_priv.h` declares internal plane-state helpers for construction, destruction, and pipe-mask lookup.

## Important APIs
`dc_plane_construct` initializes a `dc_plane_state` with a `dc_context`. `dc_plane_destruct` tears down owned resources. `dc_plane_get_pipe_mask` returns the pipe mask in a `dc_state` associated with a plane state.

## Control Flow And State
The header has no implementation. It separates private construction/destruction from public retain/release and gives internal code a way to inspect resource assignment state for a plane.

## Dependencies And Integration Points
It includes `dc_plane.h` and uses `struct dc_state`. Resource management, plane lifecycle implementation, and state validation consume these declarations.

## Risks
These functions are internal and can bypass public lifecycle expectations if misused. Pipe-mask lookup depends on a coherent `dc_state`; stale state could produce wrong resource masks.

## Test Signals
Plane creation/destruction tests, pipe assignment validation, SubVP/phantom plane interactions, and resource leak checks are relevant.
