# sources/distributed-fs/ceph-client/kernel/time/posix-timers.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-timers.c` is the generic POSIX clocks and timers core. It implements POSIX timer object allocation, timer ID hashing, syscall entry points, signal queue/rearm semantics, common hrtimer-backed clock behavior, time namespace conversions, clock dispatch, and initialization of the POSIX timer cache/hash. The complete 1567-line source was read.

## Important APIs, Types, and Functions

Public syscall implementations include `timer_create`, `timer_gettime`, `timer_getoverrun`, `timer_settime`, `timer_delete`, `clock_settime`, `clock_gettime`, `clock_adjtime`, `clock_getres`, and `clock_nanosleep`, plus compat variants. Cross-file APIs include `posixtimer_deliver_signal`, `posix_timer_queue_signal`, `posixtimer_create_prctl`, `posixtimer_free_timer`, `common_timer_get`, `common_timer_set`, `posix_timer_set_common`, `common_timer_del`, and `do_clock_adjtime`. Important types and tables are `struct timer_hash_bucket`, `struct k_itimer`, `struct k_clock`, the `posix_clocks[]` dispatch table, and the static clock implementations for realtime, monotonic, raw, coarse, boottime, TAI, alarm, CPU, dynamic, and auxiliary clocks.

## Control Flow

Timer creation maps a clock ID to `struct k_clock`, allocates a `k_itimer`, reserves a unique per-process timer ID in a hash bucket, initializes signal notification metadata, copies the ID to user space, invokes the clock-specific `timer_create`, and only then marks the timer valid and links it into `signal->posix_timers`. Timer lookup is RCU-protected and then validated under `it_lock` so deletion cannot race with syscall operations.

Hrtimer-backed timers use `common_timer_set`: optionally read old state, try to cancel active hrtimer callback, reset overrun state, translate absolute times from time namespace to host time, arm via `timer_arm`, and mark non-`SIGEV_NONE` timers armed. Hrtimer expiry calls `posix_timer_fn`, which queues a signal and leaves interval rearming to signal delivery. `posixtimer_deliver_signal` drops `siglock`, locks the timer, verifies signal sequence numbers, rearms interval timers, updates overrun counts, and releases the queued reference. Deletion invalidates the timer under `siglock`, removes it from process and ignored lists, repeatedly cancels with `TIMER_RETRY` handling, then unhashes and drops references.

## State and Persistence Behavior

State is in memory only: a boot-time hash table, a slab cache, each process signal struct's timer list and next ID counter, per-timer signal metadata, overrun counters, sequence counters, hrtimer state, and reference counts. CRIU-oriented restore mode can request exact timer IDs and moves the allocator counter past restored IDs. Timer lifetime is RCU/refcounted because queued timer signals may outlive deletion from syscall-visible structures.

## Dependencies and Integration Points

The file depends on hrtimers, signal queues, PID references, ucounts for `RLIMIT_SIGPENDING`, RCU, `jhash`, timekeeping, time namespaces, dynamic POSIX clocks, alarm timers, CPU timers from `posix-cpu-timers.c`, and optional aux clocks. It integrates with signal delivery through `posixtimer_deliver_signal`, with `/proc/$PID/timers` through process timer lists, with CRIU through `PR_TIMER_CREATE_RESTORE_IDS_*`, and with architecture compat syscall layers.

## Risks and Edge Cases

Timer lifetime and signal sequencing are the central risks. A timer ID is visible to user space before the timer is valid, so invalid-marker handling on `it_signal` must remain correct. `SIGEV_NONE` timers are never enqueued and must be advanced lazily by gettime. Relative `CLOCK_REALTIME` timers intentionally switch to monotonic backing while preserving `it_clock`, which is easy to break when touching `common_hrtimer_arm`. `TIMER_RETRY` loops are required to avoid deleting or reprogramming while callbacks run, especially on PREEMPT_RT. `clockid_to_kclock` must handle negative dynamic and CPU clock IDs before array indexing, with nospec protection for positive IDs.

## Test Signals

Strong tests include POSIX timer syscall suites across realtime, monotonic, boottime, TAI, CPU, alarm, and dynamic clocks; signal delivery and interval rearm tests; overrun clamp tests; CRIU restore-ID tests; timer delete while callback/signal pending stress; `SIGEV_THREAD_ID` permission tests; time namespace absolute timer and nanosleep tests; compat 32-bit syscall tests; and KASAN/KCSAN/lockdep stress around timer lookup, delete, and exit.
