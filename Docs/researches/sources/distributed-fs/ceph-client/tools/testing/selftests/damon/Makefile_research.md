# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/Makefile

## Purpose

The DAMON Makefile builds helper binaries and registers sysfs, functionality, and regression tests for DAMON selftests.

## Important APIs, Types, and Functions

It declares `TEST_GEN_FILES += access_memory access_memory_even`, shared `TEST_FILES` for `_damon_sysfs.py`, `drgn_dump_damon_status.py`, and `_common.sh`, and many `TEST_PROGS` including sysfs ABI tests, quota tests, tried-region tests, reclaim/lru_sort tests, and regressions.

## Control Flow

`../lib.mk` builds C helpers and runs scripts. The generated C programs provide synthetic memory access patterns for the Python DAMON tests.

## State and Persistence Behavior

The Makefile persists test inventory and build-clean metadata. Runtime tests mutate DAMON sysfs and module parameters.

## Dependencies and Integration Points

It integrates with DAMON sysfs, DAMON paddr/vaddr, DAMON reclaim, DAMON LRU sort, and debug sanity features.

## Risks and Edge Cases

If helper Python files are not installed as `TEST_FILES`, many tests fail at import or drgn invocation. `EXTRA_CLEAN` only removes `__pycache__`.

## Test Signals

Successful build creates memory access helpers and exposes all DAMON scripts to kselftest.
