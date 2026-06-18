## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.h

### Purpose

`i915_gem_dmabuf.h` declares the i915 PRIME dma-buf import/export entry points.

### Important APIs, types, and functions

It forward-declares `struct drm_gem_object`, `struct drm_device`, and `struct dma_buf`, and declares `i915_gem_prime_import()` and `i915_gem_prime_export()`.

### Control flow

There is no runtime control flow in the header. The implementation handles same-device import, foreign attach, export info setup, and dma-buf ops.

### State and persistence behavior

The header stores no state. The implementation creates dma-buf exports and imported GEM objects with shared reservation objects.

### Dependencies

Consumers need DRM GEM and dma-buf types. The implementation depends on Linux dma-buf APIs and i915 GEM object internals.

### Integration points

Used by driver PRIME hooks and GVT export paths.

### Risks

The declarations are part of the cross-driver sharing boundary; signature changes affect DRM driver integration.

### Test signals

Build coverage and PRIME import/export tests.
