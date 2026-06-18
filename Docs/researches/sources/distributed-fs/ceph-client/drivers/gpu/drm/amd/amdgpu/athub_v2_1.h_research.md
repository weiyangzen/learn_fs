# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.h

## Purpose
This header declares the ATHUB v2.1 clock-gating callbacks.

## Important APIs, types, and functions
It exposes `athub_v2_1_set_clockgating()` and `athub_v2_1_get_clockgating()`.

## Control flow
No executable flow is present.

## State and persistence behavior
The header defines no state; implementation state is hardware register state.

## Dependencies
It relies on includers having AMDGPU clock-gating types in scope.

## Integration points
Used by AMDGPU ATHUB v2.1/v2.4 IP registration and power-management code.

## Risks and edge cases
Include-order and prototype drift are the main risks.

## Test signals
Compile coverage of users validates it.
