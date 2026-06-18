## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.h

### Purpose

`i915_gem_clflush.h` declares the GEM object cache flush API and its behavior flags.

### Important APIs, types, and functions

It declares `i915_gem_clflush_object(struct drm_i915_gem_object *obj, unsigned int flags)` and defines `I915_CLFLUSH_FORCE` and `I915_CLFLUSH_SYNC`.

### Control flow

There is no runtime control flow in the header. The flags direct the implementation to force flushing despite read coherency or to require synchronous flushing.

### State and persistence behavior

The header stores no state. The implementation mutates object cache-dirty state and reservation fences.

### Dependencies

It includes Linux type definitions and forward-declares i915 object/device types.

### Integration points

Included by GEM domain and execbuffer paths that need cache-coherency transitions.

### Risks

Flag misuse changes correctness/performance tradeoffs. Omitting `I915_CLFLUSH_SYNC` where immediate CPU/GPU ordering is required can introduce stale data hazards.

### Test signals

Build coverage and GEM coherency/domain-transition tests for forced and synchronous flush paths.
