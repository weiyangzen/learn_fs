# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.h

## Purpose
This header declares ATHUB v3.0 clock-gating entry points.

## Important APIs, types, and functions
It declares `athub_v3_0_set_clockgating()` and `athub_v3_0_get_clockgating()`.

## Control flow
No executable logic is present.

## State and persistence behavior
The header holds no state; implementation state is hardware register state.

## Dependencies
AMDGPU device and clock-gating types must already be declared for includers.

## Integration points
ATHUB v3.x IP block code includes this header to wire power-management callbacks.

## Risks and edge cases
The simple header depends on include order and compile coverage.

## Test signals
Successful compilation of v3.x ATHUB users is the direct signal.
