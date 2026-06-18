# Research: subset-b-008675

This grouped report covers the block-based table factory and iterator files in `sources/storage-engines/rocksdb/table/block_based/`. Each section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.cc -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.cc

## Purpose
`block_based_table_factory.cc` implements RocksDB's `BlockBasedTableFactory`, the `TableFactory` backend that creates block-based SST readers and builders, owns configuration parsing/printing for `BlockBasedTableOptions`, validates cross-option compatibility, and provides shared per-factory state such as table-reader cache memory reservations and tail prefetch history. This is the option and construction entry point that links public table options to `BlockBasedTable::Open()` and `BlockBasedTableBuilder`.

## Important APIs, Types, And Functions
`TailPrefetchStats::RecordEffectiveSize()` stores recent effective tail-read byte counts in a mutex-protected ring buffer of 32 samples. `TailPrefetchStats::GetSuggestedPrefetchSize()` sorts the collected samples, chooses the largest candidate whose estimated wasted bytes are no more than one eighth of total bytes read, and caps the result at 512 KiB. A return value of `0` means no samples are available.

The static option metadata includes enum maps for `PinningTier`, `BlockBasedTableOptions::IndexType`, `BlockSearchType`, `DataBlockIndexType`, `IndexShorteningMode`, and `PrepopulateBlockCache`. `metadata_cache_options_type_info` and `block_based_table_type_info.info` describe all registered option names, offsets, option kinds, verification behavior, serialization flags, and custom parsers. Notable custom behavior includes dynamic cache construction through `Cache::CreateFromString()`, custom/shared pointer loading for policies/factories, and a compatibility parser for the historical `read_amp_bytes_per_bit` OPTIONS-file bug that reads a `uint64_t` string into a `uint32_t` field.

`BlockBasedTableFactory::BlockBasedTableFactory()` copies the incoming `BlockBasedTableOptions`, initializes defaults/sanitization, registers option metadata, and creates a `ConcurrentCacheReservationManager` for `CacheEntryRole::kBlockBasedTableReader` when block cache exists and table-reader memory charging is enabled.

`InitializeOptions()` installs default `FlushBlockBySizePolicyFactory`, chooses/clears the block cache depending on `no_block_cache`, creates the default 32 MiB `HyperClockCache` when no cache is supplied, clamps invalid block-size deviation and restart intervals, forces hash index restart interval to `1`, disables partitioned filters without two-level index search, resolves fallback cache-usage charging decisions, and raises too-old writable block-based table format versions to the minimum supported write version except for special test allowances.

`CheckCacheOptionCompatibility()` is a local helper that prevents regular block cache and persistent cache from sharing an underlying key space. It inserts a process-unique sentinel into both caches and then verifies each lookup returns the expected marker, returning `InvalidArgument` for overlapping caches and `Corruption` for unexpected mutation.

`NewTableReader()` forwards table-reader construction to `BlockBasedTable::Open()` with the sanitized options, immutable options, env options, comparator, file reader, file size, tail size, compression manager, filter-skip flag, level/lifetime metadata, direct prefetch flag, shared tail prefetch stats, block-cache tracer, L0 metadata pin sizing, DB session/file identity, persisted timestamp flag, and `avoid_shared_metadata_cache`.

`NewTableBuilder()` constructs a `BlockBasedTableBuilder` with the factory's options and the supplied writable file. `ValidateOptions()` checks the table option matrix against DB/column-family options. `GetPrintableOptions()` serializes a human-readable option dump including nested cache options. `GetOptionsPtr()` exposes the block cache option pointer unless block cache is disabled. `ParseOption()` wraps base parsing and keeps legacy escaped string behavior for named custom options. `GetBlockBasedTableOptionsFromString()`, `GetBlockBasedTableOptionsFromMap()`, `NewBlockBasedTableFactory()`, and `UserDefinedIndexFactory::CreateFromString()` provide public convenience/configuration hooks.

The file also defines property-name and metadata-block constants such as `BlockBasedTablePropertyNames::kIndexType`, `kHashIndexPrefixesBlock`, `kHashIndexPrefixesMetadataBlock`, `kPropTrue`, and `kPropFalse`.

## Control Flow
Factory construction follows a deterministic sequence: copy options, normalize them in `InitializeOptions()`, register the option metadata table, then optionally create shared table-reader memory reservation state from cache usage options. Later `PrepareOptions()` reruns `InitializeOptions()` before delegating to `TableFactory::PrepareOptions()`.

Reader creation is a thin but critical bridge: `NewTableReader()` does not parse table contents itself; it packages all validated options and shared factory state into `BlockBasedTable::Open()`. Builder creation is similarly direct, returning a raw `TableBuilder*` allocated as `BlockBasedTableBuilder`.

Validation is a long fail-fast chain. It first checks indexing prerequisites, cache/pinning requirements, and format-version support. It then evaluates compression compatibility, including custom `CompressionManager` restrictions for format versions below 7 and `block_align` incompatibility with compression. After physical size/alignment checks, it validates data-block hash-index utilization, user-defined index constraints, unordered-write merge constraints, cache-entry memory charging support, blob-cache relationships, cache key-space compatibility, checksum enum serialization, and finally the base `TableFactory` validation.

Option parsing flows through RocksDB's configurable-option system. The static `OptionTypeInfo` table maps strings to struct offsets and parsers, `ConfigureFromMap()` is driven by that table through the inherited configurable interface, and the convenience functions either parse a semicolon/string map or map directly before copying the factory's resulting `BlockBasedTableOptions` back to the caller.

## State And Persistence Behavior
`BlockBasedTableFactory` owns a copy of `BlockBasedTableOptions`; initialization mutates that copy to safe defaults and compatibility-preserving values. Cloned factories share `SharedState`, so `TailPrefetchStats` samples and the table-reader cache reservation manager are shared across clones rather than reset on every clone.

`TailPrefetchStats` is in-memory runtime state only. It is protected by `port::Mutex`, records at most 32 recent tail effective sizes, and does not persist to OPTIONS or table files. It influences future opens through `BlockBasedTable::Open()` receiving `tail_prefetch_stats`.

The option metadata controls persistence of table options in configuration strings and OPTIONS files. Fields with `kDontSerialize` or `kCompareNever`, such as cache object pointers, are intentionally excluded from serialized equality/OPTIONS behavior. Deprecated fields remain registered so older option strings can be parsed or ignored in a controlled way.

## Dependencies And Integration Points
This implementation depends on the cache subsystem (`Cache`, cache entry roles, `CacheReservationManager`), RocksDB option/configuration helpers, block-based table reader/builder types, filter/flush/user-defined-index extension points, compression manager compatibility checks, string parsing utilities, and table format constants.

It integrates upward with public APIs through `NewBlockBasedTableFactory()`, `GetBlockBasedTableOptionsFromString()`, `GetBlockBasedTableOptionsFromMap()`, and the `TableFactory` virtual interface. It integrates downward with `BlockBasedTable::Open()` for SST reads and `BlockBasedTableBuilder` for SST writes. It also integrates with cache tracing, metadata cache charging, persistent cache, blob cache memory charging, custom object loading, and user-defined indexes.

## Risks And Edge Cases
Several options are silently normalized rather than rejected during initialization, including invalid restart intervals, invalid block size deviation, hash-index restart interval incompatibility, and partitioned filters without partitioned indexes. This preserves historical behavior but can hide user configuration mistakes until option printing or validation is inspected.

The static option table marks many options mutable while the comment documents an unresolved read/write race for `SetOptions()` on block-based table option fields, especially pointer or larger fields. Callers relying on runtime mutation need to account for this known concurrency risk.

`CheckCacheOptionCompatibility()` intentionally mutates caches with a sentinel to detect shared key spaces. It uses a process-lifetime unique cache key, but any cache implementation with surprising insert/lookup semantics can cause validation failures or corruption statuses.

Compression and format-version validation is sensitive: custom compression managers require format-version support for storing the manager name; `block_align` conflicts with any enabled compression; and non-built-in compression types are rejected when using built-in-compatible compression managers. Tests need to cover both default and custom manager paths.

User-defined index support has explicit restrictions: no parallel compression, no primary UDI with two-level index or partitioned filters, and `use_udi_as_primary_index` requires a configured factory. These constraints protect layouts that the UDI wrapper cannot represent.

Cache-entry charging validation only supports a specific role set, and blob-cache charging has additional capacity and identity restrictions relative to the block cache. Misconfiguration returns `InvalidArgument`.

## Test Signals
Useful test coverage should include default option initialization, no-block-cache behavior, default HyperClockCache installation, option string/map parsing including deprecated or legacy `read_amp_bytes_per_bit` values, printable option output, and validation failures for hash index without prefix extractor, interpolation search with a non-bytewise comparator, cache-index options without block cache, unsupported format versions, `block_align` with compression, non-power-of-two alignments, invalid hash-table utilization ratio, UDI incompatibilities, and blob-cache charging constraints.

Cache compatibility tests should use distinct caches, intentionally shared/wrapped caches, and persistent cache implementations to verify `CheckCacheOptionCompatibility()`. Tail prefetch tests should exercise no-sample return, ring-buffer wraparound, sorted sample selection under the one-eighth-waste rule, and the 512 KiB cap. Reader/builder integration tests should verify `NewTableReader()` passes tail prefetch and cache reservation shared state into `BlockBasedTable::Open()` and that `Clone()` preserves shared state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.h -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.h

## Purpose
`block_based_table_factory.h` declares the public block-based SST table factory interface used by RocksDB to build and open block-based tables. It also declares `TailPrefetchStats`, a small shared runtime helper for adapting table-open tail prefetch sizes from recent open behavior.

## Important APIs, Types, And Functions
`TailPrefetchStats` exposes `RecordEffectiveSize(size_t len)` and `GetSuggestedPrefetchSize()`. Internally it stores `kNumTracked == 32` sample slots, a `port::Mutex`, and ring-buffer cursors `next_` and `num_records_`. The API is intentionally minimal: callers can record observed effective read lengths and ask for a suggested future prefetch size, with `0` meaning insufficient information.

`BlockBasedTableFactory` derives from `TableFactory`. Its constructor accepts `BlockBasedTableOptions` by const reference with a default-constructed default. `kClassName()` and `Name()` identify the factory as `kBlockBasedTableName()`, supporting RocksDB's checked-cast/configurable factory machinery.

The table construction API consists of `NewTableReader()` and `NewTableBuilder()`. The reader override accepts `ReadOptions`, `TableReaderOptions`, a `RandomAccessFileReader`, file size, destination `unique_ptr<TableReader>`, and a `prefetch_index_and_filter_in_cache` flag. The builder override accepts `TableBuilderOptions` and a `WritableFileWriter*`.

Configuration APIs include `ValidateOptions()`, `PrepareOptions()`, `GetPrintableOptions()`, protected `GetOptionsPtr()`, protected `ParseOption()`, and private `InitializeOptions()`. `IsDeleteRangeSupported()` returns true. `Clone()` returns a copy of the factory using `std::make_unique<BlockBasedTableFactory>(*this)`.

`tail_prefetch_stats()` exposes a pointer to the shared tail prefetch stats stored in `SharedState`. `SharedState` also carries a shared pointer to `CacheReservationManager`, allowing cloned factories to share cache memory reservation accounting for table readers.

The header declares extern metadata/property strings: `kHashIndexPrefixesBlock`, `kHashIndexPrefixesMetadataBlock`, `kPropTrue`, and `kPropFalse`.

## Control Flow
Consumers instantiate `BlockBasedTableFactory`, typically through the public RocksDB factory helper declared elsewhere and implemented in the `.cc` file. The factory is then used by column-family/table-building code through the virtual `TableFactory` interface. For reads, `NewTableReader()` opens an SST through the block-based reader implementation. For writes, `NewTableBuilder()` creates a block-based table builder.

Option lifecycle is exposed as prepare, validate, parse, and print hooks. `PrepareOptions()` normalizes and prepares options before validation/configuration use. `ValidateOptions()` rejects incompatible combinations with DB and column-family options. `ParseOption()` supports string/map configuration, and `GetOptionsPtr()` lets configurable infrastructure reach nested option objects such as block cache settings.

## State And Persistence Behavior
`table_options_` is the factory's owned option copy. It is the persistent configuration carrier from the factory's perspective, although individual option fields may point to external/shared objects such as caches, filter policies, or custom factories.

`shared_state_` is a `std::shared_ptr`, so a default copy or `Clone()` shares table-reader cache reservation state and tail prefetch history. This is significant for runtime behavior because cloned table factories are not independent for those adaptive/accounting components.

`TailPrefetchStats` state is volatile and synchronized. It is not serialized in table files or OPTIONS files, but it can affect later table opens while the process and shared factory state live.

## Dependencies And Integration Points
The header depends on RocksDB public table APIs (`rocksdb/table.h`), flush block policy APIs, DB/column-family option forward declarations, cache reservation management, port mutexes, and file reader/writer forward declarations.

Its main integration point is the `TableFactory` abstraction used by RocksDB column families. `BlockBasedTableFactory` is the concrete implementation for the default block-based SST format and connects option validation, reader creation, builder creation, delete-range support, and configurable object support.

## Risks And Edge Cases
The destructor is non-owning beyond standard smart-pointer fields and is declared empty. The builder API returns a raw `TableBuilder*`, so ownership transfer follows the `TableFactory` contract and callers must delete through the expected RocksDB ownership path.

`tail_prefetch_stats()` returns a raw pointer into shared state. The pointed object remains valid as long as the factory/shared state remains alive, but callers should not retain it past the owning factory graph lifetime.

`Clone()` shares `SharedState` because the default copy constructor copies `shared_state_`. This is intentional, but tests and callers should not assume clone isolation for table-reader cache reservations or tail prefetch stats.

## Test Signals
Header-level behavior is exercised through construction, clone, and virtual-interface tests. Useful checks include factory name/class name matching, delete-range support returning true, cloned factories sharing `tail_prefetch_stats()` behavior, default construction being usable without explicit options, and compile-time integration with `TableFactory::NewTableReader` overloads.

`TailPrefetchStats` should be tested for thread-safe recording, no-information return value, bounded sample retention, and stability after more than 32 records.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.cc -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.cc

## Purpose
`block_based_table_iterator.cc` implements `BlockBasedTableIterator`, the internal iterator over data entries in a block-based SST. It coordinates the index iterator, data-block iterator, prefix filters, upper-bound checks, block cache lookup, readahead and async prefetching, lazy value preparation from first-key-in-index metadata, backward iteration, and MultiScan prefetch/read-set execution.

## Important APIs, Types, And Functions
`SeekToFirst()`, `Seek()`, and `SeekImpl()` implement forward positioning. `SeekImpl()` handles MultiScan constraints, prefix capture for readahead trimming, async two-pass seeks, block-cache readahead lookup setup, prefix filter checks, index seek elision when reseeking within the current block, lazy first-key positioning when `allow_unprepared_value_` is enabled, data-block initialization, block seek, forward key discovery, upper-bound checks, and seek-order assertions.

`SeekSecondPass()` completes an async seek after `AsyncInitDataBlock()` has submitted an asynchronous read and the caller retries the seek. `SeekForPrev()` and `SeekToLast()` implement backward positioning and disable MultiScan/readahead-cache lookup state that is only valid for forward movement.

`Next()`, `NextAndGetResult()`, and `Prev()` implement movement. `Next()` materializes deferred first-key positions if needed, advances the data-block iterator, finds the next valid key/block, and checks bounds. `Prev()` restores the original index iterator if MultiScan or cache-lookup-ahead moved the index away from the current block, handles deferred first-key positions by moving to the previous index entry, then scans backward through blocks with `FindKeyBackward()`.

`InitDataBlock()` has two paths. In MultiScan mode, it reads the current block from `ReadSet` using the `MultiScanIndexIterator`'s current read-set index and enforces `prefetch_max_idx_`, returning EOF-like behavior when no max prefetch limit is set or `PrefetchLimitReached` when the configured limit is exceeded. In regular mode it chooses the current `BlockHandle` either from queued block handles produced by cache lookup-ahead or from `index_iter_->value()`, resets stale block iterators, invokes `BlockPrefetcher::PrefetchIfNeeded()`, and creates a `DataBlockIter` through `BlockBasedTable::NewDataBlockIterator()`.

`AsyncInitDataBlock()` mirrors regular block initialization but requests async IO on the first pass. If `NewDataBlockIterator()` returns `TryAgain`, it sets `async_read_in_progress_` and returns. On the second pass it polls/loads the block with async disabled and avoids a repeated block-cache lookup when appropriate.

`MaterializeCurrentBlock()` turns an `is_at_first_key_from_index_` position into a real data-block iterator. It initializes the block, seeks to first, and verifies the first key in the block matches the first internal key recorded in the index or cached `BlockHandleInfo`; mismatch is reported as corruption.

`FindKeyForward()`, `FindBlockForward()`, and `FindKeyBackward()` bridge between data blocks when the current block iterator becomes invalid. `FindBlockForward()` advances index state, handles readahead queued handles, respects iterate upper bounds, supports lazy first-key positions, and contains special MultiScan scan-range exhaustion handling. `CheckOutOfBound()` and `CheckDataBlockWithinUpperBound()` maintain upper-bound state.

`InitializeStartAndEndOffsets()` and `BlockCacheLookupForReadAheadSize()` implement auto readahead-size tuning by probing the block cache for upcoming blocks, pinning cache hits, queueing `BlockHandleInfo`, trimming read start/end offsets to miss ranges, stopping at prefix or upper-bound boundaries, and resetting previous block offset because index iteration has moved ahead.

`Prepare()` implements the MultiScan setup path. It records statistics, lets the index iterator prepare, collects block handles for all scan ranges, enforces `max_prefetch_size`, submits a sorted block-handle IO job to an `IODispatcher`, creates a `ReadSet`, wraps the collected handles in `MultiScanIndexIterator`, saves the original index iterator, and swaps the MultiScan iterator into `index_iter_`.

`CollectBlockHandles()` converts user scan ranges to internal start keys, walks the table index, collects block handles and separator keys, de-duplicates overlap with the previous range, handles the final possibly-overlapping limit block using `first_internal_key` when available, and records per-scan block index ranges.

## Control Flow
Forward seeks start by rejecting unsupported MultiScan `SeekToFirst()` calls and by recording the target prefix when `prefix_same_as_start` is active. If an async read is already in progress, the seek goes directly to `SeekSecondPass()`. Otherwise it clears cache-lookup-ahead state, optionally enables readahead cache probing, resets bound/lazy/stat state, checks prefix filters, and decides whether an index seek is required. A reseek inside the current block can avoid the index seek if the target user key is greater than the current data key and less than the index separator. After the index position is known, the iterator either defers block loading from first-key metadata or initializes/seeks the data block and then checks bounds.

Backward seeks always reset MultiScan, set direction to backward, clear readahead lookup, run prefix checks conservatively, seek the index using `Seek()` rather than `SeekForPrev()` to choose the likely containing block, handle prefix-index `NotFound`, load the block, then use `DataBlockIter::SeekForPrev()` or `SeekToLast()` followed by backward block discovery.

Regular data-block loading checks whether the requested block differs from `prev_block_offset_` or whether the previous block load was incomplete. It preserves pinned cleanups before invalidation, optionally uses queued cache-hit `CachableEntry<Block>` values, otherwise asks `BlockPrefetcher` to prefetch and then asks `BlockBasedTable` for a new data-block iterator. It also records seek-data statistics and later `value()` records whether a read block produced a useful value.

Forward block transitions reset the current data iterator, pop queued block handles when cache lookup-ahead is active, advance the index only when needed, terminate early if the next block is out of iterate upper bound, return an out-of-bound signal at MultiScan range boundaries, lazily expose first keys when allowed, and otherwise load the next data block and seek to first until a valid key is found or the index/data status stops iteration.

MultiScan preparation is a batch flow: collect all scan block handles, restrict the actually prefetched prefix by byte budget, submit a coalescible IO job, and replace the ordinary index iterator with `MultiScanIndexIterator`. Later `Seek()` calls must target the scan starts in order so the MultiScan index iterator can update range tracking; `InitDataBlock()` reads from the preloaded `ReadSet` instead of issuing ordinary block reads.

## State And Persistence Behavior
The iterator is entirely runtime state and does not persist changes to SST files. It stores references/pointers to table, read options, comparator, prefix extractor, pinned-iterator manager, block prefetcher, lookup context, current data-block iterator, and current index iterator.

Position state is split between `index_iter_`, `block_iter_`, `prev_block_offset_`, `block_iter_points_to_real_block_`, and `is_index_at_curr_block_`. These flags are essential because readahead lookup and MultiScan can move the index iterator ahead of the current data block.

Bound and lazy-value state includes `is_out_of_bound_`, `block_upper_bound_check_`, `is_at_first_key_from_index_`, `need_upper_bound_check_`, and `allow_unprepared_value_`. Lazy first-key mode lets callers observe keys from index metadata before a data block is loaded, but `PrepareValue()` or `value()` must materialize the block before value access.

Async state is tracked by `async_read_in_progress_`. While true, `status()` returns `TryAgain("Async read in progress")`, and the next seek performs the second pass.

Readahead auto-tuning state includes `readahead_cache_lookup_`, `block_handles_`, `seek_key_prefix_for_readahead_trimming_`, `is_index_out_of_bound_`, and `direction_`. `block_handles_` owns pinned cache entries and copied first-key slices for blocks discovered while probing ahead.

MultiScan state includes `multi_scan_status_`, `multi_scan_read_set_`, `multi_scan_index_iter_`, `original_index_iter_`, and `prefetch_max_idx_`. `ResetMultiScan()` drops the read set and wrapper, clears MultiScan errors, and restores the original index iterator when falling back to ordinary iteration.

## Dependencies And Integration Points
The implementation depends on `BlockBasedTable`, `BlockBasedTable::Rep`, `DataBlockIter`, `BlockPrefetcher`, `BlockHandle`, `CachableEntry<Block>`, `ReadOptions`, `InternalKeyComparator`, `UserComparatorWrapper`, prefix extractor/filter methods, cache lookup APIs, statistics tickers, `IODispatcher`, `IOJob`, `ReadSet`, `MultiScanIndexIterator`, and timestamp-aware key helpers.

It integrates upward with `DBIter`, `LevelIterator`, and merging iterators through the `InternalIteratorBase<Slice>` contract, including `PrepareValue()`, `NextAndGetResult()`, `UpperBoundCheckResult()`, pinned key/value reporting, status propagation, and MultiScan `Prepare()`. It integrates downward with table reader block lookup, block cache, prefetch buffers, async IO, and index implementations.

## Risks And Edge Cases
Lazy first-key mode is correctness-sensitive: `MaterializeCurrentBlock()` must verify the first data-block key matches the index first key, and `value()` asserts the block has already been materialized. Any caller that reads `value()` without respecting `PrepareValue()` would violate the contract.

Index/data iterator synchronization is subtle. Readahead cache lookup can advance `index_iter_` ahead of `block_iter_`, so `is_index_at_curr_block_`, queued `block_handles_`, and `prev_block_offset_` must be maintained carefully. Backward movement must clear this state and reseek the index.

Upper-bound behavior uses block separators and user-key comparisons without timestamps in some places. The code distinguishes current-block versus beyond-current-block bounds to avoid per-key checks when possible, but MultiScan bypasses the normal next-block out-of-bound shortcut because scan ranges use their own exhaustion logic.

Prefix filtering is disabled for backward direction when upper-bound checking is needed, because the prefix optimization would not be equivalent to total-order semantics. Prefix-based readahead trimming also depends on prefix extractor domain checks and fallback comparator behavior.

Async IO requires callers to retry the seek after `TryAgain`; mixed async, cache-hit queued handles, and prefetch buffers must avoid duplicate cache lookup and preserve correct block materialization.

MultiScan has explicit constraints: no `SeekToFirst()`, scan ranges should be non-overlapping and increasing, missing range limits are only safe for a single range, and internal reseeks by higher iterators are only expected to work when moving forward. `max_prefetch_size` can produce EOF-like behavior or `PrefetchLimitReached` depending on whether a limit is configured.

## Test Signals
Critical tests should cover forward seek, reseek within the same block, seek to first, seek for previous at block boundaries, seek to last, next/prev across empty or exhausted blocks, prefix-filter hit/miss statistics, upper-bound transitions within and beyond the current block, and pinned iterator cleanup delegation.

Lazy first-key tests should verify key visibility without value materialization, successful `PrepareValue()`, corruption on first-key mismatch, and `Next()` from a deferred position. Async tests should verify first-pass `TryAgain`, second-pass completion, status behavior, and interactions with block cache hits.

Readahead tests should exercise cache-hit/miss probing, trimming start/end offsets, prefix and upper-bound termination, index exhaustion while current block remains active, and direction reversal clearing lookup-ahead state. MultiScan tests should cover handle collection for bounded/unbounded ranges, overlapping range de-duplication, timestamped start-key creation, prefetch byte limits, range exhaustion signaling through `UpperBoundCheckResult()`, fallback on backward operations, and propagation of index/read-set errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.h -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.h

## Purpose
`block_based_table_iterator.h` declares `BlockBasedTableIterator`, RocksDB's internal iterator for walking the key/value entries of a `BlockBasedTable`. The declaration exposes the iterator contract used by upper layers and defines the private state machine for block loading, bounds, prefix filtering, pinning, readahead, async IO, lazy value preparation, and MultiScan.

## Important APIs, Types, And Functions
The constructor takes a `BlockBasedTable*`, long-lived `ReadOptions&`, `InternalKeyComparator&`, owned index iterator over `IndexValue`, filter and upper-bound behavior flags, prefix extractor, caller identity, optional compaction readahead size, and `allow_unprepared_value`. It initializes `BlockCacheLookupContext`, `BlockPrefetcher`, table level state, and MultiScan status.

The public iterator API overrides `Seek()`, `SeekForPrev()`, `SeekToFirst()`, `SeekToLast()`, `Next()`, `NextAndGetResult()`, `Prev()`, `Valid()`, `key()`, `user_key()`, `value()`, `status()`, `PrepareValue()`, `write_unix_time()`, `UpperBoundCheckResult()`, pinned-iterator hooks, readahead state get/set hooks, and `Prepare(const MultiScanArgs*)`.

`Valid()` requires not out-of-bound, MultiScan status OK, and either a deferred first-key-from-index position or a valid real data-block iterator. `key()` and `user_key()` switch between index first-key metadata and `DataBlockIter` depending on `is_at_first_key_from_index_`. `PrepareValue()` materializes a deferred block. `value()` records useful-seek statistics and returns the data-block value after materialization.

`write_unix_time()` parses the current internal key, handles unknown-before-all sequence/time sentinels, uses the table's `SeqnoToTimeMapping`, and for `kTypeValuePreferredSeqno` obtains the sequence number from the packed value before mapping it to a proximal write time.

`status()` prioritizes `multi_scan_status_`, then current index status when the index is expected to be at the current block, then data-block status, then async `TryAgain`, otherwise OK. `UpperBoundCheckResult()` exposes whether the iterator is known out of bound, known in bound for the current block, or unknown.

Pinning APIs report whether keys/values are pinned by the index value or block iterator and delegate block iterator cleanups to a `PinnedIteratorsManager` when resetting a real block. `GetReadaheadState()` and `SetReadaheadState()` transfer adaptive readahead state through `ReadaheadFileInfo`.

Private types include `IterDirection`, `BlockUpperBound`, `SeekStatState`, and `BlockHandleInfo`. Private helpers include `ResetMultiScan()`, `SeekSecondPass()`, `SeekImpl()`, `InitDataBlock()`, `AsyncInitDataBlock()`, `MaterializeCurrentBlock()`, block/key discovery functions, bound checks, prefix filter checks, readahead cache lookup helpers, and `CollectBlockHandles()` for MultiScan.

## Control Flow
The header defines a two-layer iteration model. The index iterator locates data blocks and provides `IndexValue` metadata; the data-block iterator walks entries inside a loaded block. Public seek/movement methods coordinate these layers through private helpers and state flags.

Lazy key exposure is part of the public contract: when `is_at_first_key_from_index_` is true, `key()` returns `index_iter_->value().first_internal_key`, and `PrepareValue()` must be called to initialize `block_iter_` before reading `value()`. This supports block cache readahead lookup and reduced data-block reads for callers that only need keys.

Bounds and prefix checks are split. `CheckPrefixMayMatch()` can skip data-block reads when the table filter says a prefix range cannot match, but it returns true for backward iteration when upper-bound checking is required. Upper-bound state is maintained separately through `block_upper_bound_check_` and `is_out_of_bound_`.

Readahead state has explicit reset and queue helpers. `ResetBlockCacheLookupVar()` clears out-of-bound readahead state, disables lookup-ahead, and clears queued block handles. `IsNextBlockOutOfReadaheadBound()` stops readahead at iterate upper bound or prefix boundary. `InitializeStartAndEndOffsets()` and `BlockCacheLookupForReadAheadSize()` are declared for implementation in the `.cc` file.

MultiScan state is declared as an optional replacement for the normal index iterator. `Prepare()` installs a `MultiScanIndexIterator`, while `ResetMultiScan()` releases the `ReadSet`, clears pointers and limits, permits/discards previous MultiScan errors, and restores the saved original index iterator.

## State And Persistence Behavior
The class keeps runtime-only iteration state. It does not persist data; it reads table blocks and reports iterator positions. `read_options_` is a reference that must outlive the iterator, making lifetime management important.

Core position state includes `index_iter_`, `block_iter_`, `prev_block_offset_`, `block_iter_points_to_real_block_`, and `is_index_at_curr_block_`. Correctness depends on knowing when the index iterator and block iterator refer to the same data block.

Adaptive/readahead state includes `block_prefetcher_`, optional `block_handles_`, prefix string `seek_key_prefix_for_readahead_trimming_`, `readahead_cache_lookup_`, `is_index_out_of_bound_`, and `direction_`. `BlockHandleInfo` owns copied first-key bytes so slices remain valid after index iterator movement.

Bound/filter/lazy state includes `allow_unprepared_value_`, `block_upper_bound_check_`, `is_at_first_key_from_index_`, `check_filter_`, `need_upper_bound_check_`, `is_out_of_bound_`, and `seek_stat_state_`. Async state is the boolean `async_read_in_progress_`.

MultiScan state includes a status object, shared `ReadSet`, raw pointer to the active `MultiScanIndexIterator`, saved original index iterator, and `prefetch_max_idx_`. The raw pointer is valid only while the unique pointer stored in `index_iter_` owns the MultiScan iterator.

## Dependencies And Integration Points
The declaration depends on sequence-number-to-time mapping, IO dispatcher types, block-based table reader internals, block prefetching, MultiScan index iteration, and reader common utilities. It uses RocksDB internal iterator, key parsing, comparator, slice transform, prefetch buffer, pinned iterator, statistics, and cache-entry abstractions through included headers.

Upper layers use this class through `InternalIteratorBase<Slice>` for scans, point/range iteration, compaction reads, and MultiScan. Lower layers are accessed through `BlockBasedTable` APIs for filters, data-block iterator creation, cache lookups, table statistics, sequence-to-time mapping, and table representation/options.

## Risks And Edge Cases
Because `index_iter_` is public, tests or nearby code can inspect or manipulate it directly; production correctness still assumes private methods maintain synchronization flags. Any direct mutation outside the class can invalidate assumptions.

The iterator stores several borrowed references and raw pointers: table, read options, comparator, prefix extractor, pinned manager, and MultiScan raw pointer. Lifetime and ownership must follow the table reader and iterator contracts.

`status()` deliberately ignores `index_iter_->NotFound()` for prefix indexes and only checks index status when the index is considered current. Bugs in `is_index_at_curr_block_` could hide or misattribute index errors.

`IsNextBlockOutOfReadaheadBound()` assumes `prefix_extractor_` is usable when `prefix_same_as_start` and a non-empty seek prefix are active. Constructor call sites must keep prefix extractor consistency with read options.

`ResetDataIter()` delegates cleanups when pinning is enabled, invalidates the block iterator, and clears upper-bound knowledge. Missing calls before block switches would risk pinned-resource lifetime bugs or stale bound answers.

MultiScan reset discards MultiScan errors when falling back to regular iteration. That is intentional for backward/fallback paths, but tests should verify real read errors are still visible while MultiScan remains active.

## Test Signals
Declaration-level contracts should be covered by iterator API tests for validity, status ordering, key/user-key sources in deferred versus materialized positions, value preparation, write-time mapping, upper-bound result states, pinning reports, readahead state transfer, and fallback from MultiScan to normal index iteration.

State-machine tests should explicitly exercise transitions among no real block, real block loaded, deferred first-key, async in-progress, index moved ahead by readahead lookup, out-of-bound, and MultiScan active. Tests should also verify cleanup delegation with pinned iterators and that `TEST_IsBlockPinnedByMultiScan()` reflects read-set availability only during active MultiScan.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.h -->
