# sources/distributed-fs/ceph/src/librados/PoolAsyncCompletionImpl.h

## Purpose

`PoolAsyncCompletionImpl.h` implements the small completion object used for asynchronous pool-level operations such as pool creation, deletion, and application enable. It is separate from object `AioCompletionImpl` and supports wait, completion status, return-value retrieval, callback dispatch, and intrusive reference ownership.

## Important APIs, Types, and Functions

`librados::PoolAsyncCompletionImpl` stores `lock`, `cond`, `ref`, `rval`, `released`, `done`, `callback`, and `callback_arg`. Methods include `set_callback()`, `wait()`, `is_complete()`, `get_return_value()`, `get()`, `release()`, and `put()`. `intrusive_ptr_add_ref()` and `intrusive_ptr_release()` make it usable with `boost::intrusive_ptr`. `CB_PoolAsync_Safe` captures an intrusive pointer and, when invoked with an integer result, marks the completion done, wakes waiters, and calls the registered C callback outside the lock.

## Control Flow and Data Flow

Async pool functions create or receive a `PoolAsyncCompletionImpl`, wrap it in `CB_PoolAsync_Safe`, and pass a lambda context to `Objecter` or manager operations. When the lower layer completes, `operator()(int r)` moves the intrusive pointer into local ownership, sets `rval` and `done`, notifies `cond`, copies callback pointers, unlocks, invokes the callback, and then relocks before exiting.

## State and Persistence Behavior

The completion object is process-local synchronization state. The operations it represents mutate persistent pool or application metadata, but the completion itself persists only `rval` and `done` until released. `released` tracks the user-facing release contract separately from reference count, while `ref` controls deletion.

## Dependencies and Integration Points

It depends on Ceph mutex/condition primitives, librados C callback types, and `boost::intrusive_ptr`. `RadosClient::pool_create_async()` and `pool_delete_async()`, plus `IoCtxImpl::application_enable_async()`, integrate with this completion type.

## Risks and Edge Cases

The callback may call back into completion APIs while the object is still alive, so invoking it outside the lock is important. `release()` asserts it is only called once but does not decrement `ref`; callers still need the intrusive/user release path. `wait()` returns only wait success, not the operation result; callers must use `get_return_value()`. Missing callback registration before completion is legal but means no callback is fired.

## Test Signals

Tests should cover callback-before-completion and callback-after-creation ordering, wait waking, result retrieval, no-callback completions, double release assertions in debug builds, intrusive pointer lifetime during callback, and async pool create/delete error propagation.
