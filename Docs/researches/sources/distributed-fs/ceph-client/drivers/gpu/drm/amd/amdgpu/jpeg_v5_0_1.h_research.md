<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.h

Purpose: declares the JPEG 5.0.1 IP block descriptor and local register constants used by `jpeg_v5_0_1.c` for JRBC ring registers, JMI stall/drop registers, core reset control, RRMT capability detection, and RAS sub-block selection.

Important APIs and types: exports `jpeg_v5_0_1_ip_block` for the AMDGPU IP discovery table. The `regUVD_JRBC*` constants provide per-ring RB write pointer, read pointer, and status offsets plus base-index metadata for ten JRBC rings. `regUVD_JMI0_*`, `regJPEG_CORE_RST_CTRL`, and `regVCN_RRMT_CNTL` support per-core stall/reset and capability probing. `enum amdgpu_jpeg_v5_0_1_sub_block` identifies `JPEG0`, `JPEG1`, and the maximum sub-block count for poison status queries.

Control flow and integration: this header has no executable control flow. It is included by the implementation so SOC15 helper macros can resolve local IP-version register names not provided by generated headers. The enum values are consumed by the RAS poison query loop.

State and persistence behavior: no runtime state is allocated here. The constants fix the ABI between driver code and hardware register layout; any mismatch persists as incorrect MMIO access in the implementation.

Dependencies: relies on the surrounding AMDGPU build including definitions for `struct amdgpu_ip_block_version`. The register naming follows generated AMD register-header conventions, allowing use in `SOC15_REG_ENTRY_STR`, `SOC15_REG_OFFSET`, and offset access macros.

Risks and test signals: risks are register-offset drift, incorrect base-index pairing, and sub-block enum mismatch with hardware poison status registers. Compile coverage of `jpeg_v5_0_1.c`, successful register dump initialization, ring rptr/wptr access for all ten rings, and poison status reads from both sub-blocks are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_1.h -->
