# Group Research: group_659_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_volumes_h_sources__de6179530334

Scope verified against `Docs/research_subset_a.md`: all listed files are within `sources/local-fs/kdave-linux`, which is included in subset A. Each source file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/volumes.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/volumes.h

## Role

`volumes.h` is the central Btrfs volume/device/chunk mapping interface. It defines the in-memory objects and public APIs used to manage multi-device filesystems, RAID profiles, chunk maps, device statistics, discard mappings, block-to-stripe translation, device replacement, balance, grow/shrink, and swapfile pinning.

## Main Definitions

- `BTRFS_STRIPE_LEN`, `BTRFS_STRIPE_LEN_SHIFT`, and related helpers define the 64 KiB stripe unit used throughout Btrfs chunk mapping.
- `enum btrfs_raid_types` maps on-disk block group profile bits to compact raid indexes. Compile-time assertions lock in expected profile ordering.
- `struct btrfs_device` represents a filesystem device, including block device handles, device id, sizes, usage counters, zoned-device metadata, device state bits, stats, sysfs kobjects, flush state, scrub state, allocation state, and per-profile temporary accounting.
- `struct btrfs_fs_devices` represents a set of devices belonging to one filesystem UUID/metadata UUID. It tracks open/missing/rw/total devices, seed devices, allocation lists, mount state, sysfs state, read policy, and per-profile available-space estimates.
- `struct btrfs_io_context` carries logical-to-physical mapping results for submitted I/O, including stripes, mirror selection, replace-target duplication, RAID56 full-stripe layout, and raid-stripe-tree ordering metadata.
- `struct btrfs_chunk_map` describes a logical chunk: logical start/length, stripe size, RAID type, stripe count, and per-stripe physical mappings.
- `struct btrfs_raid_attr` declares RAID profile properties: minimum/maximum device counts, copies/parity, tolerated failures, profile name, and block group flag.
- `struct btrfs_balance_control` and `struct btrfs_dev_lookup_args` support balance operations and device lookup by devid, uuid, fsid, devt, or missing-device state.

## Important Behavior

Device size fields `total_bytes`, `disk_total_bytes`, and `bytes_used` use generated accessors. On 32-bit SMP builds, seqcount protection avoids torn 64-bit reads; on 32-bit preemptible builds, preemption is disabled around access; on wider or non-preempt configurations direct access is used.

Device statistics helpers update individual stat atomics and `dev_stats_ccnt` with memory barriers so transaction-time stat flushing can observe consistent changes.

Mapping APIs declared here are the core bridge from logical filesystem addresses to device stripes:

- `btrfs_map_block`
- `btrfs_map_repair_block`
- `btrfs_map_discard`
- `btrfs_find_chunk_map`
- `btrfs_get_chunk_map`
- `btrfs_remove_chunk_map`

Volume management declarations cover scanning/opening/closing devices, adding/removing devices, resizing devices, balance/resume/recover/pause/cancel, chunk creation/removal, superblock reading, degradability checks, and per-profile availability.

## Interactions

This header is consumed by much of Btrfs: chunk allocation, bio submission, scrub, dev replace, balance, zoned support, sysfs, and ioctl paths. `zoned.h` depends directly on `struct btrfs_device`, `struct btrfs_fs_devices`, and chunk/stripe layout definitions from this file.

## Notable Constraints

- `BTRFS_MAX_DATA_CHUNK_SIZE` limits data chunks to 10 GiB.
- `BTRFS_MAX_DISCARD_CHUNK_SIZE` limits one discard request to 1 GiB.
- `BTRFS_RAID1_MAX_MIRRORS` is currently 4 and must stay synchronized with RAID attributes.
- `BTRFS_MAX_DEVS` and `BTRFS_MAX_DEVS_SYS_CHUNK` derive maximum stripe counts from item sizes.
- Device name access is RCU-protected and returns `"<missing disk>"` for missing devices.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/volumes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/xattr.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/xattr.c

## Role

`xattr.c` implements Btrfs extended attribute get/set/list operations and VFS xattr handlers for `security.*`, `trusted.*`, `user.*`, and `btrfs.*` property-backed attributes.

## Main Functions

- `btrfs_getxattr()` looks up a `BTRFS_XATTR_ITEM_KEY` dir item by inode and name, returns the stored data length for size probes, validates buffer size, then copies xattr data from the leaf.
- `btrfs_setxattr()` inserts, replaces, or deletes an xattr within an existing transaction. It enforces `BTRFS_MAX_XATTR_SIZE`, honors `XATTR_CREATE` and `XATTR_REPLACE`, and handles packed dir-item replacement atomically.
- `btrfs_setxattr_trans()` starts or reuses a transaction, calls `btrfs_setxattr()`, updates inode version/ctime, and persists the inode item.
- `btrfs_listxattr()` walks all xattr items for an inode and emits NUL-terminated names, or returns the required total size.
- Handler wrappers adapt Btrfs operations to Linux `xattr_handler` callbacks.
- `btrfs_initxattrs()` initializes security xattrs during inode creation under a supplied transaction.
- `btrfs_xattr_security_init()` delegates inode security initialization to LSM code with the Btrfs callback.

## Storage Model

Btrfs stores xattrs as dir items in the tree. A leaf item may pack multiple `struct btrfs_dir_item` entries. Each packed entry is laid out as:

`struct btrfs_dir_item` + xattr name + xattr data

Replacement must preserve atomic visibility. If the matched xattr is alone in the item, the item is extended or truncated in place. If other xattrs share the same item, the old dir-name entry is deleted and a new entry-sized region is added before writing the replacement value.

## Security and Properties

`security.capability` gets special negative-result caching through `BTRFS_INODE_NO_CAP_XATTR`, reducing repeated lookups for absent capability xattrs. Setting capability clears that cache bit.

`btrfs.*` xattrs are routed through property validation and `btrfs_set_prop()`, not generic xattr storage alone. Ignored properties are accepted as no-ops.

## Transaction and Locking Notes

`btrfs_setxattr_trans()` normally starts a two-unit transaction: one unit for xattr mutation and one for inode update. If already inside a transaction, it reuses `current->journal_info`; the documented case is SMACK security xattr setup during directory creation.

For `XATTR_REPLACE`, the code asserts the inode lock is held, first performs a read-only lookup, then releases the path before the insert/replace path.

## Side Effects

Successful set/delete operations set `BTRFS_INODE_COPY_EVERYTHING` and clear `BTRFS_INODE_NO_XATTRS`. Inode ctime and i_version are updated by the transaction wrapper and property path.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/xattr.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/xattr.h

## Role

`xattr.h` is the public header for Btrfs extended attribute support.

## Exports

It declares:

- `btrfs_xattr_handlers`
- `btrfs_getxattr()`
- `btrfs_setxattr()`
- `btrfs_setxattr_trans()`
- `btrfs_listxattr()`
- `btrfs_xattr_security_init()`

## Dependencies

The header uses forward declarations for VFS and Btrfs transaction types, keeping consumers from needing the full implementation headers unless they use the function bodies.

## Relationship

The declarations correspond directly to the implementation in `xattr.c` and are used by inode, VFS, security initialization, and property-related paths.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zlib.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/zlib.c

## Role

`zlib.c` implements Btrfs zlib compression and decompression using kernel zlib streams and Btrfs compressed-bio helpers.

## Workspace Management

`struct workspace` contains a `z_stream`, an auxiliary buffer, buffer size, list node, and compression level. Workspaces are allocated through Btrfs compression workspace infrastructure.

`zlib_alloc_workspace()` allocates zlib deflate/inflate workspace memory and a staging buffer. On s390 with zlib DFLTCC acceleration, `need_special_buffer()` may allocate a 4-page buffer to improve hardware compression performance unless the filesystem minimum folio size is already large enough.

`zlib_free_workspace()` releases stream workspace, buffer, and wrapper object.

## Compression Path

`zlib_compress_bio()` compresses a file range into the compressed bio:

- Initializes deflate at the requested level.
- Allocates compressed output folios.
- Feeds input from filemap folios directly, or via the special staging buffer for s390 acceleration.
- Calls `zlib_deflate()` with `Z_SYNC_FLUSH`, then finalizes with `Z_FINISH`.
- Adds full and partial compressed folios to the bio.
- Rejects compression if output grows beyond input or becomes too large for the original range.

Expansion detection returns `-E2BIG`, causing upper layers to store data uncompressed.

## Decompression Paths

`zlib_decompress_bio()` inflates compressed bio contents into page-cache targets using `btrfs_decompress_buf2page()`. It maps compressed input folios one at a time and refills zlib input as needed.

`zlib_decompress()` handles smaller direct decompression into a destination folio, intended for cases where input and output are bounded by one sector. It zero-fills the destination tail if decompression produces too little data and returns `-EIO`.

Both decompression paths detect zlib headers without preset dictionaries and can use negative window bits to skip the Adler-32 check.

## Error Handling

Initialization or stream errors are logged with root id, inode number, and offset. Compression failures return `-EIO`, allocation failures return `-ENOMEM`, and ineffective compression returns `-E2BIG`.

## Compression Levels

`btrfs_zlib_compress` exposes levels 1 through 9 with `BTRFS_ZLIB_DEFAULT_LEVEL`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zoned.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/zoned.c

## Role

`zoned.c` implements Btrfs zoned block device support. It handles zone discovery, zone caches, superblock log zones, allocation-pointer reconstruction, sequential-zone constraints, active-zone accounting, zone append integration, metadata write-pointer checks, data relocation reservations, zone finishing, zone reset/reclaim, and zoned statistics.

## Device Zone Discovery

`btrfs_get_dev_zone_info()` builds `struct btrfs_zoned_device_info` for each device when the filesystem has the zoned incompat flag. It supports both real zoned devices and regular devices under zoned emulation.

Key behavior:

- Real zoned devices use `bdev_zone_sectors()`.
- Non-zoned devices emulate conventional zones, with zone size derived from existing device extents if not already known.
- Zone sizes must be power-of-two, at least 4 MiB, at most 8 GiB, and consistent across devices.
- Bitmaps track sequential zones, empty zones, and active zones.
- Optional `zone_cache` stores reported `blk_zone` data for real zoned devices.
- Active-zone limits are checked against device limits or a default maximum.
- Superblock log zones are read and validated.

`btrfs_destroy_dev_zone_info()` frees bitmaps/cache. `btrfs_clone_dev_zone_info()` clones zone metadata for device replacement-related use while intentionally not cloning the cache.

## Zoned Mode Validation

`btrfs_check_zoned_mode()` rejects host-managed zoned devices unless the filesystem is zoned. In zoned mode it:

- Ensures all devices have equal zone size.
- Stacks queue limits from zoned block devices.
- Requires zone size alignment to `BTRFS_STRIPE_LEN`.
- Rejects mixed block groups.
- Sets `fs_info->zone_size`, `max_zone_append_size`, zoned chunk allocation policy, and maximum extent size.

`btrfs_check_mountopts_zoned()` rejects space cache v1 and `NODATACOW`, and disables async discard.

## Superblock Log Zones

Zoned devices use pairs of sequential zones for each superblock mirror. The code defines mirror locations at primary, 512 GiB, and 4 TiB offsets.

`sb_write_pointer()` interprets the two-zone log state machine, handling empty, in-use, full, and corrupted combinations. If both zones are full, it reads the final superblocks from both zones and chooses the older zone for the next write based on generation comparison.

`btrfs_sb_log_location_bdev()` and `btrfs_sb_log_location()` return read/write superblock locations. `btrfs_advance_sb_log()` updates cached superblock-zone state after writes and finishes full zones when needed. `btrfs_reset_sb_log_zones()` resets a superblock log zone pair.

## Allocation and Empty-Zone Handling

`btrfs_find_allocatable_zones()` finds an aligned, empty, superblock-free zone range inside a device hole. It avoids both zoned superblock log zones and regular superblock offsets.

`btrfs_reset_device_zone()` issues `REQ_OP_ZONE_RESET`, marks zones empty, and clears active-zone bits.

`btrfs_ensure_empty_zones()` validates or resets zones in a free region before allocation. Non-empty sequential zones in free space trigger a warning and reset.

## Block Group Write Pointer Loading

`btrfs_load_block_group_zone_info()` reconstructs block group allocation state at mount or block group creation. It maps the logical block group to physical stripes, loads per-stripe zone state, and computes:

- `alloc_offset`
- `zone_capacity`
- `meta_write_pointer`
- sequential-zone runtime flags
- active block group list membership

For conventional-only mappings, it calculates the allocation pointer from the highest extent in the extent tree.

RAID-specific helpers enforce zoned write-pointer consistency:

- SINGLE requires a recoverable write pointer.
- DUP requires both copies to have matching offsets and requires raid-stripe-tree for data DUP.
- RAID1/RAID1C3/RAID1C4 tolerate missing devices only in degraded mode but otherwise require matching write pointers.
- RAID0 and RAID10 reconstruct logical allocation progress from stripe-row positions and reject stripe disorder, multiple partial stripes, or excessive stripe gaps.
- RAID5/RAID6 are rejected as unsupported in zoned mode.

Data block groups with non-SINGLE profiles require raid-stripe-tree.

## Zone Append and Ordered Extents

`btrfs_use_zone_append()` enables `REQ_OP_ZONE_APPEND` only for zoned data writes in sequential-zone block groups. It excludes reads, metadata, and data relocation roots.

`btrfs_record_physical_zoned()` adjusts checksum logical positions based on the actual physical address assigned by zone append.

`btrfs_finish_ordered_zoned()` handles completion after zone append. If zone append caused non-contiguous physical placement, it splits ordered extents and rewrites extent maps so final disk bytenrs match the actual append results. For nodatasum I/O it frees dummy checksum structures after using them to track logical addresses.

## Metadata Write Pointer Control

`btrfs_check_meta_write_pointer()` ensures metadata extent buffers are written exactly at the block group metadata write pointer. It may activate a metadata/system block group, pivot away from a previously active metadata block group, finish the old group, or return:

- `0` when writing is allowed,
- `-EAGAIN` when a transaction commit should fill a hole,
- `-EBUSY` when writeback should bail out.

`check_bg_is_active()` contains the active metadata/system block group pivot logic and coordinates with `zoned_meta_io_lock`.

## Active Zone Accounting and Finishing

`btrfs_zone_activate()` marks a block group and its underlying zones active, respecting per-device `max_active_zones` and reserved active zones for metadata/system needs.

`do_zone_finish()` transitions an active block group to finished/full state. It can wait for reservations, ordered extents, and metadata writeback, marks allocation pointers at capacity, updates free space to zero, clears tree-log/data-relocation markers, issues `REQ_OP_ZONE_FINISH`, clears active zone bits, and removes the block group from the active list.

Public wrappers include:

- `btrfs_zone_finish()`
- `btrfs_zone_finish_endio()`
- `btrfs_schedule_zone_finish_bg()`
- `btrfs_zone_finish_one_bg()`
- `btrfs_zoned_activate_one_bg()`
- `btrfs_can_activate_zone()`

## Data Relocation and Reclaim

`btrfs_zoned_reserve_data_reloc_bg()` reserves a dedicated data relocation block group, preferring the second empty data block group or allocating a new one in the data relocation space-info subgroup.

`btrfs_zoned_release_data_reloc_bg()` clears the relocation runtime flag once all relocation extents are written.

`btrfs_zoned_should_reclaim()` compares used bytes against total bytes and the reclaim threshold.

`btrfs_reset_unused_block_groups()` resets fully unused, fully zone-unusable block groups in place, updating free-space and `bytes_zone_unusable` accounting without deleting/recreating the block group.

## Device Replace Support

`btrfs_sync_zone_write_pointer()` synchronizes a replacement target’s sequential-zone write pointer by reading source zone state and zero-filling the target from its current physical position to the source write pointer.

## Statistics

`btrfs_show_zoned_stats()` emits active block group counts, reclaimable/unused counts, reclaim need, data relocation/tree-log block group ids, and per-active-zone allocation/usage/reservation/unusable data.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zoned.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zoned.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/zoned.h

## Role

`zoned.h` declares Btrfs zoned-mode data structures, public zoned APIs, and inline fallbacks for kernels built without `CONFIG_BLK_DEV_ZONED`.

## Main Structure

`struct btrfs_zoned_device_info` stores per-device zoned metadata:

- zone size and shift
- number of zones
- maximum active zones
- reserved active zones
- atomic active-zones-left counter
- bitmaps for sequential, empty, and active zones
- optional zone cache
- cached superblock log zone descriptors

## Public Zoned API

When `CONFIG_BLK_DEV_ZONED` is enabled, the header declares APIs for:

- device zone info loading/destruction/cloning
- zoned mount validation and mount option validation
- superblock log location, advancement, and reset
- allocatable zone search and empty-zone enforcement
- block group zone info loading and unusable-space calculation
- zone append decisions and physical recording
- metadata write-pointer validation
- zeroout and dev-replace write-pointer sync
- zone activation, finish, and finish scheduling
- data relocation block group reservation/release
- zone cache freeing, reclaim decisions, active-zone reservation checks
- unused block group zone reset
- zoned stats display

It also exposes a test-only helper for loading block groups by RAID type.

## Non-Zoned Build Fallbacks

When `CONFIG_BLK_DEV_ZONED` is disabled, most functions become no-op or regular-device fallbacks. If a mounted filesystem is actually zoned, `btrfs_check_zoned_mode()` returns `-EOPNOTSUPP`. Zone append is disabled, zone activation always succeeds, and superblock locations use normal Btrfs offsets.

## Inline Helpers

The header provides small helpers to:

- Test whether a device position is sequential or empty.
- Set/clear empty-zone bits.
- Validate device zone type compatibility with filesystem zoned mode.
- Reject superblock locations inside sequential zones.
- Check whether a zone reset is aligned and valid.
- Lock/unlock zoned metadata I/O only in zoned mode.
- Clear tree-log block group tracking.
- Serialize zoned data relocation writes.
- Test whether a zoned block group is full.

## Relationship

`zoned.c` implements the enabled-mode functions declared here. Other Btrfs subsystems use this header to make zoned decisions while compiling cleanly on non-zoned configurations.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zoned.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zstd.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/zstd.c

## Role

`zstd.c` implements Btrfs zstd compression and decompression, including a custom workspace manager optimized for zstd’s level-dependent memory requirements.

## Compression Parameters

Btrfs caps zstd window log at 17, so maximum input window is 128 KiB. Supported levels are `-15` through `15`, with default level `3`. Negative levels are fast zstd modes.

`zstd_get_btrfs_parameters()` obtains zstd parameters and clamps the window log to the Btrfs maximum.

## Workspace Manager

`struct workspace` holds zstd stream memory, size, sector-sized staging buffer, requested level, actual allocated level, LRU metadata, stream buffers, and parameters.

`struct zstd_workspace_manager` maintains:

- spinlock
- global LRU list
- idle lists by clipped level
- bitmap of levels with idle workspaces
- wait queue
- reclaim timer

`zstd_calc_ws_mem_sizes()` precomputes monotonic workspace sizes so a workspace allocated for a higher level can safely serve lower levels.

`zstd_alloc_workspace_manager()` initializes the manager and attempts to preallocate a max-level workspace for forward progress. `zstd_free_workspace_manager()` drains idle workspaces, deletes the timer, and frees the manager.

`zstd_get_workspace()` first searches reusable idle workspaces at or above the requested level. If allocation fails, it waits for a workspace, relying on the protected max-level workspace for progress.

`zstd_put_workspace()` returns a workspace to the idle list, updates LRU state when appropriate, starts the reclaim timer, and wakes waiters when a max-level workspace is returned.

The reclaim timer frees idle workspaces unused for 307 seconds, except in-use workspaces and the protected forward-progress workspace.

## Compression Path

`zstd_compress_bio()` compresses a Btrfs file range into a compressed bio:

- Initializes a zstd compression stream with Btrfs-clamped parameters.
- Maps filemap folios as input.
- Allocates compressed output folios.
- Streams input through `zstd_compress_stream()`.
- Adds full output folios to the bio and finalizes with `zstd_end_stream()`.
- Rejects output that becomes larger than input or reaches the original input length.

Expansion or bio-add failure returns `-E2BIG`; zstd stream errors return `-EIO`.

## Decompression Paths

`zstd_decompress_bio()` initializes a zstd decompression stream, maps compressed bio folios one at a time, streams into the workspace buffer, and copies decompressed chunks to destination pages through `btrfs_decompress_buf2page()`.

`zstd_decompress()` handles direct decompression into one destination folio using the workspace buffer. If decompressed output is shorter than expected, it zero-fills the missing range and returns `-EIO`.

## Error Handling

Compression and decompression log root id, inode number, offset, level, and zstd error codes where available. Input folios are unmapped and released on all exit paths.

## Compression Levels

`btrfs_zstd_compress` publishes the Btrfs zstd level range and default level to the common compression layer.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/zstd.c -->