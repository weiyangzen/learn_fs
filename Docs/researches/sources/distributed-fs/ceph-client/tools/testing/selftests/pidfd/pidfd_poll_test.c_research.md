# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_poll_test.c

## Purpose
Stress-tests pidfd readiness notifications by repeatedly creating a child, opening a pidfd, killing the child through pidfd_send_signal, and requiring poll() on the pidfd to report process death with POLLIN.

## Important APIs, Types, and Functions
`handle_alarm()` records a timeout, `main()` parses an optional iteration count, uses `sys_pidfd_open()`, `sys_pidfd_send_signal()`, `poll()`, `waitpid()`, and kselftest reporting helpers from `pidfd.h` and `kselftest.h`.

## Control Flow
For each iteration the parent forks a sleeping child, opens its pidfd, arms a 3 second SIGALRM, sends SIGKILL through the pidfd, blocks in `poll()`, validates exactly one POLLIN event, closes the pidfd, and reaps the child. Transient `fork()` EAGAIN retries the same iteration.

## State and Persistence
Only process-local state is used: the global `timeout`, a child process, and an open pidfd per loop. No durable state is written; zombie cleanup is explicit through `waitpid()`.

## Dependencies and Integration Points
Depends on pidfd syscalls exposed by `pidfd.h`, Linux signal/poll semantics, and the kselftest standalone binary convention. It integrates with the pidfd selftest target as a stress-style regression test.

## Risks and Test Signals
Main risk is flakiness from scheduler stalls or missing pidfd syscall support; failure signals include timeout, missing POLLIN, unexpected extra events, pidfd syscall errors, or failed reaping. A pass means pidfd poll death notification remained stable over the configured iteration count.
