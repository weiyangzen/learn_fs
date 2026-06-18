# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ondisk.h

Purpose: Provides compile-time assertions that XFS on-disk and UABI structures have exact expected sizes, offsets, and constant values. It is a guardrail against accidental ABI/layout drift.

Important APIs: assertion macros `XFS_CHECK_STRUCT_SIZE`, `XFS_CHECK_OFFSET`, `XFS_CHECK_VALUE`, `XFS_CHECK_SB_OFFSET`, and the init-time function `xfs_check_ondisk_structs`.

Control flow: `xfs_check_ondisk_structs` runs a sequence of `static_assert` checks covering file structures, btrees, dir/attr layouts, realtime metadata, log item formats, parent pointer ioctls, v5/v4 shared header offsets, timestamp/quota time range values, superblock offsets, and ioctl UABI structures. It also documents intentionally omitted architecture-sensitive structures.

State and persistence: no runtime mutable state. Its entire purpose is to protect persistent on-disk and userspace ABI formats at build time.

Dependencies and integration: includes all relevant structure definitions indirectly through format headers. It must be updated whenever a deliberate on-disk or UABI layout change is made.

Risks and test signals: missing or stale assertions can allow silent ABI regressions; incorrect assertions can break valid builds on some architectures. Test signals are compile coverage across 32-bit/64-bit architectures, xfs/122 ondisk layout tests, and CI builds after changing any format header.
