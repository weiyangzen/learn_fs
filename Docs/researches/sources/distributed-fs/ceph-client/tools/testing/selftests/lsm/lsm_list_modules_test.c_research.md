# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_list_modules_test.c

Purpose: validates `lsm_list_modules()` syscall argument checks and returned module ordering/names against securityfs.

Important APIs/types/functions: uses `lsm_list_modules()`, `read_sysfs_lsms()`, `LSM_ID_*` constants, and kselftest harness assertions.

Control flow: negative tests verify NULL size (`EFAULT`), NULL ids (`EFAULT`), too-small size (`E2BIG`), and invalid flags (`EINVAL`). The positive test reads `/sys/kernel/security/lsm`, calls the syscall into a page-sized `__u64` array, then maps each returned ID to an expected name and compares it with the comma-separated sysfs list by advancing through the string.

State and persistence: read-only securityfs/syscall inspection.

Dependencies and integration points: active securityfs mount, LSM syscall ABI, current `LSM_ID_*` enum coverage.

Risks: the ID-to-name switch must be updated for new LSM IDs. The string comparison assumes sysfs ordering exactly matches syscall ordering.

Test signals: pass requires matching module count/order/name prefixes and correct errno for invalid invocations.
