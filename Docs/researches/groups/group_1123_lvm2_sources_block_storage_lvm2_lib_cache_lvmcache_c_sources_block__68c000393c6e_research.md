# Group Research: group_1123_lvm2_sources_block_storage_lvm2_lib_cache_lvmcache_c_sources_block__68c000393c6e

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/cache/lvmcache.c -->
# File Research: sources/block-storage/lvm2/lib/cache/lvmcache.c

## Summary
Implements LVM2's in-memory scan cache for physical volumes, volume groups, labels, metadata areas, device identity, duplicate PV detection, and stale metadata tracking. It is populated mainly by label scanning, then corrected by full `vg_read()` metadata processing.

## Main Responsibilities
- Maintain global lookup tables from PVID, VGID, and VG name to cached `lvmcache_info` and `lvmcache_vginfo` records.
- Track one cached PV/device record per selected device, including label, format, device size, metadata/data/bootloader areas, bad MDAs, and scan-time metadata sequence information.
- Track one cached VG record per discovered VG, including VG name, VGID, format, status, system ID, lock type, creation host, latest scan checksum/size/seqno, summary mismatch flags, PV summaries, active infos, and outdated infos.
- Populate cache state through `lvmcache_label_scan()` and targeted VG rescans.
- Resolve duplicate devices that expose the same PVID, preferring multipath or MD aggregate devices when duplicates are merely components, and otherwise using device ID, active LV use, device size, previous device hint, mounted filesystem, DM/subsystem status, or first-seen order.
- Correct scan-time inaccuracies after full metadata read, especially PVs without metadata areas and PVs that still contain old VG metadata after removal.
- Preserve and expose bad, missing, outdated, and mismatched metadata areas for repair paths.
- Provide device-filter diagnostic text used when a requested device cannot be used.

## Key State
- `_pvid_hash`: maps PVID strings to selected `lvmcache_info`.
- `_vgid_hash`: maps VGID strings to `lvmcache_vginfo`.
- `_vgname_hash`: maps VG names when name lookup is unambiguous.
- `_vginfos`: master list of VG records, including orphan VG records.
- `_initial_duplicates`: duplicate devices found during the current label scan but not initially inserted into `_pvid_hash`.
- `_unused_duplicates`: duplicate devices not selected for use after duplicate resolution.
- `_found_duplicate_vgnames`: disables simple VG-name lookup when multiple accessible VGs share a name.
- `_outdated_warning`: suppresses repeated outdated-metadata repair hints.

## Important Control Flow
`lvmcache_init()` creates the hash tables and list heads. `lvmcache_add()` is called by label scanning when a label/PVID is discovered. It either creates an info record or detects an existing PVID on another device and saves that device in `_initial_duplicates`.

`lvmcache_label_scan()` clears duplicate lists, runs `label_scan()`, optionally scans extra devices found through devices-file validation, then calls `_choose_duplicates()` when duplicate PVIDs were seen. Chosen replacements are rescanned into cache, unchosen devices are recorded in `_unused_duplicates`, and warnings explain which device is used.

`_choose_duplicates()` first tries to collapse duplicates that are multipath or MD components. If not component-only, it compares candidate devices by stable identity and runtime evidence: configured device ID, whether a device backs an active LV, PV-summary size match, previous device hint, mounted filesystem, DM/subsystem membership, then first-seen order.

`lvmcache_extra_md_component_checks()` performs extra full MD component checks after label scan only when scan evidence suggests the PV may have been found on an MD component, such as PV/device size mismatch or a `/dev/md*` device hint on a non-MD device.

`lvmcache_update_vgname_and_id()` attaches a PV info to a VG info, creates VG records, handles duplicate VGIDs/names, tracks local versus foreign duplicate VG names, updates VG status/system ID/lock type, and records scan seqno/checksum mismatches across MDAs and devices.

`lvmcache_update_vg_from_read()` reconciles scan-time VG membership with the fully parsed VG metadata. It moves removed/stale PVs to `outdated_infos`, attaches no-MDA PVs to the correct VG, detects PVs claiming membership in a different VG, and copies ignored MDAs into the format instance when needed.

## Key Interfaces
- Cache lifecycle: `lvmcache_init()`, `lvmcache_destroy()`.
- Scan entry points: `lvmcache_label_scan()`, `lvmcache_label_rescan_vg()`, `lvmcache_label_rescan_vg_rw()`, `lvmcache_label_reopen_vg_rw()`.
- Device/VG mutation: `lvmcache_add()`, `lvmcache_del()`, `lvmcache_del_dev()`, `lvmcache_update_vgname_and_id()`, `lvmcache_update_vg_from_read()`.
- Lookup APIs: `lvmcache_info_from_pvid()`, `lvmcache_info_from_pv_id()`, `lvmcache_vginfo_from_vgname()`, `lvmcache_vginfo_from_vgid()`, `lvmcache_device_from_pv_id()`.
- Metadata area APIs: `lvmcache_add_mda()`, `lvmcache_get_mdas()`, `lvmcache_get_bad_mdas()`, `lvmcache_get_outdated_mdas()`, `lvmcache_fid_add_mdas_vg()`.
- Duplicate/stale checks: `lvmcache_has_duplicate_devs()`, `lvmcache_dev_is_unused_duplicate()`, `vg_has_duplicate_pvs()`, `lvmcache_has_old_metadata()`, `lvmcache_scan_mismatch()`, `lvmcache_verify_info_in_vg()`.

## Cross-File Interactions
This file sits between label scanning, device filtering, metadata parsing, and command processing. It depends on label and text-format code for labels and MDAs, device-cache and device-id code for device identity, filter code for wiping rejected component devices, metadata code for PV/VG structures, and `toolcontext` for configuration and device-type state.

## Risks
The highest-risk logic is duplicate PVID resolution, because selecting the wrong device can cause commands to operate on a clone, component path, or stale copy. Stale metadata handling is also delicate: equal seqnos with different checksums, old MDAs, no-MDA PVs, and PVs moved between VGs all require conservative behavior. The file uses global mutable state and manual list/hash ownership, so missed detach/free paths can leave stale pointers or inconsistent lookups.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/cache/lvmcache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/cache/lvmcache.h -->
# File Research: sources/block-storage/lvm2/lib/cache/lvmcache.h

## Summary
Declares the public LVM cache API and the scan-time `lvmcache_vgsummary` structure used to pass lightweight VG metadata from label scanning into cache state.

## Main Responsibilities
- Define orphan VG naming macros.
- Forward-declare core LVM types used by the cache.
- Define `struct lvmcache_vgsummary`, containing VG name, VGID, status, creation host, system ID, lock type, seqno, MDA checksum/size, MDA number, mismatch flags, and PV summaries.
- Expose cache lifecycle, scan, lookup, update, metadata-area, duplicate-device, stale-metadata, bad-MDA, and diagnostic APIs.

## Key Interfaces
- Lifecycle and scan: `lvmcache_init()`, `lvmcache_destroy()`, `lvmcache_label_scan()`, VG rescan/reopen helpers.
- Cache update: `lvmcache_add()`, `lvmcache_add_orphan_vginfo()`, `lvmcache_update_vgname_and_id()`, `lvmcache_update_vg_from_read()`.
- Lookup: PVID, PV ID, VGID, VG name, cached label, cached device, format, device size, VG/PV name lengths.
- Format-instance integration: `lvmcache_fid_add_mdas()`, `lvmcache_fid_add_mdas_pv()`, `lvmcache_fid_add_mdas_vg()`.
- Duplicate and outdated handling: `lvmcache_has_duplicate_devs()`, `lvmcache_get_unused_duplicates()`, `lvmcache_has_duplicate_local_vgname()`, `lvmcache_get_outdated_devs()`, `lvmcache_del_outdated_devs()`.
- Metadata repair support: `lvmcache_has_old_metadata()`, `lvmcache_get_bad_mdas()`, `lvmcache_get_dev_mda()`.

## Important Behavior
The header intentionally hides `struct lvmcache_info` internals while exposing accessors and iterators. `valid_only` is present in lookup signatures, but the implementation currently does not make it a strong validity filter. `lvmcache_vgsummary` is explicitly scan-time summary data rather than authoritative full VG metadata.

## Cross-File Interactions
Used by label scanners, text-format metadata readers/writers, command processing, repair commands, device-id handling, and tool context initialization. `toolcontext.c` initializes orphan cache entries through this API.

## Risks
Because this is a broad internal API, changes to ownership expectations for returned labels, MDAs, or device lists affect many callers. The scan summary structure must stay aligned with text-format scan behavior; otherwise cache mismatch and repair logic can make incorrect decisions.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/cache/lvmcache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/cache_segtype/cache.c -->
# File Research: sources/block-storage/lvm2/lib/cache_segtype/cache.c

## Summary
Implements LVM2 segment type support for device-mapper cache pools and cache LVs. It imports and exports cache-related metadata, detects kernel target capabilities, builds DM target lines for cache pool and cachevol layouts, and registers the `cache_pool` and `cache` segment types.

## Main Responsibilities
- Display cache chunk size, metadata format, cache mode, policy name, and policy settings.
- Fill missing defaults for older metadata: policy `mq`, metadata format 1, and writethrough mode.
- Import/export cache settings from text metadata: `chunk_size`, `cache_mode`, `policy`, and `policy_settings`.
- Import/export cache pool segments with separate data and metadata LVs.
- Import/export cache segments that attach an origin LV to either a cache pool or a cachevol.
- Handle cachevol metadata/data ranges, optional metadata/data IDs, and metadata format 2.
- Detect the `cache` DM target and optional features such as metadata2, MQ policy, and SMQ policy.
- Apply `global/cache_disabled_features` as a runtime feature mask.
- Build activation target lines using `dm_tree_node_add_cache_target()` or `dm_tree_node_add_cachevol_target()`.
- Register `SEG_TYPE_NAME_CACHE_POOL` and `SEG_TYPE_NAME_CACHE`.

## Key Interfaces
- Segment handlers: `_cache_pool_ops` and `_cache_ops`.
- Text import/export: `_cache_pool_text_import()`, `_cache_pool_text_export()`, `_cache_text_import()`, `_cache_text_export()`.
- Activation support under `DEVMAPPER_SUPPORT`: `_target_present()`, `_modules_needed()`, `_cache_add_target_line()`.
- Registration entry point: `init_cache_segtypes()`.

## Important Control Flow
Cache pool import resolves `data` and `metadata` LV names, reads optional `metadata_format`, imports shared settings, attaches pool data and metadata LVs, and fixes defaults if the pool is already used.

Cache LV import resolves `cache_pool` and `origin`, attaches the origin as area 0, reads optional cleaner mode and cache settings, reads metadata format/ranges for cachevols, marks cachevol pools, fixes old pool defaults for non-cachevol pools, then attaches the pool LV.

Activation selects settings from the cache segment for cachevols or the pool segment for classic cache pools. Cleaner mode forces writethrough. Metadata format 2 requires kernel feature support. Policy settings are filtered for known MQ/SMQ accepted keys, with unsupported settings warned and removed from a cloned config node before target construction.

Classic cache pools use separate metadata and data UUIDs from the pool segment. Cachevols build synthetic `cmeta` and `cdata` UUIDs from either stored IDs or the cachevol LV ID and pass explicit metadata/data ranges to the cachevol target.

## Cross-File Interactions
This file depends on metadata segment helpers for attaching LVs, config parsing/export helpers for text metadata, activation code for DM target construction, module/target detection helpers, and `toolcontext.c` registration through `_init_segtypes()` when `CACHE_INTERNAL` is enabled.

## Risks
Activation behavior depends on kernel target version, optional policy modules, and config-disabled features. Metadata import must preserve backward compatibility with older cache metadata that lacks explicit policy/mode/format. Cachevol range and UUID handling is sensitive: invalid ranges or unstable IDs can build incorrect DM devices. Policy setting filtering must stay aligned with kernel policy support.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/cache_segtype/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/commands/cmd_enum.h -->
# File Research: sources/block-storage/lvm2/lib/commands/cmd_enum.h

## Summary
Generates an enum of LVM command identifiers by including the generated `cmds.h` table with a local `cmd(a, b)` macro expansion.

## Main Responsibilities
- Wrap generated command definitions in an enum.
- Convert each `cmd(foo_CMD, foo)` entry from `cmds.h` into a unique enum constant `foo_CMD`.
- Provide an include guard for command enum consumers.

## Key Interfaces
- The enum is unnamed and populated from `cmds.h`.
- `cmd_enum.h` is included by `toolcontext.h`, where `cmd_context.command_enum` stores the selected command identifier.

## Cross-File Interactions
Depends on build-generated `cmds.h`, itself derived from command definitions. Command parsing and library code use these enum values to branch on specific command behavior without string comparisons.

## Risks
The file is small but build-order sensitive: `cmds.h` must exist and must use the expected `cmd(a, b)` form. Any macro name change in the generated command table breaks enum generation.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/commands/cmd_enum.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/commands/toolcontext.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/commands/toolcontext.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/commands/toolcontext.h -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/commands/toolcontext.h -->