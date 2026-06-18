# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.c

## Purpose
`basic_api.c` is the core memblock basic API test suite. It validates initialization defaults and region-array semantics for `memblock_add*()`, `memblock_reserve()`, `memblock_remove()`, `memblock_free()`, bottom-up allocation mode, `memblock_trim_memory()`, `memblock_overlaps_region()`, and, under `CONFIG_NUMA`, `memblock_set_node()`. The tests are narrow unit-style checks that directly inspect the global `memblock` object rather than exercising a boot path.

## Important APIs, Types, And Functions
The exported entry point is `memblock_basic_checks()`, which runs all local check groups. Important helper-facing state comes from `common.h`: `struct region`, `PREFIX_PUSH()`, assertion macros, `reset_memblock_regions()`, `reset_memblock_attributes()`, and dummy physical-memory helpers. Check groups are organized as `memblock_add_checks()`, `memblock_reserve_checks()`, `memblock_remove_checks()`, `memblock_free_checks()`, `memblock_bottom_up_checks()`, `memblock_trim_memory_checks()`, `memblock_overlaps_region_checks()`, and `memblock_set_node_checks()`.

## Control Flow
Each individual check resets memblock region state, creates a few synthetic address ranges, invokes one memblock API, and asserts the expected region base, size, count, and `total_size`. The add/reserve suites cover disjoint ranges, top and bottom overlap merging, containment, duplicate insertion, gap-filling merge, `PHYS_ADDR_MAX` truncation, and array growth past the initial 128 entries. Remove/free suites mirror those cases but verify erasure, trimming, split-region behavior, absent-range no-ops, and full removal of the only region. `memblock_basic_checks()` is a fixed sequential runner, so later tests depend on previous tests restoring global memblock state.

## State And Persistence
The file mutates the global `memblock.memory`, `memblock.reserved`, `memblock.bottom_up`, and `memblock.current_limit` fields. Array-growth tests call `memblock_allow_resize()` and allocate dummy memory so `memblock_double_array()` can relocate region arrays; they then restore `memblock.memory.regions` or `memblock.reserved.regions` to avoid dangling pointers after freeing dummy memory. There is no durable persistence, but process-global state must be reset rigorously between checks.

## Dependencies And Integration Points
The suite depends on kernel memblock internals exposed to the user-space memblock test harness, Linux size constants, NUMA conditionals, and `common.c` setup helpers. It integrates with the broader memblock selftest runner through `memblock_basic_checks()` declared in `basic_api.h`.

## Risks
Several assertions are exact structural expectations, so legitimate kernel-side memblock representation changes can break tests even if external behavior remains valid. The near-`PHYS_ADDR_MAX` tests are sensitive to address arithmetic overflow behavior. Array-growth tests are fragile because they intentionally point memblock region arrays into temporary dummy memory and must restore the original arrays before cleanup. One notable test, `memblock_remove_overlap_top_check()`, asserts `rgn->base == r1.base + r2.base`; this is unusual for an overlap trim expectation and should be reviewed if failures appear around that case.

## Test Signals
Success is signaled by completing all assertions and optional verbose `ksft_test_result_pass()` output. Failures call `test_fail()` before `assert()` aborts. High-value signals include the double-array tests, all-location reserve tests, the regression case for overlapping allocation while doubling the reserved array, and the NUMA repeated `memblock_set_node()` loop that catches nid loss after array resize.
