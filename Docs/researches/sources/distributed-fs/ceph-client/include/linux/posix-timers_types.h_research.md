# sources/distributed-fs/ceph-client/include/linux/posix-timers_types.h

Purpose: provides lightweight POSIX CPU timer type definitions and clockid bitfield macros for use in task and signal structures.

Important APIs and types: macros decode CPU clock IDs into PID, per-thread bit, and clock type (`CPUCLOCK_PROF`, `CPUCLOCK_VIRT`, `CPUCLOCK_SCHED`, `CLOCKFD`). `struct posix_cputimer_base` stores next event and timerqueue head per CPU clock type. `struct posix_cputimers` groups the three bases plus active/expiry flags. `struct posix_cputimers_work` stores task-work callback, mutex, and scheduled flag for task-work based expiry.

Control flow: scheduler and POSIX timer code use the bitfield macros to classify clock IDs and use `posix_cputimers` containers embedded in task/signal state to queue and locate CPU timers efficiently.

State and persistence: runtime per-task/per-signal CPU timer state only. With `CONFIG_POSIX_TIMERS` disabled, `struct posix_cputimers` is empty.

Dependencies and integration points: depends on mutex and timerqueue type headers, and is included by task/signal/timer code that must avoid the heavier POSIX timer implementation header.

Risks and test signals: risks include clockid encoding drift, next-event cache not initialized to `U64_MAX`, active/expiry flag races, and code assuming non-empty structs in disabled builds. Test CPU timer clockid encoding/decoding, task and process timer initialization, task-work expiry scheduling, and disabled POSIX timer builds.
