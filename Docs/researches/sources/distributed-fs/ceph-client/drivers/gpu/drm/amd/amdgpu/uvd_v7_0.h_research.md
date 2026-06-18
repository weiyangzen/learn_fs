# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v7_0.h

Purpose: Declares the SOC15 UVD 7.0 IP block descriptor.

Important APIs and types: Exports `extern const struct amdgpu_ip_block_version uvd_v7_0_ip_block;` behind `__UVD_V7_0_H__`.

Control flow and integration: ASIC block tables include this header to attach UVD 7.0 lifecycle and ring functions implemented in the C file.

State and persistence: No state; all runtime data is in `adev->uvd` and firmware/virtualization structures.

Dependencies and risks: Requires consistent symbol definition in `uvd_v7_0.c`; any future minor descriptor would need a new declaration if exported.

Test signals: Build/link coverage for the exported symbol in SOC15 ASIC configurations.
