# sources/distributed-fs/ceph-client/kernel/sched/clock.c

## Purpose
`clock.c` implements scheduler clock helpers, especially for architectures with unstable per-CPU clocks. It provides `sched_clock()`, `local_clock()`, `sched_clock_cpu()`, idle sleep/wakeup hooks, stability transitions, and a weak `running_clock()` implementation.

## Important APIs, Types, And Functions
Important functions include weak `sched_clock()`, `sched_clock_init()`, `sched_clock_cpu()`, `local_clock_noinstr()`, `local_clock()`, `sched_clock_tick()`, `sched_clock_tick_stable()`, `sched_clock_idle_sleep_event()`, `sched_clock_idle_wakeup_event()`, `clear_sched_clock_stable()`, and weak `running_clock()`. Under `CONFIG_HAVE_UNSTABLE_SCHED_CLOCK`, `struct sched_clock_data` stores `tick_raw`, `tick_gtod`, and `clock`; per-CPU instances are shared-aligned. Static keys track `sched_clock_running` and `__sched_clock_stable`.

## Control Flow
On stable-clock systems, scheduler clock reads mostly forward to architecture `sched_clock()`. On unstable-clock systems, initialization computes offsets between GTOD (`ktime_get_ns()`) and raw `sched_clock()`, later marks the clock stable if no instability is detected, or schedules work to clone a safe timestamp to all CPUs and mark it unstable if instability is detected after boot.

When unstable, `sched_clock_local()` reads raw time, clamps negative deltas to zero, combines GTOD base plus raw deltas, clamps within a tick-sized window, and atomically updates the per-CPU clock monotonically. `sched_clock_remote()` couples local and remote per-CPU clocks by taking the larger value, with special atomic read handling for 32-bit. Tick and idle hooks stamp GTOD/raw samples and resync after idle wakeups unless timekeeping is suspended.

## State And Persistence
State is volatile per-CPU scheduler clock data plus global offsets/static keys. It persists only for the running boot. Stability transitions affect tick dependency state and irqtime accounting. There is no disk persistence.

## Dependencies And Integration Points
The file depends on timekeeping (`ktime_get_ns()`), raw architecture `sched_clock()`, static keys, tick dependencies, workqueues, irq/preemption controls, CPU IDs, and optional `generic_sched_clock_init()`. Scheduler, tracing, irqtime, idle, and accounting code consume these clock APIs.

## Risks
Clock code is high risk because it runs in NMI/noinstr-sensitive contexts and must preserve monotonicity without heavy locking. Incorrect offset/stability transitions can create time jumps, bad runtime accounting, scheduler latency artifacts, or tracing anomalies. Remote clock coupling must be atomic on 32-bit and safe against concurrent NMI updates.

## Test Signals
Signals include boot logs marking sched_clock stable/unstable, successful operation with `tsc=unstable`, scheduler accounting sanity, tracing timestamps without backward local movement, idle wakeup tests, and lockdep/noinstr validation. Cross-CPU comparisons may go backward by design and should not be tested as globally monotonic.
