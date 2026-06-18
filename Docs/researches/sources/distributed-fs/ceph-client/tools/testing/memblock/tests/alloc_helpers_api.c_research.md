<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.c

## Purpose

`alloc_helpers_api.c` tests the helper API `memblock_alloc_from()`, which allocates memory above a minimum address while still prioritizing successful allocation when the minimum cannot be satisfied.

## Important APIs, Types, and Functions

Scenarios cover simple aligned minimum address allocation, misaligned minimum rounding, high minimum addresses too close to the end of memory, no space above the minimum, and minimum addresses below the start of available memory. Direction-specific functions model top-down and bottom-up placement. `memblock_alloc_helpers_checks()` runs all helper scenarios.

## Control Flow

The suite initializes dummy physical memory, resets memblock attributes, and runs wrappers that execute both allocation directions. Each scenario calls `setup_memblock()`, optionally reserves blocking regions, invokes `memblock_alloc_from(size, align, min_addr)`, and asserts reserved-region base, size, count, total size, and zeroed memory where applicable.

## State and Persistence Behavior

It manipulates global memblock allocation direction and reservation arrays. Dummy physical memory is initialized once for the suite and cleaned afterward. The helper API is expected to return zeroed memory, not raw contents.

## Dependencies and Integration Points

It depends on `alloc_helpers_api.h`, `common.h`, and real memblock helper behavior. `main.c` invokes `memblock_alloc_helpers_checks()` after generic allocation tests.

## Risks and Edge Cases

The key risk is policy ambiguity: several tests expect allocation to succeed below `min_addr` if no suitable memory exists above it. Changes that make `min_addr` strict would intentionally break these assertions. Misalignment and start/end capping are sensitive to `SMP_CACHE_BYTES`.

## Test Signals

Passing signals include aligned placement at or above `min_addr` when possible, fallback allocation when the minimum is impossible, correct merging with adjacent reservations, zeroed allocation contents, and accurate reservation counters in both allocation directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.c -->
