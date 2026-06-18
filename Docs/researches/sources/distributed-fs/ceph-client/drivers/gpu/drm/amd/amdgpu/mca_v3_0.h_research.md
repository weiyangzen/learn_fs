<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.h

Purpose: declares the MCA v3.0 MP0, MP1, and MPIO RAS block descriptors for use by AMDGPU RAS setup code.

Important APIs: exports `extern struct amdgpu_mca_ras_block mca_v3_0_mp0_ras`, `mca_v3_0_mp1_ras`, and `mca_v3_0_mpio_ras`.

Control flow and state: no executable logic or allocation. The declarations expose global descriptor instances implemented in `mca_v3_0.c`.

Dependencies and integration points: requires includers to know `struct amdgpu_mca_ras_block`, normally through AMDGPU MCA/RAS headers. ASIC initialization uses these symbols to attach the correct hardware ops.

Risks and test signals: risks are missing type declarations in includers or symbol drift. Compile/link and successful RAS block registration for all three MCA domains validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mca_v3_0.h -->
