# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.h

## Purpose
Declares public LMEM GEM helpers for residency checks, WC IO mapping, and LMEM object creation.

## Important APIs
Exports `i915_gem_object_lmem_io_map()`, `i915_gem_object_is_lmem()`, `i915_gem_object_create_lmem_from_data()`, `__i915_gem_object_create_lmem_with_ps()`, and `i915_gem_object_create_lmem()`.

## Control Flow
No logic in the header. Implementations delegate allocation to memory-region helpers and manipulate residency/object backing state.

## State and Persistence Behavior
No state is stored here. Created objects store LMEM residency in object memory-region fields.

## Dependencies and Integration Points
Forward-declares i915 private, GEM object, and memory-region types and includes Linux type definitions. Used by display, region, and setup code needing LMEM-specific behavior.

## Risks and Test Signals
Callers must respect locking rules for migratable objects and contiguous requirements for IO maps. Build coverage catches API drift; LMEM/migration/display tests cover behavior.
