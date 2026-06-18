# File Research: sources/block-storage/lvm2/lib/config/config_settings.h

## Purpose

`config_settings.h` is the declarative configuration catalog for LVM2. It is not a normal standalone header; it is intentionally included multiple times with different macro definitions to generate config IDs, definition tables, defaults, comments, version metadata, validation rules, and config output.

It defines the complete schema for LVM configuration sections and settings under root sections such as `config`, `devices`, `allocation`, `log`, `backup`, `shell`, `global`, `activation`, `metadata`, `report`, `dmeventd`, `tags`, and `local`.

## Macro Contract

The file documents and uses five macro forms:

- `cfg_section(id, name, parent, flags, since_version, deprecated_since_version, deprecation_comment, comment)`
- `cfg(id, name, parent, flags, type, default_value, since_version, unconfigured_default_value, deprecated_since_version, deprecation_comment, comment)`
- `cfg_array(id, name, parent, flags, types, default_value, since_version, unconfigured_default_value, deprecated_since_version, deprecation_comment, comment)`
- `cfg_runtime(id, name, parent, flags, type, since_version, deprecated_since_version, deprecation_comment, comment)`
- `cfg_array_runtime(...)`

Runtime entries require `get_default_<id>()` helpers declared in `config.h` and implemented in `config.c`.

Array defaults use compact encoded strings such as `#S/dev` or `#Sfd#I16`, where the character after `#` identifies the value type.

## Preambles

The file defines:
- `CFG_PREAMBLE_GENERAL`: text for generated `lvm.conf` examples.
- `CFG_PREAMBLE_LOCAL`: text for generated `lvmlocal.conf` examples.

These are consumed by `config_write()` when requested through `struct config_def_tree_spec`.

## Top-Level Sections

The catalog declares the root and major sections:

- `config`: validation and profile directory behavior.
- `devices`: block device discovery, filtering, IDs, hints, alignment, duplicate PV safety, and discard behavior.
- `allocation`: LV allocation policy, thin/cache/VDO defaults, metadata/data placement, and pool sizing.
- `log`: logging, syslog, command-log reports, debug classes, journal integration.
- `backup`: metadata backup/archive retention and directories.
- `shell`: shell history settings.
- `global`: command-wide behavior, locking, external tools, system IDs, eventing, helpers, and core defaults.
- `activation`: device-mapper activation behavior, udev integration, degraded/partial activation policy, monitoring, autoextend, and lock activation lists.
- `metadata`: metadata consistency, PV/VG metadata copies, metadata area sizing, and history retention.
- `report`: report formatting, columns, sorting, JSON/basic output, fullreport defaults.
- `dmeventd`: monitoring libraries and commands for mirror, RAID, snapshot, thin, and VDO.
- `tags`: host tag creation and variable tag subsections.
- `local`: host-specific identity, PR key, extra system IDs, and sanlock host ID.

## Major Settings by Area

### Config

Defines `config/checks`, `config/validate_metadata`, `config/abort_on_errors`, and runtime `config/profile_dir`. These settings control whether config mismatches are reported, whether metadata transforms are validated, and where profiles are loaded from.

### Devices

Covers the largest block-storage-facing surface:
- device node directory and sysfs path;
- scan directories;
- udev-based device list discovery;
- external device info source;
- device hints;
- preferred names;
- system devices file usage, backup limit, devname search, and ID refresh;
- filters and global filters;
- legacy persistent cache settings;
- acceptable device types;
- sysfs scan;
- scanning LVs as PVs;
- multipath, MD, and firmware RAID component detection;
- data alignment and alignment-offset detection;
- ignoring suspended devices and LVM mirror LVs;
- restorefile requirements;
- PV minimum size;
- discard issuance;
- duplicate PV safety;
- mixed logical block size handling.

These settings are central to avoiding accidental use of wrong block devices.

### Allocation

Defines placement and default construction policy for LVs:
- cling tag lists and cling behavior;
- signature wiping behavior;
- mirror log PV separation;
- RAID striping defaults;
- cache pool metadata placement, cache mode, metadata format, policy, policy settings, chunk size, and max chunks;
- pvmove max segment size;
- thin pool metadata placement, metadata cropping compatibility, zeroing, discards, chunk-size policy, zero metadata, and runtime thin chunk size;
- default VG extent size;
- extensive VDO creation defaults, including compression, deduplication, metadata hints, IO size, block-map cache, slab size, thread counts, write policy, discard sizing, and pool header size.

Many allocation settings are marked profilable, and some are metadata-profilable, allowing behavior to be attached to VG/LV metadata.

### Log and Backup

`log` settings define command log reporting, sort/columns/selection, verbosity, silence, syslog, file logging, journal fields, prefixes, activation logging, debug classes, and debug output/file fields.

`backup` settings control metadata backup/archive enablement, runtime directory defaults, minimum archive count, and retention days.

### Global

`global` covers broad command behavior:
- umask, test mode, unit display, suffixes, activation enablement;
- proc/etc locations;
- legacy/deprecated locking controls;
- file locking directory and prioritization;
- internal error handling;
- metadata read-only mode;
- segment type defaults for mirror, raid10, and sparse LVs;
- event activation, async I/O, lvmlockd, sanlock, and lvmpolld;
- external helper commands for thin, cache, VDO, fsadm, and filesystem resize operations;
- disabled feature lists for thin/cache/VDO;
- system ID source and file;
- DBus notification;
- IO memory size.

Several legacy settings are retained with deprecation versions to keep old configs parseable while generated output can mark them deprecated.

### Activation

Activation settings control interaction with device-mapper and system services:
- internal activation checks;
- udev sync/rules/verification;
- retry deactivation;
- missing stripe filler;
- linear target preference;
- reserved stack/memory and process priority during suspension;
- volume lists, autoactivation lists, read-only lists;
- RAID/mirror region size and fault policies;
- thin full behavior;
- readahead;
- snapshot, thin pool, and VDO pool autoextend thresholds/percents;
- mlock filtering;
- monitoring and polling;
- activation skip defaults;
- activation mode (`complete`, `degraded`, `partial`);
- lock start lists.

### Metadata

Metadata settings include PV device size checks, removed-LV history retention, PV/VG metadata copy counts, runtime PV metadata size, metadata ignore defaults, stripesize, legacy metadata dirs/disk areas, and deprecated disk-area subsections.

### Report

Report settings define the output behavior of `lvs`, `vgs`, `pvs`, segment reports, device type reports, and fullreport:
- basic/json/json_std format;
- compact output;
- alignment, buffering, headings, separators, prefixes, quoting;
- binary numeric output;
- time format;
- default columns and sort fields for normal, verbose, and full report modes;
- hidden/unknown device display.

### Dmeventd, Tags, Local

`dmeventd` settings define monitor libraries and extension commands for mirror, RAID, snapshot, thin, and VDO pools.

`tags` supports host tags and variable tag subsections with `host_list`.

`local` stores settings that should not be shared between hosts: local system ID, persistent reservation key, extra system IDs, and sanlock host ID.

## Versioning and Deprecation

Every entry has a `since_version` encoded with `vsn()`. Deprecated entries also set `deprecated_since_version` and may provide a replacement comment. `config.c` uses this metadata for generated config output, filtering by version, and marking deprecated settings.

## Profile Eligibility

Flags such as `CFG_PROFILABLE` and `CFG_PROFILABLE_METADATA` define which settings can appear in command profiles or metadata profiles. `config.c` enforces these rules strictly when profiles are loaded.

This file is therefore both user documentation and an enforcement source for profile safety.

## Dependencies

The file includes `defaults.h` and also references macros supplied elsewhere by the build/config environment and other LVM headers, such as tool paths, compile-time feature defaults, segment type defaults, and device-mapper/VDO constants.

## Risk and Maintenance Notes

- This file is schema, documentation, and code-generation input at once; small macro argument mistakes can alter runtime behavior, generated documentation, and validation simultaneously.
- IDs are order-dependent. Moving entries changes enum values unless all users are rebuilt consistently.
- Runtime entries require matching helper functions. Missing helpers will break compilation through macro expansion.
- The difference between `CFG_DEFAULT_UNDEFINED` and `CFG_DEFAULT_COMMENTED` affects both generated config and upgrade behavior.
- Profile flags should be reviewed carefully for any new setting because they determine whether profiles can change runtime/storage behavior.
- Device filtering, duplicate PV handling, activation mode, discard issuance, metadata sizing, and external repair/check helper paths are high-impact settings with direct storage safety implications.
