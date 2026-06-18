# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.h

## Purpose
`amdgpu_drv.h` is the small private driver header that exposes common AMDGPU DRM driver identity constants and ioctl entry points to files that need the driver-level declarations.

## Important APIs, types, and functions
It defines `DRIVER_AUTHOR`, `DRIVER_NAME`, and `DRIVER_DESC`, declares `extern const struct drm_driver amdgpu_partition_driver`, and declares `amdgpu_drm_ioctl()` plus the compat ioctl wrapper `amdgpu_kms_compat_ioctl()`.

## Control flow
The header has no executable control flow. It is consumed by `amdgpu_drv.c` and other driver files that need the canonical DRM driver name, description, or ioctl signatures.

## State and persistence behavior
No runtime state is allocated here. The macros become compile-time constants embedded in the DRM driver objects and module metadata.

## Dependencies and integration points
It includes Linux firmware/platform-device headers and `amd_shared.h`. The `amdgpu_partition_driver` declaration connects partition DRM devices with the primary driver definition in `amdgpu_drv.c`.

## Risks and edge cases
Changing driver identity strings affects module metadata and userspace-facing DRM naming. Prototype drift from `amdgpu_drv.c` or compat code would break builds. Because the partition driver is declared here, any partition-driver feature changes must stay synchronized with the definition in the C file.

## Test signals
Build coverage is the main signal. Runtime confirmation comes from DRM device names, module metadata, compat ioctl builds, and XCP partition device registration.
