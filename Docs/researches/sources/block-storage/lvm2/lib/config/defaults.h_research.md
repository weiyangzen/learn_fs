# File Research: sources/block-storage/lvm2/lib/config/defaults.h

## Purpose

`defaults.h` defines many built-in default constants used by the LVM2 config catalog and runtime config code. It centralizes defaults for metadata backup/archive, device scanning, locking, activation, thin/cache/VDO pools, reporting, dmeventd integration, metadata layout, and local runtime directories.

`config_settings.h` includes this file and references these macros in `cfg()` declarations.

## Default Groups

### Metadata Placement and Backup

Defines default first physical extent placement at 1 MiB, backup/archive enablement, metadata validation mode, archive retention count/days, default metadata copies, label sector, default extent size, and metadata ignore behavior.

The first PE constants are expressed both in 512-byte sectors and MiB.

### Device Discovery and Safety

Defaults include:
- `/dev` as the device directory;
- no system ID source by default;
- udev device-list discovery disabled by default;
- no external device info source;
- sysfs scan enabled;
- MD component detection enabled;
- firmware RAID detection disabled;
- multipath component detection enabled;
- ignore LVM mirror LVs enabled;
- suspended device ignore disabled;
- restorefile-with-UUID required;
- data alignment and offset detection enabled;
- discards disabled;
- minimum PV size of 2048 KiB;
- duplicate PV changes disabled;
- hints enabled as `"all"`;
- devices file name `system.devices`;
- devname search mode `"all"`;
- multipath wwids file path;
- device IDs refresh interval/control default.

These defaults favor conservative scanning and protection against unsafe duplicate or layered-device use.

### Locking and Shared Storage

Defaults cover cluster locking library name, fallback behavior for local/cluster locking, wait-for-locks, lvmlockd retries, write-lock priority, sanlock LV extension size, sanlock alignment size, and read-only metadata mode.

### Activation and Device Mapper

Defines defaults for:
- activation depending on `DEVMAPPER_SUPPORT`;
- udev rules and sync;
- DBus notification;
- deactivation retries;
- activation checks;
- reserved memory/stack and process priority;
- linear target use;
- missing stripe filler;
- RAID region size;
- polling interval;
- activation skip;
- activation mode (`degraded`);
- snapshot/thin/VDO autoextend thresholds and percentages.

### Mirror, RAID, Thin, Cache, VDO

Mirror and RAID defaults include mirror log type, mirror/RAID fault policies, maximum image counts, and dmeventd libraries.

Thin defaults include:
- thin check options depending on `THIN_CHECK_NEEDS_CHECK`;
- repair/restore option defaults;
- metadata placement/cropping;
- max/min/optimal metadata sizes;
- chunk size policy and chunk sizes;
- discards mode;
- zeroing;
- pool metadata spare and zero metadata.

Cache defaults include:
- cache check options depending on `CACHE_CHECK_NEEDS_CHECK`;
- repair/restore option defaults;
- metadata placement;
- chunk size and max chunks;
- metadata size limits;
- cache policy, metadata format, and mode.

VDO defaults include compression, deduplication, metadata hints, IO size, block map cache, era length, sparse index, checkpoint frequency, index memory, slab size, thread counts, write policy, max discard, vdoformat options, and pool header reservation size.

### External Tools and Paths

Defines defaults for:
- dmeventd path depending on `DMEVENTD_PATH`;
- fsadm path;
- lvresize filesystem helper path;
- run-time directories for online PV/VG tracking and import state.

Tool command macros themselves are supplied elsewhere and referenced by `config_settings.h`.

### Logging and Reporting

Defaults include:
- umask;
- format name;
- syslog/log levels;
- command log reporting;
- units and suffix behavior;
- hosttags;
- report formatting controls;
- default report columns and sort keys for LVs, VGs, PVs, segments, PV segments, device types, and full reports;
- default time format;
- command log selection.

### Miscellaneous

Defines defaults for command argument limits, max shell history, async I/O, unknown device name, cache file prefix, search/import paths, device sysfs directory, devices-file backup limit, and IO memory size.

## Conditional Defaults

Several defaults depend on compile-time macros:
- `DEFAULT_DMEVENTD_PATH` depends on `DMEVENTD_PATH`.
- thin/cache check option lists depend on whether the check tool needs the `--clear-needs-check-flag` option.
- `DEFAULT_ACTIVATION` depends on `DEVMAPPER_SUPPORT`.
- `DEFAULT_LOG_FACILITY` and `DEFAULT_SI_UNIT_CONSISTENCY` can be supplied externally.

## Dependencies

This file assumes numerous macros and constants are available from broader LVM/device-mapper headers or build configuration, including:
- device-mapper thin/cache/VDO limits;
- command paths such as `FSADM_PATH`;
- run directory macros;
- allocation and cache metadata constants;
- segment type and feature defaults used elsewhere.

## Risk and Maintenance Notes

- Defaults in this file are user-visible through generated `lvm.conf` output and materially affect storage behavior.
- Defaults for discard, duplicate PV handling, component detection, activation mode, and metadata sizing have direct data-safety implications.
- Conditional defaults must remain aligned with external helper tool versions and kernel/device-mapper behavior.
- Some macros represent KiB, MiB, sectors, bytes, counts, or percentages; unit mistakes would propagate into generated config defaults.
