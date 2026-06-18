# sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.c` implements Btrfs' tree modification log: a transient, in-memory history of interior-tree and root changes used to give backref and extent walkers a consistent older view while concurrent writers mutate subvolume and extent trees. The file was read as a complete 1146-line source file for this report.

## Important APIs, Types, and Functions

Core private state is `struct tree_mod_elem`, an rb-tree node keyed by extent-buffer logical address and sequence, and `struct tree_mod_root`, the compact old-root pointer/level payload for root replacement records. `tree_mod_elem` carries the operation (`enum btrfs_mod_log_op`), slot, generation, and one of three payloads: removed/replaced key and block pointer, move metadata, or old-root metadata.

Public entry points include `btrfs_get_tree_mod_seq()` and `btrfs_put_tree_mod_seq()` for reader blockers, mutator logging functions `btrfs_tree_mod_log_insert_key()`, `btrfs_tree_mod_log_insert_move()`, `btrfs_tree_mod_log_insert_root()`, `btrfs_tree_mod_log_eb_copy()`, and `btrfs_tree_mod_log_free_eb()`, reconstruction helpers `btrfs_tree_mod_log_rewind()`, `btrfs_get_old_root()`, `btrfs_old_root_level()`, and status helper `btrfs_tree_mod_log_lowest_seq()`.

Important private helpers include `tree_mod_dont_log()`, `tree_mod_need_log()`, `alloc_tree_mod_elem()`, `tree_mod_log_insert()`, `tree_mod_log_search()`, `tree_mod_log_search_oldest()`, `tree_mod_log_oldest_root()`, and the static rewind engine `tree_mod_log_rewind()`.

## Control Flow

Readers that need a stable historical tree view initialize a `struct btrfs_seq_list`, call `btrfs_get_tree_mod_seq()`, perform their backref walk or tree iteration using that sequence, and eventually call `btrfs_put_tree_mod_seq()`. The get path increments `fs_info->tree_mod_seq`, links the blocker into `fs_info->tree_mod_seq_list`, and sets `BTRFS_FS_TREE_MOD_LOG_USERS`; the put path removes the blocker and frees rb-tree entries older than the lowest remaining blocker.

Writers call logging functions from Btrfs tree mutation paths before or around operations such as COW root replacement, key replacement, pointer insertion/removal, node splitting, node balancing, and extent-buffer copying. Each log function first performs a cheap `tree_mod_need_log()` test, preallocates records outside the write lock, then rechecks with `tree_mod_dont_log()` while holding `fs_info->tree_mod_log_lock`. If no blockers remain, allocations are discarded and the operation proceeds without logging; if blockers remain and allocation failed, the mutator returns an error.

The rb-tree ordering is by logical address and then descending sequence for a given logical block. Search helpers find either the newest record at or above a minimum sequence or the oldest record at or above that sequence. Rewind starts from the most recent relevant operation and walks forward through rb-next entries for the same logical block, applying the inverse of each logged operation until it reaches the requested historical time. Root reconstruction first follows `BTRFS_MOD_LOG_ROOT_REPLACE` records to locate the old root logical address and level, reads or allocates an extent buffer when necessary, then replays node-level changes.

## State and Persistence Behavior

The tree modification log is memory-only state under `btrfs_fs_info`: `tree_mod_seq`, `tree_mod_seq_list`, `tree_mod_log`, `tree_mod_log_lock`, and the users flag. It is not persisted to disk and is pruned when sequence blockers disappear. Logged records copy just enough btree node/root metadata to undo pointer-array changes for historical readers; leaf modifications are intentionally skipped, and `skip_eb_logging()` restricts logging to non-leaf extent buffers from the extent tree and filesystem trees.

The code allocates records with `GFP_NOFS` and carefully stages allocations before taking the write lock. Rewind allocates cloned or dummy extent buffers, transfers read locks to the returned buffer, and frees the current buffer when a rewind buffer is produced. Old-root reads may read tree blocks from disk when the old root still exists and needs to be cloned before replay.

## Dependencies and Integration Points

This file depends on Btrfs accessors, extent-buffer helpers, rb-trees, read/write locks, fs-info flags, tree block validation, and btree mutation code. It is integrated heavily from `ctree.c` mutation paths, while `backref.c` obtains tree-mod sequences for historical reference walking and `delayed-ref.c` queries the lowest active sequence to coordinate delayed refs. The header is included by Btrfs tree and backref code that needs either to log mutations or to retrieve old roots.

## Risks and Edge Cases

The ordering and replay logic are correctness-critical: an incorrect sequence order, missing move/remove record, or bad slot arithmetic can corrupt the reconstructed historical node and mislead backref accounting. Memory allocation failures are tolerated only when logging is no longer required after the lock recheck; otherwise mutators must fail. Root replacement is special because records are keyed by the new root logical address but may reconstruct an older root logical address and level.

The code uses `BUG_ON`, `ASSERT`, and `WARN_ON` around invariants such as slot bounds, move ranges, and node item counts. Rewind tracks `max_slot` separately from `nritems` to catch invalid memmoves during historical replay. Races are handled by rechecking the latest tree-mod record after cloning an old block in `btrfs_get_old_root()`, but that path remains sensitive to concurrent logging between search, read, and clone.

## Test Signals

Useful signals include fstests covering qgroups, backref walking, delayed refs, snapshot deletion, balance, relocation, and send/receive under concurrent metadata mutation. Targeted tests should exercise node splits/merges, root promotion/replacement, `btrfs_tree_mod_log_eb_copy()` left and right pushes, low-memory failures after a tree-mod blocker exists, and historical reads while writers modify extent and filesystem trees. Kernel warning-free runs are important because many bad states are surfaced through `WARN_ON`, `BUG_ON`, and tree checker failures rather than ordinary return values.
