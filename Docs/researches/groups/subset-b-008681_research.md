# Research: subset-b-008681

Grouped source research for RocksDB table-layer files. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.cc -->
# sources/storage-engines/rocksdb/table/merging_iterator.cc

Purpose: Implements RocksDB's internal merging iterator for combining multiple child `InternalIterator`s into one sorted stream, with optional range tombstone awareness. It is the core fan-in iterator used above memtables/SST iterators and can skip point keys covered by range deletions.

Important APIs and functions: Defines `MergingIterator`, `NewMergingIterator()`, and `MergeIteratorBuilder` implementation. Public iterator methods include `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `PrepareValue`, `SetPinnedItersMgr`, `SetRangeDelReadSeqno`, and `Prepare`. Internal helpers maintain min/max heaps and range tombstone state: `SeekImpl`, `SeekForPrevImpl`, `FindNextVisibleKey`, `FindPrevVisibleKey`, `SkipNextDeleted`, `SkipPrevDeleted`, `SwitchToForward`, `SwitchToBackward`, `InsertRangeTombstoneToMinHeap`, and `InsertRangeTombstoneToMaxHeap`.

Control flow: Forward scans build `minHeap_` from child iterators and range tombstone endpoints, pop tombstone starts into `active_`, and skip heap-top points covered by active tombstones. Reverse scans lazily initialize `maxHeap_`, mirror the endpoint logic, and treat tombstone ends as activation points. Seeks can cascade: when a newer range tombstone covers the target, older levels are reseeked to the tombstone end or start to avoid scanning invisible keys. Direction switches reseek non-current children around the current key, rebuild the appropriate heap, and reposition range tombstone iterators.

State and persistence: Runtime state includes `children_`, `pinned_heap_item_`, `range_tombstone_iters_`, `active_`, `current_`, `direction_`, heap instances, accumulated `status_`, pinned iterator manager, prefix seek mode, arena ownership mode, and optional `iterate_upper_bound_`. There is no durable persistence; correctness depends on preserving heap/range-deletion invariants across every iterator call.

Dependencies and integration points: Depends on `InternalKeyComparator`, `IteratorWrapper`, `TruncatedRangeDelIterator`, `ArenaWrappedDBIter`, `BinaryHeap`, perf counters, async `TryAgain` statuses, and file-boundary sentinel behavior from level iterators. Builder integration updates `LevelIterator` range tombstone pointers and DB iterator memtable range tombstone pointer storage.

Risks: Range tombstone logic is highly invariant-sensitive, especially same-level sequence checks, endpoint op-type ordering, file-boundary sentinels, upper-bound filtering, and reverse cascading seek. Async `TryAgain` paths must replay the exact target used before prefetch. Arena mode changes destruction responsibility. Prefix seek mode relaxes one direction-switch assertion and can hide ordering assumptions.

Test signals: Exercise forward/reverse merge order, duplicate internal keys, direction switches, async child iterators, pinned key/value forwarding, empty/one/many children, range tombstones across levels, same-level tombstone sequence comparisons, tombstones spanning file boundaries, upper-bound-limited iteration, prefix seek mode, and builder single-iterator fast paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.h -->
# sources/storage-engines/rocksdb/table/merging_iterator.h

Purpose: Declares the merging iterator factory and builder used to construct sorted union iterators over RocksDB internal point iterators and optional range tombstone iterators.

Important APIs and types: `NewMergingIterator()` returns an `InternalIterator` over the union of child iterators without duplicate suppression. `MergeIteratorBuilder` owns construction of either a direct single child or an arena-allocated `MergingIterator`. Its APIs are `AddIterator()`, `AddPointAndTombstoneIterator()`, `SetMemtablePruned()`, `GetArena()`, and `Finish()`. The forward declaration `MergingIterator` identifies the implementation class returned by the factory/builder.

Control flow: Callers either add only point iterators or add point/tombstone iterator pairs. The builder switches from direct single-iterator mode to merging mode when multiple point iterators or range tombstone handling are needed. `Finish()` returns the built iterator and, when requested, wires stored range tombstone iterator slots back into `LevelIterator` or `ArenaWrappedDBIter` owners.

State and persistence: The header defines builder state for `merge_iter`, `first_iter`, `use_merging_iter`, arena ownership, deferred range-deletion pointer fixups, and a `memtable_pruned_` flag. All state is transient iterator construction state.

Dependencies and integration points: Includes `db/range_del_aggregator.h`, `rocksdb/slice.h`, `table/iterator_wrapper.h`, and iterator type aliases. It is consumed by DB iterator setup, version/level iterator composition, and read paths that need range deletion filtering.

Risks: The API requires exclusive use of either point-only or point-plus-tombstone additions. Pointer-to-slot fixups are sensitive to vector reallocation, so they are intentionally delayed. Returning a child directly in the single-iterator case changes ownership and destructor expectations.

Test signals: Compile and behavior coverage for point-only merging, single child fast path, tombstone iterator pairs, level-iterator range tombstone pointer refresh, memtable-pruned DB iterator setup, and arena-backed destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/merging_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.cc -->
# sources/storage-engines/rocksdb/table/meta_blocks.cc

Purpose: Implements construction, lookup, parsing, and reading of SST meta blocks, especially the metaindex block and table properties block. It also dispatches table property collector callbacks during table building.

Important APIs and functions: Defines meta block names `kPropertiesBlockName`, `kIndexBlockName`, `kCompressionDictBlockName`, and `kRangeDelBlockName`. Implements `MetaIndexBuilder`, `PropertyBlockBuilder`, `LogPropertiesCollectionError`, `NotifyCollectTableCollectorsOnAdd`, `NotifyCollectTableCollectorsOnBlockAdd`, `NotifyCollectTableCollectorsOnFinish`, `ParsePropertiesBlock`, `ReadTablePropertiesHelper`, `ReadTableProperties`, `FindOptionalMetaBlock`, `FindMetaBlock`, `ReadMetaIndexBlockInFile`, `FindMetaBlockInFile`, and `ReadMetaBlock`.

Control flow: Builders collect properties/handles into sorted `KVMap`s and emit block-builder output. Property parsing iterates the properties block in sorted order, rejects unsorted duplicates, decodes known uint64 properties, copies known string properties, preserves legacy deleted/merge counters in user properties, and stores unknown keys as user-collected properties. Meta reads load the footer, fetch the metaindex block with `BlockFetcher`, seek the desired meta block handle, then fetch the target block. Table properties have special checksum handling: read once without checksum, parse global sequence offset, verify checksum, optionally zero the external SST global seqno for compatibility, and retry through filesystem reconstruction on corruption.

State and persistence: The code writes persistent SST metadata: properties, metaindex entries, optional index/dictionary/range-deletion block handles, DB/session/host IDs, timestamps, compression stats, and user-collected properties. Runtime state is limited to local builders, block handles, block contents, and temporary parsed `TableProperties`.

Dependencies and integration points: Uses block-based `BlockBuilder`, `Block`, `BlockFetcher`, footer parsing, `RandomAccessFileReader`, `FilePrefetchBuffer`, table properties collectors, persistent cache options, filesystem verify-and-reconstruct support, stats ticks, and logging. Table builders call the collector notification functions and readers call the meta block find/read helpers.

Risks: Properties must remain strictly sorted and unique. Malformed varints are logged and skipped rather than failing the whole parse. External SST global seqno mutation makes checksum verification nontrivial. Meta blocks are assumed uncompressed. The helper asserts that `ReadMetaBlock` is not used for properties because properties need special checksum handling.

Test signals: Cover property block round trips, unsorted/duplicate property corruption, malformed property values, external SST global sequence checksum compatibility, filesystem corruption retry counters, missing optional vs required meta blocks, footer read failures, prefetch-buffer paths, and user-defined property collector error logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.h -->
# sources/storage-engines/rocksdb/table/meta_blocks.h

Purpose: Declares table meta block names, builders, collector notification helpers, property parsing, and file-level meta block read/find APIs shared by RocksDB table builders and readers.

Important APIs and types: Exposes `MetaIndexBuilder`, `PropertyBlockBuilder`, `LogPropertiesCollectionError`, collector notification helpers, `ParsePropertiesBlock`, `ReadTablePropertiesHelper`, `ReadTableProperties`, `FindOptionalMetaBlock`, `FindMetaBlock`, `FindMetaBlockInFile`, `ReadMetaIndexBlockInFile`, and `ReadMetaBlock`. External block-name constants identify properties, index, compression dictionary, and range deletion meta blocks.

Control flow: Table builders add meta block handles and properties through builder classes, then call `Finish()` to produce block contents. Readers use footer/metaindex helpers to find a named block, with optional and required variants differing only in missing-block status behavior. Property readers return a heap-allocated `TableProperties` only on success.

State and persistence: The declarations define the API for SST-persistent metadata and table properties, but the header itself owns no runtime state beyond builder member declarations. Builders keep sorted maps and block builders until finish.

Dependencies and integration points: Depends on table format primitives (`BlockHandle`, `Footer`, `BlockContents`), block-based builders, table property collectors, `RandomAccessFileReader`, `FilePrefetchBuffer`, immutable/read options, and optional memory allocator support.

Risks: Callers must pass the correct table magic number and file size for footer parsing. Ownership of returned `TableProperties` is through `unique_ptr`, and output pointers are modified only on success. Misusing `ReadMetaBlock` for properties bypasses checksum compatibility logic.

Test signals: Compile coverage across block-based and plain table builders/readers, metaindex construction, properties reading with and without custom allocator, optional missing-block lookup, and required missing-block corruption behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.cc -->
# sources/storage-engines/rocksdb/table/mock_table.cc

Purpose: Implements an in-memory/mock RocksDB table factory, builder, reader, and iterator for tests. It simulates SST creation and reading by writing only a small file ID to disk and storing key/value vectors in a process-local map.

Important APIs and functions: Implements `MakeMockFile`, `SortKVVector`, `MockTableIterator`, `MockTableBuilder`, `MockTableReader::NewIterator`, `MockTableReader::Get`, `MockTableFactory::NewTableReader`, `NewTableBuilder`, `CreateMockTable`, `GetAndWriteNextID`, `GetIDFromFile`, `AssertSingleFile`, and `AssertLatestFiles`.

Control flow: Builders receive internal key/value pairs, optionally corrupt or reorder the first entries according to factory corruption mode, and on `Finish()` insert the vector into `MockTableFileSystem::files` under a generated ID. `NewTableBuilder()` writes the ID to the `WritableFileWriter`; `NewTableReader()` reads the ID back and returns a `MockTableReader` over the stored vector. Iterators perform lower/upper-bound seeks with `InternalKeyComparator`. `Get()` scans from the lookup key, parses internal keys, and feeds values into `GetContext::SaveValue()` until the context says to stop.

State and persistence: Persistent on-disk content is only the fixed 4-byte table ID. Actual table contents live in `MockTableFileSystem::files` protected by a mutex. `next_id_`, `corrupt_mode_`, and `key_value_size_` configure test behavior. Reader table properties are synthetic.

Dependencies and integration points: Integrates with the RocksDB `TableFactory`, `TableBuilder`, `TableReader`, `InternalIterator`, `GetContext`, file reader/writer wrappers, internal key parsing, and test assertion utilities.

Risks: The mock format is process-local; files are unreadable without the same factory instance state. `SeekToLast()` decrements `end()` without guarding empty tables. Corruption mode is intentionally one-shot and can produce invalid ordering or parse failures. `GetIDFromFile()` asserts a 4-byte read before checking error paths.

Test signals: Useful for DB/table tests that need deterministic table contents, builder corruption injection, latest-file assertions after compaction, get-path `SaveValue()` behavior, iterator seek/prev/next semantics, and file-not-found behavior for unknown IDs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.h -->
# sources/storage-engines/rocksdb/table/mock_table.h

Purpose: Declares the mock table format used by RocksDB tests to avoid real SST encoding while still exercising `TableFactory`, `TableBuilder`, and `TableReader` integration.

Important APIs and types: Defines `mock::KVPair`, `KVVector`, `MakeMockFile()`, `SortKVVector()`, `MockTableFileSystem`, `MockTableFactory`, and `MockTableReader`. `MockTableFactory` exposes corruption modes `kCorruptNone`, `kCorruptKey`, `kCorruptValue`, and `kCorruptReorderKey`, plus `CreateMockTable()`, `SetCorruptionMode()`, `SetKeyValueSize()`, assertion helpers, and table factory overrides. `MockTableReader` overrides iterator, get, approximate offset/size, memory usage, compaction setup, and table properties APIs.

Control flow: Tests configure a factory, build or directly create mock tables, then RocksDB opens readers through normal table factory hooks. The header makes clear that `CreateMockTable()` accepts internal-key/value pairs and bypasses the builder path.

State and persistence: `MockTableFileSystem` contains the in-memory map from file ID to sorted vectors. `MockTableFactory` owns the map, ID counter, corruption mode, and fake key/value size. `MockTableReader` references a stored vector and returns synthetic `TableProperties`.

Dependencies and integration points: Depends on RocksDB comparator/table abstractions, internal iterators, writable/random file wrappers via the implementation, `VersionEdit` types, port mutexes, and test harness utilities. It is not production table code.

Risks: `Clone()` returns `nullptr`, so code requiring cloneable table factories cannot use it. Reader lifetime depends on the factory map retaining referenced vectors. The format does not model compression, checksums, filters, range deletions, or real table properties.

Test signals: Compile tests using mock factory configuration, direct mock table creation, corruption modes, table reader get/iterator behavior, and assertion helpers for exactly one or latest generated files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/multiget_context.h -->
# sources/storage-engines/rocksdb/table/multiget_context.h

Purpose: Defines `KeyContext` and `MultiGetContext`, the compact batch state container used to process RocksDB `MultiGet` lookups over sorted subsets of keys.

Important APIs and types: `KeyContext` holds user/internal lookup key views, column family, status, merge context, tombstone coverage sequence, result buffers, timestamp output, and `GetContext`. `MultiGetContext` constructs up to `MAX_BATCH_SIZE` lookup keys, owns stack/heap placement-new `LookupKey` storage, and exposes `GetMultiGetRange()`. `Range` models a subset with skip and invalid bitmasks; `Range::Iterator` walks keys not already skipped, invalidated, or done. Range APIs include `SkipIndex`, `SkipKey`, `MarkKeyDone`, `KeysLeft`, `AddSkipsFrom`, `AddValueSize`, `Suffix`, `operator+=`, `operator-=`, and complement `operator~`.

Control flow: The constructor copies pointers from an `autovector`, materializes `LookupKey`s for the requested slice, and precomputes user-key-with-timestamp, stripped user key, and internal key slices. Lookup stages create ranges and subranges, skip filtered-out keys, mark completed keys in the shared context mask, and optionally combine adjacent/non-overlapping ranges.

State and persistence: All state is per-call runtime state. `value_mask_` is shared across ranges to make completion immediately visible to all iterators. `value_size_` accumulates result size. Lookup keys use stack storage for up to 16 keys and heap storage up to 32 keys. When coroutine support is enabled, an `AsyncFileReader` and `SingleThreadExecutor` are embedded.

Dependencies and integration points: Used by table/cache read paths and `MultiGet` implementations. Depends on `LookupKey`, timestamp stripping, merge context, async reader utilities, statistics, filesystem, and bit-counting helpers.

Risks: Bit operations assume indices below 64 and `MAX_BATCH_SIZE < 64`. Range arithmetic requires non-overlap or containment invariants and uses asserts. `FindLastRemaining()` is subtle for empty masks. KeyContext stores many external pointers, so caller-owned result/status storage must outlive the context.

Test signals: MultiGet batches of 0/1/16/17/32 keys, timestamped reads, range subsetting, skip propagation, done-mask visibility across ranges, range addition/subtraction/complement, value-size accounting, and coroutine-enabled async read execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/multiget_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.cc -->
# sources/storage-engines/rocksdb/table/persistent_cache_helper.cc

Purpose: Implements helper functions for looking up and inserting serialized or uncompressed blocks in RocksDB's persistent cache.

Important APIs and functions: Defines `PersistentCacheOptions::kEmpty` and implements `PersistentCacheHelper::InsertSerialized`, `InsertUncompressed`, `LookupSerialized`, and `LookupUncompressed`.

Control flow: Each operation derives a `CacheKey` from `BlockBasedTable::GetCacheKey(base_cache_key, handle)`. Serialized inserts assert a compressed persistent cache and store block bytes including trailer. Uncompressed inserts assert an uncompressed cache and store `BlockContents::data` without trailer. Serialized lookups fetch bytes into an owned buffer, record hit/miss ticks, and in debug verify expected size equals `handle.size() + kBlockTrailerSize`. Uncompressed lookups optionally return `NotFound` when no output `BlockContents` is provided, then populate `BlockContents` from the returned allocation on hit.

State and persistence: The helper mutates the configured persistent cache and statistics counters. It does not own cache lifetime; `PersistentCacheOptions` provides the shared cache pointer, base key, and stats pointer. Insert errors are explicitly ignored with `PermitUncheckedError()`.

Dependencies and integration points: Used by block fetching/table reading paths. Depends on `PersistentCache`, block handles, block contents, block-based cache key construction, and RocksDB statistics tick IDs `PERSISTENT_CACHE_HIT` and `PERSISTENT_CACHE_MISS`.

Risks: Correctness relies on callers choosing the serialized vs uncompressed helper matching the cache mode. Insert failures are non-fatal and invisible except through cache behavior. Debug-only size checks can hide production cache corruption until consumers parse the data. Uncompressed size assertions compare file compressed size to cache uncompressed size only loosely.

Test signals: Persistent cache hit/miss stats, compressed cache serialized round trip, uncompressed cache `BlockContents` round trip, missing cache entry behavior, null output for uncompressed lookup, and wrong-mode assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.h -->
# sources/storage-engines/rocksdb/table/persistent_cache_helper.h

Purpose: Declares `PersistentCacheHelper`, a small static utility facade for table code to read and write RocksDB persistent cache entries.

Important APIs and types: The class exposes `InsertSerialized()`, `InsertUncompressed()`, `LookupSerialized()`, and `LookupUncompressed()`. Serialized operations include block trailers and are for compressed persistent caches. Uncompressed operations operate on `BlockContents` data without trailers and are for uncompressed persistent caches.

Control flow: Callers pass `PersistentCacheOptions` plus a `BlockHandle`; helper implementations construct cache keys consistently with block-based tables and route to the configured persistent cache.

State and persistence: The header owns no state. The API mutates the persistent cache supplied through options and returns `Status` for lookup operations.

Dependencies and integration points: Includes statistics support, table format types, and `persistent_cache_options.h`. It is consumed by lower-level block fetch/read logic that wants persistent cache behavior without duplicating key construction and stats recording.

Risks: The helper assumes the caller has validated cache availability and selected the correct compressed/uncompressed path. Because insertion returns `void`, cache write failures do not propagate to table reads.

Test signals: Compile coverage in block fetcher/table reader code, lookup status propagation, serialized/uncompressed cache mode assertions, and cache key consistency with block-based table keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_options.h -->
# sources/storage-engines/rocksdb/table/persistent_cache_options.h

Purpose: Defines the lightweight context object passed through table/block read paths to enable persistent cache use.

Important APIs and types: `PersistentCacheOptions` contains a `std::shared_ptr<PersistentCache> persistent_cache`, an `OffsetableCacheKey base_cache_key`, and a `Statistics* statistics`. It provides a default constructor, a field-initializing constructor, and static `kEmpty`.

Control flow: Table readers construct non-empty options when a persistent cache should be consulted. Helpers and block fetchers pass `kEmpty` or a configured instance depending on whether cache participation is desired.

State and persistence: The struct does not persist data itself but points to the persistent cache backend and provides the base key namespace used to persist block entries. `statistics` may be null, in which case tick recording is effectively optional through statistics helpers.

Dependencies and integration points: Depends on RocksDB persistent cache API, cache key utilities, and statistics definitions. It is used by `PersistentCacheHelper`, block fetching, and meta block reading.

Risks: A default-constructed instance has no cache; helper calls generally assert a non-null cache. Incorrect base cache keys can cross-contaminate cached blocks between files. The shared pointer lifetime makes cache ownership explicit but does not guarantee the underlying cache content is valid for a specific file version.

Test signals: Empty option pass-through, configured option propagation from table reader to block fetcher, cache key namespacing by file, and stats pointer behavior when null or non-null.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/persistent_cache_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_bloom.cc

Purpose: Implements the legacy Bloom filter variant used by RocksDB plain table files for schema/backward compatibility.

Important APIs and functions: Implements `PlainTableBloomV1` construction, `SetRawData()`, `SetTotalBits()`, `BloomBlockBuilder::AddKeysHashes()`, `BloomBlockBuilder::Finish()`, and the `BloomBlockBuilder::kBloomBlock` meta block name.

Control flow: `SetTotalBits()` rounds requested bits either to a byte boundary or to a whole odd number of cache-line-sized locality blocks, allocates aligned memory from an `Allocator`, zeroes it, and adjusts the data pointer to cache-line alignment when locality is enabled. `AddKeysHashes()` inserts each precomputed hash into the embedded Bloom structure. `Finish()` exposes the raw Bloom bytes for writing to the table file.

State and persistence: The Bloom bit array is allocated in the provided allocator/arena and persisted as the plain table Bloom meta block when the builder stores indexes in the file. `SetRawData()` points a Bloom object at bytes read from an existing table.

Dependencies and integration points: Depends on `Allocator`, `LegacyLocalityBloomImpl`, `LegacyNoLocalityBloomImpl`, cache line constants, and plain table builder/reader meta block handling. The block name is added to the metaindex by `PlainTableBuilder`.

Risks: This is a legacy format and should not be reused for new filter applications. Alignment shifts mean the original allocated pointer and `data_` can differ, so lifetime belongs to the allocator. False-positive behavior depends on `num_probes`, total bit rounding, and whether prefix or full-key hashes are inserted by the caller.

Test signals: Locality and non-locality Bloom creation, raw data restoration, hash add/may-contain consistency, cache-line-aligned allocation paths, huge page allocator paths, and plain table read/write compatibility with existing Bloom version metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_bloom.h

Purpose: Declares the legacy plain-table Bloom filter and Bloom block builder used by plain table SSTs.

Important APIs and types: `PlainTableBloomV1` exposes `SetTotalBits`, `AddHash`, `MayContainHash`, `Prefetch`, `GetNumBlocks`, `GetRawData`, `SetRawData`, `GetTotalBits`, and `IsInitialized`. `BloomBlockBuilder` wraps it with `SetTotalBits`, `GetNumBlocks`, `AddKeysHashes`, and `Finish`, plus static meta block name `kBloomBlock`.

Control flow: The inline methods dispatch between locality-aware and no-locality legacy Bloom implementations depending on whether `kNumBlocks` is nonzero. `Prefetch()` only has work in locality mode. The builder is a thin adapter used by plain table construction.

State and persistence: `PlainTableBloomV1` stores total bits, locality block count, probe count, and a raw data pointer. It does not own allocation directly; the allocator passed during setup owns memory. The raw data slice is the persistent filter payload.

Dependencies and integration points: Depends on port cache-line constants, `Slice`, Bloom implementation utilities, hash/math helpers, and logging/allocator types. Plain table reader code can point the Bloom at persisted block bytes using `SetRawData()`.

Risks: The class has `k`-prefixed mutable fields, which can be mistaken for constants. Callers must initialize before adding/testing hashes. Raw data lifetime is external. The format is compatibility-only and lacks newer filter policy abstractions.

Test signals: Initialization assertions, inline may-contain behavior for both modes, prefetch no-op/non-no-op paths, raw data slice size, and `BloomBlockBuilder` output consumed by plain table readers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_builder.cc

Purpose: Implements `PlainTableBuilder`, the writer for RocksDB's plain table SST format optimized for mmap/in-memory files.

Important APIs and functions: Defines plain table magic numbers `kPlainTableMagicNumber` and `kLegacyPlainTableMagicNumber`, local `WriteBlock()`, constructor/destructor, `Add()`, `Finish()`, `Abandon()`, `NumEntries()`, `FileSize()`, checksum accessors, and `SetSeqnoTimeTableProperties()`.

Control flow: Construction initializes table properties, key encoder, optional index builder, Bloom/index metadata, DB/session/host IDs, and internal table property collectors. `Add()` parses the internal key, rejects range deletions, records prefix/full-key hashes for optional Bloom, encodes the key through `PlainTableKeyEncoder`, adds a prefix index entry, varint-encodes value length, appends the value, updates offsets and table properties, and notifies collectors. `Finish()` writes optional Bloom and plain table index meta blocks, writes the properties block, writes the metaindex block, then appends a footer with no checksum and the plain table magic number.

State and persistence: Persistent output is one data region followed by optional Bloom/index blocks, properties block, metaindex block, and footer. Runtime state tracks arena allocation, options, property collectors, Bloom builder, index builder, file writer, current offset, status/io status, table properties, key encoder, hashes, prefix extractor, and `closed_`.

Dependencies and integration points: Uses plain Bloom/index/key coding, meta block builders, footer builder, table property collectors, writable file writer, prefix extractor, internal key parsing, DB host ID reification, and RocksDB table builder interface.

Risks: Plain table does not support range deletions, compression, or checksums. Offsets are asserted to fit in 32 bits. `Finish()` has staged writes where partial files can exist on IO error. Index/Bloom emission only happens when `store_index_in_file_` and entries are present. Property collector errors are logged but do not stop the build.

Test signals: Build empty and non-empty plain tables, fixed and variable user-key lengths, plain and prefix encoding, range deletion rejection, index-in-file and no-index modes, Bloom bits per key zero/nonzero, collector callbacks, IO failure after each block write, footer magic compatibility, and checksum accessor forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_builder.h

Purpose: Declares `PlainTableBuilder`, RocksDB's `TableBuilder` implementation for writing plain table SST files.

Important APIs and types: Constructor takes immutable/mutable options, property collector factories, column family metadata, file writer, user key size, encoding type, index sparseness, Bloom/index options, DB IDs, and file number. Overrides include `Add`, `status`, `io_status`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, `GetTableProperties`, checksum accessors, and `SetSeqnoTimeTableProperties`. `SaveIndexInFile()` exposes index storage mode.

Control flow: Callers add sorted internal keys and values, then call `Finish()` or `Abandon()`. Private prefix helpers choose total-order empty prefix when no prefix extractor is configured, otherwise transform user keys through the configured prefix extractor.

State and persistence: Members include an arena for index/Bloom allocation, options references, collectors, `BloomBlockBuilder`, optional `PlainTableIndexBuilder`, output file, offset, Bloom and huge-page configuration, status fields, table properties, `PlainTableKeyEncoder`, store-index flag, collected hashes, closed flag, and prefix extractor pointer.

Dependencies and integration points: Depends on plain table Bloom/index/key coding helpers, table properties, table builder interface, RocksDB options, and prefix extraction. The factory constructs this builder from `PlainTableOptions`.

Risks: The header exposes that the builder is not copyable and requires an explicit close path. It assumes inputs are sorted by comparator and internal keys contain the 8-byte trailer. Prefix behavior changes when no prefix extractor is configured, forcing plain encoding and total-order indexing.

Test signals: Builder lifecycle tests for finish/abandon/destruction, table property visibility before/after finish, prefix helper behavior with and without extractor, and construction from all plain table option combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_factory.cc

Purpose: Implements the plain table factory, options parsing/printing, and legacy memtable factory string parsing helpers.

Important APIs and functions: Defines option metadata for `PlainTableOptions`, implements `PlainTableFactory` constructor, `NewTableReader()`, `NewTableBuilder()`, `GetPrintableOptions()`, `GetPlainTableOptionsFromString()`, `GetPlainTableOptionsFromMap()`, `NewPlainTableFactory()`, plain table property-name constants, and memtable factory parsing helpers `GetMemTableRepFactoryFromString()` plus `MemTableRepFactory::CreateFromString()` overloads.

Control flow: The constructor registers configurable options. `NewTableReader()` calls `PlainTableReader::Open()` with table options and reader options. `NewTableBuilder()` ignores `skip_filters` and returns a `PlainTableBuilder`. Option string parsing maps text to `PlainTableOptions` through the configurable object framework and normalizes unsupported/not-found errors to invalid argument. Memtable factory parsing lazily registers built-in factories once in the default object library, extracts an ID/options map, and constructs the selected factory.

State and persistence: `PlainTableFactory` stores `table_options_`. Static option metadata and one-time object-library registration are process-global configuration state. Plain table property constants are persisted into SST user-collected properties.

Dependencies and integration points: Integrates with RocksDB configurable utilities, object registry, plain table reader/builder, memtable rep factories, string utility parsing, and public `NewPlainTableFactory` API.

Risks: `NewTableReader()` ignores its `ReadOptions` parameter directly and relies on table reader options. Built-in memtable registration in this file is broader than plain table and must remain compatible with legacy option strings. The unsupported `cuckoo` memtable intentionally returns null with an error message. `GetPrintableOptions()` uses fixed buffers and format macros.

Test signals: Options string/map parsing, printable options stability, factory clone/configure behavior, builder/reader construction with all plain table options, unsupported cuckoo memtable parsing, vector/skiplist/hash memtable URI variants, and error normalization to invalid argument.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_factory.h

Purpose: Declares the `PlainTableFactory` entry point and documents the plain table on-disk format, including key/value layout, plain vs prefix key encodings, and the sequence-zero value shortcut.

Important APIs and types: `PlainTableFactory` overrides `Name`, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `Clone`. It exposes `kClassName()` and static `kValueTypeSeqId0`. The constructor accepts `PlainTableOptions`.

Control flow: RocksDB uses this factory wherever a column family is configured for plain table format. It creates builders during flush/compaction output and readers when opening plain SSTs. The extensive header comment is effectively the format contract consumed by `plain_table_builder`, `plain_table_key_coding`, and `plain_table_reader`.

State and persistence: The factory stores plain table options such as user key length, Bloom bits, hash table ratio, index sparseness, huge page TLB size, encoding type, full scan mode, and store-index mode. The documented file format is persistent and compatibility-sensitive.

Dependencies and integration points: Depends on `rocksdb/table.h` and public factory hooks. It integrates with the plain table builder/reader implementation and public `PlainTableOptions` configuration.

Risks: Plain table is designed for mmap/tmpfs-like storage and lacks compression and checksums. Fixed user-key length must match actual keys unless variable-length mode is selected. Prefix encoding correctness depends on the prefix extractor and index sparseness. `kValueTypeSeqId0` is part of the persistent key encoding shortcut.

Test signals: Format compatibility tests for plain and prefix encodings, sequence-zero special-case decoding, fixed vs variable key lengths, reader/writer round trips through the factory, and option clone/configuration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_index.cc

Purpose: Implements the hash/binary-search index block used by plain table readers and builders.

Important APIs and functions: Implements `PlainTableIndex::InitFromRawData()`, `PlainTableIndex::GetOffset()`, `PlainTableIndexBuilder::IndexRecordList::AddRecord()`, `AddKeyPrefix()`, `Finish()`, `AllocateIndex()`, `BucketizeIndexes()`, `FillIndexes()`, and static block name `PlainTableIndexBuilder::kPlainTableIndexBlock`.

Control flow: The builder receives prefix hashes and file offsets in sorted data order. It records one offset per prefix and then every `index_sparseness_` keys within a prefix. `Finish()` selects hash table size from prefix count and `hash_table_ratio`, bucketizes records by `hash % index_size_`, computes subindex storage for collisions/multiple offsets, logs keys-per-prefix histogram, and serializes varint header, primary bucket array, and subindex offsets. The reader initializes raw pointers from persisted data and `GetOffset()` maps a prefix hash to empty, direct file offset, or subindex offset by inspecting the high flag bit.

State and persistence: Persisted index data contains varint index size, varint prefix count, an array of 32-bit bucket values, and subindex records. Empty buckets use `kMaxFileSize`; subindex pointers set `kSubIndexMask`. Runtime builder state includes record groups, prefix histogram, previous prefix/hash, sparseness counters, computed sizes, prefix extractor, and arena allocation.

Dependencies and integration points: Used by plain table builder and reader. Depends on `Arena`, immutable options logging, prefix extractor, hash utilities, coding helpers, unaligned fixed32 access, and histogram logging.

Risks: File offsets are limited to 31 bits. `InitFromRawData()` assumes enough bytes remain for the bucket array after reading varints. Collision subindex order is restored by reverse write from the per-bucket linked list. `hash_table_ratio <= 0` or no prefix extractor collapses to a single bucket and binary-search-heavy behavior.

Test signals: Empty/direct/subindex lookup behavior, collision-heavy buckets, index sparseness zero and nonzero, no-prefix-extractor fallback, large prefix counts, raw data round trips, max file size boundary, and reader binary search over subindex entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_index.h

Purpose: Declares plain table index reader and builder classes and documents the persistent index format.

Important APIs and types: `PlainTableIndex` exposes `GetOffset()`, `InitFromRawData()`, `GetSubIndexBasePtrAndUpperBound()`, size/count accessors, `IndexSearchResult`, and constants `kMaxFileSize`, `kSubIndexMask`, and `kOffsetLen`. `PlainTableIndexBuilder` exposes `AddKeyPrefix()`, `Finish()`, `GetTotalSize()`, and static block name `kPlainTableIndexBlock`. Nested `IndexRecordList` groups temporary records in fixed-size arrays.

Control flow: Readers use the primary bucket table to either jump directly to a file offset, report no prefix, or decode a second-level subindex for binary search. Builders collect offsets, allocate index/subindex space in an arena, and serialize it into a block stored in the plain SST.

State and persistence: `PlainTableIndex` points into raw persisted index bytes; it does not own them. Builder state tracks prefix counts, previous prefix, current sparseness state, index/subindex sizes, hash table ratio, huge-page allocation size, and an arena-owned output buffer.

Dependencies and integration points: Depends on arena allocation, histogram logging, column family options, prefix extractors, and RocksDB options. It is tightly coupled to `PlainTableBuilder` and `PlainTableReader`.

Risks: Raw pointer interpretation requires the index block bytes to outlive the index object. The high bit of bucket values is a type flag, so valid file offsets cannot exceed `kMaxFileSize`. Prefix strings are copied for change detection, which assumes sorted input groups identical prefixes contiguously.

Test signals: Header-level integration through plain table reader/builder, subindex decoding bounds, arena lifetime, huge-page allocation path, and prefix transition/sparseness behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.cc

Purpose: Implements low-level key encoding, file reading, and key/value decoding for RocksDB plain table rows.

Important APIs and functions: Defines `PlainTableEntryType` values `kFullKey`, `kPrefixFromPreviousKey`, and `kKeySuffix`; local `EncodeSize()`; `PlainTableKeyDecoder::DecodeSize`; `PlainTableKeyEncoder::AppendKey`; `PlainTableFileReader::GetFromBuffer`, `ReadNonMmap`, `ReadVarint32`, `ReadVarint32NonMmap`; and decoder methods `ReadInternalKey`, `NextPlainEncodingKey`, `NextPrefixEncodingKey`, `NextKey`, and `NextKeyNoValue`.

Control flow: Encoding writes either plain keys with optional variable user-key length or prefix-compressed keys using full-key records at prefix boundaries/sparseness intervals and suffix records for later keys in the same prefix. Sequence-zero value keys omit the 8-byte trailer and append `PlainTableFactory::kValueTypeSeqId0`. Decoding mirrors this: it reads entry type/size, reconstructs full or prefix-compressed internal keys, handles the sequence-zero shortcut, then reads varint value size and value bytes. `PlainTableFileReader` returns direct mmap slices or manages two reusable non-mmap buffers with a 256-byte minimum prefetch.

State and persistence: Persistent row bytes are the encoded key, optional metadata byte, varint value size, and value bytes. Encoder state tracks previous prefix and key count within prefix. Decoder state tracks saved user key, current reconstructed key, prefix length, and encoding mode. Non-mmap reader state caches two recent buffers and last read status.

Dependencies and integration points: Used by `PlainTableBuilder` and `PlainTableReader`. Depends on internal key parsing, `WritableFileWriter`, plain table factory constants, reader file info, coding utilities, prefix extractors, and `IterKey` for reconstructed key ownership.

Risks: Prefix decoding depends on a valid prior full key and correct `prefix_len_`. Non-mmap slices are invalidated by subsequent reads unless copied, so decoder copies keys when needed. Mmap paths assert bounds. Varint EOF returns corruption. Sequence-zero shortcut must remain compatible with the persistent format.

Test signals: Fixed and variable plain encoding, prefix encoding with first/second/later keys, sparseness-triggered full keys, sequence-zero value shortcut, malformed entry type/varint EOF, mmap vs non-mmap slice lifetime, buffer cache hits/replacement, and value-size/value read boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.h

Purpose: Declares plain table low-level helpers for writing encoded keys, reading raw bytes from mmap/non-mmap files, and decoding rows.

Important APIs and types: `PlainTableKeyEncoder` exposes `AppendKey()` and `GetEncodingType()`. `PlainTableFileReader` exposes `Read()`, `ReadNonMmap()`, `ReadVarint32()`, `ReadVarint32NonMmap()`, `status()`, and `file_info()`. `PlainTableKeyDecoder` exposes `NextKey()` and `NextKeyNoValue()` and owns a `PlainTableFileReader`.

Control flow: Builders call `AppendKey()` before writing each value length/value. Readers call `NextKeyNoValue()` for index/key scans and `NextKey()` when the value is needed. `PlainTableFileReader::Read()` dispatches directly to mmap memory or to buffered non-mmap reads.

State and persistence: Encoder state includes effective encoding type, fixed user key length, prefix extractor, index sparseness, per-prefix key count, and previous prefix. File reader state includes file info, two buffers, buffer count, and status. Decoder state includes encoding type, fixed user key length, prefix length, saved user key, reconstructed current key, prefix extractor, and an `in_prefix_` flag.

Dependencies and integration points: Depends on `plain_table_reader.h` for reader file info and encoding types, `Slice`, `IterKey`, `ParsedInternalKey`, and writable file wrapper declarations. It is a shared dependency of plain table builder and reader.

Risks: Callers must respect slice lifetime differences between mmap and non-mmap reads. Offsets and lengths are 32-bit and bounded by plain table data end offset. Prefix decoding assumes sorted row order and a prior saved key for suffix rows. The header exposes several decoder fields publicly, making invariants easier to disturb.

Test signals: API coverage through plain table reader/builder, non-mmap buffer reuse, varint read edge cases, prefix/full-key decoding, no-value scans, and status propagation after file read failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.h -->
