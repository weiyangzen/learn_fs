# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.h

Purpose: declares the MMHUB 1.0 function table and RAS block used by the AMDGPU memory-controller/GMC initialization code.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v1_0_funcs;` for MMHUB operations and `extern struct amdgpu_mmhub_ras mmhub_v1_0_ras;` for RAS hardware callbacks. The concrete structures are defined elsewhere in AMDGPU headers and initialized in `mmhub_v1_0.c`.

Control flow, state, and persistence: this header has no runtime logic. It exposes implementation-owned global objects; persistent state is in device registers, `adev->vmhub`, `adev->gmc`, and RAS data maintained by the implementation and generic AMDGPU subsystems.

Dependencies, integration, risks, and tests: consumers must include it in contexts with visible `struct amdgpu_mmhub_funcs` and `struct amdgpu_mmhub_ras` declarations. Integration is through ASIC/IP version selection that assigns function pointers and optional RAS handlers. Risks are declaration/export mismatch or selecting this table for unsupported hardware. Compile/link coverage and successful MMHUB/RAS registration are the primary test signals.
