# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/src/refcount.c

Purpose: implements the CSS refcount registry over a single static array of `ia_css_refcount_entry` records.

Important APIs/types/functions: `myrefcount` stores `size` and `items`. `refcount_find_entry()` locates an existing pointer or first free slot. Public functions allocate/free the registry with `kvmalloc()`/`kvfree()`, maintain counts, call `hmm_free()` on final decrement, clear entries by owner ID, and validate pointer membership.

Control flow: init rejects size zero and double init, allocates and zeroes entries. Increment locates or creates an entry, checks owner ID, and increments count. Decrement checks pointer and ID, decrements, frees through HMM at zero, and resets entry metadata. Clear iterates all entries matching an ID and calls a supplied callback, then asserts counts are zero. Uninit frees any remaining managed HMM pointers before releasing the registry.

State and persistence: all state lives in the global `myrefcount`. It persists across CSS operations until uninit, but not beyond module lifetime.

Dependencies and integration: uses HMM allocation/freeing, CSS debug tracing, assertions, and CSS error/warning macros. It participates in memory lifetime for CSS buffers.

Risks and test signals: there is no synchronization around the global table, so concurrent CSS users can race. `ia_css_refcount_clear()` asserts callback non-null even though it contains a fallback branch. `ia_css_refcount_is_single()` returns true for untracked non-null pointers, which can mask missing registration. Tests should include concurrent access review, capacity exhaustion, stale pointer decrement, nonzero clear counts, and uninit leak cleanup.
