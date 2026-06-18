# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.h

## Purpose
This header exposes the GFXHUB 1.2 callback table and XCP IP hooks used by GC 9.4.3-style multi-XCC devices.

## Important APIs, Types, and Functions
It declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v1_2_funcs;` and `extern struct amdgpu_xcp_ip_funcs gfxhub_v1_2_xcp_funcs;`. The first is assigned to `adev->gfxhub.funcs`; the second gives XCP partitioning code suspend/resume hooks that accept an instance mask.

## Control Flow and State
The header has no runtime flow. Its declarations connect GMC generation selection and XCP registration to the implementation in `gfxhub_v1_2.c`. State affected by the implementation includes per-XCC `adev->vmhub[]` register offsets and persistent GMC fault/cache configuration registers.

## Dependencies and Integration Points
Users must include or otherwise know `struct amdgpu_gfxhub_funcs` and `struct amdgpu_xcp_ip_funcs`. Integration points are GMC early initialization, GART enable/disable, VM fault policy, and XCP partition lifecycle.

## Risks and Test Signals
Declaration drift is the compile-time risk. Runtime confidence comes from successful linkage and from multi-XCC partition tests that call `gfxhub_v1_2_xcp_funcs` with partial instance masks without disturbing other partitions.
