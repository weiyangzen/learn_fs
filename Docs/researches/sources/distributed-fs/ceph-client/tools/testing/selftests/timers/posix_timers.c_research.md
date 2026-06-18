# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/posix_timers.c

## Purpose
This kselftest exercises Linux POSIX and interval timer behavior across wall-clock timers, CPU-time timers, signal delivery modes, overrun accounting, `SIGEV_NONE`, and timer ID restoration. It is a broad regression suite for timer creation, arming, signal queuing, deletion, rearming, and per-thread/process CPU accounting.

## Important APIs, Types, and Functions
Core timer APIs are `setitimer()`, `timer_create()`, `timer_settime()`, `timer_gettime()`, `timer_delete()`, `clock_gettime()`, `gettimeofday()`, and raw `timer_create`/`timer_delete` syscalls. `check_itimer()` covers `ITIMER_VIRTUAL`, `ITIMER_PROF`, and `ITIMER_REAL`; `check_timer_create()` covers `CLOCK_THREAD_CPUTIME_ID` and `CLOCK_PROCESS_CPUTIME_ID`; `check_sig_ign()`, `check_rearm()`, `check_delete()`, `check_sigev_none()`, `check_gettime()`, and `check_overrun()` cover signal queue semantics. `check_timer_create_exact()` uses `prctl(PR_TIMER_CREATE_RESTORE_IDS, ...)` and raw syscalls to verify restored timer IDs.

## Control Flow
`main()` emits a kselftest plan, runs the timer ID restore test, checks interval timers and POSIX CPU timers, verifies CPU timer signal distribution, optionally runs newer `SIG_IGN` semantics on kernels at least 6.13, and finishes with overrun checks on monotonic/process/thread clocks. Signal handlers update volatile counters and overrun totals. CPU timers are driven by busy loops, while real-time timers sleep through `pause()` or blocked signal waits.

## State and Persistence
State is in process-local globals such as `done`, `ctd_count`, `ctd_failed`, and per-test `struct tmrsig` counters. Timers and signal dispositions are kernel state and are deleted or restored before each test exits. The timer ID restore test temporarily enables a task `prctl` mode and explicitly disables it again.

## Dependencies and Integration Points
The test depends on pthreads, signal delivery, VDSO time constants, raw syscalls, `kselftest.h`, and kernel support for `PR_TIMER_CREATE_RESTORE_IDS`. It integrates with the timers selftest directory and reports every check through `ksft_test_result*` and `ksft_finished()`.

## Risks
The suite is timing-sensitive: CPU load, scheduler jitter, or unrelated threads can cause false negatives, which the test acknowledges for CPU timers. Several checks assume precise overrun counts after one-second sleeps with 100 ms intervals. Newer SIG_IGN expectations are kernel-version gated, and timer ID restoration may be skipped on kernels without the prctl.

## Test Signals
Passing signals include 2 second timer deltas within a 0.5 second tolerance, CPU timer signals delivered to the running thread only, expected SIG_IGN queue/drop semantics, `timer_gettime()` interval wraps, exact overrun counts, and restored timer ID allocation behavior. Failures indicate regressions in timer accounting, signal delivery, or timer lifecycle handling.
