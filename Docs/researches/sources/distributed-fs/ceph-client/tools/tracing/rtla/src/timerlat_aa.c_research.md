# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_aa.c

## Purpose
`timerlat_aa.c` implements timerlat auto-analysis. It collects timerlat, osnoise, stack, scheduler, and workqueue events in a separate trace instance, correlates them per CPU, and prints explanations for threshold-triggered IRQ or thread latency.

## Important APIs, Types, and Functions
`struct timerlat_aa_data` stores per-CPU state: current phase, IRQ/thread latency sequence and timestamps, blocking thread, timer IRQ timing, previous IRQ, interference sums, trace sequences for formatted details, current task, and kworker data. `struct timerlat_aa_context` stores global AA configuration, per-CPU data, and owning tool. Public APIs are `timerlat_aa_init()`, `timerlat_aa_destroy()`, and `timerlat_auto_analysis()`. Event handlers cover `ftrace:timerlat`, osnoise NMI/IRQ/softirq/thread noise, kernel stack, sched switch, and workqueue execute start.

## Control Flow
Initialization allocates global context, per-CPU data, trace sequences, enables/registers required events, and stores the context in a static pointer. During tracing, handlers maintain a state machine from waiting-for-IRQ to waiting-for-thread, capture IRQ latency, thread latency, blocking thread, interference durations, stack traces, and current tasks. On threshold stop, `timerlat_auto_analysis()` iterates collected events, scales thresholds to ns, selects CPUs that crossed IRQ or thread thresholds, prints per-CPU analysis, reports max exit-from-idle latency, and optionally dumps current tasks/kworker functions.

## State and Persistence
State is process-local but tied to enabled events in the AA trace instance. Cleanup unregisters handlers, disables events, destroys trace sequences, and frees per-CPU data/context. Output is printed to stdout.

## Dependencies and Integration Points
It depends on libtraceevent field extraction, tracefs event enabling, RTLA trace helpers, `timerlat.h`, and utility formatting functions. It is created by `timerlat_enable()` and invoked by `timerlat_analyze()` when tracing stopped.

## Risks and Edge Cases
The global singleton context means only one AA session is supported per process. Correlation relies on event ordering and timestamp relationships from different clocks; the code explicitly guards some negative timing cases. Many `tep_get_field_*()` calls assume expected event fields exist. `strncpy()` into fixed comm buffers may omit NUL termination for maximum-length names. `max_exit_from_idle_cpu` is printed only when a max value exists, but should still be initialized defensively if logic changes.

## Test Signals
Test IRQ-threshold and thread-threshold stops, idle-exit cases, NMI/IRQ/softirq/thread interference, stack formats, dump-tasks mode, missing optional events, unregister cleanup, and repeated init/destroy cycles.
