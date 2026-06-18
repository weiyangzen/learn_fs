# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_racct.c

## Purpose

Accounts ZFS read/write activity into FreeBSD per-thread resource counters, optional RACCT process counters, and OpenZFS spa I/O statistics.

## Functions

- `zfs_racct_read(spa_t *spa, uint64_t size, uint64_t iops, dmu_flags_t flags)`
  - Increments current thread `ru_inblock` by `iops`.
  - When compiled with `RACCT` and `racct_enable` is true:
    - Locks `curproc`.
    - Adds `size` to `RACCT_READBPS`.
    - Adds `iops` to `RACCT_READIOPS`.
    - Unlocks `curproc`.
  - Updates pool I/O stats with `spa_iostats_read_add(spa, size, iops, flags)`.
- `zfs_racct_write(spa_t *spa, uint64_t size, uint64_t iops, dmu_flags_t flags)`
  - Increments current thread `ru_oublock` by `iops`.
  - When RACCT is active:
    - Adds `size` to `RACCT_WRITEBPS`.
    - Adds `iops` to `RACCT_WRITEIOPS`.
  - Updates pool I/O stats with `spa_iostats_write_add(spa, size, iops, flags)`.

## Conditional Behavior

- Without `RACCT`, the `size` argument is explicitly marked unused before spa stats are updated.
- Thread `rusage` and spa I/O stats are always updated.

## Concurrency

- RACCT process updates are protected by `PROC_LOCK(curproc)`.
- Spa I/O stats are delegated to the `spa_iostats_*` helpers.
