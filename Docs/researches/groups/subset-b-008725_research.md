# subset-b-008725 research

Grouped research for RocksDB trie index DB integration tests and factory implementation under `sources/storage-engines/rocksdb/utilities/trie_index`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_db_test.cc -->
# sources/storage-engines/rocksdb/utilities/trie_index/trie_index_db_test.cc

## Purpose

DB-level integration coverage for the experimental trie-based User Defined Index (UDI). The suite verifies that RocksDB block-based tables written with `TrieIndexFactory` remain readable and iterable through flush, compaction, reopen, external SST ingest, transactions, snapshots, range tombstones, prefix iteration, coalescing iterators, and primary-vs-secondary UDI modes. It complements lower-level SST tests by exercising the full DB path: memtables, WAL replay, `CompactionIterator`, block-based table building, table reader routing, and `ReadOptions::table_index_factory`.

## Important APIs, types, and helpers

The test fixture `TrieIndexDBTest : testing::TestWithParam<bool>` runs every test twice: `false` means UDI is a secondary index selected by `ReadOptions::table_index_factory`; `true` means `BlockBasedTableOptions::use_udi_as_primary_index` routes default reads through the trie. `OpenDBImpl` installs a shared `TrieIndexFactory` in `BlockBasedTableOptions`, optionally forces small data blocks, and stores `last_options_` for cleanup. `OpenDBWithoutUDI`, `OpenDBPrimary`, and `OpenDBSecondary` model migration and rollback paths.

Reusable verification helpers compare standard-index and trie-index behavior for `Get`, `Get` at snapshot, `GetEntity`, `MultiGet`, forward scans, reverse scans, `Seek`, `SeekForPrev`, prefix scans, and lockstep multi-prefix scans. `StandardIndexReadOptions()` returns bare `ReadOptions`; `TrieIndexReadOptions()` sets `table_index_factory` only in secondary mode. Key helpers build fixed-width and stress-like bytewise keys, padded values, and an `SstQueryFilterConfigsManager::Factory` with `StressLikeVariableWidthExtractor` for range-query table filters.

## Control flow and behavior covered

The first test group writes all RocksDB operation types that matter to table building: `Put`, `Delete`, `Merge`, `SingleDelete`, `PutEntity`, `TimedPut` through `WriteBatch::TimedPut`, and `DeleteRange`. Tests flush or compact those records, then assert the same visible key/value view through both indexes. Snapshot-heavy compaction tests deliberately preserve multiple versions so the trie index must select the correct data block for a target sequence number.

The same-user-key tests force many versions of one or more keys across data block boundaries by using tiny block sizes and held snapshots. They verify the trie factory's seqno side-table and overflow-block logic through `Get`, `Seek`, forward scans, reverse scans, `Prev`, and compaction. `NonBoundarySeparatorSeekCorrectness` reproduces a bug class where `FindShortestSeparator` returns an unchanged separator for different user keys while seqno encoding is active; the expected behavior is that the trie does not incorrectly advance past the target block.

Iterator coverage includes `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, direction switching, `SeekForPrev`, upper and lower bounds, snapshot plus bound interactions, iterator stability across flushes, `auto_refresh_iterator_with_snapshot`, `allow_unprepared_value`, and `NewCoalescingIterator` for both single-CF and multi-CF scans. Prefix coverage uses fixed prefix extractors, `total_order_seek`, `auto_prefix_mode`, empty prefixes, bounds, deletes, merges, memtable-plus-SST mixes, compaction, and crash-test-like batches.

Persistence and deployment-path tests cover WAL replay, reopen with cold SST reads, external file ingest using `SstFileWriter`, many small L0 SSTs, overlapping L0 SSTs, mixed SSTs with and without UDI, reopening a UDI DB without a UDI factory, primary UDI migration, rejection of pre-UDI SSTs when primary UDI is required, rollback from primary to secondary, rollback from primary without compaction, and table property `udi_is_primary_index`.

## State and persistence behavior

The file uses a per-thread temporary DB path and destroys it in setup/teardown. Most tests force data into SSTs with `FlushOptions` so the trie UDI block is actually built and read. Compaction tests rewrite SSTs and check that the new output still carries a usable trie index. Snapshot tests pin old versions so internal keys for the same user key remain live in the table and exercise trie overflow selection. Reopen and WAL replay tests ensure that persisted MANIFEST, WAL, standard index blocks, UDI meta blocks, and table properties survive process-style boundaries.

Primary mode is treated as configuration-driven routing, not a separate file format that drops the standard index. Tests assert that standard index fallback still works when removing UDI after primary-mode SST creation, while opening primary mode over pre-UDI SSTs fails with corruption because the requested primary index block is absent. Migration tests require bottommost force compaction to rewrite legacy SSTs before enabling primary UDI.

## Dependencies and integration points

The suite depends on RocksDB DB APIs (`DB`, `TransactionDB`, `WriteBatch`, `SstFileWriter`, `IngestExternalFileOptions`, `CompactRangeOptions`, snapshots, iterators, wide columns), block table configuration (`BlockBasedTableOptions`, table properties, compression), merge operators, prefix transforms, table filters, and test utilities. It directly integrates with `utilities/trie_index/trie_index_factory.h` and indirectly with the UDI builder/reader wrapper in block-based table construction.

## Risks and edge cases

Primary risks are index/data iterator desynchronization, incorrect block choice when the same user key spans blocks, wrong handling of last-block separators, over-aggressive bound rejection, fallback failures for mixed UDI/non-UDI files, non-bytewise or binary key ordering bugs, stale snapshot reads after refresh, and missing support in non-Get paths such as `MultiGet`, `GetEntity`, checksums, transactions, and coalescing iterators. The tests also call out issues around `kTypeValuePreferredSeqno`, range tombstones across levels, external SSTs, compressed data blocks, and empty/deletion-only tables.

## Test signals

Passing signals are exact equality between standard-index and trie-index scans, point reads, snapshot reads, iterator movement, and status codes. The strongest signals are the parameterized primary/secondary run, full migration/rollback tests, same-user-key overflow tests, randomized multi-level `DeleteRange` consistency checks, stress-like prefix scans, and table property assertions. Some tests are intentionally skipped or bypassed when a mode is not applicable, such as secondary-only fallback tests or zlib-dependent compression coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_db_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.cc -->
# sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.cc

## Purpose

Implements the RocksDB trie UDI factory, builder, reader, and iterator declared in `trie_index_factory.h`. The implementation converts block separator keys into a serialized LOUDS trie, stores block handles and sequence-number side-table metadata, deserializes that trie on read, and adapts `LoudsTrieIterator` to the `UserDefinedIndexIterator` contract.

## Important APIs and functions

`TrieIndexBuilder::AddIndexEntry` is called at every data block boundary. It computes a user-key separator with the comparator, detects same-user-key or duplicate-separator boundaries, chooses a packed tag for seqno correction, buffers `(separator_key, tag, handle)`, and returns the separator to RocksDB. `OnKeyAdded` is intentionally a no-op because the trie is built from block separators, not every data key. `Finish` emits the serialized trie by de-duplicating consecutive equal separators into one trie leaf plus overflow blocks.

`TrieIndexBuilder::EstimatedSize` returns an approximate serialized size from accumulated separator bytes and entry count. `TrieIndexIterator` implements `Prepare`, `SeekToFirstAndGetResult`, `SeekToLastAndGetResult`, `SeekAndGetResult`, `NextAndGetResult`, `PrevAndGetResult`, and `value`. `TrieIndexReader::InitFromSlice`, `NewIterator`, and `ApproximateMemoryUsage` wrap the deserialized `LoudsTrie`. `TrieIndexFactory::NewBuilder` and `NewReader` validate the comparator and construct the concrete builder/reader.

## Control flow

Builder flow is deferred: `AddIndexEntry` only buffers entries, and `Finish` makes the all-or-nothing serialization decision. Seqno encoding is effectively always enabled once at least one entry exists. During `Finish`, consecutive entries with identical separator keys form a run. The first entry becomes the trie leaf via `AddKeyWithSeqno`; later entries become overflow blocks via `AddOverflowBlock`. An empty builder still calls `trie_builder_.Finish()` so readers receive a parseable empty trie rather than an empty slice.

Seek flow uses user-key trie search first, then optional seqno correction. `SeekAndGetResult` advances scan option state past exhausted scan ranges, seeks the LOUDS trie by target user key, reconstructs the current separator into scratch storage, and if seqno encoding is present compares `context.target_tag` with the leaf and overflow seqnos to select the correct block in a same-key run. Exhausting the trie returns `IterBoundCheck::kUnknown` rather than `kOutOfBound` so higher-level level iteration does not stop scanning other SSTs prematurely.

Forward and reverse iteration first consume overflow runs when possible. `NextAndGetResult` increments `overflow_run_index_` inside a run before moving to the next trie leaf; `PrevAndGetResult` decrements inside the run before moving to the previous leaf. `value()` returns the primary trie leaf handle for run index 0 and the side-table overflow handle otherwise. Bounds are checked conservatively against a reference key, not the current separator, because trie keys are block upper bounds.

## State and persistence behavior

Persistent state is the serialized LOUDS trie returned by `LoudsTrieBuilder::GetSerializedData()`. It includes trie structure, block handles, a flag for seqno encoding, per-leaf seqnos, block counts, overflow bases, and overflow handles/seqnos owned by `LoudsTrie`. Runtime builder state includes the comparator, buffered entries, a finished guard, a sticky seqno flag, and a running separator-byte total. Runtime iterator state includes scan options, current scan index, scratch strings for current and previous separator keys, and overflow-run indexes.

The reader keeps zero-copy references into the serialized index block and reports memory as raw data size plus `LoudsTrie` auxiliary lookup tables. Because the data slice must remain valid for the reader lifetime, the implementation relies on RocksDB table/block cache lifetime rules.

## Dependencies and integration points

The implementation uses RocksDB's `Comparator`, `Status`, `Slice`, `UserDefinedIndex*` interfaces, `IndexEntryContext::last_key_tag`, `BlockHandle`, `PackSequenceAndType`, and `BytewiseComparator`. It depends on `utilities/trie_index/louds_trie.h` for builder, reader, iterator, block handle, seqno side-table, and overflow metadata. It integrates with block-based table building through `UserDefinedIndexFactory::NewBuilder` and with table reads through `NewReader`.

## Risks and edge cases

The factory only supports bytewise comparator ordering; non-bytewise comparators are rejected because the trie traverses byte lexicographic order. Separator correctness is delicate: the last block deliberately uses the actual last key, not a shortened successor, to avoid widening the indexed key range. Duplicate separators from either same user keys or failed shortening must not receive `kMaxSequenceNumber` sentinel behavior that would break overflow selection. Bound checking must stay conservative or level iteration can terminate too early. The unconditional seqno side-table costs extra bytes per leaf but simplifies last-block and same-key correctness.

## Test signals

Coverage is supplied by `trie_index_db_test.cc` and lower-level trie/SST tests. Relevant signals include same-user-key snapshot reads, duplicate separator reproductions, reverse iteration through overflow runs, last-block separator tests, primary/secondary migration tests, bounds tests, mixed UDI/non-UDI SST fallback, and `EstimatedSizeNonZero` table property checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.h -->
# sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.h

## Purpose

Declares the public experimental trie UDI components for RocksDB block-based tables. The header exposes `TrieIndexFactory`, the builder used during SST creation, the reader used for deserialized UDI blocks, and the iterator adapter used by table reads. It documents the intended use: set `BlockBasedTableOptions::user_defined_index_factory` when writing, and use `ReadOptions::table_index_factory` in secondary mode when reading.

## Important APIs and types

`TrieIndexBuilder final : UserDefinedIndexBuilder` owns a `LoudsTrieBuilder`, comparator pointer, finished flag, seqno-encoding flag, buffered separator entries, and a separator byte counter. Its API is `AddIndexEntry`, `OnKeyAdded`, `Finish`, and `EstimatedSize`. `BufferedEntry` stores the user-key separator, packed tag, and `TrieBlockHandle` for each block-boundary entry.

`TrieIndexIterator final : UserDefinedIndexIterator` adapts `LoudsTrieIterator` to RocksDB's UDI iteration contract. It exposes `Prepare`, seek-to-first/last, seek, next, prev, and `value`. It stores scan options, current scan index, prepared state, current and previous key scratch strings, trie pointer, comparator pointer, and overflow-run state (`overflow_run_index_`, `overflow_run_size_`, `overflow_base_idx_`). Inline helpers reset or initialize overflow state and copy trie keys into the UDI result.

`TrieIndexReader : UserDefinedIndexReader` owns a `LoudsTrie` plus comparator and raw data size. It initializes from a serialized slice, creates iterators, and reports approximate memory usage. `TrieIndexFactory : UserDefinedIndexFactory` names the customizable `"trie_index"`, aborts deprecated builder/reader APIs, and implements comparator-aware `NewBuilder` and `NewReader` overloads accepting `UserDefinedIndexOption`.

## Control flow contract

The builder contract follows RocksDB SST construction order: `OnKeyAdded` may be called for every key, `AddIndexEntry` is called for each data block boundary, then `Finish` serializes the index. The header makes clear that actual trie construction is deferred until `Finish`, allowing the implementation to make a global seqno side-table decision after all separator entries are known.

The iterator contract is scan-oriented. `Prepare` receives one or more `ScanOptions` ranges. Seeking positions the trie and sets result keys; next/prev advance either through overflow blocks for same-key runs or through trie leaves. `value()` must return the handle matching the logical current block, including overflow blocks, rather than blindly returning the trie leaf handle.

## State and persistence behavior

The header separates persistent trie contents from transient adapters. Persistent contents are produced by `LoudsTrieBuilder` and later loaded into `LoudsTrie`. Transient build state is the buffered list of separators and tags. Transient read state is held per iterator, so multiple iterators can independently maintain bounds, scratch keys, and overflow positions over the same reader-owned trie.

Seqno handling is a central state contract: the comments state that seqno encoding is always enabled after entries are added, with an 8-byte per-leaf overhead. Tags distinguish same-user-key boundaries, last-block separators, and ordinary non-boundary separators using real packed tags or the 0 sentinel.

## Dependencies and integration points

The header depends on `rocksdb/user_defined_index.h`, `rocksdb/comparator.h`, `rocksdb/types.h`, and `utilities/trie_index/louds_trie.h`. It is included by DB tests, the factory implementation, and block-table code that instantiates UDI builders/readers through the `UserDefinedIndexFactory` interface. It also participates in RocksDB's `Customizable` naming through `Name()` and `kClassName()`.

## Risks and edge cases

Deprecated base-class APIs abort unconditionally, so callers must use the `UserDefinedIndexOption` overloads. The comparator pointer is non-owning and must remain valid under RocksDB's options lifetime rules. Reader slices must remain alive for the reader because `LoudsTrie` uses serialized data directly. Iterator scratch strings back returned `Slice` keys, so result key lifetimes are tied to the iterator and overwritten on movement. Overflow state must be reset or initialized correctly on every movement to avoid returning the wrong block handle.

## Test signals

The DB test suite validates this header's contract through builder creation, reader creation, iterator movement, primary/secondary routing, seqno overflow handling, and estimated size. The implementation's bytewise-comparator restriction and deprecated API abort behavior should be considered API compatibility signals when integrating with other comparator or Customizable paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_factory.h -->
