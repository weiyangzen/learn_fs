# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/context_switch.c

## Purpose
A configurable context-switch microbenchmark measuring pipe, sched_yield, or futex ping-pong between two threads or processes pinned to selected CPUs while optionally touching FP/vector/VDSO state.

## Important APIs, Types, and Functions
Important pieces are `touch()`, `start_thread_on()`, `start_process_on()`, signal handlers, `struct actions`, pipe/yield/futex setup and worker pairs, `sys_futex()`, custom `mutex_lock()`/`mutex_unlock()`, option parsing, and `main()`.

## Control Flow
Main selects mode and CPUs, disables unavailable Altivec/VSX touches, creates a process group, installs SIGUSR1 exit handling, runs the selected setup, starts two workers on target CPUs, and idles while SIGALRM prints per-second iteration deltas until timeout kills the group.

## State and Persistence
State includes global benchmark options, iteration counters, pipe fds or futex words, optional shared memory for process futex mode, CPU affinity, and process-group signal lifecycle. No persistent files are written.

## Dependencies and Integration Points
Depends on pthreads, CPU affinity APIs, futex syscall, SysV shared memory for process mode, PowerPC hwcap helpers, and Altivec/VSX compiler support.

## Risks and Test Signals
Risks include CPU affinity failures, busy-loop resource use, signal-driven termination, and benchmark noise from scheduler/load. Output lines are throughput signals rather than pass/fail assertions.
