# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.h

## Purpose
This header declares the i915 GETPARAM ioctl handler.

## Important APIs, Types, and Functions
It declares `int i915_getparam_ioctl(struct drm_device *dev, void *data, struct drm_file *file_priv)`.

## Control Flow
No control flow is present. `i915_driver.c` registers the function in `i915_ioctls[]` for `DRM_IOCTL_I915_GETPARAM`.

## State and Persistence Behavior
The header stores no state; the implementation reads device capability state.

## Dependencies and Integration Points
It forward-declares DRM device/file types and bridges the ioctl table to `i915_getparam.c`.

## Risks
Signature drift breaks ioctl registration. The lightweight header should stay free of unnecessary dependencies.

## Test Signals
Build coverage and GETPARAM ioctl tests.
