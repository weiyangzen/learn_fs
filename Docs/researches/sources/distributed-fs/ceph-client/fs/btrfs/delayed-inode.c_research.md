# sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.c

## Purpose

`delayed-inode.c` implements delayed inode and delayed directory-index item processing for Btrfs. Instead of immediately updating inode items and directory index items in the subvolume tree for every metadata change, it stores per-inode delayed nodes in memory, batches directory index insertions/deletions, defers inode item updates, and runs those delayed items synchronously during transaction commit or asynchronously through the delayed worker queue. This reduces tree churn for operations such as create, unlink, rename, chmod, timestamp updates, and directory logging.

## Important APIs, Types, and Functions

Initialization and root setup are `btrfs_delayed_inode_init()`, `btrfs_delayed_inode_exit()`, and `btrfs_init_delayed_root()`. Delayed-node lifetime is controlled by `btrfs_get_delayed_node()`, `btrfs_get_or_create_delayed_node()`, `btrfs_release_delayed_node()`, `btrfs_remove_delayed_node()`, and kill/destroy helpers. Public mutation APIs include `btrfs_insert_delayed_dir_index()`, `btrfs_delete_delayed_dir_index()`, `btrfs_delayed_update_inode()`, and `btrfs_delayed_delete_inode_ref()`.

Flush and balancing APIs are `btrfs_run_delayed_items()`, `btrfs_run_delayed_items_nr()`, `btrfs_commit_inode_delayed_items()`, `btrfs_commit_inode_delayed_inode()`, `btrfs_balance_delayed_items()`, and `btrfs_assert_delayed_root_empty()`. Readdir and log integration APIs are `btrfs_readdir_get_delayed_items()`, `btrfs_readdir_put_delayed_items()`, `btrfs_should_delete_dir_index()`, `btrfs_readdir_delayed_dir_index()`, `btrfs_log_get_delayed_items()`, and `btrfs_log_put_delayed_items()`.

## Control Flow

Delayed nodes are stored per root in `root->delayed_nodes` and linked into the filesystem-wide `delayed_root` lists when they contain pending work. Creating or retrieving a node uses an xarray and refcounts, with a cached pointer in `btrfs_inode->delayed_node`. Items are stored in per-node cached rbtrees: insertion items in `ins_root`, deletion items in `del_root`. The node mutex protects these rbtrees, item counts, inode item snapshots, and insertion leaf reservation counters.

Directory insertion builds a `btrfs_dir_item` in a flexible delayed item, inserts it in the insertion rbtree, and accounts delayed block-reserve space by predicted leaf batches. Directory deletion first removes a still-pending insertion if possible; otherwise it queues a deletion item and migrates metadata reservation. Flushing runs insertions before deletions, then records the root in the transaction and updates the delayed inode item.

Commit flow switches `trans->block_rsv` to `fs_info->delayed_block_rsv`, walks delayed nodes, calls `__btrfs_commit_inode_delayed_items()`, and releases nodes after dropping any btree path to avoid lock inversion. Async flow picks prepared nodes from `prepare_list`, joins a transaction, commits a bounded number of delayed items, and wakes waiters. `btrfs_balance_delayed_items()` starts work or waits when item counts exceed background/writeback thresholds.

Readdir collects delayed insert/delete items up to a last index, temporarily upgrades the directory inode lock from shared to exclusive because `item->readdir_list` supports one active delayed readdir collection, and later downgrades back. Directory logging collects unlogged delayed items into log lists, marks them logged on release, and avoids requeueing the delayed node.

## State and Persistence Behavior

Persistent effects are delayed until flush: directory index keys are inserted into or removed from the subvolume tree, inode items are overwritten with a stack snapshot of VFS/Btrfs inode state, and delayed inode refs may be removed. Before flush, state is memory-only in `btrfs_delayed_node` and `btrfs_delayed_item`, with reservations held in `fs_info->delayed_block_rsv`. `delayed_root.items` and `items_seq` drive wait/wakeup behavior and background throttling.

Metadata reservation is carefully attached to delayed items or nodes. Insertion items reserve by leaves through `index_item_leaves`; deletion items store per-item `bytes_reserved`; inode updates store `node->bytes_reserved` and convert or free qgroup preallocations depending on success/error cleanup. Log replay skips some reservation behavior and uses continuous-key-only insertion batches.

## Dependencies and Integration Points

This file depends on xarrays, rbtrees, list management, refcounts, mutexes, spinlocks, wait queues, workqueues, Btrfs transactions, btree path operations, inode-item accessors, qgroups, block reservations, delayed workers, directory item format, VFS inode fields, and tree logging. It integrates with `dir-item.c` for secondary directory index creation and with transaction commit to guarantee all delayed items become durable before commit completes.

## Risks and Edge Cases

The node lifetime model is complex: xarray references, inode cached references, list references, temporary callers, debug ref trackers, and zero-ref removal must stay balanced. Delayed item reservation accounting differs for insertion, deletion, inode update, log replay, and kill paths. Async workers intentionally ignore some errors and rely on transaction commit to retry and abort if needed. Readdir's lock upgrade/downgrade must pair with VFS expectations. Log collection must handle multiple tasks logging the same directory and avoid double-listing items. Inode ref deletion is only intended for single-link inodes and is disabled during log recovery.

## Test Signals

Strong tests include metadata-heavy create/unlink/rename workloads, forced transaction commits during delayed item accumulation, async delayed worker throttling, log replay with interleaved directory indexes, fsync logging of directories with concurrent logging tasks, readdir visibility of pending insertions and deletions, inode eviction with pending delayed nodes, kill-all on dead roots, qgroup enabled metadata accounting, ENOMEM/fault injection in node/item allocation, and lockdep coverage for path versus delayed-node mutex ordering.
