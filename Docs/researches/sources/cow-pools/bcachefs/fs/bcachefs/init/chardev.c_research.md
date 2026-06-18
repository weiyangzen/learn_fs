# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.c

This file implements the bcachefs character device control interface and ioctl dispatch.

Device lookup and global ioctl:
- `bch2_device_lookup()` resolves devices either by member index (`BCH_BY_INDEX`) or userspace path, returning a referenced `bch_dev`.
- `bch2_global_ioctl()` currently handles offline fsck.
- `bch2_ioctl_query_uuid()` copies the filesystem user UUID to userspace.
- `bch2_copy_ioctl_err_msg()` copies structured error text into v2 ioctl error buffers.

Device management ioctls:
- Add, remove, online, offline, set-state, resize, and journal-resize handlers validate capability (`CAP_SYS_ADMIN`), flags, padding, and bounds before calling `dev.c` operations.
- v2 variants use `bch2_copy_ioctl_err_msg()` to return detailed error strings.
- Force flags are restricted to operations where degraded/data-loss override makes sense.

Data job ioctl:
- `bch2_ioctl_data()` starts a long-running data job through `thread_with_file`.
- `bch2_data_thread()` runs `bch2_data_job()` and records completion/device-offline status.
- The returned file supports `read()` through `bch2_data_job_read()`, which reports progress, sector counts, and totals for scrub or filesystem usage.
- A write reference `BCH_WRITE_REF_ioctl_data` prevents running data jobs after writes are disabled.

Usage/accounting ioctls:
- `bch2_ioctl_fs_usage()` reports capacity, used sectors, online reservations, persistent reservations, and replica usage entries.
- `bch2_ioctl_query_accounting()` returns accounting data selected by mask.
- `bch2_ioctl_dev_usage()` and v2 report per-device usage by data type.

Superblock and index ioctls:
- `bch2_ioctl_read_super()` copies either the filesystem superblock or a specific device superblock.
- `bch2_ioctl_disk_get_idx()` maps a block device dev_t to the bcachefs member index.

Dispatch and char-device lifecycle:
- `bch2_fs_ioctl()` dispatches filesystem ioctls, allowing a small query set before `BCH_FS_started` and requiring started state for mutating operations.
- `bch2_chardev_ioctl()` maps minors below `U8_MAX` to filesystem-specific devices; minor `U8_MAX` is the global control node.
- `bch2_fs_chardev_init()/exit()` allocate/remove per-filesystem minors and devices.
- `bch2_chardev_init()/exit()` register the global char device major, class, and control node.

Role:
- This is the kernel/userspace administrative control surface for mounted bcachefs filesystems.
