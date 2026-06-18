
# sources/distributed-fs/ceph-client/include/trace/events/sched.h

## Purpose
Defines the scheduler tracepoint interface for task lifecycle, wakeups, context switches, migration, kthread work, scheduler statistics, priority inheritance, NUMA balancing, capacity/utilization hooks, and deadline-server debug hooks.

## Important APIs, Types, and Functions
Public events include `sched_kthread_stop`, `sched_kthread_stop_ret`, `sched_kthread_work_queue_work`, `sched_kthread_work_execute_start`, `sched_kthread_work_execute_end`, wakeup events from `sched_wakeup_template`, `sched_switch`, `sched_migrate_task`, `sched_process_free`, `sched_process_exit`, `sched_wait_task`, `sched_process_wait`, `sched_process_fork`, `sched_process_exec`, `sched_prepare_exec`, schedstat events, `sched_pi_setprio`, optional `sched_process_hang`, optional NUMA events, and `sched_wake_idle_without_ipi`. It also declares non-tracefs `DECLARE_TRACE` hooks for PELT, capacity, overutilization, util-est, energy computation, scheduler entry/exit, state changes, need-resched, and deadline throttle/replenish/server transitions. `__trace_sched_switch_state()` maps task state into printable switch state when `CREATE_TRACE_POINTS` is active.

## Control Flow
Scheduler code emits these events at precise scheduling transitions: wakeup starts in the waking context, wakeup completion records the runnable task, `sched_switch` snapshots previous and next task state during context switch, migration records source and destination CPUs, process events follow fork/exec/exit/free/wait paths, and schedstat events are emitted during accounting updates. NUMA balancing events are conditional on `CONFIG_NUMA_BALANCING`; schedstat event definitions compile to no-op variants when `CONFIG_SCHEDSTATS` is disabled.

## State and Persistence
The header persists no scheduler state. Trace records snapshot task command names, pids, priorities, CPU ids, run states, delays, runtime, NUMA ids, nodemasks, exec filenames, and work item pointers into trace buffers. The non-tracefs `DECLARE_TRACE` hooks expose transient scheduler internals to in-kernel instrumentation without creating normal tracefs events.

## Dependencies and Integration Points
Depends on `linux/kthread.h`, `linux/sched/numa_balancing.h`, `linux/binfmts.h`, `linux/tracepoint.h`, scheduler task/runqueue types, cpuset/NUMA helpers, and build-time scheduler configs. Integrates with perf sched, ftrace, eBPF sched tracing, latency profilers, Android/vendor scheduler diagnostics, NUMA balancing analysis, and kernel selftests.

## Risks
Scheduler tracepoints are hot and ABI-sensitive. Changing fields or formats can break tooling. Call sites must avoid expensive work while tracing hot paths, and pointer fields such as work functions or scheduler entities must not be interpreted after object lifetime. Some comments note incomplete deadline handling for priority fields. Conditional events can make tooling config-dependent.

## Test Signals
Signals include `perf sched`, trace-cmd context-switch traces, fork/exec/exit stress tests, kthread worker tests, `CONFIG_SCHEDSTATS` enabled/disabled builds, NUMA balancing workloads, hung-task detection, BPF program attachment to sched tracepoints, and latency regressions when high-frequency events are enabled.
