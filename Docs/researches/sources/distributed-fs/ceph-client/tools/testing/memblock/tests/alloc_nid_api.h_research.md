<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.h

## Purpose

`alloc_nid_api.h` declares the range and NUMA memblock allocation test entrypoints and provides compile-time gating for NUMA-specific checks.

## Important APIs, Types, and Functions

It declares `memblock_alloc_nid_checks()`, `memblock_alloc_exact_nid_range_checks()`, and `__memblock_alloc_nid_numa_checks()`. Inline `memblock_alloc_nid_numa_checks()` calls the NUMA implementation only when `CONFIG_NUMA` is enabled; otherwise it returns zero.

## Control Flow

Compile-time `#ifdef CONFIG_NUMA` controls whether NUMA scenarios run. Range tests remain available regardless of NUMA support.

## State and Persistence Behavior

The header stores no state. The implementation manages allocator flags, memblock arrays, and dummy memory.

## Dependencies and Integration Points

It includes `common.h`, is consumed by `alloc_nid_api.c`, `alloc_exact_nid_api.c`, and `main.c`, and exposes the shared exact-NID range check hook.

## Risks and Edge Cases

As with the exact-NID header, the inline NUMA wrapper ignores the implementation return value and relies on assertions for failure. Non-NUMA builds do not cover fallback and node-tagging behavior.

## Test Signals

Both NUMA and non-NUMA builds should compile. NUMA builds should run the additional try-NID scenarios; exact-NID tests should link against `memblock_alloc_exact_nid_range_checks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.h -->
