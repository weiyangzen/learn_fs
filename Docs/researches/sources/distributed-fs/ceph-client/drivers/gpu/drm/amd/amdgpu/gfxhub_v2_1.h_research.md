# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.h

## Purpose
This header declares the GFXHUB 2.1 callback table used by GMC v10 for GC 10.3-generation devices.

## Important APIs, Types, and Functions
It exports `gfxhub_v2_1_funcs` as a `const struct amdgpu_gfxhub_funcs`. The table contains the standard VM hub callbacks and extra function pointers for UTCL2 harvest, mode2 register save/restore, and halt support.

## Control Flow and State
The header has no runtime behavior. Its symbol lets `gmc_v10_0_set_gfxhub_funcs()` bind GC 10.3 devices to the v2.1 implementation, which then persists VM hub register offsets and mode2 state in `adev->vmhub` and `adev->gmc`.

## Dependencies and Integration Points
Compilation depends on AMDGPU core type definitions being visible. Runtime integration is with GART enablement, GFXOFF/S0ix flows, VM faults, and hardware reset/harvest handling.

## Risks and Test Signals
Compile/link coverage validates the declaration. Runtime confidence comes from GC 10.3 board boot, reset, mode2 save/restore, VF operation, and UTCL2 harvest testing.
