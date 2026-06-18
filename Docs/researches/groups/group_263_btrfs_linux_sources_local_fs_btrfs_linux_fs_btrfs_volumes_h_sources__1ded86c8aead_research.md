# Group Research: group_263_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_volumes_h_sources__1ded86c8aead

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/volumes.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/volumes.h

This header defines the main public data structures, constants, inline helpers, and declarations for Btrfs multi-device volume management, chunk mapping, RAID geometry, device lookup, device statistics, balance/device operations, and logical-to-physical I/O mapping.

Core constants and RAID definitions:
- `BTRFS_MAX_DATA_CHUNK_SIZE` caps a data chunk at 10 GiB.
- `BTRFS_MAX_DISCARD_CHUNK_SIZE` limits one discard request to 1 GiB.
- `BTRFS_STRIPE_LEN`, `BTRFS_STRIPE_LEN_SHIFT`, and `BTRFS_STRIPE_LEN_MASK` define the 64 KiB Btrfs stripe unit used by chunk mapping, RAID56, and zoned allocation logic.
- `enum btrfs_raid_types` maps on-disk block-group profile bits to internal RAID indexes. Compile-time assertions enforce stable indexes for RAID0, RAID1, DUP, RAID10, RAID5, RAID6, RAID1C3, and RAID1C4.
- `struct btrfs_raid_attr` describes per-profile RAID constraints: minimum/maximum devices, tolerated failures, copies, parity stripes, device increment, and block-group flag.

Main structures:
- `struct btrfs_device` represents one member device. It tracks membership lists, owning `btrfs_fs_devices`, opened block device/file, optional zoned info, state bits, device id, sizes, bytes used, I/O alignment, superblock write errors, flush bio, scrub context, device stats, sysfs kobjects, allocation extent state, and temporary per-profile allocation accounting.
- `struct btrfs_fs_devices` represents the device set for one filesystem UUID. It stores `fsid`, `metadata_uuid`, device counts, opened/missing/rw totals, seed devices, device/allocation lists, sysfs state, mount/open hold counts, feature booleans, chunk allocation policy, mirrored-read policy, and per-profile available-space estimates.
- `struct btrfs_io_stripe` is one mapped physical stripe: target device, physical offset, raid-stripe-tree search flag, and backpointer to its `btrfs_io_context`.
- `struct btrfs_io_context` is the logical-to-physical mapping result used during bio submission. It carries refcounting, map type, original bio, error accounting, logical range, stripe count, selected mirror, device-replace duplication metadata, RAID56 full-stripe logical address, and variable `stripes[]`.
- `struct btrfs_chunk_map` is the in-memory mapping tree node for one logical chunk, with start, length, stripe size, profile type, alignment, stripe count, sub-stripes, verification counter, rb-tree node, refcount, and variable stripe array.
- `struct btrfs_swapfile_pin` records a device or block group pinned by an active swapfile, sorted by pointer and inode to block unsafe operations.
- `struct btrfs_balance_control` stores ioctl balance filters and progress.
- `struct btrfs_dev_lookup_args` centralizes device lookup by devid, uuid, fsid, devt, or missing-device flag.

Important inline helpers:
- `BTRFS_DEVICE_GETSET_FUNCS()` generates accessors for `total_bytes`, `disk_total_bytes`, and `bytes_used`. On 32-bit SMP it uses a seqcount to avoid torn 64-bit reads; on 32-bit preempt kernels it disables preemption; otherwise it reads/writes directly.
- `btrfs_free_chunk_map()` frees a chunk map only after its refcount reaches zero and asserts the rb-node has been removed.
- `btrfs_op()` converts a bio operation into `BTRFS_MAP_READ` or `BTRFS_MAP_WRITE`, treating zone append as write.
- `btrfs_chunk_item_size()` computes the on-disk chunk item size for a stripe count.
- `btrfs_stripe_nr_to_offset()` safely converts a 32-bit stripe number to a 64-bit byte offset.
- Device stat helpers increment, read, reset, and set per-device stats while updating `dev_stats_ccnt` with required memory ordering.
- `btrfs_dev_name()` returns the RCU device name or `"<missing disk>"`.
- `btrfs_fs_devices_inc_holding()` and `btrfs_fs_devices_dec_holding()` require `uuid_mutex` and protect mount-time references before devices are opened.
- `btrfs_get_per_profile_avail()` reads cached per-profile available-space estimates under `per_profile_lock`.

Declared API surface:
- Mapping and bio context: `btrfs_map_block()`, `btrfs_map_repair_block()`, `btrfs_map_discard()`, `btrfs_get_bioc()`, `btrfs_put_bioc()`.
- Chunk tree and mapping tree: `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_create_chunk()`, `btrfs_mapping_tree_free()`, `btrfs_find_chunk_map()`, `btrfs_get_chunk_map()`, `btrfs_remove_chunk_map()`, `btrfs_chunk_alloc_add_chunk_item()`, `btrfs_remove_chunk()`, `btrfs_remove_dev_extents()`.
- Device lifecycle: `btrfs_open_devices()`, `btrfs_close_devices()`, `btrfs_scan_one_device()`, `btrfs_forget_devices()`, `btrfs_alloc_device()`, `btrfs_init_new_device()`, `btrfs_rm_device()`, `btrfs_grow_device()`, `btrfs_shrink_device()`, `btrfs_update_device()`.
- Device lookup and identity: `btrfs_find_device()`, `btrfs_find_device_by_devspec()`, `btrfs_get_dev_args_from_path()`, `btrfs_put_dev_args_from_path()`, `btrfs_sb_fsid_ptr()`.
- Balance and relocation: `btrfs_balance()`, `btrfs_resume_balance_async()`, `btrfs_recover_balance()`, `btrfs_pause_balance()`, `btrfs_cancel_balance()`, `btrfs_relocate_chunk()`.
- Device replace helpers: `btrfs_rm_dev_replace_remove_srcdev()`, `btrfs_rm_dev_replace_free_srcdev()`, `btrfs_destroy_dev_replace_tgtdev()`.
- Geometry/profile helpers: `btrfs_full_stripe_len()`, `btrfs_calc_stripe_length()`, `btrfs_nr_parity_stripes()`, `btrfs_bg_flags_to_raid_index()`, `btrfs_bg_type_to_factor()`, `btrfs_bg_type_to_raid_name()`, `btrfs_describe_block_groups()`.
- Verification and repair: `btrfs_verify_dev_extents()`, `btrfs_verify_dev_items()`, `btrfs_check_rw_degradable()`, `btrfs_repair_one_zone()`, `btrfs_scratch_superblocks()`.
- Swapfile/pending extents: `btrfs_pinned_by_swapfile()`, `btrfs_first_pending_extent()`, `btrfs_find_hole_in_pending_extents()`.

Cross-file relationships:
- Implemented mainly by `volumes.c`, with device replace, zoned mode, RAID56, scrub, balance, chunk allocation, disk I/O, sysfs, and transaction code consuming these types.
- `raid56.c` depends on `struct btrfs_io_context`, `BTRFS_STRIPE_LEN`, and RAID profile geometry.
- `zoned.c` depends on `struct btrfs_device`, `struct btrfs_fs_devices`, `struct btrfs_chunk_map`, and stripe geometry for zone allocation and write-pointer recovery.
- `bio.c` and lower I/O submission code consume `btrfs_map_block()` results and `btrfs_io_context`.
- Device stats are exported through ioctl/sysfs-facing paths and persisted by transaction commit helpers.

Important invariants and risks:
- RAID enum indexes are coupled to on-disk block-group profile bits and guarded by static assertions; changing profile bits would break mapping.
- Device size fields need generated accessors outside their natural locking contexts on 32-bit platforms.
- `btrfs_io_context::num_stripes` includes device-replace duplicated stripes, so callers must distinguish real stripes from replacement stripes with `replace_nr_stripes`.
- RAID56 `full_stripe_logical` implies a specific stripe ordering: data stripes first, then P, then Q for RAID6.
- `btrfs_chunk_map` objects must be removed from the rb-tree before the final put.
- Device-stat counter updates rely on memory barriers paired with `btrfs_run_dev_stats()`.
- `fs_devices->holding` is protected by `uuid_mutex`; mount code must not manipulate it locklessly.
- Per-profile available-space estimates can be stale or unavailable and use `U64_MAX` as the sentinel.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/volumes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/xattr.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/xattr.c

This file implements Btrfs extended-attribute get, set, remove, list, VFS xattr handler dispatch, Btrfs property xattrs, and security xattr initialization.

Main exported functions:
- `btrfs_getxattr()` looks up a `BTRFS_XATTR_ITEM_KEY` dir item by inode objectid and full xattr name. It returns the value length for size queries, `-ERANGE` when the caller buffer is too small, copies the value from the leaf item when possible, and returns `-ENODATA` for missing xattrs.
- `btrfs_setxattr()` mutates an xattr inside an existing transaction. It enforces `BTRFS_MAX_XATTR_SIZE()`, handles removal when `value == NULL`, supports `XATTR_CREATE` and `XATTR_REPLACE`, inserts new dir items, and atomically replaces packed dir-item values.
- `btrfs_setxattr_trans()` wraps `btrfs_setxattr()` in a transaction when the caller does not already have one, reserves units for xattr and inode updates, updates inode ctime and i_version, writes the inode item, and aborts the transaction on update failure.
- `btrfs_listxattr()` walks all `BTRFS_XATTR_ITEM_KEY` items for an inode, iterates packed `struct btrfs_dir_item` entries inside each item, and either reports total list size or copies nul-terminated names into the caller buffer.
- `btrfs_xattr_security_init()` calls `security_inode_init_security()` with `btrfs_initxattrs()` to install initial LSM-provided security attributes during inode creation.

Mutation behavior:
- Removal uses `btrfs_lookup_xattr()` and `btrfs_delete_one_dir_name()`.
- Replace first performs a read-only lookup to ensure existence, relying on VFS inode locking to avoid racing with deletion.
- Insert uses `btrfs_insert_xattr_item()`.
- `-EOVERFLOW` from insertion means an existing leaf item could not be expanded by split logic; the code checks whether the target name exists and either replaces or returns `-ENOSPC`.
- `-EEXIST` means a matching xattr exists in the packed item and should be replaced unless `XATTR_CREATE` was requested.
- Replacement preserves atomic visibility: readers should see either the old or new value, not a transient missing value. If the xattr is alone in the item, the item is extended or truncated in place; if multiple xattrs are packed together, the old entry is deleted and a new entry is appended.

VFS xattr handlers:
- `btrfs_security_xattr_handler` handles `security.*` xattrs with capability-specific caching.
- `btrfs_trusted_xattr_handler` handles `trusted.*`.
- `btrfs_user_xattr_handler` handles `user.*`.
- `btrfs_btrfs_xattr_handler` handles `btrfs.*` property xattrs by validating and setting properties through `props.c`.
- `btrfs_xattr_handlers[]` exposes the handler array to the superblock/inode setup code.

Security/capability cache:
- `btrfs_xattr_handler_get_security()` caches missing `security.capability` by setting `BTRFS_INODE_NO_CAP_XATTR` after `-ENODATA`.
- `btrfs_xattr_handler_set_security()` clears `BTRFS_INODE_NO_CAP_XATTR` before changing `security.capability`.
- `btrfs_initxattrs()` also clears the capability-missing bit when initializing `security.capability`.

Property xattrs:
- `btrfs_xattr_handler_set_prop()` expands the handler/name pair to a full name, validates it with `btrfs_validate_prop()`, ignores properties that `btrfs_ignore_prop()` says should be ignored, starts a transaction, calls `btrfs_set_prop()`, and updates inode ctime/i_version plus the inode item.

Cross-file relationships:
- Uses `dir-item.c` helpers for xattr lookup, insertion, deletion, name matching, and leaf item packing.
- Uses `transaction.c` for start/end/abort transaction handling.
- Uses `props.c` for `btrfs.*` property validation and persistence.
- Uses inode runtime flags from `btrfs_inode.h`.
- Exposes declarations through `xattr.h`.
- Called through VFS xattr handler hooks registered by Btrfs inode/superblock operations.

Important invariants and risks:
- `btrfs_setxattr()` requires a valid transaction handle and asserts it.
- Xattr names stored here are full names including prefixes such as `security.`, `trusted.`, `user.`, or `btrfs.`.
- The total name plus value size must fit inside `BTRFS_MAX_XATTR_SIZE()`.
- Replace semantics are intentionally atomic for ACL and security correctness.
- On successful xattr mutation, `BTRFS_INODE_COPY_EVERYTHING` is set and `BTRFS_INODE_NO_XATTRS` is cleared.
- Root readonly checks happen in handler-level set paths before starting normal xattr/property transactions.
- `btrfs_setxattr_trans()` can reuse `current->journal_info` for nested security xattr initialization, notably Smack transmute xattrs during directory creation.
- `btrfs_initxattrs()` enters a NOFS allocation context while holding a transaction to reduce reclaim deadlock risk.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/xattr.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/xattr.h

This header exposes Btrfs xattr operations and the VFS handler table.

Declared API:
- `btrfs_xattr_handlers[]` is the null-terminated array of VFS xattr handlers for `security.*`, `trusted.*`, `user.*`, and `btrfs.*`.
- `btrfs_getxattr()` reads one full-name xattr.
- `btrfs_setxattr()` sets, replaces, creates, or removes one full-name xattr using an existing Btrfs transaction.
- `btrfs_setxattr_trans()` performs the same operation while starting or reusing a transaction.
- `btrfs_listxattr()` lists all xattr names for a dentry.
- `btrfs_xattr_security_init()` initializes LSM security xattrs for a new inode inside an existing transaction.

Cross-file relationships:
- Implemented by `xattr.c`.
- Used by inode creation paths, VFS xattr operations, ACL/security initialization, and property xattr handling.
- Depends only on forward declarations for `dentry`, `inode`, `qstr`, `xattr_handler`, and `btrfs_trans_handle`.

Important invariants:
- Callers of `btrfs_setxattr()` must already hold a transaction handle.
- Names passed to the lower-level get/set helpers are full xattr names, not suffix-only handler names.
- Security initialization expects the caller to supply a transaction handle via `fs_private`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zlib.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zlib.c

This file implements the Btrfs zlib compression backend: workspace allocation, workspace cleanup, whole-compressed-extent bio compression, bio decompression, inline/single-sector decompression, and supported compression-level metadata.

Workspace model:
- `struct workspace` wraps a kernel `z_stream`, allocated zlib workspace memory, a staging buffer, buffer size, list node, and current compression level.
- `zlib_get_workspace()` obtains a generic Btrfs compression workspace for the requested level and stores that level in the zlib workspace.
- `zlib_alloc_workspace()` allocates the wrapper, zlib deflate/inflate workspace memory, and a staging buffer.
- `zlib_free_workspace()` frees the zlib workspace, staging buffer, and wrapper.
- On s390 with zlib hardware acceleration, `need_special_buffer()` requests a 4-page staging buffer unless Btrfs minimum folio size is already large enough.

Compression path:
- `zlib_compress_bio()` initializes deflate with the selected level, streams filemap folio contents through zlib, allocates compressed output folios, adds output folios to `compressed_bio`, and rejects compression that grows the data.
- It uses `btrfs_compress_filemap_get_folio()` and `btrfs_calc_input_length()` for filemap input.
- Normal input mode maps file folios directly with `kmap_local_folio()`.
- s390 hardware mode uses `copy_data_into_buffer()` to copy enough file data into the larger workspace buffer before calling zlib.
- It aborts with `-E2BIG` when output exceeds input length or early output is already larger than useful.
- It returns `-ENOMEM` on compressed folio allocation failure and `-EIO` on zlib initialization or stream errors.

Bio decompression:
- `zlib_decompress_bio()` maps compressed bio folios one at a time, initializes inflate, optionally skips the zlib header/adler32 check for raw deflate when safe, inflates into the workspace buffer, and copies decompressed bytes into target pages through `btrfs_decompress_buf2page()`.
- It advances compressed input with `bio_next_folio()` and validates expected folio sizing against `btrfs_min_folio_size()`.
- It logs and returns `-EIO` if the stream does not end cleanly.

Inline/single-buffer decompression:
- `zlib_decompress()` inflates from a provided memory buffer into one destination folio at `dest_pgoff`.
- It expects input and output to fit within one sector-sized workspace buffer.
- It zero-fills any trailing destination range if decompression produced fewer bytes than expected and returns `-EIO`.

Compression levels:
- `btrfs_zlib_compress` advertises min level `1`, max level `9`, and Btrfs default zlib level.

Cross-file relationships:
- Registered through the compression backend table declared in `compression.h`.
- Uses `compressed_bio`, compressed folio allocation/freeing, and decompression copy helpers from Btrfs compression code.
- Uses `fs_info->sectorsize` and `btrfs_min_folio_size()` for staging and output sizing.
- Uses inode/root identifiers only for diagnostics.

Important invariants and risks:
- Output folios added to the bio must exactly account for `workspace->strm.total_out`.
- The backend deliberately rejects compressed output that is not smaller than input.
- All `kmap_local_folio()` mappings must be released before return, including error paths.
- The s390 hardware path depends on the staging buffer being large enough for hardware-efficient deflate.
- `zlib_deflateEnd()` and `zlib_inflateEnd()` must be called after successful stream initialization.
- Short decompression is treated as corruption and zero-fills the missing destination bytes.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zoned.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zoned.c

This file implements Btrfs zoned-mode support: device zone discovery, emulated zones for regular devices in zoned filesystems, superblock log-zone placement, active-zone accounting, block-group write-pointer recovery, sequential allocation state, zone append handling, metadata write-pointer enforcement, device-replace write-pointer synchronization, zone finishing, zoned data relocation block groups, reclaim decisions, unused block-group zone reset, and zoned statistics.

Major constants:
- `BTRFS_REPORT_NR_ZONES` limits one zone-report batch to 4096 zones.
- `WP_MISSING_DEV` and `WP_CONVENTIONAL` are pseudo write-pointer values for missing devices and conventional zones.
- Superblock log zones are anchored at 0, 512 GiB, and 4 TiB, each using two zones.
- `BTRFS_DEFAULT_MAX_ACTIVE_ZONES` supplies a default when devices expose no active-zone limit.
- `BTRFS_MIN_ACTIVE_ZONES` reserves enough active zones for superblock mirrors, system, metadata, data, tree-log, and relocation use.
- Supported zone sizes are constrained between 4 MiB and 8 GiB.

Device zone discovery:
- `btrfs_get_dev_zone_info_all_devices()` loads zone info for all open devices during mount when the incompat `ZONED` flag is present.
- `btrfs_get_dev_zone_info()` allocates `struct btrfs_zoned_device_info`, determines zone size, validates supported range, computes zone count, allocates sequential/empty/active bitmaps, optionally allocates a zone cache, reports zones, tracks active zones, validates superblock log zones, and stores max-active-zone state.
- Non-zoned devices in zoned filesystems are supported through `emulate_report_zones()`, which presents regular devices as conventional zones of the filesystem zone size.
- `calculate_emulated_zone_size()` derives emulated zone size from the first device extent when needed.
- `btrfs_get_dev_zones()` wraps cached reporting for real zoned devices and emulated reporting for regular devices.
- `btrfs_destroy_dev_zone_info()` frees bitmaps, zone cache, and the zone-info object.
- `btrfs_clone_dev_zone_info()` clones bitmap state for a replacement/clone device but intentionally drops the zone cache.

Zoned mode validation:
- `btrfs_check_zoned_mode()` rejects host-managed zoned devices when the filesystem is not zoned, enforces equal zone sizes across devices, stacks queue limits from zoned devices, checks zone-size stripe alignment, rejects mixed block groups, computes `max_zone_append_size`, switches chunk allocation policy to `BTRFS_CHUNK_ALLOC_ZONED`, bounds max extent size, and validates mount options.
- `btrfs_check_mountopts_zoned()` rejects space cache v1 and `NODATACOW`, and disables async discard for zoned mode.

Superblock log handling:
- `sb_write_pointer()` interprets the two-zone superblock log state machine, handles empty/full/in-use combinations, compares generations when both log zones are full, and detects corrupted states.
- `btrfs_sb_log_location_bdev()` computes the read/write superblock location directly from a block device, used before full Btrfs device state exists.
- `btrfs_sb_log_location()` does the same from a `btrfs_device`, using regular superblock offsets for zoned filesystems on non-zoned devices.
- `btrfs_advance_sb_log()` advances cached superblock log-zone state after a write and finishes a full log zone when necessary.
- `btrfs_reset_sb_log_zones()` resets both log zones for a mirror.

Zone allocation and reset helpers:
- `btrfs_find_allocatable_zones()` scans a device hole for an aligned region whose sequential zones are empty and that does not overlap zoned or regular superblock locations.
- `btrfs_reset_device_zone()` issues `REQ_OP_ZONE_RESET`, marks each reset zone empty, and clears active-zone accounting.
- `btrfs_ensure_empty_zones()` validates or resets a free range before allocating it.
- `btrfs_zoned_issue_zeroout()` issues zeroout only for sequential zones.

Block-group write-pointer loading:
- `btrfs_load_block_group_zone_info()` is the central mount/new-block-group loader. It verifies zone alignment, finds and stores the physical chunk map, loads per-stripe zone state, detects conventional versus sequential stripes, reconstructs allocation offsets by RAID profile, initializes `meta_write_pointer`, and inserts active groups into `fs_info->zone_active_bgs`.
- `btrfs_load_zone_info()` loads one physical stripe’s zone info, handles missing devices, conventional zones, new block groups, device replace, offline/readonly/full/empty/partial zones, and active-zone bits.
- `calculate_alloc_pointer()` derives the allocation pointer for conventional-zone block groups from the highest-addressed extent item.
- `btrfs_load_block_group_by_raid_type()` dispatches profile-specific recovery for SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10. RAID5/6 are rejected.
- `btrfs_load_block_group_single()` accepts one recovered write pointer.
- `btrfs_load_block_group_dup()` requires matching offsets across two stripes, normalizes conventional zones to `last_alloc`, requires raid-stripe-tree for data DUP, and activates zones if only one side is active.
- `btrfs_load_block_group_raid1()` tolerates missing devices only in degraded mode, normalizes conventional zones, verifies matching write pointers for non-degraded mounts, and requires raid-stripe-tree for data mirrored profiles.
- `btrfs_load_block_group_raid0()` reconstructs logical allocation from per-device stripe positions, verifies stripe ordering, forbids multiple partial stripes, checks row gaps, and requires raid-stripe-tree for data RAID0.
- `btrfs_load_block_group_raid10()` applies RAID0-style reconstruction to mirrored stripe groups and verifies mirrored write-pointer consistency.

Zone accounting and active-zone limits:
- `btrfs_dev_set_active_zone()` and `btrfs_dev_clear_active_zone()` maintain per-device active-zone bitmaps and `active_zones_left`.
- `btrfs_zone_activate()` activates all underlying device zones for a block group, honors reserved active zones for metadata/system needs, adds the block group to `zone_active_bgs`, and sets `BLOCK_GROUP_FLAG_ZONE_IS_ACTIVE`.
- `btrfs_can_activate_zone()` checks whether an allocation profile can obtain enough active zones and sets `BTRFS_FS_NEED_ZONE_FINISH` when not.
- `btrfs_check_active_zone_reservation()` reserves active-zone capacity for metadata, tree-log, and system block groups, then subtracts reservations already consumed by active metadata/system groups.
- `btrfs_zoned_activate_one_bg()` tries to activate an inactive metadata/system block group and can optionally finish another active data group to free active-zone budget.
- `btrfs_zone_finish_one_bg()` selects the active data block group with the least remaining capacity and finishes it.

Sequential allocation and unusable space:
- `btrfs_calc_zone_unusable()` computes unusable space as already-advanced write-pointer bytes beyond used bytes plus capacity lost at the tail of the block group.
- It marks the free-space cache finished and sets `free_space_ctl->free_space` to bytes from current allocation offset to zone capacity.

Data zone append and ordered extent repair:
- `btrfs_use_zone_append()` uses zone append only for zoned data writes to sequential-zone block groups, excluding reads, metadata, and data relocation.
- `btrfs_record_physical_zoned()` adjusts ordered checksum logical addresses after zone append reports the actual physical write location.
- `btrfs_finish_ordered_zoned()` rewrites or splits ordered extents when zone append caused non-contiguous physical results, and frees dummy checksum structures for nodatasum I/O.
- `btrfs_rewrite_logical_zoned()` updates the ordered extent and its extent map with the final logical disk bytenr.
- `btrfs_zoned_split_ordered()` splits both extent map and ordered extent around a contiguous zone-append result segment.

Metadata write-pointer enforcement:
- `btrfs_check_meta_write_pointer()` ensures metadata extent buffers are written exactly at a block group’s `meta_write_pointer`.
- `check_bg_is_active()` activates tree-log/metadata/system groups as needed, pivots active metadata/system groups, waits for writeback before finishing old groups, and avoids deadlocks when unsent I/O exists.
- Return meanings are explicit: `0` means the metadata buffer may be written, `-EAGAIN` means a commit-time hole must be filled, and `-EBUSY` means callers should bail out.

Device replace support:
- `read_zone_info()` maps a logical address to read mirrors and reads zone state from a usable mirror, rejecting RAID56.
- `btrfs_sync_zone_write_pointer()` advances a target device’s sequential zone by zero-filling from the current target position to the source write pointer.

Zone finishing:
- `btrfs_zone_finish()` calls `do_zone_finish()` for a block group.
- `do_zone_finish()` verifies active state, avoids finishing metadata groups with unwritten allocated space, can set a block group read-only and wait for reservations/ordered extents/extent-buffer writeback, marks allocation as full, updates metadata write pointer and free space, clears tree-log/data-reloc special markers, finishes underlying device zones, removes the group from `zone_active_bgs`, and wakes waiters.
- `call_zone_finish()` issues `REQ_OP_ZONE_FINISH` for sequential zones, restores reserved active-zone counts for metadata/system, and clears device active-zone bits.
- `btrfs_zone_finish_endio()` finishes a block group after an endio reaches the last allocatable unit.
- `btrfs_schedule_zone_finish_bg()` queues asynchronous finishing for metadata block groups near the end, waiting on the last extent buffer first.

Zoned data relocation:
- `btrfs_zoned_reserve_data_reloc_bg()` chooses or allocates an empty data block group for zoned relocation, moves it into the data-relocation space info when needed, sets `fs_info->data_reloc_bg`, marks `BLOCK_GROUP_FLAG_ZONED_DATA_RELOC`, and activates it.
- `btrfs_clear_data_reloc_bg()` clears the global data relocation block-group marker.
- `btrfs_zoned_release_data_reloc_bg()` clears the relocation runtime flag after the last relocated range has been written.

Reclaim and reset:
- `btrfs_free_zone_cache()` drops per-device zone caches after mount-time use.
- `btrfs_zoned_should_reclaim()` compares total device bytes used against total filesystem bytes and the configured reclaim threshold.
- `btrfs_reset_unused_block_groups()` finds fully zone-unusable unused block groups of a given space type, resets all underlying zones, resets allocation offset/free space/accounting, and returns reclaimed bytes to the space info.

Statistics:
- `btrfs_show_zoned_stats()` prints active block-group count, reclaimable/unused counts, reclaim need, data relocation and tree-log block-group ids, and details for every active zone/block group.

Cross-file relationships:
- Uses `volumes.h` chunk maps, devices, stripe geometry, device replace state, and mapping APIs.
- Uses `block-group.h` and `space-info.h` for block-group runtime flags, allocation offsets, free-space accounting, and space-info lists.
- Uses `bio.h`, ordered extent code, compression-independent checksum state, and extent maps for zone append completion.
- Uses `disk-io.h` superblock helpers and extent-buffer writeback waiting.
- Uses `transaction.h` and chunk allocation to reserve data relocation block groups.
- Exposes declarations and inline helpers through `zoned.h`.

Important invariants and risks:
- Zoned filesystems require all devices to have the same zone size; regular devices are allowed only via conventional-zone emulation.
- Zone size must align to `BTRFS_STRIPE_LEN`.
- Mixed block groups, space cache v1, and NODATACOW are incompatible with zoned mode.
- Sequential block-group allocation is append-only: `alloc_offset`, `zone_capacity`, and `meta_write_pointer` must never imply writes behind a device write pointer.
- Data non-SINGLE zoned profiles require raid-stripe-tree support.
- RAID5/6 zoned block groups are not supported by this loader.
- Active-zone accounting must reserve capacity for metadata/system/tree-log needs before data activation.
- Metadata writes are serialized around `zoned_meta_io_lock` and must follow `meta_write_pointer` exactly.
- Zone append can change physical placement; ordered extents and checksum logical addresses must be repaired before completion.
- Zone finish must wait for relevant outstanding writes unless the caller proves the last allocatable block has completed.
- Resetting unused block groups assumes they are fully zone-unusable and unused; partial reset is intentionally avoided.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zoned.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zoned.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zoned.h

This header declares the zoned-mode interface, defines per-device zoned state, supplies non-zoned build stubs, and provides inline helpers for zone type checks, empty-zone bitmap updates, zoned metadata/data relocation locks, and full-block-group checks.

Main structure:
- `struct btrfs_zoned_device_info` stores per-device zone geometry and state:
  - `zone_size`, `zone_size_shift`, and `nr_zones`.
  - `max_active_zones`, `reserved_active_zones`, and atomic `active_zones_left`.
  - Bitmaps for sequential zones, empty zones, and active zones.
  - Optional `zone_cache` for reported zone data.
  - Cached superblock log zones for all superblock mirrors.

Exported zoned API when `CONFIG_BLK_DEV_ZONED` is enabled:
- Device setup/teardown: `btrfs_get_dev_zone_info_all_devices()`, `btrfs_get_dev_zone_info()`, `btrfs_destroy_dev_zone_info()`, `btrfs_clone_dev_zone_info()`.
- Mount validation: `btrfs_check_zoned_mode()`, `btrfs_check_mountopts_zoned()`.
- Superblock log locations: `btrfs_sb_log_location_bdev()`, `btrfs_sb_log_location()`, `btrfs_advance_sb_log()`, `btrfs_reset_sb_log_zones()`.
- Allocation/reset helpers: `btrfs_find_allocatable_zones()`, `btrfs_reset_device_zone()`, `btrfs_ensure_empty_zones()`.
- Block-group state: `btrfs_load_block_group_zone_info()`, `btrfs_calc_zone_unusable()`, `btrfs_zone_activate()`, `btrfs_zone_finish()`, `btrfs_can_activate_zone()`, `btrfs_zone_finish_endio()`, `btrfs_schedule_zone_finish_bg()`.
- I/O helpers: `btrfs_use_zone_append()`, `btrfs_record_physical_zoned()`, `btrfs_check_meta_write_pointer()`, `btrfs_zoned_issue_zeroout()`, `btrfs_sync_zone_write_pointer()`, `btrfs_finish_ordered_zoned()`.
- Relocation/reclaim/stats: `btrfs_clear_data_reloc_bg()`, `btrfs_zoned_reserve_data_reloc_bg()`, `btrfs_free_zone_cache()`, `btrfs_zoned_should_reclaim()`, `btrfs_zoned_release_data_reloc_bg()`, `btrfs_zone_finish_one_bg()`, `btrfs_zoned_activate_one_bg()`, `btrfs_check_active_zone_reservation()`, `btrfs_reset_unused_block_groups()`, `btrfs_show_zoned_stats()`.

Non-zoned build stubs:
- Most helpers become no-ops or regular-filesystem fallbacks.
- `btrfs_check_zoned_mode()` rejects zoned filesystems with `-EOPNOTSUPP` when zoned block-device support is not compiled.
- Superblock location helpers return regular Btrfs superblock offsets.
- Zone append is disabled.
- Zone reset/zeroout synchronization returns unsupported where meaningful.

Inline helpers:
- `btrfs_dev_is_sequential()` checks the sequential-zone bitmap for a physical position.
- `btrfs_dev_is_empty_zone()` treats devices without zone info as empty and otherwise checks the empty-zone bitmap.
- `btrfs_dev_set_empty_zone_bit()`, `btrfs_dev_set_zone_empty()`, and `btrfs_dev_clear_zone_empty()` update empty-zone state.
- `btrfs_check_device_zone_type()` enforces that zoned filesystems use either regular devices or zoned devices matching the filesystem zone size, while non-zoned filesystems reject zoned devices.
- `btrfs_check_super_location()` allows superblocks only on non-sequential zones for zoned devices.
- `btrfs_can_zone_reset()` requires sequential zones and zone-aligned physical/length.
- `btrfs_zoned_meta_io_lock()` and `btrfs_zoned_meta_io_unlock()` wrap `fs_info->zoned_meta_io_lock` only for zoned filesystems.
- `btrfs_clear_treelog_bg()` clears the global tree-log block-group marker under lock.
- `btrfs_zoned_data_reloc_lock()` and `btrfs_zoned_data_reloc_unlock()` serialize data relocation I/O only for zoned data-reloc roots.
- `btrfs_zoned_bg_is_full()` checks `alloc_offset == zone_capacity` and asserts zoned mode.

Cross-file relationships:
- Implemented by `zoned.c`.
- Consumed by mount/device setup, block-group allocation/reclaim, metadata writeback, ordered extent completion, scrub/repair paths, and device replace.
- Includes `volumes.h`, `disk-io.h`, `block-group.h`, and `btrfs_inode.h` because zoned policy spans devices, chunks, block groups, metadata buffers, and inodes.

Important invariants:
- `zone_info` may be absent for non-zoned devices in non-zoned filesystems; helpers must tolerate that.
- Empty/active/sequential state is indexed by `pos >> zone_size_shift`.
- Superblock locations on true zoned devices must avoid sequential write-required zones except through the dedicated log-zone mechanism.
- Metadata I/O and data relocation locks are conditional on zoned mode and must not impose overhead or locking on regular filesystems.
- `btrfs_zoned_bg_is_full()` is valid only for zoned block groups.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zoned.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zstd.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zstd.c

This file implements the Btrfs zstd compression backend: zstd parameter limiting, per-level workspace management, idle workspace reclaim, compression into `compressed_bio`, bio decompression, inline/single-buffer decompression, and advertised zstd compression levels.

Zstd limits:
- `ZSTD_BTRFS_MAX_WINDOWLOG` is 17, capping the window to 128 KiB.
- `ZSTD_BTRFS_MAX_INPUT` is derived from that window limit.
- Supported levels range from `-15` through `15`, with default level `3`.
- `zstd_get_btrfs_parameters()` gets kernel zstd parameters for a level and source length, then caps `windowLog` to Btrfs’s maximum.

Workspace model:
- `struct workspace` stores zstd memory, memory size, sector-sized output buffer, allocated level, requested level, last-used timestamp, list nodes, zstd input/output buffers, and current parameters.
- `struct zstd_workspace_manager` owns a lock, global LRU, idle workspace lists by clipped level, active-level bitmap, wait queue, and reclaim timer.
- `clip_level()` maps the public compression level to an internal zero-based index; negative fast-mode levels use level-1 workspace sizing.
- `zstd_calc_ws_mem_sizes()` precomputes monotonic workspace memory requirements across all supported levels so a higher-level workspace can satisfy lower-level requests.

Workspace lifecycle:
- `zstd_alloc_workspace_manager()` allocates the manager, initializes lists/waitqueue/timer, stores it in `fs_info->compr_wsm[BTRFS_COMPRESS_ZSTD]`, calculates memory sizes, and tries to preallocate one max-level workspace for forward progress.
- `zstd_free_workspace_manager()` removes the manager from `fs_info`, frees idle workspaces from all level lists, deletes the reclaim timer, and frees the manager.
- `zstd_alloc_workspace()` allocates one workspace, its zstd memory, and its sector-sized buffer.
- `zstd_free_workspace()` frees a workspace.
- `zstd_find_workspace()` searches idle workspace lists at or above the requested level, removes a matching workspace, and marks its requested level.
- `zstd_get_workspace()` finds or allocates a workspace. If allocation fails under memory pressure, it sleeps on the manager wait queue and retries, relying on the protected max-level workspace for forward progress.
- `zstd_put_workspace()` returns a workspace to its idle list, updates LRU state for matching requested/allocated levels, hides one max-level workspace from reclaim, arms the reclaim timer, clears `req_level`, and wakes waiters when a max-level workspace returns.
- `zstd_reclaim_timer_fn()` scans the LRU and frees idle workspaces unused for `ZSTD_BTRFS_RECLAIM_JIFFIES`.

Compression path:
- `zstd_compress_bio()` initializes a zstd compression stream with Btrfs-capped parameters and the requested level.
- It maps filemap folios as input, allocates compressed output folios, streams input through `zstd_compress_stream()`, and adds full or final output folios to the compressed bio.
- It rejects compression when output grows beyond input or cannot fit into the target bio, returning `-E2BIG`.
- It returns `-EIO` for zstd stream errors and `-ENOMEM` for output folio allocation failure.
- It unmaps input folios and frees unused output folios on exit.

Bio decompression:
- `zstd_decompress_bio()` initializes a zstd dstream with `ZSTD_BTRFS_MAX_INPUT`, maps compressed bio folios, inflates into the workspace buffer, and copies decompressed bytes into the target pages with `btrfs_decompress_buf2page()`.
- It advances through compressed input folios as each input buffer is consumed.
- It detects zstd errors and invalid input exhaustion as `-EIO`.

Inline/single-buffer decompression:
- `zstd_decompress()` initializes a dstream, points input at the provided memory buffer, inflates into the workspace sector-sized buffer, copies the produced bytes into the destination folio, and zero-fills any missing tail.
- Short output is treated as `-EIO`.

Compression levels:
- `btrfs_zstd_compress` advertises min `-15`, max `15`, and default `3`.

Cross-file relationships:
- Registered through Btrfs compression infrastructure in `compression.h`.
- Uses `compressed_bio`, compressed folio allocation/free, and `btrfs_decompress_buf2page()`.
- Stores its workspace manager in `fs_info->compr_wsm[BTRFS_COMPRESS_ZSTD]`.
- Uses `btrfs_sb()` from `super.h` in single-buffer decompression to retrieve `fs_info`.

Important invariants and risks:
- Workspace sizes are intentionally monotonic so higher-level workspaces can be reused for lower-level requests.
- At least one max-level workspace is protected from reclaim to preserve forward progress during allocation failure.
- `req_level` distinguishes the caller-requested level from the allocated workspace level; LRU updates only happen when they correspond.
- The zstd window is capped to keep compressed extents within Btrfs’s decompression assumptions.
- Compression must produce fewer bytes than input; otherwise the backend reports `-E2BIG`.
- All mapped input folios must be unmapped and put on all paths.
- Decompression short output zero-fills the destination tail and reports error.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/zstd.c -->