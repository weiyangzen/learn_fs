# Group Research: group_915_linux_apfs_rw_sources_local_fs_linux_apfs_rw_object_c_sources_local__8dd18480addd

Scope: `Docs/research_subset_a.md`

Files researched completely:

- `sources/local-fs/linux-apfs-rw/object.c`
- `sources/local-fs/linux-apfs-rw/snapshot.c`
- `sources/local-fs/linux-apfs-rw/spaceman.c`
- `sources/local-fs/linux-apfs-rw/super.c`
- `sources/local-fs/linux-apfs-rw/symlink.c`
- `sources/local-fs/linux-apfs-rw/transaction.c`

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/object.c -->
# File Research: sources/local-fs/linux-apfs-rw/object.c

## Purpose

`object.c` implements APFS object checksum handling, checkpoint-map construction, checkpoint ring index helpers, ephemeral-object lookup, and copy-on-write mapping for non-ephemeral object blocks.

## Main Flows

- `apfs_fletcher64()` computes the APFS object checksum over 32-bit little-endian words, assuming APFS block-size bounds keep accumulator growth safe.
- `apfs_obj_verify_csum()` skips verification for buffers already in the active transaction because their checksum may be stale until commit.
- `apfs_multiblock_verify_csum()` and `apfs_multiblock_set_csum()` verify or set checksums for single-block and multi-block objects after the checksum field.
- `apfs_create_cpm_block()` initializes a checkpoint mapping block, joins it to the current transaction, marks it for checksum, and fills its object header with the current container xid.
- `apfs_create_cpoint_map()` appends a checkpoint mapping entry for an ephemeral object, returning `-ENOSPC` if the mapping block is full.
- `apfs_index_in_data_area()` and `apfs_data_index_to_bno()` convert between block numbers and current checkpoint data-ring positions.
- `apfs_ephemeral_object_lookup()` searches the in-memory ephemeral-object list by oid.
- `apfs_read_object_block()` reads a non-ephemeral object, verifies checksums when node checking is enabled, and performs CoW on write if the object belongs to an older transaction.

## Copy-On-Write Behavior

`apfs_read_object_block()` is the central non-ephemeral object CoW helper. On write, if the object's xid already matches the current container xid, the old buffer is reused. Otherwise, it allocates a new block, copies the old data, queues the old block for freeing unless `preserve` is true, updates physical object oid and xid, joins the new buffer to the transaction, and marks it for checksum.

The `preserve` path is used when the old object remains reachable, such as for snapshots. For preserved non-volume-superblock objects, the volume allocation counters are incremented because CoW adds a live block without freeing the old one.

## Integration Points

This file ties together checksum policy, checkpoint map generation, spaceman block allocation, transaction buffer tracking, and APFS physical/virtual object identity. It is used by transaction checkpoint writes, volume/omap/catalog mapping, snapshot creation, and btree/node update paths.

## Invariants And Risks

- Fletcher checksums assume APFS block sizes are small enough for the simplified implementation.
- Transaction buffers can have stale checksums until final commit.
- Ephemeral object count is fixed by the in-memory list limit elsewhere.
- CoW callers must choose `preserve` correctly or they can either leak accounting or free blocks still needed by snapshots.
- Failure after in-memory allocation changes relies on transaction abort forcing the container read-only rather than rolling back all in-memory state.

## Test Focus

Test checksum verification/set behavior, CoW of physical and virtual objects, preserved versus non-preserved writes, checkpoint-map capacity handling, checkpoint data-ring wraparound, and read-only failure paths after allocation or transaction-join errors.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/object.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/snapshot.c -->
# File Research: sources/local-fs/linux-apfs-rw/snapshot.c

## Purpose

`snapshot.c` implements snapshot creation and snapshot mount switching for APFS volumes. It creates a physical snapshot copy of the volume superblock, writes snapshot metadata/name records, rotates the live extent-reference tree, updates omap snapshot state, and maps snapshot superblocks for read-only snapshot mounts.

## Snapshot Creation

`apfs_ioc_take_snapshot()` handles `APFS_IOC_CREATE_SNAPSHOT`. It requires the ioctl on the root directory inode, checks owner/capability permissions with kernel-version-specific APIs, takes a write reference on the mount, copies the snapshot name from userspace, rejects unterminated or overlong names, and delegates to `apfs_do_ioc_take_snapshot()`.

`apfs_do_ioc_take_snapshot()` starts a regular transaction, checks that the name is unused, flushes all dirty inode metadata, copies the current volume superblock, creates snapshot metadata and name records, creates a new live extent-reference tree, updates omap snapshot tracking, increments the volume snapshot count, forces a commit, and aborts on failure.

## Metadata Records

- `apfs_create_superblock_snapshot()` allocates a new block, copies the current volume superblock, makes the snapshot superblock a physical FS object, clears the snapshot's omap oid, extentref tree oid, and snapshot metadata tree oid, and marks the buffer for checksum.
- `apfs_create_snap_metadata_rec()` inserts a metadata record keyed by current xid. The value stores the old extent-reference tree oid/type, snapshot superblock oid, create/change times, generated snapshot inode number, and null-terminated snapshot name.
- `apfs_create_snap_name_rec()` inserts a name record keyed by snapshot name and valued by current xid.
- `apfs_create_snap_meta_records()` CoWs the snapshot metadata tree root and updates the live volume superblock to point at the new root.

## Omap Snapshot Updates

`apfs_update_omap_snap_tree()` ensures the omap snapshot tree exists, CoWs its root, and inserts the current xid. `apfs_update_omap_snapshots()` CoWs the volume omap object, increments snapshot count, records the most recent snapshot xid, and updates the snapshot tree oid.

## Snapshot Mounting

`apfs_switch_to_snapshot()` is called during read-only mounting when `snap=` is set. It reads the live snapshot metadata tree, resolves the snapshot name to xid, resolves the xid to the snapshot superblock oid, unmaps the current live volume superblock, and maps the snapshot superblock by physical block number.

`apfs_snap_sblock_from_query()` rejects dataless snapshot metadata with `-EOPNOTSUPP`, so unknown dataless snapshot layouts are not mounted.

## Invariants And Risks

- Snapshot creation intentionally commits if the requested name already exists, because no modifications were made yet.
- Snapshot mounts are forced read-only by mount handling in `super.c`.
- Dirty inode metadata is flushed before snapshot layout changes to keep snapshot setup stable.
- Snapshot superblocks do not contain nested snapshot metadata and share omap state with the current volume.
- Failure after mutations relies on transaction abort and read-only fallback rather than fine-grained rollback.

## Test Focus

Test ioctl permission checks, mountpoint-only enforcement, name length and duplicate handling, transaction abort on each creation phase, snapshot metadata/name lookup, snapshot mount by name, dataless snapshot rejection, and consistency of omap snapshot counters and volume snapshot counts.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/spaceman.c -->
# File Research: sources/local-fs/linux-apfs-rw/spaceman.c

## Purpose

`spaceman.c` implements APFS space-manager support for this driver. It reads and maintains the ephemeral spaceman object, tracks internal-pool bitmaps, flushes APFS free queues, allocates normal blocks through chunk-info blocks and bitmaps, and reports free block counts.

## Spaceman Loading

`apfs_read_spaceman()` looks up the spaceman ephemeral object from the checkpoint mapping list, sets its xid to the current transaction, allocates or reuses the in-memory `apfs_spaceman`, reads internal-pool bitmaps on first use, reads main-device spaceman geometry, validates chunk-info limits, and flushes both internal-pool and main free queues at transaction start.

Fusion/large-device support is limited: `apfs_read_spaceman_dev()` rejects `sm_cab_count`, and the file generally operates on `APFS_SD_MAIN`.

## Internal Pool Bitmaps

The internal pool stores APFS metadata such as chunk-info bitmaps and CIBs. The driver keeps its bitmap blocks in memory:

- `apfs_read_ip_bitmaps()` reads all IP bitmap blocks.
- `apfs_write_ip_bitmaps()` writes dirty IP bitmap blocks at commit.
- Dirty IP bitmap writes rotate bitmap blocks by updating xid and bitmap-location arrays, freeing the old bitmap block into the IP free list and allocating a new one.
- `apfs_ip_find_free()`, `apfs_ip_mark_used()`, and `apfs_ip_mark_free()` find and update internal-pool allocation bits.

The free IP bitmap block list is represented by an on-disk linked list stored in variable-length arrays inside the spaceman object.

## Free Queues

APFS free queues delay block reuse by xid. This implementation flushes old free-queue records at transaction start:

- `apfs_free_queue_try_insert()` inserts a free range into either the IP queue or main queue, using ghost records for single-block extents.
- `apfs_free_queue_insert()` caches adjacent free ranges to reduce btree operations.
- `apfs_free_queue_insert_nocache()` bypasses the cache and treats unexpected free-queue fullness as corruption.
- `apfs_flush_free_queue()` repeatedly removes records older than the current xid and marks their blocks free in the IP bitmaps or main chunk bitmaps.

The main free queue node count is tracked to force commits before the queue gets too unbalanced.

## Block Allocation And Freeing

`apfs_spaceman_allocate_block()` scans chunk-info block addresses, optionally backwards to separate metadata and extents, reads each CIB, verifies checksums when requested, and asks `apfs_cib_allocate_block()` to allocate from one of its chunks.

`apfs_chunk_alloc_free()` handles both allocation and freeing within a chunk. It CoWs old chunk bitmaps and old CIBs when their xid predates the current transaction, updates chunk free counts and bitmap addresses, marks buffers dirty or checksummed as needed, and updates total free counts.

`apfs_main_free()` maps a block to chunk and CIB indexes, frees it through `apfs_chunk_free()`, updates the stored CIB address if CoW moved it, and may resume orphan cleanup if freeing enough space clears an earlier `-ENOSPC` condition.

## Free Space Reporting

`apfs_spaceman_get_free_blkcnt()` can run before the full spaceman has been initialized. It ensures ephemeral objects are loaded, locates the spaceman object, and sums free counts for main and tier2 device slots.

## Invariants And Risks

- The code assumes manageable internal-pool bitmap counts and rejects unusually large counts.
- CIB address arrays and other spaceman variable arrays are bounds-checked before access.
- Blocks freed in the current transaction are not reused until after commit.
- CIBs and chunk bitmaps from older transactions must be CoWed before mutation.
- Queue flushing intentionally stops at the current xid.
- Many corruption checks fail hard with `-EFSCORRUPTED`; abort then forces read-only state at the transaction layer.

## Test Focus

Test IP bitmap read/write rotation, free queue insertion and flushing for ghost and range records, allocation across full chunks and CIBs, backwards allocation, CoW of old CIBs and bitmaps, free-count accounting, free of already-free blocks, low-space transaction behavior, and statfs free-block reporting before write-mode spaceman initialization.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/spaceman.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/super.c -->
# File Research: sources/local-fs/linux-apfs-rw/super.c

## Purpose

`super.c` implements APFS filesystem registration, mount and unmount handling, shared container state, superblock/checkpoint discovery, volume superblock and omap/catalog setup, mount option parsing, feature checks, inode cache setup, statfs, sync/remount operations, and block-device management.

## Container And Volume State

The file maintains a global `nxs` list of mounted APFS containers protected by `nxs_mutex`. A single container info object can be shared by multiple mounted volumes or snapshots. The mutex protects container lookup, reference counts, volume lists, shared omap references, first-mount flag selection, and backup superblock update coordination.

Each mounted volume gets an `apfs_sb_info`, while the shared container uses `apfs_nxsb_info`. The volume superblock uses a fake anonymous device for stat identity but reports the actual block device in mount info.

## Superblock Discovery

`apfs_read_main_super()` first reads the backup container superblock at block zero to learn the real block size, then scans the checkpoint descriptor area for the newest valid APFS NX superblock by magic, xid, and checksum. It rejects non-contiguous checkpoint descriptor trees and applies an arbitrary descriptor loop bound.

After selecting the checkpoint, it copies the NX superblock into memory, records block size and xid, sets the transaction buffer limit from RAM size, checks container features, and validates fusion UUIDs when applicable.

`apfs_make_super_copy()` writes the current checkpoint superblock back to block zero on final writable unmount of the container.

## Volume Mapping

`apfs_map_volume_super()` resolves the requested volume number through the container omap. It CoWs the container omap when writing, reads the omap root, looks up the volume superblock block, and maps it with `apfs_map_volume_super_bno()`.

`apfs_read_omap()` maps the volume omap object and root node, updating on-disk oids when CoW moves objects during write transactions. `apfs_first_read_omap()` shares a single omap object across the live volume and its snapshots. `apfs_read_catalog()` reads the catalog root through the volume omap.

Snapshot mounting maps the live volume and omap first, then calls `apfs_switch_to_snapshot()` to replace the volume superblock with the snapshot superblock before reading the snapshot catalog.

## Mount Lifecycle

`apfs_mount()` or `apfs_get_tree()` parses options, forces snapshot mounts read-only, attaches or creates shared container state with `apfs_attach_nxi()`, uses `sget()`/`sget_fc()` to reuse existing matching volume/snapshot superblocks, reads the main container superblock, and calls `apfs_fill_super()` for new superblocks.

`apfs_fill_super()` sets up backing-dev info, applies container flags, maps the volume, checks volume features, initializes/shared omap, optionally switches to a snapshot, reads the catalog, sets VFS operations, loads private and root inodes, creates the root dentry, and schedules orphan cleanup on writable mounts.

`apfs_put_super()` cancels cleanup/commit work, starts a sync transaction on writable unmount, updates modified-by software info and unmount time, forces commit, updates the backup superblock copy, and releases catalog, omap, and volume-super resources.

`apfs_kill_sb()` temporarily switches `s_dev` to the anonymous device before `kill_anon_super()`, then frees APFS superblock info and shared container references.

## Options And Feature Checks

Supported mount options include `readwrite`, `cknodes`, `uid=`, `gid=`, `vol=`, `snap=`, and `tier2=`. The first mount of a container decides container-wide flags; later incompatible flag requests are ignored with a warning.

Write support is deliberately gated behind `readwrite` or `CONFIG_APFS_RW_ALWAYS`, with warnings that it is experimental. Snapshots are always mounted read-only. Remount support only turns a volume read-only.

Container feature checks reject unknown incompatible features, enforce fusion tier2 requirements, and block writable fusion mounts. Volume feature checks reject unsupported encryption/restore/PFK/secondary-root cases, restrict writes for dataless snapshots and sealed volumes, warn on encrypted or preallocated-extent features, and reject unknown read-only-compatible features for writable mounts.

## VFS Integration

The file defines `apfs_sops`, inode allocation/destruction via a slab cache, `apfs_write_inode()` transaction wrapping, `apfs_statfs()` using shared container block counts and volume object counts, `apfs_sync_fs()` forced transaction commit, and filesystem registration through `apfs_fs_type`.

Kernel-version compatibility branches cover block-device open APIs, fs_context APIs, owner checks elsewhere, BDI APIs, dentry operation setup, and inode cache allocation.

## Invariants And Risks

- Container state is shared and reference-counted across volumes and snapshots.
- `nx_big_sem` serializes APFS filesystem writes and protects mount-time reads from concurrent CoW.
- The first mount controls container-wide checksum/write flags.
- The selected checkpoint is the highest-xid valid descriptor superblock.
- Writable unmount must force a transaction commit before updating the backup superblock.
- Error handling is conservative: aborted transactions force the container read-only.
- Fusion support is partial, and writable fusion mounts are blocked.

## Test Focus

Test multi-volume and multi-snapshot mounts, duplicate mount reuse, read-only mismatch rejection, checkpoint scanning with corrupt/newer descriptors, option parsing on old and fs_context kernels, feature-mask rejection, snapshot read-only forcing, writable unmount commit, backup superblock update, shared omap reference cleanup, statfs before/after spaceman load, and block-device cleanup on mount failures.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/symlink.c -->
# File Research: sources/local-fs/linux-apfs-rw/symlink.c

## Purpose

`symlink.c` implements APFS symlink target resolution and defines inode operations for symlink inodes.

## Main Flow

`apfs_get_link()` takes the container read lock, rejects RCU/pathwalk calls without a dentry by returning `-ECHILD`, reads the symlink extended attribute size with `__apfs_xattr_get()`, allocates a target buffer, reads the target xattr, validates that it is non-empty and null-terminated, releases the APFS read lock, and returns the buffer with a delayed `kfree_link` cleanup.

The symlink target is stored in the `APFS_XATTR_NAME_SYMLINK` xattr rather than inline inode data.

## Inode Operations

`apfs_symlink_inode_operations` wires:

- `.get_link = apfs_get_link`
- `.getattr = apfs_getattr`
- `.listxattr = apfs_listxattr`
- `.update_time = apfs_update_time`
- `.readlink = generic_readlink` on kernels before 4.10

## Invariants And Risks

- Symlink targets must be null-terminated on disk.
- Empty targets are treated as corruption.
- The APFS container read lock protects xattr lookup and read.
- Allocation size comes from a first xattr size query, so races are constrained by the filesystem-wide lock.

## Test Focus

Test valid symlink reads, missing symlink xattr, empty or unterminated targets, allocation failure, RCU pathwalk fallback via `-ECHILD`, xattr listing, and timestamp updates on symlink inodes.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/transaction.c -->
# File Research: sources/local-fs/linux-apfs-rw/transaction.c

## Purpose

`transaction.c` implements APFS transaction lifecycle management. It reads checkpoint ephemeral objects, starts transactions under the container write lock, tracks dirty inodes and buffers, writes ephemeral objects and checkpoint maps, commits new checkpoints, schedules delayed commits, and aborts failed transactions by forcing the container read-only.

## Checkpoint And Ephemeral Objects

`apfs_read_ephemeral_objects()` allocates the in-memory ephemeral object list and reads checkpoint mapping blocks from the descriptor ring. Each mapping is loaded by `apfs_read_single_ephemeral_object()`, which supports objects up to two blocks, handles checkpoint data-ring wraparound, verifies checksums unconditionally, and records object data by oid.

`apfs_write_ephemeral_objects()` writes all in-memory ephemeral objects to the new checkpoint data ring, creates checkpoint mapping blocks in the descriptor ring, handles full mapping blocks, reserves the final descriptor slot for the new NX superblock, and updates checkpoint descriptor/data ring indexes and lengths.

`apfs_checkpoint_end()` writes the final NX superblock block after all other dirty data has been submitted, sets its xid and checksum, flushes the backing block device mapping before and after writing, and thereby commits the checkpoint.

## Transaction Start

`apfs_transaction_start()` takes `nx_big_sem` for write, rejects read-only containers, lazily reads ephemeral objects, increments the container xid for the first nested start, reads the spaceman, checks coarse free-space reservations by transaction kind, and CoWs/maps the volume superblock, volume omap, and catalog for write access.

If there is not enough reserved room, it forces a commit of existing work to flush queues and returns `-ENOSPC`.

## Commit Decision And Commit Work

`apfs_transaction_commit()` either commits immediately or schedules delayed commit work after 100 ms. Immediate commit is required when explicitly forced, transaction buffer/start thresholds are exceeded, free queues get large, internal-pool free queue pressure rises, or main free queue btree node limits are approached.

`apfs_trans_commit_work()` runs delayed forced commits under the container write lock. If it fails, it aborts the transaction.

## Commit Sequence

`apfs_transaction_commit_nx()` performs the actual checkpoint commit:

1. Flush all dirty inode metadata into buffers.
2. Flush the cached free-range record into the free queue.
3. Write dirty internal-pool bitmaps, which may modify the spaceman.
4. Write ephemeral objects and checkpoint mapping blocks.
5. Submit all transaction buffers, setting checksums for buffers marked `buffer_csum`.
6. Wait for writes and clear transaction buffer state.
7. Clean or free page-cache buffers for written non-metadata buffers.
8. End the checkpoint by writing the checksummed NX superblock.
9. Reset transaction start/buffer counters.

## Dirty Object Tracking

`apfs_inode_join_transaction()` holds an inode reference and links it into the transaction inode list. `apfs_transaction_flush_all_inodes()` repeatedly updates dirty inodes, clears raw dirty state, temporarily drops the APFS write lock around `iput()`, and detects aborts that occur during writeback.

`apfs_transaction_join()` attaches buffer heads to the transaction list, stores an `apfs_bh_info` in `b_private`, increments the buffer count, and marks `buffer_trans`.

## Abort And Read-Only Fallback

`apfs_transaction_abort()` clears transaction state, decrements the in-memory xid, clears and releases all tracked transaction buffers, forces every mounted volume in the container read-only, releases the write lock, and drops inode references from the transaction list.

The code does not attempt to undo all in-memory mutations from a failed transaction; instead, it prevents further writes to avoid committing inconsistent state.

## Invariants And Risks

- There is a single active transaction per container, guarded by `nx_big_sem`.
- Ephemeral objects are read once and rewritten with every committed transaction.
- The checkpoint superblock checksum is written last, so incomplete transactions should not become the selected checkpoint.
- Transaction buffer checksums can remain stale until commit.
- Dirty inode flushing must avoid recursive commit deadlocks.
- Abort is intentionally fail-closed and makes the container read-only.

## Test Focus

Test ephemeral object read/write with ring wraparound, checksum failures, transaction nesting, delayed commit scheduling/canceling, forced sync/unmount commits, free-space reservation behavior, dirty inode flush under concurrent eviction/writeback, buffer tracking cleanup, commit write error handling, and abort read-only enforcement across multiple mounted volumes.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/transaction.c -->