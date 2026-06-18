<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_list_sort.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_list_sort.c

## Purpose
KUnit test for `list_sort()`, checking sorting correctness, list integrity, element preservation, poison fields, and stability for equivalent keys.

## APIs, Types, and Functions
Defines `struct debug_el` around `struct list_head`, poison fields, sortable `value`, and original `serial`. `check()` validates element identity and poisons through `test->priv`. `cmp()` unwraps list nodes and compares values after validating both elements. `list_sort_test()` allocates elements, populates a linked list, calls `list_sort()`, and verifies the result.

## Control Flow, State, and Persistence
The test allocates an array of original element pointers and 642 list elements (`512+128+2`), fills values with random numbers below one third of the length to force duplicates, appends each element, sorts, then walks the list. During the walk it asserts bidirectional linkage, nondecreasing compare results, stable serial ordering for equal values, valid poisons, and unchanged list length. All memory is KUnit-managed.

## Dependencies and Integration
Depends on KUnit, `linux/list_sort.h`, list primitives, slab allocation, and random helpers. It integrates as the `list_sort` suite.

## Risks and Test Signals
Risks include random input not being reproducible unless the global random stream is controlled, a single chosen list length, and comparator subtraction overflow if value ranges changed. Test signals are structural integrity checks, stable-sort validation, poison preservation, and a length chosen to hit multiple internal list-sort carry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_list_sort.c -->
