<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.h

Purpose: declares the JPEG 5.0.2 IP block descriptor and local register offsets used by the implementation for ten JRBC decode rings, JMI reset/stall/drop control, core reset, RRMT probing, and JPEG sub-block IDs.

Important APIs and types: exports `jpeg_v5_0_2_ip_block`. Defines `regUVD_JRBC0` through `regUVD_JRBC9` rptr/wptr/status offsets, scratch and external MCM offsets, JMI clean/stall/drop offsets, `regJPEG_CORE_RST_CTRL`, and `regVCN_RRMT_CNTL`. `enum amdgpu_jpeg_v5_0_2_sub_block` mirrors the two JPEG RAS sub-blocks even though the active v5.0.2 implementation has ACA/RAS support disabled under `#if 0`.

Control flow and integration: no executable logic. The constants are consumed by ring setup, ring pointer accessors, register dump setup, and reset code in `jpeg_v5_0_2.c`.

State and persistence behavior: the file stores no state; it defines the hardware address contract. Incorrect values would persist as incorrect ring pointer, status, or reset MMIO programming.

Dependencies: follows AMDGPU register macro conventions and requires `struct amdgpu_ip_block_version` from AMDGPU headers. The implementation pairs these defines with generated `vcn_5_0_0_*` headers.

Risks and test signals: risks include copy-forward offset mismatch from v5.0.1 and unused RAS enum drift. Compile success, ring rptr/wptr/status access on all ten rings, register dump inclusion, core reset behavior, and RRMT capability reads validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.h -->
