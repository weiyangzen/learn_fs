# sources/distributed-fs/ceph-client/kernel/kcsan/kcsan_test.c

## Purpose
KUnit suite for KCSAN runtime behavior. It creates controlled races, captures KCSAN console reports, and verifies expected reports or non-reports across normal races, atomics, scoped assertions, weak-memory barriers, permissive filtering, and compiler atomic builtins.

## Important APIs, Types, and Functions
Uses `struct expect_report`, `begin_test_checks`, `end_test_checks`, `probe_console`, `report_matches`, many `test_kernel_*` access kernels, parameter generator `nthreads_gen_params`, torture worker `access_thread`, and KUnit lifecycle hooks `test_init`, `test_exit`, `kcsan_suite_init`, `kcsan_suite_exit`.

## Control Flow
Suite init registers the console tracepoint. Each threaded test starts torture kthreads and timers that repeatedly run two access kernels. The test body sets `access_kernels`, loops until a timeout or expected report, and matches captured report title/access lines against expected function, address, size, and access type. Exit stops workers and clears access kernels.

## State and Persistence
Static test variables (`test_var`, `test_array`, `test_struct`, locks, seqlock) provide race targets. `observed` stores the current captured report under spinlock. Worker thread arrays and test end time exist per test run only.

## Dependencies and Integration Points
Depends on KUnit, torture kthreads, timers, console tracepoint, KCSAN public checks/assertions, lock primitives, seqlocks, jiffies, and compiler TSAN/KCSAN instrumentation.

## Risks
Tests are timing and configuration dependent; many expectations branch on config options such as weak memory, value-change-only, permissive mode, ignored atomics, and compiler compound-read support. Console parsing is intentionally narrow and could break if report formatting changes.

## Test Signals
The suite registers as `kcsan`. Cases cover basic data races, concurrent races, no-value-change filtering, unknown-origin races, write-write assumptions, atomic/plain races, zero-size accesses, `data_race`, `__data_racy`, exclusive assertions, jiffies/seqlock non-reports, atomic builtins, one-bit permissive filtering, and missing/correct barriers.
