# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wait_user_fence.h

## Purpose

`xe_wait_user_fence.h` declares the Xe user-fence wait ioctl entry point for use by the driver ioctl table and related Xe DRM code.

## Important APIs, Types, And Functions

It forward declares `struct drm_device` and `struct drm_file`, then exports `int xe_wait_user_fence_ioctl(struct drm_device *dev, void *data, struct drm_file *file)`.

## Control Flow

The header has no runtime control flow. It is included by the implementation and by whichever file wires the ioctl into Xe's DRM ioctl dispatch.

## State And Persistence Behavior

The header owns no state. Its include guard `_XE_WAIT_USER_FENCE_H_` prevents duplicate declarations.

## Dependencies And Integration Points

It deliberately avoids pulling in large DRM headers by using forward declarations. Integration is the C ABI contract between Xe ioctl registration and `xe_wait_user_fence.c`.

## Risks And Test Signals

Risk is limited to declaration drift if the implementation signature changes. Compile coverage of the ioctl table and implementation is the primary test signal.
