# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/Makefile

## Purpose
Builds the AMD XCP helper module object as part of the amdgpu DRM build.

## Important APIs, Types, And Functions
Defines `amdxcp-y := amdgpu_xcp_drv.o` and adds `amdxcp.o` to `obj-$(CONFIG_DRM_AMDGPU)`.

## Control Flow
Kbuild compiles `amdgpu_xcp_drv.c` into the composite `amdxcp.o` when `CONFIG_DRM_AMDGPU` is enabled.

## State And Persistence
No runtime state. Build output affects module/object composition.

## Dependencies And Integration Points
Depends on the parent amdgpu Kbuild context and the `CONFIG_DRM_AMDGPU` option. It packages the exported XCP platform DRM-device allocation helpers for amdgpu users.

## Risks
If this Makefile is not included from the parent build, exported XCP symbols will be unavailable. The object is tied to amdgpu configuration rather than a separate XCP config switch.

## Test Signals
Kernel build with `CONFIG_DRM_AMDGPU=y/m` should produce `amdxcp.o` and resolve `amdgpu_xcp_drm_dev_alloc/free/release` symbols.
