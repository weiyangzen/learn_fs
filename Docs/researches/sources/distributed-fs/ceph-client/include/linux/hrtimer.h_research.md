# sources/distributed-fs/ceph-client/include/linux/hrtimer.h

## Purpose
`hrtimer.h` is the public high-resolution timer API. It combines mode definitions, sleeper support, expiry manipulation helpers, high-resolution enablement hooks, timerfd notifications, initialization/start/cancel/query/forward APIs, precise sleep helpers, queue execution, CPU hotplug hooks, and debug/sysrq support.

## Important APIs, Types, And Functions
`enum hrtimer_mode` defines absolute/relative, pinned, soft/hard, and lazy-rearm modes. `struct hrtimer_sleeper` combines a timer with a task pointer. Important helpers include `hrtimer_set_expires*()`, `hrtimer_add_expires*()`, `hrtimer_get_expires()`, `hrtimer_cb_get_time()`, `hrtimer_expires_remaining*()`, `hrtimer_setup()`, `hrtimer_setup_on_stack()`, `hrtimer_start_range_ns()`, `hrtimer_start()`, `hrtimer_cancel()`, `hrtimer_try_to_cancel()`, `hrtimer_start_expires()`, `hrtimer_get_remaining()`, `hrtimer_active()`, `hrtimer_is_queued()`, `hrtimer_update_function()`, `hrtimer_forward()`, `hrtimer_forward_now()`, nanosleep/schedule timeout helpers, `hrtimer_run_queues()`, `hrtimers_init()`, and CPU hotplug functions.

## Control Flow And State
Callers initialize a timer with callback, clock ID, and mode; set/start expiry; the timerqueue stores it on a per-CPU/per-clock base; clockevent interrupts or softirq processing run callbacks; callbacks return restart or no-restart. Sleepers wake tasks by clearing the task pointer. Relative low-resolution timers adjust remaining time for added resolution slack. State lives in `struct hrtimer`, per-CPU bases, active timer queues, running callback pointers, highres static key, timerfd notifications, and CPU hotplug state.

## Dependencies And Integration Points
It depends on `hrtimer_defs.h`, `hrtimer_rearm.h`, `hrtimer_types.h`, ktime, timerqueue, percpu tick devices, PREEMPT_RT, timerfd, clockevents, scheduler sleep, and CPU hotplug.

## Risks
Risks include cancel races with running callbacks, updating functions while queued, mode confusion between soft/hard on RT, lazy rearm causing extra expiry, wrong absolute/relative mode, and using lockless queue state as stable truth. On-stack timers need debug-object destruction.

## Test Signals
Run hrtimer selftests, nanosleep/schedule_hrtimeout tests, timerfd clock-set/resume tests, PREEMPT_RT cancel/wait paths, CPU hotplug migration, highres enabled/disabled builds, lazy hrtick rearm behavior, and callback restart/forward loops.
