# subset-b-008545 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/raw_bytes.go -->
# sources/storage-engines/pebble/sstable/colblk/raw_bytes.go

## Purpose
Implements `RawBytes`, the columnar block representation for an array of byte slices. It serializes an offset table followed by concatenated byte data, allowing columnar readers to return stable `[]byte` slices without per-row copies.

## Important APIs, Types, and Functions
- `RawBytes` stores `slices`, `UnsafeOffsets`, and an unsafe pointer to the data payload.
- `DecodeRawBytes` decodes the offset table using `DecodeUnsafeOffsets`, validates the computed end offset, and returns a zero-copy accessor.
- `RawBytes.At`, `Slice`, `Offsets`, and `Slices` expose individual slices and metadata.
- `RawBytesBuilder` implements `ColumnWriter` for `DataTypeBytes`.
- `RawBytesBuilder.Put`, `PutConcat`, `UnsafeGet`, `Size`, and `Finish` append values, estimate serialized size, and write the encoded column.
- `rawBytesToBinFormatter` supports binary layout descriptions used by datadriven tests and layout debugging.

## Control Flow
The builder starts with an initial zero offset, appends bytes to `data`, and records the cumulative data length in a `UintBuilder`. `Size` first sizes `rows+1` offsets and then adds the final cumulative byte count. `Finish` serializes the offsets table and copies the selected data prefix. Decoding reverses this path by reading `count+1` offsets, deriving the data start from the offset table end, and using the last offset to compute the full encoded span.

## State and Persistence Behavior
The persisted form is an offsets table encoded as a uint column, followed by raw byte data. Offsets are relative to the data section, not the full block. `Reset` keeps allocated capacity, mangles old data under invariant hooks, and reinitializes the zero offset. Decoded `RawBytes` points directly into the backing block buffer, so callers must keep that buffer alive and must not mutate returned slices.

## Dependencies and Integration Points
Depends on `UintBuilder`/`UnsafeOffsets`, `binfmt`, `treeprinter`, `invariants`, and unsafe pointer helpers. It is used by columnar data blocks, key/value blocks, and reference liveness blocks for byte-valued columns.

## Risks and Edge Cases
`DecodeRawBytes` panics on `math.MaxUint32` counts and on offsets extending beyond the byte slice. Unsafe pointer access requires block buffers to remain pinned. A mismatch between `Size` and `Finish` would corrupt subsequent columns. Large individual values force wider offset encodings, increasing block size.

## Test Signals
Covered by `raw_bytes_test.go`, which datadriven-tests size, binary formatting, decoding end offsets, and `At` lookups, plus benchmarks for builder and access throughput across slice lengths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/raw_bytes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/raw_bytes_test.go -->
# sources/storage-engines/pebble/sstable/colblk/raw_bytes_test.go

## Purpose
Datadriven and benchmark coverage for `RawBytesBuilder`, `DecodeRawBytes`, binary formatting, and random access over raw byte columns.

## Important APIs, Types, and Functions
- `TestRawBytes` runs `testdata/raw_bytes` commands.
- `build` command resets the builder, parses an artificial start offset, appends input lines, optionally truncates by `count`, writes to aligned storage, formats the encoded structure, and decodes it.
- `at` command reads values from the last decoded `RawBytes`.
- `BenchmarkRawBytes` measures builder throughput and `At` traversal for slice lengths 8, 128, and 1024 over 32 KiB of data.

## Control Flow
Each datadriven `build` command creates a fresh serialized column, validates `Size` against `Finish`, uses `rawBytesToBinFormatter` to display offsets/data, decodes from the adjusted start offset, and verifies decoded end offset. Later `at` commands operate on the retained decoded column.

## State and Persistence Behavior
The test intentionally allocates aligned buffers through `crbytes.AllocAligned`, exercising the same alignment assumptions as block serialization. It validates offset-relative persistence by varying start offset and checking decoded end offsets against the original absolute finish offset.

## Dependencies and Integration Points
Uses `datadriven`, `crstrings`, `crbytes`, `binfmt`, and `treeprinter`. It indirectly verifies `UintBuilder` offset serialization because `RawBytesBuilder` delegates its offset table to the uint column path.

## Risks and Edge Cases
The datadriven suite depends on stable binary-format output. Benchmarks discard output through `io.Discard`, so they test cost but not semantics. The `count` override exercises finishing a prefix of appended rows.

## Test Signals
Strong signal for exact serialized layout and access semantics. Benchmarks give performance regression coverage for both encoding and zero-copy lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/raw_bytes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints.go -->
# sources/storage-engines/pebble/sstable/colblk/uints.go

## Purpose
Defines compact unsigned integer column encodings for columnar blocks. It chooses among zero-width, 1-, 2-, 4-, and 8-byte storage with optional delta-base encoding to reduce per-row bytes.

## Important APIs, Types, and Functions
- `Uint` is the generic unsigned-integer constraint.
- `UintEncoding` stores width in low bits and delta mode in `uintEncodingDeltaBit`.
- `DetermineUintEncoding` and `DetermineUintEncodingNoDelta` choose encodings from min/max and row count.
- `byteWidth` maps integer bit length to 0/1/2/4/8 bytes.
- `UintBuilder` implements `ColumnWriter` for `DataTypeUint`.
- `UintBuilder.Init`, `InitWithDefault`, `Reset`, `Get`, `Set`, `Size`, and `Finish` build and serialize columns.
- `uintColumnSize` and `uintColumnFinish` encode the on-disk layout.
- `reduceUints`, `computeMinMax`, and `uintsToBinFormatter` support narrowing, slow-path stats, and human-readable formatting.

## Control Flow
`Set` grows the backing `[]uint64`, updates running min/max, and records the row that last changed the chosen encoding. `Size` and `Finish` ask `determineEncoding`; the fast path reuses stats when the caller includes the decisive row, otherwise `recalculateEncoding` scans the prefix. `uintColumnFinish` writes an encoding byte, optional little-endian 64-bit delta base, alignment padding, and a width-specific packed array.

## State and Persistence Behavior
A uint column persists as one encoding byte, optional delta base, aligned fixed-width values, and no payload for constant-zero or constant-delta encodings. `InitWithDefault` treats unset rows as zero and may leave elements unset, with `Finish` padding missing values as zero for non-delta encodings. Alignment is part of the persisted column layout and depends on the column offset.

## Dependencies and Integration Points
Used by raw byte offset tables, columnar key/value encoders, index writers, and liveness metadata. Depends on `encoding/binary`, `bits`, unsafe slice casting, endian conversion helpers, `binfmt`, `treeprinter`, and invariant assertions.

## Risks and Edge Cases
Delta encoding is avoided for very small row counts if the eight-byte base is not worth the per-row savings. `useDefault` is intentionally pessimistic for encoding choice. Unsafe casts require correct alignment and sufficient buffer sizing. Incorrect min tracking would either corrupt values or choose an oversized encoding. Width 8 must not be delta encoded.

## Test Signals
Covered by `uints_test.go` for byte width boundaries, encoding choice thresholds, datadriven binary layouts, and randomized encode/decode comparisons through `DecodeUnsafeUints`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints_decode.go -->
# sources/storage-engines/pebble/sstable/colblk/uints_decode.go

## Purpose
Provides a compact unsafe decoder holder for aligned little-endian 64-bit integer arrays in columnar blocks.

## Important APIs, Types, and Functions
- `unsafeUint64Decoder` holds only an unsafe pointer to keep embedded block decoders small.
- `makeUnsafeUint64Decoder` validates zero-length cases, pointer alignment, and buffer length before returning the decoder.
- The `At` method is implemented in endian-specific files outside this work item.

## Control Flow
Construction returns an empty decoder for `n == 0`. Otherwise it uses `unsafe.SliceData`, checks alignment against `align64`, verifies that `len(buf)` can hold `n` 64-bit values, and stores the raw pointer.

## State and Persistence Behavior
This file does not serialize data itself. It assumes the persisted buffer already contains little-endian 64-bit values and records a pointer into that buffer. The source buffer must outlive the decoder.

## Dependencies and Integration Points
Used by columnar block decoders that need low-overhead uint64 access. Depends on shared alignment constants and endian-specific methods in the `colblk` package.

## Risks and Edge Cases
Misaligned buffers panic. The decoder is intentionally unsafe and depends on callers validating buffer lifetime and bounds. Endianness behavior is split across build-specific files, so changes must stay compatible with those implementations.

## Test Signals
Indirectly tested by uint and unsafe uint tests that encode and then decode uint columns across widths and row counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints_decode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints_encode.go -->
# sources/storage-engines/pebble/sstable/colblk/uints_encode.go

## Purpose
Defines a generic unsafe integer encoder used to write native integer slices directly into target buffers and finalize them into little-endian byte order.

## Important APIs, Types, and Functions
- `serializedUint` constrains the storable integer widths to uint8/16/32/64.
- `uintsEncoder[T]` wraps a typed view over a byte buffer.
- `makeUintsEncoder` checks alignment and capacity and returns a typed slice view.
- `UnsafeSet`, `CopyFrom`, `Len`, and `Finish` populate and finalize the encoded data.

## Control Flow
The constructor builds an unsafe typed slice over `targetBuf`. Callers set values with `UnsafeSet` or `CopyFrom`; `Finish` is a no-op on little-endian platforms and reverses byte order for 2-, 4-, or 8-byte elements on big-endian platforms.

## State and Persistence Behavior
The encoder writes directly into the final serialized buffer. It has no ownership of the buffer and no separate persistence layer. The final bytes are expected to be little-endian regardless of host architecture.

## Dependencies and Integration Points
Supports uint-column and other fixed-width column encoders. Depends on shared `BigEndian`, byte-reversal helpers, alignment constants, and invariant-only bounds checks.

## Risks and Edge Cases
Bad alignment or undersized buffers panic. `UnsafeSet` omits normal bounds checks outside invariant builds. Callers must always invoke `Finish` before treating the buffer as serialized data on big-endian machines.

## Test Signals
Covered indirectly by uint column tests and unsafe uint tests, including encoded data validation through decoders.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints_encode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints_test.go -->
# sources/storage-engines/pebble/sstable/colblk/uints_test.go

## Purpose
Tests encoding choice, serialized layout, builder operations, and randomized round-trips for compact uint columns.

## Important APIs, Types, and Functions
- `TestByteWidth` covers width thresholds from zero through `math.MaxUint64`.
- `BenchmarkByteWidth` measures the precomputed table path.
- `TestUintEncoding` checks `DetermineUintEncoding` and small-row delta avoidance.
- `TestUints` is a datadriven state machine for init, write, get, size, and finish/format commands.
- `TestUintsRandomized` compares builder output against `DecodeUnsafeUints` for randomized row counts and values.

## Control Flow
The datadriven test mutates a single `UintBuilder` across commands, allowing tests of reset/default-zero behavior and partial finishes. Randomized tests build expected value slices, optionally leave default-zero rows unset, serialize, decode, and compare each row.

## State and Persistence Behavior
The test validates serialized size and binary formatting at arbitrary offsets, which exercises alignment padding. It also checks `InitWithDefault` semantics where encoded rows can be greater or fewer than explicitly set rows.

## Dependencies and Integration Points
Uses `datadriven`, `crbytes.AllocAligned`, `binfmt`, `treeprinter`, `require`, and `DecodeUnsafeUints`. It relies on shared `interestingIntRanges` for expected encodings.

## Risks and Edge Cases
Randomized seed is time-based and logged, so failures are reproducible manually but not deterministic by default. The suite explicitly targets row-count thresholds where delta-base overhead changes the best encoding.

## Test Signals
High-value coverage for boundary values, partial-prefix finishing, offset alignment, default-zero operation, and decoder compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/uints_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/unsafe_uints.go -->
# sources/storage-engines/pebble/sstable/colblk/unsafe_uints.go

## Purpose
Provides zero-copy decoders for compact uint columns and offset tables, translating `UintEncoding` metadata into unsafe accessors.

## Important APIs, Types, and Functions
- `UnsafeUints` implements `Array[uint64]` with pointer, delta base, and byte width.
- `DecodeUnsafeUints` reads the encoding byte, optional delta base, aligns the data pointer, and returns the accessor plus end offset.
- `makeUnsafeUints` validates allowed widths.
- `UnsafeOffsets` specializes offset access for non-delta 0/1/2/4-byte values.
- `DecodeUnsafeOffsets` rejects delta and 8-byte offset encodings.
- `unsafeGetUint32`, `unsafeSetUint32`, and `unsafeGetUint64` are no-bounds-check helpers.

## Control Flow
For zero rows, decoding returns an accessor pointing at `&b[off]` with width zero, relying on columnar blocks carrying a trailing padding byte. Non-empty decoding validates the encoding, consumes the optional base, aligns to element width, and computes the end offset from `rows * width`.

## State and Persistence Behavior
The accessor stores a pointer into immutable serialized block memory. `UnsafeUints.At` and `UnsafeOffsets.At/At2` are provided by endian-specific files and apply base/width decoding when accessed.

## Dependencies and Integration Points
Used throughout columnar block decoders, especially for uint columns and raw-byte offsets. Integrates with `UintBuilder`, endian helpers, and invariant bounds checks.

## Risks and Edge Cases
The zero-row path assumes callers provide an allocated padding byte. Offset decoding is intentionally stricter than generic uint decoding. Incorrect end-offset calculation can desynchronize subsequent column decoders.

## Test Signals
Covered by `unsafe_uints_test.go` across encoding ranges, row counts, offset specialization, and benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/unsafe_uints.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/unsafe_uints_test.go -->
# sources/storage-engines/pebble/sstable/colblk/unsafe_uints_test.go

## Purpose
Validates and benchmarks zero-copy uint and offset accessors over serialized uint columns.

## Important APIs, Types, and Functions
- `TestUnsafeUints` generates values from each interesting integer range and row count, serializes with `UintBuilder`, decodes with `DecodeUnsafeUints`, and compares all values.
- For non-delta widths up to 4 bytes, it also decodes `UnsafeOffsets` and validates `At` and `At2`.
- `BenchmarkUnsafeUints` measures random `At` access across width/delta profiles.
- `BenchmarkUnsafeUintOffsets` measures offset-specialized access.
- `encodeRandUints`, `benchmarkUnsafeUints`, and `benchmarkUnsafeOffsets` are helpers.

## Control Flow
Tests build aligned buffers with an extra trailing padding byte, serialize values, decode, and compare every row. Benchmarks precompute random read indices to isolate accessor overhead.

## State and Persistence Behavior
The tests exercise serialized buffers created by the production `UintBuilder`, not hand-crafted bytes. The extra padding byte checks the same pointer-safety contract used in columnar block serialization.

## Dependencies and Integration Points
Depends on `interestingIntRanges`, `crbytes.AllocAligned`, randomized PCG generators, and the uint builder. It validates endian-specific `At` implementations indirectly.

## Risks and Edge Cases
Random seeds use wall-clock time, so failures require logged seed capture. Offset tests only apply where the encoding is legal for offsets.

## Test Signals
Strong round-trip coverage for every supported width class and delta mode, with performance baselines for hot unsafe access paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/unsafe_uints_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/value_liveness_block.go -->
# sources/storage-engines/pebble/sstable/colblk/value_liveness_block.go

## Purpose
Implements a columnar reference liveness block used by SSTables with blob references. Each row maps a blob reference ID to encoded value-liveness bytes.

## Important APIs, Types, and Functions
- Constants define a one-column, no-custom-header block layout.
- `ReferenceLivenessBlockEncoder` owns a `RawBytesBuilder` and `BlockEncoder`.
- `Init`, `Reset`, `AddReferenceLiveness`, `Count`, `size`, and `Finish` build the block.
- `ReferenceLivenessBlockDecoder` owns a `RawBytes` column and `BlockDecoder`.
- `Init`, `DebugString`, `Describe`, `BlockDecoder`, and `LivenessAtReference` decode and inspect the block.

## Control Flow
The encoder enforces dense, ordered reference IDs by requiring `referenceID == values.Rows()`. `size` computes the columnar header plus raw bytes column plus one padding byte. `Finish` initializes a version-1 columnar block header and encodes the raw bytes column. The decoder initializes a block decoder and extracts column zero as `RawBytes`.

## State and Persistence Behavior
The persisted block is a normal columnar block with one `DataTypeBytes` column and a final padding byte. Row index equals `base.BlobReferenceID`, so missing IDs cannot be represented sparsely.

## Dependencies and Integration Points
Used by `RawColumnWriter` when writing blob reference index blocks. Layout debugging decodes these values and passes them to blob liveness decoding. Depends on `RawBytesBuilder`, `BlockEncoder`, `BlockDecoder`, `binfmt`, `treeprinter`, and `block.MetadataSize` sizing constraints.

## Risks and Edge Cases
Out-of-order or sparse reference IDs panic. The block metadata size assertion protects reader cache metadata embedding. Empty encoders return a zero-size block but `Finish` still constructs a block if called.

## Test Signals
Covered by `value_liveness_block_test.go`, and indirectly by columnar writer/blob-reference paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/value_liveness_block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/value_liveness_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/value_liveness_block_test.go

## Purpose
Datadriven coverage for reference liveness block encoding and debug formatting.

## Important APIs, Types, and Functions
- `TestValueLivenessBlock` runs `testdata/value_liveness_block`.
- `build` command initializes an encoder, adds one liveness value per input line using the line number as reference ID, finishes, decodes, and returns `DebugString`.

## Control Flow
Input lines are split into fields, the first field becomes the encoded value, rows are added densely, and the decoder immediately reads the resulting bytes to verify structure through formatted output.

## State and Persistence Behavior
The test exercises the dense row/reference-ID contract and checks the exact columnar block representation via `DebugString`.

## Dependencies and Integration Points
Uses `datadriven`, string parsing, and the production encoder/decoder.

## Risks and Edge Cases
The test focuses on layout formatting, not semantic decoding of blob liveness bitmaps. Malformed input lines would panic due to field indexing.

## Test Signals
Useful regression signal for header, raw bytes column encoding, and debug description stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/value_liveness_block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk_writer.go -->
# sources/storage-engines/pebble/sstable/colblk_writer.go

## Purpose
Implements `RawColumnWriter`, the SSTable raw writer for `TableFormatPebblev5+` column-oriented data, index, and keyspan blocks. It coordinates point/range key ingestion, block flushing, index buffering, value/blob metadata, filters, properties, and final file layout.

## Important APIs, Types, and Functions
- `RawColumnWriter` holds writer options, metadata, properties, columnar data/index/keyspan writers, value-block writer, blob liveness writer, filter writer, block property collectors, async write queue, and `layoutWriter`.
- `newColumnarWriter` initializes defaults, flush governors, encoders, collectors, filters, value blocks, and the data-block write goroutine.
- Public/raw writer methods include `Error`, `EstimatedSize`, `ComparePrev`, `IsLikelyMVCCGarbage`, `SetSnapshotPinnedProperties`, `Metadata`, `EncodeSpan`, `Add`, `AddWithBlobHandle`, `AddWithDualTierBlobHandles`, `Close`, `rewriteSuffixes`, `copyDataBlocks`, `addDataBlock`, `copyProperties`, and `SetValueSeparationProps`.
- Internal helpers include `evaluatePoint`, `internalAdd`, `flushDataBlockWithoutNextKey`, `enqueueDataBlock`, `enqueuePhysicalBlock`, `finishIndexBlock`, `flushBufferedIndexBlocks`, `drainWriteQueue`, `getExistingFilter`, and `shouldFlushWithoutLatestKV`.

## Control Flow
`Add` validates point key kind, evaluates ordering/obsolete/value-block decisions, stores values in-place or in value blocks, updates tiering metadata, and delegates to `internalAdd`. `internalAdd` appends to the current data block, decides whether to flush before the latest KV, updates block properties, filters, writer metadata, and table properties. Data blocks are compressed/checksummed and sent to a write queue; index entries are buffered and may create two-level indexes. `Close` flushes pending data, drains the write queue, writes index/filter/range/value/blob/tiering/properties blocks, finalizes attributes and footer, records metadata, and clears resources.

## State and Persistence Behavior
Persistent state includes columnar data blocks, columnar index blocks, optional two-level top index, table filter, range deletion/key blocks, value blocks/index, blob reference liveness block, tiering histogram, properties block, metaindex, and footer. Writer state tracks obsolete bits, sequence number bounds, smallest/largest keys, raw size/count properties, tombstone-dense block counts, compression stats, and block property collector outputs. Data blocks are written asynchronously but metadata blocks are written synchronously after the data queue drains.

## Dependencies and Integration Points
Integrates with `colblk` data/index/keyspan encoders, `layoutWriter`, `block.PhysicalBlockMaker`, `valblk.Writer`, blob handles, tiered metadata, block property collectors, table filters, suffix rewriting, and `CopySpan`. It depends on writer options from `options.go`, table format capabilities from `format.go`, and properties serialization from `properties.go`.

## Risks and Edge Cases
Key order checks and obsolete-bit correctness are critical, especially strict-obsolete SSTables. Value blocks are only used for likely MVCC garbage and require careful prefix comparison. Blob handles require v6+ and dual-tier handles require tiering columns. `Close` must preserve data block write ordering and detect write-queue errors. Copy/suffix rewrite paths deliberately skip or copy some derived metadata, which can overcount properties or omit block properties. The writer is not reusable after `Close`.

## Test Signals
Covered by `colblk_writer_test.go` datadriven layout/properties tests, broader `data_test.go` helpers, writer tests outside this subset, copier tests, and invariant validation of encoded data blocks when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk_writer_test.go -->
# sources/storage-engines/pebble/sstable/colblk_writer_test.go

## Purpose
Datadriven tests for building and inspecting columnar-format SSTables with `RawColumnWriter`.

## Important APIs, Types, and Functions
- `TestColumnarWriter` walks `testdata/columnar_writer`.
- `build` command constructs a v5, no-compression writer using `testkeys` schema and test block property collector, then parses test SST input.
- `open` command creates a reader over the in-memory object.
- `layout` command calls `Layout().Describe(true, ...)`.
- `props` command reads and prints the properties block.

## Control Flow
The test holds metadata, memory object, and reader across commands so a datadriven script can build, open, inspect layout, and inspect properties in sequence. Existing readers are closed before reopening.

## State and Persistence Behavior
SSTables are built in memory using `objstorage.MemObj`, allowing the test to inspect exact persisted layout without filesystem effects. Writer options may be overridden by datadriven arguments through shared helpers.

## Dependencies and Integration Points
Uses `runBuildMemObjCmd`, `optsFromArgs`, `NewReader`, `colblk.DefaultKeySchema`, test block property collectors, and `Layout.Describe`.

## Risks and Edge Cases
The default table format is pinned to v5 unless overridden, so later format-specific behavior needs explicit datadriven args. Exact layout output is sensitive to encoding and property changes.

## Test Signals
Good signal for columnar writer end-to-end layout, metadata, block properties, and properties serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/comparer.go -->
# sources/storage-engines/pebble/sstable/comparer.go

## Purpose
Re-exports comparer and merger-related base types from the public `sstable` package.

## Important APIs, Types, and Functions
- Type aliases: `Compare`, `Equal`, `AbbreviatedKey`, `Separator`, `Successor`, `Split`, `Comparer`, and `Merger`.
- Variable alias: `DefaultComparer`.

## Control Flow
There is no runtime control flow beyond alias resolution at compile time.

## State and Persistence Behavior
No state is persisted. The aliases shape public API compatibility and allow callers to configure reader/writer ordering without importing internal base packages.

## Dependencies and Integration Points
Depends on `internal/base`. Used by `ReaderOptions`, `WriterOptions`, external SSTable construction, and debugging tools.

## Risks and Edge Cases
Because these are aliases, changes in `base` type definitions propagate directly to the public `sstable` API. Comparer consistency remains essential for reading and writing SSTables.

## Test Signals
No direct tests in this file; exercised by all reader/writer tests that use `sstable.Comparer` or `DefaultComparer`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/comparer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/block_analyzer.go -->
# sources/storage-engines/pebble/sstable/compressionanalyzer/block_analyzer.go

## Purpose
Analyzes individual SSTable/blob blocks by measuring compressibility and compression/decompression performance across predefined compression profiles.

## Important APIs, Types, and Functions
- `BlockAnalyzer` stores aggregate `Buckets`, compressors for every profile, decompressor instances, a MinLZFastest compressor for test compressibility, and scratch buffers.
- `NewBlockAnalyzer`, `ResetCompressors`, `Close`, `Block`, `Buckets`, `runExperiment`, and `ensureLen` manage lifecycle and measurement.

## Control Flow
`Block` classifies a block by size and MinLZFastest compressibility, updates uncompressed-size samples, and runs each profile experiment. `runExperiment` ensures scratch capacity, yields before timing, compresses, decompresses, verifies decompression through the decompressor API, and records weighted ns/byte and compression-ratio metrics.

## State and Persistence Behavior
No on-disk persistence. State accumulates in `Buckets` until `Close` or object discard. Adaptive compressors are reset per SSTable through `ResetCompressors` so cross-file history does not affect results.

## Dependencies and Integration Points
Used by `FileAnalyzer`. Depends on `internal/compression`, `block.Compressor`, `crtime`, `metricsutil` via `Buckets`, and block kinds.

## Risks and Edge Cases
Measurements are sensitive to scheduler noise despite `runtime.Gosched`. Scratch buffers grow to block size plus headroom. Panics on decompression errors rather than returning them. Compression profile state must be reset for fair per-file results.

## Test Signals
Indirectly exercised by `file_analyzer_test.go`, while bucket formatting and classification are covered by `buckets_test.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/block_analyzer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/buckets.go -->
# sources/storage-engines/pebble/sstable/compressionanalyzer/buckets.go

## Purpose
Defines classification buckets and report formatting for compression analyzer results.

## Important APIs, Types, and Functions
- `BlockSize` categories: `Small`, `Medium`, `Large`, `Huge`.
- `MakeBlockSize` maps byte sizes to cutoff ranges.
- `Compressibility` categories: incompressible through highly compressible.
- `MakeCompressibility` maps uncompressed/compressed ratio to categories.
- `Profiles` lists Snappy, MinLZ1, Zstd1, adaptive Zstd profiles, and Zstd3.
- `Buckets`, `Bucket`, and `PerProfile` store Welford aggregates.
- `Buckets.String` and `Buckets.ToCSV` format tabular and CSV reports.
- `toMBPS` and `stdDevStr` convert timing and variability metrics.

## Control Flow
Formatting iterates all block kinds, size buckets, and compressibility buckets, skipping buckets below `minSamples`. For each included bucket, it prints average size, compression ratio, compression speed, and decompression speed for every profile.

## State and Persistence Behavior
All state is in-memory aggregate statistics. Reports are text/CSV snapshots derived from `metricsutil.Welford` and weighted Welford accumulators.

## Dependencies and Integration Points
Consumed by `BlockAnalyzer` and `FileAnalyzer` callers. Depends on `internal/compression`, `block.CompressionProfile`, `blockkind.All`, `metricsutil`, and tabwriter/time formatting.

## Risks and Edge Cases
Cutoff interpretation is encoded in both constants and `String`; changing cutoffs changes report compatibility. `MakeCompressibility` divides by compressed size and assumes nonzero compressed output. Formatting omits low-sample buckets, which can hide sparse data.

## Test Signals
Covered by `buckets_test.go` for block-size classification, compressibility classification, and deterministic example string/CSV output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/buckets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/buckets_test.go -->
# sources/storage-engines/pebble/sstable/compressionanalyzer/buckets_test.go

## Purpose
Datadriven tests for compression analyzer bucket classification and report formatting.

## Important APIs, Types, and Functions
- `TestBuckets` supports `block-size`, `compressibility`, `example-buckets-string`, and `example-buckets-csv` commands.
- `exampleBuckets` creates deterministic random aggregates across block kinds, sizes, compressibility categories, and profiles.

## Control Flow
Commands parse line-oriented numeric input for classifications or build a sample `Buckets` structure and format it with a configurable minimum sample threshold.

## State and Persistence Behavior
The example bucket generator uses a fixed PCG seed, making report output stable. It populates Welford accumulators rather than hard-coding formatted rows.

## Dependencies and Integration Points
Uses `datadriven`, `crstrings`, `blockkind.All`, `rand/v2`, and the production formatting APIs.

## Risks and Edge Cases
Tests are golden-output sensitive; legitimate formatting changes require testdata updates. Randomized example generation is deterministic but still indirect, making individual bucket values less obvious from reading the test.

## Test Signals
Provides stable coverage for bucket boundaries and public report formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/buckets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer.go -->
# sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer.go

## Purpose
Analyzes all relevant blocks in an SSTable file by reading its layout and feeding block data into `BlockAnalyzer`.

## Important APIs, Types, and Functions
- `FileAnalyzer` stores a `BlockAnalyzer`, optional token-bucket read limiter, and SSTable reader options.
- `NewFileAnalyzer`, `Buckets`, `Close`, `SSTable`, and `sstBlock` implement lifecycle and file analysis.

## Control Flow
`SSTable` resets compressors, opens an `sstable.Reader`, gets the layout, builds a list of data/index/filter/range/value/metadata blocks, sorts them by offset for readahead, and calls `sstBlock` for each non-empty handle. `sstBlock` rate-limits by block length when configured, reads the block through the block reader without metadata initialization, analyzes it, and releases the buffer.

## State and Persistence Behavior
The analyzer does not write files. It closes the readable through the reader in normal cases and explicitly closes it if reader creation fails. Accumulated results remain in the embedded `BlockAnalyzer`.

## Dependencies and Integration Points
Depends on `sstable.Reader`, `Layout`, `objstorage`, `block.Reader`, `blockkind`, and `tokenbucket`. It rejects cache-enabled reader options because the analyzer does not populate block metadata for cached entries.

## Risks and Edge Cases
Blob files are not supported. Zero-length handles are skipped, but the block list may include absent optional handles. Cache options panic on construction. The top index is appended even if empty and skipped later.

## Test Signals
Covered by `file_analyzer_test.go`, which analyzes fixture SSTables and normalizes unstable timing/compression outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer_test.go -->
# sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer_test.go

## Purpose
Datadriven tests for SSTable-level compression analysis over fixture files.

## Important APIs, Types, and Functions
- `TestFileAnalyzer` supports the `sst` command with one file path per input line.
- The test constructs `NewFileAnalyzer(nil, sstable.ReaderOptions{})`.
- It replaces the test-compressibility compressor with Snappy for platform-stable classification.

## Control Flow
For each input path, the test opens the file from the default VFS, wraps it as an `objstorage.Readable`, and calls `SSTable`. After all files are analyzed, it clears timing metrics and all non-Snappy compression-ratio metrics before formatting `Buckets.String(1)`.

## State and Persistence Behavior
The analyzer accumulates results across all listed SSTables in a single test command. Unstable metrics are zeroed to keep golden output deterministic.

## Dependencies and Integration Points
Uses fixture data under `testdata/file_analyzer`, `compression.GetCompressor`, `metricsutil.WeightedWelford`, `objstorage`, `sstable`, and VFS.

## Risks and Edge Cases
The test intentionally does not assert timing behavior. Platform-dependent MinLZ output is avoided by swapping in Snappy for classification.

## Test Signals
Good integration signal that `FileAnalyzer` can open SSTables, enumerate layout blocks, and produce stable bucket reports.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/copier.go -->
# sources/storage-engines/pebble/sstable/copier.go

## Purpose
Implements `CopySpan`, an approximate block-level SSTable subset copier. It copies whole intersecting data blocks to a new SSTable without decompressing/re-encoding every key.

## Important APIs, Types, and Functions
- `CopySpan` is the main entry point.
- `ErrEmptySpan` reports when no blocks can include the requested span.
- `indexEntry` stores an index separator and block handle with properties.
- `intersectingIndexEntries` finds data-block index entries intersecting `[start, end)`, including two-level indexes.
- `copyWholeFileBecauseOfUnsupportedFeature` falls back to byte-for-byte whole-file copy when unsupported attributes are present.

## Control Flow
`CopySpan` closes input on exit, falls back for unsupported features, configures a raw writer without filters/block property collectors, reads metaindex/properties/filter/index, copies original properties, finds intersecting blocks, and writes blocks either from cache or grouped reads through the writer. Finally it closes the writer and returns the output metadata size.

## State and Persistence Behavior
The output SSTable contains whole original data blocks for the approximate span, an updated index and footer, a copied filter, and copied table properties that may overcount. It omits block properties because individual key data is not processed. Unsupported value/range-key/range-del attributes trigger whole-file copy instead of partial copy.

## Dependencies and Integration Points
Integrates with `Reader`, `RawColumnWriter` copy helpers, `layout` attributes, object storage read handles, cache handles, table filters, and index iterators. Used by virtual/backing SSTable workflows that need fast physical subset creation.

## Risks and Edge Cases
The span is approximate because whole blocks are copied and adjacent keys may be included. Empty spans return `ErrEmptySpan` only when the index search finds no candidate blocks. Properties can overcount. Cached blocks are added as uncompressed blocks and recompressed, while uncached blocks are copied as already-encoded physical blocks. Unsupported features degrade to whole-file copy.

## Test Signals
Covered by `copier_test.go` datadriven build/iterate/copy/describe/props scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/copier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/copier_test.go -->
# sources/storage-engines/pebble/sstable/copier_test.go

## Purpose
Datadriven integration tests for block-level SSTable span copying.

## Important APIs, Types, and Functions
- `TestCopySpan` builds an in-memory filesystem, cache, key schema, and file-number mapping.
- `getReader` opens SSTables with cache and bloom filter decoder options.
- Commands include `build`, `iter`, `copy-span`, `describe`, and `props`.

## Control Flow
`build` writes a test SSTable with small block size to create many blocks. `iter` opens and scans a file with optional bounds. `copy-span` opens a reader and a separate readable for `CopySpan`, writes output to the memory FS, and reports copied size. `describe` prints non-verbose layout, and `props` prints properties.

## State and Persistence Behavior
All files live in `vfs.NewMem`. Cache handles are configured with per-file numbers to exercise cache hit/miss behavior. Output files are added back into the same memory filesystem for subsequent inspection.

## Dependencies and Integration Points
Uses `datadriven`, `objstorageprovider`, `NewWriter`, `NewReader`, `CopySpan`, `Layout.Describe`, bloom filter decoding, `testkeys`, and columnar key schemas.

## Risks and Edge Cases
The test relies on small block sizes to make copy behavior visible. It covers observable behavior but does not directly assert internal cache-hit grouping decisions.

## Test Signals
Good end-to-end signal for partial block copying, output readability, layout preservation, and property behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/copier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/data_test.go -->
# sources/storage-engines/pebble/sstable/data_test.go

## Purpose
Provides shared datadriven test helpers for building SSTables, opening readers, iterating, and rewriting suffixes across the `sstable` package tests.

## Important APIs, Types, and Functions
- `optsFromArgs` parses writer options and fills test comparer/key schema defaults.
- `runBuildMemObjCmd`, `runBuildCmd`, and `runBuildRawCmd` build SSTables in memory or object storage and return metadata/readers.
- `openReader` constructs reader options with key schemas and filter decoders.
- `runIterCmdOption`, `runIterCmdOptions`, and option helpers configure iterator test behavior.
- `runIterCmd` interprets line-oriented iterator commands and formats results.
- `runRewriteCmd` rewrites key suffixes into a new in-memory object and returns a fresh reader.

## Control Flow
Build helpers parse options, construct raw writers, parse test SST input, close writers, collect metadata, and open readers. `runIterCmd` maintains iterator state across commands such as seek, first/last, next/prev, bounds changes, stats, masking, and internal iterator state inspection. `runRewriteCmd` parses `from`/`to`, invokes `rewriteKeySuffixesInBlocks`, closes the old reader, and opens a new one.

## State and Persistence Behavior
Most helpers use `objstorage.MemObj`, but `runBuildRawCmd` exercises a real provider over an in-memory VFS. Iterator commands mutate iterator bounds, current KV, prefix/masking state, and optional stats. Build helpers ensure writers/readers are closed on errors.

## Dependencies and Integration Points
Used by many SSTable tests, including columnar writer tests in this subset. Depends on datadriven parsing, test key comparer/schema, blob test values, bloom/test filter decoders, object storage provider, blockkind stats, and block iterators.

## Risks and Edge Cases
Because this is shared test infrastructure, subtle formatting changes can affect many golden tests. `runIterCmd` contains test-only masking and internal-state inspection logic that must track iterator implementation changes. Error cleanup paths are important to avoid leaked readers/writers in tests.

## Test Signals
This file is itself test harness code; its value is enabling broad datadriven coverage of SSTable building, iteration, filters, stats, and rewrite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/data_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/external_reader.go -->
# sources/storage-engines/pebble/sstable/external_reader.go

## Purpose
Provides public shims for callers using `sstable.NewReader` directly to configure and evict block cache entries without reaching into internal packages.

## Important APIs, Types, and Functions
- `CacheHandle` aliases `cache.Handle`.
- `SetCacheOptions` sets `ReaderOptions.CacheOpts` from a cache handle and caller-assigned file number.
- `CacheHandleEvictFile` evicts all cached blocks for a file number.

## Control Flow
`SetCacheOptions` writes `sstableinternal.CacheOptions` into the supplied options. `CacheHandleEvictFile` delegates to the cache handle’s file eviction method.

## State and Persistence Behavior
No SSTable bytes are changed. State affected is reader cache configuration and cache contents. File numbers are caller-assigned and must be unique within the cache handle namespace.

## Dependencies and Integration Points
Bridges public `sstable` users to `internal/cache` and `internal/sstableinternal` cache options. Normal Pebble DB usage does not need this file because Pebble manages cache options internally.

## Risks and Edge Cases
Cache key collisions are possible if external callers reuse file numbers incorrectly. The helpers expose cache configuration but not lifecycle management beyond eviction.

## Test Signals
No direct tests in this subset; indirectly covered by reader tests that configure `CacheOpts`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/external_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/filter.go -->
# sources/storage-engines/pebble/sstable/filter.go

## Purpose
Defines table filter metrics and a small reader wrapper that records filter hits and misses.

## Important APIs, Types, and Functions
- `FilterMetrics` exposes hit/miss counters.
- `FilterMetricsTracker` stores atomic hit/miss counters and has `Load`.
- `tableFilterReader` pairs a `base.TableFilterDecoder` with optional metrics.
- `newTableFilterReader` constructs the wrapper.
- `mayContain` invokes the decoder and updates metrics.

## Control Flow
`mayContain` calls `decoder.MayContain(data, key)`. If metrics are configured, a false result increments hits because the filter avoided a data-block access, while a true result increments misses because the filter could not rule out the key.

## State and Persistence Behavior
No on-disk persistence. Metrics live in atomics and can be loaded safely while readers run.

## Dependencies and Integration Points
Used by SSTable readers with table filter blocks, including bloom/binary fuse decoders. `ReaderOptions.FilterMetricsTracker` supplies the metrics sink.

## Risks and Edge Cases
Metric naming is easy to invert: “hit” means a successful negative filter result. Unsupported filter families are handled elsewhere by not constructing a reader.

## Test Signals
Indirectly exercised by filter/reader tests and datadriven iterator tests that use filter policies.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/format.go -->
# sources/storage-engines/pebble/sstable/format.go

## Purpose
Defines SSTable table format versions, their capabilities, footer sizes, parsing, string conversion, and index-iterator selection.

## Important APIs, Types, and Functions
- `TableFormat` enum covers LevelDB, RocksDBv2, Pebble v1-v8, min/max supported formats, and unspecified.
- `footerSizes` maps formats to footer lengths.
- Long format comments document v4 obsolete-bit semantics and strict-obsolete correctness.
- `parseTableFormat`, `BlockColumnar`, `TieringMetadata`, `TieringColumnConfig`, `FooterSize`, `newIndexIter`, `AsTuple`, `String`, and `ParseTableFormatString` expose capabilities and conversions.

## Control Flow
Footer parsing supplies magic bytes and version to `parseTableFormat`, which validates known combinations and returns corruption errors for unsupported versions or bad magic. Feature methods gate columnar blocks at v5, tiering columns at v8, and footer sizes by format. `newIndexIter` selects row or columnar index iterators based on `BlockColumnar`.

## State and Persistence Behavior
The enum values themselves are not serialized. Disk format is represented by magic/version tuples and footer sizes. Format capabilities drive whether writers emit row/columnar blocks, checked footers, columnar metaindex/properties, blob handles, and tiering metadata.

## Dependencies and Integration Points
Used by readers, writers, layout decoding/formatting, options defaults, properties serialization, and value/blob/tiering feature gates. Depends on `base`, `blockiter`, `colblk`, and `rowblk`.

## Risks and Edge Cases
Adding a format requires updating enum order, footer sizes, tuple/string parsing, tests, and feature gates. Strict-obsolete semantics are correctness-sensitive for disaggregated/foreign SSTable reads. Unsupported versions must return corruption errors, not silently downgrade.

## Test Signals
`format_test.go` validates magic/version round trips and error messages for unsupported versions and bad magic.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/format_test.go -->
# sources/storage-engines/pebble/sstable/format_test.go

## Purpose
Tests table format parsing from footer tuple and conversion back to magic/version tuple.

## Important APIs, Types, and Functions
- `TestTableFormat_RoundTrip` enumerates valid LevelDB, RocksDBv2, and Pebble v1-v8 cases.
- Invalid cases cover bad RocksDB version, unsupported Pebble version, and unknown magic.

## Control Flow
Each case calls `parseTableFormat`, wraps errors to match reader footer errors, checks either exact error text or expected format, then checks `AsTuple`.

## State and Persistence Behavior
No persisted files are written; the test models footer magic/version interpretation.

## Dependencies and Integration Points
Uses `leaktest`, `errors.Wrapf`, `base.DiskFileNum`, and `require`. Provides a regression guard for reader footer parsing.

## Risks and Edge Cases
Exact error strings are asserted. New formats require adding valid cases and adjusting unsupported-version expectations.

## Test Signals
Strong targeted coverage for format tuple compatibility and corruption diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/format_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/internal.go -->
# sources/storage-engines/pebble/sstable/internal.go

## Purpose
Re-exports internal key kinds and key/span aliases from public `sstable`, and asserts scratch-buffer sizing for value/blob handles.

## Important APIs, Types, and Functions
- Constants alias `base.InternalKeyKind*` values that are part of the file format.
- `InternalKey` aliases `base.InternalKey`.
- `Span` aliases `keyspan.Span`.
- Compile-time constants assert `blockHandleLikelyMaxLen` can hold value block index handles, value handles plus prefix byte, and blob inline handles plus prefix byte.

## Control Flow
No runtime flow. Compile-time arithmetic asserts buffer-size invariants.

## State and Persistence Behavior
No state is stored. The aliases expose file-format key kinds and key/span types to external SSTable users. Size assertions protect writer scratch buffers used when encoding handles into persisted values/metaindex entries.

## Dependencies and Integration Points
Depends on `base`, `keyspan`, `blob`, and `valblk`. Used by writers, tests, and external callers constructing SSTables.

## Risks and Edge Cases
Changing handle maximum lengths can break compile-time assertions and requires revisiting writer scratch buffer sizing. Key-kind aliases are file-format sensitive and must remain compatible with existing SSTables.

## Test Signals
Assertions are compile-time. Runtime behavior is covered indirectly by writer/value/blob tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/internal/genprops/gen_props.go -->
# sources/storage-engines/pebble/sstable/internal/genprops/gen_props.go

## Purpose
Generates `sstable/properties_gen.go` from `Properties` struct tags, replacing reflection with explicit load/encode/string code.

## Important APIs, Types, and Functions
- `Field` describes a tagged property field: Go name, property tag, kind, encode-empty flag, and intern flag.
- `tmpl` is the generated source template containing `Properties.load`, `encodeAll`, `isLoaded`, `String`, and bit constants.
- `zeroVal` returns literal zero values for template comparisons.
- `main` loads the `sstable` package, finds the `Properties` struct, extracts `prop` and `options` tags, validates supported types and bitfield size, formats generated source, and writes `properties_gen.go`.

## Control Flow
The generator uses `go/packages` to inspect syntax and type info, walks type declarations until it finds `github.com/cockroachdb/pebble/sstable.Properties`, records tagged fields in declaration order, locates the package directory, executes the template, formats it, and writes the output file. If formatting fails, it writes the unformatted buffer for debugging before fatal exit.

## State and Persistence Behavior
The generator writes generated Go source to the `sstable` package. Generated code persists property load-state in a `Loaded` bitfield and encodes properties into maps for row/columnar property blocks.

## Dependencies and Integration Points
Triggered by `//go:generate` in `properties.go`. Depends on `go/ast`, `go/packages`, `reflect.StructTag`, `text/template`, and `go/format`. Generated code is consumed by `Properties` load/save/string paths.

## Risks and Edge Cases
Only bool, uint8, uint32, uint64, and string property fields are supported. More than 64 tagged fields fails due to the `Loaded` bitfield. Template imports must stay gofmt-compatible. Adding tags/options requires generator support.

## Test Signals
No direct test in this subset; correctness is checked indirectly by compiling generated code and by properties read/write tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/internal/genprops/gen_props.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/layout.go -->
# sources/storage-engines/pebble/sstable/layout.go

## Purpose
Describes, decodes, formats, and writes the physical block layout of an SSTable, including data/index/meta/filter/range/value/blob/tiering/footer blocks.

## Important APIs, Types, and Functions
- `Layout` records block handles by role plus table format.
- `NamedBlockHandle` names handles for ordering and display.
- `Layout.orderedBlocks` and `Layout.Describe` produce physical-layout descriptions.
- Formatting helpers handle row/columnar data/index/keyspan blocks, properties, metaindex, value/blob/tiering metadata, and footers.
- `decodeLayout`, `decompressInMemory`, `newIndexIter`, `forEachIndexEntry`, `decodeMetaindex`, and `decodeColumnarMetaIndex` reconstruct layout from bytes.
- `layoutWriter` writes physical blocks, records metaindex entries, clears cache collisions, and finalizes metaindex/footer.
- Writer methods include `WriteDataBlock`, `WritePrecompressedDataBlock`, `WriteIndexBlock`, `WriteFilterBlock`, `WritePropertiesBlock`, `WriteRangeKeyBlock`, `WriteBlobRefIndexBlock`, `WriteTieringHistogramBlock`, `WriteRangeDeletionBlock`, `WriteValueBlock`, `WriteValueIndexBlock`, `Finish`, and `Abort`.

## Control Flow
Layout description sorts all known blocks by offset and optionally reads/decompresses each block for verbose formatting. Layout decoding parses the footer, decodes row or columnar metaindex, reads properties to detect one- vs two-level index, walks index entries to collect data handles, and decodes value block index handles. `layoutWriter` writes blocks sequentially, records named metaindex handles, writes a row or columnar metaindex depending on format, encodes the footer, finishes the writable, and closes compression resources.

## State and Persistence Behavior
This file defines the order and metadata linkage of persisted SSTable blocks. Formats v6+ use columnar metaindex blocks; v7+ may use compressed columnar properties and footer attributes. Named blocks are stored in the metaindex, while the footer stores metaindex and last index handles plus checksum/attributes/version/magic. `layoutWriter.offset` is the authoritative current file offset.

## Dependencies and Integration Points
Central integration point for `Reader`, `RawColumnWriter`, `CopySpan`, compression analyzer, block readers/writers, `footer`, `Attributes`, `valblk`, `blob`, `tieredmeta`, row/columnar block packages, and object storage. The layout description path is used heavily by datadriven tests.

## Risks and Edge Cases
Handle decoding must match row/columnar metaindex format and special value-index handle encoding. Footer checksum/attributes offsets are format-specific. Cache clearing is defensive against cache key collisions. Optional handles with zero length must be skipped by callers. Verbose formatting must not leak buffers and must release block handles.

## Test Signals
Exercised by `colblk_writer_test.go`, copier tests, file analyzer tests, and many reader/writer datadriven suites that compare `Layout.Describe` output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/layout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/options.go -->
# sources/storage-engines/pebble/sstable/options.go

## Purpose
Defines public reader/writer options, defaults, compression profile aliases, key-schema registries, tombstone-density defaults, and table-format compatibility checks.

## Important APIs, Types, and Functions
- Constants: `MaximumRestartOffset`, `DefaultNumDeletionsThreshold`, and `DefaultDeletionSizeRatioThreshold`.
- `ignoredInternalProperties` lists RocksDB internal properties not surfaced as user properties.
- `Comparers`, `Mergers`, `KeySchemas`, and `MakeKeySchemas`.
- `ReaderOptions.ensureDefaults` fills comparer, merger, logger/tracer, and key schemas.
- Compression profile aliases expose block compression settings.
- `WriterOptions` includes block sizing, comparer/compression/filter/index/key schema, table format, obsolete/tiering/blob/value/block-property options, cache/internal settings, and tombstone-density thresholds.
- `UserKeyPrefixBound.IsEmpty`, `JemallocSizeClasses`, `WriterOptions.SetInternal`, `WriterOptions.ensureDefaults`, and `tableFormatSupportsCompressionProfile`.

## Control Flow
Reader defaults are filled before opening tables. Writer defaults fill restart interval, block size, thresholds, comparer, index size, merger, checksum, table format, deletion thresholds, columnar key schema, compression fallback, and filter policy. Compression defaults fall back to Snappy if the selected profile is unsupported by the table format, such as MinLZ before v6.

## State and Persistence Behavior
Options influence persisted SSTable layout and metadata: table format, block sizes, compression, filters, key schema names, obsolete bit behavior, tiering metadata, value-block usage, block property collectors, and deletion-density properties. The options structs themselves are not persisted, but selected values are written into properties and footer/layout.

## Dependencies and Integration Points
Used by `NewReader`, `NewWriter`, `RawColumnWriter`, `layoutWriter`, and test helpers. Depends on `base`, `sstableinternal`, `block`, `colblk`, and `rowblk`.

## Risks and Edge Cases
`MakeKeySchemas` panics on duplicate names. Defaults depend on table format, so changing `TableFormat` after `ensureDefaults` can leave inconsistent key schema/compression choices. External use of `DisableValueBlocks` is specialized and can affect performance/format behavior. Tiering histogram options require matching getter/extractor functions.

## Test Signals
Indirectly covered across reader/writer tests, format tests, columnar writer tests, and option parsing tests outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/properties.go -->
# sources/storage-engines/pebble/sstable/properties.go

## Purpose
Defines the SSTable `Properties` struct, derived property helpers, property serialization to row/columnar blocks, and conversion to footer attributes.

## Important APIs, Types, and Functions
- `Properties` contains RocksDB-compatible and Pebble-specific table properties with `prop` tags used by the generator.
- `NumPointDeletions` and `NumRangeKeys` compute derived counts.
- `accumulateProps` combines generated encodings with user properties and legacy RocksDB compatibility properties for pre-Pebble formats.
- `saveToRowWriter` and `saveToColWriter` serialize properties in sorted key order.
- `toAttributes` maps properties to an `Attributes` bitset for v7+ footers.
- Package variables hold common encoded legacy property values.

## Control Flow
Writers update `Properties` while building an SSTable. On close, `accumulateProps` calls generated `encodeAll`, merges user properties, conditionally adds/removes legacy RocksDB keys, then `saveToRowWriter` or `saveToColWriter` emits sorted key/value pairs depending on table format. `toAttributes` derives quick footer flags from nonzero counts and index type.

## State and Persistence Behavior
Properties are persisted in a metadata block and loaded when an SSTable is opened. Formats before v7 use a row block with large restart interval; v7+ can use columnar/compressed properties. `Loaded` records which fields were present during loading for string output, while `UserProperties` captures unrecognized non-internal keys.

## Dependencies and Integration Points
Generated methods from `properties_gen.go` are required for load/encode/string behavior. Used by `RawColumnWriter`, `Reader`, `Layout`, copier, and tests. Depends on `rowblk`, `colblk`, `maps`, `slices`, `encoding/binary`, and `unsafe` for string-to-byte conversions in columnar property writing.

## Risks and Edge Cases
Adding a property requires a supported tag type and regenerating code. `saveToColWriter` skips zero-length keys because `unsafe.StringData` cannot handle them. Copied SSTables may intentionally overcount properties. Attribute derivation must track new optional blocks and features.

## Test Signals
Covered indirectly by writer layout/properties datadriven tests, copier property tests, and generated-code compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/properties.go -->
