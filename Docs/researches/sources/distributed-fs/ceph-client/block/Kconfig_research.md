# sources/distributed-fs/ceph-client/block/Kconfig

## Purpose
This Kconfig file defines the Linux block layer configuration menu for this source tree. It controls whether the block layer is built and gates optional features such as block integrity, zoned devices, cgroup controllers, writeback throttling, debugfs, Opal SED support, and inline encryption.

## Important APIs, types, and symbols
`menuconfig BLOCK` is the root switch, defaulting to enabled and selecting `FS_IOMAP` and `SBITMAP`. Feature symbols include `BLOCK_LEGACY_AUTOLOAD`, `BLK_DEV_BSGLIB`, `BLK_DEV_INTEGRITY`, `BLK_DEV_WRITE_MOUNTED`, `BLK_DEV_ZONED`, `BLK_DEV_THROTTLING`, `BLK_WBT`, `BLK_WBT_MQ`, `BLK_CGROUP_IOLATENCY`, `BLK_CGROUP_FC_APPID`, `BLK_CGROUP_IOCOST`, `BLK_CGROUP_IOPRIO`, `BLK_DEBUG_FS`, `BLK_SED_OPAL`, `BLK_INLINE_ENCRYPTION`, `BLK_INLINE_ENCRYPTION_FALLBACK`, `BLK_PM`, `BLOCK_HOLDER_DEPRECATED`, and `BLK_MQ_STACKING`.

## Control flow
Kconfig control is declarative. All nested options are visible only under `if BLOCK`. Several options select lower-level dependencies, for example integrity selects CRC libraries, throttling selects `BLK_CGROUP_RWSTAT`, IOCOST selects request allocation timestamps, and inline encryption fallback selects crypto primitives. The file also includes `block/partitions/Kconfig` and `block/Kconfig.iosched`.

## State and persistence behavior
The persistent output is the kernel `.config`; selected symbols drive compiled code and default runtime behavior. `BLK_DEV_WRITE_MOUNTED` is particularly visible at runtime because `bdev.c` initializes `bdev_allow_write_mounted` from it while still allowing a boot parameter override.

## Dependencies and integration points
The symbols map directly to `block/Makefile` object inclusion and to conditional code throughout the block layer. They also expose user-facing policy choices through help text and cgroup/debugfs interfaces.

## Risks
Disabling `BLOCK` removes block device usability and dependent storage subsystems. Enabling experimental or policy-heavy controllers changes IO behavior. `BLK_DEV_WRITE_MOUNTED=n` improves protection but can break tools that expect to write mounted read-only block devices. Dependency errors here produce missing objects or unused code paths.

## Test signals
Run Kconfig parsing, build `allnoconfig`, `defconfig`, and configurations toggling each option. Boot smoke tests should verify block device nodes, cgroup IO files, inline encryption fallback, debugfs entries, and mounted-device write policy under both config and boot-parameter settings.
