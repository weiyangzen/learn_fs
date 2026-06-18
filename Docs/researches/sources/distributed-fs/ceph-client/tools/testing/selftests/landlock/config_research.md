# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/config

## Purpose
This kselftest config fragment lists kernel configuration options needed for the Landlock selftest suite. It ensures the test environment includes Landlock, audit, filesystems, networking, namespaces, cgroups, keys, and other kernel features touched by the tests.

## Important APIs, Types, And Functions
The file is declarative Kconfig input rather than C code. Key options are `CONFIG_SECURITY_LANDLOCK=y`, `CONFIG_SECURITY=y`, `CONFIG_AUDIT=y`, `CONFIG_KEYS=y`, `CONFIG_OVERLAY_FS=y`, `CONFIG_TMPFS=y`, `CONFIG_TMPFS_XATTR=y`, `CONFIG_PROC_FS=y`, `CONFIG_SYSFS=y`, `CONFIG_CGROUPS=y`, network options including `CONFIG_NET`, `CONFIG_INET`, `CONFIG_IPV6`, `CONFIG_NET_NS`, `CONFIG_AF_UNIX_OOB`, and MPTCP options.

## Control Flow
There is no runtime control flow. The kselftest tooling can use this file to identify required or recommended kernel config settings before running the Landlock tests.

## State, Persistence, And Dependencies
The file persists expected kernel build-time state. It does not mutate the system. It depends on kernel config option names remaining valid and aligned with the Landlock selftest coverage.

## Integration Points
The fragment integrates with the Linux selftests configuration-checking workflow. It supports the C tests in this directory by documenting the kernel features they assume, including audit for `audit_test.c`, keys for `base_test.c`, and filesystem/network features used by broader Landlock tests.

## Risks
The config can become stale as tests add dependencies or kernel symbols are renamed. It lists options for the broader directory, not only the files in this work item, so a minimal environment for a single test may need fewer options. Missing `CONFIG_AUDIT` or `CONFIG_SECURITY_LANDLOCK` will cause high-level skips or failures rather than build errors.

## Test Signals
Good signals are config-check passes before running Landlock selftests and runtime availability of Landlock, audit netlink, keyrings, and relevant filesystems. Failures show up as skipped tests, missing syscalls/features, or fixture setup errors.
