# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-condvar.c

Read completely: 465 lines.

This implements Solaris-style condition variables for the Linux SPL using Linux wait queues, scheduler states, atomic waiter/reference counters, and high-resolution timeout support.

Key responsibilities:
- Initializes and destroys `kcondvar_t` objects.
- Implements uninterruptible, interruptible, I/O, idle, timed, and high-resolution condition waits.
- Implements signal and broadcast wakeups.
- Exposes the tunable `spl_schedule_hrtimeout_slack_us`, capped at 1000 microseconds.

Important implementation details:
- Each condvar tracks `cv_magic`, `cv_event`, `cv_destroy`, `cv_waiters`, `cv_refs`, and a debug `cv_mutex`.
- Wait paths increment references, assert all waiters use the same mutex, call `prepare_to_wait_exclusive()`, drop the mutex, schedule, finish the wait, decrement waiter/ref counts, and reacquire the mutex.
- Destruction marks `CV_DESTROY`, drops the initial ref, and waits until no refs, no waiters, and no active waitqueue entries remain.
- Timed jiffies waits return `1` for wake before timeout and `-1` for timeout; signal variants return `0` when a signal is pending.
- High-resolution waits use `schedule_hrtimeout_range()` with configured slack and support relative or absolute Illumos-style flags.
- Idle waits block all signals around interruptible sleep to emulate idle wait semantics.

Dependencies and interactions:
- Used by SPL/ZFS code expecting Illumos `cv_*` semantics over Linux scheduler primitives.
- Exports all public condition variable entry points used by other OpenZFS modules.

Reliability notes:
- The `cv_mutex` tracking is intentionally best-effort and racy only for debug validation.
- The jiffies timed wait code explicitly notes it does not handle jiffies wrap properly.
