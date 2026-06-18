# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.h

Purpose: declares the MMHUB 2.0/2.1 function table for AMDGPU ASIC initialization.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v2_0_funcs;`, implemented by `mmhub_v2_0.c`. No RAS object is declared for this generation in this header.

Control flow, state, and persistence: no runtime logic. The implementation owns VM hub register metadata, client-ID mappings, and hardware register programming state.

Dependencies, integration, risks, and tests: consumers must have `struct amdgpu_mmhub_funcs` visible. Integration is through IP-version selection that assigns this table to the device MMHUB callbacks. Risks are declaration/export mismatch and incorrect table selection for unsupported MMHUB 2.x variants. Compile/link coverage and successful GART/VM/fault callback registration are the main signals.
