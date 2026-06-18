# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.h

Purpose: Declares the UVD 4.2 AMDGPU IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version uvd_v4_2_ip_block;` behind `__UVD_V4_2_H__`.

Control flow and integration: ASIC initialization code can include this header to add the CIK UVD 4.2 block to an IP block list.

State and persistence: No runtime state is stored here; all state is in the implementation and `adev->uvd`.

Dependencies and risks: Requires callers to have the AMDGPU IP block type available. Declaration drift would create compile or link failures.

Test signals: Successful compilation and linkage of ASIC tables referencing `uvd_v4_2_ip_block`.
