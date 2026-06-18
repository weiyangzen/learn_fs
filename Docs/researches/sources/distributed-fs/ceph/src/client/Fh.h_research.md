# sources/distributed-fs/ceph/src/client/Fh.h

## Purpose
`Fh.h` declares the per-open file handle state used by high-level fd operations and low-level libcephfs APIs.

## Important APIs, Types, and Functions
`Fh` stores `InodeRef inode`, open `flags`, generation, opening `UserPerm`, refcount `_ref`, current `pos`, open `mode`, position lock/waiters, `Readahead`, POSIX/flock lock state, and `async_err`. `has_any_filelocks()`, `take_async_err()`, `get()`, and `put()` are the main helpers.

## Control Flow
Client open creates an `Fh`, fd maps point to it, read/write/lseek lock and update `pos`, readahead state feeds read scheduling, lock calls update file lock state, and close/release drops refs and cleans lock/delegation state.

## State and Persistence Behavior
The handle is volatile process state. File locks and open modes are coordinated with MDS state by `Client`/`Inode`, but the local structures are not persisted. `async_err` latches writeback errors until the next consumer calls `take_async_err()`.

## Dependencies and Integration Points
It depends on `Readahead`, `InodeRef`, `UserPerm`, and MDS lock definitions. `Client` manages fd maps and lock operations. `Delegation` holds an `Fh*`.

## Risks and Edge Cases
Position locking uses a boolean plus waiter list rather than a mutex object, so all callers must follow client locking protocol. Async errors must not be lost across fsync/close. File lock state must be released before handle destruction. Delegations require the `Fh` lifetime to exceed delegation lifetime.

## Test Signals
Concurrent read/write/lseek position behavior, readahead lifecycle, fsync/close async error delivery, file lock release on close, and fd generation reuse tests.
