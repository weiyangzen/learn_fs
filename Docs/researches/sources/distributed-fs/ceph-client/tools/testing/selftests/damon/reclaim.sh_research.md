# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/reclaim.sh

## Purpose

`reclaim.sh` verifies the `damon_reclaim` module parameter can start and stop a kdamond.

## Important APIs, Types, and Functions

It checks `/sys/module/damon_reclaim/parameters/enabled`, uses `pgrep kdamond`, and writes `Y`/`N`.

## Control Flow

After root/dependency checks, it skips if another kdamond exists, enables reclaim and expects one kdamond, disables reclaim and expects zero.

## State and Persistence Behavior

It mutates the global DAMON reclaim enabled parameter and resulting kdamond process state.

## Dependencies and Integration Points

It depends on DAMON_RECLAIM support and the module parameter ABI.

## Risks and Edge Cases

Concurrent DAMON users cause skip. Slow kdamond teardown can produce false failures.

## Test Signals

Pass is exact kdamond process count transitions 0 -> 1 -> 0.
