# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory.c

## Purpose

`access_memory.c` is a synthetic workload for DAMON tests. It allocates a configurable number of regions and touches each for a configurable duration, once or repeatedly.

## Important APIs, Types, and Functions

It defines `enum access_mode`, parses `<number> <size> <time_ms> [repeat]`, allocates `char **regions`, uses `malloc()`, `clock()`, `CLOCKS_PER_SEC`, and `memset()`.

## Control Flow

The program validates arguments, allocates region pointers and backing memory, then loops over regions. For each region it writes bytes until the requested per-region milliseconds elapsed. If mode is `repeat`, the region loop repeats forever.

## State and Persistence Behavior

It allocates anonymous process memory and continuously changes its contents. No files are written; process memory access patterns are observed externally by DAMON.

## Dependencies and Integration Points

DAMON Python tests launch this binary to produce predictable working sets for WSS, quota, and apply-interval tests.

## Risks and Edge Cases

There is no allocation failure handling and no cleanup before exit. Timing uses CPU `clock()` rather than wall time, which can vary with scheduling.

## Test Signals

The signal is external: DAMON should report tried bytes/regions corresponding to the touched region size and access cadence.
