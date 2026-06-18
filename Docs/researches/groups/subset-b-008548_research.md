# subset-b-008548 Research

Grouped research for the listed Pebble SSTable row-block and table files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_iter.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_iter.go

## Purpose
Implements iterators over Pebble's row-oriented block format. `Iter` reads blocks containing internal keys, while `RawIter` reads row blocks with raw user keys. The file is in the critical read path for SSTable data, range deletion, range key, index, and properties blocks, so it contains many manual varint and binary-search fast paths.

## Important APIs, Types, And Functions
`Iter` implements `blockiter.Data` and supports `Init`, `InitHandle`, `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `NextWithSamePrefix`, `Prev`, `KV`, `Valid`, `Close`, `Describe`, and metadata-returning variants. It tracks restart offsets, current and next entry offsets, decoded key/value state, reverse-iteration caches, synthetic prefix/suffix transforms, hidden obsolete point filtering, synthetic sequence numbers, and lazy value handling for TableFormatPebblev3 value prefixes.

`RawIter` provides the same block-walking mechanics for non-internal-key row blocks and exposes `SeekGE`, `First`, `Last`, `Next`, `Prev`, `Key`, `Value`, `All`, and `Describe`. `KVEncoding` and `DescribeKV` support diagnostic formatting. `decodeVarint` and `decodeRestart` are hot helpers used throughout the iterators.

## Control Flow And State
Initialization parses the restart count from the block suffix, computes the restart table boundary, stores an unsafe pointer to the block bytes, applies any synthetic prefix buffer initialization, and pre-decodes the first user key for lower-bound checks. Forward movement decodes `{shared, unshared, valueLen}` varints, reconstructs prefix-compressed keys into `fullKey` when necessary, points values into the block data, decodes the internal trailer, applies hidden-obsolete and synthetic-seqnum rules, optionally replaces key suffixes, and constructs either in-place or lazy value handles.

Seeking performs binary search over restart points, then linearly scans within a restart region. Reverse iteration cannot decode prefix-compressed entries backwards, so it replays from the preceding restart point and caches entries in `cached`/`cachedBuf`; switching from reverse back to forward repopulates `fullKey` before continuing. Synthetic suffix seeking has extra off-by-one handling because the restart binary search happens on original on-disk suffixes while returned keys use the replacement suffix.

`NextPrefix` has a TableFormatPebblev3-specific path that uses the value prefix's `SetHasSamePrefix` bit and the high bit in restart entries to skip many MVCC versions with the same prefix before falling back to `SeekGE`. `NextWithSamePrefix` stores a copied prefix for repeated same-prefix advancement.

## Persistence And Integration
The iterator does not persist data itself; it interprets immutable serialized block bytes produced by `rowblk.Writer` and owned either directly or through a `block.BufferHandle`. `Close` releases the handle and preserves reusable buffers. It integrates with SSTable readers through `blockiter.Data`, `base.InternalKV`, `block.GetInternalValueForPrefixAndValueHandler`, `blockiter.Transforms`, and table-format features described in `sstable/table.go`.

## Dependencies
Key dependencies are `internal/base` for internal keys and comparers, `sstable/block` for lazy values and block handles, `sstable/blockiter` for transform contracts, `treeprinter`/`treesteps` for diagnostics, `invariants` for debug checks, and unsafe pointer arithmetic for speed.

## Risks
The main risks are memory-safety and corruption sensitivity around unsafe varint reads, restart offsets, invalid blocks, and very large offsets. Synthetic suffix logic relies on strong invariants: no duplicate prefixes in a suffix-replaced block and comparator ordering of replacement suffixes versus original suffixes. Hidden obsolete points complicate seeks and reverse iteration. Lazy value prefix handling assumes SET values are non-empty when value prefixes are enabled. Because many routines are manually inlined for speed, bug fixes must be applied consistently across duplicated decode paths.

## Test Signals
`rowblk_iter_test.go` exercises raw iteration, datadriven internal iteration, key stability, reverse-to-forward direction changes, synthetic prefix and suffix transforms, and randomized `IsLowerBound` checks. `unsafe_test.go` covers the shared unsafe varint decoder. Table-level iterator benchmarks in `single_lvl_iter_benchmark_test.go` provide performance signal for construction and first-seek paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_iter_test.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_iter_test.go

## Purpose
Tests row-block iteration semantics for both `RawIter` and internal-key `Iter`, including restart intervals, ordering, prefix compression, key stability, direction changes, and synthetic key transforms.

## Important APIs, Types, And Functions
`blockIterInternalIterator` adapts `Iter` to `base.InternalIterator` for `itertest.RunInternalIterCmd`. `TestInvalidInternalKeyDecoding` verifies malformed internal keys decode to invalid trailers. `TestBlockIter` tests `RawIter` seek/forward/reverse behavior against a hand-encoded block. `TestBlockIter2` uses datadriven commands to build blocks at restart intervals 1 through 4 and exercise iterator commands. `TestBlockIterKeyStability`, `TestBlockIterReverseDirections`, `TestBlockSyntheticPrefix`, `TestBlockSyntheticSuffix`, and `TestIsLowerBoundRand` cover important iterator contracts.

## Control Flow And State
Tests construct row blocks with `Writer`, open iterators with no transforms or synthetic prefix/suffix transforms, and compare returned `InternalKV` sequences against an equivalent block with transformed keys materialized on disk. The synthetic suffix tests intentionally seek around original suffixes, replacement suffixes, in-between suffixes, suffixless keys, exhausted iterators, and direction changes. The randomized lower-bound test generates sorted key sets and random transforms, then checks that `IsLowerBound` has no false positives.

## Persistence And Integration
The tests persist only transient encoded blocks in memory. They integrate with `datadriven` testdata, `itertest`, `testkeys.Comparer`, `blockiter.Transforms`, and `require` assertions. The key-stability test inspects unsafe pointer ranges to ensure restart-interval-1 user keys are backed by the original block bytes.

## Risks
Coverage is broad for transform and seek behavior, but the tests use in-memory blocks and do not directly cover corrupt restart tables, checksum boundaries, lazy value-block retrieval, or very large block offsets. Randomized tests depend on logged seeds for reproduction.

## Test Signals
This file is itself the primary semantic signal for `rowblk.Iter`. It also acts as regression coverage for a previous reverse-to-forward bug where `fullKey` was not restored after reverse iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_rewrite.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_rewrite.go

## Purpose
Provides a reusable row-block rewriter that replaces a point-key suffix within one encoded row block while preserving trailers, values, restart interval behavior, and row-block encoding.

## Important APIs, Types, And Functions
`NewRewriter` creates a `Rewriter` with a comparer and restart interval. `Rewriter` owns reusable `Writer`, `Iter`, scratch key, and byte allocator state. `RewriteSuffixes(input, from, to)` returns the rewritten block plus the first and last rewritten internal keys.

## Control Flow And State
The rewriter initializes an `Iter` over the source block, pre-sizes writer buffers when possible, scans every key with `First`/`Next`, requires every key to be a SET, validates that each user-key suffix equals `from`, builds a scratch key with the same prefix and trailer but `to` suffix, validates keys under invariants, and writes the original in-place value through `Writer.Add`. It copies the first and last rewritten keys through `bytealloc.A` so returned span keys outlive the scratch buffer.

## Persistence And Integration
The function transforms one in-memory uncompressed row block into another. It is used by `sstable/suffix_rewriter.go` and `RawRowWriter.rewriteSuffixes` for fast whole-SST suffix replacement. It intentionally preserves raw v3 value-prefix bytes because the row-block iterator is not configured to interpret value prefixes in this path.

## Dependencies
Depends on `base.Comparer` for comparison, splitting, and validation; `rowblk.Iter` for decoding; `rowblk.Writer` for encoding; `bytealloc` for durable returned keys; and `blockiter.NoTransforms` for reading original on-disk keys.

## Risks
The source block must contain only SET keys whose suffix is exactly `from`; any other key kind or suffix aborts. Obsolete bits are not preserved as semantic metadata beyond the decoded trailer behavior exposed by `Iter`. Writer buffer reuse means callers must treat the returned block as owned until the next rewrite. Since the rewriter is per-block, table-level metadata and properties must be reconciled by the caller.

## Test Signals
The block rewriter is exercised indirectly by `suffix_rewriter_test.go`, especially the by-block rewrite path that compares rewritten SST properties and, when formats match, byte-for-byte output against the reader/writer loop.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_rewrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_writer.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_writer.go

## Purpose
Serializes key/value pairs into Pebble's row-oriented block format: prefix-compressed entries followed by restart offsets and a restart count. It is the low-level encoder used for data, index, range deletion, range key, properties, and raw blocks.

## Important APIs, Types, And Functions
`Writer` exposes `Reset`, `EntryCount`, `CurKey`, `CurValue`, `CurUserKey`, `Add`, `AddWithOptionalValuePrefix`, `Finish`, `EstimatedSize`, `AddRaw`, and `AddRawString`. Constants include `MaximumRestartOffset`, `EmptySize`, `TrailerObsoleteBit`, `TrailerObsoleteMask`, and `ErrBlockTooBig`. `storeWithOptionalValuePrefix` performs the actual varint, key, optional value-prefix, value, and restart encoding.

## Control Flow And State
Each add swaps `curKey` and `prevKey`, encodes the internal key, optionally sets the obsolete bit, computes a shared prefix up to `maxSharedKeyLen`, appends a restart offset when `nEntries == nextRestart`, and writes three varints followed by unshared key bytes and value bytes. For Pebblev3 data blocks, `setHasSameKeyPrefixSinceLastRestart` is accumulated and encoded into the high bit of restart offsets; `maxSharedKeyLen` limits key sharing to the previous key prefix so `NextPrefix` can skip efficiently.

`Finish` ensures even an empty block has one restart point, appends all restart offsets and the restart count, returns the encoded block, and clears per-block counters/buffers for reuse. `Reset` fully resets state while preserving allocated slices.

## Persistence And Integration
The writer produces the persistent bytes read by `rowblk.Iter` and described by `sstable/table.go`. It integrates with `RawRowWriter`, suffix rewriting, properties serialization, range-key/range-delete blocks, and value-block prefix metadata. The obsolete bit is internal to row-block encoding and masked away when reading current keys.

## Dependencies
Uses `base.InternalKey` encoding, `block.ValuePrefix` for v3 value/value-block metadata, `errors` for corruption-sized block reporting, and unsafe string-to-byte conversion in `AddRawString`.

## Risks
`RestartInterval` must be configured by callers; an interval of zero would make restart scheduling invalid. Blocks cannot exceed `MaximumRestartOffset` because one restart bit is reserved for prefix metadata. The high-bit restart flag and obsolete trailer bit are format-internal and must stay consistent with `Iter.decodeRestart` and trailer masking. Manual varint and shared-prefix encoding is performance-sensitive and assumes keys are added in sorted order by higher layers.

## Test Signals
`rowblk_writer_test.go` verifies reset semantics, exact byte layout for raw prefix compression, optional value-prefix encoding, and high-bit restart metadata. Iterator and suffix rewrite tests also validate that written blocks can be read and transformed correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_writer_test.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_writer_test.go

## Purpose
Provides focused unit coverage for the low-level row-block writer's state reset and exact byte encoding.

## Important APIs, Types, And Functions
`TestBlockWriterClear` exercises `Writer.Reset`. `TestBlockWriter` checks exact raw block output for `apple`, `apricot`, and `banana`. `TestBlockWriterWithPrefix` drives `AddWithOptionalValuePrefix` and inspects current key/value accessors and restart high-bit behavior.

## Control Flow And State
The tests write small blocks, compare internal writer state before and after reset, and compare the full encoded block bytes against hard-coded expected encodings. The prefix test uses restart interval 2 to produce multiple restart points and verifies that cumulative `setHasSameKeyPrefix` metadata is only set when all entries since the last restart kept the same prefix.

## Persistence And Integration
All persistence is in-memory encoded row blocks. The test protects the wire format consumed by `rowblk.Iter`, `RawIter`, table indexes, and properties blocks.

## Risks
Hard-coded bytes are precise and valuable but cover only small examples. They do not test `ErrBlockTooBig`, invalid restart intervals, high cardinality restart tables, or non-SET key kinds with obsolete bits.

## Test Signals
The file gives strong regression signal for byte-level compatibility of row-block encoding, especially value-prefix storage and restart high-bit encoding introduced for prefix skipping.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/unsafe_test.go -->
# sources/storage-engines/pebble/sstable/rowblk/unsafe_test.go

## Purpose
Tests and benchmarks the unsafe varint decoder used by row-block iterators.

## Important APIs, Types, And Functions
`TestDecodeVarint` encodes selected `uint32` values with `binary.PutUvarint` and decodes them through `decodeVarint`. `BenchmarkDecodeVarint` creates random encoded values and repeatedly decodes unsafe pointers while retaining the final pointer to prevent dead-code elimination.

## Control Flow And State
The test covers values across one- through five-byte uvarint lengths, including powers at 7, 14, 21, 28, and 31-bit boundaries. The benchmark stores pointers to allocated five-byte buffers and times only decoder calls.

## Persistence And Integration
No persistent state is written. The benchmark and tests integrate with the performance-critical decoder in `rowblk_iter.go`.

## Risks
The unit test currently prints mismatches instead of failing, so it is weak as a correctness gate. It also does not test malformed or truncated varints; production callers assume valid block bounds. The benchmark uses random time-based data, so exact numbers are not reproducible, though the code path is stable.

## Test Signals
The benchmark is useful for detecting performance regressions in the decoder, while the correctness test should be strengthened to assert equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/unsafe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk_writer.go -->
# sources/storage-engines/pebble/sstable/rowblk_writer.go

## Purpose
Implements Pebble's row-oriented SSTable writer (`RawRowWriter`) for table formats through Pebblev4. It coordinates point, range deletion, range key, index, filter, value block, property, footer, and suffix-rewrite output using row-oriented blocks.

## Important APIs, Types, And Functions
`RawRowWriter` implements the row-block `RawWriter` surface: `Add`, blob-handle rejection methods, `EncodeSpan`, `ComparePrev`, `IsLikelyMVCCGarbage`, `Error`, `Close`, `EstimatedSize`, `Metadata`, suffix/data-block copy helpers, and internal block/property/filter setters. Important helpers include `coordinationState`, `sizeEstimate`, `indexBlockBuf`, `dataBlockEstimates`, `dataBlockBuf`, `bufferedIndexBlock`, `makeAddPointDecisionV2`, `makeAddPointDecisionV3`, `addPoint`, `addTombstone`, `addRangeKey`, `flush`, `maybeFlush`, `finishDataBlockProps`, `addIndexEntry`, `writeTwoLevelIndex`, and `assertFormatCompatibility`.

## Control Flow And State
`newRowWriter` validates row format use, applies defaults, initializes metadata, flush governors, block writers, optional value-block writer, filter writer, property collectors, obsolete collector, and range-key encoder. Point adds check ordering, decide obsolete status, optionally write older SET values to value blocks in Pebblev3, maybe flush the current data block, update block properties and filters, encode the key/value into the active `rowblk.Writer`, and update table properties.

When a data block flushes, the writer finishes block properties, finalizes the row block, updates tombstone-density counters, compresses/checksums the block, computes an index separator, possibly rotates a lower-level index block, schedules the write through `writeQueue`, and starts a fresh data block. `Close` drains the queue, finalizes the last data block or an empty block, writes filters, single- or two-level indexes, range deletion and range key blocks, value blocks, table properties, metaindex/footer via `layoutWriter`, then records metadata and returns pooled buffers.

## Persistence And Integration
This file is the persistence boundary for row-format SSTables. It writes data blocks, index blocks, meta blocks, properties, filters, range blocks, optional value blocks, and the footer to an `objstorage.Writable`. It integrates with `sstable.Writer`, `layoutWriter`, `rowblk.Writer`, `valblk.Writer`, block property collectors, Bloom filters, `rangedel`/`rangekey` encoders, table format compatibility, and suffix-rewrite/copy APIs.

## Dependencies
Major dependencies include `internal/base` for key kinds and comparers, `keyspan`, `rangedel`, `rangekey`, `objstorage`, `sstable/block`, `blockkind`, `rowblk`, `valblk`, `blob`, `bytealloc`, `invariants`, and `sync.Pool` for reusable block buffers.

## Risks
Correctness depends on strict key ordering, fragmented range tombstones/range keys, accurate block handle offsets, sequential block property collector calls, queue draining before close, and consistent table-format feature gating. The writer contains subtle lifetime rules: separators and properties must be copied or encoded before scratch buffers are reused, and block buffers are pooled after close. Obsolete-key marking in strict-obsolete tables is complex around MERGE, point deletes, lowest-level writes, and forced range-delete obsolescence. Suffix-copy paths intentionally reset or recompute only selected properties and require collector support.

## Test Signals
Direct tests are spread across SSTable writer/reader suites outside this work item. Within this subset, `suffix_rewriter_test.go` exercises `rewriteSuffixes`, filter copying, property remapping, and close/metadata behavior; `rowblk_writer_test.go` protects the underlying block encoder; `single_lvl_iter_benchmark_test.go` builds an SST through `NewWriter` and reads it with row-block iterators.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/runlength_bitmap.go -->
# sources/storage-engines/pebble/sstable/runlength_bitmap.go

## Purpose
Implements a compact run-length encoding for bitmaps that are written in increasing set-bit order and read sequentially. It is optimized for spatial locality, especially long all-zero or all-one byte runs.

## Important APIs, Types, And Functions
`BitmapRunLengthEncoder` exposes `Init`, `Set`, `FinishAndAppend`, and `Size`. `IterSetBitsInRunLengthBitmap` returns an `iter.Seq[int]` yielding set bit indexes from an encoded bitmap.

## Control Flow And State
The encoder buffers one current byte (`currByte`) and its byte index, plus a pending run length for consecutive all-set bytes. `Set(i)` requires monotonically increasing indexes, folds bits into the current byte when possible, flushes mixed bytes directly, encodes all-zero gaps as `0x00` followed by a uvarint byte count, and encodes all-one runs as `0xFF` followed by a uvarint byte count. Mixed bytes are stored literally, excluding `0x00` and `0xFF` because those byte values signal runs.

The decoder scans encoded bytes, treating `0x00` as a zero-run skip, `0xFF` as a set-run yield loop, and all other bytes as literal bit masks. `Size` estimates the final encoded length without mutating the pending state.

## Persistence And Integration
The encoded byte slice is intended to be embedded in SSTable metadata or related table structures that need compact sequential bitmap scans. The file itself is independent of disk I/O and returns bytes through caller-provided buffers.

## Dependencies
Uses `encoding/binary` for uvarints, Go's `iter` package for sequence iteration, and `invariants.MaybeMangle` to catch stale buffer assumptions during reset.

## Risks
`Set` assumes strictly increasing indexes; out-of-order calls are not checked and would corrupt logical output. `IterSetBitsInRunLengthBitmap` assumes valid encodings; it does not handle malformed/truncated uvarints. All-one runs can yield many indexes, so decoding intentionally scales with the number of set bits.

## Test Signals
`runlength_bitmap_test.go` provides datadriven exact encoding checks plus randomized round-trip coverage that decodes and re-encodes generated bitmaps.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/runlength_bitmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/runlength_bitmap_test.go -->
# sources/storage-engines/pebble/sstable/runlength_bitmap_test.go

## Purpose
Validates the run-length bitmap encoder/decoder with datadriven expected encodings and randomized round trips.

## Important APIs, Types, And Functions
`TestRunLengthBitmap` reads `testdata/runlength_bitmap`, encodes textual `0`/`1` inputs, reports `Size`, dumps binary encoding with `binfmt.FHexDump`, and verifies decode/re-encode equality. `TestRunLengthBitmap_Randomized` generates random bitmap densities and validates canonical round trips.

## Control Flow And State
The datadriven test resets a reusable encoder and buffers for each command, sets bits for `1` characters in the input, finalizes the encoding, then reconstructs a new encoder by iterating `IterSetBitsInRunLengthBitmap`. The randomized test chooses bitmap length up to 100,000 and a density cutoff, encodes all selected indexes in order, and requires the re-encoded bytes to match exactly.

## Persistence And Integration
No durable files are written beyond datadriven test output expectations. The tests integrate with the public encoder and iterator in `runlength_bitmap.go`.

## Risks
The tests do not feed malformed encodings or out-of-order `Set` calls. Randomized coverage uses a time-based seed without logging it, which can make failures harder to reproduce.

## Test Signals
The combination of exact datadriven cases and randomized canonicalization gives useful signal that `Size`, `FinishAndAppend`, and the sequential decoder agree on the encoding format.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/runlength_bitmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/single_lvl_iter_benchmark_test.go -->
# sources/storage-engines/pebble/sstable/single_lvl_iter_benchmark_test.go

## Purpose
Benchmarks construction and first-positioning operations for row-block single-level SSTable iterators.

## Important APIs, Types, And Functions
Global `benchReader` and `benchIterOpts` are initialized in `init`. Benchmarks include `BenchmarkIteratorConstruction`, `BenchmarkIteratorFirst`, `BenchmarkIteratorSeekGE`, `BenchmarkIteratorSeekPrefixGE_Hit`, and `BenchmarkIteratorSeekPrefixGE_NoHit`.

## Control Flow And State
The `init` function builds an in-memory Pebblev3 SSTable with 10,000 ordered keys, 4 KiB data and index blocks, Bloom filter policy, default comparer, and default merger. It opens a reader and prepares iterator options with a block buffer pool and trivial reader provider. Each benchmark constructs `newRowBlockSingleLevelIterator`; some time only construction, while others stop the timer around setup and measure `First`, `SeekGE`, or `SeekPrefixGE` with filter enabled for hit/no-hit cases.

## Persistence And Integration
The benchmark stores its SSTable in `vfs.NewMem` and keeps a reader alive globally for repeated benchmark iterations. It integrates the row-block writer, table reader, block cache/buffer environment, Bloom filters, and single-level row-block iterator path.

## Risks
Because setup happens in package init and uses a fixed synthetic dataset, benchmark representativeness is limited to sorted short keys and Pebblev3 row blocks. The global reader is not closed, which is acceptable for process-lifetime benchmarks but not a production pattern. Benchmark results are sensitive to filter settings and buffer pool behavior.

## Test Signals
This file provides performance regression signal for iterator construction, first access, point seek, and prefix seek with Bloom-filter hit and miss behavior. It is not a correctness test.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/single_lvl_iter_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/suffix_rewriter.go -->
# sources/storage-engines/pebble/sstable/suffix_rewriter.go

## Purpose
Implements efficient SSTable key-suffix replacement. It can rewrite all point SET keys and range-key SET suffixes from `from` to `to`, preserving the input table format and copying or recomputing selected table metadata.

## Important APIs, Types, And Functions
Top-level APIs are `RewriteKeySuffixesAndReturnFormat`, `RewriteKeySuffixesViaWriter`, and `NewMemReader`. Internal helpers include `rewriteKeySuffixesInBlocks`, `rewriteDataBlocksInParallel`, `rewriteRangeKeyBlockToWriter`, `getShortIDs`, `copyFilterWriter`, `readBlockBuf`, and `memReader`. `blockRewriter` abstracts row- or column-block rewriting, and `blockWithSpan` carries rewritten block span keys plus compressed physical data.

## Control Flow And State
The fast path opens a memory reader, reads properties, validates concurrency, rejects value-block SSTables, requires matching comparer names, forces the output table format to the input format, disables filter rebuilding, and delegates to `RawWriter.rewriteSuffixes`. Data blocks are rewritten in parallel with static round-robin partitioning: each worker reads and verifies a block, calls a block rewriter, validates start/end keys, compresses the rewritten block, and merges compression stats under a mutex. Errors are collected deterministically by worker id.

Range key blocks are rewritten through a raw range-key iterator: every key must be `RangeKeySet`, every suffix must equal `from`, and suffix fields are replaced before re-encoding spans. Existing filters can be copied through `copyFilterWriter` because prefix filters are unaffected by suffix replacement. `RewriteKeySuffixesViaWriter` is slower but simpler: it iterates all keys through a reader, rewrites each key into a new writer, and rederives more metadata.

## Persistence And Integration
The APIs read SSTable bytes from memory and write a new SSTable to `objstorage.Writable`. They integrate with `Reader`, `RawWriter`, `RawRowWriter.rewriteSuffixes`, block property collectors, filters, block compression/checksum code, and in-memory `objstorage.Readable`. The fast path preserves table format and copies filter bytes; properties are partially copied and partially recomputed by the writer.

## Dependencies
Depends on `base.Comparer` splitting and validation, `objstorage`, `block` compression/checksum/decompression, `blockkind`, `invariants`, `sync`, `slices`, `cmp`, unsafe alignment checks, and block property collector contracts such as `SupportsSuffixReplacement` and `AddCollectedWithSuffixReplacement`.

## Risks
Inputs are constrained: all point keys must be SETs with the `from` suffix, range keys must be SETs with the `from` suffix, value-block SSTables are rejected, and range deletes are ignored by the top-level documented contract. Obsolete bits are lost. Copying filter blocks assumes prefix-only filtering and matching comparer/split behavior. `readBlockBuf` may return slices into the source SSTable, so callers must clone when a writable may mutate buffers. Parallel rewriting must preserve output block order and deterministic error reporting.

## Test Signals
`suffix_rewriter_test.go` checks property collector remapping, range-key suffix replacement, filter copying, format preservation, idempotence against mutable output buffers, and equivalence between fast by-block and slower reader/writer rewrites when formats match. `BenchmarkRewriteSST` compares throughput across sizes, compression modes, and concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/suffix_rewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/suffix_rewriter_test.go -->
# sources/storage-engines/pebble/sstable/suffix_rewriter_test.go

## Purpose
Tests and benchmarks SSTable suffix rewriting across table formats, property collectors, filters, point keys, and range keys.

## Important APIs, Types, And Functions
`TestRewriteSuffixProps` is the main correctness test. `makeTestkeySSTable` builds synthetic SSTables with a shared prefix, test-key suffixes, point SETs, and range-key SETs. `BenchmarkRewriteSST` compares `RewriteKeySuffixesViaWriter` with block-level rewriting at several concurrency levels.

## Control Flow And State
The test iterates table formats from Pebblev2 through `TableFormatMax`, creates an SSTable with a random subset of test block property collectors, then rewrites suffix `@212` to `@645` using both the by-block and writer-loop paths. Rewriter options intentionally specify a random table format to verify that block-level rewrite preserves the original format. New collector subsets are shuffled and truncated, then expected table and block property values are checked on the rewritten reader. Each rewrite is repeated five times to catch mutation of the source SSTable buffer.

`makeTestkeySSTable` writes many point keys through `Raw().Add` and range keys through `RangeKeySet`. The benchmark constructs SSTables at 100, 10,000, and 1,000,000 keys with no compression and Snappy, then measures reader/writer loop and block rewrite with concurrency 1, 2, 4, 8, and 16.

## Persistence And Integration
Tests use `objstorage.MemObj` and `NewMemReader` for in-memory SSTables. They integrate with test key comparers/schemas, Bloom filters, block property collector test utilities, range keys, table layout inspection, and reader property loading.

## Risks
The test uses random collector subsets and seeds are logged, which helps reproduction. It focuses on suffix-rewrite-compatible SSTables and does not test expected failures like bad suffixes, non-SET point keys, value-block SSTables, mismatched comparers, or unsupported collectors. The benchmark appears to pass `_123`/`_456` in one block-rewrite branch while constructed keys use `@123`/`@456`, which may be intentional failure-path coverage or a typo worth reviewing if the benchmark is used.

## Test Signals
Strong signal for successful suffix rewrite metadata behavior: table properties, user property short IDs, per-block properties, format preservation, filter copy viability, and by-block versus reader/writer equivalence when block boundaries are unchanged.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/suffix_rewriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/table.go -->
# sources/storage-engines/pebble/sstable/table.go

## Purpose
Defines the SSTable package overview, on-disk table layout documentation, footer constants and parsing/encoding logic, and a helper for two-level-index support by table format.

## Important APIs, Types, And Functions
The central type is unexported `footer`, containing table format, attributes, checksum type, metaindex handle, index handle, and footer handle. Functions are `readFooter`, `parseFooter`, `footer.encode`, and `supportsTwoLevelIndex`. The file also declares block handle sizing constants, checksum/magic/version/footer sizes, meta block names, index type constants, and table magic strings.

## Control Flow And State
`readFooter` reads up to the maximum footer length from the end of an `objstorage.Readable`, validates minimum size, and delegates to `parseFooter`. `parseFooter` dispatches on magic bytes for LevelDB, RocksDB, and Pebble footers; determines table format from magic/version; selects footer length; validates checksum type; verifies Pebblev6+ footer CRC; reads Pebblev7 attributes; decodes metaindex and index block handles; and rejects handles extending beyond file size.

`footer.encode` writes the corresponding footer format: zeroed padding, checksum type, encoded block handles, format version, magic, optional attributes, and optional CRC over footer bytes with the checksum field skipped. `supportsTwoLevelIndex` allows two-level indexes for RocksDBv2 and Pebble formats but not LevelDB.

## Persistence And Integration
This file documents and implements persistent SSTable footer compatibility across LevelDB, RocksDB, and Pebble formats. It is used by readers to locate metaindex and index blocks and by writers/layout code to finalize table files. The layout comment also defines how row blocks, restart points, data-block v3 value prefixes, restart high bits, and v4 obsolete bits are interpreted by `rowblk.Writer` and `rowblk.Iter`.

## Dependencies
Depends on `objstorage` for reads, `block.ReadRaw` and block handle encoding/decoding, `crc` for footer checksums, `base` for corruption errors/logging/file numbers, and table-format helpers defined elsewhere in the `sstable` package.

## Risks
Footer parsing is compatibility-critical. Incorrect footer-size, magic, version, checksum offset, or handle-bound validation can make valid tables unreadable or accept corrupt tables. Pebblev7 attributes must be checksummed consistently. The package comment is also a contract for row-block encoding, so changes in `rowblk` must remain aligned with this documentation.

## Test Signals
Tests for footer parsing and table format compatibility are outside this subset. In this work item, row-block writer/iterator tests and suffix-rewriter tests indirectly validate the documented row-block and table layout assumptions by writing and reading in-memory SSTables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/table.go -->
