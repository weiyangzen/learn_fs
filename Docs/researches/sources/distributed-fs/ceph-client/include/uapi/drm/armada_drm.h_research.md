# sources/distributed-fs/ceph-client/include/uapi/drm/armada_drm.h

## Purpose
Defines the small Armada DRM driver ioctl ABI for GEM buffer creation, mmap offset lookup, and CPU writes.

## Important APIs, Types, And Functions
Exports command IDs `DRM_ARMADA_GEM_CREATE`, `DRM_ARMADA_GEM_MMAP`, `DRM_ARMADA_GEM_PWRITE`, macro `ARMADA_IOCTL`, structs `drm_armada_gem_create`, `drm_armada_gem_mmap`, `drm_armada_gem_pwrite`, and matching `DRM_IOCTL_ARMADA_*` values.

## Control Flow
No executable flow. The intended sequence is create GEM, request mmap information, map or write buffer contents, and hand the GEM object to KMS/driver paths.

## State, Persistence, And Dependencies
Kernel state consists of GEM objects and mmap offsets associated with a DRM file. `pwrite` copies user memory into a GEM buffer at a byte offset. It depends on `drm.h`.

## Integration Points
Used by Armada userspace drivers/tools and the Armada kernel DRM ioctl handlers. It relies on generic DRM command numbering and GEM handle lifetime rules.

## Risks
The `pwrite` payload has a user pointer, handle, offset, and size, so bounds checking and overflow handling are essential. The simple 32-bit size/offset fields limit maximum operation sizes.

## Test Signals
GEM create/mmap/pwrite ioctl tests, invalid handle tests, out-of-bounds pwrite rejection, mmap offset mapping tests, and 32/64-bit userspace pointer compatibility tests.
