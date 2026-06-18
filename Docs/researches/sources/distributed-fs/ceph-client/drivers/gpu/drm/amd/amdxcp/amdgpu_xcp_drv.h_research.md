# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.h

## Purpose
Declares the XCP DRM platform-device helper API.

## Important APIs, Types, And Functions
Exports prototypes for `amdgpu_xcp_drm_dev_alloc`, `amdgpu_xcp_drm_dev_free`, and `amdgpu_xcp_drv_release`.

## Control Flow
No implementation flow. Callers allocate a DRM device pointer, later free it, and can release all devices during teardown.

## State And Persistence
No state in the header. State lives in `amdgpu_xcp_drv.c`.

## Dependencies And Integration Points
Requires `struct drm_device` to be visible to including C files. Used by amdgpu/KFD XCP partition code that needs per-partition DRM render nodes.

## Risks
The API does not encode ownership beyond a raw pointer; callers must avoid double-free and must not pass unrelated DRM devices.

## Test Signals
Build coverage for users of the declarations and runtime allocation/free cycles through the implementation.
