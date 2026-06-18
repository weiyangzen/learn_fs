# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/fork.c

## Purpose
Microbenchmarks thread creation, fork, vfork, and optional exec throughput on an optional CPU affinity.

## Important APIs, Types, and Functions
Important functions are `set_cpu()`, `start_process_on()`, `run_exec()`, `bench_fork()`, `bench_vfork()`, `bench_thread()`, signal handlers, `bench_proc()`, `usage()`, and `main()`.

## Control Flow
Main parses `--fork`, `--vfork`, `--exec`, `--timeout`, and `--exec-target`, optionally chdirs beside the executable for `exec_target`, pins CPU, creates a process group, starts a benchmark worker process, and prints per-second iteration deltas until timeout sends SIGUSR1.

## State and Persistence
State includes global mode flags, CPU choice, iteration counters, signal alarms, and child processes/threads. It writes no files.

## Dependencies and Integration Points
Depends on pthreads, fork/vfork/waitpid, execve of `./exec_target`, CPU affinity, and process-group signaling.

## Risks and Test Signals
Risks include runaway process creation on broken termination, inaccurate measurements under load, and requiring `exec_target` in the working directory for exec mode. Output throughput is the main signal.
