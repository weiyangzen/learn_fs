# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.h

## Purpose

`xe_vm_madvise.h` is the public declaration header for the Xe VM madvise ioctl implementation. It exposes the ioctl entry point without leaking internal madvise helper structures.

## Important APIs, Types, and Functions

The only function declared is `xe_vm_madvise_ioctl(struct drm_device *dev, void *data, struct drm_file *file)`. The header forward-declares `struct drm_device`, `struct drm_file`, and `struct xe_bo`; the `xe_bo` forward declaration is currently not used by the visible prototype but keeps the header ready for BO-related madvise integration.

## Control Flow and State

The header contains no state and no executable control flow. It exists so the DRM ioctl dispatch table or other Xe VM code can call into `xe_vm_madvise.c`.

## Dependencies and Integration Points

The integration point is the DRM ioctl layer for `DRM_IOCTL_XE_MADVISE`. Implementation dependencies remain private to the C file, keeping compile dependencies for callers minimal.

## Risks and Edge Cases

The main risk is API drift: if the ioctl signature or dispatch expectations change, this header and the implementation must stay synchronized. Because it intentionally hides internal state, any future helper exported here should be reviewed to avoid exposing lock-order-sensitive madvise internals.

## Test Signals

Build coverage confirms the ioctl prototype matches the implementation and call sites. Runtime test signals live in `xe_vm_madvise.c` ioctl tests.
