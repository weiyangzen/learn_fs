# sources/distributed-fs/ceph-client/mm/damon/tests/core-kunit.h

## Purpose
This header defines KUnit tests for DAMON core data structures, region mutation, operation registration, monitoring attribute validation, DAMOS filters, quotas, migration destinations, context commit, and helper algorithms. It is conditionally compiled under `CONFIG_DAMON_KUNIT_TEST`.

The tests are embedded in DAMON core compilation and validate low-level invariants that the sysfs and operation layers rely on.

## Important APIs, Types, And Functions
The suite is named `damon` and is registered with `kunit_test_suite(damon_test_suite)`. It exercises `struct damon_ctx`, `struct damon_target`, `struct damon_region`, `struct damos`, `struct damos_filter`, `struct damos_quota`, `struct damos_quota_goal`, and `struct damos_migrate_dests`.

Major test groups include:

- Region and target lifecycle: `damon_test_regions()`, `damon_test_target()`.
- Aggregation and monitoring-result math: `damon_test_aggregate()`, `damon_test_nr_accesses_to_accesses_bp()`, `damon_test_update_monitoring_result()`, `damon_test_moving_sum()`.
- Region splitting/merging/setting: `damon_test_split_at()`, `damon_test_merge_two()`, `damon_test_merge_regions_of()`, `damon_test_split_regions_of()`, `damon_test_set_regions()`, `damon_test_apply_min_nr_regions()`, `damon_test_is_last_region()`.
- Ops and context configuration: `damon_test_ops_registration()`, `damon_test_set_attrs()`, `damon_test_commit_ctx()`.
- DAMOS object updates: `damos_test_new_filter()`, `damos_test_commit_quota_goal()`, `damos_test_commit_quota_goals()`, `damos_test_commit_quota()`, `damos_test_commit_dests()`, `damos_test_commit_filter()`, `damos_test_commit_pageout()`, `damos_test_commit_migrate_hot()`, `damos_test_filter_out()`, `damon_test_set_filters_default_reject()`.
- Feedback loop: `damon_test_feed_loop_next_input()`.

## Control Flow
Each test allocates minimal DAMON objects, sets fields directly, calls the core API under test, and asserts state with `KUNIT_EXPECT_*`. Allocation failures call `kunit_skip()` after freeing prior allocations. Helper functions construct targets and regions or compare commit results across source/destination structures.

The suite table `damon_test_cases[]` lists all tests and terminates with an empty entry. KUnit discovers and runs them as part of the compiled suite.

## State And Persistence
All state is local to test functions. Tests directly mutate in-memory DAMON structs and free them before returning. Some tests temporarily modify global operation registration state, protected by `damon_ops_lock`, then restore the original registered operation.

The tests intentionally use stack-allocated DAMOS objects in several commit cases and initialize list heads manually to isolate commit logic from allocator behavior.

## Dependencies And Integration Points
The file depends on DAMON core implementation symbols being visible from the including translation unit. It includes `<kunit/test.h>` and assumes DAMON internal list macros and allocation helpers are in scope.

It indirectly validates behavior that `sysfs.c`, `sysfs-schemes.c`, and `vaddr.c` depend on: valid attrs constraints, `damon_set_regions()`, target-region commit semantics, filter default-reject behavior, quota-goal commit behavior, migration destination updates, and action-specific commit fields.

## Risks And Edge Cases
The tests are white-box and compiled into the implementation, so they can reach static/internal helpers. That improves precision but means they are not standalone API consumers.

Several tests use `kunit_skip()` on allocation failure, so low-memory paths may reduce coverage instead of failing. Some helpers build temporary arrays on the stack; future struct layout changes could require updating expected comparisons.

`damon_test_ops_registration()` temporarily clears `damon_registered_ops[DAMON_OPS_VADDR]`; restoration is careful but any added early return path would risk leaking global test state.

The tests cover many core invariants but do not exercise concurrent mutation, live kdamond worker calls, sysfs locking, page-table walking, or actual memory migration.

## Test Signals
This file is itself the test signal. It provides direct coverage for core mutation logic, validation failures, DAMOS commit behavior, filtering splits, and feedback-loop direction. For this subset, it is especially relevant as indirect coverage for sysfs scheme commit behavior and vaddr region adjustment.
