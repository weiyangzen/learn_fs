<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_sort.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_sort.c

## Purpose
Simple KUnit regression test for the generic `sort()` helper on integer arrays.

## APIs, Types, and Functions
Defines `cmpint()` as the comparator and `test_sort()` as the sole test. It uses `sort(base, num, size, cmp, swap)` with a NULL custom swap function.

## Control Flow, State, and Persistence
The test allocates 1000 integers, fills them with a deterministic multiplicative-modulo sequence, sorts the full array, and verifies nondecreasing order. It then refills `TEST_LEN - 1` entries with a different seed, sorts that shorter range, and verifies order again. State is local KUnit-managed memory.

## Dependencies and Integration
Depends on KUnit, `linux/sort.h`, slab allocation, and module metadata. It registers as `lib_sort`.

## Risks and Test Signals
Risks include comparator subtraction overflow if values are expanded beyond the current small range, no stability check, and limited type coverage. Test signals are deterministic input, full-length and off-by-one-length sort coverage, and post-sort monotonic assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_sort.c -->
