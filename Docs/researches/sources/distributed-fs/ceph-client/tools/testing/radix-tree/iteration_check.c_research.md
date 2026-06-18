# sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check.c

## Purpose
`iteration_check.c` stress-tests XArray iteration while entries are concurrently inserted, removed, tagged, and retagged. It targets races involving retry entries, deleted nodes, paused iteration, RCU protection, and multi-order entries.

## Important APIs, Types, And Functions
Important constants are `NUM_THREADS`, `MAX_IDX`, `TAG`, and `NEW_TAG`. Functions include `my_item_insert()`, thread functions `add_entries_fn()`, `tagged_iteration_fn()`, `untagged_iteration_fn()`, `remove_entries_fn()`, `tag_entries_fn()`, and public `iteration_test(order, test_duration)`.

## Control Flow
`iteration_test()` seeds three per-thread random generators, sets `max_order`, starts five pthreads, sleeps for the requested duration, flips `test_complete`, joins all threads, and frees the XArray. Insertion attempts the largest conflict-free order down to zero under `xas_lock()`, handles allocation retry through `xas_nomem()`, and marks stored entries. Iterator threads repeatedly scan tagged or all entries under RCU, using `xas_retry()` and occasionally `xas_pause()` with an intervening `rcu_barrier()`. Other threads erase random entries and copy tags.

## State And Persistence
Global test state includes the thread array, random seeds, `DEFINE_XARRAY(array)`, `test_complete`, and `max_order`. State is reset at the start of each `iteration_test()` invocation and destroyed by `item_kill_tree()` at the end.

## Dependencies And Integration Points
This file depends on XArray advanced state APIs, local item allocation/free helpers, pthreads, sleep, and the user-space RCU harness. `main.c` calls it twice: once with order 0 and once with order 7.

## Risks
The test is inherently timing-sensitive. It catches concurrency bugs by running races for a duration rather than by deterministic interleavings, so weak machines or short durations may reduce coverage. The shared `rand_r()` seeds avoid global `rand()` races but still produce nondeterministic behavior from the main seed.

## Test Signals
The main signal is no crash, assertion, deadlock, or leak during the timed run. Failures often appear as invalid iteration, use-after-free under RCU, allocation accounting mismatches, or hangs during join.
