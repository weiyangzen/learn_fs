# Research: subset-b-008568

Grouped research for RocksDB blob source, direct-write batch transformation, and DB blob behavior tests. Each section is wrapped for reconciliation into its source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_source_test.cc

## Purpose

This file is a focused unit test suite for `BlobSource`, the read-side component that opens blob files, reads blob records, decodes/decompresses values, interacts with the blob value cache, and exposes single-blob and multi-blob read helpers below the public `DB` API. It uses synthetic blob files written directly through `BlobLogWriter` so the tests can control offsets, sizes, compression, file numbers, and cache state without relying on full DB write paths.

The suite covers primary blob cache behavior, cache-only read tiers, compressed blobs, reads spanning multiple blob files, secondary cache promotion/demotion, error detail preservation after file refresh failures, and charged cache reservation accounting.

## Important APIs, Types, and Functions

- `WriteBlobFile(...)`: anonymous helper that creates a `.blob` file with a header, records, and footer. It optionally compresses each blob with the built-in compression manager, records blob offsets and compressed sizes, and is the fixture's persistence primitive.
- `BlobSourceTest`: `DBTestBase` fixture configuring `enable_blob_files`, a real LRU blob cache, `lowest_used_cache_tier = kVolatileTier`, DB identity/session IDs, and a separate `BlobFileCache`.
- `BlobSource::GetBlob`, `MultiGetBlob`, `MultiGetBlobFromOneFile`, `GetBlobFileReader`, and `TEST_BlobInCache`: core APIs under test.
- `BlobSecondaryCacheTest`: fixture with a small primary cache, compressed secondary cache, and `lowest_used_cache_tier = kNonVolatileBlockTier`.
- `BlobSourceCacheReservationTest`: fixture that wraps blob cache charging through `ChargedCache` and validates `ConcurrentCacheReservationManager` state.
- `OffsetableCacheKey`, `CacheKey`, `BlobContents`, `CacheHandleGuard<BlobFileReader>`, `PinnableSlice`, `BlobReadRequest`, and `BlobFileReadRequests` are the important data carriers.

## Control Flow

Most tests follow the same flow: configure options and cache, reopen the DB to obtain immutable/mutable CF options, write one or more blob files with known keys and values, create a `BlobFileCache`, construct `BlobSource`, and perform read sequences under different `ReadOptions`.

`GetBlobsFromCache` first reads with `fill_cache=false` and confirms no blob values are cached; then reads with `fill_cache=true` and verifies values are cached and pinned; then switches to `kBlockCacheTier` to prove cache-only reads succeed only while entries are resident. After erasing unreferenced entries, cache-only reads return `Incomplete`. A final missing-file path returns `IOError`.

`GetCompressedBlobs` writes Snappy-compressed records, confirms file reader compression metadata and compressed sizes, reads/decompresses from file while filling cache, then verifies later cache-only reads return uncompressed values without extra decompression time.

`MultiGetBlobsFromMultiFiles` and `MultiGetBlobsFromCache` build grouped read requests by file number, exercise batch reads, add a fake file request, and check per-request statuses rather than treating the batch as all-or-nothing.

The secondary cache test intentionally alternates two large blobs through an undersized primary cache, then inspects raw primary and secondary cache entries to validate dummy handles, promotion, and blob content materialization. The reservation tests read blobs with and without fill-cache, then assert reserved dummy-entry size and memory usage grow and shrink as cache entries are inserted and erased.

## State and Persistence Behavior

Persistent state is created as actual blob files in per-test CF paths. The helper writes valid blob log headers, records, and footers, so `BlobSource` observes normal on-disk metadata. Blob offsets and sizes are captured from the writer and reused as exact lookup coordinates.

Transient state includes primary blob cache entries keyed by DB identity, DB session, blob file number, and offset; secondary cache entries; blob file reader cache handles; `PinnableSlice` pinning; perf-context counters; and statistics tickers. Tests explicitly reset perf context and statistics between phases to isolate cache hits, misses, adds, bytes read, bytes written, checksum time, decompression time, and filesystem read counters.

The reservation fixture validates that blob cache memory is charged through `ChargedCache` and that dummy reservation size is released when the last blob cache entry is erased through the wrapper.

## Dependencies

The tests depend on RocksDB internals: `db/blob/blob_source.h`, `BlobFileCache`, `BlobFileReader`, `BlobLogWriter`, `BlobLogRecord`, `BlobLogHeader`, `BlobLogFooter`, compression helpers, `CompressedSecondaryCache`, `ChargedCache`, `DBTestBase`, filename utilities, and perf/statistics infrastructure. Snappy-specific tests skip when Snappy is unavailable.

## Integration Points

Although the tests instantiate `BlobSource` directly, they model the read behavior used by higher-level DB `Get`, iterator, MultiGet, and compaction code. They verify the boundary between blob file reader cache and blob value cache, the cache key format shared with secondary cache, `ReadOptions::read_tier` semantics, and the DB identity/session scoping used to avoid cache key collisions across DB lifetimes.

## Risks

- Cache counter assertions are detailed and can become brittle if cache lookup ordering changes, even when user-visible behavior remains correct.
- The tests depend on hand-computed file sizes and record byte counts; changes to blob log record encoding or footer/header size require updates.
- Secondary cache behavior relies on dummy-handle implementation details and raw cache lookups, so it can fail on internal cache refactors.
- Error preservation tests require the first read to populate/open a file and a later deleted-file refresh path to combine corruption and I/O details correctly.
- Compression tests use compressed sizes as read inputs; any compression framing or manager behavior change can alter expected size comparisons.

## Test Signals

Strong signals include exact `Status` categories (`OK`, `Incomplete`, `IOError`, `Corruption`), returned value equality, `PinnableSlice::IsPinned`, `TEST_BlobInCache`, perf-context counters, `BLOB_DB_CACHE_*` ticker counts, secondary cache hit/promotion state, and charged cache reservation sizes. These tests are especially useful when changing `BlobSource`, blob cache admission, secondary cache integration, blob file reader refresh, or blob log format accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.cc

## Purpose

This implementation transforms an input `WriteBatch` into an output batch that stores eligible large values directly in blob files and replaces them with `BlobIndex` records. It is the direct-write bridge between the write batch layer and `BlobFilePartitionManager`. Non-qualifying operations are copied through unchanged so callers can use the transformed batch only when at least one value was separated.

It also handles wide-column entities by rewriting eligible columns into V2 serialized wide-column entities containing blob references, while preserving rollback accounting for blob records already appended to blob files.

## Important APIs, Types, and Functions

- `BlobWriteBatchTransformer::TransformBatch(...)`: static entry point. Clears the output batch, iterates the input batch through the handler, reports whether any value was transformed, and returns used partition managers and rollback info.
- `MaybePreprocessWideColumns(...)`: shared helper for sorted wide-column arrays. It selects a wide-column partition, writes each column meeting `min_blob_size`, decodes the generated blob index, and serializes either V2 blob-bearing entities or inline entities.
- `PutCF(...)`: direct-write path for ordinary puts. It caches per-CF settings and manager lookups, writes qualifying values with `BlobFilePartitionManager::WriteBlob`, records `RollbackInfo`, encodes a `BlobIndex`, and appends `PutBlobIndex` to the output batch.
- `PutEntityCF(...)`: deserializes V2 entities, rejects pre-existing blob references, rewrites large columns through `MaybePreprocessWideColumns`, or passes the original serialized entity through.
- `TimedPutCF`, deletes, range deletes, merges, existing blob indexes, log data, and transaction markers are pass-through handlers implemented with `WriteBatchInternal`.

## Control Flow

`TransformBatch` constructs a handler and calls `input_batch->Iterate(&transformer)`. Each callback writes to `output_batch_`. If no callback transforms data, `has_transformed_` remains false and callers can ignore the output batch.

For a `PutCF`, the handler refreshes cached CF settings/partition manager when the CF ID changes. It passes through when no manager exists, direct write is disabled, or the value is below `min_blob_size`. Otherwise it writes the blob, tracks the manager and exact file/count/byte rollback tuple, encodes a `BlobIndex`, sets `has_transformed_`, and emits a blob-index put.

For a `PutEntityCF`, the handler similarly caches CF state, passes through when direct write is unavailable, deserializes the entity as V2, rejects entities that already contain blob references, then calls the wide-column preprocessing helper. If no column qualifies, the original serialized entity is preserved; if any column qualifies, the rewritten entity is emitted.

All transaction-control records are reproduced in the output batch, so transformed batches preserve prepare/commit/rollback/noop structure.

## State and Persistence Behavior

The transformer itself is per-batch and transient, but it causes persistent side effects before the DB write batch has necessarily committed: qualifying values are appended to blob files via `BlobFilePartitionManager::WriteBlob`. Because those appends may outlive a later write failure, the transformer collects `RollbackInfo` with partition manager, file number, blob count, and byte count so callers can account abandoned writes as initial garbage.

The class caches the last CF settings and partition manager to avoid repeated provider lookups for consecutive entries. It also stores `used_managers_` so callers can flush or sync blob file managers after transformation. `blob_index_buf_` is reused across puts to reduce allocation.

## Dependencies

The implementation depends on `BlobFilePartitionManager`, `BlobIndex`, `BlobLogRecord`, wide-column serialization, `WriteBatchInternal`, compression settings from `BlobDirectWriteSettings`, and `WriteBatch::Handler` callback ordering. It uses `UNLIKELY` for the unsupported pre-serialized blob-reference path.

## Integration Points

This code is called from write paths that enable blob direct write. It consumes provider callbacks so the DB layer can supply per-column-family blob settings and partition managers. Its output is a normal `WriteBatch` containing inline entries plus blob index entries, making it compatible with the rest of write batch processing, WAL/transaction markers, memtable insertion, and recovery semantics.

The wide-column path integrates with entity serialization: it accepts already sorted columns and emits V2 entities when blob references are present. It intentionally rejects user-supplied/pre-serialized entities with blob references because those references would not be covered by the current batch's blob lifetime tracking.

## Risks

- Blob writes happen before the transformed batch is durable, so rollback accounting must remain exact or garbage statistics and blob GC can become inaccurate.
- `MaybePreprocessWideColumns` may write some blobs and then fail during a later blob write, blob-index decode, or serialization; callers depend on partial rollback info being returned.
- Pre-existing blob references in entities are rejected to avoid stale references; relaxing that rule would require lifetime tracking outside this transformer.
- The output batch is meaningful only when `transformed` is true. Callers must use the original batch when false because pass-through output is still produced during iteration but is documented as ignorable only in the no-transform case.
- CF setting caching assumes provider results are stable for the duration of one batch transformation.

## Test Signals

Useful verification signals include transformed flag behavior, output batch contents (`PutBlobIndex` for qualifying puts and `PutEntitySerialized` V2 for qualifying entities), correct pass-through for deletes/merges/timed puts/transaction markers, used manager collection, rollback byte counts using `BlobLogRecord::kHeaderSize + key.size() + blob_size`, rejection of V2 entities with existing blob references, and successful reads of transformed values through normal DB paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.h -->
# sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.h

## Purpose

This header declares the public contract for direct-write blob batch transformation. It defines the per-column-family settings required to decide whether a write should be separated into blob files, provider callback types for settings and partition managers, and the `BlobWriteBatchTransformer` handler class that rewrites `WriteBatch` contents.

The header is intentionally narrow: it exposes enough for DB write paths to invoke transformation and clean up side effects, while leaving blob writing and partition selection to `BlobFilePartitionManager`.

## Important APIs, Types, and Functions

- `BlobDirectWriteSettings`: settings snapshot with `enable_blob_direct_write`, `min_blob_size`, `compression_type`, `compression_opts`, raw `Cache* blob_cache`, and `PrepopulateBlobCache`.
- `BlobDirectWriteSettingsProvider`: callback from CF ID to settings.
- `BlobPartitionManagerProvider`: callback from CF ID to `BlobFilePartitionManager*`.
- `BlobWriteBatchTransformer::RollbackInfo`: records `partition_mgr`, `file_number`, appended record `count`, and appended `bytes` for failed transformed writes.
- `MaybePreprocessWideColumns(...)`: static helper for callers that need direct-write processing of wide-column data outside a full batch handler.
- `TransformBatch(...)`: static full-batch API with optional `used_managers` and `rollback_infos` outputs.
- `WriteBatch::Handler` overrides: put, timed put, entity put, delete, single delete, range delete, merge, existing blob index, log data, and transaction markers.
- `HasTransformed()`: reports whether at least one value was rewritten to a blob index.

## Control Flow

The intended call flow is provider setup, `TransformBatch`, then conditional use of the output batch. `TransformBatch` drives the handler callbacks internally, so most callers do not instantiate the handler directly. During callbacks, the private cached CF ID, settings, and partition manager avoid repeated provider lookups.

The class has two transformation surfaces: ordinary key/value puts and wide-column entities. Ordinary puts are rewritten when the value size crosses the CF's minimum threshold. Wide-column entities are parsed and selectively rewritten per column, producing a V2 entity only when necessary.

## State and Persistence Behavior

The header documents that transformation can append blob records before the final batch succeeds. `RollbackInfo` is therefore part of the contract: even on failure, partial blob writes should be observable to callers so they can account them as garbage. `used_managers` similarly exposes which partition managers received data and may need follow-up flush/sync work.

`BlobDirectWriteSettings::blob_cache` is a raw pointer because it is owned by `ColumnFamilyOptions` and expected to outlive settings snapshots. This avoids reference-count overhead in hot put paths but makes lifetime expectations explicit.

## Dependencies

The header depends on RocksDB public option and write-batch types (`advanced_options.h`, `compression_type.h`, `options.h`, `slice.h`, `status.h`, `write_batch.h`) plus `util/hash_containers.h`. It forward-declares `BlobFilePartitionManager` and `Cache` to reduce compile coupling.

## Integration Points

DB write code supplies the two provider callbacks from column-family metadata. The transformed output batch integrates with `WriteBatchInternal`, memtable insertion, WAL/transaction handling, and blob GC accounting. Wide-column integration depends on callers passing sorted `WideColumns`, as documented by `MaybePreprocessWideColumns`.

## Risks

- Provider callbacks and raw cache pointers encode lifetime assumptions that must remain true across write path refactors.
- The header contract says `output_batch` is empty/ignorable when no values qualify, so callers need to respect `transformed`.
- The rollback vector is optional, but callers that skip it cannot precisely account abandoned blob records after transformation failure.
- `MaybePreprocessWideColumns` requires sorted columns; unsorted input can produce serialized entities that violate wide-column ordering assumptions.

## Test Signals

Header-level behavior is validated by implementation and DB tests that check direct-write blob indexes, wide-column entity reads, rollback/garbage accounting, prepopulate cache settings, compression propagation, and pass-through of non-transforming write batch records. API compatibility signals include successful compilation of write path callers using providers, `RollbackInfo`, and all handler overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_write_batch_transformer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_basic_test.cc -->
# sources/storage-engines/rocksdb/db/blob/db_blob_basic_test.cc

## Purpose

This file is the main end-to-end DB test suite for integrated blob-file behavior. Unlike `blob_source_test.cc`, it exercises public `DB` APIs and DB-internal paths that produce, read, cache, merge, trace, recover, and size blob-backed values. It validates that blob indexes stored in SSTs are transparent to users while preserving correct error statuses and cache semantics.

The coverage spans `Get`, iterators, `MultiGet`, direct I/O multi-read ordering, multiple blob files, corrupt blob indexes, inlined TTL blob indexes, missing files, IO tracing, best-efforts recovery, merge operands, DB properties, blob cache prepopulation, secondary cache, wide-column `GetEntity`, timestamped reads, and approximate-size accounting.

## Important APIs, Types, and Functions

- `DBBlobBasicTest`: base fixture using `DBTestBase`.
- `DBBlobBasicIOErrorTest` and `DBBlobBasicIOErrorMultiGetTest`: parameterized fixtures using `FaultInjectionTestEnv` and sync points for blob open/read failures.
- `DBBlobWithTimestampTest`: timestamp-aware fixture using `DBBasicTestWithTimestampBase` and `TestComparator`.
- Public APIs under test: `Put`, `Flush`, `Get`, `MultiGet`, `NewIterator`, `PrepareValue`, `GetEntity`, `MultiGetEntity`, `CompactRange`, `IngestExternalFile`, `StartIOTrace`, `EndIOTrace`, `GetProperty`, `GetIntProperty`, `GetApproximateSizes`, and dynamic `SetOptions`.
- Internal helpers and types: `BlobIndex`, `WriteBatchInternal::PutBlobIndex`, `BlobLogRecord`, `BlobFilePartitionManager`, `BlobLogSequentialReader`, `RandomAccessFileReader::MultiRead`, `SyncPoint`, trace reader/writer types, and file-name parsing.

## Control Flow

Most tests enable blob files, choose `min_blob_size`, write values, flush to produce SSTs containing blob indexes plus blob files, and then use a public read path to verify transparent value reconstruction. Cache-focused tests alternate `ReadOptions::fill_cache` and `read_tier` to prove blob values are unavailable in cache-only mode until explicitly cached.

Iterator tests cover forward and backward movement, cache pinning on blob values only, and `allow_unprepared_value`, where keys can be positioned before blob values are fetched and `PrepareValue()` performs the actual blob read.

`MultiGetWithDirectIO` constructs a layout where keys from different levels refer to offsets in the same blob file out of offset order. A sync point asserts that blob multi-read requests are sorted before direct I/O alignment so the filesystem sees one merged aligned request.

Error tests tamper with blob indexes, inject filesystem errors at blob open/read sync points, or simulate table-cache `FindTable` errors. They assert precise per-key statuses and ensure raw blob handles are not leaked as values after partial failures.

Later tests validate cache warmup during flush, runtime disabling of `prepopulate_blob_cache`, secondary cache promotion, wide-column entity reads backed by blobs, timestamped blob values and merges, and approximate sizes with optional blob-file inclusion.

## State and Persistence Behavior

These tests create real RocksDB state: WAL/write batches, SST files with blob indexes, blob files, table cache entries, blob cache entries, secondary cache entries, properties derived from version metadata, and optional IO trace files. `Flush` is the main persistence boundary for creating blob files. `CompactRange` updates live version metadata, garbage accounting, and sometimes blob file liveness.

Cache state is intentionally manipulated with shared LRU caches, small cache capacities, and `read_tier`. Some tests hold iterators open to keep old versions alive, proving `kTotalBlobFileSize` counts blob files across live versions without double-counting shared files.

Best-efforts recovery deletes the newest blob file after flushing two table/blob pairs and verifies reopening with `best_efforts_recovery` can fall back to an older value.

## Dependencies

The suite depends on RocksDB DB test utilities, blob index/log formats/readers, block-based table cache options, compressed secondary cache, file naming, random access file readers, trace reader/writer utilities, replay support, sync points, compression helpers, fault injection env, merge operators, and timestamp comparator test utilities.

Some tests depend on platform support, especially direct I/O. The direct I/O test skips when reopening with `use_direct_reads` returns `InvalidArgument`.

## Integration Points

This file is a broad integration harness for blob files across the DB stack: write path blob creation, SST blob-index lookup, version-level `Get` and `MultiGetBlob`, iterators, merge resolution, compaction filters, table cache errors, IO tracing, cache prepopulation during flush, secondary cache, timestamped APIs, DB properties, and approximate-size estimation.

It also protects interactions with external SST ingest and bottommost-level compaction, ensuring blob reads still work when table levels and blob file offsets are not naturally aligned by user key order.

## Risks

- Many tests assert exact status classes. Reclassifying errors between `Incomplete`, `IOError`, `Corruption`, and `Aborted` can break compatibility.
- Direct I/O request ordering is subtle; unsorted blob offsets can increase I/O count or violate alignment assumptions.
- `allow_unprepared_value` changes iterator validity after `PrepareValue()` failures, so iterator state transitions are easy to regress.
- Empty values must remain inline even with `min_blob_size = 0`; storing them as blobs can waste space and break secondary cache paths.
- Cache prepopulation must happen during flush but not compaction, and runtime option changes must take effect for later flushes.
- Timestamped iteration combines internal keys, user timestamps, blob values, and bounds; comparator or iterator changes can disturb ordering.

## Test Signals

High-value signals include cache-only `Incomplete` reads before blob caching, successful cache-only reads after fill-cache or flush prepopulation, exact merge results, corruption from malformed blob indexes, IOError preservation under injected filesystem failures, direct I/O aligned request count, `BLOB_DB_CACHE_*` and `SECONDARY_CACHE_HITS` ticker counts, DB blob property strings and integer properties, IO trace records containing blob file operations, and approximate sizes increasing when `include_blob_files` is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_basic_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_compaction_test.cc -->
# sources/storage-engines/rocksdb/db/blob/db_blob_compaction_test.cc

## Purpose

This file tests compaction behavior when values are stored in blob files. It verifies when compaction can decide using blob indexes only, when it must read blob values, when it writes replacement blob records, how blob garbage is tracked, and how blob reads are optimized during compaction with readahead and cache bypass.

The tests are built around custom `CompactionFilter` implementations that use different decision APIs (`FilterBlobByKey` and `FilterV2`) and different decisions (`kKeep`, `kRemove`, `kChangeValue`, `kRemoveAndSkipUntil`, invalid blob decisions, and errors).

## Important APIs, Types, and Functions

- `DBBlobCompactionTest::GetCompactionStats()`: reaches into `VersionSet`, default `ColumnFamilyData`, and `InternalStats` to inspect per-level compaction blob bytes.
- `FilterByKeyLength`: removes blob-backed entries based only on key length using `FilterBlobByKey`.
- `FilterByValueLength`: removes based on materialized value length through `FilterV2`.
- `BadBlobCompactionFilter`: returns unsupported decisions to validate error handling.
- `ValueBlindWriteFilter`: writes a new value from `FilterBlobByKey` without reading the old blob.
- `ValueMutationFilter`: reads existing values through `FilterV2` and appends padding.
- `AlwaysKeepFilter`, `SkipUntilFilter`, and `ReadBlobCompactionFilter`-style behavior validate keep, skip-until iteration, and read-blob paths.
- Sync points observe blob-index tampering, `BlobCountingIterator` in-flow processing, and non-prefetch blob reads.

## Control Flow

The tests generally enable blob files, set `min_blob_size`, install a compaction filter, write keys, flush, run `CompactRange`, then verify user-visible values and internal blob byte stats.

Key-only filtering removes entries without reading or writing blob files, so `bytes_read_blob` and `bytes_written_blob` remain zero. Value-based filtering reads blob values and removes short ones, so read bytes increase while write bytes stay zero. Blind writes produce replacement blob records without reading old blob values. Value mutation reads old blobs and writes new blobs.

`BlobCompactWithStartingLevel` uses an SST partitioner to force multiple output table files and checks that blob files are created only when compaction output reaches `blob_file_starting_level`.

`TrackGarbage` writes two flush generations, overwrites two keys, compacts, then inspects `VersionStorageInfo::GetBlobFiles()` metadata to confirm old blob records are marked garbage while newer records remain live.

Readahead tests enable `blob_compaction_readahead_size` and use sync points to assert compaction paths that need blob values avoid non-prefetch reads. `CompactionDoNotFillCache` confirms compaction blob reads do not populate the blob cache.

## State and Persistence Behavior

Compaction rewrites table metadata and can update blob file metadata without always rewriting blob files. Some filters remove table references, making existing blob records garbage. Other filters write replacement blob records and produce new blob files or new records. `TrackGarbage` directly validates durable version metadata for total blob count, total blob bytes, garbage blob count, and garbage blob bytes.

Starting-level behavior controls when values remain inline in compaction output versus being written to blob files. Readahead state is transient read buffering during compaction and should not alter cache state.

## Dependencies

The file depends on `BlobIndex`, `BlobLogRecord`, DB test utilities, `InternalStats`, `VersionSet`, `VersionStorageInfo`, compaction filters, merge operators, SST partitioners, and sync points. It uses direct internal metadata access rather than only public properties.

## Integration Points

These tests protect the integration between blob indexes and the compaction iterator, compaction filters, merge resolution, blob garbage collection, blob file metadata, blob compaction readahead, and cache admission policy. They also validate that unsupported compaction-filter decisions for blob paths fail as `NotSupported` rather than silently corrupting data.

## Risks

- Blob byte counters depend on precise record-size accounting via `BlobLogRecord::CalculateAdjustmentForRecordHeader`.
- `FilterBlobByKey` paths must not accidentally materialize blob values, or key-only compactions become unnecessarily expensive.
- `FilterV2` paths must receive materialized values for blob-backed entries and must not see `kBlobIndex` when a normal value is expected.
- Unsupported decisions such as `kChangeBlobIndex` and `kIOError` from filter paths must fail cleanly.
- Readahead regressions may preserve correctness but cause extra non-prefetch reads, hurting compaction performance.
- Compaction reads should not fill the blob cache; doing so can pollute user read caches.

## Test Signals

Important signals include final `Get` results, `CompactRange` statuses (`OK`, `NotSupported`, `Corruption`), per-level `bytes_read_blob` and `bytes_written_blob`, blob file counts, table file counts by level, blob file metadata totals and garbage counts/bytes, sync-point counters for in-flow skip handling and non-prefetch reads, and `BLOB_DB_CACHE_ADD` remaining zero during compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_compaction_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_corruption_test.cc -->
# sources/storage-engines/rocksdb/db/blob/db_blob_corruption_test.cc

## Purpose

This small test file verifies whole-file checksum validation for blob files. It creates blob files with file checksum generation enabled, corrupts the newest blob file on disk, reopens the DB, and asserts `VerifyFileChecksums` reports corruption and triggers the checksum mismatch sync point exactly once.

## Important APIs, Types, and Functions

- `DBBlobCorruptionTest`: `DBTestBase` fixture for blob corruption tests.
- `Corrupt(FileType filetype, int offset, int bytes_to_corrupt)`: scans the DB directory, picks the latest file of the requested type, and corrupts bytes in place with `test::CorruptFile`.
- `VerifyWholeBlobFileChecksum`: test enabling `file_checksum_gen_factory`, writing two blob files, verifying checksums, corrupting one blob file, then validating corruption detection.
- `DBImpl::VerifyFullFileChecksum:mismatch`: sync point used to observe the internal mismatch status.

## Control Flow

The test opens a DB with `enable_blob_files`, `min_blob_size = 0`, and CRC32C file checksum generation. It writes and flushes two blob values, verifies checksums successfully, closes the DB, corrupts bytes at offset zero of the latest `.blob` file, reopens, installs a sync-point callback, and runs `VerifyFileChecksums(ReadOptions())`. The callback counts mismatch events and asserts the status is non-OK.

## State and Persistence Behavior

Persistent state is two flushed blob files with whole-file checksum metadata. The test mutates one blob file after close, then reopens so verification reads the durable corrupted file rather than cached state. No repair is attempted; the expected durable signal is checksum mismatch corruption.

## Dependencies

The file depends on `DBTestBase`, file-name parsing via `ParseFileName`, `test::CorruptFile`, `GetFileChecksumGenCrc32cFactory`, `SyncPoint`, and `VerifyFileChecksums`. It installs the normal RocksDB stack trace handler and custom object registration in `main`.

## Integration Points

This test ties blob files into the DB-wide full file checksum verification API. It ensures blob files are included alongside other file types and that internal mismatch reporting preserves a corruption status visible both through sync points and the public `VerifyFileChecksums` result.

## Risks

- The helper corrupts the latest file of a type, so file numbering and flush behavior must create at least one blob file and leave it in the DB directory.
- Corrupting at offset zero assumes header/checksum validation will detect the change; checksum format changes should preserve that signal.
- Sync-point callback cleanup is required to avoid leaking callbacks into later tests.

## Test Signals

The key signals are an initial successful `VerifyFileChecksums`, successful reopen after corruption, final `VerifyFileChecksums(...).IsCorruption()`, and exactly one invocation of `DBImpl::VerifyFullFileChecksum:mismatch` with a non-OK status.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_corruption_test.cc -->
