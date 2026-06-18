# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_helpers.h

## Purpose

`mseal_helpers.h` provides assertion/reporting macros and fallback pkey constants for `mseal_test.c`.

## Important APIs, Types, and Functions

`FAIL_TEST_IF_FALSE()` emits a failing kselftest result with function and line number, then returns from the current void test function. `SKIP_TEST_IF_FALSE()` emits a skip result and returns. `REPORT_TEST_PASS()` emits a pass result using the current function name. The header defines fallback `PKEY_DISABLE_ACCESS`, `PKEY_DISABLE_WRITE`, `PKEY_BITS_PER_PKEY`, `PKEY_MASK`, and `u64`.

## Control Flow

The macros are designed for single test functions that should stop on the first failed precondition or assertion. They do not abort the whole process, allowing the large mseal suite to continue after individual test failures.

## State and Persistence Behavior

The header has no state. It relies on kselftest global counters manipulated by `ksft_test_result_*()`.

## Dependencies and Integration Points

It assumes inclusion after `kselftest.h` and is used by `mseal_test.c`. The pkey constants support architectures or libc headers that do not provide the names used in the test.

## Risks and Edge Cases

The macros return without cleanup, so test functions that allocate mappings before a failure may leak VMAs until process exit. `u64` is conditionally defined as `unsigned long long`, which could conflict if included after another incompatible typedef.

## Test Signals

Signals are the pass, fail, or skip kselftest result lines emitted by the macros in `mseal_test.c`.
