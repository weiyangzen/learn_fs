# subset-b-008627 Research

Grouped research report for subset-b-008627. Each section is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/db_wide_basic_test.cc -->

# sources/storage-engines/rocksdb/db/wide/db_wide_basic_test.cc

Purpose: This is the broad integration test suite for RocksDB wide-column entities. It validates `PutEntity`, `GetEntity`, `MultiGetEntity`, iterator `columns()`, merge, compaction filter, read-only reopen, blob-backed wide columns, and error handling across memtable, WAL recovery, SST, compaction, universal compaction, and block-cache-only read tiers.

Important APIs/types/functions: `DBWideBasicTest` extends `DBTestBase` and centralizes option helpers for blob and direct-write modes. The file exercises public APIs `DB::PutEntity`, `WriteBatch::PutEntity`, `DB::GetEntity`, `DB::MultiGetEntity`, `DB::Get`, `DB::MultiGet`, `DB::GetMergeOperands`, `Iterator::columns`, `Iterator::value`, `Iterator::Seek/Next/Prev/SeekForPrev`, `Flush`, `CompactRange`, `ReadOnlyReopen`, and column-family attribute-group forms. Helper methods `RunEntityBlobAfterFlush`, `RunEntityBlobAfterCompaction`, and `RunCompactionFilterWithBlobGC` share larger blob scenarios. `DBWideMergeV3Test` defines custom `MergeOperator::FullMergeV3` implementations returning either wide-column entities or plain values. `TTLCompactionFilter` implements `CompactionFilter::FilterV4` over wide-column inputs.

Control flow: Early tests establish the core contract: an entity with a default column behaves like a plain value for `Get`, an entity without a default column returns an empty default value, and a plain key/value appears as a single default wide column through entity APIs. The suite then repeats these checks for column families, attribute groups, multi-key/multi-CF reads, iterators, recovery, readonly open, and flushed storage. Merge tests cover plain bases, entity bases with and without default columns, V3 merge operators, snapshots preventing flush-time collapse, and compaction-time merge collapse. Compaction-filter tests run keep, remove, change-value, and change-wide-entity filters through the `FilterV4` wide-column interface. The blob half writes large columns, flushes or compacts to create V2 blob-backed entities, and verifies point reads, batched reads, forward and reverse iteration, merge operands, read-only reopen, block-cache-tier failures, and blob garbage collection.

State and persistence behavior: The tests intentionally move records across memtable, immutable memtable, WAL recovery, SST, compaction output, and read-only DB instances. Blob scenarios verify that large column values move to blob files when blob options or direct write are enabled, while small columns remain inline. The blob GC helper writes 100 records over 10 flushes, filters records by TTL during repeated compactions, and expects blob file metadata to shrink to zero once all referencing wide-column entities are removed. Direct-write memtable tests check that blob-backed V2 entities can exist before flush and still resolve through `Get`, `GetEntity`, `MultiGet`, merge, and read-only recovery paths.

Dependencies: The file depends on `db/db_test_util.h` for test harness operations, `wide_column_test_util.h` for blob/direct-write option presets and value generators, `utilities/merge_operators.h` for string append merge operators, `test_util/testutil.h`, `port/stack_trace.h`, and `util/overload.h` for local merge visitor helpers. It also relies on RocksDB value-type plumbing (`kDefaultWideColumnName`, `PinnableWideColumns`, `AttributeGroups`, `WideColumnBlobResolver`) through included DB headers.

Integration points: This suite is the high-level guard for the wide-column read and write path. It covers DBImpl write paths, write batches, memtable lookup, multi-get batching, DBIter value/column exposure, merge helper resolution, compaction iterator/filter V4 integration, blob file creation, blob fetch resolution, blob GC accounting, block-cache-tier read semantics, and read-only recovery behavior. The tests implicitly validate `WideColumnSerialization`, `ReadPathBlobResolver`, `CompactionBlobResolver`, and `BlobFetcher` because user-visible reads must reconstruct the original `WideColumns`.

Risks and edge cases: The tests document several compatibility risks: user timestamp comparators reject `PutEntity`; duplicate/out-of-order columns become serialization corruption; null column-family handles and invalid `io_activity` settings must return `InvalidArgument`; block-cache-only reads must return `Incomplete` rather than `Corruption`; blob-backed merge bases must resolve before merge operators see them; read-only and memtable direct-write paths need a valid blob fetcher even without mutable write state; and compaction filters must not accidentally read large blob payloads when only inline TTL columns are needed. Iterator tests also guard against exposing a valid entry before blob-backed columns have been resolved.

Test signals: The file itself is a large positive test signal. It checks memtable, flush, compaction, universal compaction, readonly reopen, forward/reverse iteration, `MultiGetEntity`, `MultiGet`, `GetMergeOperands`, block-cache tier, blob statistics, blob file metadata, and garbage collection. It includes both success-path assertions and negative-path assertions for invalid arguments, unsupported timestamps, duplicate columns, and cache-tier incomplete reads.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/db_wide_basic_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/db_wide_blob_direct_write_test.cc -->

# sources/storage-engines/rocksdb/db/wide/db_wide_blob_direct_write_test.cc

Purpose: This test suite focuses on blob direct write for wide-column entities. It verifies that large wide-column values can be written directly to blob files before flush, represented as V2 wide-column entities with blob indexes, and resolved correctly through reads, iterators, snapshots, compaction filters, partitioning, and metadata accounting.

Important APIs/types/functions: `DBWideBlobDirectWriteTest` extends `DBTestBase` and adds helpers for blob-file counting, generated stress keys, dynamic wide-column backing storage, iterator population, and coalescing iterator validation. `ToWideColumns` converts owning string pairs into `WideColumns` slices for tests. Local compaction-filter classes include `TTLOnlyLazyDropFilter`, `ResolvingWideValueFilter`, and `BlobResolvingErrorIgnoringFilter`, with flush-only factories. `NameBasedWideColumnPartitionStrategy` implements the wide-column overload of `BlobFilePartitionStrategy::SelectPartition` and records whether value or wide-column overloads were called.

Control flow: The suite starts by rejecting empty attribute groups and serialized entities that already contain blob references when direct write is enabled. It then writes wide entities with large columns, verifies them before and after memtable switch, flush, reopen, and blob partition manager metadata publication. Auto-flush and partition-strategy tests confirm blob generation ordering and that wide-column partition selection is used. Coalescing iterator tests compare `NewCoalescingIterator` against direct iterators across auto-refresh, trie index reads, reuse-before-refresh, and multi-CF merges. Flush-time filter tests cover lazy TTL removal without resolving blob payloads, resolving blob values on demand, propagation of missing-blob errors, overwrite elision marking old blobs garbage, and all-expired flushes not leaking blob generations. Snapshot tests compare `MultiGetEntity` with point `GetEntity` for memtable/SST, trie/plain index, duplicate/unique keys, and snapshot visibility.

State and persistence behavior: Direct-write mode stores qualifying column values in blob files before the containing wide entity is flushed to an SST. The entity in the memtable can therefore reference blob records that must remain live through memtable switch, flush, WAL recovery, read-only reopen, and compaction. Tests inspect `BlobFileAddition`, `BlobFileGarbage`, `ColumnFamilyMetaData`, `LiveFileMetaData`, and `BlobMetaData` to confirm total and garbage blob counts/bytes. Partitioned workloads verify active blob-file reuse, generation ordering, and dropping expired-only blob files during compaction without reading blob bytes. Snapshot cases ensure older entity versions remain readable after newer direct-write updates are added and flushed.

Dependencies: The file includes blob internals (`blob_file_partition_manager.h`, `blob_index.h`, `blob_log_format.h`), column-family internals, `WriteBatchInternal`, `wide_column_serialization.h`, wide-column test utilities, fixed-length coding helpers, and the trie index factory. It relies on `DBTestBase` hooks such as `TEST_SwitchMemtable`, `TEST_WaitForFlushMemTable`, `PrepareFlushAdditions`, `GetBlobFileNumbers`, `MoveFilesToLevel`, `GetLiveFilesMetaData`, and environment file deletion to create controlled missing-blob failures.

Integration points: The tests connect direct-write wide entities to DB write APIs, write batches, blob partition management, table-file creation filters, compaction filters with `WideColumnBlobResolver`, coalescing iterators, trie-index reads, snapshots, `MultiGetEntity`, iterator `PrepareValue`, blob file metadata, and DB background error latching. They are especially important for integration between memtable-resident V2 entities and read/compaction paths that historically expected blob references only after flush or compaction.

Risks and edge cases: The suite highlights risks around accepting already-serialized blob references from users, losing blob generation order during auto-flush, using the wrong partition strategy overload, leaking blob files when all direct-write records are filtered out, not marking overwritten blobs as garbage, swallowing filter resolver errors, exposing valid iterators before blob resolution succeeds, reading blob payloads unnecessarily in TTL-only filters, and snapshot `MultiGetEntity` diverging from point reads under trie index or duplicate keys. Missing blob files must surface as hard flush/background errors or iterator invalidation, not silent data preservation.

Test signals: Strong coverage exists for direct write before and after flush, auto-flush generation metadata, custom partition strategies, single-CF and multi-CF coalescing iterators, flush-time lazy compaction filters, resolver success and failure paths, overwrite elision garbage accounting, all-expired generation cleanup, snapshot reads, eager iterator blob resolution, iterator invalidation on missing blobs, and large partitioned TTL compaction with zero blob payload reads.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/db_wide_blob_direct_write_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.cc -->

# sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.cc

Purpose: Implements `ReadPathBlobResolver`, the read-side helper that lazily resolves blob-backed wide-column values in V2 entities. It lets point lookups and iterators expose a `WideColumns`-like entity while fetching only blob columns that callers actually request, with a small per-entity cache.

Important APIs/types/functions: `BuildReadPathBlobResolverReadOptions` maps resolver constructor inputs into `ReadOptions` for `BlobFetcher`. The constructor initializes `blob_fetcher_` with `Version`, read tier, checksum verification, cache-fill behavior, IO activity, optional blob-file cache, and write-path fallback permission. `Reset` installs the current user key plus pointers to parsed columns and `(column_index, BlobIndex)` metadata. `ResolveColumn`, `ResolveColumns`, `ResolveAllColumns`, `IsUnresolvedColumn`, `HasUnresolvedColumns`, and `NumColumns` implement the resolver interface.

Control flow: `ResolveColumn` validates bounds, asks `blob_resolver_util::FindBlobColumn` whether the requested index is a blob reference, and either returns the inline `WideColumn::value()` or consults `resolved_cache_`. Inlined blob indexes are cached through `CacheInlinedBlob`; external blob indexes allocate a `PinnableSlice`, call `BlobFetcher::FetchBlob`, and remove the cache entry if fetching fails. `ResolveColumns` repeatedly calls `ResolveColumn` and clears partial output on the first error. `ResolveAllColumns` iterates only blob-column metadata and lets `ResolveColumn` skip already cached columns. The query helpers detect unresolved blob indexes by comparing `blob_columns_` with the cache.

State and persistence behavior: The resolver does not persist data. It holds non-owning pointers to the current entity's parsed columns and blob metadata until the next `Reset`, plus a cache of resolved blob values whose `PinnableSlice` storage remains address-stable through `unique_ptr`. The `Cleanable` member lets callers pin resources such as a `SuperVersion` or version lifetime for as long as the resolver might fetch blobs. Persistence effects are indirect: external blob payloads are read from blob files through `BlobFetcher`, respecting read tier and checksum options.

Dependencies: The implementation depends on `Version`, `BlobFetcher`, `BlobIndex`, `PinnableSlice`, `FilePrefetchBuffer`, and shared helpers in `db/wide/blob_column_resolver_util.h` for blob-column lookup and cache lookup. It also depends on `ReadOptions` fields and `Env::IOActivity` to make blob reads honor the caller's read policy.

Integration points: Used by DB iterator and point-lookup paths that parse V2 wide-column entities but need lazy resolution for `PinnableWideColumns` or iterator column access. It mirrors compaction-side blob resolution but uses the read-path backend (`BlobFetcher` over `Version`) rather than compaction iterator machinery. It directly supports block-cache-tier behavior because `BlobFetcher::FetchBlob` can return `Incomplete` when blob data is not available without IO.

Risks and edge cases: Callers must keep `columns`, `blob_columns`, `user_key`, `Version`, and any pinned resources alive while the resolver is used. A failed external fetch pops the just-created cache entry; callers must not retain slices from failed calls. `IsUnresolvedColumn` returns false for out-of-range indexes, so callers that need strict validation must use `ResolveColumn`. Linear cache scans are intentional for small blob counts but could become expensive if entities gain many blob-backed columns.

Test signals: This file is indirectly covered by wide-column blob tests in `db_wide_basic_test.cc` and direct-write tests in `db_wide_blob_direct_write_test.cc`, which verify `GetEntity`, iterators, `MultiGetEntity`, read-only reopen, block-cache-tier incomplete status, and merge/default-column resolution over blob-backed V2 entities.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.h -->

# sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.h

Purpose: Declares `ReadPathBlobResolver`, the public internal class for read-path lazy blob resolution of wide-column entities. The header defines the ownership/lifetime contract and the resolver operations used by DBIter and point lookup code.

Important APIs/types/functions: The constructor accepts `Version*`, `ReadTier`, checksum and cache flags, `Env::IOActivity`, optional `BlobFileCache`, and `allow_write_path_fallback`. `Reset` binds the resolver to a user key plus parsed `std::vector<WideColumn>` and blob-column metadata. `ResolveColumn`, `ResolveColumns`, and `ResolveAllColumns` fetch or expose column values. `IsUnresolvedColumn`, `HasUnresolvedColumns`, and `NumColumns` query resolver state. `RegisterCleanup` forwards cleanup registration to the embedded `Cleanable`.

Control flow contract: Callers reset the resolver for each entity after V2 deserialization, then either resolve selected columns lazily or force all blob columns to be fetched. Inline columns are returned without IO; blob columns may fetch from blob files and cache the result. The header makes clear that `ResolveColumn` can fail for out-of-bounds indexes or blob IO errors.

State and persistence behavior: The class owns a `BlobFetcher`, current key slice, non-owning pointers to columns and blob metadata, a vector cache of resolved blob values, and a `Cleanable` for lifetime pinning. It persists no state itself, but it depends on blob files remaining available and on caller-pinned version resources. `Reset` clears the cache so blob values from one entity cannot leak into another.

Dependencies: The header includes blob fetch/index types, RocksDB `Cleanable`, `Options`/`ReadTier`, `Slice`, `Status`, and `wide_columns.h`. It forward-declares `Version` and exposes `BlobFileCache` through the constructor.

Integration points: The documented users are iterator (`DBIter`) and point-lookup (`GetEntity` via `PinnableWideColumns`) paths. The TODO notes duplication with `CompactionBlobResolver`, indicating a shared logical contract across read and compaction paths but different blob-fetching backends and stats contexts.

Risks and edge cases: The class is explicitly not thread-safe. `Version*`, `columns`, and `blob_columns` must outlive the resolver or next reset. Because resolved slices can point into internal cache storage, callers must respect resolver lifetime. `RegisterCleanup` is critical for SuperVersion pinning; missing cleanup registration can cause use-after-free of version/blob metadata.

Test signals: Coverage is indirect through read-path tests for blob-backed wide columns, block-cache-tier incomplete handling, read-only reopen, direct-write memtable reads, iterator eager resolution, and multi-get entity behavior.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_serialization.cc -->

# sources/storage-engines/rocksdb/db/wide/wide_column_serialization.cc

Purpose: Implements the wide-column entity wire format. Version 1 serializes sorted columns with inline values. Version 2 adds per-column value types and blob-index references so large column values can live in blob files while the entity remains a single RocksDB value.

Important APIs/types/functions: Serialization entry points are `Serialize`, `SerializeV2` for string pairs, and `SerializeV2` for `WideColumns`. Deserialization and inspection entry points are `Deserialize`, `DeserializeV2`, `HasBlobColumns`, `ForEachBlobFileNumber`, `GetValueOfDefaultColumn`, `GetValueOfDefaultColumnResolvingBlobs`, `ResolveEntityBlobColumns`, and `ResolveEntityForMerge`. Internal helpers include `BuildBlobIndexMap`, `ContainsBlobType`, `DeserializeV1`, `DeserializeV2Impl`, `GetVersion`, `SerializeResolvedEntity`, and templated `SerializeV2Impl`.

Control flow: V1 serialization validates the column count, strict sorted name order, name sizes, and value sizes, then writes version, count, length-prefixed names with value sizes, and a contiguous value payload. V2 serialization first builds a per-column blob-index map, validates name order and sizes, serializes blob indexes for blob-backed columns, computes section sizes, and writes header, skip info, column type bytes, name sizes, value sizes, names, and values into a pre-sized output string. V1 deserialization parses name/value-size metadata first and then assigns value slices. V2 deserialization parses skip info, validates type bytes, bounds-checks section sizes, walks name-size/value-size/name/value sections in one pass, validates strict name ordering, and decodes blob indexes for `kTypeBlobIndex` columns.

State and persistence behavior: This file defines the durable byte layout for wide-column entities. V1 output is fully inline. V2 output can contain inline values and serialized `BlobIndex` payloads. Deserialized `WideColumn` values are slices into the input buffer; callers must keep the input alive or copy as needed. Blob resolution helpers fetch blob values, build a resolved inline column set, and reserialize it as V1 so older consumers and merge operators can operate on all-inline entity bytes.

Dependencies: The implementation uses `BlobIndex`, `BlobFetcher`, `PrefetchBufferCollection`, `WideColumnsHelper`, `PinnableSlice`, `autovector`, and `util/coding` varint/fixed helpers. It depends on `ValueType` constants such as `kTypeValue`, `kTypeBlobIndex`, and `kTypeWideColumnEntity` from `dbformat.h`. Blob resolution uses `FilePrefetchBuffer` per blob file and updates optional byte/read counters.

Integration points: Write paths call V1 or V2 serialization depending on whether any columns are blob-backed. Read paths use `Deserialize`, `DeserializeV2`, default-column fast paths, and blob-detection helpers. Blob GC and manifest logic can use `ForEachBlobFileNumber` to inspect blob references without full deserialization. Merge paths call `ResolveEntityForMerge` to ensure `TimedFullMerge` sees a V1 all-inline entity when a V2 base contains blob references. Point lookup default-column reads use `GetValueOfDefaultColumnResolvingBlobs` when the default column itself is blob-backed.

Risks and edge cases: Format compatibility is the central risk. Column names must be strictly sorted and unique; otherwise serialization or deserialization reports corruption. Size accounting must stay within `uint32_t`, and V2 section-size arithmetic must reject truncated or inconsistent inputs. `Deserialize` deliberately rejects V2 entities with blob references and directs callers to `DeserializeV2`; using the wrong API can produce `NotSupported`. `GetValueOfDefaultColumn` has a V2 fast path but refuses blob-backed default columns unless the resolving variant is used. `ResolveEntityForMerge` requires a blob fetcher when blob columns exist, otherwise it returns corruption.

Test signals: The serializer is exercised by `PutEntitySerializationError` for duplicate columns, all standard `PutEntity`/`GetEntity` round trips, V2 blob-resolution tests in `db_wide_basic_test.cc`, direct-write rejection of preexisting blob references in `db_wide_blob_direct_write_test.cc`, merge-on-blob-backed-entity tests, default-column blob tests, blob-file metadata/GC paths, and block-cache-tier incomplete behavior.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_serialization.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_serialization.h -->

# sources/storage-engines/rocksdb/db/wide/wide_column_serialization.h

Purpose: Declares `WideColumnSerialization`, the internal static utility that owns RocksDB's wide-column entity serialization contract. The header documents V1 and V2 layouts and exposes APIs for writing, reading, blob-reference inspection, default-column extraction, and blob resolution.

Important APIs/types/functions: Constants `kVersion1` and `kVersion2` identify the supported formats. Public methods include `Serialize`, `SerializeV2`, `Deserialize`, `DeserializeV2`, `HasBlobColumns`, `ForEachBlobFileNumber`, `GetValueOfDefaultColumn`, `ResolveEntityBlobColumns`, `GetValueOfDefaultColumnResolvingBlobs`, and `ResolveEntityForMerge`. Private helpers cover version parsing, resolved-entity serialization, `uint32_t` size validation, strict column-order validation, templated V2 serialization, blob-index map construction, V1/V2 parsing, supported `ValueType` validation, and blob-type scanning.

Control flow contract: Producers serialize sorted `WideColumns`; if any columns are stored externally, they call V2 serialization with a list of `(column_index, BlobIndex)` entries. Consumers can use `Deserialize` for all-inline entities, `DeserializeV2` when blob references are possible, `HasBlobColumns` for a cheap type-byte check, and `ForEachBlobFileNumber` for lightweight blob-file discovery. Merge/read compatibility helpers resolve blob references and produce an effective all-inline V1 entity when required.

State and persistence behavior: The header is the durable format specification. V1 stores version, column count, column names and value sizes, then values. V2 stores version/count, skip-info byte lengths, per-column type bytes, name-size varints, value-size varints, names, and values or blob-index encodings. The skip-info design allows default-column and type checks without scanning every variable-length name/value field. No runtime state is owned by the class.

Dependencies: The declaration depends on `db/dbformat.h` for `ValueType`, RocksDB `Status`, `Slice`, `WideColumns`, blob-related forward declarations, `PrefetchBufferCollection`, `PinnableSlice`, standard `function`, `limits`, and vectors of blob-index metadata.

Integration points: The API is used by DB write paths, write batches, memtables/SST values, read paths, merge paths, compaction/blob GC, and tests. It bridges wide-column semantics to blob storage by treating serialized `BlobIndex` values as per-column payloads in V2. The resolving APIs are compatibility shims for consumers that still require V1 all-inline entity bytes.

Risks and edge cases: Because this header defines on-disk bytes, any layout change must preserve backward compatibility. `kTypeWideColumnEntity` is intentionally rejected as a per-column type to avoid recursive entities. Callers must choose resolving APIs whenever blob-backed default columns or merge bases are possible. Deserialized slices reference the input buffer, so lifetime management belongs to callers.

Test signals: The contract is covered by the wide-column basic and direct-write suites in this subset: duplicate-column errors, V1 round trips, V2 blob references, default-column extraction, merge resolution, blob-file-number accounting, direct-write serialized-blob rejection, cache-tier incomplete reads, and read-only recovery of blob-backed entities.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_serialization.h -->
