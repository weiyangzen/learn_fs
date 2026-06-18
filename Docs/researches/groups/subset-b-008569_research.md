<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_direct_write_test.cc -->
# sources/storage-engines/rocksdb/db/blob/db_blob_direct_write_test.cc

## Purpose
This GoogleTest file validates RocksDB blob direct-write behavior, where eligible large user values are written directly to blob files during foreground writes while memtables/SSTs store blob indexes. It stresses direct-write partitioning, active-file readability, flush/reopen recovery, dynamic option changes, initial garbage accounting for failed writes, lazy iterator pinning, ordered tracing, and unsupported configurations.

## Important APIs, Types, And Functions
`FixedBlobDirectWritePartitionStrategy` and `RecordingBlobDirectWritePartitionStrategy` implement `BlobFilePartitionStrategy` for deterministic partition routing and call inspection. `RemoteBlobVisibilityFileSystem`, `ActiveBlobVisibilityWritableFile`, and `ActiveBlobVisibilityRandomAccessFile` model file systems where active blob size visibility depends on `FileOpenContract`. The `DBBlobDirectWriteTest` fixture derives from `DBTestBase` and provides `GetBlobDirectWriteCompatibleOptions()`, `GetDirectWriteOptions()`, `CountBlobFiles()`, `ReadBlobFileHeader()`, `ReadBlobFileRecords()`, `GetSupportedCompressedBlobCompression()`, and `AssertOrderedTraceStoresLogicalPut()`. `DBBlobDirectWriteWithTimestampTest` derives from timestamp test infrastructure to verify timestamp rejection.

## Control Flow
Most tests open with direct-write-compatible options, issue `Put`, `WriteBatch`, `Delete`, `Flush`, `CompactRange`, `Close`, and `Reopen`, then read through `Get`, `MultiGet`, iterators, metadata APIs, or raw blob-log readers. Partition tests verify the default round-robin path, fixed/custom routing, modulo handling for out-of-range partition returns, per-blob strategy calls inside a batch, and shared strategy behavior across column families. Reader tests intentionally open a reader while a direct-write file is active, append more blobs, flush or keep the file growing, and then confirm cached readers refresh enough to read later offsets. Rotation and compression tests force new blob files by size or option changes and inspect blob headers/records to ensure compression type/options are reflected in persisted data. Failure-path tests inject a post-direct-write error, then assert the physical blob record is recorded as initial garbage after a later successful flush.

## State And Persistence Behavior
The tests persist blob log files, SST metadata, manifest blob additions/garbage, column-family metadata, ordered traces, and WAL/recovery state. They assert active direct-write files remain readable before flush, sealed files survive reopen, failed foreground writes do not become visible user records, and blob metadata tracks total/garbage counts and bytes across reopen. Lazy iterator tests rely on old blob files remaining live while an iterator with `allow_unprepared_value` still references them through a version, even after overwrites, flush, compaction, and purge waiting.

## Dependencies And Integration Points
Coverage touches `db/blob/blob_file_partition_manager.h`, `db/blob/blob_index.h`, `db/blob/blob_log_format.h`, `db/blob/blob_log_sequential_reader.h`, `ColumnFamilyData`/`ColumnFamilyHandleImpl`, `RandomAccessFileReader`, composite file systems, trace/replayer APIs, compression utilities, sync points, fault-injection style status injection, and wide-column test utilities. The tests integrate foreground write preprocessing with blob file partition management, memtable reads, immutable memtables, flush, compaction, manifest metadata, DB properties, table/cache readers, and trace serialization.

## Risks And Edge Cases
Direct write is deliberately rejected with pipelined writes, concurrent memtable writes, unordered writes, two write queues, mempurge, and user-defined timestamps because ordering, rollback, and blob-index visibility contracts would be unsafe. File-open-contract behavior is risky on remote file systems; active blob writers must promise no write reopen but still allow readers. Dynamic compression settings risk stale cached compressors, so tests toggle compression types and ZSTD checksum options. Failed writes risk leaked visible blobs; tests expect those records to become manifest-tracked garbage. Lazy iterators risk dereferencing purged blob files; tests require version-held blob metadata to keep old files live.

## Test Signals
The file is itself a high-signal suite. It checks direct reads, direct IO skip behavior, blob file counts, `ColumnFamilyMetaData`, `LiveFileMetaData.oldest_blob_file_number`, raw blob log headers/records, DB properties, `BlobFilePartitionManager` rollback error handling, ordered trace contents, `KeyMayExist`, `MultiGet`, iterator forward/backward/prepare-value paths, and reopen persistence. It also uses `SyncPoint` for deterministic write-failure injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_direct_write_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_index_test.cc -->
# sources/storage-engines/rocksdb/db/blob/db_blob_index_test.cc

## Purpose
This GoogleTest file verifies how RocksDB stores, exposes, resolves, filters, iterates, compacts, garbage-collects, and recovers blob-index-backed values. It covers both the legacy StackableDB BlobDB contract for raw `kTypeBlobIndex` records and the integrated BlobDB/wide-column path where large columns or values are stored in blob files and resolved on demand.

## Important APIs, Types, And Functions
`DBBlobIndexTest` derives from `DBTestBase` and defines storage tiers (`kMemtable`, `kImmutableMemtables`, `kL0SstFile`, `kLnSstFile`) to exercise the same operation from memtables and SSTs. Helper methods include `PutBlobIndex()`, `GetImpl()`, `GetBlobIndex()`, `GetBlobIterator()`, `MaybeResolveDirectWriteValueForTest()`, `MaybeResolveMemtableBlobValueForTest()`, `GetTestOptions()`, `GetBlobTestOptions()`, and `MoveDataTo()`. The file defines multiple compaction filters and factories: plain value filters for flush, lazy wide-column filters using `WideColumnBlobResolver`, eager/resolving filters, FilterV3-only compatibility filters, remove filters, and a TTL-style entity drop filter. `CorruptPinnedBlobIndexOnCleanup()` stresses pinned-slice lifetime by corrupting backing storage after cleanup.

## Control Flow
The early tests write raw blob-index values through `WriteBatchInternal::PutBlobIndex`, move data across tiers, and assert `GetImpl` returns raw blob indexes only when `is_blob_index` is supplied; normal base-DB reads fail with `NotSupported` from memtables or `Corruption` from SSTs. Update and iterator tests combine blob indexes with puts, merges, deletes, single deletes, delete ranges, snapshots, normal iterators, and blob-exposing iterators. Direct-write helper tests ensure blob indexes are decoded before `PinnableSlice` cleanup and fail closed when no blob fetcher is available. The integrated tests write wide-column entities with large blob-backed columns, flush, compact, recover from WAL, mix entity writes with regular puts, run lazy/eager compaction filters, delete backing blob files to force resolver errors, and verify passive GC drops all-garbage blob files after filtered entity removal.

## State And Persistence Behavior
The tests persist raw internal value types in memtables/SSTs, wide-column entity encodings, blob files, manifest blob metadata, snapshots, WAL records, and DB properties/statistics. Snapshot tests require older blob-backed entity values to remain readable through a snapshot while current values move forward. Recovery tests require blob-backed entities in flushed SSTs and unflushed WAL entries to survive close/reopen, including `avoid_flush_during_recovery`. Passive GC tests rely on compaction-produced blob garbage metadata to remove blob files whose only references came from dropped wide-column entities.

## Dependencies And Integration Points
The file ties together `DBImpl::GetImpl`, `DBImpl::MaybeResolveDirectWriteValue`, `DBImpl::MaybeResolveMemtableBlobValue`, `ArenaWrappedDBIter`, `BlobIndex`, `WriteBatchInternal`, merge operators, `ColumnFamilyData`, wide-column APIs (`PutEntity`, `GetEntity`, `Iterator::columns()`), `CompactionFilter` FilterV3/FilterV4 contracts, `WideColumnBlobResolver`, blob file name helpers, DB statistics tickers, and universal compaction/passive GC. It is a broad integration surface between read path blob-index exposure, compaction filtering, blob fetching, and garbage accounting.

## Risks And Edge Cases
Raw blob-index bytes must never be returned as user values accidentally; unresolved memtable blob values without a fetcher must fail closed. FilterV3-only filters expect eager resolution and must fail compaction if blob reads fail before the filter sees data. FilterV4 lazy filters can avoid blob IO by using `IsBlobColumn()`, but once `ResolveColumn()` reports an error the compaction must fail even if the filter returns `kKeep`. Iterators must distinguish exposed blob values from normal values and set status correctly across seek/next/prev paths. Passive GC can regress if `BlobGarbageMeter` misses `kTypeWideColumnEntity` garbage after filters drop entities.

## Test Signals
The suite asserts exact status categories (`OK`, `NotFound`, `NotSupported`, `Corruption`, `IOError`), raw blob-index equality, iterator validity/status, `ArenaWrappedDBIter::IsBlob()`, blob read byte statistics, blob file counts and sizes, DB properties (`kNumBlobFiles`, `kTotalBlobFileSize`), background error severity, and post-compaction entity/regular value equality. Missing-blob tests deliberately delete blob files and check compaction and background error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/db_blob_index_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.cc -->
# sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.cc

## Purpose
Implements lazy creation and lookup for `PrefetchBufferCollection`, a small blob-compaction helper that keeps one `FilePrefetchBuffer` per blob file number.

## Important APIs, Types, And Functions
The sole function is `FilePrefetchBuffer* PrefetchBufferCollection::GetOrCreatePrefetchBuffer(uint64_t file_number)`. It uses `ReadaheadParams` and `FilePrefetchBuffer` from RocksDB file prefetch infrastructure.

## Control Flow
The method indexes `prefetch_buffers_` by `file_number`, creating an empty map entry when none exists. If the `unique_ptr` is null, it builds `ReadaheadParams` with both `initial_readahead_size` and `max_readahead_size` set to the collection's fixed `readahead_size_`, constructs a `FilePrefetchBuffer`, stores it in the map, and returns the raw pointer. Later calls for the same file number return the existing buffer.

## State And Persistence Behavior
There is no on-disk persistence. State is in-memory only: an unordered map from blob file number to owned prefetch buffer. The collection lifetime owns all buffers, and callers receive non-owning pointers whose validity is bounded by the collection lifetime and map entry lifetime.

## Dependencies And Integration Points
The implementation depends on `db/blob/prefetch_buffer_collection.h` and indirectly on `file/file_prefetch_buffer.h`. It is designed for compaction readahead when blob-backed records need reads from potentially many blob files. Each subcompaction should have its own collection because access is intentionally single-threaded.

## Risks And Edge Cases
`operator[]` mutates the map even on lookup, so every distinct requested file number consumes a map entry and potentially a buffer. The class has no locking; sharing it across subcompactions would race and could corrupt buffer state. The fixed initial/max readahead sizes avoid growth but also mean incorrect sizing cannot adapt dynamically within this helper.

## Test Signals
No direct tests appear in this file. Behavioral coverage is expected through blob compaction and blob-index/wide-column tests that exercise blob fetching and compaction readahead paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.h -->
# sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.h

## Purpose
Declares `PrefetchBufferCollection`, an owner for per-blob-file `FilePrefetchBuffer` objects used to implement compaction readahead for blob files.

## Important APIs, Types, And Functions
The public API is `explicit PrefetchBufferCollection(uint64_t readahead_size)` and `FilePrefetchBuffer* GetOrCreatePrefetchBuffer(uint64_t file_number)`. Private state is `uint64_t readahead_size_` and `std::unordered_map<uint64_t, std::unique_ptr<FilePrefetchBuffer>> prefetch_buffers_`.

## Control Flow
Construction records the configured readahead size and asserts it is positive. Lookup/creation is implemented in the `.cc` file and returns a stable non-owning pointer to the buffer associated with a file number. The map key is the blob file number, not a path or cache key.

## State And Persistence Behavior
All state is transient memory owned by the collection. It has no explicit cleanup method because `unique_ptr` members release buffers when the collection is destroyed. The comments state it is single-thread-only and each subcompaction should maintain its own collection because even reads from the same blob file can happen from different positions.

## Dependencies And Integration Points
The header includes `file/file_prefetch_buffer.h` and RocksDB namespace definitions. It integrates with blob compaction/read code that needs readahead without sharing `FilePrefetchBuffer` instances between independent scan streams.

## Risks And Edge Cases
The constructor only asserts positive `readahead_size_`; release builds rely on callers to pass a meaningful nonzero value. There is no concurrency protection, and buffer pointers should not escape longer than the collection. Since buffers are keyed only by file number, callers requiring multiple independent streams over the same blob file need separate collections.

## Test Signals
The header has no standalone tests. Indirect test signals should come from compaction tests that compare blob read behavior, lazy resolution, and performance/statistics when blob files are read during compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.cc -->
# sources/storage-engines/rocksdb/db/builder.cc

## Purpose
Implements RocksDB table creation for flush/recovery/compaction-style paths. `BuildTable()` consumes an internal iterator plus range tombstones, optionally creates blob files, writes an SST through a `TableBuilder`, fills `FileMetaData`, performs verification and IO finalization, tracks blob garbage/additions, emits listener/event-log notifications, and cleans up failed or empty outputs.

## Important APIs, Types, And Functions
`NewTableBuilder()` delegates to the configured table factory after asserting column-family ID/name consistency. `ExtractTimestampFromTableProperties()` copies `rocksdb.timestamp_min` and `rocksdb.timestamp_max` user properties into `FileMetaData`. `BuildTable()` is the central function; important collaborators include `OutputValidator`, `CompactionRangeDelAggregator`, `BlobGarbageMeter`, `BlobCountingIterator`, `MergeHelper`, `BlobFileBuilder`, `CompactionIterator`, `WritableFileWriter`, `TableCache`, `SeqnoToTimeMapping`, `EventHelpers`, and `TableProperties`.

## Control Flow
`BuildTable()` initializes metadata, optionally wraps the input iterator with `BlobCountingIterator` for flush-time blob garbage accounting, seeks input, aggregates fragmented range tombstones, builds the output table file name, and notifies listeners that table creation started. If there are point records or range tombstones, it may create a compaction filter for table-file creation, opens a writable SST with a no-reopen/no-readers contract, wraps it in `WritableFileWriter`, creates a `TableBuilder`, and constructs a `CompactionIterator`. When blob files are enabled and level/options allow it, `BlobFileBuilder` is attached so eligible values are emitted to blob files while table values become blob references.

During iteration, each compaction output key/value is optionally rewritten from `kTypeValuePreferredSeqno` to a packed preferred seqno or plain `kTypeValue`, added to the output validator and table builder, counted in flush stats, passed through blob garbage outflow accounting, and used to update `FileMetaData` boundaries. Range tombstones are serialized after point keys and update range boundaries and compensated range-deletion size. The builder is abandoned on error or empty output; otherwise relevant seqno-time mappings are copied, table properties are set, and `Finish()` completes the table.

After finish, the function propagates builder IO status, fills file size/tail/checksum/unique ID/table properties/timestamp fields, syncs and closes the writer, finishes or abandons attached blob file creation, opens the new table through `TableCache` for usability checks, optionally performs paranoid output hash validation by scanning the file, checks iterator status, emits blob garbage records, and deletes SST/blob files on failure or empty output. Final events use `(nil)` and an aborted listener status for empty SSTs even when the returned status is OK.

## State And Persistence Behavior
Successful execution persists an SST file, optional blob files, file checksums, unique IDs, table properties, timestamp ranges, smallest/largest keys and sequence numbers, blob additions, blob garbage, memtable payload/garbage byte estimates, flush stats, and optional fast-open metadata. Failed or empty builds delete the partially created SST and any created blob files and release obsolete table-cache handles. The function is careful to sync/close before exposing checksum metadata and to notify listeners both at start and finish.

## Dependencies And Integration Points
This file is a core integration point among DB options, file systems, table factories, compaction iteration, merge operators, compaction filters, range tombstone aggregation, blob file generation, table cache verification, IO tracing, listeners, event logging, internal stats, thread-status IO reporting, sequence-number-to-time mapping, and version metadata. `BuildTable()` is declared in `db/builder.h` and is called by flush/recovery paths and related table-materialization code. It also cooperates with `Version`/`ColumnFamilyData` for blob fetching during flush/recovery and range-deletion size approximation.

## Risks And Edge Cases
The function must correctly handle empty input with only tombstones, builder errors that leave `s` OK, iterator errors after output work, IO status vs logical status precedence, blob builder abandonment after table failure, and cleanup of files that were created but must not enter the version set. Preferred-seqno rewriting depends on `SeqnoToTimeMapping` and must preserve metadata bounds. Flush-time filters must have `IgnoreSnapshots() == true`; otherwise table creation is rejected. Blob garbage accounting is only enabled when the caller supplies `blob_file_garbages`, and correctness depends on tracking both input and surviving output blob references.

## Test Signals
Direct test hooks include sync points such as `BuildTable:create_file`, `BuildTable:BeforeFinishBuildTable`, `BuildTable:BeforeCheckEmpty`, `BuildTable:BeforeSyncTable`, `BuildTable:BeforeCloseTableFile`, `BuildTable:BeforeOutputValidation`, and `BuildTable:BeforeDeleteFile`. Broader coverage comes from RocksDB flush, recovery, compaction, table-cache, blob, range-deletion, checksum, timestamp, and fault-injection tests. The blob direct-write and blob-index suites in this subset exercise related blob metadata, filter, garbage, and readback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.h -->
# sources/storage-engines/rocksdb/db/builder.h

## Purpose
Declares RocksDB table-building entry points shared by flush, recovery, and compaction-output code. The header exposes the `BuildTable()` contract and small helpers for table builder creation and timestamp metadata extraction.

## Important APIs, Types, And Functions
`TableBuilder* NewTableBuilder(const TableBuilderOptions& tboptions, WritableFileWriter* file)` creates a table builder from the configured table factory. `void ExtractTimestampFromTableProperties(const TableProperties& tp, FileMetaData* meta)` copies timestamp table properties into file metadata. `Status BuildTable(...)` has a wide signature carrying DB name, `VersionSet`, immutable/table/file options, `TableCache`, input iterator, range tombstone iterators, output `FileMetaData`, optional blob additions/garbage, snapshots and snapshot checking, paranoid checks, stats, IO status, IO tracing, blob creation reason, seqno-time mapping, event logging, write lifetime hints, full-history timestamp bounds, blob completion callbacks, current version, payload/garbage counters, flush stats, and fast-SST-open output metadata.

## Control Flow
The header documents the high-level contract: build a table from `iter`, name it by `meta`'s file number, fill the remaining metadata on success, and set `meta->file_size` to zero without producing a table when no data is present. The declaration makes optional outputs explicit by nullable pointers; callers choose which integration lanes, such as blob metadata, table properties, flush stats, or fast-open metadata, they need.

## State And Persistence Behavior
`BuildTable()` mutates `FileMetaData` and optional out-parameters and may create persistent SST/blob files. The header-level contract establishes that zero file size is the sentinel for no produced table. Optional blob vectors are used to communicate manifest-relevant blob additions and garbage to the caller.

## Dependencies And Integration Points
The header includes internal stats, range tombstone fragmentation, seqno-time mapping, table property collectors, version metadata, event logging, column-family options, comparators, env/file APIs, listeners, statuses, table properties, and RocksDB types. Forward declarations keep implementation dependencies lighter while exposing integration with `BlobFileAddition`, `BlobFileGarbage`, `SnapshotChecker`, `TableCache`, `TableBuilder`, `WritableFileWriter`, `BlobFileCompletionCallback`, and `Version`.

## Risks And Edge Cases
The large parameter list is powerful but error-prone: pointer nullability controls behavior, and callers must keep snapshot vectors, timestamp bounds, blob vectors, version pointers, and stats outputs consistent with the table creation reason. Misconfigured options can cause `BuildTable()` to create files with metadata the caller does not record, or skip accounting lanes such as blob garbage. Callers must inspect both returned `Status` and `meta->fd.file_size`.

## Test Signals
Testing is primarily through callers of `BuildTable()` rather than the header. Useful signals include empty-input behavior, metadata population, timestamp property extraction, blob addition/garbage propagation, paranoid file verification, IO error propagation through `IOStatus`, and listener/event-log notifications.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.h -->
