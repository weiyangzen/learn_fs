# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.h

Purpose: small public header for CIK common support shared by AMDGPU CIK IP blocks.

Important APIs and constants: defines `CIK_FLUSH_GPU_TLB_NUM_WREG` as the number of register writes needed for a CIK GPU TLB flush sequence. Declares `cik_srbm_select()` for selecting ME/pipe/queue/VMID indexed register instances, `cik_set_ip_blocks()` for adding ASIC-specific IP blocks to an AMDGPU device, and `legacy_doorbell_index_init()` for legacy doorbell setup.

Control flow: the header has no implementation. Its declarations support the startup path where common CIK code installs IP blocks and other blocks, especially SDMA/GFX, select indexed registers during initialization or command emission.

State and persistence: stateless header. Declared functions mutate hardware register selection, device IP block lists, and doorbell-index layout.

Dependencies and integration points: depends on `struct amdgpu_device` and fixed-width AMDGPU integer types from including context. Used by `cik.c`, `cik_sdma.c`, and other CIK-generation blocks.

Risks: the TLB flush constant must stay aligned with the actual GMC flush emission sequence used by SDMA ring sizing. Prototype drift can break cross-IP initialization. `cik_srbm_select()` users must restore default selection after indexed access.

Test signals: CIK build coverage, VM flush ring emission sizing tests, and runtime validation of IP block addition and indexed register programming.
