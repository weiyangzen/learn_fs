# sources/distributed-fs/ceph-client/kernel/time/sched_clock.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/sched_clock.c` provides generic `sched_clock()` support by extending a low-level hardware counter into a monotonic 64-bit nanosecond value. It handles clock registration, epoch updates before counter wrap, NMI-safe latch reads, suspend/resume behavior, and optional IRQ time accounting enablement. The complete 333-line source was read.

## Important APIs, Types, and Functions

Important types are `struct clock_data` and `struct clock_read_data`. Externally visible functions include `sched_clock_read_begin`, `sched_clock_read_retry`, `sched_clock_noinstr`, `sched_clock`, `sched_clock_register`, `generic_sched_clock_init`, `sched_clock_suspend`, and `sched_clock_resume`. Internal helpers include `jiffy_sched_clock_read`, `cyc_to_ns`, `__sched_clock`, `update_clock_read_data`, `update_sched_clock`, `sched_clock_poll`, and `suspended_sched_clock_read`. The file registers syscore suspend/resume callbacks and exposes the `irqtime` core parameter.

## Control Flow

Before a hardware sched clock is registered, the implementation uses jiffies as a fallback source. `sched_clock_register` rejects slower sources than the current one, calculates mult/shift and wrap duration, samples the new and old clocks to preserve epoch continuity, updates both latch copies, restarts the wrap-protection hrtimer if active, and enables IRQ time accounting for fast enough clocks or explicit `irqtime`. `sched_clock()` disables preemption, marks its critical section atomic for KCSAN, and reads the active latch copy until the seqcount is stable. `generic_sched_clock_init` finalizes the fallback if needed, updates the epoch, and starts the polling hrtimer. Suspend freezes reads at the last epoch and cancels the poll timer; resume samples the actual clock as the new epoch and restarts polling.

## State and Persistence Behavior

State is global and in memory: `cd` stores the current read function, conversion parameters, epoch cycle/ns values, counter mask, rate, and wrap interval. Two `read_data` copies are maintained so NMI readers never observe partially updated conversion data. `sched_clock_timer` periodically advances the epoch before the underlying counter wraps.

## Dependencies and Integration Points

Dependencies include clocksource math helpers, hrtimers, seqcount latch APIs, scheduler clock headers, syscore operations, module/core parameters, KCSAN annotations, and timekeeping. Architecture or platform code integrates by calling `sched_clock_register` with a counter read function, bit width, and rate. Scheduler accounting, tracing, IRQ time accounting, and timestamp users consume `sched_clock()`.

## Risks and Edge Cases

The key risk is preserving monotonic-looking nanosecond output while changing clock sources or crossing hardware counter wraps. Registration must run with interrupts disabled and must not publish mixed epoch/conversion data. Suspend handling deliberately swaps the read function to return a stable cycle value; missing that would let stopped hardware counters appear to jump. Very slow or narrow counters require correct wrap polling or `sched_clock()` can regress.

## Test Signals

Useful signals include boot logs showing registered source rate/resolution/wrap; architecture tests registering fallback and hardware clocks; suspend/resume timestamp monotonicity tests; long-running wrap tests for narrow counters; tracing/scheduler clock sanity checks; KCSAN/lockdep coverage around latch updates; and IRQ time accounting behavior with `irqtime=` overrides.
