# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota.py

## Purpose

`damos_quota.py` verifies DAMOS byte quota enforcement and quota-exceed accounting.

## Important APIs, Types, and Functions

It uses `access_memory`, `_damon_sysfs.DamosQuota`, `DamosAccessPattern`, `update_schemes_tried_bytes()`, and `update_schemes_stats()`. The quota is 1 MiB per 100 ms reset interval.

## Control Flow

The script runs a two-region access workload, starts a vaddr DAMON context with one matching scheme and a size quota, samples tried bytes and stats every 100 ms while the workload runs, sorts samples, and fails if any tried byte sample exceeds the quota or if `qt_exceeds` is lower than the number of samples exactly at the quota.

## State and Persistence Behavior

It starts kdamond, mutates DAMON scheme quota state, samples runtime stats, and terminates when the workload exits.

## Dependencies and Integration Points

It depends on DAMOS quota support, tried-bytes update support, stats accounting, and the access workload producing enough hot memory to hit quota.

## Risks and Edge Cases

Timing and workload variability can affect quota samples. The script does not explicitly call `kdamonds.stop()` at the end.

## Test Signals

Failures print quota-violating samples or mismatch between expected and reported quota exceed counts. Exit 0 means all observed tried bytes stayed within the configured quota.
