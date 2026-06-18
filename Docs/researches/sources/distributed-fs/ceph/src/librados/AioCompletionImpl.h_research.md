# sources/distributed-fs/ceph/src/librados/AioCompletionImpl.h

## Purpose
`AioCompletionImpl.h` defines the internal librados asynchronous completion object and callback functors used by `IoCtxImpl`.

## Important APIs, Types, and Functions
`librados::AioCompletionImpl` stores a mutex, condition variable, refcount, result, release/complete flags, object version, operation tid, complete/safe callbacks and args, read buffers, owning `IoCtxImpl*`, aio write sequence, and xlist item. It provides callback setters, wait/is-complete APIs, return/version accessors, `get()`, `_get()`, `release()`, `put()`, and `put_unlock()`. `CB_AioComplete` invokes user callbacks after operation completion. `CB_AioCompleteAndSafe` marks a completion complete and invokes both callbacks, used by flush/synthetic completion paths.

## Control Flow
Operations create or receive a completion with refcount 1. Submit paths take extra refs when contexts or waiters need ownership. Completion contexts set `rval`/`complete`, notify waiters, defer callback functors on the finish strand, then `put()`. User release marks `released` and drops a ref.

## State and Persistence Behavior
State is in-memory and synchronization-only. It mirrors completion status for RADOS operations but does not persist to cluster storage.

## Dependencies and Integration Points
It depends on Ceph mutexes, bufferlists, xlist, OSD types, C librados callback typedefs, and `IoCtxImpl`. `IoCtxImpl.cc` uses `aio_write_list_item` to implement write flush ordering.

## Risks
Callback invocation reads callback pointers outside the lock in the functors, so lifecycle relies on the retained completion reference and ordered clearing. `_get()` asserts the lock is already held. `release()` asserts single release.

## Test Signals
Tests should exercise wait before/after completion, callbacks, release/refcount deletion, read buffer return lengths, write flush waiters, and cancellation paths.
