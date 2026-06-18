# sources/distributed-fs/ceph-client/lib/test_parman.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_parman.c` tests the priority array manager (`parman`) using the `PARMAN_ALGO_TYPE_LSORT` algorithm. It randomly adds and removes items across many priorities, then checks array ordering, indexing, gap policy, and resize behavior. The source was read as a complete 395-line file.

## Important APIs, Types, and Functions

Local types are `struct test_parman_prio`, `struct test_parman_item`, and `struct test_parman`. The operation callbacks are `test_parman_resize` and `test_parman_move`, exposed through `test_parman_lsort_ops`. Flow helpers include `test_parman_rnd_init`, `test_parman_priority_gen`, `test_parman_prios_init`, `test_parman_items_init`, `test_parman_create`, `test_parman_destroy`, `test_parman_run_check_budgets`, `test_parman_run`, `test_parman_check_array`, `test_parman_lsort`, and `test_parman_init`.

## Control Flow

Module load calls `test_parman_lsort`, which creates a `parman` instance with a backing pointer array, seeds a deterministic pseudo-random generator, initializes 128 unique priorities, assigns 8192 items to random priorities, and then runs up to `TEST_PARMAN_RUN_BUDGET` add/remove attempts. Random bulk budgets create no-op stretches and operation bursts. After the run, `test_parman_check_array` scans the backing array to ensure no forbidden gaps, monotonically increasing priorities, correct `parman_item.index` values, matching used-item counts, and reasonable trailing unused capacity.

## State and Persistence Behavior

All state is allocated in one `struct test_parman` and freed in `test_parman_destroy`. The backing priority array is resized with `krealloc` through parman callbacks and zeroed for new capacity. Priorities and items are in fixed arrays inside the test object; no state persists after module load.

## Dependencies and Integration Points

Direct includes cover kernel, module, slab, bitops, err, prandom, and `<linux/parman.h>`. Integration points are `parman_create`, `parman_destroy`, `parman_prio_init`, `parman_prio_fini`, `parman_item_add`, `parman_item_remove`, callback-driven resize/move semantics, and deterministic `prandom` state.

## Risks and Edge Cases

The test exercises resizing and item movement heavily, but only covers the lsort algorithm. It depends on deterministic randomness, so accidental seed changes alter coverage. `test_parman_resize` calls `krealloc` before checking `new_count == 0`; this matches kernel `krealloc(ptr, 0, ...)` semantics but is an area where allocator semantics matter. Memory pressure can fail creation or insertion and becomes a test failure.

## Test Signals

Success logs `Priority array check successful` and module init returns `0`. Failures identify gaps, bad priority order, bad index values, used count mismatches, too much trailing slack, or allocation/add errors.
