# sources/distributed-fs/moosefs/mfsmaster/flocklocks.c

## Purpose
`flocklocks.c` implements MooseFS master-side whole-file advisory locks for FUSE `flock` semantics. It tracks active reader/writer locks by inode, queues blocking lock attempts, wakes client requests when locks become available or are interrupted, persists active locks into metadata, and replays lock changes from changelogs.

The implementation models three wake/fairness modes: `MODE_CORRECT`, `MODE_BSD`, and `MODE_LINUX`, controlled by the `FLOCK_MODE` configuration option. It also has optional debug dumping through `EXTRA_DEBUG_INFO`.

## Important APIs, Types, And Functions
The core data structures are `instance`, `lock`, and `inodelocks`. `instance` stores waiting request identifiers (`msgid`, `reqid`) for a blocking lock owner. `lock` stores owner, connection pointer, session id, active/waiting state, reader/writer type, waiting instances, parent inode record, and intrusive-list links. `inodelocks` stores one inode's active lock list and FIFO waiting queue.

`inodehash` is a 1024-bucket hash table keyed by inode through `FLOCK_INODE_HASH`. Each bucket chains `inodelocks` records. Active locks are held as an intrusive list, while waiting locks use `waiting_head` plus a tail pointer-to-pointer for append.

Public entry points are `flock_locks_cmd`, `flock_file_closed`, `flock_disconnected`, `flock_list`, `flock_mr_change`, `flock_store`, `flock_load`, `flock_cleanup`, and `flock_init`.

Important internal helpers include `flock_check` for conflict/fairness detection, `flock_lock_new` for active-or-waiting creation, `flock_lock_check_waiting` for promotion/wakeup after unlocks, `flock_lock_wake_up_one` and `flock_lock_wake_up_all` for client notifications, `flock_lock_append_req` for coalescing waiting request instances by `reqid`, and `flock_lock_remove`/`flock_do_lock_remove` for cleanup with or without changelog emission.

## Control Flow
`flock_locks_cmd` is the main client command path. For all operations except interrupt and release, it first checks `of_checknode(sessionid, inode)` so only opened files can receive locks. Missing inode lock records are created lazily for lock operations and ignored for unlock/interrupt/release.

Interrupt handling scans waiting locks for the same connection/session/owner, wakes only the matching request id with `MFS_ERROR_EINTR`, and removes the waiting lock if it no longer has any instances. Active locks are not interrupted.

For active locks owned by the same session/owner, unlock and release remove the lock, emit a `FLOCK(...,U)` changelog through `flock_lock_remove`, promote waiters if possible, and remove the inode record if empty. Shared/exclusive conversion is handled in place when possible, or by unlocking and requeueing when a blocking conversion may need to wait. Try-lock conversions return `MFS_ERROR_EAGAIN` instead of queueing.

For existing waiting locks by the same connection/session/owner, repeated blocking requests append or replace `instance` records. Changing the requested type cancels existing waiters with `MFS_ERROR_ECANCELED`, switches the waiting lock type, appends the new request, and continues waiting. Unlock while waiting is ignored for OS compatibility except in `MODE_CORRECT`, where it cancels/removes the waiting lock.

New try locks run `flock_check` and return `MFS_ERROR_EAGAIN` on conflict. New blocking locks use `flock_lock_new`; if conflicted, the lock is queued and returns `MFS_ERROR_WAITING`, otherwise it is attached active and logged.

`flock_lock_check_waiting` performs waiter promotion after unlocks. A writer at the queue head is promoted only when no active locks remain. Readers can be promoted when there are no active locks or active locks are readers. Linux mode scans the whole waiting queue and promotes all reader waiters it finds, while BSD/classic mode promotes only the reader prefix at the queue head.

## State And Persistence Behavior
Only active locks are persistent. Active lock creation/removal via the normal path emits changelog records like `FLOCK(inode,sessionid,owner,R/W/U)`. Waiting requests are connection-local transient state and are neither stored nor replayed.

`flock_store` writes metadata chunk version `0x10` records of 17 bytes: inode, owner, session id, and lock type, followed by an all-zero terminator. `flock_load` accepts only version `0x10`, validates that the referenced open-file record exists with `of_checknode`, verifies there is no conflicting existing active lock, then reconstructs active locks. With `ignoreflag`, invalid closed-file or conflicting records are logged and skipped; otherwise load fails.

`flock_mr_change` is the changelog/restore application path. It removes active locks for unlock commands, or attaches active reader/writer locks for lock commands after checking for conflicts. It increments metadata version with `meta_version_inc` when it successfully mutates state, and intentionally uses non-logging helpers so replay does not emit a second changelog.

## Dependencies And Integration Points
The module depends on `MFSCommunication.h` for flock operation and lock-type constants, `matoclserv_fuse_flock_wake_up` for waking blocked FUSE requests, `openfiles.c` through `of_checknode` and `flock_file_closed`, `metadata.c` for `meta_version_inc` and FLCK metadata chunk load/store, `restore.c` for changelog replay through `flock_mr_change`, `changelog.h` and `main_time` for durable log emission, `cfg.h` for runtime options, and `main.h` for reload/info registration.

`matoclserv.c` calls `flock_locks_cmd`, `flock_list`, and `flock_disconnected`. `openfiles.c` calls `flock_file_closed` when an open-file record closes. `metadata.c` stores and loads the `FLCK` chunk after open-file state, as noted by its dependency comment.

## Risks
Intrusive list pointer maintenance is delicate. In `flock_do_lock_inode_attach`, the active-list insertion sets the old head's `prev` to `&(l->next)`, which is correct for this intrusive pattern but easy to break in future edits. Waiting queue tail updates similarly rely on pointer-to-pointer invariants.

Mode comments and values are inconsistent: `MODE_BSD` is `1` and `MODE_LINUX` is `2`, but `flock_reload` comments say `1 - LINUX , 2 - BSD`. That can cause operator confusion even if behavior follows the constants.

`flock_disconnected` removes only waiting locks for a connection. Active locks are tied to open-file/session cleanup, so disconnect paths must reliably close open files or active locks can persist until session cleanup/recovery handles them.

Load/replay depends on open-file state being loaded first. The metadata integration comment says FLCK depends on OPEN; violating this order will either fail load or skip locks under `ignoreflag`.

Fairness differs by configured mode. `MODE_LINUX` can promote later readers around a waiting writer, while `MODE_CORRECT` blocks new readers behind any waiter to avoid writer starvation. Compatibility changes here can alter client-visible blocking behavior.

## Test Signals
High-value tests include shared/shared coexistence, exclusive conflicts, try-lock `EAGAIN`, blocking wakeups, interrupt by request id, release of waiting locks, conversion between shared and exclusive, close-triggered cleanup, disconnect cleanup of waiters, and metadata store/load with valid and invalid open-file dependencies.

Replay tests should compare changelog `FLOCK` records to live command behavior, ensuring active locks are reconstructed without duplicate changelog emission. Configuration tests should exercise all three `FLOCK_MODE` values with a writer queued behind readers and readers queued behind a writer to catch fairness regressions.
