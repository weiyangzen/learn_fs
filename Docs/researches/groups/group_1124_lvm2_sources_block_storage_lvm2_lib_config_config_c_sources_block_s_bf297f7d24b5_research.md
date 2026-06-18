# Group Research: LVM2 Config Core (`sources/block-storage/lvm2/lib/config`)

Scope confirmed from `Docs/research_subset_a.md`: `sources/block-storage/lvm2` is included in subset A. All four listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/config/config.c -->
# File Research: sources/block-storage/lvm2/lib/config/config.c

## Purpose

Implements LVM2's configuration subsystem: config tree creation, file/device/string/profile loading, validation against the declarative schema, cascaded override lookup, config tree merging, generated config output, and runtime-computed defaults.

## Main Responsibilities

- Builds `_cfg_def_items[]` by including `config_settings.h` with macros that expand the schema into runtime definition records.
- Tracks config source metadata with `struct config_source` and file metadata with `struct config_file`.
- Loads config from regular files, special files, profile files, command-line strings, and device metadata buffers.
- Maintains config cascade precedence:

`CONFIG_STRING -> CONFIG_PROFILE_COMMAND -> CONFIG_PROFILE_METADATA -> CONFIG_FILE/CONFIG_MERGED_FILES`

- Validates parsed config trees against known section/setting definitions, types, profile eligibility, and context restrictions.
- Provides typed lookup APIs for strings, integers, floats, booleans, arrays, and nodes.
- Generates default/current/full/missing/new/profilable/diff/list config trees.
- Writes config trees with optional comments, summaries, version metadata, preambles, list mode, and values-only mode.
- Implements runtime defaults for paths, pool chunk sizes, VDO metadata hints, mirror policy, cache max chunks, and PV metadata size.

## Important Control Flow

`config_open()` creates a `dm_config_tree`, allocates custom source metadata, and prepares file metadata for file/profile/special-file sources.

`config_file_check()` validates a config file as a regular file, records ctime and size, and treats an empty file as valid but with no file content to parse.

`config_file_changed()` compares stored timestamp and size with current `stat()` results to decide whether a file-backed config should be reloaded.

`config_file_open_and_read()` opens a config tree and loads a file when present. Missing non-profile config files are tolerated; missing profile files fail.

`config_file_read_fd()` is the low-level reader for both regular config files and metadata areas on devices. It supports regular reads, device reads, split/circular metadata buffers, checksum validation, invalid metadata-name rejection on block devices, checksum-only mode, duplicate-node-check bypass, and optional parsing of only the `physical_volumes` section.

`override_config_tree_from_string()` and `override_config_tree_from_profile()` insert override trees into the cascade at the correct precedence point.

`config_def_check()` validates an entire config tree. It builds a hash of full schema paths, substitutes `#` for variable-name sections, rejects unknown settings/sections, checks scalar and array value types, rejects invalid profile content, marks used/valid/diff status, and enforces disallowed flags such as `CFG_DISALLOW_INTERACTIVE`.

`config_force_check()` creates a temporary validation handle and forces checks even when `config/checks` is disabled, suppressing messages when normal checks are disabled.

`merge_config_tree()` destructively merges one tree into another. Raw merge replaces values; tag-aware merge skips top-level `tags`, applies host-tag selection, strips tag subsections, and merges selected value lists such as `activation/volume_list`, `devices/filter`, and `devices/types`.

`config_def_create_tree()` builds generated config trees from the schema and current config/check state. For `CFG_DEF_TREE_FULL`, it creates defaults and then merges current config over them.

`config_write()` emits the tree to stdout or a file with callbacks that add comments, preambles, version strings, deprecation notices, default-commenting behavior, list output, value-only output, and diff filtering.

## Validation Details

The validator checks:

- top-level entries must be sections;
- known schema paths, including variable section names;
- scalar versus section misuse;
- array versus scalar misuse;
- bools represented as native ints or recognized strings;
- empty values only where `CFG_ALLOW_EMPTY` is set;
- profile content only where `CFG_PROFILABLE` or `CFG_PROFILABLE_METADATA` permits it;
- command-profile versus metadata-profile restrictions;
- context-specific disallowed flags;
- default differences when requested.

`_check_value_differs_from_default()` compares configured values with static or runtime defaults and marks the full parent path with `CFG_DIFF`.

## Lookup Behavior

The typed lookup helpers resolve the schema item, construct its path, optionally apply a local profile, start from the static or runtime default, consult the active cascaded tree, then remove any temporarily inserted profile.

Disabled settings marked `CFG_DISABLED` warn when explicitly present and return defaults.

Array defaults are decoded from compact strings such as `#S/dev#I16` by `_get_def_array_values()`.

## Runtime Defaults

Runtime default helpers include:

- `devices/cache_dir` and `devices/cache` based on `cmd->system_dir`;
- backup, archive, and profile directories;
- mirror image fault policy inherited from mirror device fault policy;
- thin pool chunk size from allocation helper logic;
- cache pool chunk size and max chunks;
- VDO metadata hints default disabled for kernels newer than 6.8;
- PV metadata size from metadata defaults.

## Dependencies

Uses libdevmapper config APIs, LVM device abstractions, command context state, metadata helpers, profile state, logging, memory pools, device I/O, CRC/checksum helpers, and definitions from `config_settings.h`.

## Risk and Maintenance Notes

- Config cascade ordering is a core behavior invariant.
- Profile validation is intentionally strict; relaxing it could make profiles alter unsupported settings.
- The schema table is generated by macro inclusion, so macro signature or ordering changes affect IDs, defaults, validation, and generated output.
- `CFG_PATH_MAX_LEN` bounds path construction.
- Array default encoding is compact and fragile; malformed internal defaults are treated as internal errors.
- Runtime defaults may call config lookup helpers, so dependency cycles should be avoided.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/config/config.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/config/config.h -->
# File Research: sources/block-storage/lvm2/lib/config/config.h

## Purpose

Public interface and shared type definitions for LVM2 configuration handling. It defines config source kinds, profiles, schema item metadata, validation flags, generated-tree modes, validation handles, merge modes, accessors, loaders, writers, and runtime default hooks.

## Key Types

`config_source_t` identifies config origins: undefined, single file, merged files, command-line string, command profile, metadata profile, and special-purpose file.

`struct profile` stores a profile list node, source type, name, and loaded config tree.

`struct profile_params` stores profile directory, global command/metadata profiles, pending profiles, loaded profiles, and shell profile state.

`cfg_def_type_t` describes accepted schema value types: section, array, boolean, integer, float, and string.

`cfg_def_value_t` and `cfg_def_unconfigured_value_t` store either static defaults or runtime-default function pointers.

`cfg_def_item_t` is the per-setting schema record: ID, parent ID, name, type mask, flags, version metadata, default values, deprecation comment, help comment, and file preamble.

`cfg_def_tree_t` describes generated output modes: current, missing, full, default, new, new-since, profilable, command-profilable, metadata-profilable, diff, and list.

`struct config_def_tree_spec` parameterizes generated tree/output creation with command context, current tree, version filters, comment options, local-section filtering, list/value-only modes, and validation status.

`struct cft_check_handle` stores validation context and per-schema-item status bits.

## Flags and Status

Schema flags define behavior including variable names, empty value allowance, advanced/unsupported visibility, profile eligibility, metadata-profile eligibility, undefined/commented/runtime defaults, disabled settings, octal integer formatting, subtree validation bypass, and interactive-mode disallowance.

Validation status flags:

- `CFG_USED`: item appeared in the checked tree.
- `CFG_VALID`: item was valid.
- `CFG_DIFF`: item differs from default.

`CFG_PROFILABLE_METADATA` intentionally includes `CFG_PROFILABLE`; validation logic depends on this bit composition.

## Generated IDs

The enum of config IDs is generated by including `config_settings.h` with local macros that emit only IDs. `CFG_COUNT` is the sentinel final entry and sizes arrays such as validation status.

This makes declaration order in `config_settings.h` important for every table indexed by config ID.

## Public API Surface

Profile APIs:

- `add_profile()`
- `load_profile()`
- `load_pending_profiles()`

Validation APIs:

- `config_def_get_path()`
- `config_def_check()`
- `config_force_check()`
- `get_config_tree_check_handle()`

Cascade/source APIs:

- `override_config_tree_from_string()`
- `override_config_tree_from_profile()`
- `get_config_tree_by_source()`
- `remove_config_tree_by_source()`
- `config_get_source_type()`

File/tree lifecycle APIs:

- `config_open()`
- `config_file_read_fd()`
- `config_file_read_from_file()`
- `config_file_open_and_read()`
- `config_write()`
- `config_def_create_tree()`
- `config_destroy()`
- `config_file_timestamp()`
- `config_file_changed()`
- `config_file_check()`

Lookup APIs:

- explicit-tree: `find_config_node()`, `find_config_bool()`;
- cascaded-tree: node, string, allow-empty string, int, int64, float, bool, and array lookup helpers.

Merge API:

- `merge_config_tree()` with raw and tag-aware merge modes.

Runtime default declarations cover cache paths, backup/archive/profile directories, mirror fault policy, thin/cache chunk sizing, cache max chunks, VDO metadata hints, and PV metadata size.

## Dependencies

Depends on libdevmapper config/list/pool types, device abstractions from `device.h`, and generated IDs from `config_settings.h`.

## Risk and Maintenance Notes

- Runtime schema entries require matching `get_default_<id>` helpers unless explicitly defined as `NULL`.
- Path construction depends on `CFG_PATH_MAX_LEN`.
- Profile flags are behavior boundaries; incorrect flags can allow unsafe profile overrides or reject valid profile settings.
- Any change to generated enum order must remain consistent with `_cfg_def_items[]` and validation status indexing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/config/config.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/config/config_settings.h -->
# File Research: sources/block-storage/lvm2/lib/config/config_settings.h

## Purpose

Declarative schema and documentation catalog for LVM2 configuration. This header is intentionally included multiple times with different macro definitions to generate config IDs, definition tables, defaults, comments, version metadata, validation behavior, and generated config output.

It includes `defaults.h` and defines all major LVM config sections and settings.

## Macro Contract

The schema uses:

- `cfg_section(...)` for sections.
- `cfg(...)` for scalar settings.
- `cfg_array(...)` for array settings.
- `cfg_runtime(...)` for scalar settings whose defaults are computed at runtime.
- `cfg_array_runtime(...)` for runtime array defaults.

Each item includes ID, config node name, parent ID, flags, type information, default values, version metadata, deprecation metadata, and help text.

Array defaults use encoded strings where `#S`, `#I`, `#B`, and `#F` identify string, integer, boolean, and float values.

## Preambles

Defines:

- `CFG_PREAMBLE_GENERAL` for generated `lvm.conf` examples.
- `CFG_PREAMBLE_LOCAL` for generated `lvmlocal.conf` examples.

These are consumed by config output code when requested.

## Top-Level Sections

The catalog declares:

- `config`: validation and profile directory behavior.
- `devices`: block device discovery, filtering, IDs, hints, alignment, duplicate-PV safety, and discard behavior.
- `allocation`: LV placement policy plus thin/cache/VDO defaults.
- `log`: logging, syslog, command-log reports, debug classes, journal integration.
- `backup`: metadata backup/archive enablement and retention.
- `shell`: interactive shell history.
- `global`: broad command behavior, locking, helpers, system IDs, eventing, and external tools.
- `activation`: device-mapper activation, udev, monitoring, autoextend, activation lists, and degraded/partial behavior.
- `metadata`: metadata validation, metadata copies, metadata area sizing, and LV history.
- `report`: report formatting, columns, sorting, JSON/basic output, and fullreport defaults.
- `dmeventd`: monitoring libraries and extension commands.
- `tags`: host tags and variable tag subsections.
- `local`: host-specific identity, persistent reservation key, extra system IDs, and sanlock host ID.

## Important Setting Areas

`config` includes checks, metadata validation level, abort-on-errors, and runtime profile directory.

`devices` includes device directory, sysfs override, scan paths, udev discovery, external device info, hints, preferred names, devices-file controls, device-ID refresh, regex filters, global filters, persistent cache legacy settings, acceptable device types, sysfs scan, LV-as-PV scanning, multipath/MD/firmware RAID component detection, alignment controls, suspended-device behavior, mirror-LV scanning behavior, restorefile UUID policy, PV minimum size, discard issuance, duplicate PV safety, and mixed block size allowance.

`allocation` covers cling behavior, wiping, mirror/RAID placement, cache pool metadata/data placement, cache mode/policy/settings/chunk sizing, pvmove segment limits, thin pool defaults, metadata zeroing, physical extent size, and many VDO creation defaults such as compression, deduplication, IO sizing, block-map cache, slab size, thread counts, discard limit, and pool header size.

`log` defines command-log reporting, sort/column/selection defaults, verbosity/silence, syslog, file logging, journal options, prefixes, activation logging, debug classes, and debug output fields.

`backup` defines backup/archive enablement, runtime directories, minimum archive count, and retention days.

`global` covers umask, test mode, units, suffix, activation, proc/etc paths, legacy locking options, file-lock directories, internal-error abort behavior, metadata read-only mode, default segment types, event activation, async I/O, lvmlockd, sanlock, lvmpolld, DBus notification, IO memory size, system ID source/file, and external helper commands for thin/cache/VDO/fsadm/filesystem resize.

`activation` covers activation checks, udev synchronization/rules/verification, retry deactivation, missing stripe filler, linear target preference, memory locking reserves, activation volume lists, autoactivation lists, read-only lists, RAID/mirror region and fault policy, thin full behavior, readahead, snapshot/thin/VDO autoextend, mlock filtering, monitoring, polling, activation skip, activation mode, and lock start lists.

`metadata` includes PV device-size checks, historical LV retention, PV/VG metadata copy counts, runtime PV metadata size, metadata ignore defaults, stripesize, and legacy/deprecated metadata disk-area subsections.

`report` defines default output format, compact output, alignment, buffering, headings, separators, prefixes, quoting, numeric binary output, time format, default sort/column fields for `lvs`, `vgs`, `pvs`, segment reports, device type reports, fullreport, and hidden/unknown device presentation.

`dmeventd`, `tags`, and `local` define monitor libraries/commands, host tag matching, local system ID, persistent reservation key, extra accessible system IDs, and sanlock host ID.

## Versioning, Deprecation, and Profiles

Every entry carries a `since_version` encoded with `vsn()`. Deprecated entries carry `deprecated_since_version` and may carry replacement comments.

Profile flags define which settings may appear in command profiles or metadata profiles. `config.c` enforces these strictly during profile loading.

## Dependencies

References defaults from `defaults.h` plus build/config macros and constants supplied elsewhere, including helper paths, compile-time feature defaults, segment type defaults, device-mapper constants, and VDO limits.

## Risk and Maintenance Notes

- This file is schema, documentation, and code-generation input at once.
- Macro argument mistakes can affect runtime behavior, validation, generated documentation, and output.
- IDs are order-dependent.
- Runtime entries require matching helper implementations.
- `CFG_DEFAULT_UNDEFINED` versus `CFG_DEFAULT_COMMENTED` affects generated config and upgrade behavior.
- Device filters, duplicate-PV policy, activation mode, discard behavior, metadata sizing, and external repair/check helper paths are storage-safety-sensitive.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/config/config_settings.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/config/defaults.h -->
# File Research: sources/block-storage/lvm2/lib/config/defaults.h

## Purpose

Defines built-in default constants used by the LVM2 configuration schema and runtime config code. `config_settings.h` includes this file and references its macros in `cfg()` declarations.

## Default Groups

Metadata and backup defaults include first PE placement at 1 MiB, backup/archive enablement, metadata validation mode, archive retention count/days, PV/VG metadata copy defaults, label sector, extent size, metadata ignore defaults, and metadata history retention.

Device discovery and safety defaults include `/dev` as device directory, no system ID source, udev device-list discovery disabled, no external device info source, sysfs scan enabled, MD component detection enabled, firmware RAID detection disabled, multipath component detection enabled, LVM mirror LV scanning ignored, suspended-device ignore disabled, restorefile-with-UUID required, PV minimum size, duplicate-PV changes disabled, data alignment detection enabled, and discard issuance disabled.

Locking and process defaults include legacy locking library path, lock fallback behavior, wait-for-locks, lvmlockd retries, write-lock prioritization, mlock behavior, metadata read-only default, async I/O default, sanlock extension/alignment defaults, process priority, reserved memory, and reserved stack.

Thin/cache/VDO defaults include check/repair/restore option encodings, metadata placement policies, metadata size bounds, chunk-size policies, cache policy/mode/metadata format, max cache chunks, thin discards/zeroing, VDO compression/deduplication/metadata hints, VDO IO/thread/cache/slab/write/discard defaults, and VDO pool header size.

Activation and monitoring defaults include device-mapper activation default, udev rules/sync/DBus notification, retry deactivation, activation checks, readahead, allocation policy, mirror/RAID fault policy, segment defaults, dmeventd libraries/commands, monitoring, background polling, activation mode, linear target preference, stripe filler, RAID region size, polling interval, and pool autoextend thresholds/percents.

Reporting defaults include command log report settings, units, suffix, SI consistency, verbosity/silence/loglevel/syslog, report output format, column sets, sort keys, separators, headings, quoting, buffering, compact output, time format, and fullreport defaults.

Runtime directory/file defaults include cache file prefix, devices file name, WWIDs file, online PV/VG runtime directories, devices import path, sysfs device ID directory, devices-file backup limit, and device-ID refresh interval.

## Notable Encoding

Array defaults for external helper options use the same compact encoding consumed by config parsing, e.g. `#S<option>` sequences for string arrays.

Several defaults are conditional on compile-time macros, including dmeventd path, log facility, activation support, SI unit consistency, thin/cache check options, and helper command paths.

## Dependencies

Uses constants from surrounding LVM/device-mapper build headers, including command paths, default directories, segment type names, VDO limits, and device-mapper support flags.

## Risk and Maintenance Notes

- These constants are user-visible through generated config and affect command defaults when settings are absent.
- Safety-sensitive defaults include duplicate PV behavior, filters/scanning assumptions, discard issuance, metadata backup/archive, activation mode, component detection, and metadata read-only state.
- Compile-time conditionals can make defaults vary between builds, so generated config and behavior may differ by distribution or feature set.
- Unit conventions matter: many values are in KiB, MiB, sectors, percentages, or counts.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/config/defaults.h -->