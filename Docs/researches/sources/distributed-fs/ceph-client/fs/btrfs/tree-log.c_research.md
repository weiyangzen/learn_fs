# sources/distributed-fs/ceph-client/fs/btrfs/tree-log.c

## Purpose

`tree-log.c` implements Btrfs tree logging: the write-ahead log used by fsync/O_SYNC paths to persist selected inode, directory, extent, checksum, xattr, and name-reference changes without committing the whole transaction. On mount after an unclean shutdown it replays log trees back into subvolume trees, fixes link counts, restores data extent references and checksums, and then commits the recovery transaction. It also maintains the in-memory coordination needed for concurrent log writers, log committers, rename/link/unlink log updates, and forced full transaction commit fallback.

The file has two large halves:

- log replay: walking log trees, pinning log extents, replaying inode items, dir index items, xattrs, inode refs/extrefs, file extents, checksum records, and cleanup/fixup items.
- log production/sync: starting/joining log transactions, copying changed items into per-root log trees, recording authoritative directory ranges for deletion replay, logging changed extents/checksums, handling delayed directory items, updating the log-root tree, writing log extents and superblocks, and freeing log trees.

## Important APIs, types, and constants

- `MAX_CONFLICT_INODES` caps how many conflicting inodes discovered during name-ref override checks can be recursively logged before forcing a full commit.
- `LOG_INODE_ALL` and `LOG_INODE_EXISTS` select full inode logging versus minimal "this inode exists" logging.
- `LOG_WALK_PIN_ONLY`, `LOG_WALK_REPLAY_INODES`, `LOG_WALK_REPLAY_DIR_INDEX`, and `LOG_WALK_REPLAY_ALL` are the replay phases. Replay intentionally walks the log multiple times to first protect extents, then materialize inodes, then replay names and remaining metadata.
- `struct walk_control` carries the replay/free traversal state: whether blocks are being freed or pinned, current phase, source log root, destination subvolume root, transaction handle, callback, current log leaf/key/slot, and a scratch path for destination tree updates.
- `btrfs_iget_logging()` wraps inode lookup in `memalloc_nofs_save()`/restore to avoid transaction recursion and deadlocks while logging/replaying under a transaction handle.
- `start_log_trans()`, `join_running_log_trans()`, `btrfs_pin_log_trans()`, and `btrfs_end_log_trans()` coordinate writers and committers using root log mutexes, `log_writers`, `log_commit[]`, `log_ctxs[]`, and log transaction IDs.
- `btrfs_sync_log()` is the central fsync log-commit routine. It writes dirty log-tree extents, updates the log-root tree, waits for log IO, records the log root in superblocks, wakes waiting contexts, and returns `BTRFS_LOG_FORCE_COMMIT`/errors when a full commit is required.
- `btrfs_log_dentry_safe()` is the public dentry fsync entry point and delegates to `btrfs_log_inode_parent()`.
- `btrfs_recover_log_trees()` is the mount-time recovery entry point.
- `btrfs_free_log()` and `btrfs_free_log_root_tree()` tear down per-root log trees and the tree of log roots at full transaction commit time.
- `btrfs_del_dir_entries_in_log()`, `btrfs_del_inode_ref_in_log()`, `btrfs_record_unlink_dir()`, `btrfs_record_snapshot_destroy()`, `btrfs_record_new_subvolume()`, and `btrfs_log_new_name()` are integration hooks for unlink, rename, link, snapshot deletion, and subvolume creation code.

## Replay control flow

`btrfs_recover_log_trees()` sets `BTRFS_FS_LOG_RECOVERING`, starts a transaction on the tree root, and then uses `walk_log_tree()` repeatedly. The first pass uses `process_one_buffer()` with `wc.pin = true` to pin log metadata and, on mixed block groups, exclude logged data extents so replay cannot overwrite blocks it still needs. Later passes iterate every per-subvolume log root found in the log-root tree:

1. `LOG_WALK_REPLAY_INODES` copies inode items first. For each inode item, `replay_xattr_deletes()` removes xattrs missing from the log, `replay_dir_deletes()` removes directory entries in logged authoritative ranges but absent from the log, `overwrite_item()` installs the inode item, and regular-file extents beyond logged size are dropped before data extent replay.
2. `LOG_WALK_REPLAY_DIR_INDEX` replays logged `BTRFS_DIR_INDEX_KEY` entries with `replay_one_dir_item()` and `replay_one_name()`, deleting conflicting existing dir entries when needed.
3. `LOG_WALK_REPLAY_ALL` handles remaining item types: xattrs through `overwrite_item()`, inode refs/extrefs through `add_inode_ref()`, and file extents through `replay_one_extent()`.
4. After the all-items phase for a root, `fixup_inode_link_counts()` drains the special `BTRFS_TREE_LOG_FIXUP_OBJECTID` orphan/fixup items and recomputes link counts from inode refs/extrefs. Zero-link directories have delete replay forced recursively and zero-link inodes get orphan items.
5. Recovery commits the transaction, which unpins blocks, and clears `BTRFS_FS_LOG_RECOVERING`.

Replay uses `btrfs_abort_log_replay()` instead of plain transaction abort in most deep replay helpers. It captures and prints the current subvolume leaf and log leaf/key/slot once, making corruption and logic failures diagnosable without flooding logs.

## Replay data and name semantics

`overwrite_item()` is the generic item copier. It searches the destination subvolume tree, inserts or resizes destination items, avoids COW when contents match, preserves old directory `i_size`, and treats inode items with generation zero as "existence only" records that must not blindly overwrite persisted inode data.

`replay_one_extent()` is responsible for the expensive data side effects. It drops overlapping file extents, inserts the logged inline/regular/prealloc extent, updates or allocates data extent references with qgroup tracing, transfers checksums from the log tree to the checksum tree, deletes overlapping checksum ranges first to avoid duplicate/overlapping csum items, updates the inode extent range cache, and corrects inode byte counts.

Directory replay is range-based. Log production creates `BTRFS_DIR_LOG_INDEX_KEY` range items to say "the log is authoritative for this index range." During replay, `find_dir_range()`, `replay_dir_deletes()`, and `check_item_in_log()` scan subvolume dir-index items in those ranges and unlink anything absent from the log. New or changed entries are replayed through `replay_one_name()`, which checks both the dir item and dir index item, removes conflicts with `drop_one_dir_item()`, and defers entries whose inode refs/extrefs are themselves logged so the ref replay path can create the correct links.

Inode reference replay uses `add_inode_ref()`, `__add_inode_ref()`, `unlink_refs_not_in_log()`, `unlink_extrefs_not_in_log()`, and `unlink_old_inode_refs()` to reconcile old-style refs and extended refs. Before adding a logged link, the code removes stale/conflicting refs and directory entries that are not present in the log. This prevents dangling directory entries, duplicate names, wrong hard-link counts, and resurrected old names after rename/unlink crash scenarios.

## Log production control flow

The fsync path enters through `btrfs_log_dentry_safe()`, which gets the parent dentry and calls `btrfs_log_inode_parent()` with `LOG_INODE_ALL`. `btrfs_log_inode_parent()` rejects unsupported cases with full-commit fallback: tree logging disabled, deleted roots, subvolumes created in the current transaction, or later errors. It starts a log transaction, logs the target inode through `btrfs_log_inode()`, and, when needed, logs old/current parents and new ancestors to preserve rename/link semantics.

`btrfs_log_inode()` is the main producer:

- Allocates source and destination paths and locks `inode->log_mutex`.
- Checks whether the inode was already logged in the current transaction with `inode_logged()`, including the evicted-inode case where `logged_trans == 0` and the log tree must be searched.
- Chooses full, existence-only, fast-fsync, or partial directory logging based on inode type, `BTRFS_INODE_NEEDS_FULL_SYNC`, `BTRFS_INODE_COPY_EVERYTHING`, symlink mode, and caller mode.
- Drops or truncates previous log items when relogging would otherwise leave overlapping stale state.
- Copies inode items, refs/extrefs, xattrs, and selected extent data with `copy_inode_items_to_log()`.
- Logs all xattrs with `btrfs_log_all_xattrs()` so replay can detect xattr deletions.
- Logs NO_HOLES gaps with `btrfs_log_holes()` when required.
- For fast fsync, logs modified extent maps through `btrfs_log_changed_extents()` and `log_one_extent()`, plus prealloc extents beyond EOF through `btrfs_log_prealloc_extents()`.
- For full directory logging, logs changed dir-index items and range keys with `log_directory_changes()`, then logs delayed insertion/deletion items directly when possible.
- Updates `inode->logged_trans`, `last_log_commit` for true full inode logging, and resets `last_reflink_trans` after full extent logging.
- Logs conflicting inodes and new delayed dentries after releasing the inode log mutex.

Several helpers intentionally clone source leaves before writing to the log tree (`clone_leaf()`, used by `copy_items()` and directory item logging). This avoids lock-order inversions between subvolume-tree read locks, log-tree COW/write locks, delayed inode mutexes, and reclaim paths.

## Log sync and persistence behavior

`btrfs_sync_log()` serializes commit of a per-root log transaction. It waits for older or concurrent log commits using two alternating `log_commit[]` slots, waits for active writers, and may sleep briefly for batching on non-SSD devices when multiple tasks are logging. It writes dirty extents for the root log with the appropriate `EXTENT_DIRTY_LOG1` or `EXTENT_DIRTY_LOG2` mark, copies the log root item under `root->log_mutex`, advances the root log transid, and then updates the global log-root tree under its log mutex.

After both root log and log-root-tree extents are written and waited on, it acquires `fs_info->tree_log_mutex`, records `super_for_commit` log root bytenr/level, and calls `write_all_supers()`. This lock ordering prevents racing the normal transaction commit superblock write. Any IO error, Btrfs fs error state, ENOSPC/update failure, zoned write hole, or explicit full-commit flag marks the log for full commit and wakes all log contexts with the error/fallback result.

Persistence is split across volatile in-memory fields and on-disk log items:

- `inode->logged_trans`, `last_log_commit`, `last_unlink_trans`, `last_dir_index_offset`, `runtime_flags`, modified extent lists, and log context lists are in-memory coordination/caching only.
- Log trees persist copied btree items, dir-log range items, logged checksums, and log root items until the next full transaction commit frees them.
- Superblocks persist the root of the log-root tree so mount recovery can find every per-subvolume log tree.
- Ordered extents logged by fast fsync are marked so the enclosing transaction waits for their completion before wiping log trees.

## Directory, rename, link, unlink, and subvolume integration

The file encodes many rename/link/unlink crash consistency cases. `btrfs_record_unlink_dir()` marks the unlinked inode's `last_unlink_trans` and, for renames where neither the inode nor old directory was already logged, marks the old directory to force a commit if it is fsynced later. `btrfs_del_dir_entries_in_log()` and `btrfs_del_inode_ref_in_log()` opportunistically remove stale logged names/refs after unlink so a later log sync does not replay old links. `btrfs_log_new_name()` updates the log after rename/link by optionally deleting the old dir entry from the old logged directory and logging the new name/existence chain while pinning the log transaction so the pair of updates is atomic with respect to log sync.

Subvolume and snapshot cases are deliberately conservative. `btrfs_record_snapshot_destroy()` and `btrfs_record_new_subvolume()` set the parent directory's `last_unlink_trans`, causing directory fsync to fall back to a transaction commit when a log replay could otherwise resurrect or reference an unpersisted/deleted root. Rename of subvolumes is handled elsewhere by forcing full commit.

## Dependencies and integration points

This file is tightly integrated with core Btrfs subsystems:

- btree search, insert, delete, item resize, tree walking, and extent buffers from `ctree.h`, `accessors.h`, `locking.h`, and `disk-io.h`.
- transactions and abort/commit paths from `transaction.h` and root-tree helpers.
- extent allocation/refcounting and delayed refs through `extent-tree.h`.
- file extent, checksum, and ordered extent handling through `file-item.h`, `file.h`, compression helpers, and extent maps.
- directory and inode metadata helpers through `dir-item.h`, `inode-item.h`, delayed inode/item APIs, and orphan handling.
- qgroup accounting via `btrfs_qgroup_trace_extent()`.
- block-group/space-info accounting when cleaning log buffers without a transaction.
- fscrypt names for encrypted directory entry operations.
- VFS dentries/inodes, inode versioning, link counts, i_size, and delayed iput.

## Risks and edge cases

- Crash consistency depends on subtle pairings: dir range logging with replay deletion, inode ref replay with directory item replay, checksum overwrite before insert, and parent/ancestor logging for renamed or newly linked inodes.
- `BTRFS_LOG_FORCE_COMMIT` is a correctness escape hatch. Many rare cases intentionally abandon tree logging rather than risk an unreplayable or incomplete log, including deleted roots, current-transaction subvolume roots, too many conflicting inodes, unsafe directory rename cases, new subvolume entries, and some extended-ref ancestor cases.
- Race handling is central: `inode_logged()` must handle eviction resetting `logged_trans`; log commits must coordinate with concurrent writers; rename/link log updates pin or join running log transactions; checksum logging serializes reflink-overlap cases with `log_csum_range`.
- Memory allocation happens under transaction context, so NOFS and leaf cloning are used to avoid reclaim and lock-order deadlocks.
- Zoned filesystems have stricter sequential write constraints. The code waits for previous log commits in more places and may force full commits on log-root-tree write holes.
- Replay error handling must be precise: partial replay with wrong abort/cleanup behavior could corrupt metadata or leave pinned/log blocks inconsistent.
- Directory i_size and inode nbytes are not blindly trusted from log inode items. Replay recomputes or preserves selected fields to avoid data loss, stale directory size, and wrong link counts.

## Test signals

Useful validation should target crash-replay and forced-commit behavior, not only normal fsync success:

- fsync a file after writes, crash before transaction commit, mount, and verify file data, extents, checksums, and inode size.
- fast fsync after random writes, reflinks, compression, NODATASUM, prealloc beyond EOF, NO_HOLES hole punching, and shrinking/expanding truncates.
- directory fsync after create/unlink/rename/link sequences, including cross-directory renames, hard links, and deleted old parents.
- rename/link of already logged inodes and directories, verifying old names are removed and new names survive.
- xattr create/update/delete followed by fsync and crash replay.
- delayed dir item insertion/deletion paths, including deep new directory trees that exercise recursion limiting.
- snapshot deletion and new subvolume creation followed by parent fsync, verifying full commit fallback and no stale log replay.
- zoned-mode log sync behavior and fallback on `-EAGAIN` write holes.
- ENOSPC, EIO, checksum-root lookup failure, and corruption paths that should abort replay or force full commit.
- Link-count repair cases with hard links and directory deletions, ensuring no stale dentries prevent unlink/rmdir after replay.
