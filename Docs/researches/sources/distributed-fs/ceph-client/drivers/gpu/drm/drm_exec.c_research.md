# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_exec.c

## Purpose

`drm_exec.c` implements the DRM execution context helper for locking multiple GEM objects with wound/wait dma-resv semantics. It abstracts the retry loop needed by command submission, page table updates, and similar operations that need to lock several buffer objects without deadlocking. It also optionally reserves fence slots after locking.

## Important APIs and Data

The public object is `struct drm_exec` from `drm_exec.h`. This file manages its flags, dynamic `objects` array, `num_objects`, `max_objects`, `contended` object, `prelocked` object, and `ww_acquire_ctx ticket`. The sentinel `DRM_EXEC_DUMMY` marks the first pass through the helper's retry loop.

Exported APIs are `drm_exec_init()`, `drm_exec_fini()`, `drm_exec_cleanup()`, `drm_exec_lock_obj()`, `drm_exec_unlock_obj()`, `drm_exec_prepare_obj()`, and `drm_exec_prepare_array()`. Locking behavior is controlled by flags such as `DRM_EXEC_INTERRUPTIBLE_WAIT` and `DRM_EXEC_IGNORE_DUPLICATES`. Iteration macros are defined in the header and used here for reverse unlock.

## Control Flow

`drm_exec_init()` allocates the initial object tracking array with `kvmalloc_array()`, defaulting to one page worth of pointers when `nr` is zero. Allocation failure is deferred by setting `max_objects` to zero; the first object lock will attempt growth. It initializes `contended` to `DRM_EXEC_DUMMY` so `drm_exec_cleanup()` can create the wound/wait acquire context on the first loop iteration.

`drm_exec_cleanup()` is designed for use inside `drm_exec_until_all_locked()`. If `contended` is NULL, no contention remains, so it calls `ww_acquire_done()` and returns false to leave the retry loop. If `contended` is the dummy sentinel, it initializes `ticket`, clears contention, and returns true for the first pass. If `contended` points to an object, it unlocks and drops all previously locked objects, resets `num_objects`, and returns true so the caller retries with the contended object locked first.

`drm_exec_lock_obj()` first calls `drm_exec_lock_contended()`. That helper slow-locks the previously contended object, tracks it, and stores it in `prelocked`. If the next requested object is the same prelocked object, the function drops the extra prelocked reference and returns success. Otherwise it locks the object's reservation with interruptible or non-interruptible ww locking. On `-EDEADLK`, it takes a reference, stores the object in `contended`, and returns `-EDEADLK` for the caller macro to trigger cleanup and retry. On duplicate lock `-EALREADY`, the optional ignore flag can suppress the error. Successful locks are tracked with an object reference in the dynamic array.

`drm_exec_prepare_obj()` locks one GEM object and reserves `num_fences` on its `dma_resv`; reservation failure unlocks and removes that object. `drm_exec_prepare_array()` applies that operation across an array and stops at the first error. `drm_exec_fini()` unlocks all tracked objects, frees the array, drops a live contended reference if present, and finalizes the ww ticket.

## State and Persistence Behavior

The execution context is caller-owned stack or heap state. The file mutates GEM object reservation locks and holds GEM object references while objects are tracked. `drm_exec_unlock_all()` releases locks in reverse order and drops references. `prelocked` temporarily owns an extra reference after slow-locking the contended object. No global state is kept. The module metadata declares the component as "DRM execution context" under dual MIT/GPL licensing.

## Dependencies and Integration Points

The file depends on GEM object reference helpers, dma-resv locks and fence reservation, Linux `kvmalloc`/`kvrealloc`/`kvfree`, and the reservation wound/wait class. It is used by DRM drivers around hardware submissions and memory-management operations that need to lock arbitrary object sets. The helper integrates with caller-side macros that repeatedly call `drm_exec_cleanup()` and retry on `-EDEADLK`.

## Risks and Edge Cases

Correctness depends on callers following the retry pattern and calling the retry macro after each lock/prepare that can return `-EDEADLK`. Forgetting `drm_exec_fini()` leaks object references and leaves locks held. `drm_exec_unlock_obj()` searches backward and is intended for recently locked objects; using it for old objects is less efficient. Duplicate object handling depends on `DRM_EXEC_IGNORE_DUPLICATES`; otherwise `-EALREADY` propagates. Memory growth uses page-sized increments and can fail after an object reservation lock succeeds, in which case the code unlocks that object before returning `-ENOMEM`. Interruptible waits can return signal-related errors that callers must propagate or handle.

## Test Signals

Tests should cover a no-contention lock/prepare/fini path, duplicate objects with and without ignore flag, array preparation stop-on-error behavior, fence reservation failure cleanup, dynamic object array growth, explicit unlock of the most recent object, interruptible slow-lock error handling, and simulated ww contention where a contended object is locked first on retry. Lockdep and GEM reference leak checks are important signals, as are driver submission tests that exercise many-object command buffers under parallel contention.
