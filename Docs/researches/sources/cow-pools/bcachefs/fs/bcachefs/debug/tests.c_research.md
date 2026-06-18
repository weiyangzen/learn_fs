# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.c

Implements optional `CONFIG_BCACHEFS_TESTS` btree iterator, update, snapshot, extent-overwrite, and performance tests callable through the sysfs `perf_test` attribute.

Key entry points:
- `bch2_btree_perf_test()` parses a named test, iteration count, and thread count, launches one or more kernel threads, times execution, and prints throughput.
- Unit-style tests cover delete idempotency, delete after journal flush, forward/reverse iteration, slots iteration, extent slot iteration, end peeking, extent overwrite cases, overlapping snapshot extents, and snapshot filtering.
- Performance tests include random insert, multi-insert, lookup, mixed lookup/update, delete, sequential insert, lookup, overwrite, and delete.
- `delete_test_keys()` clears test data from extents and xattrs btrees before many unit tests.

Core mechanics:
- Tests primarily use synthetic `bkey_i_cookie` keys in `BTREE_ID_xattrs` and `BTREE_ID_extents`.
- Iterator tests assert exact offsets, slot/deleted-key behavior, and reverse traversal ordering with `BUG_ON()`.
- Extent overwrite tests insert overlapping extents and rely on btree update behavior to split/overwrite correctly.
- Snapshot tests create snapshot nodes and verify unrelated snapshot keys are skipped as expected.
- Perf tests coordinate start/finish with atomics, wait queues, and completions so threads begin together and timing spans all workers.

Important invariants:
- `nr` and `nr_threads` must be nonzero.
- Unknown test names return `EINVAL_test_unknown_test`.
- Many checks intentionally use `BUG_ON()`, so this code is for controlled debug/test builds.
- Threaded tests divide iterations across `nr_threads`.

Filesystem relevance:
- Provides in-kernel stress and correctness coverage for bcachefs btree iteration/update semantics, especially areas that affect metadata lookup, extents, snapshots, and hash-table-like xattr/dirent behavior.

Notable risks:
- Test cleanup deletes broad key ranges in extents and xattrs btrees, so it is not a normal production data path.
- `BUG_ON()` assertions can crash a kernel when a test fails.
- Tests are compiled only under `CONFIG_BCACHEFS_TESTS` and exposed through sysfs only in that configuration.
