# sources/distributed-fs/orangefs/src/client/windows/client-test/timer.c

Purpose: Provides elapsed-time measurement helpers for client tests on Windows and POSIX.

Important APIs/functions: On Windows, `timer_start()` returns a `QueryPerformanceCounter()` tick value and `timer_elapsed()` converts the difference to seconds using `QueryPerformanceFrequency()`. On POSIX, `timer_start(struct timeval *)` stores `gettimeofday()`, and `timer_elapsed(struct timeval *)` computes wall-clock seconds.

Control flow: Platform-specific compilation selects one signature set. Error handling returns `0` seconds/ticks when Windows high-resolution counter calls fail.

State/persistence: No global state; callers hold the start timestamp.

Dependencies/integration: Paired with `timer.h`. Used by performance-oriented client tests and by report helpers through `report_perf()` formatting conventions.

Risks: POSIX timing uses wall-clock time, so clock adjustments can skew elapsed values. Windows path recomputes frequency on every elapsed call. Failure is indistinguishable from true zero elapsed time.

Test signals: Verify monotonic positive elapsed values after sleeps on both platforms and format output through `report_perf()`.
