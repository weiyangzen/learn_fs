# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.c

## Purpose

`timerlat_u.c` implements the user-space workload side of rtla timerlat. It creates `timerlatu/<cpu>` processes pinned to monitored CPUs, opens each CPU's `osnoise/per_cpu/cpuN/timerlat_fd`, and blocks in reads so timerlat can measure user-space return latency.

## Important APIs, Types, and Functions

The file consumes `struct timerlat_u_params` from `timerlat_u.h`. `timerlat_u_main()` configures one child process, `timerlat_u_send_kill()` terminates child PIDs, and `timerlat_u_dispatcher()` is the pthread entry that forks and supervises one child per selected CPU.

## Control Flow and Data Flow

The dispatcher allocates a PID array sized by `nr_cpus`, iterates over the CPU set, forks one child per monitored CPU, names it `timerlatu/N`, and enters `timerlat_u_main()`. Each child sets affinity, applies either default SCHED_FIFO priority 95 or caller-provided scheduler attributes, optionally joins a cgroup, opens the per-CPU timerlat fd, and repeatedly reads until error/termination. The parent polls `waitpid(WNOHANG)` while `should_run` remains true, kills remaining children, waits for all exits, and marks `stopped_running`.

## State and Persistence Behavior

State is process-local and shared only through `timerlat_u_params` flags and forked child PIDs. The timerlat fd and scheduler/cgroup settings affect kernel runtime state while processes live. No measurement data is persisted here; the tracer records latency elsewhere.

## Dependencies and Integration Points

This code depends on tracefs timerlat per-CPU fd files, scheduler syscalls, pthread naming, `prctl(PR_SET_NAME)`, cgroup helpers from `utils.c`, `common.h` globals such as `nr_cpus`, and the surrounding timerlat tool that starts the dispatcher and flips `should_run`.

## Risks and Edge Cases

Affinity setup fails for offline CPUs. Default FIFO priority requires privilege. The cgroup error path uses `pthread_exit()` in child context and reports inverted success semantics carefully because `set_pid_cgroup()` returns nonzero on success. If any child exits early, the dispatcher eventually kills all remaining children. `SIGKILL` leaves little cleanup opportunity inside children.

## Test Signals

Test signals include process naming, one child per selected CPU, affinity and priority checks, failure on offline CPUs, cgroup placement, clean `stopped_running` transition when `should_run` is cleared, and timerlat sessions with `--user-threads` confirming user latency columns are populated.
