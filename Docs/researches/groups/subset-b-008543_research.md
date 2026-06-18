# Research: subset-b-008543

This grouped report covers Pebble SSTable blob-reference liveness, block I/O, compression, block properties, block iterator contracts, and selected columnar bitmap primitives. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob_reference_index.go -->
## sources/storage-engines/pebble/sstable/blob_reference_index.go

Purpose: Maintains and decodes per-blob-reference liveness information for values referenced by an SSTable. It is used while constructing SSTables that refer to blob files, recording which value IDs within each blob value block are still live.

Important APIs/types/functions: `blobReferenceValues` accumulates state for one `base.BlobReferenceID`; `blobRefValueLivenessWriter` owns a dense `refState` slice indexed by reference ID; `addLiveValue` records `(refID, blockID, valueID, valueSize)`; `finish` yields ordered `(refID, encoding)` pairs; `BlobRefLivenessEncoding` and `DecodeBlobRefLivenessEncoding` expose decoded block-level records. The encoding is varint block ID, varint aggregate values size, varint bitmap byte length, then the run-length bitmap bytes produced by `BitmapRunLengthEncoder`.

Control flow: A writer is `init`ed, then live values arrive in monotonically increasing reference IDs and increasing blob block/value order. New reference IDs extend `refState` by exactly one slot; skipped IDs return an assertion error. A change in block ID flushes the current block via `finishCurrentBlock`, starts a new bitmap, and subsequent calls set bits for live value IDs while accumulating value bytes. `finish` flushes every current block and yields all encodings.

State and persistence behavior: State is in-memory until table construction persists the encoded byte slices as blob-reference value liveness index payloads. The dense slice index is part of the contract: reference IDs map directly to slice positions. Encodings are compact, append-only, and corruption-decoded with `base.CorruptionErrorf`.

Dependencies and integration points: Depends on `internal/base` for reference IDs and corruption/assertion errors, `sstable/blob` for blob block/value IDs, `encoding/binary` varints, `iter.Seq2`, `slices.Grow`, and the SSTable bitmap run-length helpers. It integrates with blob-file rewrite/compaction paths that need to know which blob values are live.

Risks: `DecodeBlobRefLivenessEncoding` slices `buf[:enc.BitmapSize]` after parsing bitmap size without an explicit bounds check, so malformed short buffers can panic rather than returning a corruption error. Correctness also depends on caller ordering by reference/block/value ID and on every non-empty current block being flushed exactly once. Calling `finish` repeatedly mutates by appending another copy of the current blocks.

Test signals: Covered by `blob_reference_index_test.go`, including basic multi-value/multi-block encodings, all-live values, and randomized encode/decode/rebuild round trips using `IterSetBitsInRunLengthBitmap`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob_reference_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob_reference_index_test.go -->
## sources/storage-engines/pebble/sstable/blob_reference_index_test.go

Purpose: Tests the blob-reference value liveness writer and decoder, verifying byte-level bitmap output and round-trip idempotence.

Important APIs/types/functions: `TestBlobRefValueLivenessWriter` drives `blobRefValueLivenessWriter.init`, `addLiveValue`, `finish`, `DecodeBlobRefLivenessEncoding`, and checks `BlobRefLivenessEncoding` fields. `TestBlobRefLivenessEncoding_Randomized` reconstructs liveness using `IterSetBitsInRunLengthBitmap` and compares re-encoded bytes.

Control flow: The basic subtest writes several values in one reference/block, intentionally leaves gaps in value IDs, advances to another block, decodes the resulting encoding, and checks aggregate `ValuesSize`, `BitmapSize`, and literal bitmap bytes. The all-ones subtest verifies dense value IDs. The randomized test generates increasing reference IDs, increasing block IDs with duplicates, sparse increasing value IDs, encodes, decodes, rebuilds a fresh writer from decoded set bits, and expects byte-for-byte equality.

State and persistence behavior: The tests treat the encoding as stable enough for exact byte comparisons. They also exercise writer reinitialization between rounds, which clears state while preserving capacity.

Dependencies and integration points: Uses `maps.Collect`, Go `iter`, `math/rand/v2`, Pebble `testutils`, `base.BlobReferenceID`, `blob.BlockID`, `blob.BlockValueID`, and `stretchr/testify/require`.

Risks: Randomized coverage is bounded to 20 rounds and does not feed malformed encodings into the decoder, so decode bounds/corruption behavior is not strongly covered. Tests assume ordering constraints rather than proving out-of-order inputs fail cleanly.

Test signals: Strong positive signal for canonical encoding under valid input, sparse bitmap gaps, multiple blocks, and writer re-use.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob_reference_index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/block.go -->
## sources/storage-engines/pebble/sstable/block/block.go

Purpose: Defines core block handles, checksum validation, metadata casting, read environment accounting, and `Reader`, the central block-loading path for SSTables/blob files. It bridges object storage, block cache, buffer pools, checksums, decompression, tracing, and iterator statistics.

Important APIs/types/functions: `Handle`, `HandleWithProperties`, `DecodeHandle`, and `DecodeHandleWithProperties` encode/decode varint block references. `ChecksumType`, `Checksummer`, and `ValidateChecksum` implement CRC32c and XXHash64 trailer validation. `Metadata`, `CastMetadataZero`, and `CastMetadata` provide in-allocation metadata typed overlays. `ReadEnv` records stats/corruption callbacks/buffer-pool context. `Reader.Init`, `Read`, `doRead`, `GetFromCache`, `ReadRaw`, and `Close` make up the I/O surface.

Control flow: `Reader.Read` first chooses a cache/buffer-pool path. Background pool reads may still `Peek` the cache to count hits without populating it. Normal reads use `CacheHandle.GetWithReadHandle` to coordinate a single physical read among concurrent callers. Cache hits call `recordCacheHit`; cache misses call `doRead`, then install the cache value through the cache read handle. `doRead` optionally acquires `LoadBlockSema`, reads `Length+TrailerLen`, traces slow reads, updates stats, validates checksum, truncates off the trailer, decompresses if the compression indicator is nonzero, records decompression counters, initializes metadata through a caller-provided function, and returns a `Value`.

State and persistence behavior: The durable surface includes block handle varint encoding, trailer checksum bytes, compression indicator, and checksum type semantics. In-memory state includes `Reader` options/readable, block-cache `cache.Value`s, `BufferPool`-owned buffers, and per-block metadata stored before data in the same allocation.

Dependencies and integration points: Integrates with `objstorage.Readable/ReadHandle`, `sstableinternal.CacheOptions`, `internal/cache`, `internal/base` stats/tracing/corruption, `crlib/fifo` semaphore, `objiotracing`, `blockkind`, `crc`, `xxhash`, `bitflip`, and `bytesprofile`. Higher SSTable iterators pass `ReadEnv`, block kind, handles, and metadata initialization.

Risks: The reader depends on accurate handle lengths and valid trailers; malformed lengths can route into slice bounds in checksum/decompression code. Unknown checksum or compression indicators panic/assert rather than returning soft errors in several helpers. Metadata casting uses unsafe overlays and requires `MetadataSize`/alignment to remain adequate. Cache read-handle error propagation is subtle because each caller must report corruption with its own object context.

Test signals: This file has no direct test in the subset, but many SSTable reader/iterator tests exercise it. Neighboring tests cover `PhysicalBlockMaker`, temp buffers, compression stats, buffer pools, and block properties that rely on `Reader`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/blockkind/kind.go -->
## sources/storage-engines/pebble/sstable/block/blockkind/kind.go

Purpose: Defines the low-cardinality enumeration of logical block kinds used for cache categories, compression accounting, read tracing, and per-kind metrics.

Important APIs/types/functions: `Kind` is a `uint8` enum. Values include `SSTableData`, `SSTableIndex`, `SSTableValue`, `BlobValue`, `BlobReferenceValueLivenessIndex`, `TieringHistogram`, `Filter`, `RangeDel`, `RangeKey`, and `Metadata`, plus `Unknown` and `NumKinds`. `String` maps enum values to stable short names. `All` yields kinds 1 through `NumKinds-1`.

Control flow: There is no complex control flow. `All` is an `iter.Seq` that stops early if the yield function returns false.

State and persistence behavior: The enum is not directly documented here as a durable on-disk value, but it is used throughout block read/write logic as a semantic category. Array indexes such as `[blockkind.NumKinds]` depend on numeric ordering and range stability within a process.

Dependencies and integration points: Imported by `block` as alias `Kind`, compression and category stats, cache category mapping, block writers, readers, and tracing. The string names appear in slow-read tracing and stats/debug surfaces.

Risks: `String` indexes `kindString[k]` without bounds checks beyond Go's slice panic; invalid kinds panic. Adding enum values requires updating `kindString`, `NumKinds`-sized arrays, cache category mappings, and any per-kind stat logic.

Test signals: No direct tests here in the subset. Indirect coverage comes from compressor tests using kind routing and reader/stat paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/blockkind/kind.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/buffer_pool.go -->
## sources/storage-engines/pebble/sstable/block/buffer_pool.go

Purpose: Provides memory buffers for blocks either from the block cache allocation machinery or from a short-lived, non-thread-safe `BufferPool` used by compactions, metadata reads, external iteration, blob rewrites, and level checking.

Important APIs/types/functions: `Alloc` returns a `Value` backed by either `BufferPool` or `cache.Value`. `Value` exposes `BlockData`, `BlockMetadata`, `MakeHandle`, `Truncate`, `Release`, and a testing cache-install hook. `BufferHandle` abstracts cache-backed and pool-backed handles. `BufferPool.Init`, `Reason`, `Alloc`, and `Release` manage reusable `AllocedBuffer`s. `Buf.Valid` and `Buf.Release` manage pool slots. `ReasonForBufferPool` enumerates use cases.

Control flow: Pool allocation scans existing slots for an unused buffer large enough. If the pool is at capacity and has an unused too-small slot, it replaces that slot's allocation; otherwise it appends a new allocation. Releasing a `Buf` mangles bytes under invariants and nils the slot's slice to mark it reusable. `BufferPool.Release` refuses to release while any slot is still in use.

State and persistence behavior: There is no persistent format. Pool state holds `cache.Value` allocations and active subslices. The pool never shrinks during its lifetime, so peak working set affects retained memory until `Release`.

Dependencies and integration points: Used by `block.Reader.doRead` and `Alloc` to avoid populating the block cache for background or special reads. Depends on Pebble `cache`, `base`, `invariants`, and block `MetadataSize`. Cache hit/miss categories in `Reader.Read` depend on `ReasonForBufferPool`.

Risks: Not thread-safe; copying and releasing `Buf` values incorrectly may double-release or reuse live memory. `BufferHandle.Release` calls both possible backing releases; this relies on nil-safe cache release behavior and zero-value `Buf.Release`. Long-lived pools or unexpectedly large temporary blocks can retain substantial memory.

Test signals: `buffer_pool_test.go` datadriven tests exercise init, allocation, release, reuse, replacement of too-small idle buffers, and visual slot states.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/buffer_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/buffer_pool_test.go -->
## sources/storage-engines/pebble/sstable/block/buffer_pool_test.go

Purpose: Datadriven tests for `BufferPool` allocation, release, and reuse behavior.

Important APIs/types/functions: `writeBufferPool` renders each capacity slot as `[size]` for idle, `<size>` for in-use, and `[    ]` for unused capacity. `TestBufferPool` handles `init`, `alloc`, and `release` commands against a map of named `Buf` handles.

Control flow: Each datadriven command mutates a single `BufferPool`. `init` drains any previous state, initializes with a requested capacity, and prints state. `alloc` scans or grows through `BufferPool.Alloc` and stores the returned handle. `release` releases a named handle and deletes it. A deferred drain releases active handles and the pool at test end.

State and persistence behavior: Test state persists across commands inside a datadriven file, modeling realistic pool reuse. It does not touch durable SSTable data.

Dependencies and integration points: Uses `github.com/cockroachdb/datadriven`, standard `bytes`, `fmt`, `io`, `testing`, and `BufferPool` itself.

Risks: The renderer only exposes raw allocation sizes and in-use state; it does not validate memory contents, invariant mangling, or concurrency misuse. It assumes named handle discipline in testdata.

Test signals: Good signal for slot lifecycle and pool growth/replacement behavior. It complements block reader tests that use pools indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/buffer_pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/category_stats.go -->
## sources/storage-engines/pebble/sstable/block/category_stats.go

Purpose: Implements read-category registration, QoS tagging, and sharded block read statistics aggregation for iterator/file-cache usage.

Important APIs/types/functions: `Category`, `CategoryUnknown`, `CategoryMax`, `RegisterCategory`, `Categories`, `StringToCategoryForTesting`, `QoSLevel`, `CategoryStats`, `CategoryStatsShard`, `CategoryStatsCollector`, `Accumulator`, and `GetStats`. `CategoryStats` tracks block bytes, block bytes served from cache, and uncached read duration. `CategoryStatsAggregate` returns category-labeled totals.

Control flow: Categories are registered during initialization; after `Categories` is called, later registration panics because `categoriesList` is frozen. The collector lazily creates a `shardedCategoryStats` per category in a `sync.Map`, protected by a mutex around `LoadOrStore`. `Accumulator` hashes a caller-provided pointer-ish value through an LCG formula to select a shard. `GetStats` locks every shard, aggregates counters, and sorts by category.

State and persistence behavior: All state is process-local metrics. Category IDs are bounded by `CategoryMax`; category 0 is `unknown` and latency-sensitive. Shards are padded to reduce false sharing.

Dependencies and integration points: Used through `block.ReadEnv.IterStats` and file-cache category stats collectors. Depends on `sync`, `atomic`, `runtime.GOMAXPROCS`, `cmp/slices`, `time`, `unsafe`, `errors`, and `redact`.

Risks: Registration order assigns numeric category IDs, so all categories must be registered before readers call `Categories`. The `shardPadding` compile-time expression depends on `CategoryStatsShard` size staying below 64 bytes. Stats can over-count duration when concurrent readers wait on one physical read, as documented.

Test signals: No direct tests in this subset. Indirect coverage comes from iterator stats and category integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/category_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression.go -->
## sources/storage-engines/pebble/sstable/block/compression.go

Purpose: Defines block compression profiles, on-disk compression indicators, and counters for logical bytes compressed/decompressed by level and block kind.

Important APIs/types/functions: `CompressionProfile`, `CompressionSetting`, `SimpleCompressionSetting`, `AdaptiveCompressionSetting`, `UsesMinLZ`, built-in profiles (`NoCompression`, `SnappyCompression`, `ZstdCompression`, `MinLZCompression`, `FastestCompression`, `FastCompression`, `BalancedCompression`, `GoodCompression`), `CompressionProfileByName`, `CompressionIndicator`, `Algorithm`, `compressionIndicatorFromAlgorithm`, `CompressionCounters`, `ByKind`, and `ByLevel`.

Control flow: Built-in profiles register during package initialization into a case-insensitive map, with duplicate names asserting. Simple profiles use one setting for data/value/other blocks and a 12 percent minimum reduction. Fast/Balanced/Good vary data/value/other settings and adaptive cutoffs. `CompressionIndicator.Algorithm` converts durable trailer bytes to internal compression algorithms, while `compressionIndicatorFromAlgorithm` maps compression results back to trailer bytes.

State and persistence behavior: `CompressionIndicator` constants are explicitly durable file-format bytes and must not be changed. Profile names are user/property-facing and looked up case-insensitively. Counters are in-memory atomics grouped by L5, L6, and other levels and by data/value/other block kinds.

Dependencies and integration points: Depends on `internal/compression`, `base.Level`, `blockkind`, `atomic`, and `errors`. Used by `Compressor`, `PhysicalBlockMaker`, `Reader.doRead`, table options, and compression stats/properties.

Risks: Unsupported compression indicators and algorithms panic/assert. MinLZ format support depends on table format v6+ callers falling back for older formats. Adaptive settings must not equal the `OtherBlocks` setting to be meaningful. Adding block kinds or algorithms requires updating routing and mapping logic.

Test signals: `compressor_test.go` checks per-kind profile routing, `compression_stats_test.go` checks stats formatting/parsing, and `compression_test.go` exercises temp buffers and physical block creation under Snappy.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression_stats.go -->
## sources/storage-engines/pebble/sstable/block/compression_stats.go

Purpose: Collects, formats, parses, clones, aggregates, and scales per-compression-setting byte statistics for SSTables or groups of files.

Important APIs/types/functions: `CompressionStats` stores common cases inline (`noCompressionBytes`, `fastest`) and uncommon settings in a map. `CompressionStatsForSetting` tracks compressed/uncompressed bytes and computes `CompressionRatio`. `addOne`, `Add`, `All`, `String`, `Clone`, `Scale`, and `ParseCompressionStats` are the primary operations.

Control flow: `addOne` handles no-compression specially, inlines `fastestCompression`, and lazily allocates `others`. `All` yields non-empty settings. `String` builds sorted entries by algorithm and level, using compact `None:<bytes>` for no-compression and `<setting>:<compressed>/<uncompressed>` for compressed settings. `ParseCompressionStats` accepts empty strings, current `None` format, old `NoCompression:<x>/<x>` format, known settings from `compression.ParseSetting`, and accumulates unknown settings under `compression.Unknown`.

State and persistence behavior: The string form is stored in user/table properties and must remain backward-compatible. `Scale` approximates virtual table stats by multiplying by `size/backingSize` with sane lower bounds.

Dependencies and integration points: Used by `Compressor`/`PhysicalBlockMaker` to record block compression stats and by SSTable property handling. Depends on `internal/compression`, `crmath.ScaleUint64`, Go `iter`, `cmp`, `slices`, `strings`, and Pebble invariants.

Risks: `Reset` clears but does not nil the map, retaining capacity. `ParseCompressionStats` uses simple colon/comma splitting and `fmt.Sscanf`; invalid strings return generic parse errors. Unknown setting aggregation preserves total bytes but loses original algorithm names.

Test signals: `compression_stats_test.go` covers deterministic string order, accumulation, random round trips, unknown settings, and old-format parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression_stats_test.go -->
## sources/storage-engines/pebble/sstable/block/compression_stats_test.go

Purpose: Verifies `CompressionStats` text representation, parse round trips, unknown-setting compatibility, and old-format compatibility.

Important APIs/types/functions: `TestCompressionStatsString`, `TestCompressionStatsRoundtrip`, `TestParseCompressionStatsUnknown`, and `TestParseCompressionStatsOldFormat`.

Control flow: The string test incrementally adds no-compression, Snappy, MinLZ, ZSTD1, and ZSTD3 records and checks exact string ordering/aggregation. The round-trip test randomly selects subsets of settings and random byte sizes, serializes and parses after each addition, and expects canonical string equality. Unknown parsing feeds settings such as `MiddleOut10` and `Magic`, expecting them combined into an `unknown` entry. Old-format parsing accepts `NoCompression:x/x` and rewrites it to `None:x`.

State and persistence behavior: These tests protect the user-property format that may be stored in SSTables and later read by newer versions.

Dependencies and integration points: Uses `math/rand/v2`, `internal/compression`, and `stretchr/testify/require`.

Risks: The randomized test is nondeterministic and does not record a seed. It focuses on successful parse paths, not malformed input cases.

Test signals: Strong compatibility signal for canonical formatting and backward/forward handling of compression setting names.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression_test.go -->
## sources/storage-engines/pebble/sstable/block/compression_test.go

Purpose: Randomized stress test for `TempBuffer` append/reset/release behavior and `PhysicalBlockMaker.Make` with Snappy compression and CRC32c checksums.

Important APIs/types/functions: `TestBufferRandomized` uses `PhysicalBlockMaker.Init`, `NewTempBuffer`, `TempBuffer.Append`, `Data`, `Size`, `Reset`, `Release`, and `PhysicalBlock.Release`.

Control flow: For 25 iterations, the test sometimes releases and recreates a temp buffer, then appends random byte slices until reaching a random aggregate size between 1 KiB and 4 MiB. It verifies the buffer size and trailing appended bytes after each append, then builds a physical SSTable data block and releases it.

State and persistence behavior: Exercises temporary in-memory buffer growth and physical block creation, not persisted files. Physical blocks include compressed data and trailer bytes, but the test does not decode them.

Dependencies and integration points: Uses `blockkind.SSTableData`, `SnappyCompression`, `ChecksumTypeCRC32c`, `math/rand/v2`, time seed, and `require`.

Risks: No seed control beyond logging; failures may need the logged seed. The test validates buffer integrity and allocation lifecycle but not checksum/decompression round-trip correctness.

Test signals: Good stress signal for large append paths, temp-buffer reuse, and interaction between temp buffers and physical block creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compressor.go -->
## sources/storage-engines/pebble/sstable/block/compressor.go

Purpose: Wraps internal compression compressors with Pebble block-kind routing, adaptive compression support, minimum-reduction fallback, input-byte accounting, and compression statistics.

Important APIs/types/functions: `Compressor`, `MakeCompressor`, `maybeAdaptiveCompressor`, `Close`, `Compress`, `UncompressedBlock`, `Stats`, `InputBytes`, `Decompressor` alias, and `GetDecompressor`.

Control flow: Construction creates one compressor for data blocks, one for value/blob value blocks, and one for all other blocks. Adaptive compressors are used when a `CompressionSetting` specifies a cutoff and differs from `OtherBlocks`, sampling every 10 blocks with a 256 KiB half-life and random seed. `Compress` increments per-kind input bytes, compresses with the chosen compressor, rejects compressed output if it fails `MinReductionPercent`, records stats with the actual setting used, and returns the durable `CompressionIndicator`. `Close` closes all underlying compressors and zeros the struct.

State and persistence behavior: `Stats` are in-memory until copied into table properties. `InputBytes` feed logical compression counters on `PhysicalBlockMaker.Close`. The returned compression indicator is persisted in block trailers.

Dependencies and integration points: Depends on `internal/compression`, `blockkind`, and Go `iter`/`math/rand`. Used by `PhysicalBlockMaker` for all logical-to-physical block conversion.

Risks: `Compressor` is not documented as thread-safe and has mutable stats/input counters. `Stats` returns an internal pointer valid only until the next compressor call. The minimum-reduction comparison uses integer math; edge thresholds require care. Using a closed compressor after `Close` will operate on zeroed fields and likely panic.

Test signals: `compressor_test.go` validates block-kind routing for several compression settings. Compression stats tests cover the stats representation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compressor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compressor_test.go -->
## sources/storage-engines/pebble/sstable/block/compressor_test.go

Purpose: Verifies that `Compressor` chooses the compression setting dictated by a profile for each block kind.

Important APIs/types/functions: `TestCompressor` constructs random `CompressionProfile`s, then calls `MakeCompressor`, `Compress`, `compressionIndicatorFromAlgorithm`, and `Close`.

Control flow: Across 100 runs, the test randomly assigns settings to `DataBlocks`, `ValueBlocks`, and `OtherBlocks` with `MinReductionPercent=0`. It compresses a zeroed 1 KiB source as SSTable data, SSTable value, blob value, SSTable index, and metadata. Returned indicators must match data, value, value, other, and other settings respectively.

State and persistence behavior: Tests transient compressor state only. It indirectly protects durable trailer indicator selection.

Dependencies and integration points: Uses `internal/compression`, `blockkind`, `math/rand/v2`, and `require`.

Risks: It disables minimum-reduction fallback, so fallback-to-none behavior is not covered. It also uses simple zero input and non-adaptive profiles, so adaptive compressor behavior is only indirectly covered elsewhere.

Test signals: Strong signal for `ByKind.ForKind` routing and compression indicator conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/compressor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/flush_governor.go -->
## sources/storage-engines/pebble/sstable/block/flush_governor.go

Purpose: Decides when block writers should flush the current logical block before adding another KV, balancing target block size with allocator size-class fragmentation.

Important APIs/types/functions: `FlushGovernor`, `AllocationOverheadAllowance`, `MakeFlushGovernor`, `LowWatermark`, `ShouldFlush`, `String`, and `findClosestClass`.

Control flow: Without size classes, the governor sets low watermark to `targetBlockSize*blockSizeThreshold/100` rounded up and high/target boundary to the target size. With size classes, it adds `AllocationOverheadAllowance`, finds the closest allocator class, falls back to no-size-class mode if the target is outside useful class bounds, then sets target boundary to the closest class minus overhead and high watermark to the next class minus overhead. `ShouldFlush` never flushes if the block would not grow or if `sizeBefore` is below low watermark; it always flushes if `sizeAfter` exceeds high watermark; between target boundary and high watermark, it chooses the side with less wasted space.

State and persistence behavior: The governor is immutable and copied by value. It affects block boundaries and thus SSTable layout, index entries, cache allocation behavior, and block-property granularity, but has no serialized fields.

Dependencies and integration points: Depends on `internal/cache` metadata size, block `MetadataSize`, and sorted allocator size classes such as `sstable.JemallocSizeClasses`. Used by row/column block writers.

Risks: Size classes must be sorted for binary search. Constants assert slack and alignment; changes to cache/block metadata sizes can break compile-time checks. Thresholds near 100 are clamped to avoid low watermark exceeding target boundary.

Test signals: `flush_governor_internal_test.go` covers class selection, and `flush_governor_test.go` datadriven tests cover initialization and `ShouldFlush` behavior with custom and jemalloc classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/flush_governor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/flush_governor_internal_test.go -->
## sources/storage-engines/pebble/sstable/block/flush_governor_internal_test.go

Purpose: Unit-tests the unexported allocation class selection helper used by `FlushGovernor`.

Important APIs/types/functions: `TestFindClosestClass` calls `findClosestClass` against fixed size classes `[10,20,30,50]`.

Control flow: The test enumerates targets below, exactly at, between, and above classes, checking that the closest class is selected, with ties resolved by the existing comparison rule.

State and persistence behavior: No persistent state. It protects a decision that affects physical block boundaries.

Dependencies and integration points: Standard `testing` only; same package access permits testing the unexported helper.

Risks: Does not test unsorted classes or empty slices; those are caller assumptions.

Test signals: Focused signal for boundary math around closest-class choice.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/flush_governor_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/flush_governor_test.go -->
## sources/storage-engines/pebble/sstable/block/flush_governor_test.go

Purpose: Datadriven black-box tests for `FlushGovernor` construction and flush decisions.

Important APIs/types/functions: `TestFlushGovernor` calls `block.MakeFlushGovernor`, `FlushGovernor.String`, and `ShouldFlush`. It can use custom size classes or `sstable.JemallocSizeClasses`.

Control flow: The `init` command reads target block size, block-size threshold, size-class-aware threshold, and classes, then prints watermarks. The `should-flush` command evaluates a `sizeBefore`/`sizeAfter` pair and emits whether the governor would flush.

State and persistence behavior: Test state is a single `FlushGovernor` persisted across commands in the datadriven file.

Dependencies and integration points: Uses `datadriven`, external package `block_test`, and `sstable.JemallocSizeClasses`, giving coverage closer to public usage.

Risks: Coverage depends on testdata breadth. It does not fuzz arbitrary class arrays or assert panic/fallback behavior for malformed classes.

Test signals: Good regression coverage for writer-facing watermarks and decisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/flush_governor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/kv.go -->
## sources/storage-engines/pebble/sstable/block/kv.go

Purpose: Defines the one-byte value prefix stored with block values to distinguish in-place values, SSTable value-block handles, blob handles, same-prefix optimization, and short attributes.

Important APIs/types/functions: `ValuePrefix`, bit masks/constants for value kind, `IsInPlaceValue`, `IsValueBlockHandle`, `IsBlobValueHandle`, `SetHasSamePrefix`, `ShortAttribute`, `ValueBlockHandlePrefix`, `InPlaceValuePrefix`, `BlobValueHandlePrefix`, and `GetInternalValueForPrefixAndValueHandler`.

Control flow: Methods are bit tests and constructors. The two high bits encode value kind; bit `0x20` records whether a SET has the same key prefix as the previous SET in the block; low three bits encode `base.ShortAttribute` for non-in-place values.

State and persistence behavior: This prefix is part of encoded block values and therefore format-sensitive. The same-prefix bit supports block/value-block layout optimizations and must be interpreted consistently by readers.

Dependencies and integration points: Depends on `internal/base` for `ShortAttribute` and `InternalValue`. Used by row/column block writers and iterators, value-block handle decoding, blob handle decoding, and lazy value retrieval.

Risks: `ShortAttribute` is documented as requiring non-in-place values, but not enforced. Only three bits are available for user-defined attributes. Reserved/invalid combinations are not rejected here.

Test signals: `kv_test.go` covers constructors and accessors for in-place, value-block, and blob prefixes with same-prefix flags and attributes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/kv_test.go -->
## sources/storage-engines/pebble/sstable/block/kv_test.go

Purpose: Unit-tests `ValuePrefix` bit encoding/decoding for the supported value representations.

Important APIs/types/functions: `TestValuePrefix` exercises `ValueBlockHandlePrefix`, `BlobValueHandlePrefix`, `InPlaceValuePrefix`, `IsValueBlockHandle`, `IsBlobValueHandle`, `SetHasSamePrefix`, and `ShortAttribute`.

Control flow: A table of cases chooses which constructor to call, then asserts decoded kind flags and same-prefix flag. For value-block handles it verifies the short attribute round-trip.

State and persistence behavior: Protects a durable byte-level encoding used inside blocks.

Dependencies and integration points: Uses `base.ShortAttribute` and `stretchr/testify/require`.

Risks: The test does not check `ShortAttribute` for blob handles despite blob prefixes also encoding attributes. It does not test all bit values, reserved combinations, or invalid attributes above three bits.

Test signals: Solid coverage for expected constructor/accessor combinations and same-prefix flag behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/kv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/physical.go -->
## sources/storage-engines/pebble/sstable/block/physical.go

Purpose: Builds, owns, writes, and recycles physical blocks: logical block bytes plus compression indicator/checksum trailer. It also provides temporary buffers used throughout block writing.

Important APIs/types/functions: `PhysicalBlock`, `TrailerLen`, `Trailer`, `MakeTrailer`, `PhysicalBlockLength`, `AlreadyEncodedPhysicalBlock`, `OwnedPhysicalBlock`, `WriteAndReleasePhysicalBlock`, `PhysicalBlockMaker`, `PhysicalBlockFlags`, `NoFlags`, `DontCompress`, `TempBuffer`, `NewTempBuffer`, and temp buffer methods.

Control flow: `PhysicalBlockMaker.Init` constructs a `Compressor` and initializes a `Checksummer`. `Make` obtains a `TempBuffer`, compresses unless `DontCompress`, records uncompressed stats if skipped, computes checksum over physical bytes plus compression indicator, appends trailer, and returns a releasable `PhysicalBlock`. `WriteAndReleasePhysicalBlock` writes `tb.Data()` to an `objstorage.Writable` and releases even on error. `Close` transfers compressor input-byte counts to counters and closes compressors.

State and persistence behavior: The trailer is exactly 5 bytes: one compression indicator byte followed by little-endian uint32 checksum. `PhysicalBlockLength.WithTrailer/WithoutTrailer` maintains trailer-aware sizes. `TempBuffer` instances are pooled and retained only if below `tempBufferMaxReusedSize`.

Dependencies and integration points: Used by SSTable/blob writers to serialize blocks. Depends on `objstorage.Writable`, `internal/invariants`, `encoding/binary`, `sync.Pool`, `slices`, `Compressor`, and `Checksummer`.

Risks: Callers must release or transfer ownership of physical blocks to avoid retaining pooled buffers. `TempBuffer.Release` does not put back large buffers, and after releasing a large buffer it leaves `tb.b` non-nil but does not reinsert into the pool, so callers must not reuse released buffers. Checksum type support is inherited from `Checksummer`.

Test signals: `compression_test.go` stresses temp buffer append/reset/release and physical block creation. Broader writer/reader tests validate durable compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block/physical.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property.go -->
## sources/storage-engines/pebble/sstable/block_property.go

Purpose: Implements Pebble's block-property collection and filtering infrastructure: concise per-block/table properties used to skip data/index blocks and whole SSTables during iteration.

Important APIs/types/functions: `BlockPropertyCollector`, `BlockPropertyFilter`, `BoundLimitedBlockPropertyFilter`, `BlockIntervalCollector`, `IntervalMapper`, `BlockInterval`, `DecodeBlockInterval`, `BlockIntervalSuffixReplacer`, `BlockIntervalFilter`, `shortID`, `blockPropertiesEncoder`, `blockPropertiesDecoder`, `BlockPropertiesFilterer`, `IntersectsTable`, and internal `intersects`/`intersectsFilter`.

Control flow: Writers call `AddPointKey` for point entries, `AddRangeKeys` for range spans, `FinishDataBlock`, `AddPrevDataBlockToIndexBlock`, `FinishIndexBlock`, and `FinishTable`. `BlockIntervalCollector` unions point intervals into data/index/table state and range-key intervals directly into table state. Encoded block properties omit empty properties and store non-empty values as shortID byte, uvarint length, payload. Readers initialize a `BlockPropertiesFilterer` by testing table-level user properties and mapping property names to file-local short IDs; later per-block filtering decodes properties up to relevant short IDs, returning `blockIntersects`, `blockExcluded`, or `blockMaybeExcluded` for bound-limited filters.

State and persistence behavior: Table user properties store property name to string whose first byte is the file-local short ID and whose remainder is the table-level property. Block/index entries store compact shortID/property streams. `BlockInterval` encodes non-empty `[Lower,Upper)` as two uvarints: lower and width. Empty intervals encode as nil. The short ID limit is 256 collectors per SSTable.

Dependencies and integration points: Used by SSTable writers, index entries, reader/iterator block skipping, synthetic suffix handling, and range-key masking. Depends on `base.BlockPropertyFilter`, `base.CorruptionErrorf`, `SyntheticSuffix` from the SSTable/blockiter alias context, unsafe string-to-byte conversion, `sync.Pool`, and invariants.

Risks: Semantics are intentionally nondeterministic with respect to block boundaries and can surface extra KVs; value-dependent properties are unsafe with value separation. Bound-limited filtering is subtle and requires iterator-side proof that block bounds are within filter bounds. Encoded property corruption can break iteration. Unsafe conversion assumes filters do not mutate property bytes. Synthetic suffix support requires collectors/filters to implement replacement correctly.

Test signals: `block_property_test.go` extensively covers interval encode/decode, unions/intersections, collector sequencing, encoder/decoder sparse properties, table initialization, per-block filtering, full writer/reader datadriven cases, bound-limited masking, and suffix replacement helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property_obsolete.go -->
## sources/storage-engines/pebble/sstable/block_property_obsolete.go

Purpose: Implements a specialized block property that marks blocks/indexes/tables containing only obsolete keys so iterators can skip them.

Important APIs/types/functions: `obsoleteKeyBlockPropertyCollector`, `obsoleteKeyBlockPropertyFilter`, `AddPoint`, `obsoleteKeyBlockPropertyEncode`, and `obsoleteKeyBlockPropertyDecode`.

Control flow: The collector ignores generic `AddPointKey`/`AddRangeKeys`; obsolete-key-aware writer code calls the out-of-band `AddPoint(isObsolete)`. Finishing a data block encodes whether the block had no non-obsolete points and updates table state. `AddPrevDataBlockToIndexBlock` folds the just-finished block into index state and resets block state. `FinishIndexBlock` and `FinishTable` encode index/table obsolete-only state. The filter decodes the property and intersects only if the block may contain non-obsolete keys.

State and persistence behavior: Empty property means not obsolete; single byte `'t'` means obsolete-only. The collector tracks booleans for current block, current index block, and whole table. Suffix replacement validates old property but marks the block non-obsolete because rewriting loses obsolete certainty.

Dependencies and integration points: Depends on `BlockPropertyCollector`, `BlockPropertyFilter`, `base.AssertionFailedf`, and `errors`. Used with Pebble table format v4 obsolete-key semantics and table-cache filter insertion.

Risks: Because generic `AddPointKey` ignores keys, only callers that explicitly call `AddPoint` maintain correctness. Synthetic suffix intersection asserts if an obsolete block appears with suffix replacement, reflecting an invariant rather than graceful fallback. The filter is stateless by design for in-place slice modification elsewhere.

Test signals: Covered indirectly by block-property and table-format tests elsewhere; this subset does not include a direct obsolete-property test.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property_obsolete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property_test.go -->
## sources/storage-engines/pebble/sstable/block_property_test.go

Purpose: Comprehensive tests for block-property interval encoding, collection, filtering, writer/reader integration, bound-limited filters, and suffix replacement.

Important APIs/types/functions: Tests include `TestIntervalEncodeDecode`, `TestIntervalUnionIntersects`, `TestBlockIntervalCollector`, `TestBlockIntervalFilter`, `TestBlockPropertiesEncoderDecoder`, `TestBlockPropertiesFilterer_IntersectsUserPropsAndFinishInit`, `TestBlockPropertiesFilterer_Intersects`, `TestBlockProperties`, and `TestBlockProperties_BoundLimited`. Helpers include interval mappers, datadriven build/filter/iter runners, `boundLimitedWrapper`, `keyCountCollector`, and `testkeySuffixIntervalMapper`.

Control flow: Early unit tests validate interval and sparse property primitives. Filterer tests build table-level user properties, initialize short-ID maps, permute filter order, and check whole-table/per-block inclusion. Datadriven tests build real SSTables with selectable collectors, dump collector/table/block properties, evaluate table and block filters, and run point iterators. Bound-limited datadriven tests wrap filters to log `Intersects` and key-bound checks during iteration.

State and persistence behavior: Tests build real in-memory SSTables and inspect `Reader.UserProperties`, top-level and second-level index block handles with properties, and iterator-visible KVs. They exercise file-local short IDs and block/index/table property persistence.

Dependencies and integration points: Uses `datadriven`, `leaktest`, `base`, `keyspan`, `rangekey`, `testkeys`, `block`, SSTable `Reader`/`WriterOptions`, and iterator construction. It is a major integration test for block-property writer-reader behavior.

Risks: Some random collector tests use nondeterministic order/selection, though most behavior is datadriven. Helpers are powerful and can mask production-specific collectors not represented here. Value-based collector tests are useful but production value separation caveats remain.

Test signals: Very strong signal across serialization, filtering, table skipping, block skipping, two-level index decoding, synthetic suffix, and range-key masking interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property_test_utils.go -->
## sources/storage-engines/pebble/sstable/block_property_test_utils.go

Purpose: Provides reusable test-only block-property collectors, filters, masking filters, and maximum-suffix extraction for `internal/testkeys`-style suffixed keys.

Important APIs/types/functions: `NewTestKeysBlockPropertyCollector`, `NewTestKeysBlockPropertyFilter`, `testKeysBlockIntervalSyntheticReplacer`, `NewTestKeysMaskingFilter`, `TestKeysMaskingFilter`, `testKeysSuffixIntervalMapper`, `testKeysSuffixToInterval`, and `MaxTestKeysSuffixProperty`.

Control flow: The collector maps point key suffixes and range-key suffixes to `BlockInterval`s. Unsuffixed keys map to universal `[0, MaxUint64)`. The filter builds a `BlockIntervalFilter` over a requested suffix interval. The masking filter wraps the interval filter and updates its lower bound in `SetSuffix`. `MaxTestKeysSuffixProperty.Extract` decodes a table/block interval and emits `@Upper`, matching descending testkey timestamp semantics.

State and persistence behavior: The shared property name is `pebble.internal.testkeys.suffixes`; encoded properties use the same interval format as production block intervals. These utilities do not persist outside tests unless used by test SSTables.

Dependencies and integration points: Depends on `internal/testkeys`, `math`, `strconv`, and block-property primitives. Used by higher-level Pebble tests needing deterministic block-property filters and range-key masking behavior.

Risks: The synthetic replacer panics if the synthetic suffix is less than the original upper bound for non-universal intervals. Testkey suffix ordering differs from ordinary byte ordering, so these helpers are specialized and should not be copied into production collectors blindly.

Test signals: This is support code rather than a test itself; it underpins many block-property and masking tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/block_property_test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/block_iter.go -->
## sources/storage-engines/pebble/sstable/blockiter/block_iter.go

Purpose: Defines common interfaces for row-block and columnar-block data/index iterators, allowing SSTable iterators to abstract over block engine implementations.

Important APIs/types/functions: `Data` interface covers point-block iteration (`SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextWithSamePrefix`, `NextPrefix`, `Prev`, `KV`, `Valid`, `Error`, `Close`), buffer-handle ownership (`Handle`, `InitHandle`, `Invalidate`, `IsDataInvalidated`), lower-bound proof, and `treesteps.Node`. `Index` covers index block initialization, block-handle ownership, separator comparisons, `BlockHandleWithProperties`, seeking/stepping, invalidation, close, and `treesteps.Node`.

Control flow: There is no implementation here; the interfaces define contracts. Important contracts include `SeekPrefixGE`/`NextWithSamePrefix` positioning semantics when prefix mismatches occur, ownership transfer/release of `block.BufferHandle` on `InitHandle` and `Close`, and best-effort `IsLowerBound` behavior.

State and persistence behavior: State is implementation-defined in row/column iterators. The interface influences durable decoding because `Index.BlockHandleWithProperties` must parse encoded handles plus block properties from index entries.

Dependencies and integration points: Implemented by `rowblk.Iter`, `colblk.DataBlockIter`, `rowblk.IndexIter`, and `colblk.IndexBlockIter`. Used by higher-level SSTable iterators, table format dispatch, block-property filtering, and tree-step debugging.

Risks: The contracts are subtle around invalidation versus current KV validity, prefix mismatch positioning, and buffer-handle ownership. Implementations must release handles even on reinitialization/error to avoid leaks.

Test signals: No direct tests here; concrete row/column iterator tests elsewhere validate conformance. `block_property_test.go` indirectly uses `Index.BlockHandleWithProperties`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/block_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/doc.go -->
## sources/storage-engines/pebble/sstable/blockiter/doc.go

Purpose: Package documentation for `blockiter`, declaring it as the home for block-related interfaces common to row and columnar block engines.

Important APIs/types/functions: No code besides the package comment and `package blockiter`.

Control flow: None.

State and persistence behavior: None directly. It frames the package boundary for iterator abstractions used by SSTable readers.

Dependencies and integration points: Package-level integration point for rowblk and colblk iterator implementations.

Risks: Minimal; stale package documentation would be the main concern if the package grows beyond common interfaces.

Test signals: No direct tests needed for this documentation file.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/transforms.go -->
## sources/storage-engines/pebble/sstable/blockiter/transforms.go

Purpose: Defines logical transforms applied during block iteration, including synthetic sequence numbers, hiding obsolete points, synthetic prefixes, and synthetic suffixes.

Important APIs/types/functions: `Transforms`, `NoTransforms`, `FragmentTransforms`, `NoFragmentTransforms`, `SyntheticSeqNum`, `NoSyntheticSeqNum`, `SyntheticSuffix`, `SyntheticPrefix`, `SyntheticPrefixAndSuffix`, `MakeSyntheticPrefixAndSuffix`, accessors, `SyntheticPrefix.Apply`, `SyntheticPrefix.Invert`, and `SyntheticPrefixAndSuffix.RemoveSuffix`.

Control flow: `NoTransforms` checks all transform flags. Prefix/suffix helpers expose compact slices backed by one allocated buffer stored through an unsafe pointer. `MakeSyntheticPrefixAndSuffix` returns a zero value when both inputs are empty; otherwise it copies prefix then suffix into one buffer. `RemoveSuffix` preserves the prefix backing pointer and zeroes suffix length.

State and persistence behavior: These transforms are runtime iterator behavior, often for external/foreign/virtual tables, and do not rewrite physical blocks. Synthetic sequence numbers override key trailers when surfacing keys. Synthetic prefix/suffix changes logical keys seen by readers while underlying table bloom filters and comparisons may still operate on physical partial keys under documented constraints.

Dependencies and integration points: Used by row/column block iterators, fragment/range-key iterators, block-property synthetic suffix filtering, and external ingestion/virtual table code. Depends on `base`, `bytes`, `unsafe`, and `errors`.

Risks: Unsafe pointer backing relies on the allocated slice escaping and remaining live through the struct. Synthetic suffix has strict correctness constraints: unique prefixes, replacement suffix ordering, no range deletions, limited range-key support. `SyntheticPrefix.Invert` panics if called with a non-matching key.

Test signals: `transforms_test.go` covers zero/nonzero transform detection, prefix/suffix accessors, and `RemoveSuffix`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/transforms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/transforms_test.go -->
## sources/storage-engines/pebble/sstable/blockiter/transforms_test.go

Purpose: Unit-tests transform zero-value behavior and compact synthetic prefix/suffix storage.

Important APIs/types/functions: `TestTransforms`, `TestFragmentTransforms`, and `TestSyntheticPrefixAndSuffix`.

Control flow: The first two tests verify that zero transforms and explicitly empty prefix/suffix pairs count as no transforms, while `HideObsoletePoints`, nonzero synthetic sequence numbers, nonempty prefix, and nonempty suffix make transforms active. The prefix/suffix test constructs prefix+suffix, prefix-only, suffix-only, and removed-suffix cases, asserting accessors and lengths.

State and persistence behavior: Tests runtime transform value semantics, not persisted SSTable data.

Dependencies and integration points: Uses `stretchr/testify/require` and the `blockiter` package.

Risks: Does not test `SyntheticPrefix.Apply`/`Invert` or GC/lifetime behavior of the unsafe backing pointer. Does not test semantic restrictions around suffix ordering.

Test signals: Good signal for the public value-type API and default no-transform contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blockiter/transforms_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/base.go -->
## sources/storage-engines/pebble/sstable/colblk/base.go

Purpose: Provides low-level alignment constants/helpers and runtime memory function linknames used by columnar block encoding/decoding code.

Important APIs/types/functions: `align`, `alignWithZeroes`, constants `align16`, `align32`, `align64`, shift constants, and linknamed `memmove`/`mallocgc`.

Control flow: `align` rounds an integer offset up to the next multiple of a power-of-two alignment value. `alignWithZeroes` computes the aligned offset and writes zero bytes into padding for deterministic encodings when buffers are reused.

State and persistence behavior: Alignment affects columnar block binary layouts and deterministic padding bytes. The runtime linknames have no persisted state but are low-level allocation/copy hooks for other colblk code.

Dependencies and integration points: Used by bitmap and other columnar encoders/decoders. Depends on `unsafe`, `golang.org/x/exp/constraints`, and Go runtime internals through `go:linkname`.

Risks: `align` assumes power-of-two `val`. Runtime linknames are explicitly risky; comments note future Go versions may remove access and suggest maintained assembly alternatives. Misaligned or nondeterministic padding would affect encoded block bytes and tests.

Test signals: No direct tests here. `bitmap_test.go` indirectly exercises `align` and `alignWithZeroes` through bitmap offset/padding cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/base.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/bitmap.go -->
## sources/storage-engines/pebble/sstable/colblk/bitmap.go

Purpose: Implements a compact columnar boolean bitmap with optional all-zero encoding, 64-bit-word storage, summary words for fast set-bit predecessor/successor searches, a builder, and debug formatting.

Important APIs/types/functions: `Bitmap`, `DecodeBitmap`, `At`, `SeekSetBitGE`, `SeekSetBitLE`, `SeekUnsetBitGE`, `SeekUnsetBitLE`, `BitmapBuilder`, `Set`, `Reset`, `Size`, `InvertedSize`, `Invert`, `Finish`, `bitmapRequiredSize`, `bitmapToBinFormatter`, `nextBitInWord`, and `prevBitInWord`.

Control flow: Decoding reads a one-byte encoding tag. Zero encoding returns a nil-data bitmap; default encoding aligns to 8 bytes, computes required size, and builds an unsafe uint64 decoder over bitmap words plus summary words. Set-bit searches check the current word first, then use summary words to jump to the next/previous nonzero primary word. Unset-bit searches scan primary words for non-`MaxUint64`. Builder tracks words and `minNonZeroRowCount`; `Finish` writes encoding, padding, primary words truncated to row count, zeroes sparse tail words, masks extra bits past `nRows`, and writes summary words.

State and persistence behavior: Encoded layout is one tag byte, optional padding to 8-byte alignment, primary bitmap words, then summary words. Zero bitmaps use only the tag byte. Deterministic padding and tail-bit masking protect stable on-disk bytes and correct summary search behavior.

Dependencies and integration points: Implements `Array[bool]` and `ColumnWriter`; `DecodeBitmap` implements `DecodeFunc[Bitmap]`. Depends on `unsafeUint64Decoder`, `makeUintsEncoder`, `binfmt`, `treeprinter`, `invariants`, and low-level colblk alignment helpers.

Risks: Several methods rely on caller bounds per comments; invariant checks may be disabled. `DecodeBitmap` panics on short buffers rather than returning an error. `SeekSetBitGE` can return an index beyond `bitCount` if extra tail bits were not masked by the builder, making writer correctness critical. `prevBitInWord` is called with unsigned bit arithmetic, so callers must avoid underflow cases.

Test signals: `bitmap_test.go` provides fixed datadriven binary/seek tests, randomized probability/inversion tests over many sizes, bit primitive reconstruction tests, and a builder benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/bitmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/bitmap_test.go -->
## sources/storage-engines/pebble/sstable/colblk/bitmap_test.go

Purpose: Tests columnar bitmap encoding, binary formatting, fixed and randomized seek behavior for set/unset bits, inversion, and builder performance.

Important APIs/types/functions: `TestBitmapFixed`, `TestNextPrevBitInWord`, `dumpBitmap`, `TestBitmapRandom`, and `BenchmarkBitmapBuilder`.

Control flow: The fixed datadriven test builds bitmaps from textual 0/1 input, optional row/offset arguments, optional inversion, validates `Size`/`InvertedSize`/`Finish` offsets, decodes the bitmap, dumps bits, and prints binary layout through `bitmapToBinFormatter`. It also runs seek commands against the last built bitmap. The bit primitive test reconstructs random words by repeatedly calling next/prev helpers. The randomized test builds boolean arrays for fixed and random sizes/probabilities, optionally inverts, decodes, checks every `At`, and verifies set/unset predecessor/successor correctness by scanning gaps.

State and persistence behavior: Tests encoded byte layout, padding with nonzero offsets, all-zero/default encodings, summary table correctness, and tail truncation when builder writes beyond requested row count.

Dependencies and integration points: Uses `datadriven`, `binfmt`, `treeprinter`, `math/rand/v2`, `time`, `unicode`, and `require`.

Risks: Randomized tests seed from current time and log the seed, so failures are reproducible only if logs are available. The benchmark allocates a fresh builder per iteration and may not isolate builder reuse behavior.

Test signals: Strong coverage for correctness of bitmap search primitives, encoded structure, inversion, sparse/dense probabilities, row counts around word boundaries, and offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/bitmap_test.go -->
