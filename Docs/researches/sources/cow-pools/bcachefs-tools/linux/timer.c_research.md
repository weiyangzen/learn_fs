# File Research: sources/cow-pools/bcachefs-tools/linux/timer.c

## Purpose
Userspace kernel timer-list implementation backed by a pthread/kthread and min-heap.

## Key Responsibilities
- Maintains pending timers ordered by expiration jiffies.
- Implements `mod_timer()`, `del_timer()`, `timer_delete_sync()`, and `flush_timers()`.
- Starts the timer worker lazily on first `mod_timer()`.
- Runs callbacks outside the timer mutex and tracks callback execution with `timer_seq`.

## Implementation Notes
- Heap grows by doubling via `realloc()`.
- `timer_delete_sync()` removes pending timer and waits for an in-flight callback generation to finish.
- Timer wait uses `pthread_cond_timedwait()` against `CLOCK_REALTIME` after converting jiffies to nanoseconds.
- Constructor initializes heap capacity to 64.

## Dependencies
Uses pthread mutex/condition variables, local kthread helpers, jiffies/time helpers, and Linux timer API types.
