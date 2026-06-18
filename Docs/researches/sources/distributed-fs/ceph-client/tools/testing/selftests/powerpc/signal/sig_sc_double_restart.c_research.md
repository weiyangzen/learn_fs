# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sig_sc_double_restart.c

Purpose: regression test for powerpc double syscall restart bugs when nested signals interrupt a restartable syscall.

Important APIs/types/functions: `raw_read()` issues a hand-written `sc` sequence with a branch just before it; `SIGUSR1_handler()` raises `SIGUSR2`; `test_restart()` drives the pipe/fork scenario.

Control flow: the child installs restarting handlers, duplicates the pipe read fd until it is 512 so interrupted `read()` places `ERESTARTSYS` in `r3`, and calls `raw_read()`. The parent signals `SIGUSR1`, writes data, and waits. If the kernel restarts twice, NIP retreats before the syscall and `raw_read()` returns sentinel `ENOANO`.

State and persistence behavior: only process signal masks, pipe fds, and child status are stateful. No filesystem state is persisted.

Dependencies and integration points: uses raw powerpc syscall ABI and kselftest `test_harness_set_timeout(10)`.

Risks and test signals: timing uses short `usleep()` delays to get the child blocked. Failure is explicit `ENOANO`, bad pipe data, abnormal child exit, or nonzero child status.
