# sources/distributed-fs/moosefs/mfsmaster/posixlocks.c

## Purpose
`posixlocks.c` implements MooseFS master-side POSIX byte-range locks. It normalizes closed-open lock ranges, stores active locks by inode/session/owner, queues blocking lock requests, wakes clients when conflicts clear, writes lock changes to the changelog, and persists active locks in metadata.

## Important APIs, Types, And Functions
The common internal `range` type stores `[start,end)` and lock type. In normal master builds, `alock` stores active lock owner/session/pid and a normalized range list; `wlock` stores a waiting request plus connection/message identifiers; `inodelocks` groups active and waiting locks for one inode. `inodehash` is a 1024-bucket table keyed by inode.

Core range helpers are `posix_lock_test_wlock()` and `posix_lock_apply_range()`. Master helpers include `posix_lock_inode_find/new/remove()`, waiting-list removal/interruption, conflict detection, active lock application, and `posix_lock_check_waiting()`.

Exported APIs are `posix_lock_cmd()`, `posix_lock_file_closed()`, `posix_lock_disconnected()`, `posix_lock_list()`, `posix_lock_mr_change()`, `posix_lock_store()`, `posix_lock_load()`, `posix_lock_cleanup()`, and `posix_lock_init()`.

## Control Flow
`posix_lock_cmd()` is the client command entry point. `GET` returns the first conflicting active lock or reports unlocked. `TRY` returns `MFS_ERROR_EAGAIN` on conflict. Blocking `SET` appends a `wlock` and returns `MFS_ERROR_WAITING`. `INT` interrupts a waiting request by connection and request id. Non-unlock SET/TRY commands first verify the session has the inode open through `of_checknode()`.

When a lock is applied, `posix_lock_apply_lock()` writes a `POSIXLOCK` changelog record and calls `posix_lock_do_apply_lock()`. Range application merges adjacent same-type ranges, splits ranges around changed intervals, and removes empty active lock owners. Unlocking a range can wake queued requests through `posix_lock_check_waiting()`.

`posix_lock_file_closed()` removes all waiting requests and active ranges for the closing session on one inode, then wakes newly unblocked waiters. `posix_lock_disconnected()` removes waiting locks tied to a lost client connection but does not remove active locks; active lock lifetime follows open-file/session cleanup.

Metadata replay uses `posix_lock_mr_change()`, which applies a recorded read/write/unlock without writing another changelog and increments metadata version.

## State, Persistence, And Dependencies
Active and waiting locks live only in memory during runtime. Only active locks are stored by `posix_lock_store()` as 37-byte records: inode, owner, sessionid, pid, start, end, type, terminated by an all-zero record.

`posix_lock_load()` only accepts metadata version `0x10`. It validates that the owning session still has the inode open, expects records grouped by inode/session/owner with ordered non-overlapping ranges, optionally ignores bad records, and reconstructs active lock lists. Waiting locks are not persisted.

Dependencies include `MFSCommunication.h` for lock command/type/status constants, `openfiles.h` for open-file validation, `matoclserv.h` for waking blocked FUSE requests, `changelog.h`, `metadata.h`, `main.h`, `cfg.h`, `datapack.h`, `bio.h`, and logging/assertion helpers. Under `MFSTEST`, only the range engine and a standalone randomized/manual test harness are compiled.

## Integration Points
Client lock requests enter through `matoclserv` and call `posix_lock_cmd()`. Open-file/session cleanup calls `posix_lock_file_closed()` and `posix_lock_disconnected()`. `restore.c` parses `POSIXLOCK` changelog lines into `posix_lock_mr_change()`. Metadata store/load includes active POSIX locks.

## Risks
The range algorithm is compact and branch-heavy. Boundary mistakes around adjacent versus overlapping closed-open intervals would cause silent lock leaks or over-unlocks.

Waiting locks hold raw `connptr` values. Disconnection cleanup must be called reliably, or stale waiters could remain and receive wakeups through invalid connections.

`posix_lock_load()` depends on stored range ordering. If the store order or future format changes, replay can reject otherwise valid locks.

The debug/info path is gated by config and traverses all locks. Large lock tables can produce substantial info output.

## Test Signals
Range tests should cover all `posix_lock_apply_range()` cases, adjacent merge behavior, full unlock to empty list, read/read compatibility, read/write and write/write conflicts, blocking wake-up order, interrupting a waiter, close cleanup, disconnect cleanup, metadata store/load round trips, replay mismatch handling, and `MFSTEST` randomized range runs.
