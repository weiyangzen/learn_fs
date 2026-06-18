<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.h

## Purpose

`alloc_exact_nid_api.h` declares entrypoints for exact-NID memblock allocation tests and gates NUMA-specific checks on `CONFIG_NUMA`.

## Important APIs, Types, and Functions

It declares `memblock_alloc_exact_nid_checks()` and `__memblock_alloc_exact_nid_numa_checks()`. Inline `memblock_alloc_exact_nid_numa_checks()` calls the implementation and returns zero when `CONFIG_NUMA` is enabled; otherwise it is a no-op returning zero.

## Control Flow

The header-level control flow is compile-time conditional. Non-NUMA builds still compile and run the top-level exact-NID suite without trying to execute NUMA-only checks.

## State and Persistence Behavior

The header stores no state. It controls whether NUMA test state is exercised by the implementation.

## Dependencies and Integration Points

It includes `common.h` and is used by `alloc_exact_nid_api.c` and `main.c`. It also connects to `alloc_nid_api.c` through shared range checks.

## Risks and Edge Cases

The inline wrapper discards the return value from `__memblock_alloc_exact_nid_numa_checks()`, so failures must abort through assertions rather than return codes. Non-NUMA builds provide no coverage for strict exact-node semantics.

## Test Signals

Builds with and without `CONFIG_NUMA` should compile. NUMA-enabled runs should print and execute exact-NID NUMA scenarios; non-NUMA runs should skip them cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.h -->
