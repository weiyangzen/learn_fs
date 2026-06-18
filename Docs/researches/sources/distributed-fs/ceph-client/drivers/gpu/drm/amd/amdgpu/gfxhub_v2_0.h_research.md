# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.h

## Purpose
This header declares the GFXHUB 2.0 callback table for GC 10.1/Navi 1x VM hub support.

## Important APIs, Types, and Functions
It exports `gfxhub_v2_0_funcs`, a `const struct amdgpu_gfxhub_funcs`. Consumers use it through `adev->gfxhub.funcs`, not by calling individual static functions.

## Control Flow and State
There is no runtime control flow. The declaration allows GMC v10 setup code to bind the correct GFXHUB implementation. The implementation persists VM hub register metadata in `adev->vmhub` and hardware VM/cache/fault settings in GCVM/GCMC registers.

## Dependencies and Integration Points
It requires the including C file to have the AMDGPU type definitions in scope. Integration is with `gmc_v10_0.c`, VM fault handling, GART enablement, and TLB invalidation.

## Risks and Test Signals
The header risk is symbol mismatch or missing implementation at link time. Runtime testing is driven by the `.c` callback table: Navi-class boot, GART allocation, VM fault decode, and TLB flush workloads.
