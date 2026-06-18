# File Research: sources/block-storage/lvm2/lib/commands/toolcontext.c

## Summary
Constructs, refreshes, and destroys the central LVM2 `cmd_context`. This file wires together configuration, logging, system identity, device cache, filters, formats, segment types, lvmcache, backup/archive state, lvmpolld connection state, memory pools, stream buffering, and runtime defaults used by commands.

## Main Responsibilities
- Sanitize and resolve local system IDs from `uname`, `lvmlocal`, machine-id files, systemd app-specific machine ID, or a configured file.
- Read environment overrides such as `LVM_SYSTEM_DIR`, `LVM_RUN_BY_DMEVENTD`, `DM_DISABLE_UDEV`, and `LVM_LVMPOLLD_SOCKET`.
- Detect proc/sysfs paths and configure libdevmapper paths and UUID prefix.
- Initialize logging, syslog, debug classes, output fields, journal logging, verbosity, silent mode, test mode, and log files.
- Validate loaded configuration trees when configured to do so.
- Process profilable settings such as display units, SI consistency, report formatting, and time format validation.
- Process core configuration: umask, device directory, external device info source, activation defaults, udev behavior, discards, read-ahead, metadata validation, PV minimum size, system ID, device ID refresh checks, and I/O memory size.
- Load `lvm.conf`, `lvmlocal.conf`, tag-specific config files, and profiles, then merge them into the command config cascade.
- Initialize host tags and config tags with optional host filters.
- Initialize the device cache and device scan directories.
- Build the device filter chain and wrap it in a persistent filter.
- Register metadata formats and segment types.
- Initialize lvmcache and add orphan VG cache entries for known formats.
- Initialize metadata backup/archive directories and random seed.
- Provide full refresh and teardown paths that keep command-line config/profile state where needed.

## Important Control Flow
`create_toolcontext()` allocates the command context, sets locale and stream buffering, reads environment settings, creates memory pools, loads config files, initializes logging and hostname, loads tags and local/tag configs, merges config, processes configuration, initializes profiles, device types, AIO, device cache, devices file, memlock, formats, lvmcache, orphan cache entries, segment types, backups, random seed, global defaults, optional connections, optional filters, and finally marks configuration initialized.

`refresh_toolcontext()` tears down activation, hints, lvmcache, label scanning, segment types, formats, device cache, device types, tags, and config, while preserving command-line config and global profile names. It then reloads configuration and recreates the same major subsystems, refreshes connections and filters, and resets LVM errno.

`destroy_toolcontext()` shuts down archive/backup, hints, lvmcache, label scanning, labels, segment types, formats, filters, device cache, device types, tags, command-line config, config definition hashes, stream buffering, memory pools, lvmpolld, activation, logging, syslog, and errno state.

`init_filters()` creates the configured filter pipeline: global regex, regex, type, device-id, optional sysfs, usable, optional multipath component, partitioned, signature, optional MD component, optional firmware RAID, then wraps that composite in a persistent filter.

`_init_segtypes()` registers built-in linear/striped/zero/error types and conditionally compiled RAID, thin, cache, VDO, writecache, and integrity segment types.

## Key Interfaces
- Context lifecycle: `create_toolcontext()`, `refresh_toolcontext()`, `destroy_toolcontext()`, `destroy_config_context()`.
- Config/runtime refresh: `process_profilable_config()`, `config_files_changed()`.
- Filters/connections: `init_filters()`, `refresh_filters()`, `init_connections()`, `init_run_by_dmeventd()`.
- Format/cache helpers: `get_format_by_name()`, `init_lvmcache_orphans()`.
- System identity: `system_id_from_string()`.

## Cross-File Interactions
This file is the integration hub for most LVM library subsystems. It initializes `lvmcache.c`, registers cache segment types from `cache_segtype/cache.c`, uses command enum fields declared through `cmd_enum.h` and `toolcontext.h`, config infrastructure, dev-cache/dev-type/device-id code, filters, label scanning, format-text, activation, backup/archive, lvmpolld, memlock, and logging.

## Risks
Initialization order is critical. Filters require connections to be initialized, lvmcache requires formats and orphan VG entries, device filters depend on config and dev types, and refresh must drop stale scan/cache state before rebuilding. Environment overrides can intentionally bypass config, especially udev and system directory behavior. The refresh path preserves some command-line/profile state while rebuilding many global subsystems, so partial refresh failures can leave inconsistent state if callers do not abort.
