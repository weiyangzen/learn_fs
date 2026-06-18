# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_racct.c

## Purpose

Linux resource-accounting adapter for ZFS read/write I/O accounting.

## Kernel Behavior

When `_KERNEL` is defined:

- `zfs_racct_read()` calls `task_io_account_read(size)` and updates SPA read I/O stats with `spa_iostats_read_add(spa, size, iops, flags)`.
- `zfs_racct_write()` calls `task_io_account_write(size)` and updates SPA write I/O stats with `spa_iostats_write_add(spa, size, iops, flags)`.

## Non-Kernel Behavior

Outside kernel builds, both functions are no-ops that explicitly consume their arguments.
