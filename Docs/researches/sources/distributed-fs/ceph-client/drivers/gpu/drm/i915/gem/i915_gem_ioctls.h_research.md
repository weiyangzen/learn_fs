# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ioctls.h

## Purpose
Central declaration header for i915 GEM ioctl handlers.

## Important APIs
Declares handlers for busy, create/create_ext, execbuffer2, aperture query, caching get/set, tiling get/set, madvise, mmap/mmap_offset, pread/pwrite, set_domain, sw_finish, throttle, userptr, and wait. All use the DRM ioctl signature `int handler(struct drm_device *dev, void *data, struct drm_file *file)`.

## Control Flow
No runtime logic. The header binds UAPI ioctl entry points to implementations spread across GEM files.

## State and Persistence Behavior
No state is stored here. Implementations mutate GEM objects, file handle tables, mmap state, request timelines, and memory domains.

## Dependencies and Integration Points
Forward-declares `drm_device` and `drm_file`. In this subset, execbuffer is implemented in `i915_gem_execbuffer.c`, caching/domain handlers in `i915_gem_domain.c`, and mmap handlers in `i915_gem_mman.c`.

## Risks and Test Signals
Declaration drift would break builds or ioctl table integration. Functional coverage comes from IGT GEM ioctl suites and implementation selftests.
