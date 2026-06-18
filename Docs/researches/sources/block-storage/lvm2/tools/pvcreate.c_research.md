# File Research: sources/block-storage/lvm2/tools/pvcreate.c

## Purpose

`pvcreate.c` implements `pvcreate`, which initializes physical volumes and supports recovery workflows using a backup metadata file and explicit UUID.

## Main Entry Point

- `pvcreate()`: builds `pvcreate_params`, validates recovery arguments, imports backup-derived parameters, parses normal arguments, locks globally, scans labels, and calls `pvcreate_each_device()`.

## Recovery Argument Handling

`_pvcreate_restore_params_from_args()` validates and applies:

- `--restorefile`
- `--uuid`
- `--physicalvolumesize`

Rules include:

- `--restorefile` requires `--uuid`.
- `--uuid` can require `--restorefile` depending on configuration unless `--norestorefile` is set.
- UUID setting is allowed for only one device at a time.
- Negative physical volume size is rejected.
- Restore/UUID mode disables zeroing via `pp->zero = 0`.

## Backup-Derived Parameters

`_pvcreate_restore_params_from_backup()`:

- Reads the VG backup with `backup_read_vg()`.
- Finds the PV matching the requested UUID.
- Copies bootloader area start/size, PE start, extent size, and extent count into the PV creation parameters.
- Releases the temporary VG.

## Normal Creation Flow

After recovery-specific setup:

- `pvcreate_params_from_args()` applies normal command-line settings.
- If `--restorefile` is used without `--metadatasize`, metadata size is set to `pe_start` as a maximum that lower layers can reduce.
- `pp.pv_count` and `pp.pv_names` are populated from command arguments.
- Global exclusive lock is taken because orphan PV set changes.
- Hints are cleared.
- `cmd->create_edit_devices_file` is enabled.
- `lvmcache_label_scan()` runs before processing.
- `pvcreate_each_device()` performs the actual per-device create logic.

## Notable Behavior

The file is a command-level wrapper; detailed PV initialization, wiping, metadata writing, and device validation are delegated to shared toollib code through `pvcreate_each_device()` and `pvcreate_params_from_args()`.
