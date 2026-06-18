# File Research: sources/cow-pools/bcachefs-tools/linux/sched.c

## Purpose
Userspace scheduler/task shim for kernel-style blocking and wakeup primitives.

## Key Responsibilities
- Defines thread-local `current`.
- Joins and frees task structs in `__put_task_struct()`.
- Implements `wake_up_process()` using futex wake.
- Implements `schedule()` by waiting on the current task state with futex wait.
- Implements `schedule_timeout()` using a stack timer to wake the current task.
- Initializes a main thread `task_struct` in a constructor.
- Opens `/dev/urandom` when `SYS_getrandom` is unavailable.

## Dependencies
Uses pthread task state indirectly through `task_struct`, userspace RCU futex support, `linux/timer.h`, futex syscalls, and jiffies.

## Integration Notes
This file is foundational for semaphores, waitqueues, workqueues, kthreads, timers, and shrinkers in the bcachefs-tools kernel-compat layer.
