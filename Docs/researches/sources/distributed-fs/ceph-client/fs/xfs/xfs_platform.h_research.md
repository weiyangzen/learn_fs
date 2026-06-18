# sources/distributed-fs/ceph-client/fs/xfs/xfs_platform.h

Purpose: Provides the Linux kernel platform adaptation layer for XFS. It gathers common kernel includes, maps configuration options to XFS debug macros, defines XFS core typedefs, pulls in base XFS headers, exposes tunable aliases, and supplies portability helpers and assertions.

Important APIs, types, and functions: Defines `xfs_off_t`, `xfs_ino_t`, `xfs_daddr_t`, `xfs_dev_t`, `xfs_nlink_t`, `struct xfs_kobj`, and `struct xstats`. Provides tunable aliases such as `xfs_panic_mask`, `xfs_error_level`, and timer defaults. Utility helpers include device id conversion, `rounddown_64`, `roundup_64`, `howmany_64`, `isaligned_64`, `log2_if_power2`, `mask64_if_power2`, `delay`, `kmem_to_page`, and `xfs_rw_bdev` declaration. Assertion/corruption macros include `ASSERT_ALWAYS`, build-dependent `ASSERT`, and `XFS_IS_CORRUPT`.

Control flow: The header is included before most XFS implementation files, establishing kernel APIs, endian detection, DEBUG/XFS_WARN behavior, realtime feature stubs, pointer formatting, and the `STATIC static noinline` convention used for testable internal functions.

State and persistence behavior: No direct persistent state. It references global tunables and statistics objects. Assertion and corruption macros can emit warnings, stack traces, or fatal bugs depending on config and runtime settings.

Dependencies and integration points: Integrates XFS with Linux VFS, block layer, memory management, workqueues, sysfs/debugfs, ratelimits, uaccess, endian/unaligned helpers, and XFS base modules such as stats, sysctl, buffer, message, drain, and hooks. It also gates realtime inode checks on `CONFIG_XFS_RT`.

Risks: Because this is a foundational include, changes can affect the entire XFS build. Assertion semantics differ by DEBUG and XFS_WARN, so code must not depend on assertion side effects. `XFS_IS_CORRUPT` reports and evaluates expressions; callers must keep expressions side-effect free. Type widths are part of on-disk format assumptions.

Test signals: Build matrix across DEBUG, DEBUG_EXPENSIVE, ASSERT_FATAL, XFS_WARN, realtime enabled/disabled, big-endian, and v4 support. Static analysis should flag side effects inside assertion and corruption expressions. Runtime fault tests should verify corruption reports include useful caller addresses.
