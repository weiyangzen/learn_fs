# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.c

## Purpose
Implements i915 GEM cache-domain transitions for CPU, WC, GTT, render, and display access. It waits for GPU work, pins pages when backing must be stable, flushes incompatible write domains, updates `read_domains`/`write_domain`, handles legacy caching/set-domain ioctls, and prepares scanout-safe display-plane bindings.

## Important APIs, Functions, and Types
Key helpers are `flush_write_domain()`, `i915_gem_cpu_write_needs_clflush()`, `i915_gem_object_set_to_wc_domain()`, `i915_gem_object_set_to_gtt_domain()`, `i915_gem_object_set_to_cpu_domain()`, `i915_gem_object_set_cache_level()`, `i915_gem_set_domain_ioctl()`, `i915_gem_get_caching_ioctl()`, `i915_gem_set_caching_ioctl()`, `i915_gem_object_prepare_read()`, `i915_gem_object_prepare_write()`, and `i915_gem_object_pin_to_display_plane()`. They operate on `drm_i915_gem_object` domain, dirty, PAT/coherency, VMA, and frontbuffer state.

## Control Flow
Domain moves assert the object is reserved, wait for relevant fences, pin pages where direct access needs stable backing, flush all incompatible write domains, and then set read/write domain state for the requested access. `flush_write_domain()` drains GGTT writes via bound GGTT VMAs, uses WC memory barriers, clflushes CPU writes, and marks render-domain writes `cache_dirty` when GPU writes are not coherent. Display pinning first enforces LMEM residency on LMEM platforms, forces WT or NONE cache policy, tries mappable GGTT placement, marks scanout, then flushes display-visible data.

Ioctl flow gates unsupported dGPU/newer-PAT cases, validates requested domains or caching values, looks up objects, rejects proxy or user-managed PAT objects where needed, then locks the object and delegates to the transition/cache helpers. Read/write preparation returns with pages pinned and tells callers whether manual clflush is needed.

## State and Persistence Behavior
The file mutates `obj->read_domains`, `obj->write_domain`, `obj->cache_dirty`, `obj->mm.dirty`, PAT/cache coherency through object helpers, GGTT VMA write markers, and frontbuffer invalidate/flush state. Cache-level changes persist in object PAT/coherency fields and force VMA unbind so future PTEs encode the new policy.

## Dependencies and Integration Points
Depends on clflush helpers, VMA/GGTT APIs, LMEM residency helpers, object wait/pin APIs, display frontbuffer tracking, userptr validation, and GEM UAPI structs. It is used by pread/pwrite, mmap faults/access, execbuffer relocations and submission prep, display modesetting, and DRM ioctl dispatch.

## Risks
Coherency mistakes can expose stale data or corrupt scanout, especially on non-LLC systems or when GPU access bypasses CPU cache. `pat_set_by_user` objects intentionally bypass normal kernel cache assumptions. Most helpers require object reservation locking; unlocked use can race migration, VMA state, or dirty accounting.

## Test Signals
Signals include IGT set-domain, pread/pwrite, mmap coherency, display scanout, and execbuffer relocation tests. `GEM_BUG_ON` checks catch impossible leftover write domains after transitions, and related object/coherency selftests exercise cache behavior.
