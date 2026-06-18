# subset-b-008727 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/ttl/ttl_test.cc -->
# sources/storage-engines/rocksdb/utilities/ttl/ttl_test.cc

Purpose: This is the black-box and option-serialization regression suite for RocksDB's `DBWithTTL` utility. It verifies that the TTL wrapper appends/strips write timestamps correctly, expires keys only through compaction, preserves normal read APIs before expiry, composes with user compaction filters and merge operators, and exposes registry-created TTL compaction and merge objects through the configurable-object system.

Important APIs and types: The test fixture uses `DBWithTTL::Open`, `CreateColumnFamilyWithTtl`, `SetTtl`, `GetTtl`, `CompactRange`, `Flush`, `Put`, `Write`, `DeleteRange`, `KeyMayExist`, `MultiGet`, `NewIterator`, and `DBWithTTL::Open` overloads for read-only and multi-column-family modes. Local helpers include `SpecialTimeEnv`, which makes `Env::GetCurrentTime` deterministic, `TtlTest`, `MakeKVMap`, `PutValues`, `MakePutWriteBatch`, `ManualCompact`, `SleepCompactCheck`, `SleepCompactCheckIter`, `TestFilter`, and `TestFilterFactory`. The option tests use `ObjectLibrary`, `ConfigOptions`, `CompactionFilter::CreateFromString`, `CompactionFilterFactory::CreateFromString`, `MergeOperator::CreateFromString`, `TtlCompactionFilter`, `TtlCompactionFilterFactory`, `TtlMergeOperator`, `DummyFilter`, `DummyFilterFactory`, and `BytesXOROperator`.

Control flow: Each TTL behavior test creates predictable `keyNN/valueNN` data, opens a fresh TTL wrapper over a per-thread DB path, writes data, advances fake time with `SpecialTimeEnv::Sleep`, forces manual compaction, and checks either presence or absence. Tests cover non-positive TTL as infinity, destruction without explicit `Close`, reads during and after TTL, timestamp reset by rewriting keys, iterator visibility, reopening with same or different TTL, read-only open behavior, write-batch puts/deletes, user compaction-filter precedence, unregistered merge operator tolerance, `KeyMayExist`, `MultiGet`, long TTL values, per-column-family TTLs, changing TTL on an open DB, and `DeleteRange`. The option tests register TTL and dummy objects, create objects from strings, validate options, serialize with `ToString`, and check `AreEquivalent`.

State and persistence behavior: Persistent state is a real RocksDB database under `test::PerThreadDBPath("db_ttl")`; every fixture destroys it on setup and teardown. TTL state is encoded into stored values by the TTL wrapper and later interpreted by TTL compaction filters. Time is not wall-clock state: the wrapped environment returns a mutable integer. Column-family tests persist separate TTL policies for default, existing, and newly created column families. Read-only mode deliberately leaves expired records visible because compaction is unsupported. The tests also exercise in-memory registry state by adding object factories to a per-test `ConfigOptions` registry.

Dependencies and integration points: The file sits at the boundary between `rocksdb/utilities/db_ttl.h`, `utilities/ttl/db_ttl_impl.h`, RocksDB compaction, write batches, iterators, column families, object registry loading, and merge-operator wrapping. It depends on deterministic compaction settings (`max_compaction_bytes = 1`) to strip TTL timestamps promptly and uses `Flush` plus manual compaction to avoid background timing.

Risks: The behavioral tests are sensitive to compaction semantics; `PutValues` inserts a `keymock` sentinel because the compaction filter historically does not delete the last key. Fake time makes tests deterministic but can hide races in real environments. TTL expiration occurs on compaction, so read paths may still see expired keys until compaction runs. The option tests assume registry names and option strings remain stable. The long TTL test protects against 32-bit overflow but does not exhaustively cover time arithmetic.

Test signals: Strong signals include keys remaining visible with absent, zero, or negative TTL; keys disappearing only after fake time plus compaction; updated keys using the newer timestamp; read-only compaction returning `NotSupported`; write-batch deletes overriding TTL visibility; TTL compaction taking precedence over user filters after expiry; user filters dropping/keeping/modifying records before expiry; per-column-family TTL boundaries; `DeleteRange` correctness in memtable and SST states; option objects exposing expected `TTL` values; wrapped dummy filters/operators being discoverable through `CheckedCast`; and invalid wrapped merge-operator configuration failing validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/ttl/ttl_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/types_util.cc -->
# sources/storage-engines/rocksdb/utilities/types_util.cc

Purpose: This file implements small utility functions that bridge public utility code and RocksDB internal-key encoding. It constructs synthetic internal keys suitable for forward and reverse seeks, and parses internal keys back into public `ParsedEntryInfo` fields including optional user-defined timestamps.

Important APIs and types: The exported functions are `GetInternalKeyForSeek`, `GetInternalKeyForSeekForPrev`, and `ParseEntry`. They use `Comparator::timestamp_size`, `Comparator::GetMaxTimestamp`, `Comparator::GetMinTimestamp`, `PutFixed64`, `PackSequenceAndType`, `kMaxSequenceNumber`, `kValueTypeForSeek`, `kValueTypeForSeekForPrev`, `ParseInternalKey`, `ParsedInternalKey`, `StripTimestampFromUserKey`, `ExtractTimestampFromUserKey`, and `GetEntryType`.

Control flow: The seek-key helpers first reject a null comparator, derive the comparator's timestamp size, fetch the comparator's maximum or minimum timestamp, and reject inconsistent timestamp lengths. They then overwrite the caller-provided buffer with the user key, append max timestamp for forward seek or min timestamp for reverse seek when timestamps are enabled, and append the packed internal trailer. `ParseEntry` rejects undersized internal keys and null comparators, delegates trailer parsing to `ParseInternalKey`, validates that the parsed user-key-with-timestamp is large enough for the comparator's timestamp size, strips and extracts timestamp slices when needed, and fills user key, timestamp, sequence, and public entry type.

State and persistence behavior: The functions are stateless and do not persist anything. The caller-owned `std::string` buffer receives owned internal-key bytes. `ParsedEntryInfo` receives `Slice` fields that reference the input internal key; callers must keep the input alive for as long as they inspect those slices.

Dependencies and integration points: The implementation depends on `db/dbformat.h`, so it is utility-facing code with direct knowledge of RocksDB's internal key trailer. It is used by utilities that need to seek or inspect internal entries while respecting user-defined timestamp comparators.

Risks: Comparator timestamp contracts are critical. If `GetMaxTimestamp` or `GetMinTimestamp` returns the wrong length, the helper fails early; if the comparator lies consistently, internal seek behavior can be wrong. `ParseEntry` does not null-check `parsed_entry`, so callers must pass a valid output pointer. Timestamp stripping assumes the comparator's timestamp size matches the key encoding. The helpers construct keys for seek ordering, not for user-visible persistence.

Test signals: The paired tests cover invalid internal-key length, null comparator rejection, parsing of put and delete entries without timestamps, and parsing of put and delete entries with the built-in uint64 timestamp comparator. The seek-key construction helpers are not directly covered in the listed test file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/types_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/types_util_test.cc -->
# sources/storage-engines/rocksdb/utilities/types_util_test.cc

Purpose: This test file validates `ParseEntry` from `types_util.cc`, with and without user-defined timestamps. It ensures that RocksDB internal-key parsing produces the public `ParsedEntryInfo` shape expected by utility callers.

Important APIs and types: Helpers `EncodeAsUint64` and `IKey` construct expected timestamp encodings and internal keys. The tests use `BytewiseComparator`, `BytewiseComparatorWithU64Ts`, `PutFixed64`, `PackSequenceAndType`, `ValueType::kTypeValue`, `ValueType::kTypeDeletion`, `ParsedEntryInfo`, `EntryType::kEntryPut`, `EntryType::kEntryDelete`, and `ParseEntry`.

Control flow: `InvalidInternalKey` passes an undersized key and a null comparator case, expecting `InvalidArgument`. `Basic` builds normal internal keys for `"foo"` put at sequence 3 and `"bar"` deletion at sequence 5, parses them with the bytewise comparator, and checks empty timestamp, sequence, key, and entry type. `UserKeyIncludesTimestamp` appends fixed64 timestamps to user keys before the internal trailer, parses with the uint64 timestamp comparator, and checks that the returned user key is stripped while timestamp contains the encoded fixed64 bytes.

State and persistence behavior: The tests are pure in-memory construction and parsing. The important lifetime behavior is that expected slices are checked while the backing `std::string ikey` remains alive.

Dependencies and integration points: The suite links the public utility header with internal `dbformat` helpers and RocksDB's timestamp-aware comparator. It is a narrow compatibility guard for utilities that parse internal entries from iterators or diagnostics.

Risks: Coverage is intentionally small: it covers put/delete only, one timestamp comparator, and parse errors for short keys and null comparator. It does not exercise `GetInternalKeyForSeek`, `GetInternalKeyForSeekForPrev`, malformed timestamp lengths, merge/range-delete/value-entity internal types, or caller misuse of output lifetimes.

Test signals: The main signals are exact `Status::InvalidArgument` for invalid inputs and exact parsed `user_key`, `timestamp`, `sequence`, and public `EntryType` for timestamped and non-timestamped entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/types_util_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/util_merge_operators_test.cc -->
# sources/storage-engines/rocksdb/utilities/util_merge_operators_test.cc

Purpose: This compact test verifies the utility max merge operator returned by `MergeOperators::CreateMaxOperator`. It checks full-merge, partial-merge, and multi-operand partial-merge behavior using lexicographic string maximum semantics.

Important APIs and types: The fixture stores a `std::shared_ptr<MergeOperator>` and wraps `FullMergeV2`, `PartialMerge`, and `PartialMergeMulti`. It constructs `MergeOperator::MergeOperationInput`, `MergeOperator::MergeOperationOutput`, `Slice` vectors/deques, and calls `MergeOperators::CreateMaxOperator`.

Control flow: The helper overloads convert `std::string` operands into `Slice` containers, call the merge operator, and return either the output string or `result_operand` if the operator filled that slice. The single test installs the max operator, checks full merges against existing values and operand-only inputs, then checks `PartialMergeMulti` and pairwise `PartialMerge`.

State and persistence behavior: There is no persistent state. The only mutable state is the fixture's `merge_operator_` pointer and stack-local merge output buffers.

Dependencies and integration points: This test covers the reusable merge operator factory in `utilities/merge_operators.h`. The operator can be configured into DB options or utility wrappers, so this suite guards the simple string ordering contract that callers may rely on.

Risks: The helpers do not assert the boolean return value from `FullMergeV2`, `PartialMerge`, or `PartialMergeMulti`; a future operator failure that still leaves an expected-looking buffer could be missed. The test is string-only, bytewise/lexicographic, and does not cover null existing values beyond the operand-only full merge path. It does not exercise object-registry loading of the operator.

Test signals: Expected outputs include keeping `"B"` over `"A"`, selecting `"Z"` or `"ZZZ"` among operands, preserving existing `"a"` when it is lexicographically greater than uppercase operands, and partial merges returning the maximum operand for pair and deque inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/util_merge_operators_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/wal_filter.cc -->
# sources/storage-engines/rocksdb/utilities/wal_filter.cc

Purpose: This file provides the string-based factory hook for `WalFilter`. It lets configuration code instantiate registered WAL filter implementations from a `ConfigOptions` registry and textual value.

Important APIs and types: The only implemented function is `WalFilter::CreateFromString(const ConfigOptions&, const std::string&, WalFilter**)`. It delegates to `LoadStaticObject<WalFilter>` from `rocksdb/utilities/customizable_util.h`. Included public types are `rocksdb/wal_filter.h`, `rocksdb/convenience.h`, and `rocksdb/options.h`.

Control flow: `CreateFromString` receives configuration options, a string value identifying a filter, and an output pointer. It calls `LoadStaticObject<WalFilter>` and returns that status unchanged. Object lookup, ownership rules, and error construction are handled by the customizable utility layer.

State and persistence behavior: There is no local state and no persistence. Any state involved belongs to the object registry embedded in `ConfigOptions` or to static factories registered elsewhere.

Dependencies and integration points: This is an integration shim between WAL replay/filtering APIs and RocksDB's configurable-object infrastructure. It enables options parsing, config files, and object registry users to resolve WAL filters the same way other customizable components are resolved.

Risks: Correctness depends almost entirely on `LoadStaticObject` and registry setup. The function does not validate that `filter` is non-null or clear it on failure; callers must follow the expected factory contract. There are no local semantics beyond delegation, so tests must live in registry/configuration coverage rather than algorithmic unit tests here.

Test signals: No direct tests are in this subset. Useful signals would be successful creation of a registered `WalFilter`, failure for an unknown ID, and stable behavior around static-object ownership.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/wal_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index.cc -->
# sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index.cc

Purpose: This file implements the public `WriteBatchWithIndex` utility. It wraps a `WriteBatch` with an in-memory skip-list index so callers can query pending batch updates, iterate them by key, overlay them on a DB iterator, perform batch-and-DB reads, and support wide-column entity reads before committing.

Important APIs and types: The central type is `WriteBatchWithIndex::Rep`, which owns `ReadableWriteBatch`, `WriteBatchEntryComparator`, an `Arena`, a `WriteBatchEntrySkipList`, overwrite-key bookkeeping, per-column-family stats, and operation count. Public methods include constructors/move operations, `GetWriteBatch`, `SubBatchCnt`, `NewIterator`, `NewIteratorWithBase`, `Put`, `PutEntity`, `Delete`, `SingleDelete`, `Merge`, `PutLogData`, `Clear`, `GetFromBatch`, `GetEntityFromBatch`, `GetFromBatchAndDB`, `MultiGetFromBatchAndDB`, `GetEntityFromBatchAndDB`, `MultiGetEntityFromBatchAndDB`, savepoint methods, `SetMaxBytes`, `GetDataSize`, `GetCFStats`, `GetWBWIOpCount`, and `GetOverwriteKey`.

Control flow: Mutating APIs record the current write-batch data offset, append the operation to the underlying `WriteBatch`, and, on success, add or update an index entry for the affected key. `Rep::AddNewEntry` decodes the key at the stored batch offset, strips user timestamp suffixes when the comparator has timestamps, allocates a `WriteBatchIndexEntry` in the arena, and inserts it into the skip list. In overwrite-key mode, `UpdateExistingEntryWithCfId` finds the latest indexed entry for a key and updates its offset for non-merge operations, while preserving sub-batch and overwritten single-delete metadata; merge operations keep separate index entries.

State and persistence behavior: The underlying write batch is an in-memory serialized batch buffer. The skip-list index stores offsets and key slices into that buffer, so `Clear`, rollback, and imported batch changes must rebuild or reset the index. `RollbackToSavePoint` delegates rollback to `WriteBatch`, resets sub-batch counters, and calls `ReBuildIndex`, which reparses every serialized record and verifies the write-batch count. Per-CF stats track indexed entry count and overwritten single-delete count for later ingestion into WBWI memtables. No data reaches persistent DB state until the underlying batch is written elsewhere.

Dependencies and integration points: The implementation depends on internal DB APIs (`DBImpl::GetImpl`, `PrepareMultiGetKeys`, `MultiGetWithCallback`, `MultiGetEntityWithCallback`), column-family helpers, `MergeContext`, `MergeHelper`, wide-column helpers, `Arena`, and the internal WBWI iterator/comparator classes. It is a transaction/read-your-own-writes utility and integrates with timestamp-aware comparators, read callbacks, lower/upper bounds for iterators, and wide-column entity APIs.

Risks: The index is tightly coupled to serialized write-batch offsets; corruption or unsupported tags during rebuild return corruption. Timestamped column families require a read timestamp for DB fallbacks, and entity APIs validate timestamp size strictly. `Put/Delete/SingleDelete` overloads with explicit timestamps are not supported. Merge resolution requires the column family's immutable options to have a merge operator. Overwrite-key mode has nuanced single-delete and merge restrictions. Batch values are copied into pinnable outputs because transaction lifetime cannot safely pin write-batch memory.

Test signals: Direct tests are not in this subset, but expected signals include batch-only reads returning put/entity values, deletes mapping to `NotFound`, unresolved merges mapping to `MergeInProgress`, batch-and-DB reads merging operands with DB values, multi-get preserving per-key statuses, iterator-with-base overlay hiding deleted base keys, savepoint rollback rebuilding the index, and CF stats matching inserted/overwritten entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_internal.cc -->
# sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_internal.cc

Purpose: This file implements the internal mechanics behind `WriteBatchWithIndex`: overlay iteration between a base DB iterator and batch delta iterator, parsing serialized write-batch records, ordering index entries, finding the latest update for a key, and resolving batch-local merge chains for plain and wide-column values.

Important APIs and types: Implemented classes and functions include `BaseDeltaIterator`, `WBWIIteratorImpl::AdvanceKey`, `NextKey`, `PrevKey`, `FindLatestUpdate`, `ReadableWriteBatch::GetEntryFromDataOffset`, `WriteBatchEntryComparator::operator()`, `CompareKey`, `GetComparator`, `WBWIIteratorImpl::Entry`, `MatchesKey`, `WriteBatchWithIndexInternal::CheckAndGetImmutableOptions`, `GetFromBatch`, `GetEntityFromBatch`, and the templated `GetFromBatchImpl`. It uses `ReadRecordFromWriteBatch`, `MergeContext`, `MergeHelper::TimedFullMerge`, `WideColumnSerialization`, and `WideColumnsHelper`.

Control flow: `BaseDeltaIterator` positions a base iterator and a WBWI delta iterator together for forward or reverse scans. `UpdateCurrent` asks the delta iterator for the latest visible update for its current key, compares delta and base keys without timestamps, skips deleted delta keys, chooses the current source, and prepares value/columns unless unprepared values are allowed. When delta merges are present, `SetValueAndColumnsFromDelta` resolves them against a delta put/entity, a base value/entity when keys are equal, or no base value. Direction changes in `Next` and `Prev` reposition the non-current iterator so the overlay can continue without returning duplicate keys.

State and persistence behavior: This file manipulates only in-memory iterator state and slices into the serialized write-batch buffer. `BaseDeltaIterator` owns the base iterator and delta iterator, stores merge context/results, and caches the current value or wide columns. `ReadableWriteBatch::GetEntryFromDataOffset` decodes an entry at a byte offset but does not mutate the batch. `GetFromBatchImpl` clears outputs on not-found/error paths and accumulates merge operands in caller-provided `MergeContext`.

Dependencies and integration points: The code is deeply integrated with RocksDB internals: internal write-batch tags, DB merge helpers, immutable column-family options, user comparators, timestamp stripping, wide-column serialization, and DB iterators. `WriteBatchWithIndex` public methods delegate here for batch-only lookups and base+delta iteration.

Risks: Unsupported or unexpected write-batch tags become corruption or `kError`, and `WBWIIteratorImpl::Entry` asserts that only indexed record types are returned. Merge resolution fails if no merge operator is configured for the column family. Slices returned from decoded entries depend on write-batch memory stability. Reverse iteration and direction switching are subtle, especially around duplicate keys and equal base/delta keys. Bounds checks compare keys without timestamps and assume stored index keys were stripped consistently. Wide-column merge results must deserialize successfully or the iterator/read returns an error.

Test signals: Useful coverage comes from WBWI iterator and transaction tests outside this subset: scanning forward/backward across base and batch, deletes suppressing base keys, merges resolving with base and no-base values, wide-column entities preserving default and non-default columns, `allow_unprepared_value` delaying base value preparation, lower/upper bounds, corrupted or unsupported batch tags, and missing merge-operator errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_internal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_internal.h -->
# sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_internal.h

Purpose: This header declares the private data structures that make `WriteBatchWithIndex` searchable and composable with DB iterators. It defines the batch-entry index format, skip-list comparator, readable write-batch helper, delta iterator, base/delta overlay iterator, and internal merge/read helpers.

Important APIs and types: Key declarations are `BaseDeltaIterator`, `WriteBatchIndexEntry`, `ReadableWriteBatch`, `WriteBatchEntryComparator`, `WriteBatchEntrySkipList`, `WBWIIteratorImpl`, and `WriteBatchWithIndexInternal`. `WBWIIteratorImpl::Result` distinguishes `kFound`, `kDeleted`, `kNotFound`, `kMergeInProgress`, and `kError`. `WriteBatchWithIndexInternal` exposes `GetUserComparator`, `MergeKeyWithNoBaseValue`, `MergeKeyWithBaseValue`, `GetFromBatch`, and `GetEntityFromBatch`.

Control flow: `WBWIIteratorImpl` wraps a skip-list iterator and provides seek, seek-for-prev, first/last, next/prev, and key-level movement over indexed write-batch entries for one column family. `FindLatestUpdate` normalizes the iterator to the most recent entry for a key, accumulates merge operands, and classifies the latest visible state. `BaseDeltaIterator` uses a base DB iterator and a `WBWIIteratorImpl` to expose a merged view of committed data plus batch updates. `WriteBatchWithIndexInternal` provides the shared lookup path used by plain-value and wide-column reads.

State and persistence behavior: `WriteBatchIndexEntry` stores a write-batch byte offset, column-family ID, update counters, single-delete flags, key offset/size into the write-batch data buffer, or a dummy search key for lookup. `kFlagMinInCf` encodes seek-to-first within a column family. The index does not own key bytes; real entries point into the write batch, while dummy entries point to caller-owned search slices used only during comparisons. The header itself defines no persistent format, but its layout is coupled to the in-memory skip-list and serialized write-batch record offsets.

Dependencies and integration points: The header includes DB internal formatting, merge context/helper, skip list, immutable options, comparators, iterators, status, slices, and the public `write_batch_with_index.h`. It is not a public API boundary despite living under utilities; it is used by the public implementation file and internal tests.

Risks: Correct ordering depends on `WriteBatchEntryComparator` comparing column family, user key without timestamp, and descending write-batch offset. Any mismatch between key stripping at insertion and comparison can break timestamped column families. Dummy search entries rely on special offset values to include all duplicate-key updates during seek. The classes assume the underlying write batch and comparator objects outlive iterators. Merge helpers require valid `ColumnFamilyHandle` immutable options and a configured merge operator.

Test signals: Expected tests should verify duplicate-key ordering, seek/seek-for-prev inclusion of all updates for the same key, lower/upper-bound handling, overwrite-key update counts and single-delete flags, column-family-specific comparators, timestamp-stripped keys, base/delta iteration in both directions, and batch lookup result classification for put, entity, delete, single-delete, merge-only, and unsupported records.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_internal.h -->
