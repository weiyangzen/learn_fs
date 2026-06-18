<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.c

## Purpose

`alloc_exact_nid_api.c` tests `memblock_alloc_exact_nid_raw()`, the strict NUMA-node allocator. Unlike the try-NID API, exact-NID allocation must not fall back to other nodes when the requested node or range cannot satisfy the allocation.

## Important APIs, Types, and Functions

The file defines an eight-node `node_fractions` layout and many NUMA scenarios for top-down and bottom-up modes: simple node allocation, partial reservations, split ranges where lower limits are dropped, no-overlap-low cases, small node failure, fully reserved node failure, partial-reservation failure, split-range-high failure, no-overlap-high failure, large-region failure, full merge between border reservations, and split-all-reserved failure. `__memblock_alloc_exact_nid_numa_checks()` runs exact NUMA scenarios; `memblock_alloc_exact_nid_checks()` also invokes shared exact-NID range checks from `alloc_nid_api.c`.

## Control Flow

Each scenario calls `setup_numa_memblock(node_fractions)`, computes requested node/range boundaries, optionally reserves blocking regions, calls `memblock_alloc_exact_nid_raw(size, align, min, max, nid)`, and asserts either a node-local reservation or NULL. Wrappers run symmetric top-down and bottom-up expectations where direction changes placement but not strict node selection.

## State and Persistence Behavior

The suite uses global memblock node metadata, reserved arrays, allocation direction, and dummy physical memory. `memblock_alloc_exact_nid_checks()` resets attributes, initializes dummy memory, executes range and NUMA checks, then cleans up.

## Dependencies and Integration Points

It includes `alloc_exact_nid_api.h` and `alloc_nid_api.h` because exact-NID range checks reuse the generic range-test machinery with `TEST_F_RAW | TEST_F_EXACT`. It depends on `CONFIG_NUMA` gating in the header and common NUMA setup helpers.

## Risks and Edge Cases

Strict no-fallback semantics are easy to regress if shared try-NID code paths change. Some tests deliberately expect lower range limits to be dropped while preserving exact-node behavior, which is subtle. The synthetic NUMA layout may not cover all node interleavings or large address boundaries.

## Test Signals

Strong signals are NULL for requested nodes that are too small, fully reserved, non-overlapping high, or split-all-reserved; successful reservations confined to the requested node; correct full merges at node borders; and shared range tests passing with `memblock_alloc_exact_nid_raw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.c -->
