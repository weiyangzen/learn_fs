## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_create.h

### Purpose

`i915_gem_create.h` declares the dumb-buffer creation entry point used by DRM mode-setting helpers.

### Important APIs, types, and functions

It forward-declares `struct drm_file`, `struct drm_device`, and `struct drm_mode_create_dumb`, and declares `i915_gem_dumb_create()`.

### Control flow

There is no runtime control flow. The implementation computes stride/size, creates a GEM object, and publishes a handle.

### State and persistence behavior

The header stores no state; the implementation creates persistent GEM handles.

### Dependencies

The header has only type forward declarations. Consumers depend on `i915_gem_create.c` for implementation.

### Integration points

Used by DRM driver setup for dumb framebuffer creation.

### Risks

Signature mismatch would break DRM dumb-create plumbing. The narrow header intentionally does not expose create-ext internals.

### Test signals

Build coverage and DRM dumb-buffer creation tests.
