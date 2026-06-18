# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/lru_sort.sh

## Purpose

`lru_sort.sh` verifies the `damon_lru_sort` module parameter toggles a kdamond on and off.

## Important APIs, Types, and Functions

It sources `_common.sh`, checks `/sys/module/damon_lru_sort/parameters/enabled`, uses `pgrep kdamond`, and writes `Y` then `N` to the parameter.

## Control Flow

After root and file checks, it skips if another kdamond is already running. It enables LRU sort, expects exactly one kdamond, disables it, and expects zero kdamonds.

## State and Persistence Behavior

It mutates the global `damon_lru_sort` enabled parameter and process state by starting/stopping a kdamond.

## Dependencies and Integration Points

It depends on DAMON_LRU_SORT built as a module or exposing the parameter, and no preexisting kdamond.

## Risks and Edge Cases

Other DAMON users cause skip. A stale kdamond or delayed shutdown can make counts inaccurate.

## Test Signals

Success is one kdamond after enabling and zero after disabling; failures report not turned on/off.
