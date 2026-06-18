# File Research: sources/block-storage/mdadm/mdadm.h

## Role

`mdadm.h` is the central internal header for mdadm. It establishes compile feature macros, platform defaults, common data structures, metadata-handler contracts, sysfs/ioctl helpers, command entry points, policy APIs, mdmon hooks, cluster hooks, RAID constants, and small utility inlines.

## Major Contents

- Defines runtime paths and service names such as `DEV_DIR`, `DEV_NUM_PREF`, `DEV_MD_DIR`, `MAP_DIR`, `MDMON_DIR`, `FAILED_SLOTS_DIR`, `MDMON_SERVICE`, and `GROW_SERVICE`.
- Includes Linux md headers, common mdadm headers, libc/system headers, and optional Corosync/DLM compatibility shims.
- Defines portable helpers for unaligned access, type-checked `min`/`max`, timer comparisons, byte/sector conversion, fd validation, level checks, safe fd close, `signal_s()`, debug logging, and `xasprintf()`.
- Defines the core `struct mdinfo`, carrying generic array, disk, UUID, name, size, reshape, bitmap/PPL, consistency, sysfs, bad-block, mdmon state, and linked-list device information.
- Defines command/config structures: `createinfo`, `spare_criteria`, `mddev_ident`, `context`, `shape`, `mddev_dev`, `mdstat_ent`, `map_ent`, `dev_policy`, `pol_rule`, `domainlist`, `metadata_update`, `supertype`, and `superswitch`.
- Centralizes command mode enums, special getopt values, update modes, bitmap modes, sysfs read flags, member state mapping, policy actions, RAID level/layout constants, resync sentinel values, and maximum disk limits.

## Metadata Contract

The `struct superswitch` table is the central plugin interface for metadata formats. It covers:

- Metadata examination, export, bad-block inspection, copy, detail, and platform reporting.
- UUID extraction, generic info extraction, homehost matching, and metadata updates.
- Superblock initialization, add/remove/store/write/load/compare/free operations.
- Geometry validation, available-size computation, bitmap placement, PPL validation/write, spare criteria, and drive policy validation.
- Container content enumeration, subarray kill/update, reshape handling, mdmon lifecycle hooks, metadata update processing, spare activation, backup recovery, and bad-block record/clear/list operations.

This contract is used by native metadata, IMSM, DDF, MBR, and GPT handlers and is also the bridge between normal mdadm commands and mdmon.

## Public Surfaces Declared

- `/proc/mdstat`: `mdstat_read()`, wait helpers, lookup helpers, and external/subarray predicates.
- Map file handling: add/update/remove/read/write/lock/unlock and UUID/devnm/name lookup.
- Sysfs: read/write attribute helpers, member state setters, `sysfs_read()`, device add, freeze, wait, fd/string/integer accessors, bad-block/device helpers, and reshape backup helpers.
- Command entry points: `Manage_*`, `Grow_*`, `Assemble`, `Build`, `Create`, `Detail`, `Monitor`, `Kill`, `Wait`, `WaitClean`, `Incremental`, bitmap operations, metadata dump/restore.
- Device helpers: md array ioctl wrappers, parsing, size/sector helpers, md device open/create helpers, path/name translation, mdmon process/socket helpers, systemd continuation, random UUID generation, initrd detection.
- Policy helpers: config policy parsing, disk/path policy, domain matching, udev rule generation, failed-slot persistence, and metadata-specific drive policy checks.
- Cluster hooks for Corosync cmap and DLM.

## Important Invariants

- Metadata strings are normalized through `superlist`/`superswitch` names; policy and metadata code depend on pointer-stable names for fast comparisons.
- `struct mdinfo` is reused for array-level, disk-level, sysfs, and mdmon state; callers must know which fields are valid for the read flags or metadata handler used.
- `MAX_DISKS` is intentionally large enough for v1.x metadata and bounds loops in monitor/policy paths.
- `is_subarray()` encodes mdadm’s convention that external subarrays have metadata versions beginning with `/` or `-`.
- Many declarations assume Linux md sysfs and ioctl semantics; this header is a portability layer only within mdadm’s supported Unix/Linux build variants.
