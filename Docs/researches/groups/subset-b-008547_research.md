# subset-b-008547 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_two_lvl.go -->
# sources/storage-engines/pebble/sstable/reader_iter_two_lvl.go

## Purpose
This file implements Pebble's generic two-level SSTable point iterator. It composes a top-level index iterator with a `singleLevelIterator` over second-level index blocks and data blocks, supporting both row-oriented and column-oriented table formats through generic index/data iterator parameters. Its main role is to avoid loading all index state up front, load second-level index blocks on demand, and preserve the exact iterator contract for `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `NextPrefix`, and metadata-returning variants.

## Important APIs, Types, And Functions
`twoLevelIterator[I, PI, D, PD]` owns `secondLevel`, `topLevelIndex`, pool ownership, bloom-filter state, lazy top-level index state, and invariant tracking for bloom-filter prefix misses. `newRowBlockTwoLevelIterator` and `newColumnBlockTwoLevelIterator` initialize table-format-specific instances, disable filtering on the embedded single-level iterator so filtering happens only at the top level, and configure value-block readers when the table has separated value blocks. `loadSecondLevelIndexBlock` decodes the current top-level index entry, applies block-property filtering, reads the second-level index block, and initializes `secondLevel.index`. `ensureTopLevelIndexLoaded` performs deferred top-level index loading. `resolveMaybeExcluded` handles bound-limited block-property filter ambiguity, especially in reverse iteration where it may temporarily step the top-level index backward to infer a lower bound.

## Control Flow
Forward seeks clear synthetic-key and prefix state, clamp virtual-table lower bounds when needed, lazily load the top index, choose between slow top-level seeking and fast reuse of the existing second-level index, then delegate to `singleLevelIterator` or `skipForward`. `SeekPrefixGE` first checks for synthetic max-suffix optimization, then uses bloom filters before loading index blocks; a miss returns nil without invalidating a loaded data block. Reverse seeks seek the top-level separator with `SeekGE`, load the containing or preceding second-level index block, then delegate or call `skipBackward`. `First` and `Last` position the top-level index at the edge and load the first/last second-level block, falling through to skip loops when blocks are filtered or empty. `Next` and `Prev` continue inside the current second-level iterator until exhausted, then move top-level entries. `NextPrefix` first tries second-level prefix advancement, then seeks the top-level index to the successor key.

## State And Persistence Behavior
The iterator persists no data to disk; it manages in-memory read handles, cached block handles, iterator position, error state, and pooled object reuse. Persistent SSTable structures are read through `Reader.readTopLevelIndexBlock`, `Reader.readIndexBlock`, and data-block reads hidden inside `singleLevelIterator`. `topLevelIndexLoaded` is explicitly reset on `Close` for lazy loading. `secondLevel.exhaustedBounds`, `boundsCmp`, `synthetic`, `prefix`, and `err` are carefully updated so direction changes, bound changes, and retry-after-error semantics remain correct. `Close` releases embedded iterator resources, closes the top-level index iterator, resets bloom/lazy flags, and returns the object to its pool when applicable.

## Dependencies And Integration Points
The implementation integrates tightly with `singleLevelIterator`, `Reader`, table-format-specific row/column block iterators, block-property filters, bloom filters, virtual SSTable bounds, value block readers, object storage read handles, `treesteps` tracing, and invariant checking. It implements the public package-level `Iterator`/internal iterator surface expected by Pebble's level iterators, compaction iterators, and table readers. Comments note that `twoLevelCompactionIterator.Next` mirrors `twoLevelIterator.Next` for performance, so behavior changes here can require synchronized compaction-iterator updates.

## Risks
The highest risks are off-by-one separator logic across two-level index boundaries, stale exhaustion state causing false nils, accidental block invalidation after bloom-filter misses, mishandling inclusive virtual upper bounds, and bound-limited block-property filtering that skips blocks whose keys only partially intersect the active bounds. The synthetic max-suffix path returns a fabricated key and defers real seeking until `Next`, so it is sensitive to key lifetime and prefix-containment checks. Pool reuse requires every lazy/filter/index field to be reset on `Close`.

## Test Signals
Coverage comes from the broad reader tests in `reader_test.go`, lazy-loading checks in `reader_lazy_loading_test.go`, and focused two-level benchmarks in `reader_iter_two_lvl_benchmark_test.go`. The randomized prefix/suffix rewriter test explicitly runs both single-level and two-level indexes through random iterator workloads. Checksum, block-property-filter, virtual-reader, hide-obsolete, and readahead tests exercise important integration paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_two_lvl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_two_lvl_benchmark_test.go -->
# sources/storage-engines/pebble/sstable/reader_iter_two_lvl_benchmark_test.go

## Purpose
This benchmark file measures construction and first-use behavior for two-level SSTable iterators, with special attention to the lazy top-level index loading optimization. It creates synthetic SSTables large enough to force two-level indexes and compares construction-only, first-access, seek, prefix seek, bloom-filter miss/hit, iterator reuse, concurrent creation, memory allocation, and table-format behavior.

## Important APIs, Types, And Functions
`setupTwoLevelBenchmarkData` builds a 50,000-key table with small block and index block sizes, verifies `AttributeTwoLevelIndex`, and returns the reader and keys. `setupBloomFilterData` builds a bloom-filter-backed two-level table with timestamped `testkeys`. Benchmarks include `BenchmarkTwoLevelIteratorConstruction`, `BenchmarkTwoLevelIteratorFirst`, `BenchmarkTwoLevelIteratorSeekGE`, `BenchmarkTwoLevelIteratorSeekPrefixGE_NoHit`, `BenchmarkTwoLevelIteratorSeekPrefixGE_Hit`, and a set of `BenchmarkTwoLevelLazyLoading*` functions. The table-format benchmark switches between `newRowBlockTwoLevelIterator` and `newColumnBlockTwoLevelIterator` based on `TableFormat.BlockColumnar`.

## Control Flow
Each setup uses in-memory VFS files, writes enough keys to force a two-level index, closes and reopens the table, then creates a `Reader`. Benchmark bodies repeatedly instantiate iterators with `newRowBlockTwoLevelIterator` or `newColumnBlockTwoLevelIterator`, perform the target operation, validate basic non-nil/nil expectations, and close the iterator. Bloom-filter benchmarks use a missing prefix to isolate the path where `SeekPrefixGE` should return nil before index loading. Reuse manually gets a `twoLevelIteratorRowBlocks` from a local `sync.Pool`, initializes the embedded single-level iterator, seeks, closes, resets, and returns it.

## State And Persistence Behavior
The benchmarks persist test SSTables only in `vfs.NewMem`, not on disk. They intentionally measure transient state: lazy `topLevelIndexLoaded`, pool reuse, read-handle setup, bloom-filter state, and allocations. Readers are closed after benchmark cases, while iterators are closed per iteration to include construction teardown behavior in most timings.

## Dependencies And Integration Points
The file uses Pebble's `NewWriter`, `newReader`/`NewReader`, object storage wrappers, `testkeys.Comparer`, `bloom.FilterPolicy`, `base` seek flags, and both row and column two-level constructors. It is an integration benchmark rather than a unit benchmark because it exercises actual writer output, reader metadata, index blocks, filters, and iterator construction paths.

## Risks
The setup assumes specific key counts and block sizes continue to force two-level indexes; writer format changes could make benchmarks fail or skip unexpectedly. Some benchmarks include table creation outside the timed region but still validate each iteration, so they are correctness-aware but not pure microbenchmarks. The manual pool-reuse benchmark has extra reset/put behavior that may not exactly match production pools and could double-reset if iterator close behavior changes.

## Test Signals
Failures indicate a two-level index was not created, expected hits/misses are wrong, or lazy construction no longer supports the benchmarked operation. Allocation reporting in lazy-loading benchmarks is a useful signal for regressions in deferred index loading. Concurrent access uses `b.RunParallel` to expose thread-safety issues in reader-shared state and iterator-local state.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_two_lvl_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_lazy_loading_test.go -->
# sources/storage-engines/pebble/sstable/reader_lazy_loading_test.go

## Purpose
This file adds datadriven coverage for reader iterator lazy loading. It verifies that iterators can be constructed without immediately loading index blocks and that index loading occurs only when an iterator operation needs access.

## Important APIs, Types, And Functions
`TestReaderLazyLoading` drives `testdata/reader_lazy_loading` with `build` and `iter-lazy` commands. `runBuildForLazyTest` parses writer options, optionally attaches a test filter policy, builds an SSTable with `runBuildCmd`, and returns a `Reader`. `runIterLazyCmd` creates a point iterator with `NewPointIter`, `AlwaysUseFilterBlock`, `NoReadEnv`, a trivial reader provider, and no blob handles, then delegates command execution to `runIterCmd`. `isLazyIndexLoaded` introspects single-level row/column iterators by checking `indexLoaded`. The local `testFilterPolicyImpl`, `testFilterDecoderImpl`, and `testFilterWriter` provide a minimal filter family that returns false for keys beginning with `nonexistent`.

## Control Flow
The datadriven runner maintains one active `Reader`. A `build` command closes any existing reader, constructs writer options, optionally enables the custom filter, and builds a table. An `iter-lazy` command constructs a fresh iterator and passes it to the shared iterator command runner, which performs the requested operations and closes through normal test helpers. The filter decoder allows tests to force a prefix miss path without depending on real bloom-filter hashing.

## State And Persistence Behavior
State is limited to the active reader and temporary in-memory test table generated by `runBuildCmd`. The test intentionally observes iterator-local lazy state, especially `indexLoaded` for single-level iterators. It does not write permanent repository artifacts. Readers are closed on rebuild and at test teardown.

## Dependencies And Integration Points
The test integrates with Pebble's datadriven reader test harness, `ParseWriterOptions`, `runBuildCmd`, `runIterCmd`, `NewPointIter`, filter policy/decoder interfaces, and `leaktest`. It complements the two-level lazy-loading implementation by also checking the single-level lazy mechanism through `isLazyIndexLoaded`.

## Risks
The helper assumes only `singleLevelIteratorRowBlocks` and `singleLevelIteratorColumnBlocks` expose lazy index state; other iterator types are treated as already loaded. That means this test is best at validating single-level lazy loading and command behavior, while two-level lazy top-index state needs separate coverage. The test filter writer emits nil filter bytes but reports a family and success, so changes to filter serialization validation could require updates.

## Test Signals
Useful signals include unexpected eager index loading, iterator operations that fail under `AlwaysUseFilterBlock`, and filter miss behavior for `nonexistent` keys. Because the test is datadriven, expected output changes should be reviewed for whether they reflect intentional lazy-loading semantics or accidental eager reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_lazy_loading_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_test.go -->
# sources/storage-engines/pebble/sstable/reader_test.go

## Purpose
This is the main SSTable reader test and benchmark suite. It validates reader construction, table-format behavior, virtual readers, point iteration, bloom filters, block-property filters, obsolete-point hiding, range deletion/key iteration, prefix/suffix transforms, compaction iterator read-ahead, checksum validation, corruption reporting, and core iterator performance.

## Important APIs, Types, And Functions
`Reader.get` is a test helper that manually checks table filters before using an iterator to find a key. `TestVirtualReader` and `runVirtualReaderTest` exercise virtual SSTable bounds, synthetic suffix/prefix transforms, compaction iteration, raw range deletion/key iteration, bound constraining, and point iteration under virtual `ReadEnv`. `TestReader`, `TestReaderHideObsolete`, `TestHamletReader`, `TestReaderStats`, `TestReaderWithBlockPropertyFilter`, and `TestReaderAttributes` run datadriven fixtures across formats and options. `runTestReader` is the central datadriven harness for `build`, `iter`, and `get`. `TestReaderCheckComparerMerger`, `TestInjectedErrors`, `TestInvalidReader`, `indexLayoutString`, and `forEveryTableFormat` cover metadata and error paths. The `readerWorkload`, `readCall`, and `checker` helpers support `TestRandomizedPrefixSuffixRewriter`. `TestReaderChecksumErrors`, `TestValidateBlockChecksums`, `TestReader_TableFormat`, and `TestReaderReportsCorruption` cover corruption and metadata validation. Benchmark helpers include `buildTestTableWithProvider`, `buildBenchmarkTable`, `basicBenchmarks`, and many `Benchmark*` functions.

## Control Flow
The datadriven harnesses repeatedly build SSTables with varying writer options, open readers, create point/range/compaction iterators, run scripted iterator commands, and print stable output. Virtual-reader tests build a physical table, create `virtual.VirtualReaderParams`, estimate disk usage, then run iterators with constrained bounds and optional synthetic suffixes. Randomized prefix/suffix rewriting builds a control table and a transformed table, positions both iterators, generates random calls across seek and directional methods, and asserts identical results after applying transforms. Corruption tests write valid tables, inspect layouts, flip bytes in selected blocks, reopen or continue using readers, and require checksum or corruption errors to surface.

## State And Persistence Behavior
Most tests use `vfs.NewMem`, temporary directories, or copied fixture SSTables. Reader lifecycle, cache handles, block buffer pools, and object storage providers are explicitly closed. Persistent table bytes are generated through Pebble writers and reopened through `NewReader`/`newReader`. Tests manipulate in-memory/copy-on-temp persisted SSTable bytes to simulate corruption. Virtual-reader state is carried in `ReadEnv.Virtual` and transform structs, not by mutating table bytes.

## Dependencies And Integration Points
The file touches nearly every SSTable reader dependency: cache, block readers, block iterators, filters, table formats, `testkeys`, object storage, remote storage, value blocks, virtual bounds, block properties, compression, checksums, and datadriven fixtures. It is also a performance signal for public iterator APIs because benchmarks use `Reader.NewIter`, `NewPointIter`, `NewCompactionIter`, `Layout`, `ValidateBlockChecksums`, `SeekGE`, `SeekLT`, `Next`, `Prev`, `NextPrefix`, and value reads.

## Risks
The suite is broad and therefore sensitive to legitimate format/output changes. Randomized tests depend on logged seeds for reproduction and cover subtle iterator invalid-state recovery. Corruption tests rely on layout positions and safe error details; changes in checksum implementation or block layout can affect expected errors. Some tests force two-level indexes by small index block sizes and may need adjustment if writer/index heuristics change. Resource handling is important because many subtests create readers, caches, pools, remote providers, and iterators.

## Test Signals
Strong signals include datadriven output drift, mismatch between transformed and control iterators, checksum validation misses, missing corruption callbacks for remote objects, wrong read-ahead setup for compaction, and incorrect counts when hiding obsolete points. Benchmarks establish baseline costs for seeks, scans, layout inspection, prefix advancement, many-version scans, obsolete-point filtering, and value-block-backed reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_64bit_test.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_64bit_test.go

## Purpose
This 64-bit-only test file verifies row-block writer and iterator behavior for very large blocks near or beyond 4 GiB. It protects against integer overflow in restart offsets, restart table locations, and iterator seek calculations.

## Important APIs, Types, And Functions
`TestSingularKVBlockRestartsOverflow` writes one key/value pair with a 2 GiB key and 2 GiB value, then verifies `SeekGE` and `SeekLT`. `TestExceedingMaximumRestartOffset` writes many 4 MiB values until the block buffer exceeds `MaximumRestartOffset`, then expects an `ErrBlockTooBig` on a subsequent add. `TestMultipleKVBlockRestartsOverflow` writes many entries just below 2 GiB, then a 4 GiB value that moves the restart table offset past `math.MaxUint32`, and verifies seeking earlier keys still works.

## Control Flow
Each test skips under CI and slow/instrumented builds because it needs very large allocations. The tests manually preallocate `Writer.buf` to avoid repeated growth copies, add large entries, finish the block, create a `NewIter`, and validate seek results or writer errors. The multiple-KV test verifies `iter.restarts` exceeds both `MaximumRestartOffset` and `math.MaxUint32` before repeatedly seeking keys.

## State And Persistence Behavior
All state is in memory. No files are written. The tests stress the serialized row-block byte slice produced by `Writer.Finish` and the iterator's interpretation of offsets within that slice. They directly observe `writer.buf` length and `iter.restarts`.

## Dependencies And Integration Points
The file depends on row-block `Writer`, `NewIter`, `MaximumRestartOffset`, `ErrBlockTooBig`, `blockiter.NoTransforms`, Pebble `base.InternalKey`, Go build tags for 64-bit architectures, and build/CI environment checks. It complements normal row-block tests by covering sizes impractical for routine CI.

## Risks
These tests are skipped in common automated environments, so regressions may only be caught in explicit large-memory runs. They intentionally allocate multi-GiB buffers and can cause local memory pressure. Because they inspect internal fields and thresholds, any redesign of restart offset encoding needs corresponding test updates.

## Test Signals
Passing tests indicate row-block iteration handles restart table offsets beyond 32-bit boundaries when individual restart offsets remain legal, and that the writer rejects blocks whose restart offsets exceed the supported maximum. Failures usually point to signed/unsigned overflow, truncation to 32 bits, or missing size checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_64bit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_bench_test.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_bench_test.go

## Purpose
This file benchmarks row-block iterator operations with and without synthetic prefixes and suffixes. It focuses on the lower-level block iterator used by SSTable readers, measuring `SeekGE`, `SeekLT`, `Next`, and `Prev` over a generated block.

## Important APIs, Types, And Functions
Global benchmark constants define `benchSynthSuffix`, `benchPrefix`, and `benchComparer`. `chooseOrigSuffix` randomly selects an original suffix of different lengths so suffix replacement can grow keys. `createBenchBlock` fills a row-block `Writer` until a target size, returns the keys expected to be visible to the reader, and returns synthetic prefix/suffix settings. Benchmarks instantiate `NewIter` with `blockiter.MakeSyntheticPrefixAndSuffix` and run the target operation in nested cases for synthetic prefix on/off, synthetic suffix on/off, and restart interval.

## Control Flow
Each benchmark builds one 32 KiB block per subcase, creates a row-block iterator with the selected transforms, resets the timer, then loops over random seeks or repeated directional stepping. Seek benchmarks optionally validate exact key matches under verbose mode when no synthetic suffix changes expected ordering. Directional benchmarks restart at `First` or `Last` when the iterator becomes invalid.

## State And Persistence Behavior
The benchmarks are entirely in memory. The row-block byte slice is produced by `Writer.Finish`; iterator state is reused across loop iterations. Randomness comes from a PCG seeded with current time, so exact key sequence differs by run but benchmark shape is stable.

## Dependencies And Integration Points
The file depends on row-block `Writer`/`NewIter`, `testkeys.Comparer` for MVCC-like suffix ordering, `base` seek flags, and `blockiter.Transforms`. It provides lower-level performance context for reader-level benchmarks that also use synthetic prefix/suffix transforms.

## Risks
Because the RNG seed includes wall-clock time, microbenchmark results can vary slightly across runs. Verbose-only assertions mean normal benchmark runs mainly measure performance, not exhaustive correctness. The benchmark currently tests only restart interval 16, so it does not characterize all restart configurations.

## Test Signals
Allocation or latency changes in these benchmarks can signal regressions in synthetic prefix/suffix handling, restart search, or directional stepping. Unexpected verbose-mode failures would indicate transform or comparator incompatibility in the block iterator.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter.go

## Purpose
This file implements `fragmentIter`, an adapter from a row-block point iterator to `keyspan.FragmentIterator`. It reads range deletion and range key blocks where fragmented internal keys with identical bounds are stored as adjacent entries, and reconstructs them into `keyspan.Span` values.

## Important APIs, Types, And Functions
`fragmentIter` holds a row-block `Iter`, suffix comparator, reusable key/span buffers, direction state, file number for tracing, synthetic prefix/suffix transforms, and an invariant close checker. `NewFragmentIter` initializes the underlying block iterator with fragment transforms, using the block iterator for synthetic prefix handling on start keys and the fragment iterator for end keys. `initSpan`, `addToSpan`, and `applySpanTransforms` decode rangedel/rangekey entries and apply synthetic prefix/suffix rules. `gatherForward` and `gatherBackward` collect adjacent entries with the same start key, sort span keys by trailer, and leave the inner iterator positioned just beyond the gathered span. Public methods implement `First`, `Last`, `Next`, `Prev`, `SeekGE`, `SeekLT`, `Close`, `SetContext`, `String`, `WrapChildren`, and `TreeStepsNode`.

## Control Flow
Forward gathering initializes a span from the current KV, advances while the next internal key has the same start bound, adds each fragment, applies transforms, sorts keys, and returns the span while the block iterator is positioned at the first key of the next span. Backward gathering mirrors this by stepping backward through identical bounds and leaving the iterator at the last key of the previous span. `Next` and `Prev` include direction-switching logic to compensate for those deliberate post-gather positions. `SeekGE` finds the span before `k` with `SeekLT`, returns it if it covers `k`, otherwise advances to the next span.

## State And Persistence Behavior
The iterator persists no bytes; it aliases block data where safe and copies start/end keys when synthetic prefixes or invariants-mode stress require stable buffers. Returned spans are only stable until the next positioning call, and the `Keys` slice may be reused. `Close` closes the inner iterator, clears transient state, and returns the object to `fragmentBlockIterPool` except on some invariant-checking paths.

## Dependencies And Integration Points
The implementation depends on `rowblk.Iter`, `keyspan`, `rangedel`, `rangekey`, `blockiter.FragmentTransforms`, block buffer handles, invariant finalizers, and `treesteps`. It is used by SSTable readers for raw range deletion and raw range key blocks. The restart interval assumption of 1 for range blocks is part of the memory lifetime contract because it avoids prefix-compressed unstable keys.

## Risks
Direction switching is subtle because the inner block iterator is intentionally left outside the returned span. Synthetic prefix/suffix handling can accidentally alias unstable buffers or apply invalid suffixes to unsupported range key kinds. `SeekGE` is implemented via `SeekLT` plus `Next`, which is correct but can do extra work and depends on span end comparisons. Close/pool reuse must clear buffers and handles to avoid leaks or stale data.

## Test Signals
`rowblk_fragment_iter_test.go` exercises datadriven span building, iteration, seeking, direction switches, synthetic sequence numbers, prefixes, suffixes, and invariant-only cases. Reader virtual range-del/range-key tests in `reader_test.go` provide integration coverage through SSTable-level APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter_test.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter_test.go

## Purpose
This datadriven test validates row-block fragment iteration for range deletion and range key spans. It builds range-fragment blocks from textual span input, then runs scripted iterator operations and compares formatted span output.

## Important APIs, Types, And Functions
`TestBlockFragmentIterator` is the sole test. It uses `keyspan.Fragmenter` to normalize input spans, `rangedel.Encode` or `rangekey.Encode` to write block entries, row-block `Writer` with restart interval 1, a small Pebble cache to hold the block data, and `NewFragmentIter` to construct the iterator. The `iter` command supports optional `synthetic-seq-num`, `synthetic-prefix`, `synthetic-suffix`, and `invariants-only` arguments. Scripted operations include `first`, `last`, `next`, `prev`, `seek-ge`, and `seek-lt`.

## Control Flow
A `build` command parses each input line as a `keyspan.Span`, fragments overlapping spans, writes encoded range entries into a block, stores the block in cache, and prints the normalized spans. An `iter` command constructs fragment transforms, gets a cached block handle, creates a fragment iterator, then executes each input command while recovering panics into output for invariant-focused cases. Each operation prints the returned span.

## State And Persistence Behavior
The test stores the active block in an in-memory cache value and evicts/frees the previous block on rebuild. It owns cache and block handles carefully, closing them at test teardown. No permanent files are written. The fragment iterator reads from the cached block buffer and is closed after each `iter` command.

## Dependencies And Integration Points
The test integrates `datadriven`, `keyspan.Fragmenter`, range deletion/key encoders, row-block writer/iterator code, block cache handles, synthetic transform structs, `testkeys.Comparer`, and invariant mode. It directly validates the low-level iterator that reader range deletion/range key APIs use.

## Risks
Expected output is sensitive to span string formatting and key ordering by trailer. Panic recovery is intentionally broad for invariant test cases, so non-invariant panics could be rendered rather than immediately crashing if introduced inside a scripted operation. The test assumes range blocks use restart interval 1, matching production encoding.

## Test Signals
Failures indicate incorrect span fragmentation reconstruction, broken direction switching, seek boundary errors, synthetic transform mistakes, or cache/block-handle lifetime problems. Invariant-only cases add stress for invalid synthetic suffix combinations and aliasing assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_fragment_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_index_iter.go -->
# sources/storage-engines/pebble/sstable/rowblk/rowblk_index_iter.go

## Purpose
This file defines `IndexIter`, a lightweight adapter that makes the row-block `Iter` satisfy Pebble's `blockiter.Index` interface. It is used to iterate row-oriented SSTable index blocks, exposing separators and encoded block handles to higher-level table iterators.

## Important APIs, Types, And Functions
`IndexIter` contains one embedded row-block `Iter`. `Init` initializes it from a raw block byte slice; `InitHandle` initializes it from a `block.BufferHandle`. `Valid`, `IsDataInvalidated`, `Invalidate`, `Handle`, and `Close` expose lifecycle and validity state. `Separator`, `SeparatorLT`, and `SeparatorGT` expose comparator-based separator operations. `BlockHandleWithProperties` decodes the current value with `block.DecodeHandleWithProperties`. `SeekGE`, `First`, `Last`, `Next`, and `Prev` adapt row-block iterator positioning to boolean index-iterator semantics. `TreeStepsNode` delegates tracing to the underlying iterator.

## Control Flow
The adapter is intentionally thin. Positioning calls invoke the corresponding row-block iterator method and return whether a KV was found. Separator methods read the current internal key's user key. Block handle decoding reads the current in-place value. Invalidation and close delegate directly to the inner iterator.

## State And Persistence Behavior
`IndexIter` owns no persistent data. It holds references to the block data or buffer handle managed by the inner `Iter`. `Invalidate` drops those references through the inner iterator, and `Close` releases resources through `Iter.Close`. Validity is determined by the inner restart offset range rather than by the full point-iterator `Valid` contract.

## Dependencies And Integration Points
This adapter is the row-block implementation behind table-format `newIndexIter` calls and is used by both single-level and two-level SSTable iterators. It depends on row-block `Iter`, `base.Comparer`, `block.BufferHandle`, `block.HandleWithProperties`, `blockiter.Transforms`, and `treesteps`.

## Risks
Because it is a thin adapter, the main risks are semantic mismatches: `Valid` must reflect index-entry positioning, separators must be compared with the same comparator used to build the index, and values must always encode block handles with optional properties. Any change to row-block iterator validity internals or index block value encoding can break this adapter.

## Test Signals
Coverage is mostly indirect through reader tests, two-level iterator tests, index layout printing, checksum validation, and benchmarks. Any failure to seek across data blocks, load second-level index blocks, decode handles, or print index layout can implicate this adapter.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/rowblk/rowblk_index_iter.go -->
