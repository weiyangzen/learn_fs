# sources/distributed-fs/ceph-client/fs/btrfs/zoned.c

## Purpose

`zoned.c` implements Btrfs zoned block device support. It discovers device zone geometry, validates zoned mode, manages superblock log zones, computes block-group allocation/write pointers from zone state, tracks active zones, serializes metadata and relocation writes, handles zone append completion rewrites, finishes and resets zones, reserves relocation block groups, and reports zoned runtime statistics.

## Important APIs, Types, And Functions

Zone discovery starts with `btrfs_get_dev_zone_info_all_devices()` and `btrfs_get_dev_zone_info()`. These allocate `struct btrfs_zoned_device_info`, determine zone size and count, allocate `seq_zones`, `empty_zones`, and `active_zones` bitmaps, optionally allocate a zone cache, report or emulate zones, validate active-zone limits, and validate superblock log zone pairs. `btrfs_destroy_dev_zone_info()` and `btrfs_clone_dev_zone_info()` manage lifetime and device-replace cloning.

Superblock log support is built around `sb_write_pointer()`, `sb_log_location()`, `btrfs_sb_log_location_bdev()`, `btrfs_sb_log_location()`, `btrfs_advance_sb_log()`, and `btrfs_reset_sb_log_zones()`. Zoned devices use two sequential zones per mirror as a circular log. When both are full, the latest superblock generation is selected. Write-side location can reset the next full zone before reuse.

Mode validation is handled by `btrfs_check_zoned_mode()` and `btrfs_check_mountopts_zoned()`. They reject host-managed zoned devices without the incompat flag, require equal zone sizes, validate queue limits, require stripe alignment to zone size, disallow mixed block groups, disable async discard, reject space cache v1 and NODATACOW, set `fs_info->zone_size`, `max_zone_append_size`, chunk allocation policy, and max extent size.

Allocation and block-group loading are centered on `btrfs_load_block_group_zone_info()`. It finds the chunk map, loads per-stripe zone state with `btrfs_load_zone_info()`, computes conventional fallback allocation pointers via `calculate_alloc_pointer()`, and dispatches profile-specific logic through `btrfs_load_block_group_by_raid_type()`. Profile helpers handle SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10 write-pointer reconstruction, capacity computation, active-state reconciliation, degraded handling, and raid-stripe-tree requirements for non-single data profiles.

Runtime zone management includes `btrfs_find_allocatable_zones()`, `btrfs_reset_device_zone()`, `btrfs_ensure_empty_zones()`, `btrfs_calc_zone_unusable()`, `btrfs_zone_activate()`, `btrfs_zone_finish()`, `btrfs_can_activate_zone()`, `btrfs_zone_finish_one_bg()`, `btrfs_zoned_activate_one_bg()`, `btrfs_check_active_zone_reservation()`, and `btrfs_reset_unused_block_groups()`.

IO-specific functions include `btrfs_use_zone_append()`, `btrfs_record_physical_zoned()`, `btrfs_finish_ordered_zoned()`, `btrfs_check_meta_write_pointer()`, `btrfs_zoned_issue_zeroout()`, and `btrfs_sync_zone_write_pointer()`.

## Control Flow And Integration

During mount, Btrfs reads or emulates each device's zone information, validates the filesystem's zoned mode, builds per-block-group write pointer state, and registers active block groups. Device zone bitmaps become the source of truth for sequential, empty, and active status. The chunk allocator uses `btrfs_find_allocatable_zones()` and active-zone checks to avoid superblock locations and active-zone exhaustion.

For data writes, `btrfs_use_zone_append()` selects `REQ_OP_ZONE_APPEND` only for regular data in sequential block groups and avoids relocation. Zone append can return a physical address different from the planned one, so `btrfs_record_physical_zoned()` adjusts checksum logicals and `btrfs_finish_ordered_zoned()` splits or rewrites ordered extents when completion sums are not contiguous.

Metadata writes are serialized around `meta_write_pointer`. `btrfs_check_meta_write_pointer()` caches or finds the containing block group, verifies the extent buffer starts at the current metadata write pointer, activates or pivots active metadata/system block groups if active-zone tracking requires it, and returns `-EAGAIN` or `-EBUSY` when holes or writeback ordering prevent immediate write.

Finishing a zone proceeds through `do_zone_finish()`: it verifies active state, waits for reservations, ordered extents, and metadata writeback when needed, marks the block group full/unallocatable, issues `REQ_OP_ZONE_FINISH` on sequential stripes, updates active-zone accounting and reservations, removes the block group from the active list, and wakes waiters on `BTRFS_FS_NEED_ZONE_FINISH`.

Relocation support reserves a dedicated data relocation block group via `btrfs_zoned_reserve_data_reloc_bg()`, migrating an empty data block group to the relocation space-info or allocating a new one. `btrfs_zoned_release_data_reloc_bg()` releases the flag after relocated writes reach the expected end.

## State And Persistence Behavior

Persistent zoned state is partly on disk and partly reconstructed from block device zone write pointers. Superblock mirrors are persisted as log records in two zones per mirror. Block-group `alloc_offset`, `zone_capacity`, `zone_unusable`, `meta_write_pointer`, `physical_map`, and runtime flags are reconstructed at mount and maintained during writes. Device bitmaps track runtime zone classifications and active-zone budget; empty/active bits are updated after reset, allocation, activation, and finish. The chunk tree and extent tree remain the persistent logical metadata, while write pointer reconciliation prevents allocating or writing behind the device's sequential constraints.

## Dependencies

The file depends on Linux zoned block APIs (`blkdev_report_zones_cached`, `blkdev_zone_mgmt`, `blkdev_issue_zeroout`, zone capacity/open/active limits), block queue limits, bitmaps, vmalloc, atomic counters, and memory-allocation scope controls. Btrfs dependencies include chunk maps and mapping (`volumes.h`), block-group and space-info management, transaction and chunk allocation, device replace locking, ordered extents, extent buffers, sysfs, bio mapping, checksum sums, relocation, and mount option handling.

## Risks And Edge Cases

Superblock log state has complex valid/invalid combinations; corruption returns `-EUCLEAN`. Zone sizes must be power-of-two, aligned to stripe length, equal across devices, and within supported min/max. Active-zone accounting is delicate because metadata/system reservations, data allocations, and device limits interact. Mixed conventional/sequential devices require emulated or calculated pointers and validation that no extents exist beyond write pointers. RAID0/RAID10 write-pointer reconstruction must handle partial stripes and stripe ordering. Metadata write pointer holes can deadlock if writeback waits in the wrong context. Device replace must sync target write pointers with zeroout and missing/failing devices can cause degraded-specific behavior. Resetting unused block groups bypasses deletion and must update `bytes_zone_unusable`, free-space control, and device zones coherently.

## Test Signals

Important tests include mounting zoned and non-zoned devices with and without the incompat flag; mixed regular/zoned emulation; invalid zone sizes and active-zone limits; superblock log read/write/reset after wraparound and corruption; allocation skipping superblock zones; block-group loading for SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10; degraded mount scenarios; zone append data writes with checksum logical rewrites and ordered extent splits; metadata writeback ordering and active metadata/system block-group pivoting; zone finish under full, partially written, reserved, relocation, and writeback-heavy cases; data relocation block-group reservation/release; unused block-group reset/reclaim; and sysfs or debugfs stat output.
