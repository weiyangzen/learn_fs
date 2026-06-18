# sources/distributed-fs/ceph-client/include/linux/hrtimer_defs.h

## Purpose
`hrtimer_defs.h` defines the internal per-clock and per-CPU base structures that organize hrtimers. These structures back the public hrtimer API but are split out so type definitions can be shared without pulling in the full API.

## Important APIs, Types, And Functions
`struct hrtimer_clock_base` stores the owning CPU base, base index, clock ID, sequence counter, next expiry, running timer pointer, active timerqueue head, and clock offset. `enum hrtimer_base_type` enumerates monotonic, realtime, boottime, TAI, and soft variants. `struct hrtimer_cpu_base` stores the raw spinlock, CPU number, active base bitmap, clock-set sequence, high-resolution/deferred/online/softirq state, highres statistics, PREEMPT_RT wait/softirq locks, next expiry/timer caches, deferred expiry cache, clock base array, and call-single data.

## Control Flow And State
Hrtimer enqueue/dequeue/interrupt paths lock the CPU base, choose a clock base, insert/remove timerqueue nodes, update next-expiry caches, run callbacks, and coordinate highres clockevent programming. Clock-set and CPU hotplug paths update sequence and online/migration state. PREEMPT_RT adds softirq expiry and cancel-wait state.

## Dependencies And Integration Points
It depends on ktime, timerqueue, seqlock, raw spinlocks, per-CPU call-single data, high-resolution timer config, and PREEMPT_RT. `hrtimer.h` includes it.

## Risks
These structures are concurrency-critical. Risks include false sharing/alignment regressions, stale `next_timer` dereference despite comments saying it is only an optimization, sequence counter misuse around running callbacks, and missing updates to active/next expiry state when adding new base types.

## Test Signals
Stress timer enqueue/cancel/run under CPU hotplug, clock changes, PREEMPT_RT, highres interrupts, soft timers, deferred rearm, and lockdep/RT lock validation.
