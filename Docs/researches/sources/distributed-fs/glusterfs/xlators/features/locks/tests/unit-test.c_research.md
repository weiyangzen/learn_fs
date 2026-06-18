# sources/distributed-fs/glusterfs/xlators/features/locks/tests/unit-test.c

## Purpose
This is a small standalone unit test for entry lock name conflict behavior. It constructs a `pl_inode_t` with directory lock state and calls `lock_name`/`unlock_name` directly.

## Important APIs, Types, And Functions
The file imports GlusterFS base headers plus `locks.h` and `common.h`. It declares external `lock_name(pl_inode_t *, const char *, entrylk_type)` and `unlock_name(pl_inode_t *, const char *, entrylk_type)`. The `expect` macro jumps to `out` on failure, and `main` returns 0 only if all expectations pass.

## Control Flow
The test initializes `pinode->dir_lock_mutex` and `pinode->gf_dir_locks`, then checks these scenarios: a whole-directory write lock blocks a named write lock; unlocking the whole-directory lock succeeds; repeated read locks on the same basename are compatible; a write lock conflicts with those reads; write lock/unlock on one basename succeeds; and a write lock blocks a read lock on the same different basename.

## State And Persistence Behavior
State is entirely in heap memory allocated by `CALLOC`. The test does not persist anything and does not free or destroy all initialized state before exit, which is acceptable for a short process but not a reusable harness pattern.

## Dependencies And Integration Points
It depends on the entry lock implementation exposing non-static `lock_name` and `unlock_name`. It is a lower-level signal than translator FOP tests because it bypasses frames, xdata, client identity, and inode context setup.

## Risks And Test Signals
The test covers core reader/writer compatibility for basename entry locks, including the special `NULL` basename. It does not test blocked queues, owners, domains, fd paths, or cleanup. A failure returns `1` without describing which expectation failed, so diagnostic value is limited.
