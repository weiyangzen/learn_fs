# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_gem_object.h

## Purpose
Provides a minimal mock GEM object wrapper type for selftests.

## APIs And Control Flow
Defines `struct mock_object` containing a single `struct drm_i915_gem_object base`. There is no executable flow.

## State, Dependencies, Integration, Risks, And Tests
State exists only when tests allocate the wrapper. It depends on `gem/i915_gem_object_types.h`. The wrapper is useful when a concrete container is needed around the base object. Risk is minimal, but tests needing additional ownership metadata must add it elsewhere. Build coverage validates it.
