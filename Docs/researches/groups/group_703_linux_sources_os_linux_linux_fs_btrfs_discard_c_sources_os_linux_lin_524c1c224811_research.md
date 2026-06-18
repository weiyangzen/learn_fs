# Group Research: group_703_linux_sources_os_linux_linux_fs_btrfs_discard_c_sources_os_linux_lin_524c1c224811

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/linux/linux`  
Files read: all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/discard.c -->
# File Research: sources/os/linux/linux/fs/btrfs/discard.c

## Purpose

`discard.c` implements Btrfs asynchronous discard, the background TRIM/discard engine for free regions in data-only block groups. It avoids doing large synchronous discards during transaction commit by queueing block groups on LRU-like discard lists and trimming one region at a time from delayed work.

The file explicitly excludes mixed block groups and relies on the in-memory free-space cache for discard state, so discard state is rebuilt after mount or crash rather than persisted.

## Main Concepts

- `btrfs_discard_ctl` is the central controller, owned by `btrfs_fs_info`.
- Block groups carry discard scheduling state: `discard_list`, `discard_index`, `discard_state`, `discard_cursor`, and `discard_eligible_time`.
- There are multiple discard lists indexed by priority/filter:
  - index 0: fully free/unused block groups waiting for final trim
  - later indexes: progressively smaller discard size filters
- The worker performs a two-pass trim:
  - `BTRFS_DISCARD_EXTENTS`: discard free-space extents first
  - `BTRFS_DISCARD_BITMAPS`: discard bitmap-backed free-space ranges later
  - `BTRFS_DISCARD_FULLY_REMAPPED`: special handling for remapped empty block groups

## Key Constants

- `BTRFS_DISCARD_DELAY`: initial 120 second delay before regular async discard.
- `BTRFS_DISCARD_UNUSED_DELAY`: shorter 10 second delay for unused block groups.
- `BTRFS_DISCARD_MAX_IOPS`: default 1000 IOPS cap.
- `discard_minlen[]`: discard size filters using `0`, `BTRFS_ASYNC_DISCARD_MAX_FILTER`, and `BTRFS_ASYNC_DISCARD_MIN_FILTER`.

## Important Functions

- `btrfs_discard_init()`: initializes lock, delayed work, list heads, counters, size limits, IOPS/KiB limits, and stats.
- `btrfs_discard_resume()`: enables async discard when the mount option is active and punts already-unused block groups into the discard pipeline.
- `btrfs_discard_stop()`: clears `BTRFS_FS_DISCARD_RUNNING`.
- `btrfs_discard_cleanup()`: stops discard, cancels delayed work, and purges queued block groups.
- `btrfs_discard_queue_work()`: queues a block group for async discard if `DISCARD_ASYNC` is enabled.
- `btrfs_discard_cancel_work()`: removes a block group and reschedules if the cancelled group was the active one.
- `btrfs_discard_schedule_work()`: computes delayed-work timing using IOPS, byte-rate, prior discard size, and block-group eligibility.
- `btrfs_discard_workfn()`: main state machine; selects a block group, trims one range, advances cursor/state, updates stats, and schedules the next unit.
- `btrfs_discard_check_filter()`: reprioritizes a block group when newly freed/coalesced space exceeds a higher filter.
- `btrfs_discard_update_discardable()`: propagates per-free-space-cache discardable byte/extent deltas to the global discard controller.
- `btrfs_discard_punt_unused_bgs_list()`: moves unused block groups into async discard before they go down the normal unused block-group path.

## Control Flow

1. A block group becomes discardable or unused.
2. `btrfs_discard_queue_work()` classifies it:
   - empty block groups go to the unused discard list
   - non-empty data-only block groups go to filtered discard lists
3. `btrfs_discard_schedule_work()` arms delayed work if needed.
4. `btrfs_discard_workfn()`:
   - selects an eligible block group with `peek_discard_list()`
   - initializes/reset cursor and state
   - trims extents, bitmaps, or fully remapped groups
   - moves the group to the next discard state/list or marks it unused
5. Cleanup/remount paths stop or purge the queues.

## Locking and Lifetime

- `discard_ctl->lock` protects discard lists, active `discard_ctl->block_group`, and scheduling state.
- Queued block groups receive an extra reference via `btrfs_get_block_group()`.
- Removal and purge paths drop the queue reference with `btrfs_put_block_group()`.
- `remove_from_discard_list()` also detects if the block group is currently active.

## Integration Points

- Uses block group helpers from `block-group.h`.
- Uses trim helpers from `free-space-cache.h`.
- Controlled by mount option `DISCARD_ASYNC`.
- Called from mount/resume, transaction/free-space accounting, unused block-group handling, and filesystem shutdown.
- `disk-io.c` calls `btrfs_discard_init()`, `btrfs_discard_resume()`, and `btrfs_discard_cleanup()`.

## Risks and Invariants

- Only data-only block groups are supported.
- Mixed block groups are intentionally skipped.
- The unused-list path must avoid infinite loops when an unused block group becomes non-empty before discard.
- Accurate block-group reference handling is critical because workqueue and queue ownership overlap.
- Delay calculation depends on corrected global discardable counters; negative counter drift is defensively repaired.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/discard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/discard.h -->
# File Research: sources/os/linux/linux/fs/btrfs/discard.h

## Purpose

`discard.h` is the public interface for Btrfs asynchronous discard support.

## Exposed Constants

- `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`: default maximum async discard size, 64 MiB.
- `BTRFS_ASYNC_DISCARD_MAX_FILTER`: large discard filter, 1 MiB.
- `BTRFS_ASYNC_DISCARD_MIN_FILTER`: small discard filter, 32 KiB.

## Public API

List and queue management:

- `btrfs_discard_check_filter()`
- `btrfs_discard_cancel_work()`
- `btrfs_discard_queue_work()`
- `btrfs_discard_schedule_work()`

Accounting:

- `btrfs_discard_calc_delay()`
- `btrfs_discard_update_discardable()`

Lifecycle:

- `btrfs_discard_punt_unused_bgs_list()`
- `btrfs_discard_resume()`
- `btrfs_discard_stop()`
- `btrfs_discard_init()`
- `btrfs_discard_cleanup()`

## Integration Points

This header is consumed by mount/open/close code, free-space/block-group code, and transaction paths that need to queue, update, or shut down async discard.

## Invariants

The header only forward-declares Btrfs core structs, keeping the discard interface narrow and avoiding heavy include coupling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/discard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/disk-io.c -->
# File Research: sources/os/linux/linux/fs/btrfs/disk-io.c

## Purpose

`disk-io.c` is a central Btrfs mount, metadata I/O, root-management, superblock, transaction-cleanup, and filesystem shutdown implementation. It ties together superblock validation, tree block reads/writes, root loading, workqueue setup, log replay, writable mount preparation, superblock commits, and close-time teardown.

## Major Responsibilities

- Validate and checksum metadata tree blocks.
- Read extent buffers and retry alternate mirrors.
- Allocate, initialize, cache, and release Btrfs roots.
- Load global roots, filesystem roots, and important superblock roots.
- Initialize `btrfs_fs_info`, mount-time state, counters, locks, workqueues, and btree inode.
- Validate superblocks and feature compatibility.
- Execute `open_ctree()` mount flow.
- Write superblocks to all writable metadata devices.
- Execute `close_ctree()` shutdown flow.
- Clean up aborted transactions, dirty block groups, delayed refs, ordered extents, delalloc, pinned extents, and logs.
- Allocate new object IDs for roots.

## Metadata Checksum and Read Path

Key functions:

- `csum_tree_block()`: computes a checksum over a metadata tree block, skipping the checksum field itself.
- `btrfs_buffer_uptodate()`: checks whether an extent buffer is uptodate and matches the expected parent transid and optional parent check.
- `btrfs_check_super_csum()`: verifies a raw disk superblock checksum.
- `btrfs_read_extent_buffer()`: reads a tree block, retries mirrors on failure, and repairs a failed mirror after a successful alternate read.
- `btree_csum_one_bio()`: validates and checksums dirty metadata before writeback.
- `btrfs_validate_extent_buffer()`: performs read-time validation: bytenr, fsid, level, checksum, generation, first key, owner root, and leaf/node structural checks.
- `read_tree_block()`: allocates/fetches an extent buffer and reads it with required parentness checks.

## Btree Address-Space Operations

The file defines `btree_aops` for the special btree inode:

- `writepages = btree_writepages`
- `release_folio = btree_release_folio`
- `invalidate_folio = btree_invalidate_folio`
- `migrate_folio = btree_migrate_folio`
- `dirty_folio = btree_dirty_folio` in debug builds, otherwise `filemap_dirty_folio`

These operations enforce metadata-buffer lifetime rules and prevent unsafe migration or release while dirty/writeback state exists.

## Root Management

Important functions:

- `btrfs_alloc_root()`: allocates and initializes in-memory root structures, locks, lists, xarrays, refcounts, logging state, and per-root extent I/O trees.
- `btrfs_create_tree()`: creates a new tree root in a transaction and inserts its root item.
- `btrfs_read_tree_root()`: reads a root item and root node from the tree root.
- `btrfs_insert_fs_root()`: inserts a filesystem root into `fs_roots_radix`.
- `btrfs_get_fs_root()`: obtains a referenced global or filesystem root, loading from disk as needed.
- `btrfs_get_new_fs_root()`: same path for newly exposed roots with optional anonymous device handling.
- `btrfs_get_fs_root_commit_root()`: reads a temporary root from the commit root for backref/qgroup lookups.
- `btrfs_put_root()`: drops root references and frees root state.
- `btrfs_free_fs_roots()`: drops cached filesystem roots and dead roots.
- `btrfs_drop_and_free_fs_root()`: removes a root from the radix tree and drops the radix reference.

Global roots are stored in `fs_info->global_root_tree` and protected by `global_root_lock`. Helpers include:

- `btrfs_global_root_insert()`
- `btrfs_global_root_delete()`
- `btrfs_global_root()`
- `btrfs_csum_root()`
- `btrfs_extent_root()`

For extent-tree-v2, `btrfs_global_root_id()` maps a bytenr to a block group’s global root id.

## Log Tree Support

- `btrfs_init_log_root_tree()`: initializes the global log root tree.
- `btrfs_add_log_tree()`: creates a per-root log tree.
- `btrfs_replay_log()`: reads the log tree after mount and calls log recovery, committing the superblock if necessary for read-only replay cases.

## Mount-Time Initialization

`btrfs_init_fs_info()` initializes nearly all `fs_info` synchronization objects, lists, trees, counters, block reservations, work structures, discard control, reclaim state, qgroup state, scrub state, balance state, default sizes, and mount defaults.

`init_mount_fs_info()` attaches `fs_info` to the superblock, sets temporary block size values, initializes percpu counters, delayed root state, read-only/error flags, and stripe hash structures.

`btrfs_init_workqueues()` creates the main Btrfs workqueues, including workers for delalloc, flushing, caching, fixup, endio, metadata endio, read-modify-write, delayed metadata, qgroup rescan, and async discard.

## Superblock Validation

`btrfs_validate_super()` checks:

- magic value
- supported super flags
- root/chunk/log levels
- sectorsize and nodesize validity
- page-size support
- leafsize consistency
- root alignment
- fsid and metadata_uuid consistency
- device item fsid
- feature dependency rules for block-group-tree and remap-tree
- bytes used sanity
- stripesize
- device count
- super mirror bytenr
- system chunk array validity
- suspicious generation relationships

`btrfs_validate_write_super()` adds write-time checks for checksum type and incompat feature mask.

## Root Loading

- `load_super_root()` reads a root node directly from superblock bytenr/generation/level.
- `load_important_roots()` loads the tree root and optional remap root.
- `load_global_roots()` loads extent, csum, and optional free-space roots.
- `btrfs_read_roots()` loads block group, device, data reloc/remap, quota, UUID, RAID stripe, and related roots.

`init_tree_roots()` attempts normal root loading and, if configured, iterates backup root slots via `read_backup_root()`.

## `open_ctree()` Flow

`open_ctree()` is the primary mount entry point. Its high-level flow is:

1. Initialize mount `fs_info`.
2. Allocate tree and chunk roots.
3. Initialize the btree inode.
4. Read and checksum the disk superblock.
5. Copy superblock state into `super_copy` and `super_for_commit`.
6. Validate superblock and mount options.
7. Set filesystem block sizes and checksum parameters.
8. Initialize compression workspace and workqueues.
9. Read system chunk array and chunk tree.
10. Load tree roots and device/zone info.
11. Verify device items and device extents.
12. Recover balance/dev-replace/zoned/sysfs/space info/block groups.
13. Start cleaner and transaction kthreads.
14. Read qgroup config and optionally replay log.
15. Load the default filesystem root.
16. For writable mounts, run `btrfs_start_pre_rw_mount()`, resume async discard, and possibly rescan UUID tree.
17. Mark filesystem open.

The failure path unwinds sysfs, block groups, roots, workers, btree inode, and mapping tree in reverse order.

## Writable Mount Preparation

`btrfs_start_pre_rw_mount()` handles read-write setup shared by initial mount and remount:

- rebuilds or deletes free-space tree as requested
- removes orphan free-space tree entries
- finds orphan roots before orphan cleanup
- cleans filesystem roots and orphan items
- recovers relocation
- creates free-space tree if requested
- syncs v1 space cache setting
- resumes balance and device replace
- resumes qgroup rescan
- creates UUID tree if missing

## Background Threads

- `cleaner_kthread()`: delayed iputs, deleted snapshots, defrag, remap handling, unused block groups, and block group reclaim.
- `transaction_kthread()`: periodically commits transactions based on interval or explicit commit flag, and invokes transaction cleanup on errors.
- `btrfs_uuid_rescan_kthread()`: repairs/refreshes UUID tree entries.

## Superblock Write Path

- `backup_super_roots()`: rotates and fills backup root slots before transaction super writes.
- `write_dev_supers()`: writes one or more superblock mirrors to a device using direct bios, FUA for primary when barriers are enabled, and per-device error accounting.
- `wait_dev_supers()`: waits for submitted superblock writes and detects primary/all-copy failure.
- `barrier_all_devices()`: submits and waits for flushes across writable metadata devices.
- `write_all_supers()`: coordinates barriers, backup roots, per-device superblock contents, super validation, write submission, completion, and tolerated error thresholds.

## Shutdown and Cleanup

`close_ctree()` is a carefully ordered teardown path. It:

- marks closing start
- wakes unfinished drops
- cancels reclaim work
- parks cleaner
- waits for qgroup/UUID/balance/dev-replace/scrub/defrag activity
- handles aborted filesystem state
- flushes workqueues that may create delayed iputs or ordered completions
- runs delayed iputs
- cancels reclaim/shrinker works
- stops async discard
- commits the superblock unless read-only or shutdown
- stops transaction and cleaner threads
- frees qgroup config, sysfs, block groups, roots, workers, btree inode, and mapping tree

Transaction error cleanup is handled by:

- `btrfs_cleanup_transaction()`
- `btrfs_cleanup_one_transaction()`
- `btrfs_cleanup_dirty_bgs()`
- `btrfs_destroy_marked_extents()`
- `btrfs_destroy_pinned_extent()`
- `btrfs_destroy_all_ordered_extents()`
- `btrfs_destroy_all_delalloc_inodes()`
- `btrfs_drop_all_logs()`
- `btrfs_free_all_qgroup_pertrans()`

## Object ID Allocation

- `btrfs_init_root_free_objectid()` searches the root for the highest valid objectid and initializes `root->free_objectid`.
- `btrfs_get_free_objectid()` returns and increments the next free objectid under `objectid_mutex`.

## Integration Points

This file integrates with nearly every Btrfs subsystem: transactions, extent I/O, block groups, chunk/device mapping, free-space cache/tree, qgroups, UUID tree, dev-replace, zoned mode, relocation, scrub, compression, tree checker, sysfs, async discard, and tree logging.

## Risks and Invariants

- Metadata validation must reject stale, misplaced, wrong-owner, wrong-level, or corrupt tree blocks.
- Root reference counts and radix/global-tree insertion must stay balanced.
- Mount failure unwind order is critical to avoid leaked workers, roots, block groups, or btree inode pages.
- Superblock writes must respect degradability and primary-super failure rules.
- Shutdown order prevents workqueues from creating delayed iputs after cleaner teardown.
- Aborted transaction cleanup must unblock waiters and clear dirty/pinned metadata without relying on normal commit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/disk-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/disk-io.h -->
# File Research: sources/os/linux/linux/fs/btrfs/disk-io.h

## Purpose

`disk-io.h` declares the public interface for Btrfs disk/tree I/O, root management, mount/open/close lifecycle, superblock validation/writing, metadata buffer validation, log tree allocation, transaction cleanup, and object-id allocation.

## Important Constants

- `BTRFS_SUPER_MIRROR_MAX`: three superblock mirror locations.
- `BTRFS_SUPER_MIRROR_SHIFT`: shift used to derive backup superblock offsets.
- `BTRFS_BDEV_BLOCKSIZE`: fixed 4096-byte block size used for specific metadata reads like superblocks.
- `btrfs_sb_offset()`: inline helper returning primary or backup superblock offsets.

## Main API Groups

Mount and filesystem lifecycle:

- `btrfs_init_fs_info()`
- `open_ctree()`
- `close_ctree()`
- `btrfs_start_pre_rw_mount()`
- `btrfs_free_fs_info()`

Superblock and feature handling:

- `btrfs_check_super_csum()`
- `btrfs_validate_super()`
- `btrfs_check_features()`
- `write_all_supers()`
- `btrfs_commit_super()`
- `btrfs_get_num_tolerated_disk_barrier_failures()`

Tree block I/O:

- `read_tree_block()`
- `btrfs_find_create_tree_block()`
- `btrfs_validate_extent_buffer()`
- `btrfs_buffer_uptodate()`
- `btrfs_read_extent_buffer()`
- `btree_csum_one_bio()`
- `btrfs_mark_buffer_dirty()`

Root management:

- `btrfs_read_tree_root()`
- `btrfs_insert_fs_root()`
- `btrfs_free_fs_roots()`
- `btrfs_get_fs_root()`
- `btrfs_get_new_fs_root()`
- `btrfs_get_fs_root_commit_root()`
- `btrfs_global_root_insert()`
- `btrfs_global_root_delete()`
- `btrfs_global_root()`
- `btrfs_csum_root()`
- `btrfs_extent_root()`
- `btrfs_drop_and_free_fs_root()`
- `btrfs_put_root()`
- `btrfs_create_tree()`

Log tree and transaction cleanup:

- `btrfs_alloc_log_tree_node()`
- `btrfs_init_log_root_tree()`
- `btrfs_add_log_tree()`
- `btrfs_cleanup_dirty_bgs()`
- `btrfs_cleanup_one_transaction()`

Object-id helpers:

- `btrfs_get_free_objectid()`
- `btrfs_init_root_free_objectid()`

## Inline Helper

`btrfs_grab_root()` conditionally increments a root reference if the root is non-null and not already at zero, protecting callers from use-after-free when retrieving roots from shared structures.

## Integration Points

This header is included by Btrfs mount code, export code, transaction code, root-tree users, metadata I/O paths, and test infrastructure.

## Invariants

- Superblock offsets are fixed and must not be changed.
- `btrfs_grab_root()` does not guarantee the tree is not being dropped; it only protects the root structure lifetime.
- Callers must pair grabbed/read roots with `btrfs_put_root()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/disk-io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/export.c -->
# File Research: sources/os/linux/linux/fs/btrfs/export.c

## Purpose

`export.c` implements Btrfs export operations for file handles, primarily for NFS/exportfs support. It encodes Btrfs inode/root identities into stable file handles and decodes those handles back into dentries, parents, and names across subvolumes.

## File Handle Encoding

`btrfs_encode_fh()` fills `struct btrfs_fid` with:

- inode objectid
- root objectid
- inode generation
- optional parent objectid
- optional parent generation
- optional parent root objectid when the parent is in a different subvolume/root

It returns one of the Btrfs file-handle types:

- `FILEID_BTRFS_WITHOUT_PARENT`
- `FILEID_BTRFS_WITH_PARENT`
- `FILEID_BTRFS_WITH_PARENT_ROOT`

If the caller-provided buffer is too small, it updates `max_len` and returns `FILEID_INVALID`.

## Dentry Reconstruction

`btrfs_get_dentry()` reconstructs a dentry from `objectid`, `root_objectid`, and optional generation:

1. Rejects reserved object IDs below `BTRFS_FIRST_FREE_OBJECTID`.
2. Gets the root via `btrfs_get_fs_root()`.
3. Looks up the inode via `btrfs_iget()`.
4. Validates generation if nonzero.
5. Returns an alias dentry via `d_obtain_alias()`.

`btrfs_fh_to_dentry()` decodes the inode identity from a file handle and calls `btrfs_get_dentry()`.

`btrfs_fh_to_parent()` decodes parent identity, including cross-root parent handles, and calls `btrfs_get_dentry()`.

## Parent Lookup

`btrfs_get_parent()` finds a child dentry’s parent:

- For subvolume roots (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for `BTRFS_ROOT_BACKREF_KEY`.
- For regular inodes, it searches the inode’s root for `BTRFS_INODE_REF_KEY`.
- It walks to the previous matching key after a search with offset `-1`.
- It returns either a parent dentry in another root or a parent inode alias in the same root.

## Name Lookup

`btrfs_get_name()` resolves a child name relative to a parent dentry:

- Verifies the parent is a directory.
- For subvolume roots, reads the name from `BTRFS_ROOT_BACKREF_KEY`.
- For regular inodes, reads the name from `BTRFS_INODE_REF_KEY`.
- Copies the stored name from the leaf and NUL-terminates it for exportfs reconnect logic.

## Export Operations

`btrfs_export_ops` wires Btrfs into exportfs:

- `.encode_fh = btrfs_encode_fh`
- `.fh_to_dentry = btrfs_fh_to_dentry`
- `.fh_to_parent = btrfs_fh_to_parent`
- `.get_parent = btrfs_get_parent`
- `.get_name = btrfs_get_name`

## Integration Points

The file depends on root lookup from `disk-io.c`, inode lookup from Btrfs inode code, key search from the Btrfs tree API, and exportfs from the VFS.

## Risks and Invariants

- Generation checks protect against stale file handles.
- Cross-subvolume parent handles require `parent_root_objectid`.
- Reserved object IDs are rejected as stale.
- Parent/name lookup assumes Btrfs backref items are present and structurally valid.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/export.h -->
# File Research: sources/os/linux/linux/fs/btrfs/export.h

## Purpose

`export.h` declares Btrfs exportfs support and defines the packed file-handle payload used by `export.c`.

## Public Declarations

- `btrfs_export_ops`: exported `struct export_operations` used by the superblock/exportfs layer.
- `btrfs_get_dentry()`: reconstructs a dentry from objectid, root objectid, and generation.
- `btrfs_get_parent()`: finds a dentry’s parent for exportfs reconnect.

## Data Structure

`struct btrfs_fid` is a packed file identifier containing:

- `objectid`
- `root_objectid`
- `gen`
- `parent_objectid`
- `parent_gen`
- `parent_root_objectid`

The optional parent fields allow Btrfs to encode both ordinary parent relationships and cross-root/subvolume parent relationships.

## Integration Points

Included by `export.c` and any Btrfs code needing direct exportfs helpers.

## Invariants

The structure is packed because file handles are serialized into fixed-size exportfs buffers, and size calculations in `export.c` rely on exact field layout.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent-io-tree.c -->
# File Research: sources/os/linux/linux/fs/btrfs/extent-io-tree.c

## Purpose

`extent-io-tree.c` implements Btrfs byte-range state tracking using an RB-tree of `extent_state` records. It supports setting, clearing, converting, locking, waiting on, querying, counting, and iterating state bits over inclusive byte ranges.

This state engine underpins inode I/O state, delalloc tracking, dirty metadata tracking, pinned extents, log ranges, excluded extents, device allocation state, and selftests.

## Core Data Model

- `struct extent_io_tree` owns an RB-tree of `extent_state` records and a spinlock.
- `struct extent_state` records:
  - inclusive `start` and `end`
  - RB-tree node
  - waitqueue
  - refcount
  - bitmask state
  - optional debug leak-list node

Ranges are split when operations affect only part of a state and merged when adjacent states have identical mergeable bits.

## Allocation and Debugging

- `alloc_extent_state()` allocates from the `btrfs_extent_state` slab cache.
- `btrfs_free_extent_state()` drops refcounts and frees only at zero refs.
- Debug builds track all allocated states and report leaks.
- Debug range checks detect suspicious inode I/O ranges.

Slab lifecycle:

- `btrfs_extent_state_init_cachep()`
- `btrfs_extent_state_free_cachep()`

## Tree Initialization and Release

- `btrfs_extent_io_tree_init()` initializes the RB-tree, spinlock, owner, and owner pointer.
- `btrfs_extent_io_tree_release()` removes all states from a tree, asserting no lock bits and no waiters remain.

## Search Helpers

The file provides internal search helpers:

- `tree_search_for_insert()`: finds containing or next state and optional insertion parent/link.
- `tree_search_prev_next()`: finds containing state or neighboring previous/next states.
- `tree_search()`: inexact search returning containing or next state.
- `find_first_extent_bit_state()`: finds first state with any requested bit.

## Set/Clear/Convert Mechanics

`set_extent_bit()` is the central set operation. It:

- handles `EXTENT_NOWAIT` by selecting `GFP_NOWAIT`
- preallocates state records
- detects exclusive lock-bit conflicts
- splits existing ranges as needed
- inserts state records into holes
- sets requested bits
- caches useful states for repeated calls
- merges adjacent compatible states

Public wrappers include:

- `btrfs_set_extent_bit()`
- `btrfs_set_record_extent_bits()`

`btrfs_clear_extent_bit_changeset()` is the central clear operation. It:

- optionally treats `EXTENT_CLEAR_ALL_BITS` as deletion
- handles delalloc/noreserve coupling
- splits states around the cleared range
- clears requested bits
- wakes waiters for lock-bit clears
- deletes empty states
- records changesets when requested

Public wrappers include:

- `btrfs_clear_extent_bit()`
- `btrfs_clear_record_extent_bits()`
- `btrfs_unlock_extent()`
- `btrfs_unlock_dio_extent()`

`btrfs_convert_extent_bit()` converts one set of bits to another over a range, intended for mergeable state transitions such as delalloc-to-dirty, not boundary/lock semantics.

## Locking and Waiting

- `btrfs_try_lock_extent_bits()` tries to set exclusive lock bits and rolls back partial success on conflict.
- `btrfs_lock_extent_bits()` retries on `-EEXIST`, waits on conflicting states via `wait_extent_bit()`, then tries again.
- `wait_extent_bit()` waits uninterruptibly on state waitqueues until requested lock bits clear.
- `state_wake_up()` wakes waiters when `EXTENT_LOCK_BITS` are cleared.

## Query Helpers

- `btrfs_find_first_extent_bit()`: finds first state with any requested bit.
- `btrfs_find_contiguous_extent_bit()`: returns the full contiguous span with requested bits.
- `btrfs_find_delalloc_range()`: finds a delalloc run up to `max_bytes`, respecting boundaries.
- `btrfs_find_first_clear_extent_bit()`: finds the first range where requested bits are not set, treating holes as clear.
- `btrfs_count_range_bits()`: counts bytes with all requested bits set, optionally requiring contiguity.
- `btrfs_test_range_bit_exists()`: checks whether a bit exists anywhere in a range.
- `btrfs_test_range_bit()`: checks whether a whole half-open range contains one bit continuously.
- `btrfs_get_range_bits()`: ORs all state bits present over a range and caches the first found state.
- `btrfs_next_extent_state()`: returns a referenced next state for controlled iteration.

## Changeset Accounting

`add_extent_changeset()` records changed byte counts and optionally changed ranges in an `extent_changeset`. Set/clear record wrappers use this to report what actually changed.

## Integration Points

For inode-owned trees, bit changes call delalloc accounting hooks:

- `btrfs_set_delalloc_extent()`
- `btrfs_clear_delalloc_extent()`
- `btrfs_merge_delalloc_extent()`
- `btrfs_split_delalloc_extent()`

The file also emits Btrfs tracepoints for allocation, free, set, clear, and convert operations.

## Risks and Invariants

- All tree mutations require `tree->lock`.
- States with lock bits or boundary bits are not merged.
- Refcounted cached states must be freed by callers or replaced safely.
- Waitqueue activity is protected by the tree lock; release asserts there are no waiters.
- Inclusive end offsets are used internally; some public comments explicitly distinguish half-open caller semantics.
- Allocation retries deliberately drop the spinlock and reschedule when needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent-io-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent-io-tree.h -->
# File Research: sources/os/linux/linux/fs/btrfs/extent-io-tree.h

## Purpose

`extent-io-tree.h` defines the Btrfs extent state bit model, owner types, core data structures, and public API for byte-range state tracking.

## State Bits

The enum defines many range-state flags, including:

- `EXTENT_DIRTY`
- `EXTENT_LOCKED`
- `EXTENT_DIO_LOCKED`
- `EXTENT_DELALLOC`
- `EXTENT_DEFRAG`
- `EXTENT_BOUNDARY`
- `EXTENT_NODATASUM`
- `EXTENT_NORESERVE`
- `EXTENT_QGROUP_RESERVED`
- `EXTENT_DELALLOC_NEW`
- `EXTENT_FINISHING_ORDERED`
- `EXTENT_ADD_INODE_BYTES`
- `EXTENT_CLEAR_ALL_BITS`
- `EXTENT_NOWAIT`

Control masks:

- `EXTENT_DO_ACCOUNTING`
- `EXTENT_CTLBITS`
- `EXTENT_LOCK_BITS`

Device allocation aliases:

- `CHUNK_ALLOCATED`
- `CHUNK_TRIMMED`
- `CHUNK_STATE_MASK`

## Tree Owners

The owner enum identifies how a tree is used:

- pinned extents
- excluded extents
- btree inode I/O
- regular inode I/O
- relocation blocks
- transaction dirty pages
- root dirty log pages
- inode file extents
- log csum ranges
- selftests
- device allocation state

Owner identity controls whether the tree stores `fs_info` directly or an inode pointer and whether inode delalloc hooks apply.

## Core Structures

`struct extent_io_tree` contains:

- RB-tree root
- `fs_info` or inode owner pointer
- owner id
- spinlock

`struct extent_state` contains:

- inclusive start/end
- RB-tree node
- waitqueue
- refcount
- state bitmask
- optional debug leak-list node

## Public API

Lifecycle:

- `btrfs_extent_io_tree_init()`
- `btrfs_extent_io_tree_release()`
- `btrfs_extent_state_init_cachep()`
- `btrfs_extent_state_free_cachep()`
- `btrfs_free_extent_state()`

Locking:

- `btrfs_lock_extent_bits()`
- `btrfs_try_lock_extent_bits()`
- `btrfs_lock_extent()`
- `btrfs_try_lock_extent()`
- `btrfs_unlock_extent()`
- `btrfs_lock_dio_extent()`
- `btrfs_try_lock_dio_extent()`
- `btrfs_unlock_dio_extent()`

Bit mutation:

- `btrfs_set_extent_bit()`
- `btrfs_clear_extent_bit_changeset()`
- `btrfs_clear_extent_bit()`
- `btrfs_clear_extent_dirty()`
- `btrfs_convert_extent_bit()`
- `btrfs_set_record_extent_bits()`
- `btrfs_clear_record_extent_bits()`

Queries:

- `btrfs_count_range_bits()`
- `btrfs_test_range_bit()`
- `btrfs_test_range_bit_exists()`
- `btrfs_get_range_bits()`
- `btrfs_find_first_extent_bit()`
- `btrfs_find_first_clear_extent_bit()`
- `btrfs_find_contiguous_extent_bit()`
- `btrfs_find_delalloc_range()`
- `btrfs_next_extent_state()`

Owner conversion:

- `btrfs_extent_io_tree_to_inode()`
- `btrfs_extent_io_tree_to_fs_info()`

## Integration Points

This header is used widely by Btrfs metadata, inode I/O, transaction, free-space, block-group, log, qgroup, and device-allocation code.

## Invariants

- Range end values in `extent_state` are inclusive.
- `EXTENT_NOWAIT` is a control bit and must be masked out before normal state manipulation.
- Device allocation trees reuse some extent-state bits with different names and must not use lock/boundary/accounting bits with special mutation semantics.
- Cached `extent_state` pointers are refcounted and must be released.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent-io-tree.h -->