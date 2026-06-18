# File Research: sources/cow-pools/bcachefs-tools/linux/semaphore.c

## Purpose
Kernel-style counting semaphore implementation adapted for userspace compatibility.

## Key Responsibilities
- Implements `down()`, `down_trylock()`, `down_timeout()`, and `up()`.
- Uses `sem->lock`, `sem->count`, and `sem->wait_list`.
- Sleeps contended waiters via `schedule_timeout()`.
- Wakes the first waiter in `__up()` with `wake_up_process()`.

## Implementation Notes
- `down_trylock()` follows Linux semaphore convention: returns `0` on success, `1` on failure.
- Timeout waits return `-ETIME`.
- Interruptible/killable variants are not present in this file; all contended waits use `TASK_UNINTERRUPTIBLE`.

## Dependencies
Depends on local `linux/sched.h`, spinlock, list, and semaphore definitions.
