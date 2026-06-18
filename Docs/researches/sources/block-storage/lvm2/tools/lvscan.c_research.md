# File Research: sources/block-storage/lvm2/tools/lvscan.c

## Purpose
Implements `lvscan`, listing logical volumes and their active/inactive state.

## Main Flow
- `lvscan()` ignores deprecated `--cache`/`--cache_long` because lvmetad is no longer used.
- Calls `process_each_lv()` over requested arguments.

## Per-LV Behavior
`_lvscan_single()`:
- Skips hidden LVs unless `--all` is set.
- Uses `lv_info()` to determine whether the LV exists in kernel.
- For COW snapshots, checks snapshot percent; invalid percent marks snapshot inactive.
- Prints:
  - active/inactive state
  - snapshot/origin label
  - full `/dev/<vg>/<lv>` path
  - LV size
  - allocation policy string.

## Important Details
- Snapshot state is stricter than generic kernel existence.
- Output is suppressed through normal LVM silent handling.
