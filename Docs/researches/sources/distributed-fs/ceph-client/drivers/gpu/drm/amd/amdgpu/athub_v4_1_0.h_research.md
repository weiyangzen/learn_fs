# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.h

## Purpose
This header declares the ATHUB v4.1.0 clock-gating callbacks.

## Important APIs, types, and functions
It exposes `athub_v4_1_0_set_clockgating()` and `athub_v4_1_0_get_clockgating()`.

## Control flow
The file is declarative only.

## State and persistence behavior
No state is declared here.

## Dependencies
It assumes AMDGPU clock-gating types are visible before inclusion.

## Integration points
ATHUB 4.1.0 IP setup includes this header to bind the versioned implementation.

## Risks and edge cases
The header is minimal; include-order and signature drift are the main risks.

## Test signals
Compile coverage of ATHUB 4.1.0 users validates it.
