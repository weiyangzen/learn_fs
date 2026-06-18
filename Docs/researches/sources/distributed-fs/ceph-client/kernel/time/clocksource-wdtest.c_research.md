# sources/distributed-fs/ceph-client/kernel/time/clocksource-wdtest.c

Purpose: loadable or built-in unit test for the clocksource watchdog. It registers a synthetic `wdtest-ktime` clocksource and injects delay, positive skew, negative skew, and per-CPU skew to verify watchdog classification.

Important APIs and flow: `wdtest_ktime_read()` returns raw fast time, optionally delayed or offset. A watchdog interval counter advances only after a quarter second so retries observe consistent injection behavior. `wdtest_clocksource_reset()` unregisters, resets state, configures flags such as `CLOCK_SOURCE_MUST_VERIFY`, `CLOCK_SOURCE_WDTEST`, and optional `CLOCK_SOURCE_WDTEST_PERCPU`, then registers the test clocksource at 1 GHz. `wdtest_execute()` waits for expected `CLOCK_SOURCE_VALID_FOR_HRES` or `CLOCK_SOURCE_UNSTABLE` flags, and `wdtest_run()` sequences the clean, delay, positive, and negative cases for global and per-CPU modes.

State and persistence: state is module-global: injection mode, test count, last timestamp, offset, synthetic clocksource flags, and the kthread pointer. Built-in mode exits after test execution; module mode keeps a sleeping thread until unload so cleanup can stop it.

Dependencies and integration: depends on clocksource registration/unregistration, kthreads, `ktime_get_raw_fast_ns()`, delay loops, watchdog flags from core clocksource code, and `tick-internal.h`/timekeeping internals.

Risks and test signals: the file itself is a test signal. Fragility comes from timing thresholds, scheduler delays, and watchdog interval assumptions. Expected output is success after all injected cases pass; failure logs distinguish unexpected unstable/highres flags and timeouts.
