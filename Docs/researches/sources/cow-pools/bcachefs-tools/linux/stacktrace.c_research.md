# File Research: sources/cow-pools/bcachefs-tools/linux/stacktrace.c

## Purpose
Userspace implementation of `stack_trace_save_tsk()` using libunwind.

## Key Responsibilities
- Captures stack traces from the current thread directly.
- Captures stack traces from another thread by delivering `SIGRTMIN` and unwinding inside the target thread's signal handler.
- Serializes cross-thread backtrace requests with a global mutex and single in-flight request slot.

## Implementation Notes
- Uses `pthread_once()` to install the signal handler.
- Skips the signal-handler/current helper frame plus requested `skipnr`.
- Busy-waits with `sched_yield()` until the target handler marks the request done.
- Intended for debug paths, not high-contention tracing.

## Dependencies
Requires libunwind, pthreads, signals, and local `task_struct.thread`.
