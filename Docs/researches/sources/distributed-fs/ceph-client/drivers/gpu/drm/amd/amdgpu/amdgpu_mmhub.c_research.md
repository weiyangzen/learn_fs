## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.c

Purpose: provides shared MMHUB RAS software initialization.

Important APIs/functions: `amdgpu_mmhub_ras_sw_init()` registers `adev->mmhub.ras->ras_block` with the RAS framework, names it `"mmhub"`, marks the block as `AMDGPU_RAS_BLOCK__MMHUB`, sets type `AMDGPU_RAS_ERROR__MULTI_UNCORRECTABLE`, and stores `adev->mmhub.ras_if`.

Control flow: the function is a no-op if no MMHUB RAS object is installed. On registration failure it logs and returns the error. Late init is intentionally left to the default RAS block late-init behavior.

State and persistence: updates `adev->mmhub.ras_if` and the embedded RAS common descriptor in-memory. No persistence exists.

Dependencies/integration: depends on AMDGPU RAS registration and `struct amdgpu_mmhub` state configured by ASIC-specific MMHUB code.

Risks: assumes `adev->mmhub.ras` points to valid storage and that `ras_block.ras_comm.name` has enough space for `"mmhub"`. Missing RAS object silently disables MMHUB RAS registration.

Test signals: RAS-enabled boot should show MMHUB registered; RAS query/injection paths should find MMHUB as multi-uncorrectable, and late-init should follow default RAS behavior.
