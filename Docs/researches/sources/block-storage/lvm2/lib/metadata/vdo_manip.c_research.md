# File Research: sources/block-storage/lvm2/lib/metadata/vdo_manip.c

This file implements VDO pool status parsing, VDO LV conversion, target parameter filling, and memory constraint checks.

Main entry points:
- State name helpers: `get_vdo_compression_state_name()`, `get_vdo_index_state_name()`, `get_vdo_operating_mode_name()`, `get_vdo_write_policy_name()`.
- Size helpers: `get_vdo_pool_virtual_size()`, `update_vdo_pool_virtual_size()`, `get_vdo_pool_max_extents()`.
- Status parsing: `parse_vdo_pool_status()`.
- Conversion: `convert_vdo_pool_lv()`, `convert_vdo_lv()`.
- Config parsing: `set_vdo_write_policy()`, `fill_vdo_target_params()`.
- Resource validation: `check_vdo_constraints()`.

Control flow:
- `parse_vdo_pool_status()` parses device-mapper VDO target status, builds the DM name, optionally reads kvdo sysfs counters, then computes usage, saving, and data usage percentages.
- `_format_vdo_pool_data_lv()` builds `vdoformat` arguments, pipes its output, parses the default logical block count if virtual size was not specified, and reports tool output line by line.
- `convert_vdo_pool_lv()` validates VDO parameters, optionally formats the active data LV, deactivates it, inserts a `_vdata` layer, sets the segment type to `vdo-pool`, and records virtual extents/header size.
- `convert_vdo_lv()` handles full user-facing conversion: optional rename to generated pool name, temporary activation, wipe, pool conversion, virtual VDO LV creation, and segment/name swapping when preserving the original LV name.
- `check_vdo_constraints()` estimates RAM requirements from physical size, virtual size, block map cache, index memory, base overhead, and available RAM/swap.

Dependencies:
- Device-mapper VDO status/validation APIs.
- External `vdoformat` configured by `global_vdo_format_executable` and options.
- LVM layer manipulation: `insert_layer_for_lv()`, `move_lv_segments()`, `set_lv_segment_area_lv()`, `lv_create_single()`, `lv_rename_update()`.
- `/proc/meminfo` or `sysinfo()` for memory estimates.
- kvdo sysfs paths in both current `block/dm-N/vdo/...` and older `kvdo/name/...` layouts.

Correctness notes:
- VDO virtual size includes front/back headers to avoid blkid collisions, then subtracts headers before computing virtual extents.
- VDO logical size is rounded to a 4 KiB target boundary.
- Only one VDO LV per VDO pool is assumed in `update_vdo_pool_virtual_size()`.
- Non-auto write policies are accepted but logged as deprecated.

Risks:
- Conversion has many irreversible-looking metadata transformations and relies on correct deactivation after formatting.
- Output parsing from `vdoformat` is locale-sensitive by the file’s own TODO.
- Memory checks are estimates and intentionally conservative, not kernel enforcement.
