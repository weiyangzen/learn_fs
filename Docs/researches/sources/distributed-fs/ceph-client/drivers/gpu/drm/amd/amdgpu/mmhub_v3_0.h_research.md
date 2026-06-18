# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.h

Purpose: declares the MMHUB 3.0 function table for AMDGPU IP-version selection.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v3_0_funcs;`, implemented in `mmhub_v3_0.c`. The table includes VM/GART/fault/clock callbacks plus framebuffer base and MC framebuffer offset helpers.

Control flow, state, and persistence: this header has no behavior or storage. The implementation persists state in MMHUB registers and AMDGPU device metadata.

Dependencies, integration, risks, and tests: consumers need `struct amdgpu_mmhub_funcs` visible. Integration is via ASIC-specific assignment to `adev->mmhub.funcs`. Risks are limited to declaration mismatch or wrong generation selection. Compile/link coverage and successful v3.0 MMHUB callback registration are the test signals.
