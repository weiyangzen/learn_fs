<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.h

## Purpose

`alloc_helpers_api.h` declares the memblock helper allocation test entrypoint.

## Important APIs, Types, and Functions

It includes `common.h` and declares `int memblock_alloc_helpers_checks(void);`.

## Control Flow

There is no control flow in the header. The simulator entrypoint calls the declared function.

## State and Persistence Behavior

The header contains no state.

## Dependencies and Integration Points

It integrates `alloc_helpers_api.c` with `main.c` and shared memblock test helpers.

## Risks and Edge Cases

Only one top-level function is exposed, so selective helper test execution is not available through this header.

## Test Signals

Successful compilation and linkage confirm the declaration matches the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.h -->
