# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_evict.c

## Purpose
`i915_gem_evict.c` frees virtual address space in i915 GTT address spaces. It evicts idle or waitable VMAs from `drm_mm` ranges to satisfy new bindings, fixed-node reservations, or full-VM defragmentation, without freeing the objects' backing memory.

## Important APIs, Types, and Functions
Public APIs are `i915_gem_evict_something()`, `i915_gem_evict_for_node()`, and `i915_gem_evict_vm()`. Helpers include `dying_vma()`, `ggtt_flush()`, `grab_vma()`, `ungrab_vma()`, `mark_free()`, and `defer_evict()`. Selftest state `igt_evict_ctl.fail_if_busy` can force busy behavior.

## Control Flow
`i915_gem_evict_something()` assumes `vm->mutex` is held, initializes a `drm_mm_scan` for the requested hole, retires requests, then scans `vm->bound_list` in rough LRU order. It defers active or scanout VMAs on the first pass by moving them to the tail, tries to grab object locks and add unpinned VMAs to the scanner, and on success pins candidates temporarily, removes nonselected blocks, unbinds selected VMAs, and evicts color-conflicting neighbors. If no hole exists in GGTT and nonblocking is not set, it idles all GTs sharing the GGTT with `ggtt_flush()`, marks the next pass nonblocking, and scans again.

`i915_gem_evict_for_node()` targets a fixed `drm_mm_node` range, expands the search for cache-color guard pages, refuses unevictable/pinned/nonblocking-active overlaps, grabs and temporarily pins overlapping VMAs, then unbinds them. `i915_gem_evict_vm()` evicts all unpinned VMAs from a VM, flushing GGTT first to unpin context/ring objects, splitting VMAs into already-locked and newly-locked lists, optionally returning a referenced `busy_bo` when trylock fails, and ignoring most non-interrupt unbind failures so it can continue cleansing.

## State and Persistence Behavior
Eviction mutates VM `bound_list` ordering, `drm_mm` node allocation state, VMA pin counts, and VMA binding state. It takes temporary object refs/locks to stabilize VMAs. It does not destroy GEM objects or free backing pages. For GGTT, it may force GPU idleness and request retirement to release active pins on contexts/rings.

## Dependencies and Integration Points
The code depends on `drm_mm` scanning, VMA flags and node colors, object ww locking, GT request retirement/idling, GGTT multi-GT lists, tracepoints, and `__i915_vma_unbind()`. It is called by GTT insertion/reservation and VMA bind/pin paths.

## Risks
Locking is subtle: callers hold `vm->mutex`, while object locks are trylocked through ww contexts to avoid deadlocks. Dying objects need special handling because ref acquisition can fail. Active/scanout deferral protects current work but can return ENOSPC under nonblocking pressure. GGTT flushing may stall indefinitely up to `MAX_SCHEDULE_TIMEOUT`. Color guard-page handling must evict neighbors only when colors conflict; mistakes can corrupt cache-domain isolation.

## Test Signals
IGT/selftests for eviction under fragmented address spaces, fixed-node conflicts, cache coloring, pinned and unevictable nodes, active nonblocking VMAs, full-VM eviction with busy_bo return, GGTT context/ring unpinning after idle, and lockdep/KCSAN coverage for ww locking paths.
