# sources/distributed-fs/ceph-client/kernel/time/sleep_timeout.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/sleep_timeout.c` implements core kernel sleep helpers built on timer-wheel timers, hrtimer sleepers, and scheduler state transitions. It provides jiffy-based `schedule_timeout*`, high-resolution timeout helpers, and public millisecond/microsecond sleep APIs. The complete 377-line source was read.

## Important APIs, Types, and Functions

The file defines `struct process_timer`, `process_timeout`, exported `schedule_timeout`, `schedule_timeout_interruptible`, `schedule_timeout_killable`, `schedule_timeout_uninterruptible`, `schedule_timeout_idle`, `schedule_hrtimeout_range_clock`, `schedule_hrtimeout_range`, `schedule_hrtimeout`, `msleep`, `msleep_interruptible`, and `usleep_range_state`. It uses `struct timer_list`, `struct hrtimer_sleeper`, task states, jiffies conversion helpers, and hrtimer range APIs.

## Control Flow

`schedule_timeout` handles `MAX_SCHEDULE_TIMEOUT` by scheduling without a timer, rejects negative timeouts with diagnostics, creates an on-stack timer that wakes `current`, schedules, deletes/destroys the timer, and returns nonnegative remaining jiffies. The convenience wrappers set the current task state before calling it. `schedule_hrtimeout_range_clock` handles zero, infinite, and finite hrtimer sleeps: it creates an on-stack hrtimer sleeper, applies slack, starts it, schedules if the sleeper task remains set, cancels and destroys the timer, restores `TASK_RUNNING`, and returns 0 for expiry or `-EINTR` for early wake. `msleep` and `msleep_interruptible` loop over remaining jiffies. `usleep_range_state` repeatedly performs an absolute hrtimer range sleep until the minimum time has elapsed.

## State and Persistence Behavior

There is no persistent storage. All timers and sleepers are stack allocated and destroyed before return. The functions temporarily mutate the calling task state and rely on timer callbacks to wake that task. Return values communicate remaining time or interruption; no state survives except scheduler accounting and timer subsystem side effects.

## Dependencies and Integration Points

Dependencies include the timer wheel, hrtimers, scheduler state APIs, signal pending checks, jiffies conversion, delay APIs, and tick internals for timer/nohz integration. These helpers are widely consumed by kernel subsystems that need sleepable delays outside atomic context.

## Risks and Edge Cases

Callers must set a sleepable task state before many helpers or they will not actually sleep. On-stack timer and hrtimer objects require strict delete/destroy ordering. Negative jiffy timeout is treated as a caller bug but returns safely. `schedule_hrtimeout_range_clock(NULL, ...)` means infinite sleep and returns `-EINTR` after wake. `usleep_range_state` must handle `max < min` defensively and must not return before the minimum deadline.

## Test Signals

Signals include timer selftests for remaining jiffy values, interruptible sleep signal tests, hrtimer range/slack behavior, lockdep/KASAN checks for on-stack timer lifetime, `msleep_interruptible` early-return tests, and latency/power tests that verify `usleep_range_state` coalesces wakeups while respecting minimum sleep duration.
