# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.h

Purpose: declares the MMHUB 1.7 operation table and RAS block for AMDGPU ASIC selection code.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v1_7_funcs;` and `extern struct amdgpu_mmhub_ras mmhub_v1_7_ras;`. The function table provides GART/VM/fault/clock callbacks; the RAS object provides EDC counter and EA status callbacks.

Control flow, state, and persistence: none in the header. It is a declaration boundary for global objects whose implementation stores state in MMHUB registers, VM hub metadata, and generic RAS reporting structures.

Dependencies, integration, risks, and tests: consumers need AMDGPU MMHUB and RAS type definitions. Integration happens when IP-version matching assigns these exports to `adev->mmhub`/RAS setup. Risks are limited to mismatched declarations or accidental selection for a different MMHUB generation. Compile/link coverage plus successful ASIC bring-up and RAS registration are the key signals.
