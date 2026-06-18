# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.c

## Purpose
This file implements i915 GEM memory reclaim. It registers kernel shrinker, OOM, and vmap purge callbacks; frees purgeable or swappable object pages; and manages object visibility on shrink and purge lists.

## Important APIs, Types, and Functions
Main APIs are `i915_gem_shrink`, `i915_gem_shrink_all`, `i915_gem_driver_register__shrinker`, `i915_gem_driver_unregister__shrinker`, `i915_gem_shrinker_taints_mutex`, `i915_gem_object_make_unshrinkable`, `__i915_gem_object_make_shrinkable`, `__i915_gem_object_make_purgeable`, `i915_gem_object_make_shrinkable`, and `i915_gem_object_make_purgeable`. Internal callbacks include shrinker count/scan, OOM, and vmap purge handlers.

## Control Flow
`i915_gem_shrink` chooses purge-list first, then shrink-list depending on flags. It may acquire a runtime PM wakeref for bound objects, retire active requests when active shrinking is requested, then loops one object at a time under `obj_lock`, moves it to a temporary list, filters by vmap/framebuffer/releasability, takes a ref, locks the object, unbinds according to bound/active flags, puts pages, and asks backend shrink/writeback ops to finalize. Entries are spliced back afterward.

The kernel shrinker count reports `shrink_memory` and dynamically adjusts batch size. The scan path does a normal pass, then kswapd may force active/writeback reclaim. OOM and vmap notifiers perform aggressive passes and report freed pages.

## State and Persistence Behavior
The file owns list membership and accounting in `i915->mm.shrink_list`, `purge_list`, `shrink_count`, and `shrink_memory`, protected by `obj_lock`. Object `mm.shrink_pin` prevents reclaim while pinned or intentionally hidden. MADV state decides shrink vs purge placement.

## Dependencies and Integration Points
It depends on GEM object locking/refcounts, unbind paths, backend `shrink` ops, runtime PM, GT request retirement, Linux shrinker/OOM/vmap notifier APIs, swap availability, and lockdep fs-reclaim annotations.

## Risks
Reclaim can run inside allocation paths, so deadlock avoidance is critical. Objects can be freed while lists are walked, requiring refcount checks. The CHV/VTD workaround uses trylock VM unbinds. Framebuffers are skipped unless active shrinking is explicit. `i915_gem_shrink` returns an unsigned long but can return `err`, so callers must tolerate encoded negative values only where expected.

## Test Signals
Memory-pressure tests, OOM notifier tests, vmap exhaustion tests, pinned-object skip tests, purgeable MADV behavior, active GPU reclaim, kswapd writeback behavior, and lockdep under fs reclaim provide useful coverage.
