<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.c

Purpose: defines MCA v3.0 RAS block descriptors for MP0, MP1, and MPIO machine-check banks. It supplies count-query callbacks that delegate to common MCA logic with block-specific SMN status-register addresses.

Important APIs and functions: `mca_v3_0_mp0_query_ras_error_count()`, `mca_v3_0_mp1_query_ras_error_count()`, and `mca_v3_0_mpio_query_ras_error_count()` call `amdgpu_mca_query_ras_error_count()` with `smnMCMP0_STATUST0`, `smnMCMP1_STATUST0`, or `smnMCMPIO_STATUST0`. `mca_v3_0_ras_block_match()` validates that an `amdgpu_ras_block_object` matches the requested RAS block and sub-block index. The exported `mca_v3_0_mp0_ras`, `mca_v3_0_mp1_ras`, and `mca_v3_0_mpio_ras` objects provide `ras_block.hw_ops` and the match callback.

Control flow: AMDGPU RAS registration code attaches one of the exported block objects. Later RAS queries call the relevant `query_ras_error_count` callback, which reads MCA count state through the shared MCA helper. Address queries are not implemented and are set to NULL.

State and persistence behavior: no dynamic state is allocated here. Persistent hardware state is in MCA SMN status registers. The exported RAS block structures are global descriptors whose function pointers remain constant.

Dependencies and integration points: depends on `amdgpu_ras.h`, `amdgpu_mca.h`, `struct amdgpu_mca_ras_block`, and the common RAS object matching contract. It integrates with ASIC-specific RAS setup that picks MP0/MP1/MPIO blocks.

Risks and edge cases: only count queries are supported, so address reporting is unavailable. Hard-coded SMN addresses must match MCA v3.0 hardware. `mca_v3_0_ras_block_match()` rejects null and exact block/sub-block mismatches but does no broader compatibility checks.

Test signals: RAS block registration for MP0, MP1, and MPIO, correct CE/UE count reporting from each SMN address, expected failure for mismatched sub-block index, and no calls to NULL address-query hooks in paths that require address details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.c -->
