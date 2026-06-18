# sources/distributed-fs/ceph-client/kernel/crash_core_test.c

## Purpose
`crash_core_test.c` is a KUnit suite for `crash_exclude_mem_range()`. It validates how the crash-memory range exclusion helper mutates sorted memory ranges when an interval is outside, touching, overlapping, contained, covering, or splitting an existing range.

## Important APIs, types, and functions
The suite uses `struct crash_mem`, `struct range`, and KUnit assertions. Helpers are `create_crash_mem()`, which allocates a variable-sized `struct crash_mem` with KUnit-managed memory; `assert_ranges_equal()`, which checks range count and start/end values; and `run_exclude_test_case()`, which invokes `crash_exclude_mem_range()` and validates either expected output ranges or unchanged range count on expected errors.

Test data is represented by `struct exclude_test_param`. Test cases are `exclude_single_range_test()` and `exclude_range_regression_test()`, registered in `crash_exclude_mem_range_suite`.

## Control flow
Each test iterates over static parameter arrays, logs the case description, allocates a `crash_mem` sized by `initial_max_ranges`, copies initial ranges, calls `crash_exclude_mem_range(mem, exclude_start, exclude_end)`, checks the expected return code, and compares mutated ranges when success is expected. Error cases currently assert that `nr_ranges` remains equal to the initial count.

## State and persistence behavior
All memory is KUnit-managed and scoped to the test. The tests do not modify global crash-kernel state, resources, kexec images, or persistent storage. Static compound-literal range arrays define expected data.

## Dependencies and integration points
The suite depends on KUnit, `linux/crash_core.h`, and the linked implementation of `crash_exclude_mem_range()` from `crash_core.c`. It is a low-level algorithm test rather than an integration test for kexec or crash reservations.

## Risks and edge cases
The suite gives broad single-range coverage, including no overlap, boundary-touch no-ops, partial trims, full removals, point exclusions, split success, and split ENOMEM. The regression set includes a low-1M full exclusion and a known out-of-bound/capacity case. It does not validate unsorted input, overlapping initial ranges, multi-range partial mutation beyond the regression cases, invalid `mstart > mend`, or content preservation on ENOMEM beyond `nr_ranges`.

## Test signals
The primary signal is the KUnit suite name `crash_exclude_mem_range_tests`. High-value additions would cover multiple ranges with split plus removal in one call, range-list ordering after complex exclusions, invalid reversed intervals if the API should reject them, maximum capacity boundaries, and explicit verification that range contents remain unchanged on `-ENOMEM`.
