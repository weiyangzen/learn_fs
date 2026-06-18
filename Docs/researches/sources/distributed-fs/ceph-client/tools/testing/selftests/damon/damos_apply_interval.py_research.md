# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_apply_interval.py

## Purpose

`damos_apply_interval.py` verifies DAMOS `apply_interval_us` changes how often a scheme is tried.

## Important APIs, Types, and Functions

It launches `access_memory`, creates two `Damos` schemes with the same access pattern but different `apply_interval_us`, then reads `DamosStats.nr_tried` through `_damon_sysfs.update_schemes_stats()`.

## Control Flow

The workload touches two 10 MiB regions for two seconds each. DAMON starts with two schemes: one using the aggregation interval by setting apply interval 0, and one using 10 ms. After the workload exits, the script compares `nr_tried` counts and expects the shorter interval scheme to be tried at least nine times more often.

## State and Persistence Behavior

It mutates DAMON sysfs runtime state and collects per-scheme stats in Python objects. The child process exits naturally after completing memory accesses.

## Dependencies and Integration Points

It depends on DAMOS stats, vaddr monitoring, and the access workload. It validates the sysfs `apply_interval_us` setting against runtime accounting.

## Risks and Edge Cases

The expected ratio is timing-sensitive and may be noisy on overloaded systems. The script does not explicitly stop kdamond at the end, relying on process/test cleanup behavior.

## Test Signals

Failure occurs if either scheme has zero tries or the try ratio is below 9. Success is silent exit 0.
