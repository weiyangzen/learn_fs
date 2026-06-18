# Group Research: group_720_linux_sources_os_linux_linux_fs_btrfs_volumes_h_sources_os_linux_lin_328b7d5e2f9e

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/linux/linux`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/volumes.h -->
# File Research: sources/os/linux/linux/fs/btrfs/volumes.h

## Purpose
Defines the core Btrfs multi-device, chunk mapping, RAID profile, device-statistics, balance, and physical I/O mapping interfaces. This header is the shared contract between chunk allocation/removal, device open/scan/replace/remove, logical-to-physical bio mapping, degraded mount checks, discard mapping, zoned-device support, and user-visible device statistics.

## Main Data Structures
- `struct btrfs_device`: per-device runtime state, including device identity, opened block device/file, zone info, size/usage counters, flush bio, scrub state, device error counters, sysfs kobject, allocation extent tree, and active state bits.
- `struct btrfs_fs_devices`: device set for a filesystem FSID, including device lists, seed devices, open/missing/rw device counts, metadata UUID, allocation/read policy, per-profile available-space cache, and sysfs objects.
- `struct btrfs_io_context`: logical I/O mapping result used during bio submission. It owns stripes, mirror number, replacement-stripe metadata, full-stripe logical address for RAID56, error accounting, and an original bio pointer.
- `struct btrfs_chunk_map`: in-memory logical chunk map with chunk start/length, profile flags, stripe geometry, and physical stripes.
- `struct btrfs_raid_attr`: static RAID profile metadata such as min/max devices, tolerated failures, copies/parity, increment, name, and block-group flag.
- `struct btrfs_swapfile_pin`: rb-tree entry used to pin devices or block groups that contain active swapfile extents.
- `struct btrfs_balance_control`: balance filters and progress for data/metadata/system relocation.

## Constants and Profile Mapping
- `BTRFS_STRIPE_LEN` is fixed at 64 KiB with compile-time checks.
- `BTRFS_MAX_DATA_CHUNK_SIZE` is 10 GiB.
- `BTRFS_MAX_DISCARD_CHUNK_SIZE` caps a single discard request at 1 GiB.
- `enum btrfs_raid_types` maps on-disk block-group profile bits to compact RAID indices; several `static_assert`s protect this ABI-sensitive conversion.
- `BTRFS_RAID1_MAX_MIRRORS` is 4, matching RAID1C4.
- `BTRFS_MAX_DEVS()` and `BTRFS_MAX_DEVS_SYS_CHUNK` derive the maximum stripes storable in chunk items.

## Device State and Statistics
Device state bits record writability, presence in filesystem metadata, missing/replacement-target state, flush state, read-ahead disablement, and whether the device item was found in the chunk tree.

On 32-bit SMP or preemptible configurations, generated accessors for `total_bytes`, `disk_total_bytes`, and `bytes_used` avoid torn 64-bit reads using seqcount or preemption disabling. Device stats are atomic counters with explicit memory ordering around the change counter so transaction-time persistence sees consistent updates.

## Mapping and I/O Interfaces
Key exported APIs:
- `btrfs_map_block()`: maps logical ranges for read/write/get-read-mirrors into physical stripes and optional `btrfs_io_context`.
- `btrfs_map_repair_block()`: maps a selected repair mirror.
- `btrfs_map_discard()`: maps logical discard to physical discard stripes.
- `btrfs_num_copies()`, `btrfs_full_stripe_len()`, `btrfs_calc_stripe_length()`, `btrfs_nr_parity_stripes()`: profile geometry helpers.
- `btrfs_get_bioc()` / `btrfs_put_bioc()`: lifetime management for I/O contexts.

`btrfs_op()` maps Linux bio operations to Btrfs map operations. Writes and zone appends become `BTRFS_MAP_WRITE`; reads become `BTRFS_MAP_READ`.

## Device and Chunk Lifecycle APIs
The header declares mount/device discovery and teardown:
- `btrfs_scan_one_device()`, `btrfs_open_devices()`, `btrfs_close_devices()`, `btrfs_forget_devices()`, `btrfs_free_extra_devids()`.
- `btrfs_alloc_device()`, `btrfs_find_device()`, `btrfs_find_device_by_devspec()`, device lookup-argument helpers, and remove/grow/shrink/init-new-device operations.
- `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_create_chunk()`, `btrfs_chunk_alloc_add_chunk_item()`, `btrfs_remove_chunk()`, and `btrfs_remove_dev_extents()`.

Chunk-map APIs provide rb-tree lookup and mutation:
- `btrfs_find_chunk_map()`
- `btrfs_find_chunk_map_nolock()`
- `btrfs_get_chunk_map()`
- `btrfs_remove_chunk_map()`
- `btrfs_mapping_tree_free()`

## Balance, Replacement, and Degraded Operation
Balance entry points include `btrfs_balance()`, async resume/recovery, pause, cancel, and `btrfs_relocate_chunk()`. Device replacement cleanup APIs handle source and target device teardown. Degraded-mode safety is exposed through `btrfs_check_rw_degradable()` and chunk writability through `btrfs_chunk_writeable()`.

## Zoned and Swapfile Integration
`volumes.h` includes cross-file hooks for zoned repair and allocation:
- `btrfs_repair_one_zone()`
- pending extent lookup helpers
- hole lookup in pending extents
- zone-aware device state through `struct btrfs_zoned_device_info *zone_info`

Swapfile pins protect devices or block groups from unsafe relocation/removal while swap is active.

## Concurrency Notes
- `uuid_mutex` protects global filesystem UUID/device-set handling and is asserted by holding-counter helpers.
- `device_list_mutex` protects the full device list.
- `chunk_mutex` protects allocation lists and committed device sizes.
- `per_profile_lock` protects per-profile available-space cache.
- Atomic stats and explicit memory barriers protect device-stat persistence.

## Risk and Testing Signals
Important test coverage should include:
- RAID profile bit-to-index stability.
- 32-bit-safe device size/stat accessors.
- Degraded read/write eligibility.
- Logical-to-physical mapping for mirrored, striped, replacement, and RAID56 profiles.
- Device replacement stripe duplication.
- Chunk map reference lifetime and rb-tree removal.
- Swapfile pin blocking of device/block-group operations.
- Zoned-device repair and pending-extent accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/volumes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/xattr.c -->
# File Research: sources/os/linux/linux/fs/btrfs/xattr.c

## Purpose
Implements Btrfs extended-attribute get, set, remove, list, VFS xattr handlers, Btrfs property xattr handling, and security-xattr initialization during inode creation.

Btrfs stores xattrs as `BTRFS_XATTR_ITEM_KEY` dir-item-style records under the inode objectid. A leaf item can contain one or more packed `struct btrfs_dir_item` entries.

## Main Operations
- `btrfs_getxattr()` looks up a named xattr, returns its length for zero-size probes, validates caller buffer size, and copies the value from the leaf after the packed name.
- `btrfs_setxattr()` inserts, replaces, or deletes one xattr inside an existing transaction.
- `btrfs_setxattr_trans()` starts or reuses a transaction, calls `btrfs_setxattr()`, updates inode ctime/version, and persists the inode item.
- `btrfs_listxattr()` scans all xattr items for an inode and returns NUL-terminated names or total required size.

## Set/Replace/Delete Semantics
`btrfs_setxattr()` enforces `BTRFS_MAX_XATTR_SIZE(root->fs_info)` for name plus value. A `NULL` value means removal; an empty non-NULL value means an empty xattr.

For `XATTR_REPLACE`, the code does a read-only lookup first so missing xattrs return `-ENODATA`. The comment relies on the VFS inode lock to prevent racing with concurrent xattr deletion.

Insertion uses `btrfs_insert_xattr_item()`. Existing packed items are handled through `-EOVERFLOW` or `-EEXIST`, then `btrfs_match_dir_item_name()` identifies the matching dir item.

Replacement is explicitly atomic from reader perspective:
- If this is the only xattr in the leaf item, the item is extended or truncated in place.
- If multiple xattrs share the item, the old name is deleted and the item is extended for the new entry.
- The value length and value bytes are then updated in the leaf.

Successful mutation marks `BTRFS_INODE_COPY_EVERYTHING` and clears `BTRFS_INODE_NO_XATTRS`.

## VFS Handler Integration
The file defines handlers for:
- `security.*`
- `trusted.*`
- `user.*`
- `btrfs.*` properties

`btrfs_xattr_handlers[]` exports these handlers to the inode operations layer.

Generic handler get/set paths prepend the full xattr prefix with `xattr_full_name()`. Set paths reject read-only roots with `-EROFS`.

Security handlers special-case `security.capability`:
- Missing capability xattr is cached with `BTRFS_INODE_NO_CAP_XATTR`.
- Setting capability clears that cached negative bit.

## Btrfs Property Handling
`btrfs_xattr_handler_set_prop()` validates a `btrfs.*` property through `btrfs_validate_prop()`, ignores properties rejected by `btrfs_ignore_prop()`, starts a transaction, applies `btrfs_set_prop()`, updates inode version/ctime, and persists the inode.

## Security Initialization
`btrfs_xattr_security_init()` calls `security_inode_init_security()` with `btrfs_initxattrs()`.

`btrfs_initxattrs()`:
- Runs under an existing transaction handle passed as `fs_private`.
- Enters a NOFS allocation context to avoid reclaim recursion while holding a transaction.
- Builds full `security.*` names for each LSM-provided xattr.
- Clears the negative capability-xattr cache when initializing `security.capability`.
- Inserts each xattr with `btrfs_setxattr()`.

## Error Handling and Edge Cases
- Missing xattr returns `-ENODATA`; oversized destination buffer returns `-ERANGE`.
- Allocation failures return `-ENOMEM`.
- Oversized xattr payloads return `-ENOSPC`.
- Transaction failures during inode update abort the transaction.
- `btrfs_listxattr()` supports size-query mode and stops with `-ERANGE` if the provided buffer is too small.

## Cross-File Links
Uses:
- `dir-item.c/.h` xattr lookup/insert/delete/matching helpers.
- `transaction.h` for transaction start/end.
- `props.h` for Btrfs property validation/application.
- `accessors.h` for leaf item access.
- `locking.h` for inode-lock assertions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/xattr.h -->
# File Research: sources/os/linux/linux/fs/btrfs/xattr.h

## Purpose
Declares the Btrfs xattr API implemented by `xattr.c` and exports the VFS xattr handler table.

## Public API
- `btrfs_xattr_handlers[]`: handler table for `security.*`, `trusted.*`, `user.*`, and `btrfs.*`.
- `btrfs_getxattr()`: read a named xattr or query its size.
- `btrfs_setxattr()`: set/remove an xattr inside an existing Btrfs transaction.
- `btrfs_setxattr_trans()`: transaction-wrapping set/remove entry point.
- `btrfs_listxattr()`: list all xattr names for a dentry.
- `btrfs_xattr_security_init()`: initialize security xattrs for a newly created inode.

## Integration
The header forward-declares VFS and Btrfs transaction types, keeping include dependencies light for inode, file, and security initialization code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zlib.c -->
# File Research: sources/os/linux/linux/fs/btrfs/zlib.c

## Purpose
Implements the Btrfs zlib compression backend: workspace allocation/freeing, compressed-bio creation, compressed-bio decompression, and single-sector inline decompression.

## Workspace Model
`struct workspace` contains:
- `z_stream strm`
- a zlib workspace allocation
- a scratch buffer
- requested compression level
- list linkage for the common compression workspace manager

`zlib_alloc_workspace()` allocates a zlib deflate/inflate workspace large enough for both directions. It also allocates a scratch buffer:
- normally `fs_info->sectorsize`
- `4 * PAGE_SIZE` when s390 DFLTCC hardware acceleration benefits from larger input buffers and the minimum folio size is too small

`zlib_get_workspace()` obtains a generic Btrfs compression workspace and records the requested level. `zlib_free_workspace()` frees zlib internals, scratch buffer, and wrapper.

## Compression Flow
`zlib_compress_bio()`:
- Initializes deflate with the workspace level.
- Allocates compressed-output folios with `btrfs_alloc_compr_folio()`.
- Reads filemap folios through `btrfs_compress_filemap_get_folio()`.
- Either maps folio input directly or copies input into the larger scratch buffer for s390 hardware acceleration.
- Deflates with `Z_SYNC_FLUSH`, then finishes with `Z_FINISH`.
- Adds full or partial output folios to the compressed bio.
- Returns `-E2BIG` if compression expands beyond input or cannot fit output into the target bio.
- Returns `-EIO` for zlib stream failures and `-ENOMEM` for allocation failures.

The compressor abandons work early if compressed output is already larger after more than two sectors of input or total output reaches input length.

## Decompression Flow
`zlib_decompress_bio()`:
- Maps compressed bio folios one by one.
- Detects plain deflate streams without preset dictionaries and skips zlib header/adler checking by using negative `wbits`.
- Inflates into the workspace buffer.
- Copies decompressed ranges into target pages via `btrfs_decompress_buf2page()`.
- Switches input folios when the current folio is exhausted.
- Logs and returns `-EIO` on invalid stream or incomplete decompression.

`zlib_decompress()` handles a small compressed buffer into one destination folio. It expects input/output to fit within sector-sized buffers, inflates once with `Z_FINISH`, copies exactly `destlen`, and zero-fills any short output before returning `-EIO`.

## Hardware-Specific Path
`need_special_buffer()` checks zlib DFLTCC support and Btrfs minimum folio size. `copy_data_into_buffer()` gathers filemap data into the workspace buffer so s390 hardware acceleration sees a larger contiguous input region.

## Exported Compression Levels
`btrfs_zlib_compress` advertises:
- min level: 1
- max level: 9
- default: `BTRFS_ZLIB_DEFAULT_LEVEL`

## Risk and Testing Signals
Coverage should include:
- Compression expansion fallback to uncompressed I/O.
- Direct folio input versus special-buffer input.
- Multi-folio compressed output.
- Header-skipping decompression path.
- Short or corrupt compressed streams zero-filling destination tails.
- Sector-size and larger-folio configurations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zoned.c -->
# File Research: sources/os/linux/linux/fs/btrfs/zoned.c

## Purpose
Implements Btrfs zoned block-device support. It discovers and validates zone geometry, manages superblock log zones, tracks empty and active zones, calculates block-group allocation pointers from device write pointers, enforces sequential metadata/data writes, supports zone append completion rewrites, reserves active zones for metadata/system/tree-log/data-relocation use, finishes or resets zones, and exposes zoned statistics.

## Zone Discovery and Validation
`btrfs_get_dev_zone_info_all_devices()` reads zone info for every opened device on zoned filesystems.

`btrfs_get_dev_zone_info()`:
- Allocates `struct btrfs_zoned_device_info`.
- Determines real zone size for zoned block devices or emulated zone size for regular devices.
- Rejects zone sizes outside 4 MiB to 8 GiB.
- Builds bitmaps for sequential zones, empty zones, and active zones.
- Optionally builds a zone cache for zoned devices.
- Reads zone reports in batches of `BTRFS_REPORT_NR_ZONES`.
- Tracks active-zone counts and enforces device active-zone limits.
- Validates superblock log zone pairs for each mirror.

Regular devices in a zoned filesystem are represented as emulated conventional zones by `emulate_report_zones()`.

`btrfs_check_zoned_mode()` verifies all devices use a common zone size, validates block queue limits, rejects mixed block groups, derives `max_zone_append_size`, sets `BTRFS_CHUNK_ALLOC_ZONED`, and validates zoned-incompatible mount options.

## Mount Options
`btrfs_check_mountopts_zoned()` rejects:
- space cache v1, because it is not COWed
- NODATACOW

It disables async discard for zoned mode.

## Superblock Log Zones
Zoned devices use two log zones per superblock mirror. Helpers:
- `sb_zone_number()` maps mirror index to zone number.
- `sb_write_pointer()` determines the current superblock write position from the two-zone state machine.
- `sb_log_location()` returns the read or write location and resets a full target zone before reuse.
- `btrfs_sb_log_location_bdev()` works before `btrfs_device` zone info is available.
- `btrfs_sb_log_location()` uses cached device zone info.
- `btrfs_advance_sb_log()` advances cached write pointers and finishes a full log zone.
- `btrfs_reset_sb_log_zones()` resets a mirror’s log-zone pair.

The state machine treats both zones empty as no superblock, both full as requiring generation comparison, and some partially used combinations as corruption.

## Allocatable Zone Selection and Empty-Zone Handling
`btrfs_find_allocatable_zones()` searches a physical hole for a zone-aligned region that:
- is empty when sequential
- does not overlap zoned superblock log zones
- does not overlap regular superblock bytenrs

`btrfs_ensure_empty_zones()` resets sequential zones in a free region when they are unexpectedly non-empty.

`btrfs_reset_device_zone()` issues `REQ_OP_ZONE_RESET`, marks zones empty, and clears active-zone accounting.

## Block-Group Write Pointer Loading
`btrfs_load_block_group_zone_info()` is the central block-group initialization hook. It:
- Requires block-group length to be zone-size aligned.
- Finds and stores the physical chunk map in `cache->physical_map`.
- Loads per-stripe `zone_info` with physical location, capacity, and allocation offset.
- Counts sequential versus conventional stripes.
- Calculates `last_alloc` from the extent tree for conventional zones.
- Dispatches to profile-specific reconstruction.
- Sets `BLOCK_GROUP_FLAG_SEQUENTIAL_ZONE` when any stripe is sequential.
- Sets `alloc_offset`, `zone_capacity`, `meta_write_pointer`, active-list membership, and active runtime flags.

Profile-specific loaders:
- `btrfs_load_block_group_single()`: uses the single zone write pointer.
- `btrfs_load_block_group_dup()`: requires matching offsets across DUP stripes; data DUP requires raid-stripe-tree.
- `btrfs_load_block_group_raid1()`: handles mirrored profiles, missing devices, conventional zones, degraded mode, and active-zone mismatches.
- `btrfs_load_block_group_raid0()`: reconstructs striped allocation offset from per-stripe write pointers and validates stripe ordering/partial stripes.
- `btrfs_load_block_group_raid10()`: combines mirrored sub-stripes and RAID0 rows, validating mirror offset agreement and stripe ordering.
- RAID5/RAID6 are rejected.

For broken mirrored write pointers, some profiles mark the block group unallocatable by moving `alloc_offset` to `zone_capacity`.

## Free-Space Accounting
`btrfs_calc_zone_unusable()` computes:
- bytes already passed by the allocation pointer but not used
- capacity lost because zone capacity can be smaller than zone length

It marks the free-space cache finished and stores remaining sequential free space in `free_space_ctl->free_space`.

## Zone Append Data Writes
`btrfs_use_zone_append()` enables `REQ_OP_ZONE_APPEND` only for data writes in sequential-zone block groups. It avoids metadata, reads, non-zoned filesystems, and data relocation roots.

`btrfs_record_physical_zoned()` adjusts ordered checksum logical addresses after the device returns the actual physical append location.

`btrfs_finish_ordered_zoned()` finalizes ordered extents after zone append:
- Ignores preallocated/data-relocation writes.
- Walks ordered checksum ranges to detect non-contiguous actual logical placement.
- Splits ordered extents when append placement is fragmented.
- Rewrites the ordered extent and extent map disk bytenr when the final logical differs.
- Frees dummy checksum entries for NODATASUM/no-data-csum cases.

## Metadata Write Pointer Enforcement
`btrfs_check_meta_write_pointer()` ensures metadata extent buffers are written at the current block-group metadata write pointer:
- Caches the current zoned block group in the write context.
- Allows writes exactly at `meta_write_pointer`.
- Activates metadata/system/tree-log block groups when active-zone tracking is enabled.
- Returns `-EAGAIN` for holes that transaction commit can fill.
- Returns `-EBUSY` when writeback should bail out.

`check_bg_is_active()` handles active metadata/system block-group pivoting, including waiting for prior extent-buffer writeback and finishing an old active block group.

## Active Zone Management
`btrfs_zone_activate()` activates all underlying zones for a block group, respecting per-device active-zone limits and reserved active zones. Activated block groups are linked into `fs_info->zone_active_bgs`.

`btrfs_can_activate_zone()` checks whether a future block-group allocation can activate enough zones for SINGLE or DUP profiles. Failure sets `BTRFS_FS_NEED_ZONE_FINISH`.

`btrfs_check_active_zone_reservation()` reserves active zones for metadata, tree-log, and system block groups, adjusting reservations for DUP profiles and already-active metadata/system groups.

## Zone Finishing
`do_zone_finish()` is the core finisher:
- Skips inactive groups.
- Refuses metadata finish if allocated metadata has not reached `meta_write_pointer`.
- Optionally marks the block group read-only and waits for reservations, ordered data, and metadata writeback.
- Clears active flags.
- Moves allocation pointers to capacity.
- Clears treelog/data-relocation tracking.
- Issues `REQ_OP_ZONE_FINISH` to sequential device zones.
- Releases active-zone accounting and list references.

Public finish paths:
- `btrfs_zone_finish()`
- `btrfs_zone_finish_endio()`
- `btrfs_schedule_zone_finish_bg()` and its workqueue function for metadata near zone end
- `btrfs_zone_finish_one_bg()` chooses an active data block group with least remaining space and finishes it
- `btrfs_zoned_activate_one_bg()` activates one metadata/system block group, optionally finishing a data group first

## Data Relocation Reservation
`btrfs_zoned_reserve_data_reloc_bg()` reserves a dedicated data relocation block group:
- Chooses the second empty data block group when possible.
- Migrates it to the data-relocation space-info subgroup.
- Allocates a new relocation block group if needed.
- Marks `fs_info->data_reloc_bg` and `BLOCK_GROUP_FLAG_ZONED_DATA_RELOC`.
- Activates the zone.

`btrfs_zoned_release_data_reloc_bg()` clears the relocation flag once the relocation write range reaches the block group allocation pointer.

## Zone Reset and Reclaim
`btrfs_reset_unused_block_groups()` resets fully zone-unusable unused block groups without deleting/recreating the block group. It chooses matching unused groups, resets each physical zone, restores `alloc_offset` to zero, updates `zone_unusable`, returns free space, and decrements `bytes_zone_unusable`.

`btrfs_zoned_should_reclaim()` compares device bytes used to total filesystem bytes and returns true once the configured reclaim threshold is reached.

`btrfs_free_zone_cache()` frees per-device cached zone reports after mount-time use.

## Device Replace Support
`btrfs_sync_zone_write_pointer()` synchronizes a replacement target’s write pointer by reading source-zone write pointer information and zero-filling the target gap. `read_zone_info()` maps logical addresses to mirrors and reads zone info from a working device, skipping missing/failing mirrors.

## Diagnostics
`btrfs_show_zoned_stats()` prints active block-group count, reclaimable/unused counts, reclaim need, data relocation/tree-log block-group IDs, and per-active-block-group write pointer, used, reserved, and unusable bytes.

## Concurrency and Locking
- `zone_active_bgs_lock` protects active block-group list membership.
- `block_group->lock` protects block-group runtime flags and allocation pointer fields.
- `zoned_meta_io_lock` serializes metadata/system active block-group pivoting.
- `dev_replace->rwsem` protects device-replace state while reading or finishing physical stripes.
- NOFS contexts wrap zone management/report operations that can be called inside filesystem allocation paths.

## Risk and Testing Signals
Important coverage:
- Superblock log two-zone state transitions and corruption cases.
- Mount-time reconstruction for SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10.
- Mixed conventional/sequential devices.
- Degraded mirrored mounts with missing devices.
- Active-zone exhaustion and zone-finishing recovery.
- Zone append ordered-extent splitting/rewrite.
- Metadata write pointer hole handling.
- Data relocation block-group reservation/release.
- Reset of fully zone-unusable unused block groups.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zoned.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zoned.h -->
# File Research: sources/os/linux/linux/fs/btrfs/zoned.h

## Purpose
Declares the public Btrfs zoned-mode API, `struct btrfs_zoned_device_info`, compile-time stubs for kernels without `CONFIG_BLK_DEV_ZONED`, and inline helpers for zone type/emptiness checks, active write locks, tree-log/data-relocation tracking, and full-block-group detection.

## Main Type
`struct btrfs_zoned_device_info` stores per-device zone metadata:
- `zone_size`, `zone_size_shift`, `nr_zones`
- active-zone limit and reserved active-zone count
- `active_zones_left`
- bitmaps for sequential zones, empty zones, and active zones
- optional cached zone reports
- cached superblock log-zone information for all mirrors

## Exported Zoned APIs
When `CONFIG_BLK_DEV_ZONED` is enabled, the header exports APIs for:
- Device zone-info discovery/destruction/cloning.
- Zoned-mode and mount-option validation.
- Superblock log location, advancement, and reset.
- Allocatable-zone search and empty-zone enforcement.
- Block-group zone-info loading and unusable-space accounting.
- Zone append selection and physical-location recording.
- Metadata write pointer checking.
- Zone zeroout, write-pointer sync for device replace, zone activation/finish.
- Active-zone reservation, reclaim, data relocation, unused block-group reset.
- Zoned statistics display.

A sanity-test-only hook exposes profile-specific block-group loading.

## Non-Zoned Build Stubs
Without `CONFIG_BLK_DEV_ZONED`, most functions become no-ops or conservative failures:
- Zoned mode check returns `-EOPNOTSUPP` if a zoned filesystem is detected.
- Zone append is disabled.
- Zone zeroout/write-pointer sync return `-EOPNOTSUPP`.
- Activation/finish are treated as successful no-ops.
- Reclaim/reset/stats helpers return neutral values.

## Inline Helpers
- `btrfs_dev_is_sequential()` tests whether a physical position is in a sequential zone.
- `btrfs_dev_is_empty_zone()` tests empty-zone bitmap state, treating non-zoned devices as empty.
- `btrfs_dev_set_zone_empty()` / `btrfs_dev_clear_zone_empty()` mutate empty-zone bitmap state.
- `btrfs_check_device_zone_type()` enforces device compatibility with zoned/non-zoned filesystems.
- `btrfs_check_super_location()` rejects superblocks in sequential zones unless the device is non-zoned.
- `btrfs_can_zone_reset()` checks sequential-zone and alignment requirements.
- `btrfs_zoned_meta_io_lock()` / `unlock()` serialize metadata I/O only in zoned mode.
- `btrfs_clear_treelog_bg()` clears the tracked tree-log block group if it matches.
- `btrfs_zoned_data_reloc_lock()` / `unlock()` serialize data relocation writes in zoned mode.
- `btrfs_zoned_bg_is_full()` tests `alloc_offset == zone_capacity`.

## Integration
This header depends on `volumes.h`, `disk-io.h`, `block-group.h`, and `btrfs_inode.h`, reflecting how zoned mode cuts across device geometry, block-group allocation, metadata writeback, and data relocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zoned.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zstd.c -->
# File Research: sources/os/linux/linux/fs/btrfs/zstd.c

## Purpose
Implements the Btrfs zstd compression backend, including level-aware workspace management, compressed-bio creation, compressed-bio decompression, and single-sector decompression.

## Compression Parameters
Btrfs caps zstd window size:
- `ZSTD_BTRFS_MAX_WINDOWLOG = 17`
- `ZSTD_BTRFS_MAX_INPUT = 128 KiB`

Supported levels:
- minimum: `-15`
- maximum: `15`
- default: `3`

`zstd_get_btrfs_parameters()` obtains zstd parameters for a level and input size, then caps `windowLog` to the Btrfs maximum.

## Workspace Model
`struct workspace` contains:
- zstd memory buffer and size
- sector-sized decompression/output scratch buffer
- actual workspace level and requested level
- LRU timestamps/list nodes
- zstd input/output buffers
- cached parameters

Unlike zlib/lzo, zstd uses `struct zstd_workspace_manager`, with:
- one idle list per memory level
- an `active_map` bitmap
- global LRU list
- wait queue
- reclaim timer

## Workspace Management
`zstd_calc_ws_mem_sizes()` precomputes monotonic workspace sizes. This allows a higher-level workspace to safely satisfy lower-level requests even if raw zstd sizes are not naturally monotonic.

`zstd_alloc_workspace_manager()` initializes the manager and tries to preallocate one max-level workspace to guarantee forward progress.

`zstd_get_workspace()`:
- normalizes level 0 to level 1
- first searches idle workspaces at the requested or higher memory level
- allocates a new workspace under NOFS context if none is available
- waits on the max-level workspace if allocation fails

`zstd_put_workspace()` returns a workspace to its level list, updates LRU state only when used at its own level, protects one max-level workspace from reclaim, and wakes waiters when max-level workspace returns.

`zstd_reclaim_timer_fn()` frees idle workspaces unused for `307 * HZ`, skipping workspaces still in use.

## Compression Flow
`zstd_compress_bio()`:
- Initializes a zstd compression stream with Btrfs-capped parameters.
- Maps filemap input folios.
- Allocates compressed output folios.
- Streams input through `zstd_compress_stream()`.
- Adds full output folios to the compressed bio.
- Ends the frame with `zstd_end_stream()`.
- Returns `-E2BIG` if output expansion is detected or output would reach input length.
- Returns `-EIO` for zstd errors and `-ENOMEM` for output-folio allocation failure.

The function tracks `tot_in` and `tot_out`, switches input folios as each is consumed, and unmaps/releases folios on exit.

## Decompression Flow
`zstd_decompress_bio()`:
- Initializes a zstd dstream with `ZSTD_BTRFS_MAX_INPUT`.
- Maps compressed bio folios sequentially.
- Decompresses into the workspace scratch buffer.
- Copies decompressed bytes into target pages through `btrfs_decompress_buf2page()`.
- Advances to the next compressed folio as needed.
- Stops successfully when target pages are filled or the frame ends.
- Returns `-EIO` on zstd error or unexpected input exhaustion.

`zstd_decompress()` handles inline/single-buffer decompression into one destination folio. It expects sector-bounded input/output, copies the decompressed bytes, and zero-fills the destination tail with `-EIO` if output is short.

## Exported Compression Levels
`btrfs_zstd_compress` advertises min/max/default levels for the generic compression layer.

## Concurrency and Memory Notes
- Workspace manager state is protected by a spinlock.
- Timer callback runs in softirq context.
- Workspace allocation is done under `memalloc_nofs_save()` from the get path.
- A max-level workspace is kept available as a forward-progress reserve.

## Risk and Testing Signals
Relevant coverage:
- Negative zstd levels and high positive levels.
- Reuse of higher-level workspaces for lower-level requests.
- Reclaim timer freeing idle workspaces but preserving forward progress.
- Compression expansion fallback.
- Multi-folio input and output.
- Corrupt or truncated compressed streams.
- Short inline decompression with zero-filled destination tail.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/zstd.c -->