# File Research: sources/block-storage/lvm2/tools/pvremove.c

## Purpose

`pvremove.c` implements `pvremove`, clearing LVM PV labels/metadata from one or more devices. It reuses the shared `pvcreate_each_device()` machinery in removal mode.

## Main Entry Point

- `pvremove()`: validates arguments, sets removal parameters, handles locking and scanning, then calls `pvcreate_each_device()`.

## Flow

- Requires at least one physical volume path.
- Initializes `pvcreate_params` with defaults.
- Sets:
  - `pp.is_remove = 1`
  - `pp.force` from `arg_force_value()`
  - `pp.yes` from `--yes`
  - PV count and names from command args
- Takes the global lock exclusively because orphan PV set changes.
- Allows `-ff` force mode to continue if the global lock cannot be taken.
- Clears hints and scans labels.
- Disables lockd VG locking for `-ff`, because forced clearing does not care about VG locks.
- Calls `pvcreate_each_device()`; the `is_remove` flag changes checks and final action from create to remove.

## Safety Notes

- Normal removal requires the global lock.
- Force override mode can skip the global lock and VG locking, making it intentionally more destructive.
- Actual validation and wiping are delegated to shared PV create/remove helper code.
