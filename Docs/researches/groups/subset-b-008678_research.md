# subset-b-008678 Research

Grouped research report for RocksDB block-based table hash-index, filter, flush policy, index builder, and multi-scan iterator sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.cc -->
# sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.cc

## Purpose
Implements the compact per-data-block hash index declared in `data_block_hash_index.h`. The code builds a serialized bucket table appended to a data block and provides lookup-time decoding for `Block::SeekForGet`-style point lookup acceleration.

## Important APIs, Types, And Functions
`DataBlockHashIndexBuilder::Add` hashes each key with `GetSliceHash`, records the hash plus restart index, increments the bucket estimate, and invalidates the builder if the restart index exceeds `kMaxRestartSupportedByHashIndex`. `Finish` converts accumulated `(hash, restart)` pairs into `uint8_t` buckets and appends the bucket array plus a fixed16 bucket count. `Reset` clears accumulated state while preserving initialization. `DataBlockHashIndex::Initialize` decodes the bucket count from the tail and returns the hash-map offset. `Lookup` rehashes a query key and returns the stored bucket byte.

## Control Flow
The builder is initialized with a target utilization ratio, accepts one entry per restart interval key, and defers actual bucket assignment until `Finish`. `Finish` rounds the estimated bucket count up to an odd number to avoid poor distribution with power-of-two moduli, fills buckets with `kNoEntry`, stores a restart index for the first matching bucket, and replaces buckets with `kCollision` when different restart indexes map to the same bucket. The reader decodes `num_buckets_`, computes the bucket table start, then `Lookup` does a direct modulo lookup.

## State And Persistence Behavior
Persistent state is only bytes appended to the data block: one byte per bucket followed by a little-endian fixed16 bucket count. Builder state is transient: utilization inverse, floating bucket estimate, validity flag, and hash/restart pairs. `valid_` gates whether callers should append the hash index at all; the data block itself remains readable through binary search fallback.

## Dependencies And Integration Points
Depends on `Slice`, `GetSliceHash`, and fixed-width coding helpers. It integrates with `BlockBuilder` and `Block` data-block format selection, where the high bit of restart count marks hash-index presence and unsupported cases fall back to `kDataBlockBinarySearch`.

## Risks And Edge Cases
The implementation relies on block sizes fitting in `uint16_t` offsets and restart indexes fitting in one byte after reserving `254` and `255`. Hash collisions intentionally degrade to restart-interval search, not false negatives. A bad utilization ratio is normalized by the header-side initializer, but extreme bucket estimates still must stay under the 64KiB supported block-size invariant.

## Test Signals
`data_block_hash_index_test.cc` covers bucket offsets, collision markers, absent-key false-positive tolerance, max restart index invalidation, block-size fallback, and point lookup boundary behavior across adjacent data blocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.h -->
# sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.h

## Purpose
Defines RocksDB's experimental hash index embedded inside data blocks to reduce CPU cost for point lookups. The header documents the on-disk block layout extension and declares the builder and reader used by data-block construction and lookup.

## Important APIs, Types, And Functions
Constants `kNoEntry`, `kCollision`, `kMaxRestartSupportedByHashIndex`, `kMaxBlockSizeSupportedByHashIndex`, and `kDefaultUtilRatio` define encoding limits. `DataBlockHashIndexBuilder` exposes `Initialize`, `Valid`, `Add`, `Finish`, `Reset`, and `EstimateSize`. `DataBlockHashIndex` exposes `Initialize`, `Lookup`, and `Valid`.

## Control Flow
Callers create a builder, initialize it with a utilization ratio, add keys with their data-block restart indexes, check `Valid`, and append bytes through `Finish`. Readers detect hash-index presence from the data-block footer, initialize the `DataBlockHashIndex` over serialized block bytes, then ask `Lookup` for the probable restart interval before searching within the interval.

## State And Persistence Behavior
The persistent format is `HASH_IDX: [bucket bytes][fixed16 num_buckets]` appended before the data-block footer. Bucket bytes contain either a restart index, `kNoEntry`, or `kCollision`. The builder maintains transient hash/restart pairs and an estimated bucket count; only `Finish` emits bytes.

## Dependencies And Integration Points
The header depends on `rocksdb/slice.h` and is consumed by block builder/reader code and by tests. It is explicitly data-block-only and not intended for table index blocks or metadata blocks.

## Risks And Edge Cases
The format supports at most 253 restart intervals because bucket entries are `uint8_t` and reserve two sentinel values. Block offsets are `uint16_t`, so blocks at or above 64KiB cannot use this index. Collision and missing-entry handling must preserve correctness by falling back to normal restart-interval search.

## Test Signals
Friend access supports the small builder test. Coverage checks format sizing, restart limits, block-size limits, and lookup correctness with existing and non-existing keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_hash_index_test.cc -->
# sources/storage-engines/rocksdb/table/block_based/data_block_hash_index_test.cc

## Purpose
Exercises the embedded data-block hash index directly and through real `BlockBuilder`, `Block`, and table-reader paths. It verifies both serialized bucket behavior and correctness-preserving fallback when hash indexing is not supported.

## Important APIs, Types, And Functions
`SearchForOffset` interprets lookup results, allowing collisions as maybe-present and no-entry as absent. `GenerateKey` and `GenerateRandomKVs` produce sorted synthetic keys. Tests include `DataBlockHashTestSmall`, `DataBlockHashTest`, `DataBlockHashTestCollision`, `DataBlockHashTestLarge`, `RestartIndexExceedMax`, `BlockRestartIndexExceedMax`, `BlockSizeExceedMax`, `BlockTestSingleKey`, `BlockTestLarge`, and `BlockBoundary`. `TestBoundary` builds an in-memory block-based table and calls `TableReader::Get`.

## Control Flow
The direct builder tests add keys, call `EstimateSize`, append the hash index to a prefixed buffer, initialize a reader, and verify the returned map offset and bucket behavior. Block-level tests build data blocks with `kDataBlockBinaryAndHash`, inspect the resulting `Block::IndexType`, and run `SeekForGet`. Boundary tests build two large key/value pairs so each lands in its own data block, then query with different sequence numbers to validate cross-block search decisions.

## State And Persistence Behavior
Most tests use transient strings and in-memory block contents. `TestBoundary` writes a full block-based table into a `StringSink`, reopens it through `StringSource`, and checks `GetContext` state and returned `PinnableSlice` value. No external filesystem persistence is required.

## Dependencies And Integration Points
Depends on block construction, table factory/options, `InternalKey`, `GetContext`, `TableBuilder`, `TableReader`, test harness utilities, and random data generation. It is the primary regression suite linking the small hash-index format to block-based table lookup behavior.

## Risks And Edge Cases
The tests emphasize collision tolerance, false positives for absent keys, invalidation above restart index 253, fallback above the 64KiB block limit, and sequence-number-sensitive searches at block boundaries. The direct collision test does not require exact no-entry behavior for absent keys because Bloom-like false positives are allowed by design.

## Test Signals
Signals are `IndexType` selecting hash versus binary search, `SeekForGet` `may_exist` and iterator validity combinations, correct values for existing keys, and `GetContext` found/not-found states across adjacent blocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_hash_index_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_block.h -->
# sources/storage-engines/rocksdb/table/block_based/filter_block.h

## Purpose
Declares the abstract filter block builder and reader interfaces used by block-based tables. It provides a common contract for full filters, partitioned filters, plugin filter policies, point lookups, prefix checks, multi-get pruning, range existence checks, memory accounting, and cache lifecycle hooks.

## Important APIs, Types, And Functions
`FilterBlockBuilder` defines `Add`, `AddWithPrevKey`, `IsEmpty`, `EstimateEntriesAdded`, `CurrentFilterSizeEstimate`, `OnDataBlockFinalized`, `PrevKeyBeforeFinish`, `Finish`, `ResetFilterBitsBuilder`, and `MaybePostVerifyFilter`. `FilterBlockReader` defines `KeyMayMatch`, `KeysMayMatch`, `PrefixMayMatch`, `PrefixesMayMatch`, `ApproximateMemoryUsage`, `ToString`, `CacheDependencies`, `EraseFromCacheBeforeDestruction`, and `RangeMayExist`. `MultiGetRange` aliases `MultiGetContext::Range`.

## Control Flow
Table builders feed keys without timestamps into a concrete builder, optionally with previous-key context for partitioned range logic, then repeatedly call `Finish` until a full or partitioned filter is complete. Readers answer maybe-match queries: the base multi-get helpers loop through a range and call single-key methods, skipping keys when filters return false.

## State And Persistence Behavior
This header defines interfaces, not concrete storage. The `Finish` contract specifies ownership and lifetime of returned filter bytes, including optional transfer through `filter_owner`, and supports partitioned filters through `Status::Incomplete` plus the last partition block handle.

## Dependencies And Integration Points
Integrates with `FilterPolicy`, `GetContext`, `ReadOptions`, `BlockCacheLookupContext`, `FilePrefetchBuffer`, `SliceTransform`, `Comparator`, `BlockHandle`, and `MultiGetContext`. It is consumed by full-filter, partitioned-filter, and table-reader code.

## Risks And Edge Cases
Implementations must preserve no-false-negative semantics: read failures, missing filters, or unsupported filter formats should generally return maybe-present. `AddWithPrevKey` introduces sequencing constraints, and callers using it must call `PrevKeyBeforeFinish` when required. Multi-get skipping depends on safe iterator mutation through `MultiGetRange::SkipKey`.

## Test Signals
Signals come through full-filter and partitioned-filter tests, multi-get filter pruning, cache dependency tests, and table-reader point/range lookup behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.cc -->
# sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.cc

## Purpose
Implements common cache-aware logic shared by full and partitioned filter block readers. It centralizes reading filter blocks, accessing table filter options, range-prefix compatibility checks, memory accounting, and cache eviction before destruction.

## Important APIs, Types, And Functions
Template methods include `ReadFilterBlock`, `table_prefix_extractor`, `whole_key_filtering`, `cache_filter_blocks`, `GetOrReadFilterBlock`, `ApproximateFilterBlockMemoryUsage`, `RangeMayExist`, `IsFilterCompatible`, and `EraseFromCacheBeforeDestruction`. The file explicitly instantiates the template for `Block_kFilterPartitionIndex` and `ParsedFullFilterBlock`.

## Control Flow
`GetOrReadFilterBlock` first reuses a pinned/owned `filter_block_` when present; otherwise it calls `ReadFilterBlock`, which delegates to `BlockBasedTable::RetrieveBlock` using the table's filter handle. `RangeMayExist` uses the caller's prefix extractor to transform the queried user key, checks upper-bound compatibility when requested, and delegates to `PrefixMayMatch` only when the entire iterator range can be safely represented by the same prefix.

## State And Persistence Behavior
The class does not persist data. It manages ownership or cache references through `CachableEntry<TBlocklike>` and can erase a cached filter block when `uncache_aggressiveness` is positive. Prefix extractor full-length metadata is cached at construction time in the header-side object.

## Dependencies And Integration Points
Depends on `BlockBasedTable`, `RetrieveBlock`, perf timers, block cache lookup context, `ParsedFullFilterBlock`, and prefix comparator APIs including timestamp-aware `CompareWithoutTimestamp` and `IsSameLengthImmediateSuccessor`. Full-filter and partitioned-filter readers inherit this behavior.

## Risks And Edge Cases
Upper-bound compatibility is subtle: using a prefix filter for a range whose upper bound crosses into another prefix would cause false negatives, so the code falls back to maybe-present. Read errors also fall back to maybe-present through callers. Cache erasure must distinguish entries owned by the reader versus entries only present in the table cache.

## Test Signals
Indirectly covered by full-filter, partitioned-filter, iterator upper-bound, cache pinning, and table-reader prefix seek tests. Perf counters around filter-block reads can reveal cache or IO regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.h -->
# sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.h

## Purpose
Declares `FilterBlockReaderCommon`, a templated base class that lets full and partitioned filter readers share table access, cached block ownership, range compatibility, and cache cleanup behavior while still exposing the `FilterBlockReader` interface.

## Important APIs, Types, And Functions
The constructor accepts a `BlockBasedTable` and movable `CachableEntry<TBlocklike>`, then records full-length prefix-extractor support. Public overrides are `RangeMayExist` and `EraseFromCacheBeforeDestruction`. Protected helpers include `ReadFilterBlock`, `table`, `table_prefix_extractor`, `whole_key_filtering`, `cache_filter_blocks`, `GetOrReadFilterBlock`, and `ApproximateFilterBlockMemoryUsage`.

## Control Flow
Derived readers call protected helpers when they need filter data. The base class decides whether to use an already held filter block or load it through the table/cache. For iterator range filtering, callers enter `RangeMayExist`, which performs prefix-domain and upper-bound checks before invoking derived `PrefixMayMatch`.

## State And Persistence Behavior
State is a non-owning table pointer, a `CachableEntry` that may own or reference a cached filter block, and prefix-extractor length flags. No durable table bytes are modified.

## Dependencies And Integration Points
Depends on `cachable_entry.h`, `filter_block.h`, `BlockBasedTable`, and `FilePrefetchBuffer`. It is the shared base for `FullFilterBlockReader` and partitioned filter readers using `Block_kFilterPartitionIndex`.

## Risks And Edge Cases
The constructor assumes the table and table representation are valid for the reader lifetime. Derived readers must not misuse `GetOrReadFilterBlock` after table teardown. Prefix full-length metadata is captured once, so it must match the immutable table prefix extractor.

## Test Signals
Coverage is indirect through readers that inherit it, especially cache pin/unpin behavior, prefix range pruning, and upper-bound compatibility tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_policy.cc -->
# sources/storage-engines/rocksdb/table/block_based/filter_policy.cc

## Purpose
Implements RocksDB built-in Bloom-like filter policies, including legacy Bloom, fast local Bloom, Standard128 Ribbon, read-only built-in compatibility, string/object-library construction, metadata decoding, and corruption post-verification hooks.

## Important APIs, Types, And Functions
Anonymous builders/readers include `XXPH3FilterBitsBuilder`, `FastLocalBloomBitsBuilder`, `FastLocalBloomBitsReader`, `Standard128RibbonBitsBuilder`, `Standard128RibbonBitsReader`, `LegacyBloomBitsBuilder`, `LegacyBloomBitsReader`, `AlwaysTrueFilter`, and `AlwaysFalseFilter`. Policy methods include `BloomFilterPolicy::GetBuilderWithContext`, `RibbonFilterPolicy::GetBuilderWithContext`, `BuiltinFilterPolicy::GetBuiltinFilterBitsReader`, `GetBloomBitsReader`, `GetRibbonBitsReader`, `FilterPolicy::CreateFromString`, `NewBloomFilterPolicy`, `NewRibbonFilterPolicy`, and test-only fixed-implementation factories.

## Control Flow
`BloomLikeFilterPolicy` sanitizes bits-per-key, computes millibits/key, whole bits/key, and Ribbon target false-positive rate. Bloom policy chooses legacy Bloom for table format versions before 5 and fast local Bloom otherwise. Ribbon policy chooses Bloom before configured levels or Ribbon for lower/bottom levels. Builders hash keys, de-duplicate adjacent key or prefix hashes, allocate rounded filter storage, write filter bits, append five bytes of metadata, and optionally verify hash-entry checksums and post-verify every saved hash against the constructed filter. Readers inspect the metadata trailer: positive first byte means legacy Bloom, `-1` means new Bloom, `-2` means Ribbon, zero/reserved/invalid encodings return safe fallback readers.

## State And Persistence Behavior
Persistent filter content consists of raw filter bits plus a five-byte built-in metadata trailer. Legacy Bloom stores num probes and num cache lines. Fast local Bloom stores `-1`, subimplementation `0`, probe count/block-size bits, and reserved zero bytes. Standard128 Ribbon stores `-2`, seed, and a 24-bit block count. Runtime state includes cached hash entries, optional cache-reservation handles for construction memory, aggregate rounding balance for `optimize_filters_for_memory`, and atomic mutable `bloom_before_level`.

## Dependencies And Integration Points
Depends on Bloom math/implementations, Ribbon implementations, cache reservation manager, block-based table options, object registry, configuration parsing, logging, sync-point testing, `malloc_usable_size`, and table creation context. Full-filter and partitioned-filter builders use `FilterPolicy::GetBuilderWithContext`; parsed filter blocks use `GetFilterBitsReader` to read existing files across implementation changes.

## Risks And Edge Cases
The implementation must never turn malformed or future filter metadata into false negatives, so reserved or invalid reader formats generally become always-true. Empty or too-short filters become always-false to represent zero added keys, while higher-level readers preserve legacy semantics by treating empty-plugin readers conservatively. Memory-optimized rounding must avoid unexpectedly high false-positive rates. Ribbon construction can fall back to Bloom for too many keys, small filters, cache-charge failure, or seed-solving failure. Corruption-detection code must release hash-entry memory after failures or post-verification.

## Test Signals
Signals include Bloom/Ribbon unit tests elsewhere, full-filter tests in this subset, object-library creation tests, corruption construction sync points, false-positive-rate/space tests, and compatibility tests that read filters written by different built-in implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_policy_internal.h -->
# sources/storage-engines/rocksdb/table/block_based/filter_policy_internal.h

## Purpose
Declares the internal filter-building and filter-reading abstractions behind RocksDB's public `FilterPolicy`, plus built-in Bloom-like policy classes that can read all built-in filter formats.

## Important APIs, Types, And Functions
`FilterBitsBuilder` defines `AddKey`, `AddKeyAndAlt`, `EstimateEntriesAdded`, `Finish`, corruption-aware `Finish`, `MaybePostVerify`, `ApproximateNumEntries`, `CalculateSpace`, and `EstimatedFpRate`. `FilterBitsReader` defines single and batch `MayMatch`. `BuiltinFilterBitsReader` adds `HashMayMatch`. `BuiltinFilterPolicy`, `ReadOnlyBuiltinFilterPolicy`, and `BloomLikeFilterPolicy` provide compatibility reading and builder creation. `BloomFilterPolicy`, `RibbonFilterPolicy`, and test-only `LegacyBloomFilterPolicy`, `FastLocalBloomFilterPolicy`, and `Standard128RibbonFilterPolicy` specialize builder selection.

## Control Flow
Table builders call a policy's `GetBuilderWithContext`, add whole keys and/or prefixes through the returned builder, then call `Finish` and optional post-verification. Table readers pass raw filter contents to `GetFilterBitsReader`, which returns an implementation-specific reader. Configuration code can create shared policies from strings via registered names.

## State And Persistence Behavior
The header itself has no persistence, but its contracts define how many entries are reported to table properties, how filter bytes are owned by a returned buffer, and how built-in filters remain compatible across format changes. `RibbonFilterPolicy` persists mutable option state in `bloom_before_level_` and registers it for option parsing.

## Dependencies And Integration Points
Depends on public `rocksdb/filter_policy.h`, block-based table options, cache-related context, and RocksDB configurable/customizable support. It is included by full-filter, partitioned-filter, mock table tests, and filter policy implementation.

## Risks And Edge Cases
Custom builders must honor no-false-negative semantics and accurately return zero entries only when no entries were added. `AddKeyAndAlt` has stricter de-duplication expectations than two independent `AddKey` calls. `MaybePostVerify` is optional but, when enabled, must not leave corrupted filters in use.

## Test Signals
Tests use the fixed implementation classes to force legacy Bloom, fast local Bloom, and Ribbon paths. Full-filter tests use custom plugin `FilterBitsBuilder`/`FilterBitsReader` implementations to verify the contract is not limited to built-in policies.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/filter_policy_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/flush_block_policy.cc -->
# sources/storage-engines/rocksdb/table/block_based/flush_block_policy.cc

## Purpose
Implements block flush policy factories for block-based table building. The main policy cuts data or metadata blocks based on estimated block size, optional deviation thresholds, and block-alignment settings.

## Important APIs, Types, And Functions
`FlushBlockBySizePolicy` implements `FlushBlockPolicy::Update` and private `BlockAlmostFull`. `FlushBlockBySizePolicyFactory::NewFlushBlockPolicy` creates policies from table options or explicit size/deviation parameters. `NewFlushBlockBySizePolicy` returns a retargetable size policy for internal partitioned-index use. `RegisterFlushBlockPolicyFactories` registers size and every-key factories. `FlushBlockPolicyFactory::CreateFromString` loads policies through the object registry.

## Control Flow
`Update` refuses to flush an empty block. It then checks whether the current estimate already exceeds `block_size_` or whether appending the candidate key/value would exceed the target while the current block is past the deviation limit. With block alignment enabled, it adds the block trailer size before comparing to the target.

## State And Persistence Behavior
Policy state is transient: target block size, computed deviation limit, alignment flag, and a pointer to the current `BlockBuilder` supplied by the retargetable base. It influences on-disk block boundaries but does not write bytes itself.

## Dependencies And Integration Points
Depends on public flush policy interfaces, block-based table options, `BlockBuilder` size estimates, block trailer size, and object-library registration. Partitioned index construction uses `NewFlushBlockBySizePolicy` and retargets it as new sub-index builders are created.

## Risks And Edge Cases
Incorrect size estimates can produce blocks larger or smaller than expected, but correctness is preserved. Empty-block protection prevents infinite flush loops. Retargetable policies must always point to a live builder before `Update` is called.

## Test Signals
Coverage is indirect through block-builder/table-builder tests, partitioned index partition-size tests, and configurable factory loading tests. `FlushBlockEveryKeyPolicyFactory` supports deterministic test block boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/flush_block_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/flush_block_policy_impl.h -->
# sources/storage-engines/rocksdb/table/block_based/flush_block_policy_impl.h

## Purpose
Declares internal flush block policies used by block-based table building and tests. It includes a deterministic every-key policy and a retargetable base used when one policy object must follow different `BlockBuilder` instances.

## Important APIs, Types, And Functions
`FlushBlockEveryKeyPolicy` returns false for the first key and true for every subsequent key. `FlushBlockEveryKeyPolicyFactory` creates that policy and exposes `kClassName`. `RetargetableFlushBlockPolicy` stores a `BlockBuilder` pointer and exposes `Retarget`. `NewFlushBlockBySizePolicy` constructs a size-based retargetable policy.

## Control Flow
The every-key policy is stateful only for the first update. Retargetable policies are constructed with one block builder and can later be redirected before update checks, which lets partitioned index code reuse one flush-policy object across sub-index builders.

## State And Persistence Behavior
No persistence occurs in this header. The every-key policy stores a boolean `start_`; the retargetable base stores a non-owning `BlockBuilder` pointer.

## Dependencies And Integration Points
Depends on public `rocksdb/flush_block_policy.h` and is implemented by `flush_block_policy.cc`. Used by table-builder code, tests, and partitioned index builder partition cutting.

## Risks And Edge Cases
Because the retargeted builder pointer is non-owning, lifetime and retarget timing are critical. The every-key policy is intended for tests, not production tuning, because it creates very small blocks.

## Test Signals
Factory registration and block-boundary tests can force one key per block. Partitioned-index tests exercise retargeting through size-policy reuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/flush_block_policy_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/full_filter_block.cc -->
# sources/storage-engines/rocksdb/table/block_based/full_filter_block.cc

## Purpose
Implements full-table filter block building and reading for block-based tables. A full filter contains one filter over all keys and/or prefixes in the SST file and is used to avoid unnecessary data-block reads.

## Important APIs, Types, And Functions
`FullFilterBlockBuilder` implements `EstimateEntriesAdded`, `OnDataBlockFinalized`, `CurrentFilterSizeEstimate`, `UpdateFilterSizeEstimate`, `AddWithPrevKey`, `Add`, and `Finish`. `FullFilterBlockReader` implements `Create`, `KeyMayMatch`, `PrefixMayMatch`, `KeysMayMatch`, `PrefixesMayMatch`, private single and batch `MayMatch`, and `ApproximateMemoryUsage`.

## Control Flow
The builder receives user keys without timestamps. If a prefix extractor exists and accepts the key, it adds the prefix and optionally the whole key through `AddKeyAndAlt`; otherwise it adds only the whole key when whole-key filtering is enabled. `Finish` delegates to the configured `FilterBitsBuilder` and returns its status. The reader creation path can prefetch or pin the parsed full filter, or create a lazy reader that loads the block from cache/table on first use. Query paths call `GetOrReadFilterBlock`, obtain the `FilterBitsReader`, then update bloom hit/miss counters and prune keys/ranges on false.

## State And Persistence Behavior
Persistent bytes are whatever the selected `FilterBitsBuilder` returns for the full filter block. Runtime builder state includes a `FilterBitsBuilder`, optional owned filter bytes, and a cached size estimate. Reader state is inherited from `FilterBlockReaderCommon` and may own, pin, or lazily read a `ParsedFullFilterBlock`.

## Dependencies And Integration Points
Depends on `FilterBitsBuilder`, `FilterBitsReader`, `ParsedFullFilterBlock`, `BlockBasedTable::RetrieveBlock`, perf counters, prefix extractors, cache entries, and read options. It is used by block-based table builders/readers when partitioned filters are not selected.

## Risks And Edge Cases
Read errors and missing filter readers must return maybe-present to avoid false negatives. Empty full filters keep legacy semantics where `KeyMayMatch` can return true at the block-reader layer. Batch filtering must keep arrays aligned with the filtered `MultiGetRange`, especially when some keys are outside the prefix extractor domain.

## Test Signals
`full_filter_block_test.cc` verifies empty builders, plugin filter support, duplicate collapse, entry estimates, single-key lookup, and negative filtering for missing keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/full_filter_block.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/full_filter_block.h -->
# sources/storage-engines/rocksdb/table/block_based/full_filter_block.h

## Purpose
Declares full-filter builder and reader classes for block-based tables. Full filters store one filter block covering the whole SST file and expose key/prefix maybe-match APIs to point lookup, multi-get, and range logic.

## Important APIs, Types, And Functions
`FullFilterBlockBuilder` derives from `FilterBlockBuilder` and exposes construction with a prefix extractor, whole-key flag, and owned `FilterBitsBuilder`. It overrides add, finish, estimate, data-block-finalization, reset, and post-verification methods. `FullFilterBlockReader` derives from `FilterBlockReaderCommon<ParsedFullFilterBlock>` and exposes `Create`, single-key/prefix methods, batch key/prefix methods, `KeysMayMatch2`, and memory accounting.

## Control Flow
Table construction creates a builder from table filter policy context, feeds all keys to it, and writes the returned full filter as a meta block. Table reading creates a full-filter reader around a cached/pinned/lazy parsed block. Point and prefix queries delegate into a private `MayMatch` helper.

## State And Persistence Behavior
The builder owns `filter_bits_builder_` and may own `filter_data_` after finishing. The reader owns or references a `ParsedFullFilterBlock` through the base class. Durable format is selected by the underlying filter policy, not by the wrapper itself.

## Dependencies And Integration Points
Depends on filter interfaces, internal filter policy declarations, parsed full filter blocks, prefix extractors, block cache context, and block-based table reader state. It integrates with full-filter table options and with partitioned filter code through the compatible `KeysMayMatch2` helper.

## Risks And Edge Cases
The builder stores raw pointers to prefix extractor configuration that must outlive the builder but are not dereferenced in destruction. `ResetFilterBitsBuilder` makes later post-verification invalid if called too early. `whole_key_filtering` determines whether keys outside prefix-domain still produce filter entries.

## Test Signals
Full-filter tests validate empty behavior, custom plugin policies, duplicate/prefix counting, and both positive and negative may-match results.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/full_filter_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/full_filter_block_test.cc -->
# sources/storage-engines/rocksdb/table/block_based/full_filter_block_test.cc

## Purpose
Tests full-filter block building and reading with both custom plugin filter policies and the built-in Bloom filter policy.

## Important APIs, Types, And Functions
`TestFilterBitsBuilder` serializes fixed32 hashes, `TestFilterBitsReader` scans those hashes, and `TestHashFilter` exposes them as a `FilterPolicy`. `PluginFullFilterBlockTest` and `FullFilterBlockTest` inherit `mock::MockBlockBasedTableTester`. `CountUniqueFilterBitsBuilderWrapper` records unique keys/prefixes while delegating to a real builder. Tests include `PluginEmptyBuilder`, `PluginSingleChunk`, `EmptyBuilder`, `DuplicateEntries`, and `SingleChunk`.

## Control Flow
Tests construct a `FullFilterBlockBuilder`, add keys, finish into a `Slice`, wrap the bytes in `ParsedFullFilterBlock`, construct a `FullFilterBlockReader`, and call `KeyMayMatch`. Duplicate-entry tests add repeated keys and prefixes through fixed prefix extractors and assert the unique-entry accounting before finish.

## State And Persistence Behavior
All table/filter data is in memory. The mock table owns a minimal `BlockBasedTable::Rep`, while `CachableEntry` owns each parsed filter block without real cache handles. Custom filter bytes are simple arrays of fixed32 hashes.

## Dependencies And Integration Points
Uses public/internal filter policy APIs, mock block-based table scaffolding, parsed full filter blocks, fixed-prefix transforms, test harness utilities, and coding/hash helpers. It validates that full-filter code works with non-built-in plugin filters as well as `NewBloomFilterPolicy`.

## Risks And Edge Cases
Empty filter behavior is intentionally conservative at the full-filter reader level. Duplicate tests check the interaction between whole-key filtering and prefix filtering, including empty keys and empty prefixes. The plugin reader provides deterministic negative results, avoiding probabilistic Bloom false positives.

## Test Signals
Expected signals are empty finish output for no keys, `KeyMayMatch` true for inserted keys, false for missing plugin-hash keys, Bloom entry estimates that collapse duplicate `box`, and unique-count assertions for whole-key-plus-prefix additions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/full_filter_block_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/hash_index_reader.cc -->
# sources/storage-engines/rocksdb/table/block_based/hash_index_reader.cc

## Purpose
Implements the table-level hash index reader for block-based tables configured with `kHashSearch`. It combines the normal binary-search index block with optional prefix-hash metadata blocks to accelerate prefix-based index seeks.

## Important APIs, Types, And Functions
`HashIndexReader::Create` reads or prepares the primary index block, locates `kHashIndexPrefixesBlock` and `kHashIndexPrefixesMetadataBlock`, fetches those blocks, and creates a `BlockPrefixIndex`. `NewIterator` returns an index iterator over the primary index block, optionally supplied with `prefix_index_`.

## Control Flow
Creation can prefetch/pin the primary index block according to cache flags. After constructing the reader, it tries to find and read hash-index prefix metablocks through the meta-index. Missing prefix metadata is treated as non-fatal, so the reader still works through binary search. If both prefix blocks read and parse successfully, the `BlockPrefixIndex` is attached. Iterator creation reads or reuses the index block, handles errors by invalidating or returning an error iterator, and calls `Block::NewIndexIterator` with comparator and index-format flags.

## State And Persistence Behavior
The reader may hold a cached/owned primary index block via `IndexReaderCommon` and optionally owns an in-memory `BlockPrefixIndex` parsed from persisted prefix metadata blocks. It does not modify table files.

## Dependencies And Integration Points
Depends on `FindMetaBlock`, `BlockFetcher`, `BlockPrefixIndex`, table prefix extractor, footer/decompressor/cache options, memory allocator, and `IndexReaderCommon`. It integrates with table open/read paths for hash-search indexes created by `HashIndexBuilder`.

## Risks And Edge Cases
Prefix-index creation failures intentionally fall back to binary-search behavior, but primary index read failures are hard errors. The code asserts a table prefix extractor exists when creating the prefix index. Metadata block read or parse problems should not create false negatives because the primary index remains authoritative.

## Test Signals
Coverage is indirect through block-based table hash-search tests, prefix seek behavior, and table open compatibility tests where hash index metadata is missing or unreadable.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/hash_index_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/hash_index_reader.h -->
# sources/storage-engines/rocksdb/table/block_based/hash_index_reader.h

## Purpose
Declares `HashIndexReader`, the `IndexReader` implementation that augments block-based table index iteration with a prefix hash index.

## Important APIs, Types, And Functions
`Create` is the factory used during table open. `NewIterator` returns an `InternalIteratorBase<IndexValue>` over index entries. `ApproximateMemoryUsage` combines inherited index-block usage with reader and prefix-index memory. Private construction accepts a table pointer and movable `CachableEntry<Block>`.

## Control Flow
The factory builds a reader around the main index block and optional prefix index metadata. Read operations obtain an iterator through `NewIterator`, which delegates to the underlying index block and passes `prefix_index_.get()` when available.

## State And Persistence Behavior
Runtime state is inherited `IndexReaderCommon` plus an owned `std::unique_ptr<BlockPrefixIndex>`. Persistent state is read from primary index and hash-prefix metablocks written by `HashIndexBuilder`.

## Dependencies And Integration Points
Depends on `index_reader_common.h`, `BlockBasedTable`, `FilePrefetchBuffer`, `InternalIterator`, `IndexBlockIter`, `GetContext`, and block cache lookup context. It plugs into the block-based table reader's index-reader factory selection.

## Risks And Edge Cases
Memory accounting differs under `ROCKSDB_MALLOC_USABLE_SIZE`; without it, prefix-index memory is explicitly added. The reader must remain correct when `prefix_index_` is null by relying on ordinary index lookup.

## Test Signals
Hash-search table tests should show successful point/prefix lookup with and without prefix-index metadata and stable approximate memory usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/hash_index_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_builder.cc -->
# sources/storage-engines/rocksdb/table/block_based/index_builder.cc

## Purpose
Implements block-based table index builder factories and the non-inline behavior for shortened single-level indexes and partitioned two-level indexes.

## Important APIs, Types, And Functions
`IndexBuilder::CreateIndexBuilder` selects `ShortenedIndexBuilder`, `HashIndexBuilder`, or `PartitionedIndexBuilder`. `ShortenedIndexBuilder::FindShortestInternalKeySeparator`, `FindShortInternalKeySuccessor`, and `UpdateIndexSizeEstimate` implement separator shortening and cached size estimates. `PartitionedIndexBuilder` implements `CreateIndexBuilder`, constructor, `MakeNewSubIndexBuilder`, `RequestPartitionCut`, `CreatePreparedIndexEntry`, `PrepareIndexEntry`, `MaybeFlush`, `FinishIndexEntry`, `AddIndexEntry`, `Finish`, `NumPartitions`, and `UpdateIndexSizeEstimate`.

## Control Flow
Factory selection follows `BlockBasedTableOptions::IndexType`. Shortened indexes compute separators from neighboring block keys and may omit sequence numbers when safe. Partitioned indexes maintain a list of sub-index builders; as entries are added, `MaybeFlush` cuts a partition when requested or when the metadata block-size policy says the active partition is large enough. `Finish` is multi-step: each call returns one partition index with `Status::Incomplete`, then later calls feed the just-written partition handle into the top-level index until the final top-level index is returned with `Status::OK`.

## State And Persistence Behavior
The file writes no table bytes directly but populates `IndexBlocks` with index block contents and metadata. Partitioned indexes persist first-level partition blocks plus a top-level index. Runtime state tracks partition list, current sub-builder, flush policy, handle delta encoding, cached size estimates, sequence-number separator mode, and uniform-index block counts.

## Dependencies And Integration Points
Depends on internal key formatting/comparators, `BlockBuilder`, `BlockHandle`, flush block policies, partitioned filter coordination, table options, and statistics. It is called by block-based table builder when finalizing data blocks and table metadata.

## Risks And Edge Cases
Separator shortening must preserve total ordering with internal keys and user-defined timestamps. Once any partition requires key-plus-sequence separators, the mode must be applied consistently to all sub-index builders. Parallel compression splits prepare/finish work across threads, so cached estimates and mode flags use relaxed atomics. The finish protocol is easy to misuse because callers must keep calling while status is incomplete and provide the last written partition handle.

## Test Signals
Index builder tests elsewhere should validate index type selection, key shortening, first-key inclusion, partition counts, partition/filter alignment, user-defined timestamp stripping, value delta encoding, and current index size estimates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_builder.h -->
# sources/storage-engines/rocksdb/table/block_based/index_builder.h

## Purpose
Declares the index-builder abstraction and concrete builders for block-based table primary indexes: shortened binary-search indexes, hash-search indexes with prefix metadata, and partitioned two-level indexes.

## Important APIs, Types, And Functions
`IndexBuilder` declares `CreateIndexBuilder`, `IndexBlocks`, `AddIndexEntry`, the `PreparedIndexEntry` pipeline, `OnKeyAdded`, `Finish`, `IndexSize`, `NumUniformIndexBlocks`, `CurrentIndexSizeEstimate`, and separator-mode helpers. `ShortenedIndexBuilder` manages primary index block construction, optional first-key storage in `IndexValue`, separator shortening, delta-encoded handles, and parallel prepare/finish. `HashIndexBuilder` wraps a shortened primary index and emits hash-prefix metadata blocks. `PartitionedIndexBuilder` builds multiple shortened sub-indexes plus a top-level index and coordinates partition cuts with filters.

## Control Flow
Table builder calls `OnKeyAdded` for keys and `AddIndexEntry` or the prepare/finish pipeline for each data block. `ShortenedIndexBuilder` computes a separator between the last key of one block and the first key of the next, tracks whether sequence numbers are required, and adds encoded `IndexValue`s to one of two block builders. `HashIndexBuilder` counts restart indexes and groups adjacent keys by extracted prefix, flushing prefix metadata when the prefix changes. `PartitionedIndexBuilder` cuts sub-index partitions, then emits them one by one before emitting a top-level index.

## State And Persistence Behavior
Persistent output is `IndexBlocks::index_block_contents` plus optional `meta_blocks`. Hash search writes `kHashIndexPrefixesBlock` and `kHashIndexPrefixesMetadataBlock`, where prefixes are concatenated separately from metadata triples. Partitioned indexes persist partition index blocks and a final index-on-index block. Runtime state includes block builders, pending prefix metadata, active partition builders, cached size estimates, and flags for timestamp persistence and sequence-number separator mode.

## Dependencies And Integration Points
Depends on `InternalKeyComparator`, `InternalKeySliceTransform`, `BlockBuilder`, `FlushBlockPolicy`, block-based table options, and table format helpers. Integrated with `HashIndexReader`, partitioned filter builders, table property accounting, and parallel compression/construction.

## Risks And Edge Cases
User-defined timestamp persistence affects whether timestamps are stripped from index keys and first internal keys. Key shortening must be disabled or fall back when comparator shortening cannot produce a valid separator. Hash prefix metadata assumes sorted keys and a stable prefix extractor. `CurrentIndexSizeEstimate` for `HashIndexBuilder` currently returns zero, so callers relying on estimates get no useful signal for hash indexes.

## Test Signals
Look for tests around binary search with first key, hash search prefix lookup, partitioned index finishing, partition/filter alignment, user-defined timestamps, and table open/read compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_reader_common.cc -->
# sources/storage-engines/rocksdb/table/block_based/index_reader_common.cc

## Purpose
Implements common cache-aware primary index block access for block-based table index readers.

## Important APIs, Types, And Functions
`BlockBasedTable::IndexReaderCommon::ReadIndexBlock` reads the table's index block through `RetrieveBlock`. `GetOrReadIndexBlock` reuses an already held block or loads it lazily. `EraseFromCacheBeforeDestruction` evicts the cached index block when requested.

## Control Flow
`ReadIndexBlock` records `read_index_block_nanos`, asserts inputs, gets `rep->index_handle`, and retrieves a `Block_kIndex` with decompression and block-cache lookup enabled. `GetOrReadIndexBlock` returns an unowned value when the reader already has the block; otherwise it uses table cache settings. Destruction-time erasure either resets a cached entry if this reader has the last ref or asks the table to erase the index handle from cache.

## State And Persistence Behavior
No persistent state is modified. The code manages `CachableEntry<Block>` references and controls cache eviction policy for index blocks.

## Dependencies And Integration Points
Depends on `block_cache.h`, `BlockBasedTable::RetrieveBlock`, perf timers, block cache lookup context, and the table representation's index handle/decompressor/options. It is shared by hash, binary, partitioned, and other index readers.

## Risks And Edge Cases
Index-block read failures must be propagated to iterators so table reads do not silently ignore index corruption or IO failures. Cache erasure must not invalidate blocks still referenced elsewhere. Lazy loading assumes the table remains alive.

## Test Signals
Covered indirectly by table open, iterator, cache pinning, block cache, and index reader tests. Perf metrics can show read path regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_reader_common.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_reader_common.h -->
# sources/storage-engines/rocksdb/table/block_based/index_reader_common.h

## Purpose
Declares `BlockBasedTable::IndexReaderCommon`, a base class for index readers that need shared access to the primary index block regardless of whether it is owned, cached, pinned, or lazily read.

## Important APIs, Types, And Functions
The constructor stores a table pointer and movable `CachableEntry<Block>`. Public `EraseFromCacheBeforeDestruction` is overridden from `IndexReader`. Protected helpers include `ReadIndexBlock`, `table`, `internal_comparator`, `index_has_first_key`, `index_key_includes_seq`, `index_value_is_full`, `cache_index_blocks`, `user_defined_timestamps_persisted`, `GetOrReadIndexBlock`, and `ApproximateIndexBlockMemoryUsage`.

## Control Flow
Derived readers call `GetOrReadIndexBlock` before creating iterators. Helper accessors expose immutable table representation flags needed to configure `Block::NewIndexIterator`.

## State And Persistence Behavior
Runtime state is a non-owning `BlockBasedTable` pointer and `CachableEntry<Block>` for the index block. The class does not write table bytes.

## Dependencies And Integration Points
Depends on `block_based_table_reader.h` and `reader_common.h`. It is inherited by `HashIndexReader` and other index-reader implementations in the block-based table reader.

## Risks And Edge Cases
All helper methods assert a valid table representation, so lifetime is critical. Derived classes must transfer cache handles to returned iterators when needed to keep block contents alive.

## Test Signals
Indirect signals are successful iterator creation over cached and uncached index blocks, accurate memory usage, and safe cache erasure on reader destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/index_reader_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/mock_block_based_table.h -->
# sources/storage-engines/rocksdb/table/block_based/mock_block_based_table.h

## Purpose
Provides minimal block-based table scaffolding for unit tests that need a `BlockBasedTable` and filter builder context without opening a real SST file.

## Important APIs, Types, And Functions
`mock::MockBlockBasedTable` publicly exposes a constructor around `BlockBasedTable::Rep`. `mock::MockBlockBasedTableTester` owns `Options`, `ImmutableOptions`, `EnvOptions`, `BlockBasedTableOptions`, `InternalKeyComparator`, and a `BlockBasedTable`. Constructors accept raw or shared `FilterPolicy`. `GetBuilder` creates a `FilterBuildingContext` and calls `BloomFilterPolicy::GetBuilderFromContext`.

## Control Flow
Tests instantiate the tester with a filter policy. The constructor stores the policy in table options, creates a `BlockBasedTable::Rep` with fixed file size and mock level, and wraps it in `MockBlockBasedTable`. `GetBuilder` populates context fields such as column family name, compaction style, level, and logger before asking the filter policy for a builder.

## State And Persistence Behavior
All state is in memory. No table file is opened or persisted. The mock `Rep` is enough for filter builders/readers that inspect table options and immutable options.

## Dependencies And Integration Points
Depends on public filter policy API, block-based table reader internals, and internal filter policy context. Used by `full_filter_block_test.cc` and similar tests.

## Risks And Edge Cases
The mock table is intentionally incomplete; tests using it must avoid code paths that require real file handles, block handles, or loaded table properties. The raw-pointer constructor wraps ownership into `std::shared_ptr<const FilterPolicy>`, so callers should not reuse/delete the pointer separately.

## Test Signals
Successful construction of full-filter readers/builders in tests without real SST files is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/mock_block_based_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.cc -->
# sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.cc

## Purpose
Implements an index iterator over a precomputed set of data block handles for multi-scan reads. It walks only blocks relevant to prepared scan ranges, releases prefetched blocks as they become unnecessary, and reports prefetch waste and limit conditions.

## Important APIs, Types, And Functions
`MultiScanIndexIterator` implements constructor, destructor, `ReleaseBlocks`, `Seek`, `SeekToBlock`, `SeekToBlockIdx`, `SetExhausted`, `Next`, `SeekToFirst`, reverse-positioning stubs, `key`, `user_key`, `value`, and `GetMaxPrefetchSize`. It uses `MultiScanArgs`, `ReadSet`, `BlockHandle`, data-block separators, per-scan block index ranges, `InternalKeyComparator`, and statistics ticks.

## Control Flow
`Seek` is forward-only and tracks the previous seek key. It maps the seek target to prepared scan ranges: before the next range start, after it, or exactly at it. It then positions to the correct block or marks the current range exhausted. `SeekToBlock` advances `next_scan_idx_`, releases skipped blocks, linearly scans separators to find the first block whose separator is not less than the target, and delegates to `SeekToBlockIdx`. `Next` releases the current block, advances, checks current scan-range end, and stops with `Status::PrefetchLimitReached` if it crosses the prefetch window. `SetExhausted` distinguishes out-of-bound for an exhausted range from natural EOF after the last range.

## State And Persistence Behavior
There is no persistence. Runtime state includes owned vectors of block handles/separators/ranges, borrowed scan options, a shared `ReadSet` for pinned block lifetime, current and next scan indexes, valid/exhausted flags, previous seek key, status, and wasted-prefetch count. The destructor releases any remaining pinned blocks and records `MULTISCAN_PREFETCH_BLOCKS_WASTED`.

## Dependencies And Integration Points
Depends on multi-scan table-reader infrastructure, `ReadSet::ReleaseBlock`, internal key formatting, user comparator timestamp-aware comparisons, `Statistics`, and perf tick definitions. Returned `IndexValue`s feed downstream data-block iteration while disabling first-key optimization by using an empty first internal key.

## Risks And Edge Cases
The iterator is intentionally forward-only; backward operations invalidate it. Seek targets before earlier prepared ranges are invalid and counted as seek errors. Correct block release is delicate because `SeekToBlock` may release blocks before updating `cur_idx_`, and the destructor must avoid double-release. Separator comparisons use user keys without timestamps, so range starts and separators must be in the same comparator domain. Prefetch limit status is used to trigger additional prefetch rather than signal table corruption.

## Test Signals
Expected signals include correct block-handle sequence for multiple scan ranges, `is_out_of_bound_` behavior when a prepared range is exhausted, `PrefetchLimitReached` when crossing a bounded prefetch window, released-block accounting, wasted-prefetch statistics, and invalid reverse iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.cc -->
