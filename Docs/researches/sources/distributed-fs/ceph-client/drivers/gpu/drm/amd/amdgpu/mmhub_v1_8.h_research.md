# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.h

Purpose: declares the MMHUB 1.8 operations and RAS integration objects.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v1_8_funcs;` and `extern struct amdgpu_mmhub_ras mmhub_v1_8_ras;`. The implementation supplies multi-AID VM/GART callbacks and status-register/ACA-based RAS callbacks.

Control flow, state, and persistence: this header has no runtime behavior. It exposes implementation globals; all state is in `adev->vmhub[]`, MMHUB registers, PSP-mediated register state, and generic AMDGPU RAS structures.

Dependencies, integration, risks, and tests: requires consumers to have AMDGPU MMHUB/RAS type declarations. It integrates through ASIC discovery and RAS block registration. Main risks are selecting this multi-AID implementation for an incompatible ASIC or declaration mismatch. Compile/link coverage, MMHUB function-table assignment, and RAS late-init binding are the test signals.
