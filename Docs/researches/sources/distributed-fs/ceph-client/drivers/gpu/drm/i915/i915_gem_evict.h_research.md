# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.h

## Purpose
This header declares the i915 GTT virtual-address-space eviction API.

## Important APIs, Types, and Functions
It declares `i915_gem_evict_something()`, `i915_gem_evict_for_node()`, and `i915_gem_evict_vm()`, with forward declarations for `drm_mm_node`, `i915_address_space`, `i915_gem_ww_ctx`, and GEM objects.

## Control Flow
There is no control flow. GTT insertion and bind paths call these functions while holding the relevant VM mutex.

## State and Persistence Behavior
The header stores no state. Its APIs mutate VM/VMA binding state in the implementation.

## Dependencies and Integration Points
It is the contract between `i915_gem_gtt.c`, VMA binding code, execbuf defragmentation, and the eviction implementation.

## Risks
Callers must satisfy locking and interpret ENOSPC/EBUSY/EINTR correctly. Function signatures expose flags shared with GTT pinning; semantics must remain aligned with `i915_gem_gtt.h`.

## Test Signals
Build and eviction selftests covering all three entry points.
