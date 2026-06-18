# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.h

Purpose: Declares the VCE 2.0 AMDGPU IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version vce_v2_0_ip_block;` behind `__VCE_V2_0_H__`.

Control flow and integration: Included by ASIC block selection code for CIK VCE 2.0.

State and persistence: None in the header.

Dependencies and risks: Requires matching symbol definition in `vce_v2_0.c` and visible AMDGPU IP block type declarations.

Test signals: Compile/link coverage in configurations that include VCE 2.0.
