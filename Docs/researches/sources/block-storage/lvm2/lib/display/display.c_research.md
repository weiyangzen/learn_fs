# File Research: sources/block-storage/lvm2/lib/display/display.c

This file implements human-readable and legacy-colon display helpers for LVM metadata objects and common conversion routines. It covers allocation policy conversion, lock-type conversion, size and percentage formatting, PV/LV/VG display output, segment display, name validation diagnostics, and the interactive yes/no prompt used by commands.

Allocation and lock helpers:
- `_policies` maps `alloc_policy_t` values to strings and report characters. `get_alloc_from_string` also accepts old metadata text `next free` as normal allocation.
- `get_lock_type_string` and `get_lock_type_from_string` map internal lock types to text values such as `none`, `dlm`, `sanlock`, and `idm`.
- `get_percent_string` maps percent denominator types to strings used in reports.

Formatting helpers:
- `display_lvname` and `display_percent` use a ring buffer in `cmd_context` to return short-lived strings.
- `display_size`, `display_size_long`, and `display_size_units` delegate sector-based formatting to `dm_size_to_string` using current command unit settings.
- `display_mb_size` converts MiB units to sectors before formatting.

PV display functions produce colon, segment, full, and short output. Full PV display derives usable/unusable size from PE layout, shows allocation state, PE counts, and UUID. Segment display iterates PV segments and prints either mapped LV extent ranges or free ranges.

LV display is broad and target-aware:
- `lvdisplay_full` handles historical LVs, visible vs internal naming, activation/read-only state, snapshots, thin volumes/pools, cache, cache pools, integrity, VDO pools/volumes, mirrors, RAID availability, read ahead, persistent major/minor, and block device numbers.
- It queries activation status with `lv_info`, target-specific status helpers such as `lv_thin_status`, `lv_cache_status`, `lv_vdo_pool_status`, and releases status memory pools after use.
- `lvdisplay_colons` preserves legacy colon output fields.
- `lvdisplay_segments` iterates segments and delegates segment-specific display to each segment type handler.

VG display functions emit full, colon, and short summaries including system_id, format, metadata area count, seqno, access mode, resize/export/shared status, LV/PV counts, active PVs, extent counts, sizes, free space, and UUID.

`display_formats`, `display_segtypes`, and `display_tags` simply iterate command-context lists and print names. `display_name_error` translates name validation enum values into user-facing errors.

`yes_no_prompt` is a robust stdin prompt parser. It defaults to `n` in silent mode or EOF, accepts lowercase yes/no prefixes with stricter newline behavior for yes, ignores leading/trailing whitespace, logs invalid input, and integrates with LVM signal handling so interrupts result in a negative answer.

Important dependencies include metadata object definitions, activation/status helpers, segment type handlers, config defaults, signal helpers, and logging functions. Most routines are display-only, but they can trigger target status queries and therefore may allocate/free transient status structures.
