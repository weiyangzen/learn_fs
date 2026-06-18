# Research: subset-b-008544

Columnar SSTable block research for `sources/storage-engines/pebble/sstable/colblk`. Each section is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block.go -->
# sources/storage-engines/pebble/sstable/colblk/block.go

## Purpose
`block.go` defines the common on-disk/in-memory columnar block envelope used by data, index, keyspan, and simple key/value blocks. It documents the block format: a custom header area, a fixed columnar header containing version, column count, row count, one 5-byte header per column, encoded column payloads, and a final padding byte that keeps "one past the column" pointers inside an allocated object.

## Important APIs, Types, And Functions
Key exports are `Version`, `Header`, `HeaderSize`, `DecodeHeader`, `BlockEncoder`, `FinishBlock`, `DecodeColumn`, and `BlockDecoder`. `BlockEncoder.Init` allocates or reuses aligned storage through `crbytes.AllocAligned`, writes the fixed header at the custom-header offset, and tracks the next column-header slot plus the next data page offset. `BlockEncoder.Encode` asks a `ColumnWriter` to finish each physical column and records its `DataType` and page start. `BlockEncoder.Finish` writes the trailing padding byte and asserts that the computed offset consumed the entire allocation. `BlockDecoder` owns a decoded `Header`, raw block bytes, and `customHeaderSize`, and exposes typed accessors for bitmap, raw bytes, prefix bytes, and uint columns.

## Control Flow
Encoding is size-first: callers compute a full block size, initialize a `BlockEncoder`, encode each column writer in order, then finish. Decoding is header-first: `DecodeBlock` or `BlockDecoder.Init` records metadata, and typed column access validates the column index and type before invoking the column's `DecodeFunc`. `DecodeColumn` also checks that the decoded end offset equals the next column's page start, so malformed column decoders or inconsistent offsets panic early.

## State And Persistence Behavior
The persistent representation is little-endian for header fields and column page offsets. `BlockEncoder.Reset` mangles old buffers in invariant builds and drops very large retained buffers above `maxBlockRetainedSize`. The final padding byte is part of the persisted block image. `BlockDecoder.Header` returns custom header bytes, while `pageStart` reads column offsets with unsafe pointer arithmetic into the block buffer.

## Dependencies And Integration Points
The file depends on `ColumnWriter`/`DecodeFunc` from `column.go` and concrete column encodings such as `Bitmap`, `UnsafeUints`, `RawBytes`, and `PrefixBytes`. It integrates with `binfmt` and `treeprinter` through `FormattedString`, `HeaderToBinFormatter`, and `ColumnToBinFormatter`, enabling datadriven golden tests and human binary-format inspection. Higher-level files add custom headers for data and keyspan blocks on top of this same envelope.

## Risks
Risks are concentrated around unsafe access, alignment, and offset accounting. The caller must supply a correctly computed size, aligned buffer, correct custom-header size, and a matching column schema. The format has no defensive bounds checks beyond panics, so production callers generally rely on block-cache metadata initialization converting panics to corruption errors in higher-level code. Adding a new `DataType` requires updating formatter and typed decoder dispatch paths.

## Test Signals
`block_test.go` exercises this file directly with datadriven format output and randomized round trips across bool, uint, raw bytes, and prefix bytes columns. Other block tests indirectly stress `HeaderSize`, `BlockEncoder`, `BlockDecoder`, and typed decoding through data, index, keyspan, and key/value formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/block_test.go

## Purpose
`block_test.go` validates the generic columnar block envelope and provides shared test helpers for randomized blocks. It checks that heterogeneous column schemas can be encoded, decoded, and formatted without losing row data or corrupting header metadata.

## Important APIs, Types, And Functions
The test-local `testColumnSpec` records a column `DataType`, integer range metadata for uint columns, and bundle size for prefix-byte columns. `intRange` defines interesting uint ranges and expected encodings reused by other tests. `TestBlockWriter` is a datadriven test over `testdata/block_writer`; `randBlock`, `buildBlock`, and `testRandomBlock` generate and verify random blocks; `TestBlockWriterRandomized` drives single-column and multi-column randomized coverage.

## Control Flow
The datadriven test accepts `init`, `write`, and `finish` commands. `init` builds a schema and the corresponding column writers, `write` parses rows into the proper builders, and `finish` calls `FinishBlock`, decodes the result, and returns `FormattedString`. The randomized path builds in-memory expected column values, encodes them through concrete builders, decodes with `DecodeBlock`, checks header column count and row count, validates data types, and compares cloned decoded arrays against the expected values.

## State And Persistence Behavior
The tests model persistence by serializing a full block byte slice through `FinishBlock` and immediately treating it as the decoder input. Randomized tests cover value distributions that force distinct uint physical encodings and prefix-byte bundle choices. Prefix-byte input is sorted before encoding because that encoding requires lexicographic order.

## Dependencies And Integration Points
The tests depend on concrete column writers (`BitmapBuilder`, `UintBuilder`, `RawBytesBuilder`, `PrefixBytesBuilder`) and typed block decoder accessors. They use `datadriven` for golden-format output, `crbytes.CommonPrefix` for prefix-byte construction, and `Clone` from `column.go` to materialize decoded arrays.

## Risks
The datadriven `write` command currently sets bool and uint builder rows starting at the per-command row index rather than the aggregate row index, so it is best suited for simple scripted cases. Randomized coverage is seed-based with logged time seeds; failures are reproducible only if the seed is captured. The randomized tests check equality after decode but do not fuzz malformed headers or inconsistent column offsets.

## Test Signals
This file is itself the direct test signal for the block envelope. It exercises type dispatch, row/header metadata, `FinishBlock`, `DecodeBlock`, formatted output, and randomized combinations of up to nine columns.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/colblk_64bit_test.go -->
# sources/storage-engines/pebble/sstable/colblk/colblk_64bit_test.go

## Purpose
`colblk_64bit_test.go` is a compile-time guard for 64-bit platforms. It verifies that `block.MetadataSize` is not larger than required for the columnar data-block decoder and key-seeker metadata payload.

## Important APIs, Types, And Functions
The file contains a single build-tagged constant assertion:
`const _ uint = uint(unsafe.Sizeof(blockDecoderAndKeySeekerMetadata{})) - block.MetadataSize`. This fails compilation if `block.MetadataSize` grows beyond the exact size of `blockDecoderAndKeySeekerMetadata` on `arm64` or `amd64`.

## Control Flow
There is no runtime control flow. The Go type checker evaluates the constant expression during compilation. If the subtraction underflows, compilation fails.

## State And Persistence Behavior
This file does not persist data, but it protects in-memory block-cache layout. `blockDecoderAndKeySeekerMetadata` is stored inside `block.Metadata`, so unnecessary metadata growth can increase every cached block allocation.

## Dependencies And Integration Points
The assertion couples `data_block.go`'s metadata struct with `sstable/block.MetadataSize`. It is intentionally architecture-specific because pointer and alignment sizes differ across platforms.

## Risks
The guard is strict: legitimate future growth of `block.MetadataSize` for unrelated consumers would require updating or rethinking this assertion. It only covers `arm64` and `amd64`, not all supported architectures.

## Test Signals
The signal is compilation success. It complements the more general compile-time assertions in `data_block.go` that the metadata struct fits and is aligned.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/colblk_64bit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/column.go -->
# sources/storage-engines/pebble/sstable/colblk/column.go

## Purpose
`column.go` defines the shared type system and interfaces for column encoders/decoders in the columnar block format. It is the small contract layer that lets `block.go` and higher-level block writers compose concrete encodings uniformly.

## Important APIs, Types, And Functions
`DataType` enumerates logical column kinds: invalid, bool, uint, raw bytes, and prefix-compressed bytes. `ColumnWriter` extends `Encoder` with `NumColumns`, `DataType`, and `Finish`, allowing one logical writer to emit one or more physical columns. `Encoder` defines `Reset`, `Size`, and `WriteDebug`. `DecodeFunc[T]` is the typed decoder function signature used by `DecodeColumn`. `Array[V]` is a minimal indexed-access interface, and `Clone` materializes the first `n` values of any `Array`.

## Control Flow
There is no complex control flow. The key contract is size-before-finish: block writers call `Size(rows, offset)` to calculate offsets, then call `Finish(col, rows, offset, buf)` in column order. The `rows` parameter may be the current row count or one less, supporting block writers that decide to split just before the last appended row.

## State And Persistence Behavior
`DataType` values are persisted as one byte per column header in the columnar block envelope. The string names support diagnostics and tests but are not the persisted representation. The interfaces themselves do not own persistent state; implementors such as `UintBuilder`, `RawBytesBuilder`, and `PrefixBytesBuilder` do.

## Dependencies And Integration Points
`block.go` depends directly on these interfaces. `data_block.go`, `index_block.go`, `keyspan.go`, and `key_value_block.go` all implement or consume `ColumnWriter`. Tests use `Clone` to compare decoded arrays against generated expected data.

## Risks
`DataType.String` indexes directly into `dataTypeName`, so invalid out-of-range values can panic rather than return a safe placeholder. Any addition to `DataType` must update `dataTypesCount`, `dataTypeName`, block formatting dispatch, randomized tests, and concrete decoder access paths.

## Test Signals
There is no standalone test file for `column.go`; coverage comes from all block round-trip tests. `block_test.go` especially verifies `DataType` names, `ColumnWriter` composition, and `Clone` through randomized schemas.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/column.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block.go

## Purpose
`data_block.go` implements Pebble's columnar point-key data block format, default user-key schema, metadata initialization, validation, suffix rewriting, and hot-path iteration. It decomposes internal keys into schema-specific key columns plus trailers, prefix-change bitmap, values, external-value flags, obsolete flags, and optional tiering metadata.

## Important APIs, Types, And Functions
`KeySchema`, `KeyWriter`, `KeySeeker`, and `KeySeekerMetadata` define the customization points for database-specific user-key decomposition and search. `DefaultKeySchema` splits keys into prefix `PrefixBytes` and suffix `RawBytes`. `DataBlockEncoder` exposes `Init`, `Reset`, `Add`, `AddWithSecondaryBlobHandle`, `Rows`, `Size`, `MaterializeLastUserKey`, and `Finish`. `OptionalColumnConfig`, `NoTieringColumns`, and `WithTieringColumns` govern tiering columns. `DataBlockRewriter.RewriteSuffixes` rewrites block suffixes. `InitDataBlockMetadata`, `InitIndexBlockMetadata`, and `InitKeyspanBlockMetadata` initialize block-cache metadata. `DataBlockDecoder`, `DataBlockValidator`, and `DataBlockIter` provide read, validation, and iteration surfaces.

## Control Flow
Writing starts with `DataBlockEncoder.Init`, which creates a schema key writer and column builders. Each `Add` writes key columns, trailer, prefix-same bit, value payload, external-value bit, obsolete bit, and optional tiering fields. `Finish` inverts `prefixSame` into a persisted `prefixChanged` bitmap, writes schema and max-key-length custom headers, encodes all columns, and returns the last internal key. Reading initializes `DataBlockDecoder` from an aligned block and then builds a `KeySeeker` either per iterator or once in `block.Metadata`. Iteration routes `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `NextPrefix`, and `NextWithSamePrefix` through row indexes, lazily materializing keys and values only when needed.

## State And Persistence Behavior
Persistent state includes the schema custom header, a four-byte maximum user-key length, the generic column header, and all column payloads. Values that are external are stored with a leading `block.ValuePrefix`; in-place values elide that prefix. Tiering span IDs, attributes, and secondary blob handles are present only when both tiering columns are configured. `DataBlockIter` owns transient row state, reusable key buffers, block handles, transform configuration, cached prefix-range bounds, lazy tiering column decoders, and obsolete-row cursors. `InitHandle` relies on metadata previously initialized inside the block cache and releases the previous handle before adopting a new one.

## Dependencies And Integration Points
This file integrates deeply with `internal/base`, `sstable/block`, `sstable/blockiter`, `PrefixBytes`, `RawBytes`, `Bitmap`, and `UnsafeUints`. It provides the `blockiter.Data` implementation used by SSTable iterators. `DataBlockRewriter` is used by suffix rewriting paths and expects no value-block lookups. Metadata initialization converts panics to `base.CorruptionErrorf`, giving higher layers a corruption boundary around unsafe decoding.

## Risks
The code is performance-sensitive and uses unsafe casts, manual metadata packing, manual key-buffer sizing, and copied inline decode logic. Bugs can arise if `decodeKey` and inlined copies diverge, if optional column configuration mismatches the actual block format, if a caller supplies unaligned data, or if external-value handlers are nil when external values are present. `RewriteSuffixes` explicitly drops secondary blob handles and performs row-by-row rewriting. `Finish(rows, size)` supports only `Rows()` or `Rows()-1`, and the caller must provide the exact size for the chosen row count.

## Test Signals
`data_block_test.go` provides datadriven format/iterator/rewrite coverage, validation checks, writer benchmarks, decoder-init benchmarks, and randomized semantic tests for `SeekPrefixGE` plus `NextWithSamePrefix` with transforms and obsolete hiding. `data_block_meta_test.go` verifies `*WithMeta` tiering metadata paths. `data_block_iter_bench_test.go` measures common iterator operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_iter_bench_test.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block_iter_bench_test.go

## Purpose
`data_block_iter_bench_test.go` benchmarks hot `DataBlockIter` operations on a realistic columnar data block containing many versions per prefix. It is performance instrumentation rather than correctness coverage.

## Important APIs, Types, And Functions
The file defines `BenchmarkDataBlockIter`. It builds a roughly 32 KiB block using `DataBlockEncoder`, `DefaultKeySchema`, and `NoTieringColumns`, then benchmarks `SeekGE`, `SeekPrefixGE`, `SeekGE` with `TrySeekUsingNext`, `Next`, and `Prev`.

## Control Flow
The setup writes numeric prefixes with ten MVCC-style suffix versions each, in reverse timestamp order to satisfy the comparer ordering. It finishes the block, initializes `DataBlockDecoder`, constructs one `DataBlockIter`, and reuses it across benchmark subtests. Random-seek benchmarks use a deterministic shuffled prefix slice. The `TrySeekUsingNext` benchmark walks prefixes monotonically and uses a plain `SeekGE` only when wrapping to the beginning.

## State And Persistence Behavior
The benchmark creates one persisted block byte slice in memory and then repeatedly exercises iterator state over that decoded block. It does not touch disk. The benchmark's useful state is the row distribution: repeated prefixes with multiple suffixes exercise prefix-change bitmap and suffix-seek logic.

## Dependencies And Integration Points
The benchmark depends on `testkeys.Comparer`, `block.InPlaceValuePrefix`, `blockiter.Transforms`, and the shared `testKeysSchema` from `data_block_test.go`. It gives performance feedback for the same methods used by higher-level SSTable iterators.

## Risks
Because one iterator is reused inside each sub-benchmark, measurements reflect realistic stateful iteration but may hide costs of repeated initialization. It uses no transforms, obsolete hiding, external values, or tiering metadata, so it does not measure those cold paths.

## Test Signals
The benchmark can detect regressions in seek and step performance. It is not a pass/fail correctness test beyond requiring setup and iterator operations not to panic.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_iter_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_meta_test.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block_meta_test.go

## Purpose
`data_block_meta_test.go` verifies that columnar data-block iterators correctly return per-KV tiering metadata through the meta iterator methods. It focuses on optional tiering columns introduced through `OptionalColumnConfig`.

## Important APIs, Types, And Functions
The key test is `TestDataBlockIterWithMeta`. It uses `WithTieringColumns`, `DataBlockEncoder.Add`, `DataBlockIter.FirstWithMeta`, `NextWithMeta`, and `SeekGEWithMeta`.

## Control Flow
The test builds a default-schema data block with three keys and explicit `base.KVMeta` values, including a zero-valued metadata row. It finishes and decodes the block, initializes a `DataBlockIter` with tiering enabled, walks all rows through `FirstWithMeta` and `NextWithMeta`, checks exhaustion returns nil plus empty metadata, and tests `SeekGEWithMeta` for both present and absent targets.

## State And Persistence Behavior
The test exercises persisted tiering span ID and tiering attribute columns. It also covers lazy metadata decoding in `DataBlockIter`: tiering columns are decoded only when `decodeMeta` is needed, not during ordinary key/value iteration.

## Dependencies And Integration Points
It integrates `DefaultKeySchema`, `testkeys.Comparer`, `block.InPlaceValuePrefix`, `blockiter.Transforms`, and `testify/require`. The tested API is part of `base.MetaIterator` behavior used by consumers that need tiering metadata during iteration.

## Risks
Coverage is intentionally narrow: it does not test `InitHandle`, secondary blob handle persistence, transforms combined with metadata, or mismatched optional column configs. A nil lazy value handler is safe here because all values are in-place.

## Test Signals
The test directly guards the `DataBlockIter` `FirstWithMeta`, `NextWithMeta`, and `SeekGEWithMeta` paths and validates empty metadata on iterator exhaustion or missing seek results.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_meta_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block_test.go

## Purpose
`data_block_test.go` is the primary correctness and behavior test suite for columnar data blocks. It covers datadriven binary-format output, writer sizing, iteration commands, suffix rewriting, validation, random `SeekPrefixGE`/`NextWithSamePrefix` semantics, and benchmark setup helpers.

## Important APIs, Types, And Functions
`testKeysSchema` defines the default schema used by most tests. `dataBlockIterInternalIterator` adapts `DataBlockIter` to `itertest.RunInternalIterCmd`. `TestDataBlock` runs datadriven commands over `testdata/data_block`. Helper functions `makeTestKeyRandomKVs`, `randTestKey`, and `getInternalValuer` support benchmarks and randomized tests. `TestDataBlockIterSeekPrefixGENextWithSamePrefix` independently verifies prefix-seek and same-prefix iteration semantics. `BenchmarkDataBlockWriter` and `BenchmarkDataBlockDecoderInit` measure writer and metadata initialization costs.

## Control Flow
The datadriven test supports `init`, `write`, `write-block`, `rewrite`, `finish`, and `iter`. Writes parse internal keys and values, compute key comparisons with the encoder key writer, set value prefixes for in-place, value-handle, or blob-handle strings, mark shadowed duplicate point keys obsolete, and track sizes after each row. `finish` can serialize all rows or `rows=n`, decodes and formats the block, and runs `DataBlockValidator`. `iter` initializes `DataBlockIter` with optional synthetic seqnum/prefix/suffix and obsolete hiding, then delegates commands to `itertest`.

## State And Persistence Behavior
The tests persist blocks to byte slices and repeatedly decode them through `DataBlockDecoder`. They exercise `Finish(rows, sizes[rows-1])`, including omitting the last row, and confirm the returned last key. Rewriting replaces suffixes and updates decoder state to the rewritten block. The randomized prefix test builds a block with random obsolete bits and then compares visible iterator behavior against a linear-scan model under random transforms.

## Dependencies And Integration Points
The file connects `colblk` to `internal/base`, `internal/testkeys`, `itertest`, `binfmt`, `treeprinter`, `sstable/block`, and `sstable/blockiter`. It is the closest test proxy for how upper-level SSTable iterators consume `DataBlockIter`.

## Risks
The randomized test uses time seeds, so logs are required for exact reproduction. The datadriven lazy-value handler always returns a mock in-place value for external handles, so it verifies routing more than storage lookup. Tiering metadata has separate coverage in `data_block_meta_test.go`.

## Test Signals
Strong signals include golden binary layout, validator failures surfaced in output, iterator command transcripts, suffix rewrite output, randomized prefix-seek equivalence, and benchmarks for writer and metadata initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian.go -->
# sources/storage-engines/pebble/sstable/colblk/endian.go

## Purpose
`endian.go` provides endian-conversion helpers that reverse bytes in slices of 16-, 32-, and 64-bit unsigned integers. These helpers support reading or preparing unsafe integer arrays on big-endian platforms while keeping the persisted format little-endian.

## Important APIs, Types, And Functions
Exports are `ReverseBytes16`, `ReverseBytes32`, and `ReverseBytes64`. Each loops over the slice in groups of four elements using unsafe conversion to a slice of `[4]T` to help the compiler eliminate bounds checks, then handles the tail one element at a time with `math/bits.ReverseBytes*`.

## Control Flow
Each function checks `len(s) >= 4`, processes full quads, then computes `tail := s[len(s)&^3:]` and reverses the remaining elements. The operation mutates the slice in place.

## State And Persistence Behavior
The functions do not own state. They transform in-memory typed views of integer data. Because columnar uint encodings are persisted in little-endian form, these helpers are part of preserving platform-independent decoding.

## Dependencies And Integration Points
The file depends on `math/bits` and `unsafe`. The architecture-specific files `endian_big.go` and `endian_little.go` define how unsafe integer accessors use byte reversal or direct loads.

## Risks
Unsafe slice conversion assumes the input slice is suitably aligned for its element type, which is true for typed Go slices but important if callers derive slices from raw bytes. The functions are low-level and mutate inputs, so accidental reuse of pre-reversal data would be incorrect.

## Test Signals
`endian_test.go` randomly generates values, stores them as little-endian typed words, applies these functions, and verifies that the bytes now decode as big endian with the original values.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_big.go -->
# sources/storage-engines/pebble/sstable/colblk/endian_big.go

## Purpose
`endian_big.go` defines big-endian implementations of unsafe uint and offset accessors. Its goal is to keep columnar block integer decoding semantically little-endian even on big-endian CPUs.

## Important APIs, Types, And Functions
The file is guarded by big-endian build tags. It exports `const BigEndian = true` and implements `unsafeUint64Decoder.At`, `UnsafeUints.At`, `UnsafeOffsets.At`, and `UnsafeOffsets.At2`. Multi-byte values are loaded through unsafe pointer arithmetic and passed through `bits.ReverseBytes16/32/64` as needed.

## Control Flow
`UnsafeUints.At` is optimized by encoded width. Width 8 loads and reverses a raw `uint64` with no base. Width 0 returns the base. Widths 4 and 2 reverse a loaded word and add the base. Width 1 reads a byte and adds the base. `UnsafeOffsets.At` and `At2` perform similar dispatch for 0-, 1-, 2-, and 4-byte offsets, with `At2` loading adjacent offsets together when possible.

## State And Persistence Behavior
The persistent representation remains little-endian and width-coded. This file only changes in-memory interpretation on big-endian targets. It relies on block buffers being aligned according to the column encoders' alignment rules.

## Dependencies And Integration Points
It integrates with `UnsafeUints`, `UnsafeOffsets`, and `unsafeUint64Decoder` defined in the uint encoding files outside this work item. It is selected instead of `endian_little.go` by Go build constraints.

## Risks
The code is performance-sensitive and unsafe. `At2` has subtle byte-order handling, especially for 1-byte offsets where no `ReverseBytes16` is required because the function returns the values in logical order. Mistakes would silently corrupt offsets, which would affect raw bytes, prefix bytes, and many higher-level block decoders.

## Test Signals
Direct accessor tests likely live in `uints_test.go` and `unsafe_uints_test.go`, outside this subset. `endian_test.go` covers the shared reversal helpers, not this build-tagged file on little-endian CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_big.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_little.go -->
# sources/storage-engines/pebble/sstable/colblk/endian_little.go

## Purpose
`endian_little.go` defines little-endian implementations of unsafe uint and offset accessors. Because the columnar format stores integers little-endian, little-endian platforms can decode with direct unsafe loads.

## Important APIs, Types, And Functions
The file is selected by little-endian build tags and exports `const BigEndian = false`. It implements `unsafeUint64Decoder.At`, `UnsafeUints.At`, `UnsafeOffsets.At`, and `UnsafeOffsets.At2`.

## Control Flow
`UnsafeUints.At` dispatches on encoded width: 8-byte values are direct `uint64` loads with no base, width 0 returns the column base, widths 4 and 2 load smaller words and add the base, and width 1 reads a byte. `UnsafeOffsets.At` returns direct offset loads. `UnsafeOffsets.At2` loads two adjacent offsets together for width 2 and width 4, then splits the combined word into low and high logical offsets.

## State And Persistence Behavior
The file interprets persisted little-endian integer columns directly in memory. It assumes the block buffer and column payloads are aligned as required by the block and column encoders.

## Dependencies And Integration Points
It is the common implementation on mainstream `amd64`, `arm64`, and other little-endian platforms. Raw bytes, prefix bytes, index block handles, key trailers, and metadata columns all depend on these accessors indirectly through `UnsafeUints` and `UnsafeOffsets`.

## Risks
Unsafe pointer arithmetic and direct typed loads make bounds, alignment, and width correctness essential. The code is duplicated structurally with `endian_big.go`; behavior changes must preserve both variants.

## Test Signals
Most regular CI on little-endian platforms exercises this file indirectly through every columnar block test, plus uint/unsafe-uint tests outside the listed subset. `endian_test.go` covers only byte-reversal helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_little.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_test.go -->
# sources/storage-engines/pebble/sstable/colblk/endian_test.go

## Purpose
`endian_test.go` validates the shared byte-reversal helpers in `endian.go`. It ensures that slices encoded as little-endian typed words can be transformed so that their backing bytes decode as big endian to the same logical values.

## Important APIs, Types, And Functions
The tests are `TestReverseBytes16`, `TestReverseBytes32`, and `TestReverseBytes64`. Each uses `encoding/binary`, random values from `math/rand/v2`, `slices.Clone`, and unsafe byte views of typed slice elements.

## Control Flow
For 100 iterations per width, a random length below 100 is chosen, random logical values are generated, values are written into a typed slice using little-endian byte order, the slice is cloned and reversed in place, and each reversed element's bytes are decoded as big endian and compared to the original logical value.

## State And Persistence Behavior
The tests model the persisted little-endian integer representation and the in-memory transformation required for big-endian interpretation. No disk state is touched.

## Dependencies And Integration Points
The tests exercise only `ReverseBytes16/32/64`, not the build-tagged `UnsafeUints` accessors directly. They support the endian abstraction used by uint and offset column decoders.

## Risks
Random lengths below 100 cover tails of 0 through 3 elements as well as quad loops, but the tests are not exhaustive over all values. They run on little-endian machines too because they construct byte layouts explicitly using `encoding/binary`.

## Test Signals
Failures indicate incorrect byte reversal, tail handling, or unsafe typed-byte slicing. Passing tests give confidence that the big-endian helper functions preserve logical integer values.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block.go -->
# sources/storage-engines/pebble/sstable/colblk/index_block.go

## Purpose
`index_block.go` implements columnar SSTable index blocks. These blocks map separator keys to data-block handles and optional block properties, and the same writer supports first-level and second-level index blocks.

## Important APIs, Types, And Functions
`IndexBlockWriter` owns `RawBytesBuilder` separators, uint offset/length builders, raw block-property bytes, row count, and a `BlockEncoder`. It exposes `Init`, `Reset`, `Rows`, `AddBlockHandle`, `UnsafeSeparator`, `Size`, and `Finish`. `IndexBlockDecoder` decodes separators, offsets, lengths, block properties, and the embedded `BlockDecoder`. `IndexIter` implements `blockiter.Index` with initialization from a decoder, raw bytes, or a block-cache handle; navigation methods; separator comparison helpers; `BlockHandleWithProperties`; invalidation; close; and tree-step diagnostics.

## Control Flow
Writing appends one row per index entry and serializes four columns in fixed order: separator, offset, length, properties. `Finish(rows)` supports all rows or all but the last row and uses the common block envelope. Decoding initializes typed column accessors. `IndexIter.SeekGE` performs binary search over separators, applying synthetic prefix/suffix transforms if configured. Navigation methods update the row index and return validity. `BlockHandleWithProperties` reads the current row's offset, length, and props into a `block.HandleWithProperties`.

## State And Persistence Behavior
Persistent state is a four-column columnar block with no custom header. Offsets and lengths are uint columns, separators and properties are raw bytes columns. `IndexIter` may own a `block.BufferHandle`; `Init`, `InitHandle`, and `Close` release any previous handle before replacing or clearing it. Synthetic transforms are transient and materialized into `keyBuf` for comparisons and returned separators.

## Dependencies And Integration Points
The file integrates with `sstable/block` handles and cache handles, `blockiter.Index`, `base.Comparer`, and block-cache metadata initialized by `InitIndexBlockMetadata` in `data_block.go`. Higher-level table iterators use this iterator to locate data blocks.

## Risks
Separators can be equal in snapshot scenarios, so binary search and comparison semantics must use greater-or-equal carefully. Transform handling currently materializes keys during binary search, which is correct but potentially expensive. `BlockHandleWithProperties` panics in invariant builds if called on an invalid row. Decoder initialization assumes well-formed aligned block data.

## Test Signals
`index_block_test.go` provides datadriven build/format/iterator coverage, synthetic transform checks through iterator commands, and a concurrent `InitHandle` cache test that validates block metadata use, handle release, iteration, and invalidation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/index_block_test.go

## Purpose
`index_block_test.go` validates columnar index-block encoding, decoding, formatted output, iterator positioning, synthetic transforms, and cache-handle initialization.

## Important APIs, Types, And Functions
`TestIndexBlock` is datadriven over `testdata/index_block`, using `IndexBlockWriter`, `IndexBlockDecoder`, and `IndexIter`. `TestIndexIterInitHandle` constructs a cache-backed block, stores initialized `IndexBlockDecoder` metadata, and repeatedly initializes iterators through `InitHandle` concurrently.

## Control Flow
The datadriven `build` command parses rows of separator, offset, length, and optional props, finishes a block with optional row truncation, prints `UnsafeSeparator(rows-1)`, initializes the decoder, and prints `DebugString`. The `iter` command initializes `IndexIter` with optional synthetic prefix/suffix transforms and executes commands including seek, first, last, next, prev, validity check, and invalidation.

## State And Persistence Behavior
Tests persist an index block in memory, decode it, and in the cache test copy it into a `block.Alloc` buffer with metadata initialized in place. The cache test creates a Pebble cache handle, stores the block, obtains `CacheBufferHandle`s, and verifies `Close` releases handles under concurrent reuse.

## Dependencies And Integration Points
The tests use `datadriven`, `crstrings`, `testkeys.Comparer`, `internal/cache`, `sstable/block`, and `sstable/blockiter`. The concurrent handle test mirrors higher-level block-cache usage.

## Risks
Datadriven expectations must be updated with any binary layout change. The concurrent test checks repeated read-only iterator initialization, but does not race writes because block metadata is immutable after initialization.

## Test Signals
Signals include golden debug strings, iterator transcript output, correct block handles and props, `IsDataInvalidated` transitions, and lack of data races or handle misuse across eight concurrent workers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/index_block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block.go -->
# sources/storage-engines/pebble/sstable/colblk/key_value_block.go

## Purpose
`key_value_block.go` implements a simple two-column key/value block used as a drop-in columnar replacement for SSTable metaindex and properties blocks.

## Important APIs, Types, And Functions
`KeyValueBlockWriter` owns raw-byte key and value builders, row count, and a `BlockEncoder`. It exposes `Init`, `Rows`, `AddKV`, `Finish`, and an internal `size`. `KeyValueBlockDecoder` owns raw-byte key/value arrays plus a `BlockDecoder`, and exposes `Init`, `DebugString`, `Describe`, `BlockDecoder`, `KeyAt`, `ValueAt`, and `All`.

## Control Flow
Writing initializes raw-byte builders, appends key/value pairs row by row, computes a two-column block size plus trailing padding, and encodes keys then values. Decoding initializes the generic block decoder and typed raw-byte columns. `All` returns an `iter.Seq2` that yields each key/value pair until exhausted or the callback stops.

## State And Persistence Behavior
Persistent state is a two-column columnar block with no custom header. Keys and values are copied into `RawBytesBuilder` storage and serialized as raw byte slices. The decoder returns slices backed by the block data, so callers must respect block lifetime and immutability.

## Dependencies And Integration Points
This block format shares the common block envelope and `RawBytes` column encoding. Tests encode block handles for metaindex values and arbitrary properties values. The `iter` package integration provides a convenient range-over API for consumers that want sequential key/value access.

## Risks
There is no explicit `Reset` method, so writer reuse currently requires `Init` and relies on builder initialization behavior. `Finish(rows)` does not enforce `rows == Rows()` or `Rows()-1` in this file, so callers must pass a sensible row count. Decoded key/value slices alias block memory.

## Test Signals
`key_value_block_test.go` builds metaindex and properties blocks from datadriven inputs and verifies debug-format output after decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/key_value_block_test.go

## Purpose
`key_value_block_test.go` validates the simple key/value block format for metaindex and properties use cases through datadriven golden output.

## Important APIs, Types, And Functions
`TestMetaIndexBlock` builds a `KeyValueBlockWriter` where values are varint-encoded `block.Handle`s. `TestPropertiesBlock` builds a writer from literal key/value fields. Both initialize `KeyValueBlockDecoder` and print `DebugString`.

## Control Flow
Each datadriven test supports a `build` command. The metaindex test parses key, offset, and length, encodes the handle into a local fixed array, and adds the encoded bytes as the value. The properties test parses a key and value and adds them directly. Both finish all rows, initialize a decoder, and return the formatted block.

## State And Persistence Behavior
The tests persist the columnar block into an in-memory byte slice. Metaindex values exercise compact block-handle serialization as raw bytes; properties values exercise arbitrary raw value slices.

## Dependencies And Integration Points
The tests use `datadriven`, `crstrings`, `sstable/block.Handle`, and `testify/require`. They model the metaindex/properties block consumers that expect sorted key/value records.

## Risks
The tests validate layout and formatting, not the `All` iterator method. Inputs are simple whitespace-delimited fields, so values containing spaces are not covered.

## Test Signals
Golden debug strings guard the two-column layout, raw-byte offsets, and compatibility with encoded block-handle payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan.go -->
# sources/storage-engines/pebble/sstable/colblk/keyspan.go

## Purpose
`keyspan.go` implements columnar blocks and iterators for fragmented range deletions and range keys. The format stores unique span boundary user keys separately from per-`keyspan.Key` trailer/suffix/value columns, reducing repeated boundary storage across fragmented spans.

## Important APIs, Types, And Functions
`KeyspanBlockWriter` exposes `Init`, `Reset`, `AddSpan`, `KeyCount`, `UnsafeBoundaryKeys`, `UnsafeLastSpan`, `Size`, `Finish`, and `String`. `KeyspanDecoder` exposes `Init`, `DebugString`, `Describe`, and boundary search. `NewKeyspanIter` creates pooled iterators from a block-cache handle. `KeyspanIter` wraps `keyspanIter` with handle ownership and pooling; `keyspanIter` implements `keyspan.FragmentIterator` methods `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `Close`, `SetContext`, `WrapChildren`, and `TreeStepsNode`.

## Control Flow
`AddSpan` writes start/end boundaries, avoiding duplicate storage when an abutting span starts at the previous end key, and appends each contained `keyspan.Key` to trailer/suffix/value columns. `Finish` writes a four-byte custom header containing boundary-key count, then encodes boundary columns with boundary-key row count and key columns with key count. Decoding must call `DecodeColumn` manually for boundary columns because their row count differs from the block header's key count. Iteration binary-searches boundaries for seeks, then gathers the next non-empty span forward or backward and materializes keys from index ranges between adjacent boundary entries.

## State And Persistence Behavior
Persistent state consists of boundary user keys, boundary key-indexes, trailers, suffixes, values, and a custom boundary-count header. Iterator state tracks the current boundary index, reusable `keyspan.Span`, inline two-key buffer, optional synthetic prefix buffers, transforms, and cache handle. `KeyspanIter.Close` releases the handle and usually returns the iterator to a pool, with invariant-mode finalizers checking missed releases.

## Dependencies And Integration Points
The file integrates with `internal/keyspan`, `internal/base`, `sstable/block`, `sstable/blockiter.FragmentTransforms`, `treesteps`, and block-cache metadata initialized through `InitKeyspanBlockMetadata`. It serves range-deletion and range-key block iteration in SSTable readers.

## Risks
Correctness depends on input spans already being fragmented and sorted. Empty spans are tolerated only singly between non-empty spans; consecutive or terminal empty spans panic as corruption. Synthetic suffix support is limited to range-key set/delete semantics. Unsafe metadata casting and pooled iterator lifetime require disciplined `Close` calls.

## Test Signals
`keyspan_test.go` provides datadriven encode/decode/iterator coverage, synthetic transform coverage, pooled cache-handle iterator tests under concurrency, and benchmarks for range-deletion seek and next operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan_test.go -->
# sources/storage-engines/pebble/sstable/colblk/keyspan_test.go

## Purpose
`keyspan_test.go` validates columnar keyspan block encoding, decoding, iteration, iterator pooling, cache-handle behavior, and range-deletion performance.

## Important APIs, Types, And Functions
`TestKeyspanBlock` is datadriven over `testdata/keyspan_block`. `TestKeyspanBlockPooling` exercises `NewKeyspanIter`, `KeyspanIter.Close`, and cache-backed metadata. `BenchmarkKeyspanBlock_RangeDeletions` and `benchmarkKeyspanBlockRangeDeletions` measure seek and next performance across span/key counts and key sizes.

## Control Flow
Datadriven commands include `init`, `reset`, `add`, `finish`, and `iter`. `add` parses span lines, `finish` reports unsafe boundary keys and debug formatting, and `iter` initializes a non-pooled `keyspanIter` with optional synthetic seqnum/prefix/suffix transforms before running `keyspan.RunFragmentIteratorCmd`. The pooling test builds a two-span block, stores initialized decoder metadata in a cache value, and concurrently obtains handles, iterates first/next/exhaustion, and closes.

## State And Persistence Behavior
Tests persist blocks in memory and, for pooling, inside Pebble's cache allocation with block metadata initialized in place. They verify that iterator pooling does not retain live handles after close and that cached decoder metadata can be shared across concurrent read-only iterators.

## Dependencies And Integration Points
The file uses `internal/keyspan`, `internal/cache`, `testkeys.Comparer`, `sstable/block`, `sstable/blockiter`, `datadriven`, and `testify/require`. The benchmark reflects range-deletion workloads.

## Risks
Datadriven coverage depends on fragmented, sorted span inputs. The pooling test checks concurrency and handle release, but not transform behavior through `NewKeyspanIter` specifically. Benchmarks use generated numeric string keys and may not capture all production key distributions.

## Test Signals
Signals include golden block debug output, fragment-iterator command transcripts, boundary key reporting, successful concurrent pooled iteration, and benchmark metrics including average bytes per row.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/keyspan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes.go -->
# sources/storage-engines/pebble/sstable/colblk/prefix_bytes.go

## Purpose
`prefix_bytes.go` implements the `PrefixBytes` column encoding for lexicographically sorted byte slices. It compresses one block-wide shared prefix, one prefix per fixed-size bundle, and per-row suffixes, with duplicate keys represented as empty row slices.

## Important APIs, Types, And Functions
`PrefixBytes` implements `Array[[]byte]` and exposes `DecodePrefixBytes`, `At`, `UnsafeFirstSlice`, `SharedPrefix`, `RowBundlePrefix`, `BundlePrefix`, `RowSuffix`, `Rows`, `BundleCount`, and `Search`. `PrefixBytesIter` provides reusable buffer materialization through `Init`, `SetAt`, and `SetNext`. `PrefixBytesBuilder` implements `ColumnWriter` with `Init`, `Reset`, `Rows`, `Put`, `UnsafeGet`, `Finish`, `Size`, and `WriteDebug`. Helpers include `prefixBytesSizing`, `writePrefixCompressed`, and `bundleCalc`.

## Control Flow
Builders ingest sorted keys through `Put(key, bytesSharedWithPrev)`. The first key initializes placeholder offsets and sizing metadata. Starting a new bundle finalizes the previous bundle prefix offset and compressed size, potentially shrinks the block prefix, and starts new placeholders. Within a bundle, duplicate keys append an unchanged offset, while distinct keys update current bundle prefix length and compressed sizing. `Finish` writes the bundle shift byte, a uint-encoded offset table, and compressed string data through width-specialized `writePrefixCompressed`. Decoding reads the bundle shift, computes total logical slices, decodes a modified `RawBytes`, and records shared-prefix length.

## State And Persistence Behavior
Persistent state starts with one byte storing `log2(bundleSize)`, followed by a modified raw-bytes encoding of `1 + bundleCount + rows` slices. Offset zero stores the length of the block-wide prefix instead of an implicit zero. Builder state keeps raw uncompressed concatenated keys, offset placeholders, two rolling `prefixBytesSizing` records for `n` and `n-1` finishing, completed bundle length, bundle geometry, and max shared-prefix length. Decoded accessors return slices into block memory; `At` allocates by concatenating prefix components.

## Dependencies And Integration Points
The encoding is used by `DefaultKeySchema` for user-key prefixes and by generic block tests. It depends on `RawBytes`, uint encoders, unsafe allocation/copy helpers, `crbytes.CommonPrefix`, `binfmt`, `treeprinter`, and `blockiter.SyntheticPrefix` for iterator buffers.

## Risks
The format assumes non-empty sorted keys and power-of-two bundle sizes. Search is subtle around duplicate empty row slices, bundle-boundary comparisons, and block-prefix mismatches. `PrefixBytesIter` relies on callers allocating enough capacity based on maximum key length plus synthetic transforms. `UnsafeGet` only supports the last two keys and panics otherwise. Size/finish support for `Rows()` or `Rows()-1` depends on rolling sizing state staying correct.

## Test Signals
`prefix_bytes_test.go` provides datadriven format/search/get coverage, randomized reconstruction and search checks across many sizes and alphabets, `UnsafeGet` checks, and build/iteration benchmarks. Generic block tests also exercise prefix bytes as a column type.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes_test.go -->
# sources/storage-engines/pebble/sstable/colblk/prefix_bytes_test.go

## Purpose
`prefix_bytes_test.go` validates the prefix-compressed byte-slice column encoding. It checks binary layout, reconstruction, search behavior, row truncation, builder reset, `UnsafeGet`, and performance.

## Important APIs, Types, And Functions
`TestPrefixBytes` is datadriven over `testdata/prefix_bytes`. `TestPrefixBytesRandomized` generates sorted key sets and verifies round trips. `TestPrefixBytesBuilder_UnsafeGet` stresses last and second-last key retrieval. `BenchmarkPrefixBytes` measures build and iteration costs. Test helpers include `debugString` and `wrapStr`.

## Control Flow
Datadriven commands initialize a builder with bundle size, put sorted keys while computing shared prefix length from the previous key, call `UnsafeGet`, finish a chosen row count into a buffer with an extra byte for checkptr safety, decode and format the result, reconstruct selected keys through `SharedPrefix`/`RowBundlePrefix`/`RowSuffix`, search keys, and list bundle prefixes. Randomized tests create keys with a common block prefix, sort them, choose bundle sizes, sometimes call `Reset`, sometimes finish all but the last key, decode, reconstruct keys in random order, and verify `Search` finds an equal row.

## State And Persistence Behavior
The tests persist encoded prefix bytes into byte slices, explicitly adding one trailing byte outside the column to satisfy Go pointer rules during standalone column tests. They record size after each row to test row-count-specific finishing. Randomized reset paths verify retained builder state does not leak into subsequent encodings.

## Dependencies And Integration Points
The tests use `datadriven`, `crbytes.CommonPrefix`, `binfmt`, `treeprinter`, `testkeys`, `invariants`, and `testify/require`. They directly cover the encoding used by `DefaultKeySchema` in data blocks.

## Risks
Randomized tests use time seeds and should log the seed for reproduction. They mostly generate lowercase byte keys and do not intentionally feed malformed unsorted or empty keys outside invariant panic paths. The benchmark's invariant equality checks run only when invariants are enabled.

## Test Signals
Signals include golden debug formatting, exact size/finish agreement, decoded end offsets, successful key reconstruction, search equality for duplicates, `UnsafeGet` correctness for duplicate versions, and benchmark metrics for build and sequential iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes_test.go -->
