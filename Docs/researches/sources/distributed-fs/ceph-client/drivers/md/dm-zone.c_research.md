# sources/distributed-fs/ceph-client/drivers/md/dm-zone.c

## Purpose

`dm-zone.c` provides the generic device-mapper integration layer for zoned block devices. It lets mapped devices expose `report_zones`, revalidate zone state while a new DM table is being bound, compute zoned queue restrictions, decide whether zone append must be emulated, translate zone append completions back to the original logical position, and build bitmaps for emulated `ZONE_RESET_ALL`.

## Important APIs, Types, and Functions

- `dm_blk_report_zones()` is the block-device `gendisk` report-zones operation exported through `dm_blk_dops` in `dm.c`. It chooses either the live table or the temporary `zone_revalidate_map` used during table binding.
- `dm_report_zones()` is exported for zoned target implementations. It wraps `blkdev_report_zones()` and remaps target-relative zone starts and write pointers to mapped-device sector space through `dm_report_zones_cb()`.
- `dm_revalidate_zones()` temporarily exposes a not-yet-live table to `blk_revalidate_disk_zones()` so zone write plug resources can be initialized during `__bind()`.
- `dm_set_zones_restrictions()` inspects each target's devices through `iterate_devices`, establishes max open/active zone limits, disables native zone append if any target requires emulation, and rejects incompatible reloads once zone plug resources exist.
- `dm_finalize_zone_settings()` updates `DMF_EMULATE_ZONE_APPEND` and clears zoned disk state when the table is effectively non-zoned.
- `dm_zone_endio()` adjusts the original bio sector after a successful `REQ_OP_ZONE_APPEND` clone completes.
- `dm_zone_get_reset_bitmap()` reports zones internally and marks the non-empty sequential zones that need individual reset for reset-all emulation.

## Control Flow

Zone reporting starts in `dm_blk_report_zones()`, obtains a table under SRCU unless the caller is the revalidation task, then loops over targets with `dm_blk_do_report_zones()`. Each target must provide `report_zones`; the callback stops at the target end, remaps `start` and `wp`, optionally calls an internal callback, and finally emits the report with `disk_report_zone()`.

Queue setup calls `dm_set_zones_restrictions()` after table queue-limit calculation. It first determines whether native zone append can be used by checking target flags and the zoned status of all iterated devices. It then iterates all targets again to count mapped sequential zones and reduce max open/active limits. If no sequential zones are mapped, the DM device is downgraded to a regular block device by clearing zoned features and zone sizing.

## State and Persistence Behavior

This file does not define durable metadata. Its state is transient DM core state: `md->zone_revalidate_map`, `md->revalidate_map_task`, `md->disk->nr_zones`, queue-limit fields, `DMF_EMULATE_ZONE_APPEND`, and zone write plug allocation state.

## Dependencies and Integration Points

It depends on the block layer zoned APIs, DM table APIs, and target callbacks (`report_zones`, `iterate_devices`). `dm.c` calls `dm_zone_endio()` from clone completion, uses `dm_is_zone_write()` to avoid unsafe requeueing, and uses `dm_zone_get_reset_bitmap()` for `ZONE_RESET_ALL` emulation.

## Risks and Test Signals

Partially mapped underlying zoned devices can produce unreliable open/active limits; reloads after zone plug allocation are constrained; target zone reports must be correctly target-relative. Test with `blkzone report`, table reloads, append completion position checks, reset-all emulation, and conventional-only mappings.
