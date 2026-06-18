<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.c

## Purpose

`alloc_nid_api.c` tests range-limited and NUMA-aware memblock allocation through `memblock_alloc_try_nid()`, `memblock_alloc_try_nid_raw()`, and, for shared range cases, `memblock_alloc_exact_nid_raw()`. It verifies alignment, range clipping, reservation merging, fallback behavior, node selection, and memory zeroing/raw semantics.

## Important APIs, Types, and Functions

`get_memblock_alloc_nid_name()` labels the active API. `run_memblock_alloc_nid()` dispatches based on `TEST_F_RAW` and `TEST_F_EXACT`. Range tests cover simple ranges, misaligned start/end, exact-address fit, narrow ranges, low max failure, min/max-adjacent reserved merges, reserved gaps with and without space, full merge, all reserved, and min/max capping. NUMA tests use `node_fractions` to cover requested-node success, small-node fallback, fully reserved node fallback, partial reservation success and fallback, split ranges, no-overlap ranges, large-region failure, reserved full merge, split-all-reserved failure, and `memblock_alloc_node()` nid tagging.

## Control Flow

The suite first runs range checks with `NUMA_NO_NODE`, then NUMA checks through `memblock_alloc_nid_numa_checks()`. Direction wrappers set top-down or bottom-up mode, because placement differs by direction while final reservations must still satisfy range and node policy. `memblock_alloc_nid_checks()` runs both zeroing and raw try-NID modes; `memblock_alloc_exact_nid_range_checks()` reuses range checks with exact/raw dispatch.

## State and Persistence Behavior

State includes `alloc_nid_test_flags`, global memblock arrays, per-region `nid` metadata, allocation direction, and dummy physical memory. Normal try-NID allocations are expected to zero memory, while raw and exact raw allocations are expected to leave nonzero dummy contents. Each top-level run resets attributes and initializes/cleans dummy memory.

## Dependencies and Integration Points

It includes `alloc_nid_api.h` and common helpers, and it is used both directly by `main.c` and indirectly by `alloc_exact_nid_api.c` for shared range tests. It depends on NUMA setup helpers and the real memblock allocator implementation.

## Risks and Edge Cases

Fallback rules are subtle: try-NID may fall back to `NUMA_NO_NODE`, while exact-NID must not. Range bounds can be dropped or capped in some cases, and tests assert those policies precisely. The file is large and scenario-rich, so adding allocator behavior without updating mirrored top-down/bottom-up cases can leave asymmetric coverage.

## Test Signals

Passing signals include correct reserved table geometry for every range case, fallback to suitable nodes for try-NID, no allocation for truly impossible ranges, correct `nid` on `memblock_alloc_node()`, zeroed versus raw memory content, and successful reuse of range checks by exact-NID mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.c -->
