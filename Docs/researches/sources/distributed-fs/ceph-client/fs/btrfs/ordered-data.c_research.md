# sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.c

## Purpose
`ordered-data.c` manages Btrfs ordered extents: in-memory records that bridge data writeback completion and metadata insertion. Ordered extents serialize overlapping writes, track checksums, qgroup reservations, outstanding extent accounting, root-wide wait lists, fsync logging state, completion work, and error propagation. The source was read as a complete 1357-line file.

## Important APIs, Types, and Functions
Public APIs include `btrfs_alloc_ordered_extent()`, `btrfs_add_ordered_sum()`, `btrfs_mark_ordered_extent_error()`, `btrfs_finish_ordered_extent()`, `btrfs_mark_ordered_io_finished()`, `btrfs_dec_test_ordered_pending()`, `btrfs_put_ordered_extent()`, `btrfs_remove_ordered_extent()`, `btrfs_wait_ordered_extents()`, `btrfs_wait_ordered_roots()`, `btrfs_start_ordered_extent_nowriteback()`, `btrfs_wait_ordered_range()`, lookup helpers, logging collection, ordered-range lock helpers, `btrfs_split_ordered_extent()`, `ordered_data_init()`, and `ordered_data_exit()`. Internal rb-tree helpers implement non-overlap insertion, cached searches, and range-overlap detection.

## Control Flow
Allocation validates flag combinations, transfers or frees qgroup reservations depending on COW versus NOCOW/PREALLOC, initializes the ordered extent, grabs the inode, increments outstanding extents, inserts into the per-inode rb-tree, adds it to the per-root ordered list, and adds the root to the filesystem ordered-root list when needed.

I/O completion decrements `bytes_left` under `ordered_tree_lock`. When the final byte finishes, it sets `BTRFS_ORDERED_IO_DONE`, wakes waiters, takes a reference, and queues `finish_ordered_fn()` to the appropriate endio workqueue. Error completion marks mapping error and, for failed COW writes, sets an inode runtime flag forcing future fast fsync to wait for completion before logging extent maps.

Removal is called after metadata completion. It updates outstanding extents, releases delalloc metadata, subtracts ordered bytes, erases the rb-node, clears cached lookup state, sets `BTRFS_ORDERED_COMPLETE`, wakes transaction waiters if `BTRFS_ORDERED_PENDING` was set, removes the root-list entry, and wakes extent waiters. Refcount release frees checksum sums, schedules delayed iput, and returns the object to the kmem cache.

Wait flows either target one inode range, one root list, or all roots. `btrfs_wait_ordered_range()` starts writeback, waits writeback errors, then walks ordered extents backward through the range and waits each one. `btrfs_wait_ordered_extents()` splices root extents, queues flush work for up to `nr` matching extents, waits completions, and restores skipped entries. Range lock helpers repeatedly lock the extent state, check for overlapping ordered extents, unlock and wait until none remain.

Splitting creates a new leading ordered extent, trims the original offsets/lengths/checksum list, and updates both the inode rb-tree and root list under the root and inode locks to avoid races with ordered-extent waiters.

## State and Persistence Behavior
Ordered extents are volatile memory but represent pending persistent changes to file extent items and checksums. State lives in `struct btrfs_ordered_extent`, per-inode `ordered_tree` and cache pointer, per-root `ordered_extents` and count, global `ordered_roots`, `fs_info->ordered_bytes`, transaction `pending_ordered`, qgroup reservations, and workqueue/completion objects. Persistent metadata is written by the finish path declared externally, not by this file directly.

## Dependencies and Integration Points
The module integrates with transactions, Btrfs inode and extent I/O trees, compression/encoded writes, delalloc space accounting, qgroups, subpage support, file writeback, block groups, tracepoints, and lockdep wait-event annotations from `locking.h`/`misc.h`. It depends on `btrfs_finish_one_ordered()` and `btrfs_finish_ordered_io()` implementations elsewhere.

## Risks and Edge Cases
Overlapping ordered extents are fatal and trigger `btrfs_panic()`. Accounting must keep `bytes_left`, delalloc metadata, qgroup reservations, and outstanding extents consistent across success, errors, truncation, direct I/O, compressed writes, encoded writes, and NOCOW/PREALLOC. Failed COW writeback can otherwise let fast fsync log unwritten extent maps. Range wait logic intentionally waits all extents even after writeback error to avoid re-dirty races and `-EEXIST` on reinsertion. Splitting rejects compressed or partially inconsistent extents and has careful lock ordering to avoid races with root-level waiters.

## Test Signals
Signals include xfstests for buffered and direct writes, compressed and encoded writes, NOCOW/PREALLOC writes, qgroup accounting, ENOSPC/error injection during writeback, fast fsync after write errors, truncate/split ordered extents, ordered-range lock nowait behavior, root-wide waits during snapshot/balance, transaction pending-ordered waits, and KCSAN/lockdep stress around splitting and root ordered lists.
