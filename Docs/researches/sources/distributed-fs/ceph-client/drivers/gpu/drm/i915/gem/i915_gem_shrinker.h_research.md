# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.h

## Purpose
This header exposes the GEM shrinker interface and shrink-selection flags for the rest of i915.

## Important APIs, Types, and Functions
It declares `i915_gem_shrink`, `i915_gem_shrink_all`, shrinker register/unregister helpers, and `i915_gem_shrinker_taints_mutex`. Flags are `I915_SHRINK_UNBOUND`, `I915_SHRINK_BOUND`, `I915_SHRINK_ACTIVE`, `I915_SHRINK_VMAPS`, and `I915_SHRINK_WRITEBACK`.

## Control Flow
The header has no executable control flow. The flags define how callers select unbound objects, bound objects requiring runtime PM, active objects requiring request retirement/waits, vmapped objects, and writeback behavior.

## State and Persistence Behavior
No state is stored here. Implementations use the declarations to mutate object shrink-list state, page backing, and kernel shrinker registration.

## Dependencies and Integration Points
This header is included by allocation paths, shmem retry logic, PM freeze, and other GEM code that needs explicit reclaim. It forward-declares `drm_i915_private`, `i915_gem_ww_ctx`, and `mutex`.

## Risks
Flag combinations are semantically important: asking for bound or active reclaim can wake hardware or wait on GPU work, while writeback changes shmem/TTM persistence behavior. Callers in reclaim context must avoid flags that can deadlock.

## Test Signals
Compile coverage plus targeted shrink calls using each flag combination, especially shmem allocation retry and freeze-late paths, validate this interface.
