# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/Makefile

Purpose: builds PID namespace selftests.

Important settings: `CFLAGS` adds debug info and kernel header includes. `TEST_GEN_PROGS` lists `regression_enomem`, `pid_max`, and `pidns_init_via_setns`. `LOCAL_HDRS` depends on the shared pidfd helper header.

Control flow/integration: includes `../lib.mk` for standard kselftest rules and pulls helper APIs from `../pidfd/pidfd.h`.

State/dependencies: no persistent state. Runtime requires PID and user namespaces, procfs remounting for some tests, and clone3/pidfd helpers.

Risks: tests need namespace permissions and may fail in locked-down containers.

Test signals: build outputs three executables; runtime pass/fail/skip comes from C files.
