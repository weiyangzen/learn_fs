# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/config

Purpose: minimal kernel config fragment for LSM tests.

Important APIs/types/functions: requests `CONFIG_SYSFS`, `CONFIG_SECURITY`, and `CONFIG_SECURITYFS`.

Control flow: none.

State and persistence: build/runtime environment declaration only.

Dependencies and integration points: supports `/sys/kernel/security/lsm`, securityfs, and LSM infrastructure needed by the syscall tests.

Risks: individual LSMs are not forced on by this fragment, so tests must handle no label-producing LSMs.

Test signals: with these options available, LSM syscall tests should at least execute or report ABI errors rather than missing filesystems.
