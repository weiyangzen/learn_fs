# File Research: sources/cow-pools/bcachefs-tools/src/commands/device.rs

This file implements the `bcachefs device` command group.

Subcommands:
- `add`
- `online`
- `offline`
- `remove`
- `evacuate`
- `set-state`
- `resize`
- `resize-journal`

Major behavior:
- `add` first tries online add through a mounted filesystem handle, then falls back to offline add with `nostart`, `copygc_enabled=0`, and `reconcile_enabled=0`.
- Device-add formatting reuses `format_util::format_for_device_add()`.
- Device paths and numeric device indexes can be resolved against a filesystem handle.
- Multipath component devices are detected and require `--force`.
- `offline`, `remove`, and `set-state` set force flags for degraded/data/metadata-loss cases.
- Offline `set-state` edits member state directly in the superblock.
- `resize` supports online growth and offline growth; shrinking is explicitly rejected.
- `resize-journal` supports online and offline paths.
- `evacuate` sets a device readonly/evacuating, triggers reconcile wakeup, and polls until visible non-hidden data sectors reach zero.

Version/safety checks:
- Evacuation requires kernel and filesystem metadata version supporting reconcile.
- Offline resize helpers require exactly one online device in the filesystem.

Dependencies:
- `BcachefsHandle` for online ioctls/sysfs-backed operations.
- `Fs` for offline open/start/write-super flows.
- `device_multipath`, `format_util`, `sysfs`, and accounting wrappers.
