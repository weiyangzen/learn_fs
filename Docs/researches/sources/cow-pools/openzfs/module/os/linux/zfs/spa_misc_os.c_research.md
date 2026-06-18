# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/spa_misc_os.c

## Purpose

Linux-specific SPA miscellaneous hooks: module parameter parsing, history zone label, and restoration/cleanup of UID-based dataset zoning on pool import/export.

## Parameter Hooks

- `param_set_deadman_failmode()`: validates via common deadman failmode parser, then stores char pointer.
- `param_set_deadman_ziotime()`: parses milliseconds and updates deadman ZIO time in nanoseconds.
- `param_set_deadman_synctime()`: parses milliseconds and updates deadman sync time in nanoseconds.
- `param_set_slop_shift()`: parses integer, accepts only values 1 through 31, then stores parameter.
- `param_set_active_allocator()`: validates allocator name through common parser, then stores char pointer.

## OS Hooks

- `spa_history_zone()`: returns `"linux"` for history records.
- `spa_import_os(spa)`: walks datasets in imported pool and restores nonzero `zoned_uid` properties by calling `zone_dataset_attach_uid(kcred, ...)`.
- `spa_export_os(spa)`: walks datasets and detaches nonzero `zoned_uid` delegations with `zone_dataset_detach_uid(kcred, ...)`.
- `spa_activate_os()` / `spa_deactivate_os()`: no-op Linux hooks.

## Notes

Restore and cleanup callbacks log warnings if UID delegation attach/detach fails with errors other than expected duplicate/missing cases.
