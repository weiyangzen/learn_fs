# sources/distributed-fs/ceph-client/kernel/locking/Makefile

## Purpose
`kernel/locking/Makefile` selects core kernel locking implementation objects and disables instrumentation that would distort or recursively enter locking code.

## Important APIs, Types, and Functions
It disables KCOV for the directory, marks several objects for context analysis, builds core mutex/semaphore/rwsem/percpu-rwsem objects, disables KASAN/KCSAN for lockdep, removes ftrace instrumentation from lockdep and mutex-debug objects when function tracing is enabled, and conditionally builds debug, lockdep, spinlock, queued spinlock/rwlock, rtmutex, PREEMPT_RT, torture, ww mutex selftest, and lock event objects.

## Control Flow
Kbuild uses configuration symbols such as `DEBUG_IRQFLAGS`, `DEBUG_MUTEXES`, `LOCKDEP`, `PROC_FS`, `SMP`, `QUEUED_SPINLOCKS`, `RT_MUTEXES`, `PREEMPT_RT`, `LOCK_TORTURE_TEST`, `WW_MUTEX_SELFTEST`, and `LOCK_EVENT_COUNTS` to select implementation files.

## State and Persistence Behavior
No runtime state. Build selection determines which locking implementation and diagnostics exist in the kernel.

## Dependencies and Integration Points
It integrates with sanitizer/ftrace build flags, lockdep, debugfs lock event support, architecture spinlock implementations, PREEMPT_RT, and test modules.

## Risks and Test Signals
Instrumentation on lockdep or low-level locks can recurse and break the kernel, so flag removal matters. Build tests should cover tracing, sanitizer, PREEMPT_RT, lockdep, queued spinlock, and lock event configurations.
