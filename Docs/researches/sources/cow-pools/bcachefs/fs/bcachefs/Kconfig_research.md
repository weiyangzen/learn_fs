# File Research: sources/cow-pools/bcachefs/fs/bcachefs/Kconfig

This file defines the kernel configuration surface for the bcachefs filesystem.

`BCACHEFS_FS` is the main tristate option, marked experimental, depending on `BLOCK` and selecting the filesystem, crypto, compression, RAID/parity, checksum, key, and support libraries bcachefs needs. The help text describes bcachefs as a modern copy-on-write filesystem with multiple-device, compression, and checksumming support.

Additional options expose feature and debug knobs:
- `BCACHEFS_QUOTA` depends on `BCACHEFS_FS` and selects `QUOTACTL`.
- `BCACHEFS_DEBUG` enables extra assertions and checks, with expected performance cost.
- `BCACHEFS_INJECT_TRANSACTION_RESTARTS` depends on debug and randomly injects transaction restarts in core paths.
- `BCACHEFS_TESTS` includes unit/performance tests for core btree code.
- `BCACHEFS_LOCK_TIME_STATS` exposes lock hold-time stats in debugfs.
- `BCACHEFS_NO_LATENCY_ACCT` disables device latency tracking and timing stats for performance testing.
- `BCACHEFS_SIX_OPTIMISTIC_SPIN` defaults on for SMP and enables optimistic spinning on six locks.
- `BCACHEFS_PATH_TRACEPOINTS` adds high-volume btree path tracepoints when tracing is available.
- `BCACHEFS_TRANS_KMALLOC_TRACE` traces transaction allocation calls.
- `MEAN_AND_VARIANCE_UNIT_TEST` wires the bcachefs utility KUnit test into `KUNIT_ALL_TESTS`.

There is also a `BCACHEFS_DKMS` conditional that forces `CONFIG_BCACHEFS_FS := m` for DKMS builds. This file is purely build/configuration policy; it does not implement runtime logic, but it controls whether the allocation/accounting code in this group is compiled and what debug instrumentation may be active.
