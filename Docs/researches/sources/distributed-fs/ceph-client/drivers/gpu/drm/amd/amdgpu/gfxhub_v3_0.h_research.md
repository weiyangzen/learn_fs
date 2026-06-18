# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.h

## Purpose
This header declares the GFXHUB 3.0 callback table for GC 11-generation VM hub support.

## Important APIs, Types, and Functions
It exports `gfxhub_v3_0_funcs` as a `const struct amdgpu_gfxhub_funcs`. Consumers select it through generation-specific GMC setup, then use the callback table indirectly via `adev->gfxhub.funcs`.

## Control Flow and State
There is no executable flow in the header. Runtime state is created by the implementation when it initializes `adev->vmhub[AMDGPU_GFXHUB(0)]` and programs GCVM/GCMC registers.

## Dependencies and Integration Points
The header expects AMDGPU core type definitions to be available. It integrates with `gmc_v11_0.c`, fault handling, GART setup, and VM invalidation.

## Risks and Test Signals
Header risk is compile/link mismatch. Runtime test signals include GC 11 hardware initialization, GART enable log output, VM faults, and suspend/resume behavior.
