<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.h

Purpose: declares the LSDMA 7.1 callback table.

Important APIs: includes `soc15_common.h` and exports `extern const struct amdgpu_lsdma_funcs lsdma_v7_1_funcs`.

Control flow and state: none; the header only publishes the function-table symbol.

Dependencies and integration points: used by AMDGPU IP/ASIC setup paths that select LSDMA 7.1 behavior. Requires common AMDGPU LSDMA type declarations.

Risks and test signals: compile/link errors catch declaration drift. Runtime signal is successful copy/fill dispatch through the v7.1 table, with callers tolerating the missing memory power-gating member.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.h -->
