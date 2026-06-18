# File Research: sources/block-storage/linux-dm/drivers/md/dm-zone.c

## Scope

This file provides generic Device Mapper support for zoned block devices. It implements report-zones dispatch/remapping across a DM table, maintains resources for zone-append emulation, tracks sequential-zone write pointers, serializes writes per zone, and adjusts completion semantics for native or emulated zone append.

## Public And Internal APIs Covered

- Zone reporting: `dm_blk_report_zones()`, internal `dm_blk_do_report_zones()`, helper `dm_report_zones()`, and callback `dm_report_zones_cb()`.
- Zoned-device setup/cleanup: `dm_set_zones_restrictions()`, `dm_cleanup_zoned_dev()`, `dm_revalidate_zones()`.
- Zone write classification: `dm_is_zone_write()`, `dm_need_zone_wp_tracking()`.
- Zone append emulation: `dm_zone_map_bio()`, `dm_zone_endio()`, `dm_zone_map_bio_begin()`, `dm_zone_map_bio_end()`.
- Write-pointer state helpers: `dm_get_zone_wp_offset()`, `dm_update_zone_wp_offset()`, `dm_update_zone_wp_offset_cb()`.
- Per-zone locking helpers: `dm_zone_lock()` and `dm_zone_unlock()`.

## Control Flow And Behavior

- `dm_blk_report_zones()` obtains the live table under SRCU, refuses reports while suspended, and walks targets by sector. Each target must provide `report_zones`.
- `dm_report_zones()` is the helper target drivers call to report a backing block device; its callback remaps zone starts and write pointers from target-relative sectors back into the mapped-device address space.
- `dm_set_zones_restrictions()` sets the mapped queue zone count, detects whether all targets and backing devices support native zone append, and either clears append emulation or allocates emulation state.
- Revalidation scans all zones while the mapped device is suspended, builds the conventional-zone bitmap, sequential-zone write-lock bitmap, and `md->zwp_offset` write-pointer offset array. It uses `memalloc_noio_save()` because the bind path must not recurse into I/O allocation.
- `dm_zone_map_bio()` is the special map path for targets needing zone append emulation. It locks the sequential zone, verifies writes/reset/finish/append against the tracked write pointer, rewrites zone append into a non-mergeable regular write at the current write pointer, calls the target mapper, updates `zwp_offset`, and drops an extra pending I/O reference.
- `dm_zone_endio()` unlocks the zone at clone completion. For native append, it adjusts the original bio sector by the lower bits of the completed clone sector. For emulated append, failed write-pointer-changing operations invalidate the tracked offset, and successful appends report the actual sector by using the offset after write completion.
- If a tracked write pointer is invalid, the next mapping path re-reports the single zone to recover the current offset before proceeding.

## State And Data Structures

- Uses `mapped_device` fields `nr_zones`, `zwp_offset`, `flags` including `DMF_EMULATE_ZONE_APPEND`, and the mapped queue fields `conv_zones_bitmap` and `seq_zones_wlock`.
- `DM_ZONE_INVALID_WP_OFST` marks a sequential zone whose write pointer must be rediscovered.
- `struct dm_report_zones_args` carries original callback/data, target, start sector, next sector, and zone index through target reports.
- The clone bio flag `BIO_ZONE_WRITE_LOCKED` records ownership of the per-zone write lock.

## Dependencies

- DM core table/target/SRCU APIs and `dm_target_io`/`dm_io` pending-count helpers.
- Linux zoned block APIs: `blkdev_report_zones()`, `blkdev_nr_zones()`, `bio_zone_no()`, `bio_zone_is_seq()`, `blk_queue_zone_sectors()`, zone conditions/types, and queue zone bitmaps.
- Bit wait/wakeup primitives for per-zone write locking.

## Risks And Invariants

- Zone-append emulation depends on strict serialization per sequential zone; `BIO_ZONE_WRITE_LOCKED` and `seq_zones_wlock` must be balanced on every map/completion path.
- `zwp_offset` must be updated only after target mapping has accepted the write-pointer-changing operation, and invalidated on uncertain failures.
- Zone append must not be truncated; the emulation path treats truncated append writes as I/O errors.
- Report-zone remapping must stop at target boundaries to avoid exposing backing zones beyond a target range.
- Memory allocations during revalidation and single-zone update run under NOIO constraints to avoid block-layer recursion.
