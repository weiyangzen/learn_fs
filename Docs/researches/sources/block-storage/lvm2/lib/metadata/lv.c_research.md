# File Research: sources/block-storage/lvm2/lib/metadata/lv.c

Purpose: implements core logical-volume utility functions for type checks, report/display duplication, LV relationship discovery, segment device formatting, kernel-status interpretation, RAID health checks, LV naming/VG association, activation, and lock-holder resolution.

Read coverage: complete file read, 1,936 lines.

Key responsibilities:
- Implements `lv_is_locked()` as a recursive check over sub-LVs, replacing a simple top-level flag check.
- Identifies simple single-segment `error` and `zero` LVs and orphan pvmove error LVs.
- Formats segment PV/LV areas and metadata areas into report lists and strings, including extent ranges and optional hidden-device marking.
- Provides report duplicate helpers for segment type, tags, cache mode, monitor state, discards, kernel discards, LV names, UUIDs, full names, paths, device-mapper paths, timestamps, hosts, profiles, lock args, and active state.
- Computes segment start/size/chunk size and data/metadata/origin sizes.
- Converts device-mapper target status into percentages for integrity recalculation, cache data/metadata/dirty usage, writecache usage, RAID sync, snapshots, thin pools, thin volumes, and VDO pools.
- Checks whether an LV or any sub-LV is placed on a given PV or list of PVs.
- Resolves LV relationships: origin, parent, mirror log, pool LV, data LV, metadata LV, conversion LV, pvmove source PV, and visible layer names.
- Checks mirror and RAID image sync state through mirror percent or RAID health strings.
- Implements `lv_raid_healthy()` and maps RAID health to refresh/repair needs, including special treatment for virtual/error legs after missing-PV removal and reshape count mismatches.
- Builds the standard 10-character `lv_attr` string, combining LV type, permissions, allocation/lock state, activation state, open state, layout class, zeroing, partial/RAID/cache/thin/writecache health, and activation-skip state.
- Maintains creation metadata, LV names in the VG radix tree, and LV movement between VGs.
- Activates/deactivates LVs while coordinating persistent lockd locks for exclusive/shared activation modes.
- Finds the LV that should hold activation locks through COW, thin, external origin, RAID, pvmove, cache, and pending-delete relationships.

Important entry points:
- Type and relation helpers: `lv_is_historical()`, `lv_is_locked()`, `lv_origin_lv()`, `lv_parent()`, `lv_pool_lv()`, `lv_data_lv()`, `lv_metadata_lv()`, `lv_lock_holder()`.
- Reporting helpers: `lv_attr_dup_with_info_and_seg_status()`, `lv_attr_dup()`, `lvseg_percent_with_info_and_seg_status()`, `lvseg_*_str()`, `lv_*_dup()`.
- RAID/sync helpers: `lv_mirror_image_in_sync()`, `lv_raid_image_in_sync()`, `lv_raid_healthy()`.
- Mutation helpers: `lv_set_creation()`, `lv_set_name()`, `lv_set_vg()`, `lv_active_change()`.

Dependencies:
- Uses metadata, activation, display, config/defaults, lvmlockd, device-mapper status structs, dmeventd monitoring when enabled, radix-tree name indexes, and segment-type callbacks.
- Depends on many metadata helpers declared in `metadata-exported.h` and `lv.h`.

Risk and edge cases:
- Report helpers often allocate from caller-provided pools; allocation failures are logged and returned as `NULL`.
- RAID health strings may not match area counts during reshape, so the code falls back to broader unhealthy detection.
- `lv_attr` is dense external-facing behavior; changing character meanings can break scripts and user expectations.
- `lv_set_name()` must keep the VG radix tree consistent and rejects duplicate names.
- Lock-holder resolution must skip pending-delete and unused cache-pool users to avoid locking dead or irrelevant layers.
