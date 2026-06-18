# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.h

Purpose: Declares the UVD 5.0 IP block descriptor.

Important APIs and types: Provides `extern const struct amdgpu_ip_block_version uvd_v5_0_ip_block;` behind `__UVD_V5_0_H__`.

Control flow and integration: Used by ASIC-specific block tables to select the UVD 5.0 implementation.

State and persistence: None in the header; the declared block metadata is defined in `uvd_v5_0.c`.

Dependencies and risks: Depends on the including translation unit knowing `struct amdgpu_ip_block_version`. Header/API drift would surface at build or link time.

Test signals: Compile and link coverage for ASIC tables referencing the symbol.
