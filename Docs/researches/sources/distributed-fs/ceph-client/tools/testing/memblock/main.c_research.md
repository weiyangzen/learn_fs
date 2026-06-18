<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/main.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/main.c

## Purpose

`main.c` is the entrypoint for the memblock simulator test binary. It parses command-line options and runs the memblock API suites in a fixed order.

## Important APIs, Types, and Functions

`main(argc, argv)` includes headers for basic, allocation, helper allocation, NUMA allocation, exact-NID allocation, and common test utilities. It calls `parse_args()`, `memblock_basic_checks()`, `memblock_alloc_checks()`, `memblock_alloc_helpers_checks()`, `memblock_alloc_nid_checks()`, and `memblock_alloc_exact_nid_checks()`.

## Control Flow

Execution is linear: parse options, run each suite, return zero if assertions do not abort. Each suite handles its own prefix stack, dummy memory initialization, memblock reset, and cleanup.

## State and Persistence Behavior

Global simulator state such as memblock region arrays, dummy physical memory, prefix state, and option flags is initialized and reset by the called suites. The entrypoint itself persists nothing.

## Dependencies and Integration Points

It links all test object files named in the Makefile. It is the integration point that proves the real `mm/memblock.c` can coexist with simulator stubs and every selected test suite.

## Risks and Edge Cases

Because all suites run in one process, leaked global state from an earlier suite can affect later suites. The fixed order can hide order dependencies unless individual suites reset state thoroughly.

## Test Signals

Running `./main` should complete without assertion failure and return zero. Running with verbose/debug/NUMA build options should show the suite prefixes and still pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/main.c -->
