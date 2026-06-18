# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.h

## Purpose
This header declares the GFXHUB 1.1 XGMI information helper for other AMDGPU source files. It is intentionally narrow: GFXHUB 1.1 in this subset contributes topology discovery rather than a whole public callback table.

## Important APIs, Types, and Functions
The exported prototype is `int gfxhub_v1_1_get_xgmi_info(struct amdgpu_device *adev);`. The function returns `0` on successful discovery or disabled XGMI, and `-EINVAL` for unsupported ASICs or invalid register-derived topology. The caller owns the `struct amdgpu_device` and reads the resulting `adev->gmc.xgmi` fields.

## Control Flow and State
The header itself has no runtime control flow. It establishes a compile-time contract for code that needs to query XGMI and then use the persisted GMC XGMI fields during VRAM/GART placement.

## Dependencies and Integration Points
It relies on a forward-visible `struct amdgpu_device` from the including translation unit. It is included by `gfxhub_v1_2.c` and other generation-specific GMC/GFXHUB code that can reuse the v1.1 topology convention.

## Risks and Test Signals
The main header-local risk is declaration drift if the implementation changes signature. Build coverage catches that. Runtime validation belongs to the `.c` implementation: multi-node XGMI address layout, hot reset, and VM fault-free access to remote/local VRAM segments.
