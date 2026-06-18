<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.h

## Purpose

`alloc_api.h` declares the public entrypoint for the generic memblock allocation tests.

## Important APIs, Types, and Functions

It includes `common.h` and declares `int memblock_alloc_checks(void);`.

## Control Flow

The header has no control flow. `main.c` calls the declared function to run normal and raw allocation suites.

## State and Persistence Behavior

It stores no state. The implementation manages memblock and dummy memory state.

## Dependencies and Integration Points

It integrates `alloc_api.c` with the simulator entrypoint and shared test helpers.

## Risks and Edge Cases

The narrow interface hides individual scenarios from other translation units; adding selective execution would require new declarations.

## Test Signals

Successful compilation and linkage of `main.o` against `alloc_api.o` confirm the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.h -->
