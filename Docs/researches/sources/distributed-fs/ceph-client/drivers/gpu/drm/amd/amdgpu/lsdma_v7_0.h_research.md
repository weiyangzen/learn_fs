<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.h

Purpose: declares the LSDMA 7.0 callback table.

Important APIs: includes `soc15_common.h` and exports `extern const struct amdgpu_lsdma_funcs lsdma_v7_0_funcs`.

Control flow and state: no executable control flow or storage; this is a header-level integration contract.

Dependencies and integration points: requires AMDGPU LSDMA type definitions from common headers. ASIC/IP setup code includes this header to bind v7.0 LSDMA operations.

Risks and test signals: declaration mismatch or missing type visibility would fail compile/link. Runtime validation is through successful invocation of v7.0 copy/fill and memory power-gating callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.h -->
