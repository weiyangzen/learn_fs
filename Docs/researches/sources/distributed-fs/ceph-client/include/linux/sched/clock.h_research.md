# sources/distributed-fs/ceph-client/include/linux/sched/clock.h

Purpose: declares scheduler clock interfaces that provide fast runtime timestamps for scheduler accounting, tracing, and CPU-local timing.

Important APIs and types: `sched_clock()`, `sched_clock_noinstr()`, `running_clock()`, `sched_clock_cpu()`, `sched_clock_init()`, `sched_clock_tick()`, idle sleep/wakeup hooks, `cpu_clock()`, `local_clock()`, `local_clock_noinstr()`, clock stability controls, and IRQ-time accounting toggles are exported or stubbed by config.

Control flow: architecture or generic clock code initializes the source, scheduler/timer paths tick or mark idle transitions, and consumers choose local or CPU-specific clocks depending on monotonicity and instrumentation constraints.

State and persistence: clock stability, offsets, and per-CPU clock accounting live in scheduler clock implementation. The values are volatile runtime time sources, not persistent state.

Dependencies and integration points: depends on SMP and optional unstable/generic scheduler clock configs. Integrates scheduler accounting, tracing, idle/nohz, IRQ time accounting, and architecture clock sources.

Risks and test signals: risks include comparing clocks across CPUs, using `sched_clock()` where monotonicity is required, noinstr violations, unstable-clock drift, and IRQ-time opt-in overhead. Test with clocksource changes, suspend/idle, NOHZ, IRQ accounting, tracing noinstr validation, and multi-CPU timestamp monotonicity expectations.
