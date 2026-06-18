# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.h

## Purpose
This header exposes the optional VIDI connection IOCTL hook to the Exynos DRM core. It lets `exynos_drm_drv.c` wire the IOCTL when VIDI support is enabled while compiling to a NULL handler otherwise.

## Important APIs, Types, and Functions
When `CONFIG_DRM_EXYNOS_VIDI` is enabled, it declares `int vidi_connection_ioctl(struct drm_device *drm_dev, void *data, struct drm_file *file_priv);`. When disabled, it defines `vidi_connection_ioctl` as `NULL`, allowing the driver IOCTL table to compile without conditional call-site logic.

## Control Flow
There is no runtime flow in the header. At compile time, the preprocessor selects either the real function declaration or the NULL macro. At runtime, the DRM IOCTL dispatcher calls the function only when the driver table contains the real symbol.

## State and Persistence Behavior
The header stores no state. It controls availability of VIDI's connection state machine by build configuration only.

## Dependencies and Integration Points
The prototype depends on DRM core types `struct drm_device` and `struct drm_file`, usually provided through the including Exynos DRM driver headers. Its main integration point is the `DRM_IOCTL_DEF_DRV(EXYNOS_VIDI_CONNECTION, ...)` entry.

## Risks
The NULL macro form means consumers must only use the symbol in contexts where a NULL function pointer is valid. If a caller tried to invoke it directly while VIDI is disabled, it would become an invalid call through NULL. Build coverage should include both enabled and disabled configurations.

## Test Signals
Compile with `CONFIG_DRM_EXYNOS_VIDI=y/m` and confirm the IOCTL resolves to the real implementation. Compile with VIDI disabled and confirm the Exynos DRM driver still builds and the IOCTL table safely omits or rejects the VIDI operation according to core DRM behavior.
