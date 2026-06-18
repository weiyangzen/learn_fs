# File Research: sources/cow-pools/openzfs/module/zfs/zfs_rlock.c

## Summary
Implements byte-range locking for ZFS file operations. It serializes readers, writers, append writes, truncation, hole punching, indirect ZIL data capture, and block-size growth using an AVL tree of locked ranges.

## Main Responsibilities
- Initialize and destroy per-znode range lock state.
- Acquire blocking or nonblocking reader, writer, and append locks.
- Split overlapping reader ranges into proxy locks with reference counts.
- Wake waiting readers and writers fairly enough to avoid continuous-reader starvation of writers.
- Reduce an over-wide writer lock after block-size growth has been completed.

## Key APIs
- `zfs_rangelock_init()`, `zfs_rangelock_fini()`.
- `zfs_rangelock_enter()`, `zfs_rangelock_tryenter()`.
- `zfs_rangelock_exit()`.
- `zfs_rangelock_reduce()`.

## Important Behavior
Writer acquisition checks for any overlapping AVL node. Append and block-size-growth handling is delegated to the caller-supplied callback, which must convert `RL_APPEND` into `RL_WRITER` and may expand the lock to the whole file.

Reader acquisition allows overlap with other readers but waits behind active writers or ranges with a writer waiting. Overlapping reader locks are represented by proxy nodes. Existing ranges may be proxified and split so each AVL node describes a non-overlapping segment with a reference count.

Unlocking a reader either removes the original node directly or walks the proxy segments representing the original range, decrements counts, removes zero-count proxies, broadcasts waiters, and defers condition-variable destruction/freeing until after the range-lock mutex is dropped.

`zfs_rangelock_reduce()` asserts that the caller holds the whole-file writer lock, rewrites its offset/length to the final range, and wakes waiters.

## Dependencies
Uses AVL trees, ZFS mutex/condition-variable wrappers, kernel memory allocation, and the `zfs_rangelock_cb_t` callback used by ZPL and zvol callers.

## Risks
Correctness depends on exact proxy splitting and reference-count invariants. Wait condition variables are lazily initialized per contested range and must be destroyed only after no waiters can observe them. `zfs_rangelock_reduce()` broadcasts outside the mutex after changing the range, which relies on the asserted whole-file exclusive state.
