# sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.c

## Purpose
`extent-io-tree.c` implements Btrfs' in-memory interval state tree for byte ranges. It tracks dirty, locked, delalloc, boundary, reservation, direct-I/O, and related flags over inclusive ranges using an rb-tree of `struct extent_state` records, with split/merge logic, wait queues for lock bits, changeset accounting, and debug leak detection.

## Important APIs, types, and functions
Public APIs include `btrfs_extent_io_tree_init`, `btrfs_extent_io_tree_release`, `btrfs_set_extent_bit`, `btrfs_clear_extent_bit_changeset`, `btrfs_convert_extent_bit`, `btrfs_lock_extent_bits`, `btrfs_try_lock_extent_bits`, `btrfs_find_first_extent_bit`, `btrfs_find_first_clear_extent_bit`, `btrfs_find_contiguous_extent_bit`, `btrfs_find_delalloc_range`, `btrfs_count_range_bits`, `btrfs_test_range_bit`, `btrfs_test_range_bit_exists`, `btrfs_get_range_bits`, `btrfs_set_record_extent_bits`, `btrfs_clear_record_extent_bits`, `btrfs_next_extent_state`, `btrfs_extent_state_init_cachep`, and `btrfs_extent_state_free_cachep`. Important internals are `tree_search_for_insert`, `tree_search_prev_next`, `insert_state`, `split_state`, `merge_state`, `set_state_bits`, `clear_state_bit`, `wait_extent_bit`, and cached-state helpers.

## Control flow
Set/clear/convert operations search for the first state intersecting the requested range, split existing records at range boundaries, insert records for holes, update bits, merge adjacent compatible records, and retry after dropping the spinlock if atomic preallocation fails or rescheduling is needed. Lock operations use exclusive `EXTENT_LOCK_BITS`: if a lock bit already exists, the partially acquired prefix is cleared, callers wait on the existing state's waitqueue, and the operation retries. Range queries walk the rb-tree under the tree lock and optionally preserve a referenced cached state to speed repeated scans.

## State and persistence
All state is volatile memory. `extent_io_tree->state` is an rb-root protected by `tree->lock`; each `extent_state` stores inclusive `start/end`, bitmask, refcount, waitqueue, and optional leak-list linkage. For inode I/O trees, set/clear/split/merge callbacks update delalloc accounting in the owning inode. There is no direct on-disk persistence, but the state drives writeback, transaction dirty page tracking, pinned extents, device allocation state, and other paths that later update persistent metadata.

## Dependencies and integration points
The file depends on Linux slab caches, rbtrees, spinlocks, wait queues, refcounts, tracing, and Btrfs helpers from extent I/O, inode, messages, and ctree code. It is used by inode I/O, btree inode metadata, transaction dirty-page tracking, pinned/excluded extents, relocation, root dirty log pages, log checksum ranges, selftests, and device allocation state. The owner field determines whether the union points to `fs_info` or an inode and whether delalloc accounting callbacks are invoked.

## Risks and test signals
Risk concentrates in off-by-one inclusive range handling, split/merge correctness, cached-state refcounting, lock wait/wakeup ordering, NOWAIT allocation behavior, changeset accounting under GFP_ATOMIC, and owner-specific delalloc callbacks. Because this tree is used in transaction cleanup and writeback, leaks or missed wakeups can cause unmount hangs or metadata/accounting corruption. Test signals include Btrfs extent-io selftests, lock/unlock contention, delalloc writeback and truncation, direct-I/O locking, dirty-range conversion, clear-all truncation paths, fault injection for allocation failures, CONFIG_BTRFS_DEBUG leak checks, lockdep, and KASAN/KCSAN runs.
