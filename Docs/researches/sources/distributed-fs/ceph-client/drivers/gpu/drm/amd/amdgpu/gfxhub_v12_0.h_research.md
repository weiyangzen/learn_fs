# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.h

Purpose: declares the GC 12.0 GFXHUB function table used by AMDGPU device setup.

Important APIs/types/functions: declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v12_0_funcs`, defined in `gfxhub_v12_0.c`.

Control flow: no runtime control flow; this is a selection/export header.

State and persistence behavior: no local state. The referenced function table persists for the driver/module lifetime.

Dependencies and integration points: depends on AMDGPU core type declarations. Included by ASIC setup code that binds GC 12.0 GFXHUB callbacks.

Risks and test signals: the header is intentionally minimal. Test signal is successful compilation and link resolution of `gfxhub_v12_0_funcs`.
