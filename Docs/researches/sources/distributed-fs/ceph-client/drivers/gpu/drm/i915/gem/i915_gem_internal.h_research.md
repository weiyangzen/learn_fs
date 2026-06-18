# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.h

## Purpose
Declares constructors for driver-private internal GEM objects.

## Important APIs
`i915_gem_object_create_internal(i915, size)` creates a default volatile internal object. `__i915_gem_object_create_internal(i915, ops, size)` allows custom object ops while preserving the internal-object creation path.

## Control Flow
No logic in the header. The implementation validates size, initializes private GEM metadata, marks volatile/struct-page state, and uses backend get/put pages.

## State and Persistence Behavior
No state is stored here. The created objects maintain volatile page-backed state in `drm_i915_gem_object`.

## Dependencies and Integration Points
Includes `<linux/types.h>` and forward-declares i915/object/ops structures. Internal driver subsystems include it to allocate temporary GPU-addressable storage.

## Risks and Test Signals
Custom ops through the `__` constructor must preserve internal-object invariants. Build coverage catches signature drift; allocation and shrinker tests cover behavior.
