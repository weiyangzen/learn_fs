# Research: subset-b-008677

This grouped report covers RocksDB block-based table reader, block encoding, cache, prefetch, prefix-index, footer, and tests. Each file section is wrapped with reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_test.cc -->
## sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_test.cc

Purpose: this is an integration-heavy test suite for `BlockBasedTable` readers. It builds real block-based SST files, opens them through `BlockBasedTableFactory::NewTableReader`, and validates reads through `Get`, `MultiGet`, `NewIterator`, `VerifyChecksum`, strict block-cache capacity, table-reader memory charging, filesystem prefetch capability discovery, and `MultiScan` preparation.

Important APIs/types/functions: `BlockBasedTableReaderBaseTest` owns table creation/open helpers, `GenerateKVMap()` creates fixed-size internal keys and values across predictable block boundaries, `NewBlockBasedTableReader()` wires `TableReaderOptions`, file readers, checksum reads, and user-defined timestamp persistence. `BlockBasedTableReaderTestParam` and `BlockBasedTableReaderTestParamBuilder` generate a large matrix over compression, direct reads, index type, block cache, timestamp mode, compression dictionary, comparator, async I/O, and alignment. Specialized fixtures cover `ChargeTableReaderTest`, `StrictCapacityLimitReaderTest`, checksum mismatch, and `MultiScan` behavior.

Control flow: most tests create a table, open a `BlockBasedTable`, verify table checksums, then exercise reader APIs while checking cache state and returned values. `Get` expects the first key of a block to miss cache and later keys to hit because the whole data block is cached. `MultiGet` constructs `MultiGetContext`/`KeyContext` ranges and expects data-block reads, populated statuses, cache hits, and correct values. Iterator tests scan forward/backward. `MultiScan` tests call `Prepare()` before ordered `Seek()` calls and validate prefetch limits, pinned block ownership, first-internal-key pruning, and reseek-after-exhaustion handling.

State and persistence behavior: tests persist temporary table files under a per-thread DB path and destroy it in teardown. Cache state is observable through `TEST_KeyInCache`, charge-tracking cache wrappers, strict-capacity LRU behavior, and block pinning probes. User-defined timestamp state is represented by comparator timestamp size, persisted/stripped key encodings, read timestamp slices, and generated same-key/different-timestamp inputs. Compression dictionaries and super-block alignment affect file layout and reader metadata.

Dependencies/integration points: depends on table builder/reader/factory, block cache reservation, file system wrappers, compression managers, direct I/O sync-point setup, RocksDB comparators, `MultiGetContext`, `BlockBasedTableIterator`, `PartitionedIndexIterator`, perf context counters, and `FSSupportedOps::kFSPrefetch`.

Risks: parameter explosion can make failures hard to isolate; several checks rely on block-size assumptions and are skipped for compression where needed. Async MultiScan is disabled, so async-specific regressions can hide. Cache and prefetch assertions depend on strict test layout and may be brittle if table builder block-size heuristics change.

Test signals: this file itself is the signal. It covers cache warmup, strict cache memory-limit propagation, checksum corruption accounting, first-internal-key index pruning, reverse comparators, timestamp persistence/stripping, direct/non-direct reads, compression dictionary paths, and filesystem prefetch support initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_builder.cc -->
## sources/storage-engines/rocksdb/table/block_based/block_builder.cc

Purpose: implements `BlockBuilder`, the writer for RocksDB block payloads. It emits prefix-compressed key/value entries, restart arrays, optional data-block hash indexes, optional separated key/value storage, timestamp-stripped keys, value-delta encoded index values, and a `DataBlockFooter` describing encoded features.

Important APIs/functions: constructor initializes restart state and optional `DataBlockHashIndexBuilder`; `Reset()` and `SwapAndReset()` clear builder state; `EstimateSizeAfterKV()` predicts size after adding one entry; `Finish()` appends values, restart offsets, optional hash index, and footer; `Add()` stores and maintains `last_key_`; `AddWithLastKey()` uses caller-provided previous key; `AddWithLastKeyImpl()` is the hot encoding path; `MaybeStripTimestampFromKey()` applies user-defined timestamp stripping; `GetRestartKey()` decodes restart-point keys; `ScanForUniformity()` marks blocks suitable for auto/interpolation search using restart-key gap coefficient of variation.

Control flow: each add strips timestamps as configured, maybe starts a new restart interval, computes shared prefix bytes unless delta encoding is disabled or skipped, emits varint headers, writes the non-shared key delta, and writes either the full value or caller-provided delta value. With separated KV storage, values go into `values_buffer_` and restart entries include a value offset. On finish, the values section is appended before restarts, then the footer is encoded.

State and persistence behavior: persistent on-disk state is the serialized block buffer, restart offsets, optional hash index payload, and footer bits. In-memory mutable state includes `buffer_`, `values_buffer_`, `restarts_`, `estimate_`, `counter_`, `last_key_`, `finished_`, `is_uniform_`, and hash-index builder state. The implementation assumes input slice sizes fit in 32 bits and notes unchecked 4 GiB buffer overflow risks for huge blocks.

Dependencies/integration points: uses `dbformat` for internal key/timestamp helpers, `block_util.h` decoders and `ReadBe64FromKey`, `DataBlockFooter`, `DataBlockHashIndexBuilder`, `BlockBasedTableOptions`, `Statistics`, and RocksDB coding helpers. Readers in `block.cc` and tests in `block_test.cc` must decode exactly this layout.

Risks: callers must not mix `Add()` and `AddWithLastKey()` between resets; delta values must match value-delta encoding semantics; timestamp stripping must also be done by callers for timestamp-bearing values such as first internal keys; separated-KV changes footer size and decode boundaries; format-bit changes require careful backward compatibility.

Test signals: `block_test.cc` exercises plain/data hash blocks, separated KV, user-defined timestamps, value-delta index blocks, uniformity detection, interpolation search, checksums, and corruption boundaries. `block_based_table_reader_test.cc` validates the produced blocks through real table reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_builder.h -->
## sources/storage-engines/rocksdb/table/block_based/block_builder.h

Purpose: declares `BlockBuilder`, the block-format writer used by table builders for data, index, range tombstone, and metadata-style blocks. It exposes a compact append/reset/finish API while hiding format details such as prefix compression, restart intervals, hash indexes, timestamp stripping, separated KV storage, and uniform-key detection.

Important APIs/types: constructor parameters control restart interval, key delta encoding, value delta encoding, data-block index type, hash-table utilization ratio, timestamp size and persistence, whether keys are user keys, separated KV storage, statistics, and uniform CV threshold. Public methods are `Reset()`, `SwapAndReset()`, `Add()`, `AddWithLastKey()`, `Finish()`, `CurrentSizeEstimate()`, `EstimateSizeAfterKV()`, `empty()`, `MutableBuffer()`, and `IsUniform()`.

Control flow: callers add strictly sorted keys until a block is ready, call `Finish()` to obtain a `Slice` into builder-owned memory, then `Reset()` or `SwapAndReset()` for reuse. `AddWithLastKey()` exists for call sites already tracking previous keys and avoids redundant state maintenance. The header documents invariants: no mixing `Add()` and `AddWithLastKey()`, no finish-before-reset appends, and keys larger than prior keys except for range tombstone blocks.

State and persistence behavior: fields in the class mirror serialized layout. `buffer_` stores encoded entries and final footer, `restarts_` stores restart offsets, `values_buffer_` temporarily stores separated values, `last_key_` supports prefix compression, `estimate_` tracks uncompressed size, `counter_` tracks restart interval position, and `is_uniform_` records the most recent finished block’s uniformity bit.

Dependencies/integration points: includes RocksDB `Slice`, public table options, and `DataBlockHashIndexBuilder`. It is consumed by block-based table builders and by tests constructing synthetic blocks.

Risks: constructor flags must match the block reader path. Mis-setting `is_user_key_`, timestamp persistence, or value-delta encoding can produce blocks that decode incorrectly. The `Slice` returned by `Finish()` is invalidated by `Reset()`.

Test signals: parameterized tests instantiate the builder across restart intervals, timestamp modes, separated KV, data block hash indexes, and index block value-delta settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_cache.cc -->
## sources/storage-engines/rocksdb/table/block_based/block_cache.cc

Purpose: implements typed block-cache creation and helper lookup for block-based table blocks. It bridges raw cached block contents to strongly typed block-like wrappers and selects cache item helpers based on `BlockType` and cache tier.

Important APIs/functions: `BlockCreateContext::Create()` overloads build `Block_kData`, `Block_kIndex`, `Block_kFilterPartitionIndex`, `Block_kRangeDeletion`, `Block_kMetaIndex`, `Block_kUserDefinedIndex`, `ParsedFullFilterBlock`, and `DecompressorDict`. `GetCacheItemHelper()` returns either full helper support for secondary cache/non-volatile tiers or basic helper support for volatile-only use.

Control flow: typed cache code passes raw or decompressed `BlockContents` into `BlockCreateContext`. Data/index/meta variants allocate a `Block` wrapper with appropriate read-amplification and restart interval metadata, then initialize per-KV protection information according to block role. Filter and decompressor dictionary variants construct non-`Block` parsed objects. Helper arrays are indexed by `BlockType` enum values and intentionally leave unsupported block types as `nullptr`.

State and persistence behavior: no disk persistence is introduced here. Runtime state comes from `BlockCreateContext` fields such as table options, immutable options, statistics, decompressor, comparator, checksum bytes per key, index value flags, and restart intervals. Cache helper selection controls how cached entries are charged, serialized, and used with secondary cache.

Dependencies/integration points: depends on `block_cache.h`, `BlockBasedTableReader`, typed cache APIs, `ParsedFullFilterBlock`, decompression utilities, and `BlockType` ordering. Block readers rely on these wrappers to initialize checksum verification and memory accounting consistently.

Risks: helper arrays must stay aligned with `BlockType`; adding an enum value without updating arrays can produce wrong helper lookup. Context pointers such as `table_options`, `ioptions`, and `decompressor` must be valid when compression or parsing needs them. Meta-index blocks are constructible but not stored in block cache.

Test signals: checksum initialization and approximate memory tests in `block_test.cc` use `BlockCreateContext`; reader tests cover cache insertion, secondary cache style typed helpers indirectly, and strict cache capacity behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_cache.h -->
## sources/storage-engines/rocksdb/table/block_based/block_cache.h

Purpose: declares role-specific block-like wrapper types and cache interfaces for block-based table cache entries. The design gives each cached payload a compile-time `CacheEntryRole` and `BlockType` without virtual dispatch overhead.

Important APIs/types: `Block_kData`, `Block_kIndex`, `Block_kFilterPartitionIndex`, `Block_kRangeDeletion`, and `Block_kMetaIndex` derive from `Block`; `Block_kUserDefinedIndex` derives from `BlockContents`; `BlockCreateContext` carries construction settings and provides templated compressed/raw `Create()` plus overloads for each block-like type. `BlockCacheInterface<T>` and `BlockCacheTypedHandle<T>` alias `FullTypedCacheInterface`. `UncacheAggressivenessAdvisor` models when to keep evicting blocks.

Control flow: typed cache users instantiate `BlockCacheInterface<TBlocklike>` with a `BlockCreateContext`. If cached content is compressed, the templated `Create()` decompresses into allocated block contents; otherwise it copies raw bytes. It then dispatches to role-specific overloads and returns memory charge from `ApproximateMemoryUsage()`.

State and persistence behavior: wrapper types do not persist extra data; they annotate cached entries for cache role accounting and helper selection. `BlockCreateContext` carries transient table-reader state. `UncacheAggressivenessAdvisor` maintains useful/not-useful erase counters and stops aggressive uncaching when the observed useful ratio drops below a threshold derived from the option.

Dependencies/integration points: depends on typed cache, `Block`, `BlockType`, filter parsing, table format, compression allocators, and RocksDB cache role options. It is central to block reads, cache warming, secondary cache interaction, and checksum initialization.

Risks: the SFINAE `WithBlocklikeCheck` relies on all block-like types having `kCacheEntryRole`. Wrong `index_value_is_full` or `index_has_first_key` context causes index checksum/protection parsing mismatch. Decompression creation requires `ioptions` and `decompressor` to be valid.

Test signals: `block_test.cc` explicitly creates typed data/index/meta blocks and validates checksum and memory behavior. `block_based_table_reader_test.cc` exercises cache role charging and strict capacity paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefetcher.cc -->
## sources/storage-engines/rocksdb/table/block_based/block_prefetcher.cc

Purpose: implements block read-ahead policy for block-based table reads. It chooses between filesystem prefetch and RocksDB `FilePrefetchBuffer`, handling compaction readahead, explicit user readahead, implicit sequential auto-readahead, direct I/O, async prefetch buffering, and cache-tier reads that disallow I/O.

Important API/function: `BlockPrefetcher::PrefetchIfNeeded()` takes the table representation, current block handle, requested readahead size, compaction flag, sequential-check bypass flag, read options, optional callback for readahead sizing, and async prefetch mode.

Control flow: the method returns immediately for `kBlockCacheTier`. For compaction, it uses filesystem prefetch when supported and direct I/O is off; otherwise it creates an internal prefetch buffer using compaction readahead settings. For normal reads, explicit user `readahead_size` always creates a user-scan prefetch buffer. Implicit auto-readahead first checks max/initial settings, then either bypasses sequential checks or tracks offsets to require sequential reads before prefetching. With filesystem prefetch support it calls `RandomAccessFileReader::Prefetch`, records `readahead_limit_`, and doubles `readahead_size_` up to the configured maximum. Unsupported or unavailable filesystem prefetch falls back to `FilePrefetchBuffer`.

State and persistence behavior: no persistent state. Runtime state includes previous block offset/length, file read count, current readahead size, readahead limit, initial auto size, compaction size, and a lazily created prefetch buffer. `ResetValues()` resets auto-readahead after non-sequential access.

Dependencies/integration points: depends on `BlockBasedTable::Rep`, `BlockHandle`, table options, `RandomAccessFileReader`, filesystem supported operations, `ReadOptions`, `ReadaheadParams`, and `FilePrefetchBuffer` usage labels.

Risks: incorrect sequential detection can under-prefetch scans or over-prefetch random reads. Filesystems may advertise prefetch but return `NotSupported`, so fallback correctness matters. Direct I/O requires internal buffering. Async mode changes buffer count and may affect stats timing.

Test signals: `block_based_table_reader_test.cc` validates `fs_prefetch_support` initialization and has a disabled async MultiScan test covering coalesced reads, cached-block exclusion, and prefetch limits. MultiScan prefetch-limit tests cover higher-level effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefetcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefetcher.h -->
## sources/storage-engines/rocksdb/table/block_based/block_prefetcher.h

Purpose: declares `BlockPrefetcher`, the per-iterator/per-reader helper that tracks sequential block access and owns optional file prefetch buffering.

Important APIs/types: constructor sets compaction readahead and initial auto readahead. Public methods are `PrefetchIfNeeded()`, `prefetch_buffer()`, `UpdateReadPattern()`, `IsBlockSequential()`, `ResetValues()`, and `SetReadaheadState()`. `SetReadaheadState()` imports persisted adaptive-readahead state from `ReadaheadFileInfo::ReadaheadInfo` and exposes a sync point for tests.

Control flow: callers update or query the object around block reads. `IsBlockSequential()` compares the next offset with `prev_offset_ + prev_len_`, treating the first read as sequential. `ResetValues()` restarts auto-read detection after a random access. `PrefetchIfNeeded()` performs the actual policy implementation in the `.cc` file.

State and persistence behavior: state is in-memory and bound to scanning/read behavior: compaction readahead, current/initial auto readahead, readahead limit, number of file reads, previous offset/length, and owned `FilePrefetchBuffer`. The `SetReadaheadState()` hook can restore adaptive readahead counters from file-level info but does not persist them itself.

Dependencies/integration points: includes `block_based_table_reader.h` for `BlockBasedTable::Rep`, file prefetch buffer types, block handles, and read options. It is used by block-based table iterators and compaction read paths.

Risks: object reuse without `ResetValues()` after access pattern changes can retain stale sequential state. The prefetch buffer pointer is exposed raw, so lifetime remains with the `BlockPrefetcher`.

Test signals: filesystem prefetch-support and MultiScan tests exercise call sites. Sync-point callback in `SetReadaheadState()` provides a targeted hook for adaptive-readahead tests outside this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefetcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefix_index.cc -->
## sources/storage-engines/rocksdb/table/block_based/block_prefix_index.cc

Purpose: implements a compact hash index mapping key prefixes to candidate data-block IDs. It accelerates prefix-based lookup by reading prefix metadata blocks and building an in-memory bucket table.

Important APIs/functions: local helpers hash prefixes and encode/decode bucket entries. `BlockPrefixIndex::Builder::Add()` records a prefix span. `Builder::Finish()` builds the bucket array and optional block-array buffer. `BlockPrefixIndex::Create()` decodes serialized prefix and prefix-meta slices. `GetBlocks()` transforms a lookup key to an internal prefix and returns candidate block IDs.

Control flow: `Create()` iterates over `prefix_meta`, reading varint triples `(prefix_size, entry_index, num_blocks)`, slicing the corresponding prefix bytes from `prefixes`, and adding them to the builder. `Finish()` uses roughly one bucket per prefix, groups records by hash bucket, merges connected spans within a bucket, counts block-array storage, and fills buckets either with `kNoneBlock`, a direct block ID, or an encoded pointer into `block_array_buffer_`. `GetBlocks()` hashes the lookup prefix and decodes the bucket representation.

State and persistence behavior: source persistence is the table’s hash-index prefix and metadata blocks. Runtime state is `num_buckets_`, `buckets_`, `num_block_array_buffer_entries_`, `block_array_buffer_`, and an `InternalKeySliceTransform` wrapping the prefix extractor. The destructor releases the two arrays.

Dependencies/integration points: depends on `SliceTransform`, internal-key prefix transformation, `Arena`, varint coding, and RocksDB hash. It integrates with block-based table readers that load hash-index metadata and pass `BlockPrefixIndex` into index/data iterators.

Risks: malformed metadata can cause corruption statuses; hash collisions intentionally broaden candidate block sets. Builder assumes records arrive in nondecreasing block order for span merging assertions. `GetBlocks()` returns internal pointers that remain valid only for the index lifetime.

Test signals: direct tests are not in this file set, but `block_based_table_reader_test.cc` includes `kHashSearch` parameterization and prefix extractors, while block/hash behavior is indirectly exercised through table reads and cache checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefix_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefix_index.h -->
## sources/storage-engines/rocksdb/table/block_based/block_prefix_index.h

Purpose: declares `BlockPrefixIndex`, the reader-side hash structure mapping a transformed key prefix to one or more possible data blocks.

Important APIs/types: `GetBlocks(const Slice& key, uint32_t** blocks)` returns the number of candidate blocks and an internal pointer to block IDs. `ApproximateMemoryUsage()` reports object plus bucket/buffer arrays. Static `Create()` builds an index from serialized prefix and metadata blocks using a caller-owned `SliceTransform`. The private constructor stores bucket metadata and an `InternalKeySliceTransform`.

Control flow: table readers call `Create()` after reading hash-index metadata blocks. Lookup paths call `GetBlocks()` before or during index search to narrow candidate blocks by prefix. If zero is returned, the key cannot exist under that prefix index.

State and persistence behavior: persistent bytes live in table metadata; this class owns only decoded heap arrays. Ownership is manual (`new[]`/`delete[]`), and `prefix_extractor` ownership remains with the table reader as documented.

Dependencies/integration points: depends on RocksDB `Status`, `Slice`, `SliceTransform`, comparators, and internal key transforms. It is used with block-based table hash search and prefix extraction options.

Risks: callers must not outlive the prefix extractor. Returned block pointers are internal and must not be freed or retained beyond the index lifetime. Because hash buckets can contain collisions, consumers must treat returned blocks as candidates, not exact matches.

Test signals: hash-search table reader parameterization and prefix extractor setup in `block_based_table_reader_test.cc` indirectly validate creation/lookup. Corruption paths would need targeted metadata corruption tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_prefix_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_test.cc -->
## sources/storage-engines/rocksdb/table/block_based/block_test.cc

Purpose: comprehensive unit tests for block encoding/decoding, data/index/meta block iteration, read-amplification accounting, index search, user-defined timestamps, separated KV storage, value-delta encoding, block footer feature flags, per-KV checksums, and corruption handling.

Important APIs/types/functions: helpers `GenerateInternalKey()`, `GenerateRandomKVs()`, `GetBlockContents()`, `CheckBlockContents()`, `AddIndexBlockEntry()`, and `GenerateRandomIndexEntries()` build synthetic block contents. Fixtures include `BlockTest`, `IndexBlockTest`, `BlockPerKVChecksumTest`, `DataBlockKVChecksumTest`, `IndexBlockKVChecksumTest`, `MetaIndexBlockKVChecksumTest`, corruption-test subclasses, and `MetaBlockEntryCorruptionTest`.

Control flow: tests construct `BlockBuilder` instances with parameterized encoding options, finish raw blocks, create `Block`/typed cache wrappers, and use data/index/meta iterators to scan and seek. Index tests validate key/value decoding, optional first internal key, value-delta handles, binary/interpolation/auto search, and uniformity detection. Checksum tests generate protection info, inspect checksum bytes, use sync points to count verification, and corrupt decoded values to require corruption statuses.

State and persistence behavior: no files are required except DB fixture setup for option validation. Serialized state under test is raw block bytes: entry varints, key deltas, values or separated value section, restart arrays, data block footer, optional hash index, and per-KV checksum side metadata initialized in `Block`. Read amplification tests maintain statistics counters for total and useful bytes.

Dependencies/integration points: depends on `Block`, `BlockBuilder`, `BlockCreateContext`, `DataBlockFooter`, `BlockBasedTable` constants, DB test utilities, internal-key formatting, comparators, slice transforms, protection checksums, sync points, and table format `IndexValue`.

Risks: several tests rely on internal test-only accessors and sync-point names, making them sensitive to refactors. Corruption tests mutate byte offsets and assume compact varint sizes in small synthetic blocks. Interpolation search behavior depends on key distribution assumptions.

Test signals: broad parameter matrices cover delta/no-delta, timestamp persistence, binary/hash data index, restart intervals, separated KV, index search type, first key inclusion, user-vs-internal index keys, uniform/non-uniform distributions, checksum lengths, and corruption for data/index/meta blocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_type.h -->
## sources/storage-engines/rocksdb/table/block_based/block_type.h

Purpose: defines `BlockType`, the compact enum identifying block-based table block roles, plus a string conversion helper for diagnostics.

Important APIs/types: `enum class BlockType : uint8_t` includes data, filter, filter partition index, properties, compression dictionary, range deletion, hash-index prefixes, hash-index metadata, meta index, index, user-defined index, and invalid. `BlockTypeToString()` maps each enum value to a stable human-readable string.

Control flow: there is no runtime stateful flow; call sites use the enum to select typed cache helpers, block roles, tracing/accounting labels, and format-specific parsing paths. `kInvalid` is explicitly required to stay last because arrays in cache code size themselves using it.

State and persistence behavior: the enum can represent persisted or cached block role metadata indirectly, but this header itself stores no state. Ordering is part of the ABI-like contract for helper arrays in `block_cache.cc`.

Dependencies/integration points: included by block cache and table-reader code. `Block_k*` wrappers in `block_cache.h` each advertise one `BlockType`, and `GetCacheItemHelper()` indexes arrays using these enum ordinal values.

Risks: adding or reordering values without updating helper arrays and string conversion can break cache helper selection. Missing `BlockTypeToString()` cases would degrade diagnostics.

Test signals: cache helper and table reader tests indirectly depend on correct mapping. No direct unit test for `BlockTypeToString()` appears in this file set.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_util.h -->
## sources/storage-engines/rocksdb/table/block_based/block_util.h

Purpose: provides hot-path utility decoders for block entries and keys, including format-version-4 index-block variants, plus a big-endian key reader used for interpolation/uniformity logic.

Important APIs/types: `DecodeEntry` decodes shared key bytes, non-shared key bytes, value length, and optional separated-KV value offset. `DecodeKey` discards value length for key-only parsing. `DecodeKeyV4` decodes format-v4 entries where value length is omitted. `DecodeEntryV4` adapts v4 key decoding for entry interfaces with value length set to zero. `ReadBe64FromKey()` extracts up to eight bytes from a key at an offset as an order-preserving big-endian integer.

Control flow: decoders first attempt a fast one-byte varint path for small values, then fall back to bounded `GetVarint32Ptr()` parsing. They return `nullptr` on malformed/truncated input, allowing iterators to surface corruption. `ReadBe64FromKey()` strips internal key trailer when requested, clamps offset to key size, uses endian swap for eight-byte fast path, and zero-pads shorter suffixes.

State and persistence behavior: stateless utilities interpreting persisted block bytes. Their behavior defines how block entries written by `BlockBuilder` are read by `Block`, index iterators, footer/uniformity scanning, and corruption checks.

Dependencies/integration points: depends on internal-key constants, platform endian helpers, `Slice`, coding utilities, and math helpers. `BlockBuilder::GetRestartKey()` uses `DecodeKey`/`DecodeKeyV4`; block iterators use these decoders for normal reads.

Risks: fast-path preconditions must match caller checks; `DecodeEntry` asserts at least three bytes whereas `DecodeKeyV4` explicitly checks. Separated-KV callers must pass a `value_offset` pointer only when the entry format includes it. Internal-key reads assert enough bytes when stripping trailers.

Test signals: `block_test.cc` corruption tests exercise boundary failures; interpolation and uniformity tests exercise `ReadBe64FromKey()` behavior through `BlockBuilder` and iterators.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/cachable_entry.h -->
## sources/storage-engines/rocksdb/table/block_based/cachable_entry.h

Purpose: declares `CachableEntry<T>`, a move-only handle for objects that may be cached, uniquely owned, or unowned. It centralizes release/delete behavior for block-like objects returned by block-based table readers.

Important APIs/types: constructors accept value pointer, cache pointer, cache handle, and ownership flag. Public methods include move construction/assignment, `IsEmpty()`, `IsCached()`, accessors, `Reset()`, `ResetEraseIfLastRef()`, `TransferTo(Cleanable*)`, `SetOwnedValue()`, `SetUnownedValue()`, `SetCachedValue()`, and `As<TWrapper>()` for layout-compatible block wrapper casts.

Control flow: destruction and reset call `ReleaseResource()`, which releases cache handles or deletes owned values. Moves transfer all management fields and clear the source. `TransferTo()` registers cache-handle release or value deletion cleanup with a `Cleanable`, then clears this entry so iterator cleanup owns the resource. Setter methods are idempotent for identical current values and otherwise reset before installing new state.

State and persistence behavior: runtime ownership state is `value_`, `cache_`, `cache_handle_`, and `own_value_`. No data is persisted. Cache release can optionally erase if this is the last reference via `ResetEraseIfLastRef()`.

Dependencies/integration points: depends on RocksDB `Cache`, `Cleanable`, likely/unlikely branch macros, and advanced cache handle APIs. Used by table reader paths that may return cached blocks, non-cached owned blocks, or pinned/unowned objects and transfer them to iterators.

Risks: invariants require cache and handle to be both null or both non-null, and cached entries cannot own values. `As<TWrapper>()` relies on identical object size and pointer-compatible wrapper layout; misuse would be unsafe. Unowned values require external lifetime management.

Test signals: no direct tests in this set, but reader and iterator tests stress cleanup through cache hits/misses, block pinning, strict capacity failures, and iterator transfer paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/cachable_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_footer.cc -->
## sources/storage-engines/rocksdb/table/block_based/data_block_footer.cc

Purpose: implements encoding and decoding of `DataBlockFooter`, the compact trailer for data block metadata. The footer packs restart count with feature bits for hash index, uniform keys, and separated KV storage.

Important APIs/functions: `DataBlockFooter::EncodeTo()` appends an optional values-section offset followed by a packed fixed32 word. `DecodeFrom()` reads from the end of a `Slice`, sets `index_type`, `separated_kv`, `is_uniform`, `num_restarts`, and optionally `values_section_offset`, then removes consumed bytes from the input.

Control flow: encode asserts restart count fits the low 28 bits, writes `values_section_offset` first when separated KV is enabled, sets bit 31 for `kDataBlockBinaryAndHash`, bit 28 for separated KV, and bit 29 for uniform keys, then writes the packed word. Decode requires at least four bytes, reads the packed word from the end, peels off known bits, rejects any remaining value above `kMaxNumRestarts`, removes the packed word, and if separated KV is set reads/removes the preceding offset.

State and persistence behavior: this is persisted block-format metadata. It changes how readers find restart arrays, separated values, hash indexes, and auto/interpolation search hints. Unknown reserved bits are treated as corruption for forward-compatibility failure rather than silent misread.

Dependencies/integration points: uses fixed32 coding utilities and `BlockBasedTableOptions::DataBlockIndexType`. `BlockBuilder::Finish()` writes this footer; `Block` parsing consumes it. `block_test.cc` directly inspects packed bits and footer size in separated/non-separated corruption tests.

Risks: bit 30 is documented as dangerous because older corruption checks can overflow; future feature allocation needs a format-version bump or careful compatibility. Decode consumes from the end, so callers must pass the full remaining block slice.

Test signals: separated KV tests, hash index tests, uniformity tests, and corruption-boundary tests in `block_test.cc` indirectly and directly validate encoding layout.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_footer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_footer.h -->
## sources/storage-engines/rocksdb/table/block_based/data_block_footer.h

Purpose: declares `DataBlockFooter`, the on-block trailer metadata for data block structure and features.

Important APIs/types: constants `kMaxNumRestarts`, `kMaxEncodedLength`, and `kMinEncodedLength` describe footer limits. Fields include `index_type`, `separated_kv`, `values_section_offset`, `num_restarts`, and `is_uniform`. Constructors support default binary-search/zero-restart state and explicit index type plus restart count. Methods are `EncodeTo()` and `DecodeFrom()`.

Control flow: block writers populate the fields before encoding; block readers decode from the end of the input slice and use the resulting metadata to locate restart arrays, values section, hash index, and uniform-search hints.

State and persistence behavior: the encoded footer stores low 28 bits of restart count plus high feature bits. With separated KV, an extra fixed32 offset precedes the packed word. The header documents compatibility expectations and why only some reserved bits can be safely interpreted by older versions as corruption.

Dependencies/integration points: depends on RocksDB `Slice`, `Status`, and table options. It is used by `BlockBuilder`, `Block`, and tests that compute raw block boundaries.

Risks: the restart-count capacity is tied to 32-bit block-size assumptions. New features must respect reserved-bit compatibility. Callers must handle variable encoded length rather than assuming four bytes.

Test signals: `block_test.cc` separated-KV corruption helpers use `kMaxNumRestarts` and footer-size logic; data block hash and uniformity tests exercise `index_type` and `is_uniform` bits through reader behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/data_block_footer.h -->
