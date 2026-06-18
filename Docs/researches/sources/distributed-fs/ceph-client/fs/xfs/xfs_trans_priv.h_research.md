# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_priv.h

## Purpose
`xfs_trans_priv.h` declares private transaction and AIL interfaces shared among XFS transaction implementation files. It exposes internal structures and helpers that should not be part of the broader filesystem API.

## Important APIs, types, and functions
It defines `struct xfs_ail_cursor` and `struct xfs_ail`, declares transaction item helpers, superblock unreservation, AIL insert/update/delete/cursor functions, tail LSN assignment, and push helpers. Inline helpers include `xfs_ail_min`, `xfs_trans_ail_update`, `xfs_ail_push`, `xfs_ail_push_all`, `xfs_ail_get_push_target`, `xfs_ail_assign_tail_lsn`, and `xfs_trans_ail_copy_lsn`.

## Control flow
Callers include this header when they need to manipulate the AIL or private transaction item list directly. Cursor helpers document the invalidation protocol: removed items cause affected cursor pointers to be tagged so a traversal restarts safely. Push helpers wake the AIL daemon or set the push-all bit before waking it.

## State and persistence
The header declares in-memory state only. `struct xfs_ail` holds the log pointer, daemon task, sorted item list, active cursors, spinlock, push target, delayed-write buffers, and empty wait queue. `ail_head_lsn` and log-tail helpers affect persistent log recovery boundaries indirectly through the mounted log state.

## Dependencies and integration points
It bridges transaction core code, AIL daemon code, log item implementations, and log tail accounting. The 32-bit `xfs_trans_ail_copy_lsn` variant locks around 64-bit LSN copies to avoid torn reads.

## Risks and test signals
Risks include misuse of functions that release `ail_lock`, stale cursor assumptions, push-all bit handling, and cross-architecture torn LSN reads. Test signals are mostly indirect through AIL insert/delete stress, 32-bit builds, lockdep, and log tail movement tests.
