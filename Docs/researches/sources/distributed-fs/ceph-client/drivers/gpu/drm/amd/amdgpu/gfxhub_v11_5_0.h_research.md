# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.h

Purpose: declares the GC 11.5.0 GFXHUB function table for AMDGPU ASIC setup code.

Important APIs/types/functions: declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v11_5_0_funcs`, defined by `gfxhub_v11_5_0.c`.

Control flow: no runtime control flow. Including code selects this table when binding a GC 11.5.0 GFXHUB implementation.

State and persistence behavior: no local state. The exported function table has static driver lifetime.

Dependencies and integration points: depends on `struct amdgpu_gfxhub_funcs` being available from AMDGPU headers. Integrates with GMC/GFXHUB selection code.

Risks and test signals: narrow header surface minimizes coupling. Test signal is build/link success for ASIC code referencing `gfxhub_v11_5_0_funcs`.
