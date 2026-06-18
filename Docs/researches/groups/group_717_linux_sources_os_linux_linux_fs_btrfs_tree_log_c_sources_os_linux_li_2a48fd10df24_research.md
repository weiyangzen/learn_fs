# Group Research: group_717_linux_sources_os_linux_linux_fs_btrfs_tree_log_c_sources_os_linux_li_2a48fd10df24

Scope checked against `Docs/research_subset_a.md`: both requested files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-log.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tree-log.c

Btrfs tree-log implementation. This file implements the filesystem-specific write-ahead log used by fsync/O_SYNC to avoid full transaction commits, plus mount-time log replay that restores logged inode, directory, xattr, extent, checksum, and link-count state into subvolume trees.

Key responsibilities:
- Creates, joins, pins, commits, and frees per-root log trees and the global log-root tree.
- Synchronizes log transactions to disk, writes marked log extents, updates the log-root tree, writes superblocks with log-root pointers, and coordinates concurrent log writers/committers.
- Recovers log trees at mount by walking them in ordered stages: pin metadata/data extents, replay inode items, replay directory index entries, replay remaining refs/xattrs/extents, then fix link counts and commit replay.
- Replays logged file extents into subvolume trees, including dropping overlapping extents, inserting inline/regular/prealloc/hole items, updating extent references, qgroup tracing, and restoring logged checksums.
- Replays directory state using `BTRFS_DIR_LOG_INDEX_KEY` range items that make the log authoritative for selected directory index ranges and allow deleted entries to be removed after a crash.
- Reconciles inode refs and extrefs during replay, removing stale/conflicting names from directories and backrefs before installing logged names.
- Fixes link counts after replay through a temporary fixup namespace keyed by `BTRFS_TREE_LOG_FIXUP_OBJECTID`.
- Logs inode items, inode refs/extrefs, xattrs, holes, directory index items, delayed directory insertions/deletions, changed extents, prealloc extents past EOF, and checksums.
- Detects rename/link/unlink conflict cases that require logging additional parent/conflicting inodes or falling back to a full transaction commit.
- Updates the log during live link/rename/unlink operations by deleting stale logged dentries/backrefs and logging new names when needed.
- Records directory states that must force full commits for unlink, rename, snapshot destroy, and new subvolume cases.

Important data flows:
- Fsync entry: `btrfs_log_dentry_safe()` calls `btrfs_log_inode_parent()`, which starts a log transaction, logs the target inode, logs required parents/ancestors/new dentries, ends the log transaction, and returns either log success, no-sync-needed, or force-commit.
- Log sync: `btrfs_sync_log()` waits for writers, writes dirty log pages for the subvolume log, updates the log-root tree item, writes the log-root tree, waits for writeback, records the log root in the superblock, wakes waiters, and propagates the result to all contexts in that log transaction.
- Replay: `btrfs_recover_log_trees()` first pins all log extents, then repeatedly scans log-root-tree entries for each stage. `replay_one_buffer()` dispatches log leaf items to inode overwrite, directory delete replay, dir-index replay, xattr overwrite, inode-ref reconciliation, or extent replay.
- Extent replay: `replay_one_extent()` reads the logged file extent item, drops overlapping subvolume extents, inserts the logged item or explicit hole, adds/allocates extent refs, restores checksums from the log csum items into the real csum tree, updates the inode file-extent range, nbytes, and inode item.
- Directory replay: logged range items identify directory index offsets where the log is authoritative. `replay_dir_deletes()` scans subvolume dir-index items in those ranges and removes entries missing from the log; `replay_one_dir_item()` installs logged names and queues non-directory targets for link-count fixup.
- Inode logging: `btrfs_log_inode()` decides full vs fast logging from inode mode, runtime flags, prior logging state, and requested mode. It copies selected B-tree items, logs all xattrs, logs holes for `NO_HOLES`, logs changed extents/checksums for fast fsync, and logs directory changes/delayed items for full directory logging.
- Changed extent logging: `btrfs_log_changed_extents()` drains `inode->extent_tree.modified_extents`, sorts them by file offset, logs each extent and checksum, then marks ordered extents as logged/pending so transaction commit waits for unfinished ordered I/O.
- Checksum logging: `copy_items()`, `log_one_extent()`, and `log_extent_csums()` collect csum records from ordered extents or checksum roots and insert them into the log tree. Reflink cases serialize csum logging and delete overlapping logged csum ranges before insertion.
- Rename/link updates: `btrfs_log_new_name()` checks whether the inode or old directory was already logged, optionally pins the running log, records deletion of the old logged name, then logs the inode with `LOG_INODE_EXISTS` and parent ancestry.

Concurrency and locking:
- Log transaction state is guarded by `root->log_mutex`, `log_root_tree->log_mutex`, `root->log_writers`, two-slot `log_commit[]` state, and wait queues for writers and committers.
- `btrfs_pin_log_trans()` and `btrfs_end_log_trans()` keep a running log transaction from syncing while multi-inode updates are made atomically.
- Per-inode log mutation is serialized by `inode->log_mutex`; transient fields such as `logged_trans`, `last_unlink_trans`, and `last_log_commit` use `inode->lock` where needed.
- Log replay runs during mount under a transaction and uses `BTRFS_FS_LOG_RECOVERING`; it can modify subvolume trees without normal runtime concurrency.
- Tree copying avoids deadlocks by cloning source leaves before mutating the log tree, preventing log-tree COW/allocation paths from running while holding subvolume leaf locks.
- Checksum log ranges use `log_root->log_csum_range` extent locking for reflink overlap cases.
- Ordered extent lists in `btrfs_log_ctx` hold references while fsync needs checksum/state information and are released under the inode lock.
- Commit-root searches set `path->search_commit_root` and `path->skip_locking` only for read-only committed-tree lookups.

Important invariants:
- The tree log is an fsync optimization only; any unsafe or ambiguous case must return `BTRFS_LOG_FORCE_COMMIT` or set `last_trans_log_full_commit`.
- Log replay is staged so inodes exist before directory entries/refs/extents that point to them.
- Directory replay relies on dir-index range items, not old `BTRFS_DIR_ITEM_KEY` logging; old dir item keys from older kernels are ignored.
- Directory inode size is reconstructed during replay from replayed names; logged directory i_size is preserved or reset carefully to avoid stale sizes.
- Regular-file inode `nbytes` is not trusted from logged inode items; replay recomputes it while replaying extents and dropping overlaps.
- `LOG_INODE_EXISTS` logs just enough to recreate/name an inode and may store generation zero to prevent overwriting existing inode metadata during replay.
- Fast fsync must log checksums for new extents and mark ordered extents so transaction commit does not discard the log before ordered I/O completion.
- Prealloc extents at or beyond EOF must be logged explicitly; otherwise replay plus truncation would lose them.
- With `NO_HOLES`, hole ranges must be logged as explicit hole extents when required so replay can remove stale extents.
- Rename/unlink cases that cannot be represented safely by the log must force a full transaction commit.

Notable risks:
- Directory rename/link/unlink replay is highly stateful; missing a parent, range item, backref, or conflict inode can resurrect deleted names, lose renamed files, or create stale dentries.
- Checksum logging around reflinked extents can create overlapping csum items unless serialized and trimmed.
- Log commit ordering with two in-flight log transaction slots, writer counts, superblock updates, and full-commit fallback is subtle, especially for zoned filesystems.
- Replay extent handling touches file extent items, extent refs, checksum trees, qgroups, inode nbytes, and file-extent range tracking in one path; partial failure requires transaction abort diagnostics.
- `logged_trans` is in-memory only, so eviction/reload paths must search the log tree to avoid both missed logging and redundant logging.
- Delayed directory items can be flushed concurrently with logging; the code must collect, batch, and reconcile delayed insertions/deletions without missing index ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-log.h -->
# File Research: sources/os/linux/linux/fs/btrfs/tree-log.h

Public Btrfs tree-log interface. This header defines the log context used across fsync/logging paths, the special log return values, and the exported helpers for syncing, replaying, freeing, pinning, and updating tree logs.

Key responsibilities:
- Defines `BTRFS_NO_LOG_SYNC`, meaning the inode was already safely logged and no log sync is required.
- Defines `BTRFS_LOG_FORCE_COMMIT`, the sentinel that forces callers to commit the whole transaction instead of relying on the tree log.
- Defines `struct btrfs_log_ctx`, which carries per-fsync logging result, log transaction id, inode pointer, ordered extents, conflict inode tracking, recursive logging flags, and reusable scratch extent buffer.
- Provides helpers to initialize log contexts, allocate scratch buffers for expensive item-copy logging, and release ordered extents held by a context.
- Provides inline full-commit flag helpers through `last_trans_log_full_commit`.
- Declares log sync, log freeing, log-root-tree freeing, mount-time log replay, safe dentry logging, log dentry/ref deletion, log transaction pin/end, unlink/snapshot/subvolume recording, and new-name logging APIs.

Important fields:
- `log_ret` and `log_transid` carry the result and id observed by tasks sharing a log commit.
- `log_new_dentries`, `logging_new_name`, and `logging_new_delayed_dentries` control recursive logging of new names and delayed directory entries.
- `logged_before` caches whether the target inode was already logged in the current transaction.
- `ordered_extents` keeps ordered extents whose checksums/state are needed for fsync correctness.
- `conflict_inodes`, `num_conflict_inodes`, and `logging_conflict_inodes` bound and control recursive conflict-inode logging.
- `scratch_eb` is a reusable cloned/dummy extent buffer used to avoid allocation and lock-order problems while copying tree items into the log.

Dependencies:
- Includes Linux list, VFS, fscrypt, and Btrfs transaction definitions.
- Forward-declares VFS dentries/inodes, ordered extents, roots, and transaction handles.

Important invariants:
- `btrfs_set_log_full_commit()` and `btrfs_need_log_full_commit()` are transaction-scoped via `trans->transid`.
- `BTRFS_LOG_FORCE_COMMIT` is deliberately negative so generic error-style propagation marks the log unusable for fast sync.
- Context ordered extents must be released by callers after logging completes or aborts.
- Log pin/end calls must be balanced to avoid either premature log sync or permanently blocked log commits.
- Callers using name/ref deletion helpers must already be in the correct transaction and satisfy the locking contracts established by `tree-log.c`.

Notable risks:
- Misinterpreting `BTRFS_NO_LOG_SYNC` as ordinary success that still needs sync would add unnecessary work; misinterpreting `BTRFS_LOG_FORCE_COMMIT` as a normal error could skip the required full commit fallback.
- `struct btrfs_log_ctx` is shared across recursive logging paths, so flag restoration and conflict list cleanup are essential.
- The header exposes low-level log mutation functions whose safety depends on precise ordering around rename, unlink, snapshot deletion, and subvolume creation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-log.h -->