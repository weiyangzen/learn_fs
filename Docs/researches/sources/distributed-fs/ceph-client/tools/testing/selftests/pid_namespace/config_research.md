# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/config

Purpose: declares namespace config prerequisites for PID namespace tests.

Important settings: `CONFIG_PID_NS=y` and `CONFIG_USER_NS=y`.

Control flow/integration: used by kselftest config checks before running PID namespace binaries.

State/dependencies: declarative only. It does not guarantee that unprivileged user namespaces are enabled by runtime policy.

Risks: sysctl or container policy can still block `unshare(CLONE_NEWUSER)` or `CLONE_NEWPID`.

Test signals: none directly.
