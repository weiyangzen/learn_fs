# Group Research: group_959_linux_stable_sources_os_linux_linux_stable_fs_btrfs_tree_log_c_sourc_d0a562f042a2

Scope checked against `Docs/research_subset_a.md`: both files are under `sources/os/linux/linux-stable`, which is included in subset A. Both listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-log.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-log.c

## Purpose

`tree-log.c` implements Btrfs tree logging: the per-subvolume write-ahead log used to satisfy `fsync()`/`O_SYNC` without forcing a full transaction commit. It logs selected inode, extent, xattr, directory, and name-reference metadata into a log tree, syncs that log tree and the global tree of log roots, and replays the logs during mount after a crash.

The file is one of the most correctness-sensitive Btrfs components. Its core job is to preserve the observable effects of fsync while avoiding full commit cost, especially across rename, unlink, hard link, xattr deletion, reflink, preallocation, NO_HOLES, delayed directory items, zoned-device write ordering, and log replay recovery cases.

## Main Concepts

- **Per-root log tree**: each fs/subvolume root can have `root->log_root`, created by `start_log_trans()` through `btrfs_add_log_tree()`.
- **Log root tree**: `fs_info->log_root_tree` stores root items for individual log roots and is pointed to by the superblock during log sync.
- **Log transaction ids**: roots track `log_transid`, `log_transid_committed`, two-slot `log_commit[]` wait state, and `log_ctxs[]` waiters.
- **Tree-log fallback**: `BTRFS_LOG_FORCE_COMMIT` means the tree log cannot safely represent the operation and the caller must force a full transaction commit.
- **Replay stages**:
  - `LOG_WALK_PIN_ONLY`: pin log metadata and relevant mixed block group extents.
  - `LOG_WALK_REPLAY_INODES`: create/replay inode items, xattr deletes, directory deletes.
  - `LOG_WALK_REPLAY_DIR_INDEX`: replay directory index entries.
  - `LOG_WALK_REPLAY_ALL`: replay xattrs, inode refs/extrefs, extents, then fix link counts.
- **Directory range logging**: `BTRFS_DIR_LOG_INDEX_KEY` items describe index ranges for which the log is authoritative. During replay, missing entries inside a logged range mean deletes.
- **Link-count fixups**: the synthetic fixup namespace rooted at `BTRFS_TREE_LOG_FIXUP_OBJECTID` records inodes whose nlink must be recomputed after replay.
- **Conflict inodes**: when a logged inode’s name conflicts with another inode from the commit root, the other inode or its parent may need logging to avoid replay deleting or duplicating the wrong object.

## Important Internal Structures

- `struct walk_control`: transient state for log tree traversal and replay. It carries the current replay stage, source log leaf/key/slot, target root, log root, transaction handle, path for subvolume edits, and whether the walk is pinning or freeing.
- `struct btrfs_dir_list`: small queue element used by `log_new_dir_dentries()` to recursively log newly created directory dentries.
- `struct btrfs_ino_list`: queue element used by conflicting-inode logging, storing an inode number plus parent inode number.

## Exported Entry Points

- `btrfs_init_log_ctx()` initializes a `btrfs_log_ctx` with default flags, lists, inode pointer, conflict counters, and scratch extent buffer.
- `btrfs_init_log_ctx_scratch_eb()` preallocates a scratch extent buffer for expensive copy/full-sync paths.
- `btrfs_release_log_ctx_extents()` releases ordered extents held by a log context.
- `btrfs_pin_log_trans()` and `btrfs_end_log_trans()` hold and release a log transaction against concurrent sync.
- `btrfs_sync_log()` writes the log tree, updates the log root tree, writes superblocks with log root pointers, wakes waiters, and returns either success, real errors, or `BTRFS_LOG_FORCE_COMMIT`.
- `btrfs_free_log()` and `btrfs_free_log_root_tree()` walk/free log trees at full transaction commit or cleanup.
- `btrfs_recover_log_trees()` replays all log roots during mount.
- `btrfs_log_dentry_safe()` is the public fsync path helper for a dentry.
- `btrfs_del_dir_entries_in_log()` and `btrfs_del_inode_ref_in_log()` update an already-created log after unlink/rename removes a name.
- `btrfs_record_unlink_dir()`, `btrfs_record_snapshot_destroy()`, and `btrfs_record_new_subvolume()` mark cases where future directory fsyncs must force a full commit.
- `btrfs_log_new_name()` updates the log after link/rename creates a new name.

## Logging Flow

The main fsync path is:

`btrfs_log_dentry_safe()` -> `btrfs_log_inode_parent()` -> `start_log_trans()` -> `btrfs_log_inode()` -> caller later invokes `btrfs_sync_log()`.

`start_log_trans()` ensures the global log root tree exists, creates the per-subvolume log tree if needed, handles zoned filesystem restrictions, increments `root->log_writers`, and attaches the caller context to the current log transaction unless the caller is doing a special new-name update.

`btrfs_log_inode_parent()` enforces early fallback cases: `notreelog`, deleted roots, roots created in the current transaction, and already-logged inodes with no pending ordered extents. It then logs the inode, logs parents when needed, logs all old/current parents after unlink, logs new ancestors for newly created directory chains, and optionally logs new directory dentries discovered while logging a directory.

`btrfs_log_inode()` is the central logger. It decides between full logging, existence-only logging, and fast extent logging. It handles symlinks by forcing full inode logging, computes whether the inode was already logged in the transaction, drops or truncates old log items when relogging, collects delayed directory items for full directory logging, copies changed inode items, logs all xattrs, logs holes for `NO_HOLES`, logs changed extents or clears modified extent maps, logs directory changes and delayed insert/delete items, updates `logged_trans`, and then logs conflicting inodes.

## Inode and Item Logging

`copy_inode_items_to_log()` scans the subvolume tree for changed keys in the current transaction and copies batches into the log. It skips xattrs for separate all-xattr logging, stops regular extent copying at EOF when prealloc extents beyond EOF are handled separately, checks inode ref/extref name override conflicts against the commit root, and records conflicting inodes.

`copy_items()` clones the source leaf before modifying the log tree to avoid lock dependency cycles between subvolume leaves, log tree COW, delayed items, and memory reclaim. It copies batched keys and item payloads and logs file data checksums for new regular extents.

`log_inode_item()` writes or updates the inode item. `fill_inode_item()` deliberately avoids trusting `nbytes` during fast fsync; replay recomputes it while replaying extents. For `LOG_INODE_EXISTS`, generation may be set to zero to signal replay not to overwrite a fully existing inode item, while preserving a safe logged size.

`inode_logged()` combines the in-memory `inode->logged_trans` cache with a log-tree lookup for evicted/reloaded inodes. It carefully handles races by using inode locks and a “mark as not logged” helper that avoids clobbering a concurrent logging update.

## File Extents, Checksums, Holes, and Preallocation

`btrfs_log_changed_extents()` consumes the inode extent map tree’s `modified_extents`, sorts them, and logs each extent through `log_one_extent()`. It caps extreme modified-extent counts and falls back through error handling if logging becomes too large.

`log_one_extent()` converts an extent map into a `BTRFS_EXTENT_DATA_KEY` item in the log, optionally replacing overlapping log extents if the inode was logged before. It handles regular and preallocated extents, compressed extents, holes, and physical offset encoding.

`log_extent_csums()` and `log_csums()` log checksums into the log tree. They account for ordered extents that may not have reached the csum tree yet and serialize checksum logging for reflinked ranges to prevent overlapping checksum items in the log.

`btrfs_log_prealloc_extents()` scans the subvolume tree, not only extent maps, to preserve preallocation beyond EOF and avoid wrong extent-map merges. It also handles prealloc extents crossing i_size.

`btrfs_log_holes()` explicitly logs holes when the `NO_HOLES` feature could otherwise cause replay to miss hole punching or truncation effects.

## Directory Logging and Replay Semantics

`log_directory_changes()` and `log_dir_items()` scan changed directory index keys and insert directory range items that describe authoritative deletion ranges. `process_dir_items_leaf()` copies new directory index items, skips old entries, detects gaps, and sets `ctx->log_new_dentries` when logged dentries point to non-root-item inodes whose link count may require fixup.

Delayed directory items are handled separately:

- `log_delayed_insertion_items()` batches delayed insertion items into log `BTRFS_DIR_INDEX_KEY` entries.
- `log_delayed_deletion_items()` records delayed deletion ranges.
- `log_delayed_deletions_full()` emits range keys for a full directory log.
- `log_delayed_deletions_incremental()` deletes existing logged dir index items or adds compact range keys for incremental relogging.
- `log_new_delayed_dentries()` logs inodes pointed to by delayed insertion items, limiting recursion.

`log_new_dir_dentries()` recursively logs new dentries in logged directories. Regular files are logged in existence mode, directories in full mode, matching journaled-filesystem expectations for directory fsync.

## Rename, Link, Unlink, and Conflict Handling

The file spends substantial complexity on name topology:

- `btrfs_del_dir_entries_in_log()` removes logged directory entries after unlink/rename if the directory was already logged.
- `btrfs_del_inode_ref_in_log()` removes inode references from the log when a logged inode loses a name.
- `btrfs_log_new_name()` handles link/rename after adding a new name. It pins the log when both old directory and renamed inode need updates, deletes or range-logs the old dentry, then logs the inode parent chain in existence mode.
- `btrfs_record_unlink_dir()` marks the inode’s `last_unlink_trans` and sometimes the directory’s `last_unlink_trans` so future fsyncs can force a full commit when cross-directory rename/unlink cannot be represented safely.
- `btrfs_record_snapshot_destroy()` and `btrfs_record_new_subvolume()` force conservative directory logging behavior around snapshot/subvolume operations.

`btrfs_check_ref_name_override()` detects when a new inode reference would override a name that belonged to another committed inode. `add_conflicting_inode()` queues that other inode or its parent for logging, with `MAX_CONFLICT_INODES` as a cap to avoid unbounded work. `log_conflicting_inodes()` processes that queue with one recursion level.

Some directory cases deliberately force full commits, especially directories unlinked in the current transaction or cases that could replay a directory with two hard links.

## Log Sync Path

`btrfs_sync_log()` is the commit path for a log transaction. It:

1. Serializes by `root->log_mutex`, current `log_transid`, and two-slot `log_commit[]`.
2. Waits for prior writers and prior log commits.
3. Writes marked log extents for the per-root log tree.
4. Captures a consistent copy of the log root item.
5. Updates the global log root tree under its own log mutex.
6. Writes the log root tree extents.
7. Waits for writeback of per-root and log-root-tree log extents.
8. Updates superblock log root fields under `tree_log_mutex`.
9. Writes all supers.
10. Updates `last_log_commit`, removes waiting log contexts, clears commit flags, and wakes waitqueues.

Zoned filesystems get special handling because sequential write constraints make concurrent or hole-creating log writes unsafe; several paths either wait, retry, or force a full commit.

## Log Tree Walk, Free, and Recovery

`walk_log_tree()` traverses log-tree blocks with `walk_down_log_tree()` and `walk_up_log_tree()`, invoking a callback for pinning, replaying, or freeing.

`process_one_buffer()` pins log tree blocks for replay and excludes logged extents in mixed block groups. `clean_log_buffer()` clears dirty state and either pins reserved extents under a transaction or manually accounts reserved bytes when no transaction is present.

`btrfs_recover_log_trees()` performs mount-time recovery. It starts a transaction, pins all log-tree blocks first, then iterates all log roots repeatedly through replay stages. It skips deleted subvolume roots after pinning their log root node, attaches each log to its fs root, replays it, fixes link counts after the final stage, initializes free objectid state, commits the recovery transaction, and clears `BTRFS_FS_LOG_RECOVERING`.

## Replay Details

`replay_one_buffer()` is the replay callback. It reads log leaves and processes items depending on stage:

- In inode stage, it skips zero-link tmpfile/deleted inodes, replays xattr deletes, replays directory deletes, overwrites inode items, truncates regular file extents beyond logged size before replaying extents, and links inodes into the fixup list.
- In dir-index stage, it replays directory index entries with `replay_one_dir_item()`.
- In final stage, it overwrites xattrs, replays inode refs/extrefs, and replays extent data.

`overwrite_item()` copies a log item to the subvolume tree, resizing existing destination items when needed. It preserves existing `nbytes`, handles directory `i_size` specially, respects zero-generation existence-only inode items, and fills missing generation values.

`replay_one_extent()` drops overlapping file extents, inserts or overwrites inline/regular/prealloc extents, updates extent references or allocates logged file extents, logs qgroup tracing, replays checksums while deleting overlapping existing csum ranges, updates inode extent ranges, and fixes inode bytes.

`replay_one_name()` and related helpers handle directory entry replay. They delete conflicting dir/index entries when the target inode exists, skip dentries pointing to missing inodes, avoid double-adding dentries that will be added from logged backrefs, and update directory size only when appropriate.

`replay_dir_deletes()` uses logged directory ranges to find subvolume dir index entries that are absent from the log and removes them. `check_item_in_log()` drives the comparison and unlinks victims through `unlink_inode_for_log_replay()`.

`replay_xattr_deletes()` deletes xattrs present in the subvolume tree but missing from the log, preserving expected fsync semantics for xattr deletion.

## Link Count Repair

`link_to_fixup_dir()` records an inode under `BTRFS_TREE_LOG_FIXUP_OBJECTID` and temporarily increments nlink so it survives until repair.

`fixup_inode_link_counts()` scans fixup items after final replay, calls `fixup_inode_link_count()`, counts normal refs and extrefs, updates the inode’s nlink, resets directory index state, handles zero-link directories by replaying full directory deletes, and inserts orphan items for zero-link inodes.

## Error Handling and Diagnostics

The replay path uses `btrfs_abort_log_replay()` to abort the transaction while printing the current subvolume leaf, log leaf, key, slot, root id, replay stage, and formatted error context. It uses `BTRFS_FS_STATE_LOG_REPLAY_ABORTED` to avoid repeated verbose dumps.

Most tree-log errors either abort the transaction during replay/recovery or set the log full-commit flag during live fsync logging, causing callers to fall back to a full transaction commit. ENOSPC and zoned write constraints are treated conservatively.

## Concurrency and Locking

Important locking patterns include:

- `root->log_mutex` serializes log transaction creation, writer registration, and per-root log commit state.
- `log_root_tree->log_mutex` serializes updates to the tree of log roots.
- `tree_log_mutex` serializes superblock log root writes against transaction commits.
- `inode->log_mutex` serializes per-inode log updates and protects `last_unlink_trans` style state.
- `log_writers` prevents sync while active writers are modifying the log tree.
- `join_running_log_trans()` lets rename/unlink update an existing log transaction safely.
- Source leaves are cloned before log-tree modifications to avoid lock inversion with delayed items, extent buffer allocation, and reclaim.
- Several paths avoid taking VFS inode locks when recursively logging new dentries, relying instead on replay-time link count correction.

## External Dependencies

This file depends heavily on other Btrfs subsystems:

- B-tree operations from `ctree`, `disk-io`, `locking`, and accessors.
- Extent and delayed-ref management from `extent-tree`, `file`, `file-item`, and `backref`.
- Directory item helpers from `dir-item`.
- Delayed inode/item support from `delayed-inode`.
- Checksums and compression helpers from `compression` and file extent helpers.
- Qgroup tracing from `qgroup`.
- Root-tree and orphan item support from `root-tree` and `orphan`.
- Block group and space accounting from `block-group` and `space-info`.
- VFS, fscrypt, inode versioning, writeback, wait queues, and block plug APIs from the kernel.

## Key Correctness Invariants

- A committed log must be replayable without requiring uncommitted subvolume metadata.
- Directory replay uses logged ranges as authoritative delete windows.
- Directory entries and inode refs/extrefs must agree after replay.
- Link counts may be temporarily wrong during replay but must be fixed before recovery commits.
- Existence-only inode logging must not shrink or overwrite valid file data.
- Xattr deletion must be represented by absence from the log, so all xattrs are logged when an inode is logged.
- Checksums in the log must not overlap in ways that break replay lookup.
- Prealloc extents beyond EOF must be preserved.
- Symlinks must always log inline contents.
- Logged tree blocks and referenced extents must be pinned before replay modifies fs trees.
- When tree-log safety is uncertain, the code forces a full transaction commit.

## Notable Edge Cases Documented in Code

The file contains many executable design notes. Major covered cases include:

- Directory fsync after rename/unlink losing moved names unless a full commit or parent logging occurs.
- `rm -rf` of directories needing recursive delete replay.
- Hard links added under directory fsync requiring link-count fixup.
- Reflinked extents causing overlapping checksum ranges.
- `NO_HOLES` hole punching being invisible unless holes are explicitly logged.
- Prealloc extents beyond EOF being lost without special logging.
- New ancestors of a newly created path needing existence logging.
- Deleted snapshots/subvolumes requiring conservative full commit behavior.
- Cross-directory rename with old parent deletion causing duplicated links after replay.
- Deep chains of delayed dentries being bounded to avoid unbounded recursion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-log.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-log.h

## Purpose

`tree-log.h` declares the public interface and shared context structure for Btrfs tree logging. It is included by Btrfs code that starts fsync logging, syncs or pins log transactions, updates logs after namespace changes, records cases that require full commits, and runs mount-time log recovery.

## Public Constants

- `BTRFS_NO_LOG_SYNC` is a positive sentinel return value from `btrfs_log_dentry_safe()` meaning the inode was already logged and no log sync is needed.
- `BTRFS_LOG_FORCE_COMMIT` is a negative sentinel outside normal errno values. It means the tree log cannot safely represent the operation and callers must force a full transaction commit.

## Main Structure: `struct btrfs_log_ctx`

`btrfs_log_ctx` carries per-fsync/per-log-operation state:

- `log_ret`: result propagated to waiters after a log commit.
- `log_transid`: log transaction id joined by this context.
- `log_new_dentries`: set when directory logging discovers new dentries whose target inodes must also be logged.
- `logging_new_name`: distinguishes rename/link log updates from ordinary fsync logging.
- `logging_new_delayed_dentries`: recursion guard for logging delayed directory dentries.
- `logged_before`: records whether the target inode was already logged in the current transaction.
- `inode`: primary inode for this context.
- `list`: linkage into a root’s log context waiter list.
- `ordered_extents`: ordered extents tracked for fast fsync and checksum/logged-ordered coordination.
- `conflict_inodes`: list of inodes discovered through reference/name conflicts while logging.
- `num_conflict_inodes`: cap counter for `conflict_inodes`.
- `logging_conflict_inodes`: recursion guard for conflict logging.
- `scratch_eb`: reusable temporary extent buffer used when copying subvolume-tree leaves into the log tree.

## Inline Helpers

- `btrfs_set_log_full_commit()` stores the current transaction id into `fs_info->last_trans_log_full_commit`, marking this transaction as unsafe for further tree-log commits.
- `btrfs_need_log_full_commit()` checks whether the current transaction has been marked for full commit.

Both helpers use `READ_ONCE`/`WRITE_ONCE` because this flag is consulted by concurrent log writers and syncers.

## Declared Functions

Context lifecycle:

- `btrfs_init_log_ctx()`
- `btrfs_init_log_ctx_scratch_eb()`
- `btrfs_release_log_ctx_extents()`

Log sync and cleanup:

- `btrfs_sync_log()`
- `btrfs_free_log()`
- `btrfs_free_log_root_tree()`
- `btrfs_recover_log_trees()`

Logging entry point:

- `btrfs_log_dentry_safe()`

Live log updates for unlink/rename/link:

- `btrfs_del_dir_entries_in_log()`
- `btrfs_del_inode_ref_in_log()`
- `btrfs_log_new_name()`

Transaction pinning:

- `btrfs_end_log_trans()`
- `btrfs_pin_log_trans()`

Recording operations that affect future logging safety:

- `btrfs_record_unlink_dir()`
- `btrfs_record_snapshot_destroy()`
- `btrfs_record_new_subvolume()`

## Dependencies

The header includes:

- `<linux/list.h>` for list heads in `btrfs_log_ctx`.
- `<linux/fs.h>` for VFS inode/dentry-related types.
- `<linux/fscrypt.h>` for encrypted filename strings used in log update declarations.
- `"transaction.h"` for `struct btrfs_trans_handle` and transaction context.

It forward-declares several Btrfs and VFS structures to keep inclusion light.

## Relationship to `tree-log.c`

The header exposes only the operations needed by the rest of Btrfs. The heavy policy, replay engine, directory range logic, conflict handling, extent/checksum logging, and zoned-device sync behavior live in `tree-log.c`. The header’s main design role is to centralize the `btrfs_log_ctx` contract and the two sentinel return values that callers must interpret correctly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-log.h -->