# File Research: sources/block-storage/kvdo/vdo/uds-threads.h

This header declares the UDS threading abstraction over Linux kernel primitives. It defines `struct cond_var`, opaque `struct thread`, and `struct barrier` implemented with semaphores and arrival counters.

Declared APIs cover thread creation/join/exit, current thread id, CPU count, once-only initialization, barriers, condition variables, scheduler yield, and inline mutex/semaphore wrappers.

The semaphore acquire helper intentionally loops on `down_interruptible()` and sleeps briefly after signals to avoid long kernel stall warnings and CPU spinning during operations such as dmsetup-driven waits. `uds_attempt_semaphore()` supports try-acquire or timed acquire based on a relative `ktime_t`.
