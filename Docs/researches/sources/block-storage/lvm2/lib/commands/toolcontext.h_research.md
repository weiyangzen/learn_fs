# File Research: sources/block-storage/lvm2/lib/commands/toolcontext.h

## Summary
Defines LVM2's central command context structure and associated lifecycle APIs. `struct cmd_context` carries command-line state, memory pools, formats, segment types, system identity, device filtering, configuration, archive/backup state, host tags, paths, reporting state, runtime flags, and assorted command behavior switches.

## Main Responsibilities
- Define `struct config_info`, the active/default mutable configuration subset used during command processing.
- Define `struct cmd_context_initialized_parts`, tracking whether config, filters, and connections are initialized.
- Define `struct cmd_report`, storing grouped reporting/log-report handles and report state.
- Define `struct cmd_context`, the central per-command or library context passed through most LVM internals.
- Declare tool context lifecycle, refresh, filter, connection, config, format lookup, orphan cache, and system ID APIs.

## Key Fields
- Memory: `libmem`, `mem`, `pending_delete_mem`.
- Command state: command line, command name, parsed command, enum ID, argv, option values, positional args.
- Formats/segments: current format, backup format, format list, segment type list.
- Identity: `system_id`, `product_uuid`, `hostname`, `kernel_vsn`.
- Flags: many bitfields controlling activation, foreign/shared VG visibility, locking, device scanning, devices-file behavior, MD detection, hints, component LV handling, reports, and validation.
- Devices/filtering: `dev_types`, `filter`, devices-file entries, devices list, MD component mode, device ID refresh/search state.
- Configuration: config file list, profile params, cascaded config tree, config definition hash, default/current settings.
- Paths: system directory, device directory, proc directory, devices file path, device-id sysfs override.
- Reporting and output: `cmd_report`, display buffer, time format, report list separator.
- Miscellaneous: pending delete list, random seed, VDO conversion params, lock options.

## Key Interfaces
- `create_toolcontext()`, `destroy_toolcontext()`, `refresh_toolcontext()`.
- `refresh_filters()`, `init_filters()`.
- `init_connections()`, `init_run_by_dmeventd()`.
- `process_profilable_config()`, `config_files_changed()`.
- `init_lvmcache_orphans()`.
- `get_format_by_name()`.
- `system_id_from_string()`.

## Cross-File Interactions
Included widely by LVM library and command modules. It includes `cmd_enum.h`, so the generated command enum becomes part of the context contract. `lvmcache.c` consumes configuration and device state from this context, and `cache_segtype/cache.c` receives it during segment type registration and activation feature checks.

## Risks
`cmd_context` is broad shared state with many bitfields and subsystem pointers. Adding fields or changing initialization assumptions requires coordinated updates in `create_toolcontext()`, `refresh_toolcontext()`, and `destroy_toolcontext()`. Since many subsystems cache pointers into memory pools or config trees owned here, lifetime and refresh ordering are the main hazards.
