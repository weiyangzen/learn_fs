# sources/distributed-fs/orangefs/src/client/usrint/locks.h

## Purpose
`locks.h` provides a local replacement for glibc/libio stream lock definitions that are not reliably exported by modern system headers. It lets OrangeFS stdio interposition code store and operate on `_lock` fields in `FILE`-like streams without depending on private libc `_IO_lock_t` definitions.

## Important APIs, Types, And Macros
The key type is `_PVFS_lock_t`, with simple fields `lock`, `cnt`, and `owner`. `_PVFS_lock_initializer` and `_PVFS_lock_finalizer` provide static initializer values. `_PVFS_lock_init` and `_PVFS_lock_fini` write initial/final marker values into `stream->_lock`. `_PVFS_lock_lock`, `_PVFS_lock_trylock`, and `_PVFS_lock_unlock` delegate to `stdio_ops.flockfile`, `stdio_ops.ftrylockfile`, and `stdio_ops.funlockfile`.

## Control Flow
The stdio layer allocates or embeds `_PVFS_lock_t`, assigns it to a stream's `_lock`, initializes it with `_PVFS_lock_init`, then uses the lock/unlock macros around stream operations. Finalization marks the fields as `-1`/`NULL` before deallocation or teardown. Actual synchronization is performed by the underlying stdio operation table rather than by direct atomic operations on the fields.

## State And Persistence Behavior
Lock state is process-local and attached to stream objects. The fields are not persisted and are meaningful only while the stream and its `_lock` pointer remain valid. The `owner` pointer is opaque and initialized to `NULL`.

## Dependencies And Integration Points
This header is consumed by `stdio.c`, which defines static locks for standard streams and allocates locks for PVFS stream wrappers. It requires `stdio_ops` to be in scope with `flockfile`, `ftrylockfile`, and `funlockfile` members. It also assumes stream objects expose a `_lock` member compatible with casting to `_PVFS_lock_t *`.

## Risks
The include guard defines only `LOCKS_H` without setting it to a value, which still works for `#ifndef` but is nonstandard style. The lock fields are not themselves authoritative if `stdio_ops` maintains separate locking state, so code must not inspect them as synchronization truth. The macros directly cast `stream->_lock`; invalid or uninitialized `_lock` pointers will corrupt memory. The trailing backslashes on lock operation macros are harmless in macro definitions but make formatting brittle.

## Test Signals
Tests should cover initialization/finalization for standard and dynamically allocated streams, recursive or nested `flockfile` behavior as mediated by `stdio_ops`, trylock failure paths, and teardown after close. Build tests should compile against current glibc headers where private `_IO_lock_t` is unavailable.
