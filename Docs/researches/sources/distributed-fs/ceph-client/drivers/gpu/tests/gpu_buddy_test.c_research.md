# sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_buddy_test.c

Purpose: KUnit validation suite for the generic GPU buddy allocator, covering allocation limits, range allocation, alignment, fragmentation, clear/dirty state, contiguous allocation, and pathological split/merge behavior.

Important APIs and functions: test cases include `gpu_test_buddy_alloc_limit`, `alloc_optimistic`, `alloc_pessimistic`, `alloc_pathological`, `alloc_contiguous`, `alloc_clear`, `alloc_range`, `alloc_range_bias`, `fragmentation_performance`, `alloc_exceeds_max_order`, `offset_aligned_allocation`, and `subtree_offset_alignment_stress`. The suite uses `gpu_buddy_init`, `gpu_buddy_alloc_blocks`, `gpu_buddy_free_list`, `gpu_buddy_free_block`, block offset/size/order helpers, and clear-state helpers.

Control flow: suite init chooses a nonzero random seed. Tests allocate synthetic address spaces, perform expected-success and expected-failure allocations, inspect returned block lists, free in controlled or randomized orders, and verify allocator metadata such as `avail`, `max_order`, root count, and `subtree_max_alignment`.

State and persistence: state is isolated per test in local `struct gpu_buddy` instances and temporary lists. Randomness is deterministic per suite run once the seed is printed.

Dependencies and integration: depends on KUnit, `linux/gpu_buddy.h`, kernel list helpers, prime/random utilities, sizes, and `gpu_random` helpers.

Risks: slow fragmentation tests can be expensive because they model multi-GiB spaces. Randomized tests improve coverage but failures need the printed seed for reproduction. Some tests inspect internal allocator fields, so allocator refactors may require test updates.

Test signals: the file itself is the primary signal for GPU buddy correctness and performance regressions. `KUNIT_CASE_SLOW` marks the long fragmentation/performance path.
