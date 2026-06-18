
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_rap.h

## Purpose
Declares the RAP debugfs initialization hook for AMDGPU.

## Important APIs, Types, and Functions
The only public declaration is `amdgpu_rap_debugfs_init(struct amdgpu_device *adev)`.

## Control Flow
Debugfs setup code can include this header and call the initializer; the implementation decides whether RAP is initialized enough to expose `rap_test`.

## State and Persistence Behavior
No state is defined here. It depends on `adev->psp.rap_context` managed by PSP code.

## Dependencies and Integration Points
Includes `amdgpu.h` for `struct amdgpu_device` and integrates with DRM debugfs setup plus the PSP RAP TA service.

## Risks and Test Signals
Risk is minimal; the important signal is that builds see the prototype and debugfs creation remains gated in the implementation. Test with RAP-capable and RAP-absent firmware.
