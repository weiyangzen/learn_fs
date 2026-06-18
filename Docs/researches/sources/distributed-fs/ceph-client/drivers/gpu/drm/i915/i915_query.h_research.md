# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.h

## Purpose

`i915_query.h` declares the DRM query ioctl entry point for the i915 driver. It is a narrow internal header used by the driver ioctl table to expose the implementation in `i915_query.c`.

## Important APIs, types, and functions

The only exported function is `int i915_query_ioctl(struct drm_device *dev, void *data, struct drm_file *file);`. The header forward declares `struct drm_device` and `struct drm_file` and uses an include guard.

## Control flow

There is no runtime control flow in the header. `i915_driver.c` includes it and registers `i915_query_ioctl` as the handler for `DRM_IOCTL_I915_QUERY`; all dispatch to individual query IDs happens in the C file.

## State and persistence behavior

The header owns no state. It defines the call boundary for a read-only discovery ioctl that snapshots driver state into userspace buffers.

## Dependencies

It depends only on DRM forward declarations. The implementation pulls in i915 and uAPI details separately.

## Integration points

The sole integration point is the i915 DRM ioctl table. Keeping this header small limits rebuild coupling for code that only needs to register the ioctl handler.

## Risks

Risks are limited to prototype drift or accidental inclusion of heavy dependencies. Any signature change must match the DRM ioctl handler convention exactly.

## Test signals

Build coverage of `i915_driver.c` and `i915_query.c` validates the declaration. Runtime query ioctl tests validate the actual implementation.
