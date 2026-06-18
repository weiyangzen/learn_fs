# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_tried_regions.py

## Purpose

`damos_tried_regions.py` verifies DAMOS tried-region reporting produces a plausible number of regions for a synthetic even-region workload.

## Important APIs, Types, and Functions

It runs `access_memory_even`, starts `_damon_sysfs.Kdamonds` with `DamonCtx(ops='vaddr')`, one target, and a `stat` scheme, then calls `update_schemes_tried_regions()`.

## Control Flow

The script samples tried-region counts every 100 ms until it has more than 10 samples, sorts them, and uses the median-ish fifth sample as a stability check. It expects that value to be at least 14 for a 14-region workload.

## State and Persistence Behavior

It starts a kdamond and a child workload, stores sampled counts in memory, and terminates the workload before evaluating.

## Dependencies and Integration Points

It depends on DAMON vaddr monitoring, tried-region sysfs export, and the `access_memory_even` helper.

## Risks and Edge Cases

Region discovery is timing-sensitive and can undercount on slow or noisy systems. The failure path tries to join integer values directly, which may itself be buggy if reached.

## Test Signals

Success prints the 50th percentile count and expectation met. Failure indicates tried-region reporting did not expose enough regions.
