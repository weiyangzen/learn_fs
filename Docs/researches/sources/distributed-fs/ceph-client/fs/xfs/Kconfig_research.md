# sources/distributed-fs/ceph-client/fs/xfs/Kconfig

## Purpose
This Kconfig file exposes XFS kernel configuration switches. It defines the main `XFS_FS` tristate and feature/debug gates for deprecated formats, quotas, POSIX ACLs, realtime subvolumes, online scrub/repair, statistics, hooks, in-memory btrees, warnings, and debug behavior.

## Important Symbols
- `XFS_FS` depends on `BLOCK` and selects `EXPORTFS`, `CRC32`, and `FS_IOMAP`.
- `XFS_SUPPORT_V4` and `XFS_SUPPORT_ASCII_CI` are deprecated-format compatibility toggles, defaulting to `n`, with documented removal timelines.
- `XFS_QUOTA`, `XFS_POSIX_ACL`, and `XFS_RT` enable quota, ACL, and realtime subvolume code.
- Internal booleans `XFS_DRAIN_INTENTS`, `XFS_LIVE_HOOKS`, `XFS_MEMORY_BUFS`, and `XFS_BTREE_IN_MEM` are selected by scrub/repair.
- `XFS_ONLINE_SCRUB`, `XFS_ONLINE_SCRUB_STATS`, and `XFS_ONLINE_REPAIR` gate mounted metadata checking, debugfs usage stats, and mounted repair.
- `XFS_WARN`, `XFS_DEBUG`, `XFS_DEBUG_EXPENSIVE`, and `XFS_ASSERT_FATAL` tune runtime diagnostics and assertion behavior.

## Control Flow and Build Effects
Kconfig dependency resolution controls which objects from `fs/xfs/Makefile` are built. Enabling online scrub selects live hooks, drain intents, and memory-backed buffers; enabling repair selects in-memory btrees. `XFS_RT` defaults to `BLK_DEV_ZONED`, making realtime support mandatory for zoned block devices in the described configuration.

## State and Persistence Behavior
Kconfig itself stores no runtime filesystem state, but it determines whether kernels can mount or operate on certain on-disk features. Disabling V4 or ASCII-CI compatibility can deliberately reject older/case-insensitive filesystems. Enabling online repair changes mounted repair capabilities but does not by itself persist metadata.

## Dependencies and Integration Points
The symbols integrate with the kernel build system, XFS Makefile object lists, generic quota and ACL subsystems, debugfs, tmpfs/shmem for online scrub support, jump labels, iomap, exportfs, and zoned block device support.

## Risks and Edge Cases
Risk centers on distribution defaults: turning off deprecated compatibility can make legacy filesystems unmountable, while turning it on preserves attack surface. Online repair depends on newer on-disk metadata such as reverse mappings and parent pointers, so configuration support is not sufficient for all filesystems. Debug options can drastically alter performance and failure mode.

## Test Signals
Useful signals are allmodconfig/allyesconfig build coverage, feature-matrix builds for quota/ACL/RT/scrub/repair, boot/mount tests for V4 and ASCII-CI images with symbols on and off, xfstests scrub/repair groups, debugfs scrub stats checks, and build checks that selected internal symbols pull the expected object files.
