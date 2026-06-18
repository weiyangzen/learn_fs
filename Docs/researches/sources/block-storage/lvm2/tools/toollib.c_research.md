# File Research: sources/block-storage/lvm2/tools/toollib.c

## Purpose
`toollib.c` is the shared execution library for LVM CLI tools. It provides common command iteration over VGs, LVs, PVs, labels, LV segments, and PV segments; command selection support; activation helpers; tag changes; argument normalization; LV rule enforcement; PV creation/removal preparation; and persistent-reservation helpers.

## Process Handles And Selection
`init_processing_handle()` creates a `processing_handle`, initializes report formatting when needed, and enables internal selection reporting for non-report commands using `--select`. `init_selection_handle()` builds a selection report handle. `select_match_vg()`, `select_match_lv()`, and `select_match_pv()` invoke `report_for_selection()` so ordinary commands can filter objects with report expressions. `destroy_processing_handle()` restores report state and tears down report formatting when appropriate.

## Object Iteration
- `process_each_vg()` parses VG names/tags, scans labels, resolves duplicate VG names, locks global state when needed, reads VGs, applies selection, and calls a command callback per VG.
- `process_each_lv()` derives VG/LV targets from arguments or option-provided VG names, scans VGs, then delegates per-VG LV processing.
- `process_each_lv_in_vg()` filters visible, hidden, component, sanlock, historical, tag-selected, and named LVs; enforces command-definition LV type/property rules; then calls the LV callback.
- `process_each_pv()` maps PV path arguments to devices, scans all VGs, processes PVs by device/tag/all selection, handles duplicates, and can include non-PV devices for `-a` style reports.
- `process_each_label()` scans labels directly and has duplicate-device handling for label reporting.
- `process_each_segment_in_lv()` and `process_each_segment_in_pv()` iterate segments and propagate aggregate selection status.

## Validation And Command Rules
The file maps command-definition LV type/property bits to real predicates through `_lv_is_type()` and `_lv_is_prop()`. `_check_lv_types()` validates positional LV type requirements, while `_check_lv_rules()` evaluates conditional `RULE: ... INVALID|REQUIRE ...` constraints involving options, LV types, and LV properties. This ties generated command metadata to runtime object checks.

## Parameter Helpers
The file parses and validates common command options:
- `vgcreate_params_set_defaults()` and `vgcreate_params_set_from_args()` populate VG defaults, extent sizes, metadata copies, system IDs, lock types, shared VG settings, and sanlock lock args.
- `get_pool_params()`, `get_stripe_params()`, `get_cache_params()`, `get_vdo_settings()`, `get_writecache_settings()`, and `get_integrity_settings()` parse feature-specific options and config snippets.
- `get_activation_monitoring_mode()` resolves dmeventd monitoring behavior.
- `get_and_validate_major_minor()` handles persistent major/minor rules.
- `validate_lvname_param()` and `validate_restricted_lvname_param()` normalize VG/LV names and enforce naming restrictions.

## Activation And Background Work
`lv_change_activate()` centralizes LV activation/deactivation checks for cache pools, merging origins, partial RAID snapshots, duplicate PVs, and integrity recalculation. `lv_refresh()` refreshes an LV and starts background polling for snapshot merges when needed. `vg_refresh_visible()` refreshes visible LVs in a VG. `lv_spawn_background_polling()` starts pvmove or lvconvert pollers for in-progress operations.

## PV Create/Remove Workflow
`pvcreate_params_from_args()` parses PV creation/removal arguments including metadata copies, label sector, zeroing, alignment, metadata size, bootloader area, persistent-reservation options, and shared-VG constraints.

`pvcreate_each_device()` is the main device workflow for `pvcreate`, `pvremove`, `vgcreate`, and `vgextend` style callers. It builds per-device state, scans and filters devices, checks block-size consistency, detects existing PV/VG usage, handles force/yes prompts, temporarily releases the global lock while waiting for prompts, reacquires and rescans devices exclusively, verifies devices did not change, starts persistent reservations when requested, wipes signatures, creates PV labels, removes PV labels, updates device IDs, and invalidates exclusive label-scan state.

## Other Utilities
`change_tag()` applies add/remove tag operations to exactly one VG, LV, or PV target. `lvremove_single()` removes an LV with dependency handling and records removed UUIDs for device-file updates. `get_rootvg_dev_uuid()` finds the root mount in `/etc/mtab`, maps its device number to a dm UUID, and returns it when it is an LVM UUID. `persist_start_include()` implements direct, supplementary, and automatic persistent-reservation start behavior.

## Integration Notes
`toollib.c` sits between command handlers and lower LVM libraries: metadata read/write, lvmcache, label scanning, device filters, lockd, activation, reporting, config, persistent reservations, and device-id files. Many command handlers depend on its callback contracts and return-code aggregation.

## Risks
The file encodes many global CLI semantics in one place. Important risk areas include duplicate VG/PV handling, lock ordering around prompts and shared VGs, selection/report recursion, command-rule drift when LV type/property macro lists change, device filtering during PV creation, and paths that intentionally process inaccessible or partially readable metadata.
