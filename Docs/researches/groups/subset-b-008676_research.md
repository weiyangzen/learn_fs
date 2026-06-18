# subset-b-008676 Research

Grouped research report for RocksDB block-based table reader implementation and headers. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.cc -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.cc

## Purpose
Implements the concrete `BlockBasedTable` reader for RocksDB SST files in block-based format. The file owns table open-time metadata loading, tail prefetch, block cache lookup and insertion, direct file reads, decompression, filter and index construction, point lookup, iterator creation, table prefetch, checksum verification, cache eviction for obsolete files, approximate size/offset estimation, table dumping, and diagnostic test helpers.

## Important APIs, Types, And Functions
Top-level read-scoped buffer helpers include `AllocateReadScopedBlockBuffer`, `AllocateReadScopedAlignedBuffer`, `MakeReadScopedAlignedBufferAllocator`, `GetReadScopedBlockBufferProvider`, `ShouldUseDataBlockCacheForIterator`, `CopyBufferToHeapBlockContents`, and `CopyBufferToReadScopedBlockContents`. They validate caller-provided read-scope storage and route iterator data-block reads away from shared cache when that alternate backing is configured.

`BlockBasedTable::Open` is the central construction path. It reads the footer, metaindex, table properties, range deletion block, compression metadata, index reader, filter reader, user-defined index, and optional uncompression dictionary. It also sets stable cache keys, persistent cache options, timestamp bounds, global sequence number, table prefix extractor, block create context, and table-reader cache reservation state. `PrefetchTail`, `ReadMetaIndexBlock`, `ReadPropertiesBlock`, `ReadRangeDelBlock`, `PrefetchIndexAndFilterBlocks`, `CreateIndexReader`, and `CreateFilterBlockReader` are the main open-time subroutines.

The block access core is `ReadAndParseBlockFromFile`, `GetDataBlockFromCache`, `PutDataBlockToCache`, `MaybeReadBlockAndLoadToCache`, `RetrieveBlock`, `LookupAndPinBlocksInCache`, and `CreateAndPinBlockInCache`. These template paths cover data blocks, index blocks, full and partitioned filters, filter partition indexes, range deletion blocks, compression dictionaries, metaindex blocks, and user-defined indexes.

Read APIs implemented here include `NewIterator`, `NewRangeTombstoneIterator`, `PrefixRangeMayMatch`, `FullFilterKeyMayMatch`, `FullFilterKeysMayMatch`, `Get`, `MultiGetFilter`, `Prefetch`, `VerifyChecksum`, `ApproximateOffsetOf`, `ApproximateSize`, `ApproximateKeyAnchors`, `GetKVPairsFromDataBlocks`, and `DumpTable`. Cache and diagnostics APIs include `SetupBaseCacheKey`, `GetCacheKey`, `UpdateCacheHitMetrics`, `UpdateCacheMissMetrics`, `UpdateCacheInsertionMetrics`, `EraseFromCache`, `MarkObsolete`, `TEST_BlockInCache`, `TEST_KeyInCache`, `TEST_GetDataBlockHandle`, `TEST_FilterBlockInCache`, and `TEST_IndexBlockInCache`.

## Control Flow
Open starts with a reduced copy of `ReadOptions`, computes whether metadata should be prefetched and pinned, and either filesystem-prefetches or fills a `FilePrefetchBuffer` for the file tail. It reads and validates the footer, rejects unsupported format versions, allocates `Rep`, reads the metaindex and properties, configures decompression from the `compression_name` property, verifies any expected SST unique ID, derives prefix extractor compatibility, establishes cache keys, then reads range tombstones and prefetches or pins index/filter/dictionary dependencies. Success transfers the newly allocated `BlockBasedTable` into the caller's `TableReader` pointer.

Point `Get` first applies table-level timestamp pruning, then consults a full or prefix filter unless filters are skipped. If the filter may match, it seeks the index to the internal key, handles `first_internal_key` boundaries, constructs a data-block iterator for each candidate block, and calls `GetContext::SaveValue` until the key is resolved, an error occurs, or the search can stop. The read path writes block cache trace records with referenced key and data-size context when tracing is enabled.

Generic block retrieval first optionally checks block cache using a stable `CacheKey`. If the requested read is cache-only and the block is not cached, `RetrieveBlock` returns `Status::Incomplete`. Otherwise it uses `BlockFetcher` to read and optionally decompress bytes, using persistent cache, direct I/O, file prefetch, read-scoped provider storage, and checksum verification according to options. When `fill_cache` is true, blocks are inserted through `PutDataBlockToCache`; otherwise parsed block ownership remains local to the `CachableEntry`.

Iterator creation creates an index iterator, computes whether prefix seek should be disabled for hash indexes, and returns a `BlockBasedTableIterator` either on heap or arena. `PrefixRangeMayMatch` uses the table prefix extractor when compatible and delegates to the filter's `RangeMayExist`. `Prefetch` scans index handles over a key range and loads the corresponding data blocks. `VerifyChecksum` rereads the metaindex, all metadata blocks, and then all data blocks through a prefetch buffer.

## State And Persistence Behavior
The reader does not modify SST contents. It constructs in-memory immutable state in `Rep`: file reader, footer, properties, base cache key, persistent cache options, index reader, filter reader, uncompression dictionary reader, range tombstone fragments, table timestamp bounds, global sequence number, decompressor, block layout flags, and table option snapshots. It can insert parsed blocks and metadata into the configured block cache and persistent cache, and it can evict block cache entries when `MarkObsolete` has set `uncache_aggressiveness` before destruction.

Range deletion state is loaded into a shared `FragmentedRangeTombstoneList`. Cache-reservation state is held by `table_reader_cache_res_handle`. The only mutable long-lived field in `Rep` is the relaxed atomic obsolete-cache aggressiveness marker. Metrics and tracing update RocksDB statistics, perf counters, `GetContext` stats, and block cache trace files but not table data.

## Dependencies And Integration Points
This implementation depends on `RandomAccessFileReader`, `FilePrefetchBuffer`, `BlockFetcher`, block cache typed interfaces, persistent cache helpers, table properties readers, filter readers, binary/hash/partitioned index readers, user-defined index wrappers, range tombstone fragmentation, `GetContext`, `MultiGetContext`, comparators and timestamp APIs, compression managers, cache reservation managers, perf counters, sync points, and block cache tracing.

It is constructed by table cache and table factory code and consumed by DB reads, iterators, compaction reads, verification, backup/checksum paths, SST dump tooling, cache dump/load tooling, and tests. It cooperates with `block_based_table_reader_sync_and_async.h` for sync and coroutine `MultiGet` implementations and with `block_based_table_reader_impl.h` for template iterator helpers used by other headers.

## Risks And Edge Cases
The file is a hot path and mixes many cross-cutting concerns: cache tiers, direct I/O, mmap, persistent cache, async reads, dictionary compression, user-defined timestamps, global sequence numbers, old format versions, partitioned metadata, and tracing. Small mistakes can cause silent false negatives in reads, extra I/O under cache-only reads, pinned-value lifetime bugs, cache-key collisions, checksum verification gaps, or memory ownership errors.

Open-time metadata decisions are subtle. `avoid_shared_metadata_cache` must prevent shared cache insertion, while L0 pinning and prefetch heuristics must still avoid excessive I/O. `GetDecompressor` must reject malformed compression-manager properties while still supporting legacy compression names. Hash index routing depends on prefix extractor compatibility. Timestamp pruning uses only the table min timestamp in this file, so comparator timestamp semantics must remain consistent with table-property encoding.

The destructor's cache eviction avoids mmap because of a documented bus-error risk. `VerifyChecksumInMetaBlocks` deliberately skips index checksum rechecks in one open-verified case and has a FIXME around partition checksum coverage. `DumpTable` does raw diagnostic reads and must preserve stream error reporting. Read-scoped buffers must be valid, aligned, and kept alive through cleanup or direct I/O can write into invalid storage.

## Test Signals
Primary direct coverage is in `sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_test.cc`, including iterator reads, `VerifyChecksum`, checksum mismatch, cache probes, MultiScan behavior, first-internal-key boundaries, async I/O parameterization, prefetch-size limits, and file-system prefetch support initialization. `sources/storage-engines/rocksdb/file/prefetch_test.cc` exercises tail prefetch sizing and sync points such as `BlockBasedTable::Open::TailPrefetchLen`. `sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc` calls table reader checksum verification. Broader DB, cache, tiered-secondary-cache, user-defined-index, timestamp, and stress tests exercise the integration paths through the public DB and table factory APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.h -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.h

## Purpose
Declares the `BlockBasedTable` `TableReader` implementation and the shared helper surface for RocksDB's block-based SST reader. The header defines the public table-reader API, cache and block retrieval helpers, index-reader abstraction, metadata prefetch hooks, checksum and dumping hooks, read-scoped buffer helper declarations, and the `Rep` state container used by the implementation and closely coupled block-based reader components.

## Important APIs, Types, And Functions
The free helper declarations cover read-scoped allocation and cache policy: `AllocateReadScopedBlockBuffer`, `AllocateReadScopedAlignedBuffer`, `MakeReadScopedAlignedBufferAllocator`, `GetReadScopedBlockBufferProvider`, `ShouldUseDataBlockCacheForIterator`, `CopyBufferToHeapBlockContents`, and `CopyBufferToReadScopedBlockContents`.

`BlockBasedTable` exports `Open`, `PrefixRangeMayMatch`, `NewIterator`, `NewRangeTombstoneIterator`, `Get`, `MultiGetFilter`, sync and async `MultiGet`, `Prefetch`, approximate offset/size/key-anchor APIs, cache probes and erasure helpers, compaction setup, table properties access, sequence-to-time mapping access, memory usage, table dumping, checksum verification, and obsolete marking.

The nested `IndexReader` interface abstracts binary-search, hash, partitioned, and user-defined index readers through `NewIterator`, `ApproximateMemoryUsage`, `CacheDependencies`, and `EraseFromCacheBeforeDestruction`. Private templates declare `LookupAndPinBlocksInCache`, `CreateAndPinBlockInCache`, `NewDataBlockIterator`, `MaybeReadBlockAndLoadToCache`, `RetrieveBlock`, `SaveLookupContextOrTraceRecord`, `GetDataBlockFromCache`, and `PutDataBlockToCache`.

`PartitionedIndexIteratorState` adapts partitioned-index block maps into `TwoLevelIteratorState`. `Rep` stores immutable table reader state: options, file, cache keys, footer, metadata readers, filter/dictionary/index handles, table properties, sequence mapping, index encoding flags, range tombstones, decompressor, restart intervals, separated key/value mode, checksum-open marker, timestamp persistence flag, filesystem prefetch support, obsolete-cache aggressiveness, cache reservation handle, and optional user-defined-index block.

## Control Flow
The header establishes the layering: external callers use `TableReader` virtual methods, the implementation routes metadata access through `IndexReader` and `FilterBlockReader`, and block materialization flows through typed `CachableEntry` templates. `DECLARE_SYNC_AND_ASYNC_OVERRIDE` and `DECLARE_SYNC_AND_ASYNC_CONST` declare paired sync/coroutine versions of `MultiGet` and `RetrieveMultipleBlocks`; the implementation header is included with different coroutine macros to generate both variants.

Index lookup starts with `NewIndexIterator`, then data-block conversion is done by `NewDataBlockIterator`. Cache decisions are centralized through `RetrieveBlock`, `MaybeReadBlockAndLoadToCache`, and typed block cache helpers. Open-time construction flows through `PrefetchTail`, `ReadMetaIndexBlock`, `ReadPropertiesBlock`, `ReadRangeDelBlock`, `PrefetchIndexAndFilterBlocks`, `CreateIndexReader`, and `CreateFilterBlockReader`.

## State And Persistence Behavior
The header is declarative, but it documents the state that persists for a table reader lifetime. `Rep` holds a moved-in random access file, table metadata, constructed readers, cache identity, timestamp and global sequence settings, and ownership handles for cache reservation and user-defined-index data. It does not declare any mutation of the SST itself. Cache persistence is external to the table reader and keyed through `base_cache_key` plus block offsets.

`Rep::get_global_seqno` disables global sequence numbers for filter partition index and compression dictionary blocks. `CreateFilePrefetchBuffer` and `CreateFilePrefetchBufferIfNotExists` centralize per-reader file prefetch buffer construction. `uncache_aggressiveness` is an atomic marker used later during destruction to evict cached blocks for obsolete files.

## Dependencies And Integration Points
The declarations tie together RocksDB cache roles and keys, block cache interfaces, range tombstone fragmenters, sequence-to-time mappings, table properties, block-based table options, filters, uncompression dictionaries, persistent cache, table format, two-level iterators, block cache tracing, aligned buffers, coroutine utilities, and hash containers.

Other block-based table files depend on this header for template methods and `Rep` details. Table cache, table factory, iterators, filter readers, partitioned index readers, user-defined index wrappers, compaction code, SST dump tooling, and tests all integrate through the API declared here.

## Risks And Edge Cases
The header exposes many implementation details for template and friend access, so changes to `Rep`, block type mapping, or template signatures can break distant block-based components. `ReadOptions` lifetime is explicitly required to outlive iterators. The `IndexReader::NewIterator` contract allows returning a different iterator than the caller supplied, so callers must preserve both ownership and stack lifetime correctly.

Cache key setup depends on table properties for stable identity and falls back to current DB session and file number for older files. The `BlockSizeWithTrailer` and compression-type helpers assume block-based serialized contents with the expected trailer. User-defined timestamps can be absent in persisted keys even when the active comparator has timestamp size, so parsing code must consult `user_defined_timestamps_persisted`.

## Test Signals
Tests that instantiate `BlockBasedTable` and exercise the declared APIs are concentrated in `table/block_based/block_based_table_reader_test.cc`, with parameterization over compression, index type, cache presence, direct reads, async I/O, timestamps, and block alignment. Cache-specific APIs are indirectly covered by cache and tiered-cache tests. Public `TableReader` methods are also exercised by DB read, iterator, compaction, checksum, SST dump, and fuzz tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_impl.h -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_impl.h

## Purpose
Provides template implementations of `BlockBasedTable::NewDataBlockIterator` that must remain visible to other headers, especially block-based iterator code. It converts data, index, and range-deletion block handles or preloaded `CachableEntry<Block>` objects into typed block iterators while preserving cache handles, ownership cleanup, block pinning semantics, dictionary decompression, read-scoped cache policy, and dummy cache accounting for non-filled reads.

## Important APIs, Types, And Functions
The file defines local `IterTraits` specializations mapping `DataBlockIter` to `Block_kData` and `IndexBlockIter` to `Block_kIndex`. It aliases `IterPlaceholderCacheInterface` for dummy `CacheEntryRole::kMisc` insertions used to track memory usage when a block is not inserted into the real data cache because `fill_cache` is false.

The first `NewDataBlockIterator` overload accepts a `BlockHandle`, block type, optional existing iterator, read context, block cache lookup context, file prefetch buffer, compaction and async flags, a mutable `Status`, and a `use_block_cache_for_lookup` flag. The second overload accepts an already loaded `CachableEntry<Block>` and initializes a data iterator from it.

## Control Flow
For handle-based reads, the template allocates or reuses the requested iterator and returns an invalidated iterator immediately if the incoming status is already bad. For data blocks with a configured uncompression dictionary reader, it reads or pins the dictionary first, avoiding prefetch-buffer use during async scans and auto-readahead because those patterns can conflict with in-flight prefetch or sequential access assumptions. It then calls `RetrieveBlock` with either range-deletion specialization or the trait-selected blocklike type.

If async reading returns `Status::TryAgain`, the iterator is returned without initialization so the caller can resume after asynchronous I/O. Non-OK statuses invalidate the iterator. Successful reads assert separated key/value consistency, decide whether block contents are pinned by cache handle or immortal table backing, initialize the typed iterator through `InitBlockIterator`, attach cache handles for cached blocks, optionally inserts a dummy placeholder cache record when `fill_cache` is false, and transfers `CachableEntry` ownership and cleanup to the iterator.

For preloaded blocks, the same pinning, iterator initialization, dummy placeholder insertion, cache-handle attachment, and ownership transfer logic applies without file or cache lookup.

## State And Persistence Behavior
The template does not persist data. It moves block ownership, block cache handles, and cleanup callbacks from `CachableEntry` into iterators. A cached block remains pinned until iterator cleanup releases the cache handle. An uncached block backed by an immortal table can be treated as pinned when it does not own bytes. When `fill_cache` is false, the dummy placeholder cache entry records approximate memory usage and is released through iterator cleanup.

## Dependencies And Integration Points
This header depends on `block.h`, `block_cache.h`, `block_based_table_reader.h`, and `reader_common.h`. It calls `UncompressionDictReader::GetOrReadUncompressionDictionary`, `ShouldUseDataBlockCacheForIterator`, `RetrieveBlock`, `InitBlockIterator`, `ForceReleaseCachedEntry`, and typed `CachableEntry` APIs. It is used by table iterators, point lookup, prefetch, checksum/dump helpers, range tombstone loading, and MultiGet materialization paths.

## Risks And Edge Cases
Iterator lifetime is tightly coupled to cache cleanup transfer. Losing a cleanup, attaching the wrong cache handle, or misclassifying pinned block contents can cause use-after-free, leaks, or over-retention. Async `TryAgain` must not initialize from incomplete block contents. Dictionary reads must not disturb async prefetch buffers. Range deletion blocks force cache use separately from normal iterator data-block cache policy. The dummy cache accounting path must be best-effort and must not turn a failed accounting insert into a read failure.

## Test Signals
The behavior is covered indirectly by `block_based_table_reader_test.cc` iterator, range tombstone, MultiScan, cache, and checksum tests; DB iterator and point lookup tests; prefetch tests; and stress tests with compression dictionaries, direct reads, async reads, and `fill_cache=false`. Cache memory accounting regressions would show up through block cache usage and pinned-value lifetime tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_sync_and_async.h -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_sync_and_async.h

## Purpose
Defines the sync and coroutine variants of `BlockBasedTable::RetrieveMultipleBlocks` and `BlockBasedTable::MultiGet`. The file is included twice from `block_based_table_reader.cc` under different coroutine macros, allowing one implementation body to generate blocking and async-capable versions of batched point-read logic.

## Important APIs, Types, And Functions
`RetrieveMultipleBlocks` performs batched data-block reads for `MultiGet`, using `Env::MultiRead` or coroutine `MultiReadAsync`, optional shared scratch memory, direct-I/O buffers, filesystem-provided scratch buffers, checksum verification, corruption reconstruction retry, and cache insertion through `CreateAndPinBlockInCache`.

`MultiGet` implements table-level batched lookup. It applies full or prefix filters to a `MultiGetRange`, seeks the index for each surviving key, groups repeated block handles, issues async block cache lookups, batches disk reads for misses, initializes data block iterators, calls each key's `GetContext::SaveValue`, manages pinned value cleanup when multiple keys reuse the same block, records filter and cache metrics, and writes block cache trace records when enabled.

## Control Flow
`RetrieveMultipleBlocks` first handles mmap reads by falling back to individual `RetrieveBlock` calls. For non-mmap reads, it builds `FSReadRequest` entries from non-null block handles. Adjacent blocks can be combined into one read when using shared scratch or filesystem scratch and not using direct I/O. Requests either point into caller scratch, allocate per-request heap scratch, leave scratch null for direct I/O or filesystem buffers, or later use an `AlignedBuffer` allocation context. The sync path calls `file->MultiRead`; the coroutine path awaits `batch->context()->reader().MultiReadAsync` when not using direct I/O.

After I/O, each request is validated for truncation, wrapped into `BlockContents`, optionally checksum-verified, and retried with `verify_and_reconstruct_read` when checksum corruption is detected and the filesystem supports reconstruction. Good blocks are parsed and inserted or pinned through `CreateAndPinBlockInCache`. Filesystem scratch buffers are explicitly reset after combined reads.

`MultiGet` begins by rejecting empty batches, applying filters, and building an index iterator with hash-prefix compatibility checks. It then scans the filtered range, seeking the index for each key, rejecting keys that fall before a block's `first_internal_key`, lazily loading the uncompression dictionary, marking repeated block offsets with null handles, and starting async block cache lookups for unique handles. Cache hits populate result entries; misses contribute to the cumulative read length. Misses are read with `RetrieveMultipleBlocks`, using stack scratch for small compressed batches, heap scratch for larger ones, filesystem scratch when supported, or direct-I/O handling as required.

Finally, `MultiGet` walks the surviving keys, reuses loaded blocks where possible, creates `DataBlockIter` instances, honors cache-only `Status::Incomplete` by marking keys as may-exist, saves values through `GetContext`, handles merge/value pinning cleanup sharing for reused blocks, scans following blocks when needed, updates filter true-positive counters, and stores per-key statuses.

## State And Persistence Behavior
The file does not alter SST persistence. It mutates per-call `MultiGetRange` state by skipping filtered or resolved keys and writing each key's status. It fills temporary arrays of block handles, statuses, `CachableEntry<Block_kData>`, async cache handles, cache keys, and lookup contexts. It can insert blocks into block cache, increment per-read `GetContext` stats, record perf counters, and write block cache trace records.

Pinned value state is managed through `SharedCleanablePtr` when adjacent keys reuse a block. This avoids extra block cache references while ensuring a cached block is released only after all returned pinned values are done. Scratch buffers are stack, heap, direct-I/O, or filesystem-owned depending on block compression, file mode, and filesystem features.

## Dependencies And Integration Points
The implementation depends on coroutine macros from `util/coro_utils.h`, `AlignedBuffer`, `AsyncFileReader`, `RandomAccessFileReader::MultiRead`, `MultiGetContext`, `BlockCacheInterface`, `BlockCreateContext`, `UncompressionDictReader`, `CreateAndPinBlockInCache`, `NewDataBlockIterator`, filter readers, index iterators, checksum utilities, filesystem feature detection, `GetContext`, and block cache tracing.

It is compiled into both regular and async table reader methods. DB batched point reads, async I/O experiments, tiered/secondary cache paths, direct I/O reads, and block cache tracing all depend on this code staying behaviorally aligned between sync and coroutine expansion.

## Risks And Edge Cases
Batch ordering and index-to-result mapping are fragile because null handles represent both skipped reused blocks and already cached blocks. `reused_mask`, `idx_in_batch`, cache lookup indexes, request indexes, and skipped `MultiGetRange` entries must stay aligned. Combined reads must compute offsets correctly or checksum and block parsing will read the wrong bytes. Direct I/O, filesystem scratch, heap scratch, and compressed-block paths each have different ownership rules.

Cache-only reads must return may-exist rather than false negatives. User-defined timestamps prevent early stop on some hash-seek misses. `first_internal_key` boundary checks must avoid scanning blocks that cannot contain the key. Shared cleanup for reused pinned blocks must not double-release or miss a release. The comment notes some break paths can bypass data-block trace record writing, which is a diagnostic completeness risk.

## Test Signals
`block_based_table_reader_test.cc` contains `BlockBasedTableReaderGetTest`, MultiScan and async MultiScan parameterized tests, first-internal-key boundary tests, prefetch-size and unpin-previous-block tests, and cache-related assertions that exercise much of this machinery. DB-level `MultiGet` tests, tiered secondary cache tests, direct I/O tests, read-scoped block buffer provider stress flags, corruption/checksum tests, and async I/O builds provide additional coverage. A key regression signal is mismatch between sync and coroutine behavior because both are generated from this one header.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_sync_and_async.h -->
