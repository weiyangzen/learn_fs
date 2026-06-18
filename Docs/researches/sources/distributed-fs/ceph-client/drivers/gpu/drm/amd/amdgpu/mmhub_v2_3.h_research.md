# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.h

Purpose: declares the MMHUB 2.3 function table used by AMDGPU generation selection code.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v2_3_funcs;`. The implementation provides GART, VM fault, invalidation, page-table, and clock-gating callbacks.

Control flow, state, and persistence: none in the header. Runtime state is maintained by `mmhub_v2_3.c` in MMHUB registers, `adev->vmhub`, and `adev->mmhub` client information.

Dependencies, integration, risks, and tests: requires AMDGPU MMHUB type definitions. Integration is via assigning the declared table to matching MMHUB 2.3 ASICs. Risks are declaration mismatch or wrong ASIC matching. Compile/link coverage and successful VM hub callback registration are primary signals.
