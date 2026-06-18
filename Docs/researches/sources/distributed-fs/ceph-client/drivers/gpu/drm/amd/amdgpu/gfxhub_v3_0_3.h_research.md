# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.h

## Purpose
This header declares the GC 11.0.3-specific GFXHUB callback table.

## Important APIs, Types, and Functions
It exports `gfxhub_v3_0_3_funcs` as a `const struct amdgpu_gfxhub_funcs`. The table is selected by GMC v11 when the GC IP version requires GC 11.0.3 register programming.

## Control Flow and State
The header has no runtime flow. It enables linkage to the implementation that initializes `adev->vmhub` and hardware GCVM/GCMC registers.

## Dependencies and Integration Points
It depends on AMDGPU core type declarations in including files. Integration is with `gmc_v11_0.c`, VM fault processing, GART initialization, and reset/resume paths.

## Risks and Test Signals
Risks are compile/link mismatch and accidental selection for the wrong GC IP version. Tests should cover GC 11.0.3 boot, VM activity, and fault handling.
