# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v1_0.h

## Purpose
This header declares the ATHUB v1.0 clock-gating interface used by AMDGPU IP block setup code.

## Important APIs, types, and functions
It declares `athub_v1_0_set_clockgating(struct amdgpu_device *adev, enum amd_clockgating_state state)` and `athub_v1_0_get_clockgating(struct amdgpu_device *adev, u64 *flags)`.

## Control flow
There is no runtime flow in the header. It supplies prototypes for the implementation in `athub_v1_0.c`.

## State and persistence behavior
No state is defined. The declared functions operate on `amdgpu_device` hardware clock-gating state and caller-provided flag storage.

## Dependencies
The prototypes rely on `struct amdgpu_device`, `enum amd_clockgating_state`, and `u64` being visible to includers through broader AMDGPU headers.

## Integration points
ATHUB v1.x IP block registration and power-management code include this header to call the versioned set/get functions.

## Risks and edge cases
The header has no include of AMDGPU types, so include order matters. Prototype drift from the implementation would break compile coverage.

## Test signals
Compile testing of ATHUB v1.x users is the main signal.
