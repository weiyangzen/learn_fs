# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.h

Purpose: provides the public declarations needed by the AMDGPU IP discovery and XCP partition layers for the GFX 9.4.3 implementation.

Important APIs/types/functions: declares `extern const struct amdgpu_ip_block_version gfx_v9_4_3_ip_block` and `extern struct amdgpu_xcp_ip_funcs gfx_v9_4_3_xcp_funcs`. These symbols are defined in `gfx_v9_4_3.c`.

Control flow: no runtime control flow. Inclusion allows device-specific IP tables to reference the GFX block version and optional per-partition suspend/resume hooks.

State and persistence behavior: no state is defined here. The declarations refer to global constant/function-table objects whose lifetime is the driver/module lifetime.

Dependencies and integration points: depends on prior visibility of `struct amdgpu_ip_block_version` and `struct amdgpu_xcp_ip_funcs` from AMDGPU headers. Integrated by ASIC discovery or IP block registration code that selects the GC 9.4.3 implementation.

Risks and test signals: the header intentionally exposes only two symbols; adding private implementation details here would widen coupling. Test signals are successful compilation of source files that include this header and correct link resolution to `gfx_v9_4_3.c`.
