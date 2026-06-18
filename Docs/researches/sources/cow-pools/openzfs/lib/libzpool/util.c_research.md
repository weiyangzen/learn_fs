# File Research: sources/cow-pools/openzfs/lib/libzpool/util.c

Shared libzpool utility routines. It contains vdev/pool stats printing, command-line tunable handling, and pool config operations for import logic.

Key behavior:
- `show_vdev_stats()` recursively prints capacity, ops, bandwidth, and error columns for vdev trees, including logs, spares, and L2ARC.
- `show_pool_stats()` fetches pool config and prints the root vdev plus L2/cache/spare children.
- `handle_tunable_option()` supports `name`, `name=value`, `show`, `show=name`, `info`, and `info=name`.
- `refresh_config()` calls `spa_tryimport()`.
- `pool_active()` checks whether a pool is active by issuing `ZFS_IOC_POOL_STATS` against `/dev/zfs`.

FreeBSD has extra ioctl-version handling for OpenZFS vs legacy ioctl layouts.
