## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.c

### Purpose

`i915_gem_create.c` implements GEM buffer creation uAPIs, dumb-buffer creation, memory-region placement selection, protected-content and PAT create extensions, object initialization, and handle publication.

### Important APIs, types, and functions

Public functions are `__i915_gem_object_create_user()`, `i915_gem_dumb_create()`, `i915_gem_create_ioctl()`, and `i915_gem_create_ext_ioctl()`. Important helpers are `object_max_page_size()`, `object_set_placements()`, `i915_gem_publish()`, `__i915_gem_object_create_user_ext()`, `set_placements()`, `ext_set_placements()`, `ext_set_protected()`, and `ext_set_pat()`.

### Control flow

Object creation flushes free objects, rounds size to the maximum min-page-size across placements, rejects zero/too-large sizes, allocates an object, stores placement regions, calls the first memory region's `init_object()` with user-clear flags, applies extension flags, traces creation, and publishes a GEM handle. Dumb create computes format/stride/size, chooses local memory when available or system memory otherwise, creates a user object, and returns handle/size. `GEM_CREATE_EXT` parses user extensions, defaults placement to system memory, validates `NEEDS_CPU_ACCESS`, sets GPU-only allocation for non-system/multi-placement cases, optionally sets PAT index, and publishes the object.

### State and persistence behavior

Created objects persist through GEM handles. The code sets `obj->mm.placements`, `obj->mm.n_placements`, allocation flags such as `I915_BO_ALLOC_USER`, `I915_BO_ALLOC_GPU_ONLY`, `I915_BO_PROTECTED`, and optional PAT state (`pat_set_by_user`). `i915_gem_publish()` drops the allocation reference after handle creation because the handle holds the object alive.

### Dependencies

It depends on DRM fourcc/print helpers, display dumb framebuffer stride limits, GEM ioctl declarations, local/system memory region APIs, PXP, tracing, and generic user-extension parsing.

### Integration points

The ioctls are registered in `i915_driver.c`. Memory region placement integrates with LMEM/SMEM object backends. Protected object creation integrates with PXP enablement. PAT setting is limited to Xe_LPG and newer graphics versions.

### Risks

Placement validation must reject duplicates, private regions, invalid classes, and missing system memory fallback for CPU-accessible multi-region objects. Size rounding to region page size can change returned object size. Protected-content objects require PXP availability. PAT indices are platform-specific and must respect `max_pat_index`.

### Test signals

igt GEM create/create-ext tests, memory-region placement tests on LMEM systems, dumb framebuffer creation, protected-content create failures/success, PAT index validation on supported hardware, handle leak tests, and size/stride boundary tests.
