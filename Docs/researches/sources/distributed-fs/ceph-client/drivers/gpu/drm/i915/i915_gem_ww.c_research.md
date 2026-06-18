# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_ww.c

## Purpose
`i915_gem_ww.c` implements i915's wrapper around Linux dma-resv wound/wait locking for GEM objects. It tracks objects locked within an acquire context and provides deadlock backoff handling.

## Important APIs, Types, and Functions
Public functions are `i915_gem_ww_ctx_init()`, `i915_gem_ww_ctx_fini()`, `i915_gem_ww_ctx_backoff()`, and `i915_gem_ww_unlock_single()`. The local helper `i915_gem_ww_ctx_unlock_all()` unlocks and drops references for every object in `ww->obj_list`.

## Control Flow
Init initializes `ww_acquire_ctx` with `reservation_ww_class`, the object list, interruptible flag, and `contended`. Normal finish unlocks all tracked objects, warns if `contended` remains, and finalizes the acquire context. Backoff requires a contended object, unlocks all currently held objects, slow-locks the contended object's dma-resv interruptibly or uninterruptibly, adds it to the object list on success, or drops its reference on failure, then clears `contended`.

## State and Persistence Behavior
The ww context is short-lived per multi-object locking operation. It owns references to locked GEM objects via `obj_list` and temporarily owns `contended` across an `-EDEADLK` retry.

## Dependencies and Integration Points
It depends on dma-resv ww locking, GEM object lock/unlock/ref helpers, and the reservation ww class. It is used by GEM pinning, execbuf, eviction, and other multi-object operations.

## Risks
Every object added to `obj_list` must be referenced and locked; otherwise `unlock_all` will corrupt lifetime. Missing backoff after `-EDEADLK` can deadlock. Interruptible contexts must propagate EINTR. `i915_gem_ww_unlock_single()` assumes the object is on the list.

## Test Signals
Multi-object locking selftests, forced `-EDEADLK` backoff paths, interruptible signal handling, lockdep ww-class validation, and refcount leak checks.
