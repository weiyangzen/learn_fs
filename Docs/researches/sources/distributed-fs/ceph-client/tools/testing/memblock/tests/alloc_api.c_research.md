<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.c

## Purpose

`alloc_api.c` tests the generic `memblock_alloc()` and `memblock_alloc_raw()` APIs against a simulated physical memory map. It verifies placement, alignment, zeroing behavior, reservation merging, and failure cases for both top-down and bottom-up allocation modes.

## Important APIs, Types, and Functions

`get_memblock_alloc_name()` labels the active API, and `run_memblock_alloc()` dispatches to raw or zeroing allocation based on `alloc_test_flags`. Scenario functions cover simple allocation, disjoint reservations, before/after merges, second fit, in-between full merge, small gaps, all memory reserved, insufficient space, limited exact space, no registered memory, and too-large allocations. `memblock_alloc_checks_internal(flags)` runs all scenarios for one API mode; `memblock_alloc_checks()` runs normal and raw modes.

## Control Flow

Each test resets or sets up memblock, optionally reserves regions, calls the selected allocation API, then asserts returned pointer, memory contents, `memblock.reserved` entry base/size/count, and `total_size`. Wrapper functions run directional variants by toggling `memblock_set_bottom_up()` or using `run_top_down()` and `run_bottom_up()`.

## State and Persistence Behavior

The suite manipulates global `memblock`, reservation arrays, allocation direction, and dummy physical memory. It initializes dummy memory at suite start and cleans it at suite end. Raw allocations are expected to preserve nonzero memory content, while normal allocations are expected to zero memory.

## Dependencies and Integration Points

It depends on `alloc_api.h`, `common.h`, the real memblock implementation, and common helpers such as `setup_memblock()`, `dummy_physical_memory_init()`, `assert_mem_content()`, and prefix/test reporting. It is called from `main.c`.

## Risks and Edge Cases

Assertions assume precise reserved-region ordering and merge behavior, so legitimate changes to memblock sorting or alignment policy require test updates. The tests use small synthetic memory sizes, which may miss overflow or large-map behavior. Raw memory checks depend on dummy memory being pre-poisoned.

## Test Signals

Passing signals include correct top-down placement near the end of DRAM, bottom-up placement at the start, proper merging with adjacent reservations, NULL on impossible allocations, accurate `reserved.cnt` and `total_size`, zeroed normal allocations, and nonzero raw allocations under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.c -->
