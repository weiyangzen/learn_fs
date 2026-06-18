# File Research: sources/block-storage/util-linux/sys-utils/eject.c

## Scope

Implements `eject`, a removable-media utility that resolves devices or mountpoints, optionally unmounts mounted filesystems/partitions, and performs tray, CD-ROM, SCSI, floppy, tape, changer, speed, auto-eject, and manual-lock operations.

## Public And Internal APIs Covered

- Main command-line entry point.
- Argument handling: `parse_args()`, `usage()`.
- Device resolution/mount handling: `find_device()`, `device_get_mountpoint()`, `get_disk_devname()`, `umount_partitions()`, `umount_one()`, `is_ejectable()`, `open_device()`.
- CD-ROM operations: `auto_eject()`, `manual_eject()`, `changer_select()`, `close_tray()`, `eject_cdrom()`, `toggle_tray()`, `select_speed()`, `read_speed()`, `list_speeds()`.
- Other eject methods: `eject_scsi()`, `eject_floppy()`, `eject_tape()`.
- Verbose/info helpers.

## Control Flow And Behavior

- Resolves default `/dev/cdrom`, explicit `/dev/...`, relative device names under `/dev`, mountpoints, tags/specs via libmount, and whole-disk devices for partition inputs.
- Uses libmount to parse mtab or `/proc/mountinfo` and determine whether the device or mountpoint is mounted.
- Unless `--no-unmount` is used, unmounts mounted partitions or the whole-device mountpoint by forking `/bin/umount`, dropping permissions in the child.
- `--no-partitions-unmount` changes partition handling into a safety check: if multiple mounted partitions remain, eject fails with device-in-use.
- After unmounting, later open uses `O_EXCL` unless `--force` is set, reducing races with remounts.
- Direct action options handle:
  - default-device printing,
  - no-op resolved-device display,
  - manual eject lock/unlock,
  - auto-eject on/off,
  - tray close/toggle,
  - list/set CD speed,
  - changer slot selection.
- If no eject method is explicitly selected, it tries CD-ROM, SCSI, floppy, and tape methods in order until one succeeds.
- SCSI eject uses SG_IO commands: allow medium removal, start/stop stop, then start/stop eject, with selected sense errors ignored for compatibility.

## Dependencies

- Linux CD-ROM, floppy, tape, block, SCSI SG_IO, and mount APIs.
- libmount for mount table parsing, cache, source/target lookup, and spec/path resolution.
- Sysfs helpers for hotplug/removable checks, whole-disk lookup, and partition scanning.
- util-linux helpers for timing, file/path utilities, parsing, allocation, i18n, and permission dropping.

## Risks And Invariants

- By default, non-hotpluggable/non-removable devices are rejected unless `--force` is used.
- Device resolution may replace a partition device with its whole disk before ejecting.
- Unmount is delegated to `/bin/umount`; failures abort eject.
- Tray toggle has two implementations: drive-status based when available, timing heuristic otherwise.
- SCSI handling intentionally tolerates unsupported medium-removal and no-medium sense codes but rejects other driver/host failures.
