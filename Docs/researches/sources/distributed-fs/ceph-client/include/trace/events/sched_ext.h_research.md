
# sources/distributed-fs/ceph-client/include/trace/events/sched_ext.h

## Purpose
Provides tracepoints for the `sched_ext` extensible scheduler framework, mainly for dumping textual state, recording named scheduler-extension events, and observing bypass load-balancing decisions.

## Important APIs, Types, and Functions
Defines `sched_ext_dump`, `sched_ext_event`, and `sched_ext_bypass_lb`. `sched_ext_dump` stores a single string line, `sched_ext_event` stores a string name plus signed delta, and `sched_ext_bypass_lb` records node, CPU count, task count, number balanced, and min/max distribution before and after bypass balancing.

## Control Flow
The sched_ext core or BPF-backed scheduler code emits these tracepoints when producing diagnostic dump lines, accounting named events, or bypassing normal load-balance behavior. Each event copies scalar or string values into the trace record immediately.

## State and Persistence
No state is owned here. Trace buffers persist the copied strings and counters. The events reflect transient scheduler-extension diagnostics and balancing outcomes rather than stable kernel state.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and the sched_ext implementation. Integrates with tracefs/perf/BPF tooling used to debug BPF schedulers, load-balance bypass behavior, and scheduler-extension dumps.

## Risks
String-based event names and dump lines are flexible but weaker ABI than structured fields. High-volume dump/event emission can distort scheduler behavior when enabled. Consumers must treat deltas and balancing counters as point-in-time diagnostics.

## Test Signals
Signals include sched_ext selftests, loading sample BPF schedulers, enabling `events/sched_ext/*`, forcing load imbalance, verifying dump line capture, and checking that tracing does not destabilize scheduler-extension workloads.
