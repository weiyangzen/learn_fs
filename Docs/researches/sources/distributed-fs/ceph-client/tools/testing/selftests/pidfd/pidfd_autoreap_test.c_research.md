# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_autoreap_test.c

Purpose: tests newer clone3 pidfd lifecycle extensions: `CLONE_AUTOREAP`, `CLONE_NNP`, and `CLONE_PIDFD_AUTOKILL`, including validation failures, exit reporting, reparenting, multithreaded exit, inheritance, no_new_privs, capabilities, and autokill ownership.

Important APIs/functions: fallback flag definitions, `drop_all_caps()`, `create_autoreap_child()`, and `create_autokill_child()` wrap clone3 argument setup. Tests use `poll()` on pidfds, `PIDFD_GET_INFO`, `sys_pidfd_send_signal()`, `waitpid()`, socketpairs, pthreads, `prctl(PR_SET_CHILD_SUBREAPER)`, and `PR_GET_NO_NEW_PRIVS`.

Control flow: early tests validate accepted/rejected flag combinations. Basic/signaled tests create autoreap children and verify pidfd readability, exit code/signal through `PIDFD_GET_INFO`, and no waitable zombie. Reparent and multithreaded tests verify autoreap across subreaper reparenting and after all threads exit. No-inherit confirms grandchildren are normal waitable children. NNP tests verify only `CLONE_NNP` sets no_new_privs and rejects thread use. Autokill tests verify closing the clone3-created pidfd kills the child, that ordinary `pidfd_open()` fds do not trigger autokill, and that capability/NNP requirements are enforced.

State and persistence: many short-lived children, pidfds, sockets, threads, signal kills, and capability changes. No files persisted. The `autokill_requires_cap_sys_admin` test drops all capabilities in its process.

Dependencies/integration: requires kernel support for these clone3 extension flags, pidfd polling, pidfs info ioctl, pthreads, and root/CAP_SYS_ADMIN for one positive capability test. Unsupported features skip on `EINVAL`.

Risks: this file targets very new kernel behavior; older kernels will skip or fail depending on errno. Capability dropping is irreversible within that test process. Timing uses sleeps and poll timeouts.

Test signals: kselftest harness assertions and skips; expected unsupported kernels report skip for feature-specific tests.
