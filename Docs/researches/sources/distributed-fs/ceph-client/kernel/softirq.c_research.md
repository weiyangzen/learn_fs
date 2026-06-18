# sources/distributed-fs/ceph-client/kernel/softirq.c

## Purpose
`softirq.c` implements Linux softirq dispatch, bottom-half enable/disable accounting, tasklets, interrupt entry/exit softirq invocation, and the per-CPU `ksoftirqd` fallback threads. It is the common deferred interrupt work engine used by networking, timers, RCU, block IRQ polling, scheduler, tasklets, and workqueue softirq actions.

## Important APIs, types, and functions
- Global/per-CPU state: `softirq_vec[NR_SOFTIRQS]`, `irq_stat`, `ksoftirqd`, `softirq_to_name`, and tasklet per-CPU queues.
- Bottom-half APIs: `__local_bh_disable_ip()`, `__local_bh_enable_ip()`, `_local_bh_enable()` on non-RT, and `local_bh_blocked()` on RT.
- Dispatch APIs: `open_softirq()`, `raise_softirq()`, `raise_softirq_irqoff()`, `__raise_softirq_irqoff()`, `do_softirq()`, `__do_softirq()`.
- IRQ integration: `irq_enter_rcu()`, `irq_enter()`, `irq_exit_rcu()`, `irq_exit()`, `do_softirq_post_smp_call_flush()` on RT.
- Tasklet APIs: `tasklet_setup()`, `tasklet_init()`, `__tasklet_schedule()`, `__tasklet_hi_schedule()`, `tasklet_kill()`, `tasklet_unlock_wait()`, `tasklet_unlock_spin_wait()`.
- Threading: `softirq_threads` descriptor for `ksoftirqd/%u`; optional forced-threading `timer_thread` for `ktimers/%u`.

## Control flow
Softirq producers set a per-CPU pending bit with interrupts disabled. Interrupt exit checks pending work after decrementing hardirq context and either runs softirqs inline/on the IRQ stack or wakes `ksoftirqd`, depending on context and forced IRQ threading. `handle_softirqs()` snapshots pending bits, clears the per-CPU pending word, enables interrupts, invokes each registered action with tracing/stat accounting, then loops for bounded restarts until time, reschedule, or restart limits force wakeup of `ksoftirqd`. Tasklet scheduling appends to a per-CPU list and raises `TASKLET_SOFTIRQ` or `HI_SOFTIRQ`; the action drains the list, runs enabled tasklets under per-tasklet serialization, and requeues locked/disabled tasklets.

## State and persistence behavior
Softirq state is transient, CPU-local kernel state: pending bitmaps, per-CPU tasklet lists, `ksoftirqd` task pointers, optional timer-thread pending masks, and RT-specific `softirq_ctrl` counters/locks. No userspace-persistent state is stored. Pending work migrates during CPU hotplug through `takeover_tasklets()` and `workqueue_softirq_dead()`.

## Dependencies and integration points
This file integrates with interrupt entry code, RCU context tracking, tick/nohz handling, hrtimer deferred rearming, workqueues, tracing (`trace/events/irq.h`), kernel stats, lockdep, freezer/kthreads, `smpboot_register_percpu_thread()`, and optional PREEMPT_RT behavior. It relies on architecture softirq stack helpers and optional `CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK`.

## Risks
Softirq dispatch is latency-critical and concurrency-sensitive. Incorrect preempt count restoration is detected and repaired with an error log, but indicates broken handlers. Starvation risk is bounded by `MAX_SOFTIRQ_TIME` and `MAX_SOFTIRQ_RESTART`; changing these affects latency/fairness. PREEMPT_RT paths split accounting between task and per-CPU counters, so lock/unlock imbalance can block softirq progress. Tasklets are legacy and risky when killed or waited from interrupt/atomic contexts.

## Test signals
Signals include boot-time softirq init, CPU hotplug with pending tasklets, networking/timer/RCU load, lockdep IRQ flag tests, PREEMPT_RT bottom-half tests, forced IRQ threading, and tracepoints for raise/entry/exit. Runtime warnings about preempt count mismatch, tasklet state mismatch, or local BH misuse are high-value regression indicators.
