# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.h

## Purpose
This header declares the ATHUB v2.0 clock-gating API.

## Important APIs, types, and functions
It declares `athub_v2_0_set_clockgating()` and `athub_v2_0_get_clockgating()` with the standard AMDGPU clock-gating callback shape.

## Control flow
The file is declarative only.

## State and persistence behavior
No state is stored in the header; the implementation mutates hardware state through `amdgpu_device`.

## Dependencies
The header assumes AMDGPU core type declarations are already available to the includer.

## Integration points
IP block and power-management code include it to bind the v2.0 ATHUB implementation.

## Risks and edge cases
Include-order dependency is the main risk. Any signature mismatch would be caught by compiler users.

## Test signals
Compile coverage of ATHUB v2.0 users validates the header.
