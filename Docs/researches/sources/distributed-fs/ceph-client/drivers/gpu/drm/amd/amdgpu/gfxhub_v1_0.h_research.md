# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.h

## Purpose
This header is the public declaration point for the GFXHUB 1.0 backend used by the AMDGPU GMC code on older Vega-era GC 9 hardware. It exposes `gfxhub_v1_0_funcs`, a `const struct amdgpu_gfxhub_funcs` implemented in the matching `gfxhub_v1_0.c` and selected by generation-specific GMC code such as `gmc_v9_0.c`.

## Important APIs, Types, and Functions
The only exported symbol is `gfxhub_v1_0_funcs`. The type is defined elsewhere in the AMDGPU core and supplies callbacks for VM hub register initialization, GART enable/disable, page-table base programming, fault-default policy, and related GFX VM-hub services. This header relies on including translation units already knowing `struct amdgpu_gfxhub_funcs`.

## Control Flow and State
There is no executable control flow or persistent state in the header. Its effect is compile-time linkage: users include it so they can assign `adev->gfxhub.funcs` to the v1.0 callback table during GMC early initialization.

## Dependencies and Integration Points
The include guard `__GFXHUB_V1_0_H__` prevents duplicate declarations. Integration is with AMDGPU device setup code that switches callback tables by GC IP version. The callbacks eventually operate on `adev->vmhub[AMDGPU_GFXHUB(0)]`, GART objects, VM manager sizing, and SOC15 register offsets.

## Risks and Test Signals
The main risk is wrong function-table selection rather than header-local behavior. Compile/link tests catch missing or mismatched `gfxhub_v1_0_funcs`; boot/resume on GC 9 boards validates the callback table, GART enablement, TLB invalidation, and VM fault handling.
