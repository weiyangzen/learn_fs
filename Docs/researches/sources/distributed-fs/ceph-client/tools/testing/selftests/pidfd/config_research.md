# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/config

Purpose: declares kernel config prerequisites for pidfd tests.

Important settings: enables UTS, IPC, USER, PID, NET, TIME namespaces, cgroups, and checkpoint/restore.

Control flow/integration: used by kselftest config tooling to request namespace and checkpoint/restore functionality needed by pidfd tests.

State/dependencies: declarative only. It does not ensure runtime permissions, pidfs feature availability, or clone3 extensions.

Risks: feature tests may still skip/fail on older kernels or restricted environments even when these config symbols are enabled.

Test signals: none directly.
