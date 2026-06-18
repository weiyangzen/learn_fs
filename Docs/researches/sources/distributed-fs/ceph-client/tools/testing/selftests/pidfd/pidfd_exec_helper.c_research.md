# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_exec_helper.c

Purpose: minimal exec target used by pidfd thread/exec tests. It parks the execed process until killed.

Important API/function: `main()` calls `pause()` and exits failure if `pause()` returns; otherwise process lifetime is controlled by signals.

Control flow: after exec, the process blocks in `pause()`. Normal test cleanup sends a signal, so this program does not report success independently.

State and persistence: no filesystem state; it only holds a process alive.

Dependencies/integration: built as `TEST_GEN_PROGS_EXTENDED` and executed by `pidfd_info_test.c` via `execveat(AT_FDCWD, "pidfd_exec_helper", ...)`.

Risks: must be discoverable in the test working directory. If it exits unexpectedly, pidfd exec tests fail.

Test signals: no direct TAP output; parent tests observe process/pidfd behavior.
