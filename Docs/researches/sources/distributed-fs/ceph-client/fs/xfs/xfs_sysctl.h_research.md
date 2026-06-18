# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.h` defines XFS global tunable structures, sysctl IDs, debug/global knobs, and registration stubs. It is the shared contract between sysctl registration, mount/superblock code, and code paths that consume global XFS parameters. The source was read as a complete 100-line file for this report.

## Important APIs, Types, and Functions

Important types are `xfs_sysctl_val_t`, `xfs_param_t`, and `struct xfs_globals`. Important declarations are `extern xfs_param_t xfs_params`, `extern struct xfs_globals xfs_globals`, `xfs_sysctl_register`, and `xfs_sysctl_unregister`. The enum preserves historical sysctl IDs such as `XFS_PANIC_MASK`, `XFS_ERRLEVEL`, `XFS_STATS_CLEAR`, inheritance defaults, and `XFS_FILESTREAM_TIMER`.

## Control Flow

There is no runtime control flow in the header. When `CONFIG_SYSCTL` is disabled, register/unregister collapse to no-op stubs so module init can call them unconditionally.

## State and Persistence Behavior

The header defines the shape of global in-memory tunables. `xfs_params` holds min/current/max triples for user-facing sysctl values. `xfs_globals` holds debug and internal global knobs such as log recovery delay, mount delay, assert behavior, always-COW, bulk-load slack, and debug-only parallel workqueue thread limits.

## Dependencies and Integration Points

The header depends on `<linux/sysctl.h>`. It integrates with `xfs_sysctl.c`, `xfs_super.c`, debug sysfs attributes in `xfs_sysfs.c`, error handling, mount delay simulation, btree bulk loading, and reflink debug behavior.

## Risks and Edge Cases

Because many subsystems read `xfs_params` and `xfs_globals`, changing defaults or ranges can affect mount behavior, error handling, and test-only debug behavior globally. The historical enum values should remain stable for compatibility. Debug-only fields must be guarded consistently with users in `xfs_sysfs.c`.

## Test Signals

Compile coverage with `CONFIG_SYSCTL` on and off plus debug and non-debug builds is essential. Runtime signals include sysctl knob presence, correct default ranges, debug sysfs behavior for `xfs_globals`, and mount-delay/log-recovery-delay injection tests.
