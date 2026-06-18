# subset-b-008572 Research

Grouped research for the listed RocksDB files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/c_test.c -->
# sources/storage-engines/rocksdb/db/c_test.c

## Purpose
This file is RocksDB's broad C API regression and smoke test for `rocksdb/c.h`. It is a single C translation unit that opens real temporary RocksDB instances, exercises nearly every exported C wrapper family, verifies data-path behavior with direct assertions, and checks that wrapper-owned handles can be created, queried, and destroyed without obvious ABI or lifetime regressions.

The suite is intentionally end-to-end rather than mock-driven. It validates database creation, backup/restore, checkpoints, external SST ingestion, write batches, iterators, pinned reads, multi-get variants, column families, prefix/filter behavior, option getter/setter parity, transactions, optimistic transactions, secondary instances, statistics, wait-for-compact, write buffer management, remote compaction service callbacks, SST file manager settings, and final background-work cancellation.

## Important APIs, Types, And Helpers
The test imports only the public C API header, `rocksdb/c.h`, plus standard C/POSIX headers. Its helper layer includes:

- `StartPhase`, `CheckNoError`, `CheckCondition`, `CheckEqual`, `Free`, `CheckValue`, and `CheckPinnedValue`, which make phase-tagged failures abort immediately.
- `CheckGet`, `CheckGetCF`, `CheckPinGet`, and `CheckPinGetCF`, which wrap normal and pinned point lookup checks.
- `CheckMultiGetValues`, `CheckIter`, and write-batch callback validators (`CheckPut`, `CheckDel`, `CheckPutCF`, `CheckDelCF`, `CheckMergeCF`, `CheckLogData`).
- Custom callback implementations for comparator (`CmpCompare`/`CmpName`), compaction filter and factory (`CFilterFilter`, `CFilterCreate`), merge operator (`MergeOperatorFullMerge`, `MergeOperatorPartialMerge`), and remote compaction service (`RemoteCompactionSchedule`, `RemoteCompactionWait`, `RemoteCompactionCancel`, `NullSchedule`).
- `CheckMetaData`, `GetAndCheckMetaData`, and `GetAndCheckMetaDataCf`, which validate column-family metadata, level metadata, and SST file metadata returned through the C wrappers.
- `LoadAndCheckLatestOptions`, which loads persisted options from a DB, checks expected column-family names/options, and verifies reopening with the loaded options.

The `main` function creates and destroys many C API handle types: `rocksdb_t`, `rocksdb_options_t`, `rocksdb_readoptions_t`, `rocksdb_writeoptions_t`, `rocksdb_compactoptions_t`, `rocksdb_cache_t`, `rocksdb_env_t`, `rocksdb_dbpath_t`, `rocksdb_checkpoint_t`, `rocksdb_backup_engine_t`, `rocksdb_writebatch_t`, `rocksdb_writebatch_wi_t`, `rocksdb_iterator_t`, `rocksdb_column_family_handle_t`, `rocksdb_transactiondb_t`, `rocksdb_transaction_t`, `rocksdb_optimistictransactiondb_t`, table/filter/compaction/backup/statistics/memory/remote-compaction option wrappers, and factory wrappers.

## Control Flow
The program is a linear phase-driven test. Temporary path names are derived from `TEST_TMPDIR` or `/tmp`/`TEMP` and a process/user-derived test id, then each `StartPhase` block mutates the DB or a wrapper object and validates expected results before moving on.

Early phases construct base options, a custom comparator, block-based table options, LRU cache, default env, rate limiters, read/write/compact options, and the base DB. Basic persistence phases then destroy/open the DB, put and get `foo`, create backups, restore from the latest backup, compare DB identities, create checkpoints, test DB identity behavior when `write_dbid_to_manifest` is enabled, and export/import a column family through checkpoint metadata.

Middle phases exercise data operations. Compaction APIs are run over full and bounded ranges. Cache usage is checked after pinning data through an iterator. External SST files are written with `rocksdb_sstfilewriter_t`, ingested, overwritten, and cleaned up. WriteBatch and WriteBatchWithIndex coverage includes put/delete/delete-range, vectored key/value APIs, savepoints, serialized representation round trips, indexed reads from batch plus DB, batch iterators over base DBs, and read-option bounds.

Iterator/read phases verify first/last/next/prev/seek/seek-for-prev, slice-returning iterator APIs, ordinary multi-get, pinned zero-copy reads, `rocksdb_get_into_buffer`, approximate sizes, property reads, snapshots, snapshot behavior with in-place memtable updates, repair, filters using Bloom/Ribbon policies, compaction filters/factories, merge operator behavior, and prefix seek behavior with plain table/hash skiplist configuration.

Column-family coverage creates, lists, opens, writes, deletes, range-deletes, flushes, multi-gets, batched multi-gets, slice-based batched multi-gets, pinned CF reads, `key_may_exist`, CF iterators, multi-CF iterator creation, metadata inspection, CF-specific DB paths, option loading, and dropped-CF cleanup.

The large options section checks many `rocksdb_options_t` setters/getters, makes an independent copy, then mutates the copy to confirm fields are copied rather than aliased. Separate phases cover read, write, compact, flush, cache, allocator, logger, env, universal compaction, FIFO compaction, backup-engine, and compression options.

Transaction phases open TransactionDBs and OptimisticTransactionDBs, exercise direct DB reads/writes, transactional reads/writes/deletes, pinned reads, multi-get, transaction names, WAL log data scanning via `rocksdb_get_updates_since`, snapshots, iterators, rollback, savepoints, column families, memory usage, WAL/CF flushes, two-phase prepare/commit/rollback recovery, `multi_get_for_update` lock conflicts, write-prepared policy, and optimistic transaction reopen with column families.

Late phases test memtable representation selection, secondary DB catch-up, DB paths, prefix-seek filters, statistics ticker/histogram access, wait-for-compact options, wait-for-compact execution, write buffer manager fields, remote compaction callback installation/fallback behavior, scheduler response wrappers, compaction service options override setters, checksum/SST partitioner factories on regular options, null remote callback handling, cancellation flag wrappers, SST file manager settings, duplicate-column-family error returns, `rocksdb_cancel_all_background_work`, and final handle destruction.

## State And Persistence Behavior
The file creates real on-disk RocksDB state under temporary directories. It repeatedly destroys and recreates `dbname`, creates separate backup/checkpoint/SST/DB-path/secondary/import/export paths, and uses actual WAL, SST, MANIFEST, checkpoint, backup, and column-family metadata side effects as test evidence.

Persistence-sensitive checks include restore retaining `"foo"`, checkpoint and backup DB identity changes, manifest-stored DB identity remaining stable across checkpoint reopen, external SST ingestion materializing keys, metadata reporting non-empty levels/files, write batch WAL log data being discoverable after commit, prepared transactions surviving DB reopen, secondary DB catch-up seeing primary writes, and statistics counters/histograms changing after writes. Most allocated C API return values are explicitly freed or destroyed, which is part of the wrapper contract under test.

## Dependencies And Integration Points
This file is integrated with RocksDB's C binding layer and indirectly with many C++ subsystems: DB open/close/destroy/repair, Env, Cache, block-based/plain/cuckoo table factories, filters, prefix extractors, compaction, backup engine, checkpoints, external SST ingestion, metadata, WriteBatch, WriteBatchWithIndex, snapshots, WAL iteration, TransactionDB, OptimisticTransactionDB, memory accounting, statistics, remote compaction service, file checksum factories, SST partitioners, and SST file manager.

Because it includes only `rocksdb/c.h`, it is an ABI-facing test: new C wrappers are often wired into this file to prove they compile from C, expose sensible ownership semantics, map options correctly, and interoperate with the underlying C++ implementation.

## Risks And Edge Cases
The test is large and linear, so earlier option mutations can leak into later phases if not reset carefully. Several phases rely on precise data-path side effects such as Bloom/Ribbon false-positive counters, non-empty metadata after compaction/flush, DB identity length, or platform-specific allocator support. Temporary path handling uses fixed-size 200-byte buffers and process-derived names; unusually long `TEST_TMPDIR` paths can stress these buffers.

Resource lifetime is a major risk area. The file tests many ownership boundaries, but any missed destroy/free can hide in the long happy path. Conversely, destroying a factory or logger too early would expose wrapper ownership bugs. Remote compaction coverage intentionally falls back to local compaction; it validates callback plumbing rather than a real serialized remote compaction result.

## Test Signals
The primary signal is the process printing `PASS` after every phase completes without aborting. Failures include phase names in stderr. Meaningful sub-signals include successful DB reopen after loaded options, expected point lookup results after each mutation, expected CF list sizes/names, expected metadata invariants, option getter values matching setters and independent copies, expected transaction conflict/prepared-transaction behavior, non-zero statistics after writes, remote compaction schedule/wait counters, and `create_column_family` returning `NULL` with an error for duplicate names.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/c_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/coalescing_iterator.cc -->
# sources/storage-engines/rocksdb/db/coalescing_iterator.cc

## Purpose
Implements `CoalescingIterator::Coalesce`, the value-population hook for an iterator that exposes a single logical key across multiple column-family iterators by coalescing their wide-column values. The implementation gathers wide columns from matching child iterators, chooses one value per column name according to the order supplied by `MultiCfIteratorImpl`, stores owned copies of the bytes, and exposes the default wide column as the iterator's scalar `value()` when present.

## Important APIs, Types, And Functions
The source includes `db/coalescing_iterator.h` and `db/wide/wide_columns_helper.h`. Its only function is:

- `void CoalescingIterator::Coalesce(const autovector<MultiCfIteratorInfo>& items)`: called by `MultiCfIteratorImpl` after it has found child iterator entries at the current coalesced key.

It uses the header-defined `MinHeap`, `WideColumnWithOrder`, and `WideColumnWithOrderComparator`. `MultiCfIteratorInfo` supplies an `iterator` pointer and an `order` field. The child `Iterator::columns()` API provides `WideColumn` entries, and `WideColumnsHelper::HasDefaultColumn`/`GetDefaultColumn` identify the conventional default column used to fill the scalar `value_` slice.

## Control Flow
`Coalesce` starts with assertions that `wide_columns_` and `owned_columns_` are empty. It creates a heap and pushes every wide column from every input child iterator, tagging each with the child order. If no columns exist, it returns and leaves the iterator's value/columns empty.

For non-empty input, it reserves storage sized to the heap, then defines `add_column`, which copies a wide column name and value into `owned_columns_` and appends a `WideColumn` pointing at those owned strings into `wide_columns_`. The heap is then popped in sorted order. When the next heap entry has a larger name than the current entry, the current column is emitted. When names compare equal, the current column is replaced by the later popped heap entry, so duplicates collapse to one emitted column. A comparison showing the current name greater than the heap top is treated as an impossible heap-order violation and asserted.

After the heap is drained, the last current column is emitted. If the final wide-column list contains a default column, `value_` is set to the default column's value slice.

## State And Persistence Behavior
This code has no disk persistence. Its important state is in-memory iterator result state:

- `owned_columns_` owns copied `std::string` name/value bytes.
- `wide_columns_` contains `WideColumn` objects whose slices point into `owned_columns_`.
- `value_` points to the default column value inside `wide_columns_` when present.

The explicit copies are a lifetime guard: coalesced results remain valid even if child iterators refresh or reuse internal buffers after the populate step. `Reset` in the header clears these containers before the next movement/repopulation cycle.

## Dependencies And Integration Points
`Coalesce` is integrated with `MultiCfIteratorImpl`, which handles movement and groups child iterators at a logical key before invoking the populate callback. It depends on each child iterator supporting the wide-column `columns()` API and on the ordering contract encoded by `MultiCfIteratorInfo::order`. It also depends on `BinaryHeap` semantics to provide ascending wide-column-name order through the custom comparator.

The scalar `Iterator::value()` compatibility path is integrated through `WideColumnsHelper`, so callers that only understand key/value entries still see the default wide column when coalesced data includes one.

## Risks And Edge Cases
Duplicate wide-column names are resolved by heap pop order and `item.order`; this makes the comparator's tie-break behavior critical. If the order semantics change in `MultiCfIteratorImpl`, coalescing precedence could silently change. The function asserts rather than reports an error for heap-order violations, so release builds may not catch impossible ordering issues explicitly.

The function assumes `Reset` was called before population, enforced by asserts. If future code calls `Coalesce` directly without clearing state, old columns could leak into the new logical result in non-assert builds. The empty-column case returns without setting `value_`, so callers rely on the reset path to avoid stale values.

## Test Signals
Useful tests should construct multiple child iterators that yield the same user key with disjoint and overlapping wide-column names, then verify sorted output column names, deterministic duplicate-name precedence, copied lifetime after child iterator movement, empty-column behavior, and scalar `value()` exposure when the default column is present. Integration tests should move forward and backward through a multi-CF coalescing iterator to confirm `Reset` and `PrepareValue` interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/coalescing_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/coalescing_iterator.h -->
# sources/storage-engines/rocksdb/db/coalescing_iterator.h

## Purpose
Declares `CoalescingIterator`, a RocksDB `Iterator` implementation that delegates multi-column-family positioning to `MultiCfIteratorImpl` and customizes value population by merging wide columns from all child iterators at the current logical key. It provides the ordinary `Iterator` surface while preserving coalesced wide-column results and a scalar default-column value.

## Important APIs, Types, And Members
The constructor accepts `ReadOptions`, a `Comparator`, and an rvalue vector of `(ColumnFamilyHandle*, unique_ptr<Iterator>)` pairs. These are forwarded into `MultiCfIteratorImpl<ResetFunc, PopulateFunc>` along with callbacks bound to the enclosing `CoalescingIterator`.

The public iterator API delegates almost entirely to `impl_`: `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, `status`, and `PrepareValue`. `value()` returns `value_` and `columns()` returns `wide_columns_`, both requiring `Valid()`. `Reset()` clears `value_`, `wide_columns_`, and `owned_columns_`.

Private helper types are:

- `ResetFunc`: callback object that invokes `iter_->Reset()`.
- `PopulateFunc`: callback object that invokes `iter_->Coalesce(items)`.
- `WideColumnWithOrder`: heap item containing a `WideColumn` pointer and a child order.
- `WideColumnWithOrderComparator`: comparator that orders heap items by column name and then by order.
- `MinHeap`: `BinaryHeap<WideColumnWithOrder, WideColumnWithOrderComparator>`.

Private state consists of `impl_`, `value_`, `wide_columns_`, and `owned_columns_`. `owned_columns_` is a vector of copied `(name, value)` strings used to back the slices stored in `wide_columns_` and `value_`.

## Control Flow
All movement and seek operations are delegated to `MultiCfIteratorImpl`. When the delegated implementation needs to discard the current materialized value, it calls `ResetFunc`, clearing all coalesced result storage. When it needs to materialize the value/columns for the current key, it calls `PopulateFunc`, which passes the current matching `MultiCfIteratorInfo` set into `Coalesce`.

The `PrepareValue` override is also delegated to `impl_`, which means lazy value preparation, if any, is coordinated by the multi-CF implementation. Once prepared, callers retrieve the current coalesced key from `impl_.key()`, scalar value from `value_`, and wide-column set from `wide_columns_`.

## State And Persistence Behavior
`CoalescingIterator` has no persistent state; it is a transient read iterator. Its stateful behavior is about pointer validity and lifecycle. `value_` and `wide_columns_` expose slices, but the actual bytes are owned by `owned_columns_`, so values survive child iterator internal buffer reuse until the next reset. The class is non-copyable because it owns iterators and slice-backed result buffers.

`Reset` is the boundary between logical positions. It must run before new coalesced data is populated, otherwise stale slices could be exposed. The destructor is default-like and relies on member destructors for child iterator and buffer cleanup.

## Dependencies And Integration Points
The header depends on `db/multi_cf_iterator_impl.h` for movement, grouping, `MultiCfIteratorInfo`, `BinaryHeap`, and callback orchestration. It depends on RocksDB iterator abstractions (`Iterator`, `ReadOptions`, `Comparator`, `Slice`, `WideColumns`, `ColumnFamilyHandle`) and is implemented further in `coalescing_iterator.cc`.

This class is an adapter between the multi-CF iterator infrastructure and wide-column semantics. It lets higher-level code use a normal `Iterator` API over several column-family iterators while receiving a single coalesced wide-column view per key.

## Risks And Edge Cases
The class exposes `value()` and `columns()` only when valid, guarded by asserts. Callers in release builds still need to respect the `Iterator` contract. The callback objects store raw pointers to the parent iterator; this is safe only because they are embedded in `impl_` inside the parent and do not outlive it.

Tie-breaking for duplicate wide-column names is encoded in the heap comparator and implemented in `Coalesce`; mistakes there affect which column value wins. Because `value_` points into `owned_columns_` through `wide_columns_`, changing the storage container type or appending after taking slices would require careful lifetime review. The current `reserve(heap.size())` in the implementation is important to avoid vector reallocation invalidating stored string references while constructing `wide_columns_`.

## Test Signals
Header-level expectations are best validated through integration tests using real child iterators: movement delegates should keep key ordering stable across column families, `PrepareValue` should populate exactly once per logical position, `Reset` should clear stale values between keys, `columns()` should remain valid until movement, and `value()` should track the default wide column. Compile-time signal includes enforcing non-copyability and successful template instantiation with `MultiCfIteratorImpl<ResetFunc, PopulateFunc>`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/coalescing_iterator.h -->
