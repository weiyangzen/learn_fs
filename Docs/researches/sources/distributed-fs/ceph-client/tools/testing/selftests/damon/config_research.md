# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/config

## Purpose

This config declares DAMON features required by the DAMON selftest suite.

## Important APIs, Types, and Functions

It requests `CONFIG_DAMON`, `CONFIG_DAMON_SYSFS`, `CONFIG_DAMON_PADDR`, `CONFIG_DAMON_VADDR`, `CONFIG_DAMON_RECLAIM`, `CONFIG_DAMON_LRU_SORT`, and `CONFIG_DAMON_DEBUG_SANITY`.

## Control Flow

There is no runtime flow; kselftest config tooling consumes the symbols.

## State and Persistence Behavior

It persists only kernel capability requirements.

## Dependencies and Integration Points

These symbols match the sysfs model, physical/virtual address monitoring, reclaim/lru_sort module parameter tests, and debug sanity assertions used by the suite.

## Risks and Edge Cases

Having the config does not guarantee runtime root permissions, drgn availability, or idle kdamond state required by some tests.

## Test Signals

Kernels with these options should expose `/sys/kernel/mm/damon/admin` and module parameter files used by the suite.
