# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.h

Purpose: declares the GC 12.1 GFXHUB function table and its XCP partition callback table.

Important APIs/types/functions: declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v12_1_funcs` and `extern struct amdgpu_xcp_ip_funcs gfxhub_v12_1_xcp_funcs`, both defined in `gfxhub_v12_1.c`.

Control flow: no runtime control flow. The declarations allow ASIC setup code to bind normal GFXHUB callbacks and XCP partition suspend/resume callbacks.

State and persistence behavior: no local state. The referenced tables have static driver/module lifetime and operate on per-device `adev->vmhub` and GMC state.

Dependencies and integration points: depends on AMDGPU type declarations for `amdgpu_gfxhub_funcs` and `amdgpu_xcp_ip_funcs`. Integrated by GC 12.1 ASIC initialization and XCP manager registration paths.

Risks and test signals: the header is small but exposes an additional mutable-looking non-const XCP table. Test signals are successful build/link and correct registration of both normal and partition-specific callbacks.
