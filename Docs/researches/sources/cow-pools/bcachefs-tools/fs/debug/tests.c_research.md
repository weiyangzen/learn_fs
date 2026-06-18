# File Research: sources/cow-pools/bcachefs-tools/fs/debug/tests.c

## Purpose

Provides optional btree unit/performance tests compiled under `CONFIG_BCACHEFS_TESTS`. The tests are invoked from sysfs `perf_test` and exercise btree insertion, lookup, deletion, iteration, extent overwrite behavior, snapshot filtering, and deliberately corrupted extent cases.

## Main Interfaces

- `bch2_btree_perf_test(struct bch_fs *c, const char *testname, u64 nr, unsigned nr_threads)`.
- Internal named tests selected by string: random insert/multi-insert/lookup/mixed/delete, sequential insert/lookup/overwrite/delete, delete tests, forward/reverse iteration, slot iteration, extent overwrite variants, overlapping extent creation, duplicate physical extent injection, and snapshot filtering.

## Behavior

The file deletes prior test keys from `extents` and `xattrs`, inserts cookie keys or extents, and validates iterator behavior with `BUG_ON()` assertions. Extent overwrite tests insert overlapping logical ranges and rely on btree update semantics. Snapshot tests create snapshot nodes and verify lookup filtering.

Performance tests run a selected function across one or more kthreads. A shared `test_job` synchronizes thread start with atomics and a waitqueue, records `sched_clock()` timing, waits for completion, and prints total time, nanoseconds per iteration, and throughput.

## State And Side Effects

Tests mutate live btrees, especially `BTREE_ID_xattrs` and `BTREE_ID_extents`, and can inject intentionally malformed duplicate physical extents for fsck repair validation. They flush journal pins in `test_delete_written()` and may create snapshot nodes. The code is not a passive diagnostic; it is a destructive/internal test harness.

## Dependencies

Uses bcachefs btree update/iterator APIs, bucket allocation headers, journal reclaim, snapshot creation, kernel kthreads, random bytes, and the test declaration header.

## Risks And Notes

Many failures use `BUG_ON()`, so this is for controlled testing only. `bch2_btree_perf_test()` rejects zero iterations or zero threads with custom `EINVAL_test_*` errors. Unknown test names are also custom error returns.
