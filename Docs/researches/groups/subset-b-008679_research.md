# subset-b-008679 Research

Grouped research report for the requested RocksDB table/block-based and cuckoo table source files. Each section preserves the source path in its title and is delimited for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.h -->
# sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.h

Purpose: declares `MultiScanIndexIterator`, an `InternalIteratorBase<IndexValue>` adapter over a prepared vector of data block handles and per-scan block ranges. Its role is to let `BlockBasedTableIterator` reuse ordinary index-iterator seek and block-finding logic for MultiScan requests rather than adding a separate scan-specific data block path.

Important APIs/types/functions: the constructor takes moved `BlockHandle` and separator vectors, `block_index_ranges_per_scan`, a borrowed `MultiScanArgs`, shared `ReadSet`, prefetch limit, `InternalKeyComparator`, and optional `Statistics`. Public iterator operations include forward-only `Seek`, `Next`, `SeekToFirst`, `Valid`, `key`, `user_key`, `value`, `status`, `current_read_set_index`, `GetMaxPrefetchSize`, `IsScanRangeExhausted`, and `HasMoreScanRanges`. Reverse methods are declared unsupported and invalidate the iterator. Private helpers release skipped prefetched blocks, locate a block for unexpected seek targets, position by index, and mark scan ranges exhausted.

Control flow: callers prepare block metadata elsewhere, then this iterator walks only within the current scan range. `Next` advances block indexes and jumps to the next scan range at range end. `Seek` must be monotonic by `prev_seek_key_`; non-monotonic behavior would violate the forward-only contract and can produce incorrect release/prefetch accounting.

State and persistence: no durable state is written. Runtime state tracks current block index, next scan index, validity, previous seek key, wasted prefetched blocks, and a mutable internal-key buffer synthesized from the current separator plus max sequence number. `ReadSet` is shared and likely owns per-block read/prefetch lifecycle state.

Dependencies/integration: depends on RocksDB internal key encoding, `ReadSet`, `MultiScanArgs`, `InternalKeyComparator`, and table iterator code expecting `IndexValue`. The value intentionally carries an empty first internal key, disabling the first-key-from-index optimization.

Risks and test signals: risk is concentrated in monotonic seek enforcement, releasing skipped blocks exactly once, scan boundary reporting, and lifetime assumptions for borrowed `scan_opts`/`icomp`. This header has no direct tests in the subset; coverage likely comes from MultiScan table iterator tests outside this item.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.cc -->
# sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.cc

Purpose: implements the small owning wrapper for a parsed full filter block. The file turns `BlockContents` loaded from an SST filter block into an object carrying both the raw contents and a `FilterBitsReader` produced by the configured filter policy.

Important APIs/types/functions: `ParsedFullFilterBlock::ParsedFullFilterBlock(const FilterPolicy*, BlockContents&&)` moves the contents into `block_contents_` and initializes `filter_bits_reader_` with `filter_policy->GetFilterBitsReader(block_contents_.data)` when the data slice is non-empty. The destructor is defaulted out-of-line.

Control flow: construction is a single parse step: accept contents, test empty data, call the filter policy factory for a bits reader, or leave the reader null for an empty block. There is no later mutation in this implementation file.

State and persistence: the object owns or references bytes according to the moved `BlockContents` ownership mode. It does not persist anything itself; it is the cacheable in-memory representation of persisted filter block bytes.

Dependencies/integration: it includes `filter_policy_internal.h` for `FilterBitsReader` construction and is used by full and partitioned filter readers. Partitioned filter readers cache `ParsedFullFilterBlock` entries by block offset and wrap them in `FullFilterBlockReader` for actual `KeyMayMatch`/`PrefixMayMatch` probes.

Risks and test signals: callers must pass a non-null `FilterPolicy` whenever the block is non-empty. Empty blocks produce a null reader, so downstream code must preserve the convention that empty filters are treated as may-match rather than dereferencing blindly. The partitioned filter tests in this subset exercise construction indirectly through mocked cached partition blocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.h -->
# sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.h

Purpose: declares the shareable/cacheable in-memory representation of a full filter block. It separates parsing and ownership of filter block contents from readers that execute membership tests.

Important APIs/types/functions: `ParsedFullFilterBlock` exposes `filter_bits_reader()`, `ApproximateMemoryUsage()`, `own_bytes()`, `ContentSlice()`, and typed cache constants `kCacheEntryRole = kFilterBlock` and `kBlockType = kFilter`. It owns a `BlockContents` and a `std::unique_ptr<FilterBitsReader>`.

Control flow: construction is in the `.cc`; after construction, readers only query accessors. `ApproximateMemoryUsage` delegates to the underlying `BlockContents` and explicitly does not include `FilterBitsReader` memory, as called out by TODO.

State and persistence: the persisted state is the raw filter block bytes in the SST. This class owns or references those bytes according to `BlockContents`, and holds transient parsed reader state for cache reuse. `ContentSlice()` lets typed cache infrastructure key or charge the raw content slice.

Dependencies/integration: depends on `BlockContents`, `BlockType`, and filter policy abstractions. It is used as `CachableEntry<ParsedFullFilterBlock>` in partitioned filters and likely full filters; the static role/type constants integrate with RocksDB block cache accounting.

Risks and test signals: memory accounting is incomplete for the reader object, which can understate pinned filter memory. Ownership mode matters because cached unowned values are exposed by `SetUnownedValue` in partitioned filter code. Direct tests are absent here, but `partitioned_filter_block_test.cc` creates `ParsedFullFilterBlock` instances for mocked filter partitions and validates filter behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.cc -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.cc

Purpose: implements building and reading of partitioned full filters for block-based tables. The builder emits multiple filter partition blocks plus a top-level filter-partition index. The reader resolves a key or prefix to the right partition and delegates membership testing to `FullFilterBlockReader`.

Important APIs/types/functions: `PartitionedFilterBlockBuilder` implements `Add`, `AddWithPrevKey`, `PrevKeyBeforeFinish`, `Finish`, `EstimateEntriesAdded`, `CurrentFilterSizeEstimate`, and data-block-finalization size updates. Internal helpers `DecideCutAFilterBlock`, `CutAFilterBlock`, and `AddImpl` control partition boundaries. `PartitionedFilterBlockReader` implements `Create`, `KeyMayMatch`, `KeysMayMatch`, `PrefixMayMatch`, `PrefixesMayMatch`, partition handle lookup, partition block retrieval, dependency caching, and cache erasure.

Control flow: the builder computes `keys_per_partition_` from target metadata block size and filter-policy estimates. On each key, it may request/cut according to either decoupled filter partition size or the associated `PartitionedIndexBuilder`. Cutting may add the next prefix to the closing partition and previous prefix to the new partition, preserving prefix seek correctness around partition boundaries. `Finish` is multi-phase: first calls return individual partition slices with `Status::Incomplete`; later calls receive the last written partition handle, add it to the top-level index, and eventually return the top-level filter index slice or empty slice.

State and persistence: persisted output consists of filter partition blocks and a top-level index keyed by either internal separators or user keys, with optional value delta encoding. In-memory state includes a deque of pending partition entries, atomic completed size accounting for parallel compression, construction status, previous key state, two index builders, and last encoded block handle.

Dependencies/integration: tightly coupled with `FullFilterBlockBuilder`, `PartitionedIndexBuilder`, `BlockBuilder`, filter policy builders, timestamp/key encoding helpers, `BlockBasedTable::RetrieveBlock`, block cache lookup contexts, file prefetch buffers, and table reader cache-dependency hooks.

Risks and test signals: correctness risks include prefix false negatives at partition edges, timestamp stripping/persistence mismatches, incomplete `Finish` sequencing, cache pinning subset behavior, and assuming partition blocks are consecutive for prefetch. On read errors, filters conservatively return may-match. Tests cover empty builders, one/two/all key grouping, partition counts, prefix boundary bugs, format versions 2/latest, user-defined timestamp modes, and coupled versus decoupled partitioning.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.h -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.h

Purpose: declares the partitioned filter builder/reader interfaces used by block-based SST construction and reads. It is the public local contract between table building, filter policy code, partitioned index construction, and table-reader filter lookups.

Important APIs/types/functions: `PartitionedFilterBlockBuilder` derives from `FullFilterBlockBuilder` and overrides key addition, empty checks, size estimates, data-block-finalization updates, finish/previous-key hooks, reset, and post-verification behavior. It owns `FilterEntry` records containing separator/internal key, filter owner, and slice. `PartitionedFilterBlockReader` derives from `FilterBlockReaderCommon<Block_kFilterPartitionIndex>` and overrides single-key, multiget, prefix, memory, cache dependency, and cache erase operations.

Control flow: the header reveals a two-level build contract. Filter partitions are queued in `filters_`; `Finish` alternates between returning a partition and consuming the handle of the previously written partition before producing the top-level index. Reader flow is top-level index lookup, partition block retrieval, then full-filter reader delegation.

State and persistence: builder state includes the partitioned index builder pointer, timestamp sizing, decoupling flag, atomic completed partition size, total built entries, construction status, debug previous-key validators, and top-level index builders for internal-key and user-key variants. Reader state includes `filter_map_`, a cache of pinned partition blocks keyed by offset.

Dependencies/integration: depends on `block_cache.h`, filter common readers, full filter block code, `PartitionedIndexBuilder`, `BlockBuilder`, timestamp-aware comparators, and cache entry wrappers. It also exposes typed cache behavior through inherited `FilterBlockReaderCommon`.

Risks and test signals: lifetime risk exists for the raw `PartitionedIndexBuilder*` and prefix extractor/filter bits builder inherited from full filters. Parallel compression requires atomic estimates and thread-safe update paths. The tests in `partitioned_filter_block_test.cc` are strong for functional partitioning but mostly use mocked in-memory block maps rather than real file/cache IO failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block_test.cc -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block_test.cc

Purpose: unit tests for partitioned filter construction and lookup behavior, including historical prefix-partition bugs and user-defined timestamp compatibility.

Important APIs/types/functions: the file defines a global `blooms` map to simulate partition block storage, `MockedBlockBasedTable` to initialize required `Rep` fields from `PartitionedIndexBuilder`, and `MyPartitionedFilterBlockReader` to prepopulate `filter_map_` with `ParsedFullFilterBlock` objects. `PartitionedFilterBlockTest` creates builders/readers, writes returned filter partitions to the map, and verifies `KeyMayMatch`/`PrefixMayMatch`.

Control flow: helpers prepare timestamp-adjusted keys, estimate max index/filter sizes, build partitioned index/filter builders, repeatedly call `Finish` until not incomplete, and construct a reader over the final top-level index block. Tests vary metadata block size to force one, two, per-key, or all-key partitions.

State and persistence: tests do not write real SST files. They mimic persisted filter partition blocks with offsets in `blooms`, while the top-level filter index is put in an in-memory `Block`. This isolates filter logic from file IO but still exercises handle encoding and index iteration.

Dependencies/integration: uses Bloom filter policy internals, partitioned index builder, block-based table `Rep`, internal key and timestamp helpers, fixed prefix transforms, and RocksDB test harness parameterization.

Risks and test signals: coverage is meaningful across format versions `{2,3,4,5,default,latest}`, all user-defined timestamp modes, and both `decouple_partitioned_filters` booleans. It explicitly guards same-prefix-across-blocks and prefix-in-wrong-partition regressions. Gaps include real block cache insertion failures, prefetch/cache dependency paths, read-error fallback, and multiget partition grouping.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.cc -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.cc

Purpose: implements `PartitionedIndexIterator`, a two-level index iterator for partitioned block-based indexes when partition blocks are not pre-pinned into a map. It exposes a flattened stream of `IndexValue` entries from top-level index partitions.

Important APIs/types/functions: main operations are `Seek`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `SeekImpl`, `InitPartitionedIndexBlock`, `FindKeyForward`, `FindBlockForward`, and `FindKeyBackward`.

Control flow: `SeekImpl` saves the previous top-level block offset, positions the top-level index iterator, loads the pointed partition block, seeks inside it, then advances to the next non-empty partition if needed. `Next` advances the current partition iterator and calls `FindKeyForward`; if the partition is exhausted, `FindBlockForward` resets the partition iterator, advances the top-level iterator, loads the next partition, and seeks to first. Backward iteration mirrors this with `Prev`, `SeekToLast`, and `FindKeyBackward`.

State and persistence: no persistent writes. Runtime state is split between `index_iter_` for top-level partitions and `block_iter_` for the current index partition. `prev_block_offset_` avoids refetching the same partition on reseek, unless the previous read was incomplete. `BlockPrefetcher` carries readahead state.

Dependencies/integration: depends on `BlockBasedTable::NewDataBlockIterator`, `BlockPrefetcher`, `ReadOptions`, `BlockCacheLookupContext`, `IndexBlockIter`, and table `Rep` index metadata flags. It uses the table block cache path with `BlockType::kIndex`.

Risks and test signals: risks include stale `prev_block_offset_` reuse if handles share offsets unexpectedly, status propagation from partition iterators, skipped upper-bound checks, and readahead option handling. Direct tests are outside this subset; partitioned index behavior is indirectly exercised by partitioned filter tests through top-level index iteration and by block-based table reader tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.h -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.h

Purpose: declares the flattened iterator over a partitioned index. It lets block-based table iteration consume partitioned index blocks through the same `InternalIteratorBase<IndexValue>` interface used by non-partitioned indexes.

Important APIs/types/functions: constructor captures the table, read options, comparator, top-level index iterator, caller identity, and optional compaction readahead size. It implements seek/next/prev, validity, key/user-key/value/status, readahead state transfer, and `ResetPartitionedIndexIter`/`SavePrevIndexValue`.

Control flow: the header shows a two-level model: `index_iter_` points at partition handles, while `block_iter_` points at entries inside the current index partition. Private helpers load a partition and skip empty or invalid partitions forward/backward.

State and persistence: persistent data are index blocks already stored in the SST. The iterator tracks only live traversal state: current partition iterator validity, previous partition offset, lookup context, user comparator, and block prefetcher. Unsupported methods assert because table iterators should not call them in this role.

Dependencies/integration: includes block-based table reader internals, block prefetcher, and reader common definitions. `GetReadaheadState`/`SetReadaheadState` integrate adaptive readahead state with higher-level table readers.

Risks and test signals: unsupported methods returning assertions indicate a narrow integration contract. Status deliberately treats `NotFound` from prefix indexes as non-fatal. Upper-bound checks return unknown, so higher layers cannot rely on index-level bound pruning. Test signals are indirect through table reader and partitioned index tests outside this file; this subset includes reader code that constructs this iterator.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.cc -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.cc

Purpose: implements the `PartitionIndexReader`, which reads the top-level partitioned index block, creates iterators over partitioned indexes, preloads/pins index partitions, and erases index partitions from cache at table-reader teardown.

Important APIs/types/functions: `Create`, `NewIterator`, `CacheDependencies`, and `EraseFromCacheBeforeDestruction` are implemented here.

Control flow: `Create` optionally reads the top-level index block if prefetching or bypassing cache, then drops the entry if it was only preloaded and not pinned. `NewIterator` first gets the top-level block. If `partition_map_` is populated, it returns a generic two-level iterator backed by pinned blocks; otherwise it constructs a `PartitionedIndexIterator` with readahead reset to avoid a noted prefetch regression. `CacheDependencies` loads the top-level index, computes a contiguous byte range from first to last partition handle, prefetches that range if needed, reads each partition through `MaybeReadBlockAndLoadToCache`, and only publishes `partition_map_` if all partitions were available.

State and persistence: the reader persists nothing. It may hold pinned `CachableEntry<Block>` objects in `partition_map_` keyed by partition offset. All-or-nothing insertion prevents the pinned-map iterator from seeing missing partitions.

Dependencies/integration: relies on `IndexReaderCommon`, `ReadIndexBlock`, `GetOrReadIndexBlock`, `BlockBasedTable::MaybeReadBlockAndLoadToCache`, `PartitionedIndexIterator`, `NewTwoLevelIterator`, file prefetch buffers, and table `Rep` metadata.

Risks and test signals: assumes partition index blocks are consecutive on disk for prefetch range calculation. Empty top-level indexes are handled by returning iterator status. Cache erasure mirrors partitioned filters and depends on `UncacheAggressivenessAdvisor`. Direct tests are not in this subset, but block fetcher/table reader suites exercise block loading behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.h -->
# sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.h

Purpose: declares the partitioned-index reader used by block-based table readers for two-level index structures.

Important APIs/types/functions: `PartitionIndexReader` derives from `BlockBasedTable::IndexReaderCommon`. Public methods are static `Create`, `NewIterator`, `CacheDependencies`, `ApproximateMemoryUsage`, and `EraseFromCacheBeforeDestruction`. The private constructor takes a table pointer and top-level index `CachableEntry<Block>`.

Control flow: the declared contract is top-level index acquisition followed by either lazy partition reads during iteration or dependency caching/pinning before iteration. `NewIterator` returns an iterator whose first level is the partition index.

State and persistence: persistent input is the SST index metadata and partition index blocks. The reader may own or cache-reference the top-level index through the base class and may pin all index partitions in `partition_map_`. Approximate memory usage includes base index block usage plus object size, but only has a TODO for exact map memory.

Dependencies/integration: depends on `index_reader_common.h` and `UnorderedMap`. The reader is chosen by block-based table open logic when the table uses partitioned indexes, and its dependency caching is invoked by cache-index-and-filter-blocks/pin options.

Risks and test signals: all-or-none expectation for `partition_map_` is important; partial maps would make iterator logic unsafe. Memory usage undercounts the map. Direct tests are not present here, so coverage depends on block-based table reader tests, partitioned index tests elsewhere, and partitioned filter tests that reuse partitioned index builder semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/reader_common.cc -->
# sources/storage-engines/rocksdb/table/block_based/reader_common.cc

Purpose: implements small shared utilities for block-based table readers: forced cache release and checksum verification for physical blocks.

Important APIs/types/functions: `ForceReleaseCachedEntry(void*, void*)` casts arguments to `Cache` and `Cache::Handle` and releases with `erase_if_last_ref=true`. `VerifyBlockChecksum` checks the block trailer checksum using footer checksum settings, file name, block offset, and `BlockType`.

Control flow: checksum verification asserts the RocksDB block trailer size of five bytes, computes the checksum over block bytes plus compression type byte, decodes the stored checksum, removes the context checksum modifier based on footer base context and offset, compares, and returns either OK or a detailed corruption status. For CRC32c, it unmasks stored and computed values for diagnostics.

State and persistence: no persistent state is written. It consumes persisted trailer bytes and footer checksum metadata. `PERF_TIMER_GUARD(block_checksum_time)` records verification time in perf context.

Dependencies/integration: depends on `Footer`, checksum helpers in `util/crc32c`/`util/coding`, block type stringification, and perf context. `BlockFetcher::ProcessTrailerIfPresent` calls `VerifyBlockChecksum` when `ReadOptions::verify_checksums` is enabled.

Risks and test signals: the function assumes `data` includes a complete trailer after `block_size`, so callers must ensure full block-plus-trailer reads. Context checksum subtraction is subtle and affects diagnostic values. Block fetcher tests exercise successful reads and compression type handling, but this subset does not include explicit checksum mismatch tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/reader_common.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/reader_common.h -->
# sources/storage-engines/rocksdb/table/block_based/reader_common.h

Purpose: declares shared block-based table reader helpers used by block fetching, cache lifecycle, and checksum validation.

Important APIs/types/functions: `ForceReleaseCachedEntry` is a cleanup callback for cached entries. `GetMemoryAllocator` returns the block cache memory allocator from `BlockBasedTableOptions` when a block cache exists. `VerifyBlockChecksum` validates a block trailer and returns corruption diagnostics on mismatch.

Control flow: this header establishes the expected inputs for checksum verification: footer, data pointer, logical block size, file name, offset, and block type. It also documents that data must include the trailer bytes after the block data.

State and persistence: no state is declared. The functions operate on cache handles or read-only block bytes. `GetMemoryAllocator` exposes allocator configuration used by block read paths.

Dependencies/integration: includes `rocksdb/advanced_cache.h`, `rocksdb/table.h`, and `BlockType`. `BlockFetcher` and block cache wrappers depend on these declarations.

Risks and test signals: misuse risks include calling `ForceReleaseCachedEntry` with mismatched cache/handle arguments and passing an undersized buffer to checksum verification. Tests in this subset indirectly cover block fetch paths but not the release callback.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/reader_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.cc -->
# sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.cc

Purpose: implements an accessor for the compression dictionary block used to decompress table blocks. It abstracts whether the dictionary was prefetched/pinned into the reader or should be read from cache/file on demand.

Important APIs/types/functions: `Create`, `ReadUncompressionDictionary`, `GetOrReadUncompressionDictionary`, `ApproximateMemoryUsage`, and `cache_dictionary_blocks` are implemented here.

Control flow: `Create` optionally reads the dictionary when prefetching or when not using cache, and discards it if cache is enabled but pinning is not requested. `GetOrReadUncompressionDictionary` returns an unowned value when the reader already holds one, otherwise calls the static reader with a cache-use policy derived from table options. The static reader calls `BlockBasedTable::RetrieveBlock` with the table's `compression_dict_handle`.

State and persistence: the dictionary block is persisted in the SST and addressed by `Rep::compression_dict_handle`. In memory, the reader stores a `CachableEntry<DecompressorDict>` that can own, cache-reference, or be empty. Approximate memory includes owned dictionary memory plus object allocation size.

Dependencies/integration: depends on `BlockBasedTable`, `CachableEntry`, `DecompressorDict`, file prefetch buffers, block cache lookup contexts, and logging. Data block reads pass the resulting dictionary/decompressor state into block fetch/decompression code.

Risks and test signals: callers assert the compression dictionary handle is non-null before reading. Error handling logs warnings and returns status, so table open/read paths must decide whether a missing or corrupt dictionary is fatal. This subset lacks direct tests; block fetcher tests exercise decompression but not dictionary-backed compression.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.h -->
# sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.h

Purpose: declares `UncompressionDictReader`, the table-reader helper that provides access to an SST compression dictionary independent of ownership and cache pinning mode.

Important APIs/types/functions: static `Create`, public `GetOrReadUncompressionDictionary`, `ApproximateMemoryUsage`, private constructor, `cache_dictionary_blocks`, and static `ReadUncompressionDictionary`. The class stores the owning table pointer and a `CachableEntry<DecompressorDict>`.

Control flow: the class supports eager creation with optional prefetch/pin and lazy retrieval for later block reads. The static read routine centralizes the actual `RetrieveBlock` call so both creation and lazy reads follow the same path.

State and persistence: persisted state is only the dictionary block bytes in the SST. Runtime state is the cached/owned dictionary entry and the borrowed table pointer. The reader does not mutate table metadata.

Dependencies/integration: includes `cachable_entry.h` and `format.h`; forward-declares table, prefetch, get context, lookup context, and read options. It is integrated into block-based table open/read plumbing when compression dictionary handles are present.

Risks and test signals: the table pointer must outlive the reader. Cache behavior follows `cache_index_and_filter_blocks`, which can surprise callers because dictionaries are metadata-like but used for data decompression. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/user_defined_index_wrapper.h -->
# sources/storage-engines/rocksdb/table/block_based/user_defined_index_wrapper.h

Purpose: provides wrapper classes that integrate RocksDB user-defined indexes with the existing block-based table index abstraction while still building and retaining the standard internal index.

Important APIs/types/functions: `UserDefinedIndexBuilderWrapper` derives from `IndexBuilder` and forwards `AddIndexEntry`, `OnKeyAdded`, `Finish`, size estimates, and separator behavior to an internal builder plus a `UserDefinedIndexBuilder`. `UserDefinedIndexIteratorWrapper` adapts a `UserDefinedIndexIterator` to `InternalIteratorBase<IndexValue>`. `UserDefinedIndexReaderWrapper` dispatches reads between the standard index reader and UDI reader based on primary mode or `ReadOptions::table_index_factory`.

Control flow: on writes, every index entry and key is sent to the standard builder. UDI calls parse internal keys to pass user keys plus sequence/type tags in context; parse errors are stored and returned on finish because `AddIndexEntry` cannot return status. `Finish` emits the UDI as a meta block named with `kUserDefinedIndexPrefix + name_`, then finishes the standard index. On reads, UDI iterator results are converted back into internal-key separators with seq 0/value type and cached `IndexValue` block handles.

State and persistence: persistent output includes the normal index blocks plus a UDI meta block. Runtime state includes the wrapped builders/readers, UDI name, cached status, finish flag, cached iterator result/internal key/value, and primary-mode selection.

Dependencies/integration: depends on `rocksdb/user_defined_index.h`, internal key parsing/packing, table reader index interfaces, block handles, meta block naming, and `ReadOptions` dispatch. It explicitly rejects parallel-compression split index entry APIs with assertions because that mode is validated away elsewhere.

Risks and test signals: risks include sequence/tag mishandling for duplicate user keys across snapshots, value type mapping drift when new RocksDB value types are added, unsupported `SeekForPrev`, and UDI primary mode hiding standard index read bugs. This subset has no direct UDI tests; comments reference option validation and PR discussion as integration constraints.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/user_defined_index_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_fetcher.cc -->
# sources/storage-engines/rocksdb/table/block_fetcher.cc

Purpose: implements `BlockFetcher`, the central low-level path for retrieving one physical block from prefetch buffers, persistent cache, or file IO; verifying its trailer; optionally decompressing it; and returning `BlockContents` with correct ownership.

Important APIs/types/functions: helper methods include `ProcessTrailerIfPresent`, persistent-cache lookups/inserts for serialized and uncompressed blocks, `PrepareBufferForBlockFromFile`, buffer-copy helpers, `GetBlockContents`, `ReadBlock`, `ReadBlockContents`, and `ReadAsyncBlockContents`. A local helper records per-block-type read byte counters.

Control flow: synchronous reads first try uncompressed persistent cache, then prefetch buffer, then compressed persistent cache, then file read. File reads may use FS scratch/MultiRead or a prepared stack/heap/compressed/read-scoped buffer. After reading, the trailer is validated and compression type decoded. If checksum corruption occurs and the FS advertises verify-and-reconstruct support, the read is retried. Finally, compressed blocks are decompressed if requested; otherwise ownership is normalized into `BlockContents`. Async reads use `PrefetchAsync` when not for compaction, falling back to synchronous read.

State and persistence: persistent state is only optional persistent cache insertion of serialized or uncompressed blocks when `fill_cache` is set. Runtime state tracks IO status, slice/used buffer, direct IO buffer, heap/compressed allocations, read-scoped lease, FS scratch, prefetch hit state, decompression args, and debug memcpy counters.

Dependencies/integration: depends on `RandomAccessFileReader`, `FilePrefetchBuffer`, footer/checksum code, persistent cache helpers, compression manager/decompressor, memory allocators, file system features, perf counters, and block cache/table reader callers.

Risks and test signals: this code is ownership-sensitive. Key risks include returning memory backed by short-lived prefetch/stack buffers, incorrectly copying compressed versus uncompressed data, checksum retry state leaks, async fallback differences, and under-tested read-scoped leases. `block_fetcher_test.cc` verifies allocation/copy behavior across buffered, mmap, and direct reads for compressed and uncompressed data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_fetcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_fetcher.h -->
# sources/storage-engines/rocksdb/table/block_fetcher.h

Purpose: declares `BlockFetcher`, a single-block retrieval helper used by RocksDB table readers. The class hides prefetch, persistent cache, checksum, decompression, direct IO, and memory allocation details behind `ReadBlockContents` and `ReadAsyncBlockContents`.

Important APIs/types/functions: constructor arguments include file reader, optional prefetch buffer, footer, read options, block handle, output `BlockContents`, immutable options, decompression flags, block type, decompressor, persistent cache options, allocators, compaction flag, and optional read-scoped buffer provider. Public accessors expose compression type, block size with trailer, compressed block slice, and debug copy counters.

Control flow: the header lays out private phases: lookup uncompressed cache, try prefetch, lookup serialized cache, prepare file buffer, copy to final buffers, produce block contents, insert caches, process trailer, and read from file. The public methods orchestrate these phases synchronously or through async prefetch.

State and persistence: the fetcher is per-read transient. It can update persistent cache through helper methods, but otherwise owns temporary buffers and moves final ownership into `BlockContents`. `BlockContents` may end up backed by heap allocation, mmap slice, compressed allocation, or read-scoped cleanup.

Dependencies/integration: includes file utilities, memory allocator implementation, block definitions, format/footer, persistent cache options, and cast utilities. It is called by `BlockBasedTable::RetrieveBlock`/`MaybeReadBlockAndLoadToCache` paths and feeds parsed block classes.

Risks and test signals: because it stores references to footer, handle, options, and cache options, those must outlive the fetcher call. Feature flags for FS scratch and verify/reconstruct alter buffer lifetimes and retry behavior. The test file asserts expected allocations and memcpys in representative modes but not all persistent-cache or async branches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_fetcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_fetcher_test.cc -->
# sources/storage-engines/rocksdb/table/block_fetcher_test.cc

Purpose: unit tests for `BlockFetcher` buffer ownership and copy/allocation behavior under multiple IO modes and compression modes.

Important APIs/types/functions: `BlockFetcherTest` provides helpers to create a small block-based table, fetch its index block, fetch the first data block, build table readers, read footers, and wrap the raw `BlockFetcher` constructor. `MemcpyStats`, `BufAllocationStats`, and `TestStats` encode expected debug counters and custom allocator counts.

Control flow: each test creates SSTs with supported compression types, reads index handles through metadata/index readers, then calls `FetchBlock` under three modes: buffered read, mmap, and direct read. The tests compare returned block contents across modes and assert exact copy/allocation counts.

State and persistence: tests write temporary SST files under a per-thread DB path and remove the directory at teardown. They use `CountedMemoryAllocator` to validate allocation/deallocation behavior after `BlockContents::allocation.reset()`.

Dependencies/integration: depends on block-based table builder/reader/factory, binary-search index reader, footer/meta block lookup, file system abstractions, compression support enumeration, and test sync points for direct IO mocking.

Risks and test signals: coverage is strong for uncompressed reads, compressed reads without decompression, compressed reads with decompression, index block reads, and custom allocator lifetime. Gaps include persistent cache hits/inserts, checksum mismatch/retry, async prefetch, read-scoped block buffer provider, FS scratch ownership, and large-block paths exceeding the stack buffer threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_fetcher_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cleanable_test.cc -->
# sources/storage-engines/rocksdb/table/cleanable_test.cc

Purpose: tests cleanup registration/delegation primitives used throughout table/block code to transfer ownership of pinned resources, heap buffers, and cache handles.

Important APIs/types/functions: tests use `Cleanable`, `PinnableSlice`, and `SharedCleanablePtr`. Helper callbacks `Multiplier`, `ReleaseStringHeap`, and `Decrement` make cleanup execution observable. `PinnableSlice4Test` exposes internal cleanup state for validation.

Control flow: `Register` validates no-op cleanup, single cleanup, multiple cleanups, `Reset` executing cleanups, and reuse after reset. `Delegation` checks moving cleanups from one `Cleanable` to another across stack and heap cleanup-node cases. `PinnableSlice` verifies pinning with direct cleanup, cleanup delegation from another cleanable, and self pinning. Shared tests validate copy/move/cleanup transfer behavior for `SharedCleanablePtr`.

State and persistence: all state is in-memory counters and objects; no files are written. The tests rely on destructor timing at scope exit to assert cleanup execution.

Dependencies/integration: includes public RocksDB cleanable/perf/iostats headers and test harness utilities. These primitives are integrated widely with iterators, `BlockContents`, cache entries, and pinnable values.

Risks and test signals: tests guard ordering/lifetime semantics that are easy to regress when changing cleanup storage. They verify moved-from states for analyzer friendliness. They do not test concurrency, but table reader cleanup usage is primarily ownership/lifetime scoped rather than shared mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cleanable_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/compaction_merging_iterator.cc -->
# sources/storage-engines/rocksdb/table/compaction_merging_iterator.cc

Purpose: implements a compaction-specific merging iterator that merges point-key child iterators with range tombstone start keys. Its goal is to preserve sorted output while exposing tombstone starts so compaction partitioning can avoid oversized overlap ranges.

Important APIs/types/functions: `CompactionMergingIterator` implements `SeekToFirst`, `Seek`, `Next`, `key`, `value`, `status`, bound checks, pinned iterator propagation, and `IsDeleteRangeSentinelKey`. Private structures include `HeapItem`, `CompactionHeapItemComparator`, a binary min-heap, range tombstone iterator storage, and pinned tombstone heap items. Factory `NewCompactionMergingIterator` constructs heap or arena instances.

Control flow: seeking clears the heap, positions all point iterators, adds valid ones, positions each `TruncatedRangeDelIterator`, inserts current tombstone starts, skips file-boundary sentinel keys, and selects the heap top. `Next` advances either the current point iterator or current range tombstone iterator, restores the heap, skips sentinels, and updates `current_`.

State and persistence: no persistent writes. Runtime state owns child iterator wrappers, range tombstone iterators, pinned heap items, dummy tombstone value, heap, accumulated status, and optional internal stats count of running compaction sorted runs. Destruction decrements stats and deletes child iterators respecting arena mode.

Dependencies/integration: depends on internal key comparator, `TruncatedRangeDelIterator`, `IteratorWrapper`, `BinaryHeap`, pinned iterator manager, and `InternalStats`. Level iterators can receive pointers to their associated range tombstone iterator through the second element of the input pairs.

Risks and test signals: risks include comparator ordering between tombstone starts and file boundary sentinels, ignoring parse failures in `Seek`, status propagation, and assuming range tombstones from a file are exhausted before skipping its sentinel. No direct tests in this subset; compaction tests elsewhere should cover behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/compaction_merging_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/compaction_merging_iterator.h -->
# sources/storage-engines/rocksdb/table/compaction_merging_iterator.h

Purpose: declares the compaction-specific merging iterator factory and documents why compaction needs a specialized stream that includes range tombstone start keys.

Important APIs/types/functions: `NewCompactionMergingIterator` takes an internal key comparator, array of child `InternalIterator*`, child count, a vector of owned `TruncatedRangeDelIterator` pairs plus optional pointer backpatch slots, optional arena, and optional `InternalStats`.

Control flow: the factory returns an `InternalIterator` that merges point keys and synthetic range-deletion sentinel keys. The documentation explains that range tombstone starts are emitted as internal keys with `kTypeRangeDeletion` unless truncated at file boundaries.

State and persistence: no persistent state is declared. Ownership of range tombstone iterators is moved into the implementation. Child iterator ownership is transferred to the returned iterator.

Dependencies/integration: includes range deletion aggregation, merging iterator definitions, slices, types, and arena/stats forward declarations. It is used by compaction code rather than normal user iteration.

Risks and test signals: callers must use `IsDeleteRangeSentinelKey()` to distinguish range tombstone start keys from point entries, but the TODO notes that the same API is overloaded for file-boundary and range tombstone sentinels in different layers. Direct tests are absent here, so correctness depends on compaction-level suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/compaction_merging_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.cc -->
# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.cc

Purpose: implements the writer for RocksDB cuckoo-table SSTs, optimized for fast point lookups with fixed-length keys/values and limited operation types.

Important APIs/types/functions: defines cuckoo table property names and magic number, then implements `CuckooTableBuilder` constructor, `Add`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, `MakeHashTable`, `MakeSpaceForKey`, `GetFileChecksum`, and checksum function name accessors. Internal helpers expose stored keys/values and detect deletion records after closure.

Control flow: `Add` parses internal keys, accepts only value/deletion types, determines last-level mode from first key sequence number, enforces fixed key/value lengths, stores values and deletions in separate contiguous strings, tracks smallest/largest user keys for empty-bucket filler generation, and grows table size for power-of-two hashing. `Finish` computes module table size if needed, builds a cuckoo hash table, finds an unused key outside the observed bytewise range, writes all buckets with empty fillers, writes properties and metaindex blocks, then appends a footer. `MakeHashTable` tries direct candidate buckets and uses `MakeSpaceForKey` BFS displacement; it increases hash function count up to the configured maximum.

State and persistence: persisted layout is a flat bucket array followed by properties block, metaindex block, and footer. Properties include empty key, hash function count, table size, value length, last-level flag, cuckoo block size, identity/module hash flags, and user key length.

Dependencies/integration: depends on internal key parsing, `WritableFileWriter`, block/property/metaindex builders, `CuckooHash`, table properties, and footer builder.

Risks and test signals: risks include duplicate user-key detection via comparator, fixed-size assumptions, undefined/unaligned identity hash reads, empty-key search failure, collision-path limits, and partial files on finish errors. Tests cover empty files, collisions, displacement paths, block-size probing, deletions, duplicate keys, and too-long collision paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.h -->
# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.h

Purpose: declares `CuckooTableBuilder`, the `TableBuilder` implementation for cuckoo-table SST files.

Important APIs/types/functions: public methods are constructor, `Add`, `status`, `io_status`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, `GetTableProperties`, `GetFileChecksum`, and `GetFileChecksumFuncName`. Private structures and methods include `CuckooBucket`, `MakeSpaceForKey`, `MakeHashTable`, `IsDeletedKey`, `GetKey`, `GetUserKey`, and `GetValue`.

Control flow: the header contract requires keys to be added in comparator order and exactly one of `Finish`/`Abandon` before destruction. Builder state supports collecting entries first, then building the final hash table only at finish.

State and persistence: runtime state includes hash function count, file pointer, ratio/search/depth options, block size, current hash table size, last-level mode, fixed key/value lengths, concatenated key-value and deleted-key buffers, counts, status/io status, table properties, comparator, hash mode flags, smallest/largest user keys, and closure flag. This state is serialized into the file and property block during `Finish`.

Dependencies/integration: derives from `TableBuilder` and depends on version/table properties, writable file writer, comparator, and cuckoo table factory hash callback conventions.

Risks and test signals: the builder stores all keys and values in memory until finish, so memory grows with file size. It assumes fixed lengths and limited value types, making it unsuitable for snapshots/merge/prefix features. `cuckoo_table_builder_test.cc` exercises the public builder contract and many failure modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder_test.cc -->
# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder_test.cc

Purpose: unit tests for cuckoo table builder file layout, properties, collision handling, and failure modes.

Important APIs/types/functions: `hash_map` plus `GetSliceHash` give deterministic hash locations for tests. `CuckooBuilderTest` provides `CheckFileContents`, `GetInternalKey`, `NextPowOf2`, and `GetExpectedTableSize`. `CheckFileContents` reads the generated file, validates table properties, and checks every bucket against expected locations or empty-bucket filler bytes.

Control flow: tests create temporary writable files, instantiate `CuckooTableBuilder` with deterministic hash callback, add keys, assert incremental `NumEntries`/`FileSize`, finish and close, then inspect properties and raw buckets. Some tests use full internal keys; others use zero-sequence last-level mode where only user keys are stored.

State and persistence: tests write actual cuckoo table files under per-thread DB paths and read them back with `RandomAccessFileReader` and `ReadTableProperties`. Expected properties include empty key, value length, hash table size, hash function count, cuckoo block size, last-level flag, raw sizes, and data size.

Dependencies/integration: depends on file readers/writers, table properties reader, meta blocks, internal key builder/parser, bytewise comparator, and test harness.

Risks and test signals: coverage includes empty file, no-collision writes, collision writes, cuckoo block probing, displacement paths, user-key/last-level mode, too-long collision failure, duplicate key failure, value and deletion paths. It does not cover module-hash production hashing heavily, checksum names, factory integration, or crash cleanup of partially written files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.cc -->
# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.cc

Purpose: implements the table factory that wires cuckoo table options into RocksDB table reader and builder creation.

Important APIs/types/functions: `CuckooTableFactory::NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, constructor option registration, and `NewCuckooTableFactory`.

Control flow: `NewTableReader` constructs a `CuckooTableReader` with immutable options, file, file size, user comparator, and no custom hash callback; it returns the reader only if its status is OK. `NewTableBuilder` constructs a `CuckooTableBuilder` using factory options, hard-coded max hash function count of 64, table-builder comparator/column-family metadata, DB/session IDs, and file number. `GetPrintableOptions` formats selected options for diagnostics.

State and persistence: the factory owns `CuckooTableOptions`. It does not write data itself, but builder creation determines persisted cuckoo layout parameters such as hash ratio, search depth, block size, module hash, and identity hash.

Dependencies/integration: depends on configurable options registration, option type metadata, `CuckooTableBuilder`, `CuckooTableReader`, and public `NewCuckooTableFactory` entry point. It implements `TableFactory` virtual methods used by DB/table creation.

Risks and test signals: `GetPrintableOptions` omits `use_module_hash`, despite registering it, so diagnostics may be incomplete. Reader ignores prefetch-index-and-filter flag because cuckoo format has different metadata behavior. The subset's builder tests do not directly instantiate the factory; factory coverage likely comes from options/table factory tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.h -->
# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.h

Purpose: declares cuckoo table hashing and the `CuckooTableFactory` used to create cuckoo table readers/builders.

Important APIs/types/functions: `CuckooHash` computes a candidate bucket from a user key, hash index, hash mode, table size, identity-first setting, and optional test hash callback. `CuckooTableFactory` implements `Name`, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `Clone`.

Control flow: `CuckooHash` optionally delegates to a test callback in debug/Windows builds. Otherwise it uses identity hash for hash 0 when configured, or MurmurHash seeded by `kCuckooMurmurSeedMultiplier * hash_cnt`. It maps to a bucket with modulo or power-of-two masking depending on `use_module_hash`.

State and persistence: factory state is `CuckooTableOptions`. Hash choices and options flow into persisted table properties through the builder and must match reader lookup behavior.

Dependencies/integration: derives from `TableFactory`, uses public RocksDB options/table APIs, and includes MurmurHash. Comments document major format limitations: fixed key/value lengths, no snapshots, no merge operations, and no prefix bloom filters.

Risks and test signals: identity hashing reinterpret-casts key bytes as `int64_t`, which assumes sufficient key size and alignment tolerance. Power-of-two masking requires table sizes to be powers of two. Tests in `cuckoo_table_builder_test.cc` use the debug hash callback to make placement deterministic, but production hash behavior needs reader/table tests outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.h -->
