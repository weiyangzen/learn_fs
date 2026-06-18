# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ioc32.c

## Purpose
`amdgpu_ioc32.c` provides the 32-bit compatibility ioctl entry point for AMDGPU DRM on 64-bit kernels. It decides whether a compat ioctl should use generic DRM compatibility handling or the AMDGPU DRM ioctl path.

## Important APIs, types, and functions
The single exported function is `amdgpu_kms_compat_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)`.

## Control flow
The function extracts the DRM ioctl number with `DRM_IOCTL_NR(cmd)`. Commands below `DRM_COMMAND_BASE` are core DRM ioctls and are delegated to `drm_compat_ioctl()`. Driver-private command numbers are passed directly to `amdgpu_drm_ioctl()`.

## State and persistence behavior
The file maintains no state. It forwards ioctl arguments to existing DRM/AMDGPU handlers.

## Dependencies and integration points
It depends on Linux compat support, DRM ioctl helpers, the AMDGPU UAPI command base, and `amdgpu_drm_ioctl()` from the driver. It is wired into the file operations for compat userspace.

## Risks and edge cases
Correct routing depends on the DRM command-number split. Driver-private AMDGPU ioctls must already be compat-safe or perform their own structure translation. Generic DRM ioctls rely on `drm_compat_ioctl()`.

## Test signals
Run 32-bit userspace ioctl smoke tests on a 64-bit kernel, including core DRM ioctls and AMDGPU private KMS/GEM/CS ioctls, and verify invalid command handling matches native ioctl behavior.
