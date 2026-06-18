# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v1_0.h

Purpose: Declares the VCE 1.0 IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version vce_v1_0_ip_block;` behind `__VCE_V1_0_H__`.

Control flow and integration: ASIC tables include this header when selecting the VCE 1.0 implementation.

State and persistence: No state is defined in the header.

Dependencies and risks: Header users must have AMDGPU IP block type definitions available. Symbol drift creates build or link failures.

Test signals: Successful compilation/linkage for SI VCE 1.0 configurations.
