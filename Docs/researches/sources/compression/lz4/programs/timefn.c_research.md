# sources/compression/lz4/programs/timefn.c

Purpose: implements portable timing for progress refreshes and throughput reporting.

Important APIs/functions: `TIME_getTime()`, `TIME_span_ns()`, `TIME_clockSpan_ns()`, `TIME_waitForNextTick()`, and `TIME_support_MT_measurements()`.

Control flow: chooses Windows performance counters, Apple `mach_absolute_time`, POSIX `clock_gettime(CLOCK_MONOTONIC)`, C11 `timespec_get`, or C90 `clock()` fallback. Common helpers compute deltas and spin until a new tick.

State and persistence: Windows/Apple paths cache frequency/timebase statically. `TIME_t` values are only meaningful for differences.

Dependencies/integration: used by `lz4io.c` for progress throttling and final timing; may be used by benchmark code.

Risks: C90 fallback is CPU time and unsuitable for MT wall-clock measurement; timing failures abort; `TIME_waitForNextTick()` busy-waits.

Test signals: indirectly covered by CLI timing/progress and benchmark runs.
