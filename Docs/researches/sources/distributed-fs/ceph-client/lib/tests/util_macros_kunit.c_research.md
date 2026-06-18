<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/util_macros_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/util_macros_kunit.c

## Purpose
KUnit tests for `find_closest()` and `find_closest_descending()` helpers from `linux/util_macros.h`, including driver-like lookup tables and arithmetic progressions.

## APIs, Types, and Functions
Uses `FIND_CLOSEST_RANGE_CHECK` and `FIND_CLOSEST_DESC_RANGE_CHECK` macros to loop integer input ranges and assert returned indexes. Test functions are `test_find_closest()` and `test_find_closest_descending()`.

## Control Flow, State, and Persistence
Each test defines several static sorted arrays: real-world style averaging/oversampling/watchdog tables, increasing or decreasing arithmetic arrays, unsigned arrays, and mixed negative-to-positive arrays. For each inclusive input range, it calls the target helper and asserts the expected nearest index. There is no persistent runtime state.

## Dependencies and Integration
Depends on KUnit and `linux/util_macros.h`. It registers as the `util_macros.h` suite and protects helper behavior used by drivers that select the nearest supported hardware setting.

## Risks and Test Signals
Risks include no explicit tie-breaking explanation outside expected ranges, no empty-array coverage, and compile-time macro behavior depending on array type. Test signals are broad contiguous input ranges, ascending and descending variants, signed/unsigned arrays, negative inputs, and regression coverage for the AD7616 oversampling table mentioned in comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/util_macros_kunit.c -->
