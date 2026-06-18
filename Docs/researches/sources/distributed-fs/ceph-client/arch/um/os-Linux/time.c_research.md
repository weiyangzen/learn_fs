# sources/distributed-fs/ceph-client/arch/um/os-Linux/time.c

## Purpose
Wraps host POSIX clocks/timers and idle sleep primitives for UML timekeeping.

## Important APIs, Types, and Functions
`os_persistent_clock_emulation()` reads `CLOCK_REALTIME`; `os_nsecs()` reads `CLOCK_MONOTONIC`. `os_timer_create()`, `os_timer_set_interval()`, `os_timer_one_shot()`, and `os_timer_disable()` manage per-CPU POSIX timers targeting SIGALRM. `os_idle_prepare()` creates a signalfd for SIGALRM/IPI wakeups; `os_idle_sleep()` blocks SIGALRM around resched checks and polls wake signals.

## Control Flow, State, and Persistence
Persistent state includes `event_high_res_timer[CONFIG_NR_CPUS]` and thread-local `wake_signals`. Timers are per UML CPU and use `SIGEV_THREAD_ID` to target the host thread returned by `gettid()`.

## Dependencies and Integration Points
Used by `kernel/time.c`, suspend idle entry, and SMP IPI signaling. Depends on `timer_alarm_pending()`, `uml_need_resched()`, `os_poll()`, and `IPI_SIGNAL`.

## Risks and Test Signals
Risks are incorrect per-thread timer delivery, missing signalfd wakeups, SIGALRM race around idle checks, and ignored timer_settime errors in oneshot. Test timers on SMP, idle wake by timer/IPI, suspend, high-res timer availability, and time-travel mode switching.
