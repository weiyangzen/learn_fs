# File Research: sources/block-storage/linux-dm/drivers/md/dm.h

## Purpose
Defines internal Device Mapper declarations shared across DM core, table, target registry, ioctl interface, sysfs, target implementations, zoned support, request-based support, and mempool management.

## Main Interfaces
- Suspend/status flags: `DM_SUSPEND_LOCKFS_FLAG`, `DM_SUSPEND_NOFLUSH_FLAG`, `DM_STATUS_NOFLUSH_FLAG`.
- Table API declarations for target lookup, table sizing/restrictions, event callbacks, target suspend/resume hooks, queue mode, immutable target metadata, and table mempools.
- Target type helpers: `dm_target_bio_based()`, `dm_target_request_based()`, `dm_target_hybrid()`.
- Zoned declarations: `dm_set_zones_restrictions()`, `dm_zone_endio()`, `dm_blk_report_zones()`, `dm_is_zone_write()`, `dm_zone_map_bio()`, with stubs when zoned block support is disabled.
- Core mapped-device declarations for lifecycle, deletion, table devices, deferred removal, uevents, kobject lookup, open counts, and queue setup.
- Internal suspend/resume and mempool allocation declarations.

## Control Flow
This header does not implement control flow, but establishes the internal contracts used by `dm.c` and related DM files. It separates public device-mapper APIs from private cross-file entry points and makes compile-time zoned support conditional.

## State And Synchronization
Declares the functions that inspect mapped-device deletion/suspend/deferred-remove state and internal suspend state. It also exposes APIs whose implementations rely on mapped-device locks, SRCU table protection, kobject reference handling, and mempool lifetime rules.

## Integration Points
Used by DM core files, ioctl/control code, target table code, target registry code, zoned support, sysfs, request-based DM, and built-in targets such as linear and stripe.

## Notable Behaviors
- Target mode detection is callback-presence based: bio targets provide `map`, request targets provide `clone_and_map_rq`, and hybrids provide both.
- Zoned support compiles to conservative stubs without `CONFIG_BLK_DEV_ZONED`; zone mapping then kills bios by returning `DM_MAPIO_KILL`.
- Declares both `dm_internal_suspend_noflush()` and an older `dm_internal_suspend()` prototype, reflecting internal API compatibility concerns.

## Risks And Review Focus
- Because this is an internal header, prototype drift can break subtle lock or lifetime expectations across DM files.
- Callback-presence macros assume target types consistently initialize their operation tables.
- Conditional zoned stubs must match the behavior expected by core code when zoned support is unavailable.
