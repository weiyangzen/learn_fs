# Research: subset-b-008546

This grouped report covers Pebble SSTable property encoding/decoding, reader construction, point iterator contracts, lazy single-level iterator behavior, and the related tests.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/properties_gen.go -->
# sources/storage-engines/pebble/sstable/properties_gen.go

## Purpose
`properties_gen.go` is generated code for serializing, deserializing, and rendering the `Properties` structure used by Pebble SSTables. It maps well-known RocksDB-compatible and Pebble-specific property keys to typed fields, tracks which fields were present in the on-disk properties block, encodes properties back into block key/value form, and renders a stable human-readable string.

## Important APIs, Types, and Functions
- `(*Properties).load(iter.Seq2[[]byte, []byte]) error` consumes decoded property key/value pairs and populates the `Properties` receiver.
- `(*Properties).encodeAll() map[string][]byte` emits all persistent property key/value pairs, including user properties, using the on-disk byte encodings expected by SSTable writers.
- `(*Properties).isLoaded(bit int) bool` tests the generated `Loaded` bit vector.
- `(*Properties).String() string` formats loaded or non-zero fields, then user properties in sorted order.
- `_bit_*` constants define stable bit positions for every generated property field, with `_numPropBits` sizing the encoded map.

## Control Flow
`load` clears `p.Loaded`, iterates through property pairs, switches on the string property key, decodes integer fields with `binary.Uvarint`, fixed-width `IndexType` with `binary.LittleEndian.Uint32`, booleans from single-byte `"1"`, and string fields from interned byte slices. Unknown keys are treated as user properties unless present in `ignoredInternalProperties`.

`encodeAll` allocates a result map sized for known plus user properties, uses a reusable scratch allocation buffer, and inserts mandatory properties unconditionally while optional properties are omitted when they equal their zero value. Numeric properties are varint encoded; `IndexType` is little-endian; boolean properties encode as `"0"` or `"1"` when non-default.

`String` mirrors the generated property order. It prints a field when it is non-zero/non-empty/non-false or when its loaded bit is set, which preserves explicitly present zero-valued fields. User properties are sorted with `maps.Keys` and `slices.Sorted`; non-printable values are rendered as `hex:<bytes>`.

## State and Persistence Behavior
This file defines the persistence contract for the properties block. The property names are part of on-disk compatibility, including RocksDB names like `rocksdb.num.entries`, `rocksdb.comparator`, and `rocksdb.block.based.table.index.type`, plus Pebble extensions like value blocks, range-key counters, column-block schema, compression stats, obsolete-point strictness, and value-separation settings.

The `Loaded` bitset is transient state used after loading to distinguish absent fields from explicitly encoded zero values, especially for string rendering and compatibility checks. `UserProperties` persists application or collector metadata not recognized as built-in properties.

## Dependencies and Integration Points
- Uses Go `iter.Seq2` so callers can feed either row-block raw iterators or columnar key/value decoders.
- Uses `encoding/binary` for durable numeric encodings.
- Uses `intern.Bytes` to reduce allocation/copying for property names and string-like values.
- Used by `reader.go` through `decodePropertiesBlock` and `ReadPropertiesBlock`.
- Used by writer-side code through `saveToRowWriter`/property block construction, which relies on `encodeAll`.

## Risks and Edge Cases
- The generated loader ignores `binary.Uvarint` decode errors and uses zero on malformed data; corruption detection must happen in lower block decoding or surrounding validation.
- `IndexType` decoding assumes at least four bytes; malformed short values could panic unless callers validate property block shape first.
- Optional properties are omitted on zero/default encode, so old readers must tolerate absence and callers must use `Loaded` when presence matters.
- Property key strings and bit positions must stay synchronized with the `Properties` struct and generator metadata.
- User properties are stringified values; binary user values are preserved as strings but only rendered safely by `String`.

## Test Signals
`properties_test.go` loads known properties from a Hamlet fixture, round-trips a populated `Properties` value through row-block encoding, quick-checks randomized `Properties` values, and benchmarks `load`. These tests exercise the generated switch, optional-field omission, `Loaded` clearing, and sorted user-property formatting indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/properties_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/properties_test.go -->
# sources/storage-engines/pebble/sstable/properties_test.go

## Purpose
`properties_test.go` validates SSTable properties decoding, encoding round-trips, and load performance. It anchors generated property handling against both a real table fixture and randomized in-memory properties blocks.

## Important APIs, Types, and Functions
- `TestPropertiesLoad` opens `testdata/hamlet-sst/000002.sst`, constructs a reader, reads the properties block, and compares it with a known `Properties` literal.
- `testProps` is a broad fixture covering deletion counts, range-key counts, filter/index metadata, compression metadata, and user properties.
- `TestPropertiesSave` writes properties with `saveToRowWriter`, decodes them with `rowblk.NewRawIter` and `Properties.load`, and compares results.
- `BenchmarkPropertiesLoad` measures repeated raw-row properties decoding.

## Control Flow
`TestPropertiesLoad` uses the real filesystem fixture, opens it through `vfs.Default`, constructs `newReader`, calls `ReadPropertiesBlock`, clears `Loaded` before comparison, and reports structured diffs through `pretty.Diff`.

`TestPropertiesSave` defines a helper `check1` that writes a properties block with `propertiesBlockRestartInterval`, decodes it through a raw row-block iterator, clears `Loaded`, and compares the original and decoded structures. It first checks `testProps`, then runs 1000 `testing/quick` generated `Properties` values. For randomized values, it normalizes `TopLevelIndexSize` to zero when `IndexPartitions` is zero, matching writer-side omission semantics.

The benchmark builds one encoded properties block from `testProps` and repeatedly creates raw iterators and calls `load`.

## State and Persistence Behavior
The tests confirm that persisted property bytes can be read from both production fixture files and newly encoded row-block data. Clearing `Loaded` before equality checks means the tests assert semantic field values, not exact presence bits. `UserProperties` are included in `testProps`, so user metadata survives encode/decode.

## Dependencies and Integration Points
- Exercises `Reader.ReadPropertiesBlock`, `newReader`, and the fixture table reader path.
- Exercises `rowblk.Writer`, `rowblk.NewRawIter`, and `Properties.saveToRowWriter`.
- Uses `vfs.Default` for fixture IO and in-memory row block buffers for round-trip tests.
- Uses `testing/quick` to stress generated property encodings over many shapes.

## Risks and Edge Cases
- Randomized quick values may include unusual strings and maps, but the test normalizes only one known writer invariant; other writer-side omissions still need targeted coverage when new properties are added.
- The fixture comparison intentionally clears `Loaded`, so it does not protect exact loaded-bit behavior.
- The test focuses on pre-columnar row-block property encoding; columnar property block decoding is exercised through reader tests rather than directly here.

## Test Signals
Strong positive signals are fixture compatibility with an existing SSTable, deterministic round-trip of a broad explicit fixture, 1000 randomized round-trips, and a benchmark tracking decode cost. The tests should be updated whenever generated property fields or mandatory/optional encode rules change.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/properties_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/random_test.go -->
# sources/storage-engines/pebble/sstable/random_test.go

## Purpose
`random_test.go` stress-tests SSTable point iterators under random table shapes and injected read errors. Its primary contract is that if a file-read error is injected during an iterator operation, the operation must not silently return a key while hiding the error.

## Important APIs, Types, and Functions
- `TestIterator_RandomErrors` runs 50 seeded subtests.
- `runErrorInjectionTest` builds a randomized SSTable, wraps reads with `errorfs`, creates a `Reader`, constructs a point iterator, and executes 1000 random valid operations.
- `opRunner` tracks current iterator direction, last operation, current KV, and whether the last operation was `SeekPrefixGE`.
- `randomTableConfig` parameterizes writer options, keyspace, key count, value sizes, suffix/sequence ranges, and RNG.
- `buildRandomSSTable` writes sorted randomized internal keys through `NewRawWriter`.

## Control Flow
Each seed creates a memfs file, randomizes writer options across table formats, block sizes, index sizes, optional bloom filters, optional block-property collectors, column key schemas, and lowest-level behavior. After writing 10,000 random internal point keys, the test reopens the file through an `errorfs.Toggle` and `Counter`; injection begins only after `NewReader` succeeds.

The iterator is created with optional test-key block-property filters, randomized filter-block use (`AlwaysUseFilterBlock` or `NeverUseFilterBlock`), `MakeTrivialReaderProvider`, and `AssertNoBlobHandles`. A metamorphic weighted deck chooses among `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, and `Prev`. Operation runners skip invalid direction/state transitions, ensuring exactly one valid operation per loop iteration.

Before and after each operation, the test compares the injected-error counter. If an error was injected, the test asserts the iterator did not return a KV and that `it.Error()` is non-nil; otherwise it logs the latest operation and key.

## State and Persistence Behavior
The generated SSTable is persisted in memfs and read through Pebble's normal object-storage readable path. The test exercises persistent encodings across randomized table formats, index layouts, filter blocks, block property metadata, key schemas, point key kinds, sequence numbers, and values. It intentionally does not persist range deletion or range-key data.

Iterator state tracked in `opRunner` mirrors API preconditions: `Next` is only run after reverse positioning and not after `SeekPrefixGE`; `NextPrefix` requires a valid forward position; `Prev` is not run from an already reverse-exhausted state.

## Dependencies and Integration Points
- Uses `vfs.NewMem`, `objstorage.NewSimpleReadable`, and `objstorageprovider.NewFileWritable`.
- Uses `errorfs.Toggle`, `Counter`, and random injector to simulate read failures in the storage layer.
- Uses `testkeys` comparer/keyspace and `colblk.DefaultKeySchema` for suffix-rich keys and column-block compatibility.
- Integrates with table filters (`bloom`), block stats (`block.ReadEnv`), block property filters, and value-block reader provider setup.
- Uses `metamorphic.Weighted` for reproducible operation distributions.

## Risks and Edge Cases
- The test checks error surfacing, not equivalence with a no-error oracle; wrong successful results without injected errors may pass.
- It only tests point iterators; comments note range deletion and range-key iterators are not covered.
- Error injection probability and random operation selection make this high-value but non-exhaustive; failures require seed logs for reproduction.
- The writer randomization uses very small and very large block/index sizes, increasing coverage of single-level/two-level and boundary seek paths.

## Test Signals
This is a broad stochastic signal over read-time failure handling for the iterator state machine. It is especially relevant to lazy index/data/filter loading, `TrySeekUsingNext`, prefix seeks with bloom filters, block-property skipping, and reverse/forward direction changes. The saved stack trace on injection helps identify swallowed-error paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/random_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader.go -->
# sources/storage-engines/pebble/sstable/reader.go

## Purpose
`reader.go` implements the SSTable `Reader`, the object that owns file-level metadata, block handles, table attributes, comparer/schema selection, and block-reading entry points. It constructs point and range iterators, reads metadata/properties/layout information, validates block checksums, estimates disk usage, and provides value-block access for lazy values.

## Important APIs, Types, and Functions
- `Reader` stores `block.Reader`, table format, block handles for index/meta/filter/range/value/properties/blob/tiering blocks, comparer, key schema, attributes, user properties, table filter, and cached error state.
- `ReadEnv` carries virtual SSTable parameters, shared-ingestion mode, block read environment/stats, and internal bounds used by synthetic-key optimization.
- `IterOptions` configures point iterator bounds, transforms, block property filters, filter-block size policy, read env, value/blob readers, and maximum-suffix property.
- `NewReader` opens and validates the file footer, metaindex, properties, table attributes, comparer, merger, and key schema.
- `NewPointIter`, `NewIter`, and `NewCompactionIter` choose single-level vs two-level and row vs column iterators.
- `NewRawRangeDelIter` and `NewRawRangeKeyIter` read range-keyspan blocks and apply virtual truncation/foreign-SST transformation when needed.
- `ReadPropertiesBlock`, `Layout`, `ValidateBlockChecksums`, `EstimateDiskUsage`, and `CollectBlockEntries` expose metadata and block-usage functionality.
- `MakeTrivialReaderProvider` adapts a long-lived reader into `valblk.ReaderProvider`.

## Control Flow
`NewReader` verifies the input readable, applies default options, uses a preallocated read handle, reads the footer, initializes `blockReader`, and records top-level handles. It reads the metaindex and properties with metadata buffer pools to avoid polluting the block cache. It derives `Attributes` from properties and verifies footer attributes for Pebble v7+. It then resolves the comparer, merger, and column key schema, recording errors on the reader and returning failure when metadata is inconsistent or unknown.

`newPointIter` dispatches by `AttributeTwoLevelIndex` and `tableFormat.BlockColumnar()` to construct the matching row/column single- or two-level iterator. `newCompactionIter` disables filter-block use, applies shared-ingested obsolete-point hiding, constructs the same iterator family, and calls `SetupForCompaction` to alter read-handle behavior.

Block reading methods are thin wrappers around `blockReader.Read` with the correct `blockkind` and optional metadata initialization functions. Metadata initialization is needed for columnar index/data/keyspan blocks.

`readAndDecodeMetaindex` reads the metaindex block, validates its decoded size, and decodes either the older row format or Pebble v6+ columnar metaindex. `initMetaindexBlocks` extracts known meta block handles, rejects obsolete v1 range-deletion blocks, and binds the first matching filter decoder to `tableFilter`.

`Layout` walks the top-level index and, when needed, second-level index blocks, building a `Layout` with all data, index, filter, range, value, properties, metaindex, blob, and tiering block handles. `ValidateBlockChecksums` sorts all present blocks by offset and reads them sequentially to verify checksums. `EstimateDiskUsage` and `CollectBlockEntries` walk index entries without reading data blocks, scaling estimates for value-block overhead using properties.

## State and Persistence Behavior
`Reader` persists no new data itself; it interprets the immutable SSTable file. It eagerly reads file metadata required to safely operate and lazily reads most data/index/filter/value blocks through iterator paths. `Close` closes the underlying `blockReader`, preserves the first error, and then marks the reader with `errReaderClosed` so later operations fail.

Persistent compatibility hinges on footer format, metaindex block names, properties fields, filter-family names, range deletion/key block names, value-block index handles, and column key schema names. `UserProperties` from the properties block are exposed on the reader and later used by iterator synthetic-key optimization.

## Dependencies and Integration Points
- Depends on `objstorage` and `block.Reader` for storage IO and caching.
- Integrates with `rowblk`/`colblk` for index/data/keyspan decoding.
- Integrates with `keyspan` and `rangekey` for range deletion/key iteration and virtual shared-SST transformations.
- Integrates with `valblk` for external value blocks and lazy values.
- Uses `virtual.VirtualReaderParams` to constrain bounds for virtual SSTables.
- Uses `ReaderOptions` comparers, mergers, filter decoders, key schemas, cache/file numbers, and init read stats.

## Risks and Edge Cases
- Unknown comparer, merger, or column key schema makes the reader unusable; unknown column key schema currently panics after setting `r.err`.
- Metadata buffer pools must be released correctly to avoid retaining large blocks.
- Two-level index layout and disk-usage estimation rely on correct index separator semantics and block-handle decoding.
- Virtual SSTables require careful bounds constraining for point and range-key iterators, especially shared-ingested range key sequence transformation.
- `ReadPropertiesBlock` intentionally bypasses the block cache; callers expecting cache warm-up will not get it.
- `NewReader` leaves the readable open on error; callers retain cleanup responsibility as documented.

## Test Signals
The adjacent tests exercise reader creation from fixtures and memfs SSTables, lazy iterator error paths, random read-error injection, bloom-filter behavior, concurrent iterator creation, resource cleanup, boundary tables, and treesteps integration. Broader repository tests likely cover layout/checksum/disk-usage APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_common.go -->
# sources/storage-engines/pebble/sstable/reader_common.go

## Purpose
`reader_common.go` provides small public aliases and constants shared by SSTable readers and callers. It exposes block and block-iterator transform types through the `sstable` package and defines the filter-block size policy used by point iterators.

## Important APIs, Types, and Functions
- `FilterBlockSizeLimit` is a `uint32` policy controlling whether an existing bloom/filter block may be used.
- `NeverUseFilterBlock` disables filter-block checks.
- `AlwaysUseFilterBlock` allows filter-block use regardless of block size.
- Type aliases re-export `block.BufferPool`, `blockiter.Transforms`, `blockiter.FragmentTransforms`, `blockiter.SyntheticSeqNum`, `SyntheticSuffix`, `SyntheticPrefix`, and `SyntheticPrefixAndSuffix`.
- `NoTransforms` and `NoFragmentTransforms` expose default transform values.
- `MakeSyntheticPrefixAndSuffix` delegates to `blockiter.MakeSyntheticPrefixAndSuffix`.
- `NoSyntheticSeqNum` exposes the zero value that disables synthetic sequence numbers.

## Control Flow
There is no complex control flow. The file establishes names and constants. `MakeSyntheticPrefixAndSuffix` is the only function and simply constructs a combined synthetic prefix/suffix transform value through `blockiter`.

## State and Persistence Behavior
No mutable state is stored. These aliases influence read-time interpretation of persisted keys: synthetic prefix/suffix and synthetic sequence transforms can alter keys surfaced by iterators without modifying the SSTable. `FilterBlockSizeLimit` controls whether persisted filter blocks are consulted.

## Dependencies and Integration Points
- Used by `reader.go` through `IterOptions.FilterBlockSizeLimit`, `NoReadEnv`, and iterator constructors.
- Used by range deletion/key iterator creation through fragment transforms.
- Bridges callers outside `sstable` to lower-level `block` and `blockiter` transform APIs without importing those packages directly.

## Risks and Edge Cases
- `AlwaysUseFilterBlock` is `math.MaxUint32`; a filter block larger than that cannot exist under the type, so all present filters pass the size check.
- Transform aliases expose lower-level semantics; misuse of synthetic transforms can surface keys that differ from persisted bytes, so callers must understand how bounds and virtual SSTables interact.
- These definitions are intentionally thin; behavior changes occur in `blockiter` and iterator code rather than here.

## Test Signals
This file is indirectly covered by iterator, range-key, compaction, and virtual-SSTable tests that pass `NoTransforms`, synthetic transforms, and filter-block policies through `IterOptions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter.go -->
# sources/storage-engines/pebble/sstable/reader_iter.go

## Purpose
`reader_iter.go` defines the shared iterator interfaces, generic constraints, pool aliases, and invariant finalizers for SSTable point iterators. It also documents the key positioning and exhaustion invariants used by single- and two-level iterators.

## Important APIs, Types, and Functions
- `dataBlockIterator[D]` constrains embedded data block iterators to `blockiter.Data` plus metadata-returning variants and a pointer-to-`D` shape.
- `indexBlockIterator[I]` constrains embedded index iterators to `blockiter.Index` plus pointer-to-`I`.
- `Iterator` extends `base.InternalIterator` with `NextPrefix` and `SetCloseHook`.
- Type aliases instantiate single-level and two-level iterators for row blocks and column blocks.
- Four `sync.Pool` values recycle row/column single/two-level iterator instances.
- `init` initializes pools and optional invariant finalizers.
- `checkSingleLevelIterator` and `checkTwoLevelIterator` finalizers detect leaked block handles.

## Control Flow
The long package comment is part of the functional contract: it defines bounds-exhausted, data-exhausted, local vs global exhaustion, and the safe conditions for monotonic-bounds and `TrySeekUsingNext` optimizations.

At initialization, each pool constructs the appropriate iterator type, stores a pool pointer, and when invariant finalizers are enabled registers a finalizer that checks embedded data and index block handles are not still valid. The finalizer prints to stderr and exits on leaked handles.

The checker functions cast pooled objects back to concrete generic iterator types and inspect `Handle().Valid()` on embedded data/index iterators. The two-level checker inspects the embedded second-level single-level iterator.

## State and Persistence Behavior
This file manages in-memory iterator lifecycle, not persisted data. Pooling means iterator structs retain some fields across uses unless reset by close logic, so the reset boundary in `reader_iter_single_lvl.go` and two-level code must stay synchronized with fields added here and there.

The documented exhaustion state is critical persistent-read behavior: incorrect exhaustion tracking can skip or duplicate keys while reading immutable SSTables, especially when bounds, block-property filters, and direction changes interact.

## Dependencies and Integration Points
- Integrates with `base.InternalIterator`, `blockiter`, `rowblk`, and `colblk`.
- Pool aliases are used by `reader.go` constructors and single/two-level iterator implementations.
- Finalizers depend on `internal/invariants` and are intended for debug/test builds.
- `SetCloseHook` supports file-cache reference counting around `Reader` lifetimes.

## Risks and Edge Cases
- The optimization invariants are subtle; conflating bound exhaustion with data exhaustion previously caused bugs, and future changes must preserve the distinction.
- Pool reuse plus generics requires careful zeroing and handle closure, or old state/read handles can leak into new iterator uses.
- Finalizer failures exit the process, which is appropriate for invariant builds but severe if accidentally enabled in inappropriate environments.
- `NextPrefix` is a Pebble extension beyond `InternalIterator`; wrappers must preserve it when adapting iterators.

## Test Signals
`reader_iter_test.go` exercises lazy-loading lifecycle, resource cleanup, bloom-filter preservation, and concurrent iterator use. `random_test.go` stresses the documented positioning invariants under many operations and injected errors. `reader_iter_treesteps_test.go` validates tree-step introspection over iterator trees.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_single_lvl.go -->
# sources/storage-engines/pebble/sstable/reader_iter_single_lvl.go

## Purpose
`reader_iter_single_lvl.go` implements the generic single-level SSTable point iterator for both row-oriented and column-oriented data blocks. It owns lazy top-level index loading, data block loading, bounds handling, bloom-filter prefix seeks, block-property filtering, virtual SSTable bounds, synthetic-key optimization, value-block reading, iterator pooling, and debug tree-step output.

## Important APIs, Types, and Functions
- `exhaustedBounds` distinguishes not exhausted, lower-bound exhausted, upper-bound exhausted, and prefix exhausted states.
- `singleLevelIterator[I, PI, D, PD]` stores context, comparer, bounds, block-property filters, reader, read handles, error state, read env, optimization state, filter state, transforms, prefix state, maximum-suffix synthetic-key state, embedded index/data iterators, and pool metadata.
- Constructors `newColumnBlockSingleLevelIterator` and `newRowBlockSingleLevelIterator` initialize row/column-specific data iterators and value-block readers.
- Positioning methods implement `SeekGE`, `SeekGEWithMeta`, `SeekPrefixGE`, `SeekLT`, `First`, `FirstWithMeta`, `Last`, `Next`, `NextWithMeta`, `NextPrefix`, and `Prev`.
- Helpers include `ensureIndexLoaded`, `loadDataBlock`, `resolveMaybeExcluded`, `skipForward`, `skipBackward`, `virtualLast`, `bloomFilterMayContain`, and reset/close methods.

## Control Flow
Construction calls `init`, which records options, constrains bounds for virtual SSTables, creates preallocated read handles for index/filter and data reads, records transforms and maximum suffix property, and deliberately does not read the index block. Row and column constructors perform format assertions, install value-block readers when table attributes require them, and initialize embedded block iterators.

`ensureIndexLoaded` is the lazy gate. The first positioning operation reads the top-level index block through `reader.readTopLevelIndexBlock`, initializes the embedded index iterator, records `indexLoaded`, and leaves later operations to reuse it.

`loadDataBlock` requires a loaded and valid index. It decodes the current index entry, avoids reloading the same valid data block, invalidates stale data on block changes, consults block-property filters, resolves bound-limited maybe-excluded blocks, reads the data block, initializes the embedded data iterator, and computes per-block lower/upper bounds.

Forward seeks clear prefix state for `SeekGE`, optionally clamp to virtual lower bounds, handle `TrySeekUsingNext` and monotonic bounds optimizations, seek the index on the slow path, load a block, seek within it, enforce upper bounds, and call `skipForward` when a block is exhausted or irrelevant. Reverse seeks mirror this through `SeekLT`, lower-bound checks, and `skipBackward`.

`SeekPrefixGE` sets `i.prefix`, handles synthetic-key optimization when a maximum-suffix property can safely defer the real seek, checks bloom filters when enabled, preserves loaded data blocks on clean bloom misses, and then delegates to `seekGEHelper` with prefix-aware data-block seeking. `Next` resolves a synthetic key by performing the deferred seek before normal advancement.

`First` and `Last` perform absolute positioning with special handling for configured lower/upper bounds and virtual inclusive upper bounds. `NextPrefix` advances by prefix successor, first within the current data block and then by index seek/step.

`Close` delegates to `closeInternal`, closes embedded iterators and read handles, releases block-property filterers, closes value-block readers, calls the close hook, returns the first error, resets reusable fields, and returns the iterator to its pool.

## State and Persistence Behavior
The iterator reads immutable SSTable state but maintains substantial transient positioning state. Important state includes current index/data block handles, `err`, prefix mode, exhausted-bound reason, last bloom result, loaded-index flag, per-block bounds, read handles, value-block reader, and synthetic-key buffers.

Persistent behavior depends on index separators, block handles with properties, filter blocks, table properties, value-block indexes, and virtual SSTable internal bounds. Synthetic-key optimization uses reader `UserProperties` and `MaximumSuffixProperty` to return a temporary `InternalKeyKindSyntheticKey` with `SeqNumMax`; the real seek is deferred until the synthetic key is advanced.

## Dependencies and Integration Points
- Depends on `Reader` block read wrappers and table metadata.
- Embeds `rowblk` or `colblk` index/data iterators through generic constraints from `reader_iter.go`.
- Uses `block.ReadEnv` and `objstorage.ReadHandle` for IO, stats, and readahead behavior.
- Uses `BlockPropertiesFilterer` to skip irrelevant blocks.
- Uses `tableFilterReader` through `bloomFilterMayContain`.
- Uses `valblk.MakeReader` and implements value-block reads for lazy values.
- Integrates with virtual SSTables through `virtual.VirtualReaderParams` in `ReadEnv`.
- Integrates with `treesteps` for visual debugging.

## Risks and Edge Cases
- Bounds, prefix, and data-exhaustion states are intentionally distinct; collapsing them can make `TrySeekUsingNext` incorrectly return nil or skip later prefixes.
- Bloom-filter misses preserve loaded data blocks and do not position the iterator; callers must respect the API restriction on following operations.
- Block-property filters can skip blocks without loading them; reverse iteration needs extra index stepping to determine whether maybe-excluded blocks are wholly within filter bounds.
- Virtual SSTable bounds require extra lower-bound enforcement in `skipForward` after reverse scans because skipped blocks may become relevant after filter changes.
- `resetForReuse` uses unsafe byte clearing up to `clearForResetBoundary`; field placement must be maintained carefully.
- Synthetic-key optimization is only safe when prefix containment and maximum-suffix ordering invariants hold.
- Lazy index loading shifts IO errors from construction to first use, so callers must check `Error()` after iterator operations.

## Test Signals
`reader_iter_test.go` directly covers lazy index-load errors, row/column basic iteration, seek operations, resource cleanup, concurrent independent iterators, boundary cases, stress operations, and bloom-miss non-invalidation for single- and two-level iterators. `random_test.go` adds randomized table formats and injected IO failures. `reader_iter_treesteps_test.go` checks treesteps recording for iterator operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_single_lvl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_test.go -->
# sources/storage-engines/pebble/sstable/reader_iter_test.go

## Purpose
`reader_iter_test.go` validates lazy-loading iterator behavior, resource cleanup, concurrent iterator use, boundary cases, stress operations, and bloom-filter optimization behavior for single-level and two-level SSTable iterators.

## Important APIs, Types, and Functions
- `TestIteratorErrorOnInit` checks that lazy index-read errors surface on first iterator use.
- `TestLazyLoadingBasicFunctionality`, `TestLazyLoadingSeekOperations`, and helper functions build small SSTables and verify forward/reverse/seek behavior.
- `TestLazyLoadingResourceManagement`, `TestLazyLoadingResourceCleanup`, and `testMemoryLeakPrevention` exercise close paths and pool/read-handle cleanup.
- `TestLazyLoadingConcurrentAccess` runs many independent iterators against the same reader concurrently.
- `TestLazyLoadingBoundaryConditions` covers empty, single-key, and two-key tables.
- `TestLazyLoadingStressOperations` repeats mixed operations thousands of times.
- `controllableFilterDecoder`, `newControllableFilterPolicy`, `createTestSST`, and `createTestSSTWithOptions` build filter-controlled SSTables.
- Bloom tests cover single-level, two-level, and edge cases around bloom misses.

## Control Flow
The lazy error test writes a one-key SSTable, wraps the file with `errorfs.Toggle`, opens the reader before enabling injection, then creates row single-level or two-level iterators repeatedly. Since index loading is lazy, construction may succeed; `First` should return nil and `Error` should report the injected error.

Basic tests generate deterministic sorted keys, write memfs SSTables in row and column table formats with and without bloom filters, then iterate forward and backward. Seek tests assert `SeekGE` finds exact keys and `SeekLT` returns prior keys.

Resource tests create and close many iterators, close early before/after positioning, and use GC plus memory stats as a heuristic leak detector. Concurrent tests create one iterator per goroutine and perform independent operations against a shared reader.

Bloom tests install a decoder whose `MayContain` return is controlled. They first load a data block, then call `SeekPrefixGE` with a missing prefix. On clean bloom misses, they assert the embedded data iterator remains valid/not invalidated. Two-level tests force partitioning with small block/index sizes and inspect `iter.secondLevel.data`.

## State and Persistence Behavior
Tests persist SSTables in `vfs.NewMem` and reopen them through reader construction. They exercise both writer-side filter policy emission and reader-side filter decoder selection. The tests inspect iterator internal state because they are in package `sstable`, especially `data.Valid`, `IsDataInvalidated`, and two-level second-level state.

## Dependencies and Integration Points
- Uses `NewWriter`, `newReader`, `NewPointIter`, row/two-level constructors, and object-storage file wrappers.
- Uses `block.BufferPool` and `base.InternalIteratorStats` to match production iterator environments.
- Uses `bloom.FilterPolicy`, custom filter decoders, `errorfs`, `vfs`, and `objstorageprovider`.
- Exercises `MakeTrivialReaderProvider` for value-block/lazy-value compatibility even when values are inline.

## Risks and Edge Cases
- Some tests use internal fields and are tightly coupled to iterator implementation details; refactors may need test updates without changing public behavior.
- Memory leak detection is heuristic and may be noisy if runtime allocation behavior changes.
- `controllableFilterDecoder` ignores `mayContainError`; it simulates hit/miss but not decoder errors.
- Concurrent access is safe because each goroutine owns its iterator; it does not make a single iterator concurrently safe.
- Stress operations call `Next`/`Prev` after arbitrary positioning; current iterator API tolerates many but not all invalid sequences, so the test starts positioned and uses a fixed operation cycle.

## Test Signals
The file provides strong regression coverage for lazy index loading, first-use error propagation, data-block preservation on bloom misses, row/column basic operation parity, iterator cleanup, pool reuse, and two-level bloom paths. It complements `random_test.go`, which has broader randomized IO-failure coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_treesteps_test.go -->
# sources/storage-engines/pebble/sstable/reader_iter_treesteps_test.go

## Purpose
`reader_iter_treesteps_test.go` verifies treesteps recording support for SSTable iterators. It builds test SSTables from datadriven input, runs iterator commands, and returns visualization URLs representing recorded iterator tree steps.

## Important APIs, Types, and Functions
- `TestIterTreeSteps` skips when `treesteps.Enabled` is false and otherwise runs single-level and two-level datadriven suites.
- `testIterTreeSteps` manages a `Reader` across datadriven commands and supports `build` and `iter-treesteps`.
- `runIterTreeStepsCmd` creates an iterator, starts treesteps recording, delegates operation execution to `runIterCmd`, finishes recording, and returns the visualization URL.

## Control Flow
The top-level test runs two subtests against `testdata/treesteps_single_level_iter` and `testdata/treesteps_two_level_iter`. The datadriven runner handles `build` by closing any prior reader, creating `WriterOptions` with `testkeys.Comparer` and `TableFormatMax`, and calling `runBuildCmd`. It handles `iter-treesteps` by requiring a reader, opening a normal `NewIter`, recording with a position string normalized for path separators, running iterator commands, and returning `steps.URL().String()`.

## State and Persistence Behavior
The test state is the current `Reader`, rebuilt by datadriven `build` commands and closed at test completion. It creates regular SSTable data through shared test helpers, then observes in-memory iterator state transitions through treesteps. No production persistence format is changed.

## Dependencies and Integration Points
- Depends on `github.com/cockroachdb/datadriven` for test script execution.
- Uses `internal/treesteps` hooks implemented by iterators, including `TreeStepsNode` from `reader_iter_single_lvl.go` and corresponding two-level support.
- Uses `runBuildCmd` and `runIterCmd` from SSTable test infrastructure.
- Uses `testkeys.Comparer` to build keyspaces with Pebble test-key semantics.

## Risks and Edge Cases
- The test is build/config dependent and skips entirely when treesteps are disabled.
- It validates URL output rather than deeply asserting every internal step in Go code; expected datadriven files carry the meaningful golden signal.
- Since it uses `TableFormatMax`, behavior may shift when the maximum table format changes, requiring golden updates.
- Iterator close is not explicit in `runIterTreeStepsCmd`; test helper behavior and leak tests elsewhere need to catch resource issues.

## Test Signals
This is a focused debug-observability signal. It ensures iterator tree-step instrumentation remains wired for both single-level and two-level iterators and that datadriven iterator commands can generate visualization output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/reader_iter_treesteps_test.go -->
