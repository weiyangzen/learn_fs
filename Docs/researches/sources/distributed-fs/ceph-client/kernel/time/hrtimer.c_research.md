# sources/distributed-fs/ceph-client/kernel/time/hrtimer.c

Purpose: implements high-resolution timers, per-CPU timer bases, enqueue/cancel/restart semantics, hardirq and softirq expiry, nanosleep, clock-set reprogramming, high-res activation, and CPU hotplug migration.

Important APIs and flow: exported APIs include `hrtimer_setup()`, `hrtimer_start_range_ns()`, `hrtimer_try_to_cancel()`, `hrtimer_cancel()`, `hrtimer_forward()`, `__hrtimer_get_remaining()`, `hrtimer_cb_get_time()`, sleeper helpers, nanosleep syscalls, and CPU hotplug hooks. Timers live in per-CPU `hrtimer_bases` split by clock and hard/soft context. Start locks the current base, converts relative expiries, may migrate to a nohz housekeeping CPU, enqueues into a timerqueue, and reprograms only the local clockevent when needed. Expiry removes the timer, drops the base lock around callbacks, handles restart, and uses sequence barriers so `hrtimer_active()` avoids false negatives. High-res interrupt processes hard timers, raises softirq for soft timers, detects hangs, and rearms the clockevent.

State and persistence: per-CPU base state tracks active bases, next hard/soft timers, offsets, high-res mode, deferred rearm, hang counters, online state, and running callbacks. Debug objects track timer lifetime when enabled.

Dependencies and integration: depends on clockevents/tick, timekeeping offsets, scheduler/nohz housekeeping, PREEMPT_RT policy, timerfd notification, syscalls, freezer, CPU hotplug, and tracepoints.

Risks and test signals: high-risk areas are base migration, callback/cancel races, PREEMPT_RT soft callback waits, clock-set IPIs, deferred rearm, hang avoidance, low-res rounding, and CPU dying migration. Test with hrtimer selftests, nanosleep restart/remain paths, nohz/highres toggles, RT kernels, CPU hotplug, timerfd after clock_settime, and stress cancellation from callback/remote CPUs.
