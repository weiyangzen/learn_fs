# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory_even.c

## Purpose

`access_memory_even.c` is a synthetic DAMON workload that allocates multiple regions and continuously accesses only even-numbered regions.

## Important APIs, Types, and Functions

It parses `<number> <size_bytes>`, allocates region pointers and regions with `malloc()`, and writes to even-indexed regions with `memset()`.

## Control Flow

After allocation, it enters an infinite loop over all regions. For indexes divisible by two, it writes `i` into the region; odd regions remain idle.

## State and Persistence Behavior

It keeps allocated anonymous memory alive and mutates half the regions indefinitely. No persistent files are written.

## Dependencies and Integration Points

DAMON tests use it to validate region counting and access-pattern detection where active/inactive regions should be distinguishable.

## Risks and Edge Cases

It does not check allocation failures and never exits naturally. Test callers must terminate it.

## Test Signals

DAMON tried regions and region-count bounds should reflect the configured number of regions, especially in `damon_nr_regions.py` and `damos_tried_regions.py`.
