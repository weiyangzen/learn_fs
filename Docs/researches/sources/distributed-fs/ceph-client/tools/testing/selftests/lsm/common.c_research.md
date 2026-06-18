# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.c

Purpose: shared helpers for LSM syscall tests.

Important APIs/types/functions: `read_proc_attr()` reads `/proc/self/attr/<attr>` into a caller buffer and strips newline. `read_sysfs_lsms()` reads `/sys/kernel/security/lsm`. `attr_lsm_count()` counts active label-producing LSMs among SELinux, Smack, and AppArmor.

Control flow: helper functions allocate path/name buffers, open/read/probe procfs or securityfs, validate buffer termination, and return `0` or `-1`.

State and persistence: read-only inspection of process attributes and securityfs state. `attr_lsm_count()` allocates a page-sized buffer and, on read failure, returns zero.

Dependencies and integration points: `/proc/self/attr`, `/sys/kernel/security/lsm`, active LSM configuration, `linux/lsm.h` constants used by callers.

Risks: `attr_lsm_count()` leaks `names` on successful `read_sysfs_lsms()` path in this snapshot because it does not free before return. It uses substring matching, so unexpected names containing known strings could overcount.

Test signals: callers use these helpers to decide expected syscall counts and compare syscall results against legacy procfs/sysfs interfaces.
