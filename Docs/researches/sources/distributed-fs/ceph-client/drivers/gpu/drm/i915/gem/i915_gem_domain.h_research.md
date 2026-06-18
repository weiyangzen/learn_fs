# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.h

## Purpose
Small public header for GEM domain/cache-level code. It forward-declares the GEM object and cache-level enum and exposes the object-wide cache-level mutation API.

## Important APIs
`i915_gem_object_set_cache_level(struct drm_i915_gem_object *obj, enum i915_cache_level cache_level)` changes object cache policy and triggers implementation-side VMA rebinding/coherency updates.

## Control Flow
No runtime flow exists in the header. The implementation in `i915_gem_domain.c` waits for activity, updates PAT/coherency/dirty state, and unbinds VMAs.

## State and Persistence Behavior
No state is stored here. The declared API mutates object PAT/cache coherency and cache-dirty state in implementation code.

## Dependencies and Integration Points
The header is intentionally lightweight and avoids full object includes. Consumers include concrete object/cache definitions separately when needed.

## Risks and Test Signals
Risk is misuse of the declared API without required locking or misunderstanding user-managed PAT immutability. Build coverage catches declaration drift; domain/cache/display tests cover behavior.
