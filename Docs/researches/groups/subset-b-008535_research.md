# subset-b-008535 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/keyspan_probe_test.go -->
# sources/storage-engines/pebble/keyspan_probe_test.go

Purpose: this test helper file provides a programmable wrapper around `keyspan.FragmentIterator` so tests can inject iterator errors, substitute returned spans, and log range-span iterator operations. It is explicitly duplicated from internal keyspan datadriven helpers until the shared keyspan types can move to a common test package.

Important APIs/types/functions: `keyspanProbe` is the mutation hook interface. `parseKeyspanProbes` and `attachKeyspanProbes` build wrapper chains from a small DSL. `keyspanProbeContext` carries the operation under inspection through `keyspanOp`, including operation kind, seek key, returned span, and error. Probe implementations include `errorProbe`, `ifProbe`, `returnSpan`, `noop`, and `loggingProbe`. Predicate/value DSL support is provided through `equal`, `keyspanOpKind`, `bytesConstant`, `startKey`, and `seekKey`. `probeKeyspanIterator` implements `keyspan.FragmentIterator` by forwarding to a child iterator and then invoking the configured probe.

Control flow: every iterator method constructs a `keyspanOp`, optionally asks the wrapped iterator for the real result, and then calls `handleOp`, which installs the operation into the context and lets the probe rewrite `Span` or `Err`. Conditional probes run nested probes based on DSL predicates; logging probes observe the post-child, pre-rewrite state passed to them in wrapper order. `WrapChildren`, `SetContext`, `TreeStepsNode`, and `Close` preserve integration with normal iterator plumbing and tracing.

State and persistence behavior: state is transient and test-local. The wrapper stores only the child iterator, the probe, and mutable probe context. It performs no durable writes. Returned `returnSpan` spans reference parsed test values, so callers should treat them as test-controlled fixtures, not production-owned span memory.

Dependencies and integration points: depends on `internal/dsl` for parser composition, `internal/keyspan` for span iterator contracts, `treesteps` for iterator tree introspection, and Go reflection for predicate equality. It is used by iterator tests that need deterministic error injection or abnormal span behavior.

Risks and test signals: because this code can violate iterator invariants by design, misuse can hide production bugs or produce unrealistic states. `Close` ignores injected close errors after probing, matching test-helper semantics rather than production error propagation. The main test signal is whether higher-level range-key/range-delete iterators respond correctly to injected nil spans, errors, reordered results, and logging traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/keyspan_probe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_checker.go -->
# sources/storage-engines/pebble/level_checker.go

Purpose: this file implements `DB.CheckLevels`, an expensive validation pass for Pebble databases. It checks LSM level invariants for point keys and range tombstones, verifies internal key ordering, exercises merge operand processing, validates blob value liveness metadata, and cross-checks range-key table metadata.

Important APIs/types/functions: `CheckLevelsStats` exposes counts of visible points and tombstones. `DB.CheckLevels` captures a referenced read state and visible sequence number, initializes blob-file mapping and block read environment, and calls `checkLevelsInternal`. `simpleMergingIter` is a stripped-down multi-level merge iterator for validation. `checkRangeTombstones`, `addTombstonesFromIter`, `fragmentUsingUserKeys`, and `iterateAndCheckTombstones` implement tombstone consistency checks. `checkRangeKeyMetadata`, `gatherBlobHandles`, `performValidationForSSTable`, and `validateBlobValueLiveness` validate table metadata and blob liveness blocks. `simpleMergingIterHeap` orders per-level point keys by user key and descending trailer.

Control flow: `checkLevelsInternal` first builds one validation level per mutable/immutable memtable, L0 sublevel, and non-empty L1+ level. It wraps point iterators with range-deletion interleaving so point visibility can be checked against lower-level tombstones. `simpleMergingIter.step` repeatedly processes the heap root, verifies visible point ordering and level ordering for identical user keys, advances the source iterator, and finalizes active merge series at key changes or exhaustion. Phase two gathers every visible range tombstone, fragments all tombstones at all start/end boundaries, sorts by start key and descending sequence number, and ensures lower-level tombstones do not appear with newer sequence numbers. Later phases scan SSTables for blob references and range keys and compare actual contents with table metadata.

State and persistence behavior: the checker reads a stable snapshot of the current read state and memtables but does not mutate database contents. It opens and closes many iterators and readers through `newIters` and `fileCache`. It allocates in-memory tombstone slices, blob-reference maps, and block buffers; blob fetcher state is scoped to the validation call and closed on exit.

Dependencies and integration points: integrates with `DB` read-state management, memtable flushables, `levelIter`, manifest versions/sublevels, range deletion interleaving, SSTable readers, block buffer pools, blob file mappings, and region-tree range-key metadata. It relies on configured comparer, merge operator, logger, and table iterator factory.

Risks and test signals: the pass is intentionally expensive and can hold all tombstones in memory. Correctness depends on iterator close/error handling and on not missing range-key-only or blob-backed tables. Failure messages include table numbers and levels, making corruption diagnosis practical. Tests cover staged real DBs, constructed invariant violations, merge failures, unfragmented tombstones, and blob liveness mismatch cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_checker_test.go -->
# sources/storage-engines/pebble/level_checker_test.go

Purpose: this test file validates the `CheckLevels` corruption checker across normal fixture databases, synthetic LSM layouts that intentionally violate invariants, merge-operator error paths, and blob liveness block validation.

Important APIs/types/functions: `TestCheckLevelsBasics` opens staged fixture DBs and asserts `DB.CheckLevels(nil)` succeeds. `failMerger` is a test `ValueMerger` that can fail during `MergeOlder` or `Finish` while tracking close balance. `TestCheckLevelsCornerCases` builds raw SSTables in an in-memory filesystem and feeds them through `checkLevelsInternal` with a custom `newIters`. `TestPerformValidationForSSTableFailures` constructs encoded blob-reference liveness blocks and verifies `performValidationForSSTable` rejects specific mismatches.

Control flow: the corner-case datadriven test parses `define` commands into logical levels, table metadata, raw SSTable contents, and optional writer modes like unfragmented range tombstones or disabled key-order checks. The `check` command wraps those files in a test `manifest.Version`, installs the requested merger, and runs `checkLevelsInternal`. The blob tests create a small reference-liveness block and compare decoder output against hand-built `referenced` maps for row-count, dangling-reference, bitmap, size, missing-reference, and success cases.

State and persistence behavior: all table files live in `vfs.NewMem`; readers are retained in a slice indexed by table number and closed by defer. The test intentionally constructs states production code would usually prevent, so it skips under invariants. It does not persist data beyond the test process.

Dependencies and integration points: exercises `sstable.RawWriter`, manifest metadata construction, object storage wrappers, range tombstone fragmentation, test key comparer formatting, invalidating iterators, blob liveness encoders/decoders, and the production `checkConfig` path. The custom iterator factory mimics table-cache behavior enough to test the checker without opening a full `DB`.

Risks and test signals: the tests are strong at negative-path validation because they can synthesize bad ordering, bad tombstone fragmentation, and merge failures. They depend on exact error-message substrings and table-number formatting, so diagnostic text changes can require fixture updates. They also deliberately bypass invariant checks; running with invariants enabled skips the corner cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_checker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_iter.go -->
# sources/storage-engines/pebble/level_iter.go

Purpose: `levelIter` provides the v1 internal iterator over all SSTables in a single LSM level, L0 sublevel, or flushable ingest layer. It lazily opens one table iterator at a time, applies iterator bounds, skips irrelevant files, interleaves range-deletion boundaries when required by merging iteration, and supports point-key operations used by compaction and user iteration.

Important APIs/types/functions: `newLevelIter` and `init` configure comparer, manifest `LevelIterator`, table iterator factory, bounds, filters, layer, and internal read options. `initRangeDel` enables range-deletion interleaving and optional transfer of a separate range-deletion iterator to a `rangeDelIterSetter`. `initCombinedIterState` and `maybeTriggerCombinedIteration` coordinate lazy switching to combined point/range-key iteration. Search and load helpers include `findFileGE`, `findFileLT`, `initTableBounds`, and `loadFile`. Iterator methods implement `SeekGE`, `SeekGEWithMeta`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `Prev`, `SetBounds`, `SetContext`, `Span`, `Error`, `Close`, `TreeStepsNode`, `FirstWithMeta`, and `NextWithMeta`.

Control flow: absolute seeks use the manifest iterator to find a candidate file, sometimes replacing binary search with bounded `Next`/`Prev` steps for `TrySeekUsingNext` or `RelativeSeek`. `loadFile` closes the old iterator, skips files outside bounds or without point keys, detects lazy combined-iteration triggers, opens table iterators for point keys and optionally range deletions, wraps them in `keyspan.InterleavingIter`, and records the current file. If a table iterator returns nil, `skipEmptyFileForward` or `skipEmptyFileBackward` advances to neighboring files unless an in-table bound, prefix boundary condition, or exhaustion prevents it.

State and persistence behavior: the iterator is mutable and short-lived. It pins at most one table iterator, stores current file/bounds/prefix/error/exhaustion direction, and forwards context updates. It does not persist data. Close propagates iterator errors and clears range-delete setter state.

Dependencies and integration points: sits between `mergingIter`/compactions and table-cache `newIters`. It depends on manifest level ordering, comparer prefix splitting, range deletion interleaving, block property filters, treesteps tracing, and invariants checks. `Span` exposes the currently interleaved tombstone to callers that need range-delete coverage.

Risks and test signals: correctness is sensitive to bounds, exclusive sentinel keys, prefix seeks, direction changes after exhaustion, and `TrySeekUsingNext` heap invariants. Lazy combined-iteration trigger logic must scan skipped files that may contain range keys. Datadriven tests cover fake iterators, real SSTables, range-delete interleaving, file loading bounds, iterator position reporting, and benchmarks for seek/next/prev patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_test.go -->
# sources/storage-engines/pebble/level_iter_test.go

Purpose: this file provides datadriven tests and benchmarks for v1 `levelIter`, covering file selection, per-table bounds, range-deletion interleaving, prefix seek behavior, and performance-sensitive seek/scan patterns.

Important APIs/types/functions: `TestLevelIter` uses fake per-file iterators to test basic commands and table-load bounds. `levelIterTest` builds real SSTables in memory and exposes `newIters`, `runClear`, and `runBuild`. `TestLevelIterBoundaries` exercises boundary behavior over real SSTables and can save an iterator across commands. `levelIterTestIter` wraps `levelIter` to expose the separate range-delete iterator state to `itertest`. `TestLevelIterSeek` drives seek-focused datadriven cases and iterator stats. `buildLevelIterTables` plus the benchmark functions create multi-file SSTable levels for performance tests.

Control flow: fake tests parse `define` lines into `base.InternalKV` slices and manifest metadata, then run `itertest.RunInternalIterCmd`. Real-SSTable tests parse input into point keys, range deletions, and range keys, write raw SSTables, derive `TableMetadata`, and then instantiate `levelIter` over a sorted `LevelSlice`. Range-delete tests initialize `initRangeDel` with a setter so seeks can also position an external range tombstone iterator. Benchmarks repeatedly perform random seeks, sequential bounded scans, prefix seeks with and without `TrySeekUsingNext`, and forward/backward iteration.

State and persistence behavior: state is held in memory through `vfs.NewMem`, SSTable readers, metadata slices, and optional saved iterator instances. Tests close readers and iterators explicitly. No durable repo state is modified.

Dependencies and integration points: depends on `datadriven`, `itertest`, manifest slices, raw SSTable writer/reader APIs, bloom filters, range deletion and range key encoders, block read stats, object storage file wrappers, and test key comparers.

Risks and test signals: datadriven output is sensitive to iterator formatting and boundary key behavior. The tests are valuable for regressions around skipped files, bound propagation, prefix bloom filtering, range-delete handoff, and lazy file loading. Benchmarks serve as signals for regressions in common CockroachDB-like workloads such as repeated bounded scans and monotonic prefix seeks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_v2.go -->
# sources/storage-engines/pebble/level_iter_v2.go

Purpose: `levelIterV2` is the newer level iterator implementing `iterv2.Iter`. Unlike v1, it exposes both point keys and span boundaries through an `iterv2.InterleavingIter`, producing a continuous keyspace partition across files and gaps so a v2 merging iterator can reason about range deletion coverage without eagerly opening every file.

Important APIs/types/functions: `newLevelIterV2` and `init` configure the iterator. `findFileGE`, `findFileLT`, `initTableBounds`, `fileEndKey`, and `loadFile` select and open per-file iterators. Positioning and movement methods implement `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, and `Prev`. Span/error/lifecycle methods include `Span`, `Error`, `Close`, `SetBounds`, `SetContext`, `TreeStepsNode`, and `String`. Synthetic boundary helpers `maybeEmitBoundaryFwd`, `maybeEmitBoundaryBwd`, and `emitBoundary` represent gaps and bounds without opening a table.

Control flow: each loaded file is assigned an interleaving range from its smallest point key to the next file's smallest point key, extending across gaps. Forward seeks either load the target file or emit a boundary at the next file start or upper bound. Backward seeks load the previous relevant file or emit a lower-bound boundary. `Next` and `Prev` advance within the current per-file `InterleavingIter`; when exhausted, they load the adjacent file or synthesize/clear boundary state. Prefix iteration tracks `prefixExhausted` so the final nonmatching boundary may be returned once and subsequent `Next` returns nil. `TrySeekUsingNext` is supported only in forward, valid-state cases and is disabled when a file changes or the iterator was at a synthetic boundary.

State and persistence behavior: mutable state includes current file, current span, direction, prefix, error, synthetic-boundary flag, scratch boundary KV, and bounds. It closes and reuses a single embedded interleaving iterator. It reads table data through callbacks and does not persist changes.

Dependencies and integration points: integrates with manifest level iteration, `internal/iterv2`, keyspan fragment iterators, table `newIters`, comparer prefix logic, treesteps, and invariants. It deliberately does not support `RelativeSeek` and ignores maximum suffix properties pending investigation.

Risks and test signals: risks cluster around synthetic boundary correctness, gaps between files, bounds falling in gaps, prefix exhaustion, direction changes, and consistency between `files.Current()` and `iterFile`. Randomized and datadriven v2 tests compare against an `iterv2.TestIter` model over point keys, range deletions, and injected file-boundary spans.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_v2_rand_test.go -->
# sources/storage-engines/pebble/level_iter_v2_rand_test.go

Purpose: this randomized test stress-checks `levelIterV2` against the generic `iterv2.CheckIter` model over many generated point/range-delete layouts split across random SSTable boundaries.

Important APIs/types/functions: `TestLevelIterV2Rand` runs 200 random seeds. `runLevelIterV2RandomTest` generates keys/spans, builds SSTables, creates the level iterator, constructs expected model data, and invokes `iterv2.CheckIter`. Helper functions `pickFileBoundaries`, `filterPointKeys`, `clipSpans`, and `createSSTable` create realistic per-file data and metadata.

Control flow: a random key config creates 50 point keys and 10 spans. Span keys are deduplicated by trailer to satisfy SSTable writer constraints. Random boundaries partition the keyspace; points are filtered and spans clipped into each file's half-open range. Empty partitions are skipped. The test opens real SSTable readers, defines a `newIters` callback for point and range-deletion iterators, optionally applies coarse bounds, and compares `levelIterV2` against expected points plus real range deletions plus synthetic file-boundary spans.

State and persistence behavior: all files are written to an in-memory filesystem and readers are closed on exit. The random seed, key config, bounds, file metadata, points, and spans are logged on failure for reproduction. No durable state is changed.

Dependencies and integration points: relies on `iterv2` random data/model checking, `manifest.LevelSlice`, raw SSTable writer/reader APIs, object storage wrappers, range-deletion fragment transforms, and test-key comparers. It tests `levelIterV2` with real SSTable iterators rather than only fake iterators.

Risks and test signals: randomized coverage is especially useful for edge cases around clipped spans, empty gaps, file-boundary spans, lower/upper bounds, and mixed operations. Because it uses random seeds, failures need the logged seed to reproduce. It intentionally models file boundaries as zero-length spans so expected output matches the iterator's synthetic boundary behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_v2_rand_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_v2_test.go -->
# sources/storage-engines/pebble/level_iter_v2_test.go

Purpose: this datadriven test exercises `levelIterV2` with fake per-file iterators, focusing on `TrySeekUsingNext`, prefix seeking, explicit spans, synthetic file boundaries, and bounds handling without the overhead of real SSTables.

Important APIs/types/functions: `TestLevelIterV2` defines an internal `file` struct with point keys, range-deletion spans, and bounds. Its `newIters` callback returns `base.NewFakeIter` for points and `keyspan.NewIter` for spans according to requested `iterKinds`. The datadriven `define` command builds files and manifest metadata; the `iter` command creates `newLevelIterV2` and delegates operation execution to `iterv2.RunIterOps`.

Control flow: input is grouped by `F` markers. Lines containing `:{` are parsed as keyspan spans; other fields are parsed as internal point keys. Metadata extends point bounds with both point keys and range-delete sentinel keys, then initializes physical backing. Each `iter` command optionally applies lower/upper bounds, sorts metadata into a `LevelSlice`, constructs the v2 iterator, and runs scripted operations such as first, next, seek-ge, and seek-prefix-ge.

State and persistence behavior: state is test-local slices of fake files and metadata. The fake iterators enforce per-table bounds but do not touch storage. Iterators are closed after each command.

Dependencies and integration points: depends on `datadriven`, `crstrings`, `iterv2.RunIterOps`, fake internal iterators, manifest metadata, test comparers, and keyspan parsing. It complements the randomized SSTable-backed test by allowing concise, deterministic coverage of edge cases.

Risks and test signals: because fake iterators may not reproduce every SSTable property, this test is best for control-flow semantics rather than block/filter behavior. It provides strong signals for boundary emission, prefix mode, `TrySeekUsingNext` state transitions, and correct metadata construction from spans.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/level_iter_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/logger.go -->
# sources/storage-engines/pebble/logger.go

Purpose: this small public veneer re-exports logging interfaces and defaults from `internal/base` into the Pebble package API.

Important APIs/types/functions: `Logger` aliases `base.Logger`, `DefaultLogger` aliases `base.DefaultLogger`, and `LoggerAndTracer` aliases `base.LoggerAndTracer`.

Control flow: there is no executable control flow beyond package initialization of the exported variable alias. Consumers configure `Options.Logger` or related tracing/logging paths using these exported names while implementation code continues to depend on the base package definitions.

State and persistence behavior: no mutable state is introduced here. `DefaultLogger` points to the base default, which logs through the Go standard library logging implementation.

Dependencies and integration points: this file is part of Pebble's external API compatibility surface. It prevents users from importing internal packages to name logger types. Internal components such as iterators, DB checks, and options use the logger interface for fatal diagnostics and normal logging.

Risks and test signals: risk is primarily API compatibility. Changing these aliases would break downstream code or documentation. There are no dedicated tests in this file; coverage comes from compilation and any tests that instantiate `Options` with custom loggers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/lsm_view.go -->
# sources/storage-engines/pebble/lsm_view.go

Purpose: this file builds a shareable LSM visualization URL for a live `DB`. It translates the current manifest version and selected table details into `internal/lsmview.Data`, then asks the visualization package to encode it into a URL.

Important APIs/types/functions: `DB.LSMViewURL` references the current version under `DB.mu`, constructs an `lsmViewBuilder`, populates levels and keys, builds data, and returns either the generated URL or an error string. `lsmViewBuilder` holds comparer/formatter state, level names, table metadata, sorted key labels, and a scan threshold flag. `InitLevels`, `PopulateKeys`, `Build`, and `tableDetails` perform the conversion.

Control flow: `InitLevels` emits L0 sublevels from newest/display-top order, falls back to an empty `L0`, then appends L1+. `PopulateKeys` collects every table smallest/largest user key, sorts and compacts with the configured comparer, and formats labels. `Build` determines whether table contents should be scanned; up to 100 tables it opens iterators for point keys, range deletions, and range keys to include sample contents. `tableDetails` emits table number, key bounds, size, virtual/backing information, seqnums, synthetic prefix/suffix, point samples, range deletions, and range-key spans with caps on displayed entries.

State and persistence behavior: the method takes a version reference and releases it after building. It opens iterators only for display details and closes them via `CloseAll`. It performs no DB mutation and persists nothing except the returned URL string.

Dependencies and integration points: integrates with manifest table metadata, object-provider lookup for virtual table backing, `tableNewIters`, SSTable iterators, `humanize`, comparer formatting, and `internal/lsmview.GenerateURL`. It is a diagnostics/debugging entry point.

Risks and test signals: scanning is capped by table count and per-detail row limits, but opening many tables can still be nontrivial. Errors are embedded in returned strings/details rather than propagated, matching a diagnostic API. Risk areas include virtual object lookup, nil custom key formatters, iterator close handling, and range-key metadata display.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/lsm_view.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/lsm_view_test.go -->
# sources/storage-engines/pebble/lsm_view_test.go

Purpose: this test verifies `DB.LSMViewURL` through a datadriven fixture that defines databases and compares generated visualization URLs.

Important APIs/types/functions: `TestLSMViewURL` uses `datadriven.RunTest` on `testdata/lsm_view`. The `define` command delegates to `runDBDefineCmd` to create a DB from the fixture, then returns `d.LSMViewURL()`.

Control flow: each fixture command opens a DB with default options, closes it after URL generation, and fails on unknown commands or setup errors. The returned URL becomes the datadriven golden output, indirectly validating level construction, key indexing, table details, and URL encoding stability.

State and persistence behavior: DB lifetime is scoped to each command. Test cleanup relies on `defer d.Close()` and `leaktest.AfterTest`. No persistent repo state is modified by the test.

Dependencies and integration points: exercises the DB definition test harness, datadriven framework, leaktest, and the full `LSMViewURL` path including manifest metadata and URL generation.

Risks and test signals: because generated URLs encode structured data, output churn may occur when display formatting or metadata fields change. The test is narrow but useful as a regression signal that the diagnostic URL remains constructible for representative LSMs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/lsm_view_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/mem_table.go -->
# sources/storage-engines/pebble/mem_table.go

Purpose: this file implements Pebble's mutable in-memory LSM component. A `memTable` stores point keys, range deletion tombstones, and range keys in arena-backed skiplists; supports concurrent application of prepared batches; exposes flushable iterators; and caches fragmented range spans.

Important APIs/types/functions: `memTableEntrySize` estimates arena usage. `newMemTable` and `init` configure comparer functions, arena buffer, skiplists, writer refs, caches, and log sequence number. `prepare` reserves memory and adds a writer ref; `apply` inserts batch records with sequence numbers. Iterator APIs include `newIter`, `newFlushIter`, `newRangeDelIter`, and `newRangeKeyIter`. State/size APIs include `readyForFlush`, `availBytes`, `inuseBytes`, `totalBytes`, `empty`, and `computePossibleOverlaps`. Span caching uses `keySpanFrags`, `constructSpan`, `rangeDelConstructSpan`, and `keySpanCache`.

Control flow: batch application checks the batch sequence number against `logSeqNum`, iterates records, constructs internal keys, and routes range deletes to `rangeDelSkl`, range keys to `rangeKeySkl`, log data to no storage/no seq advance, and point mutations to the point skiplist. After insertion it verifies count/sequence consistency and invalidates span caches when range spans were added. Range span iterators lazily call `keySpanCache.get`, which fragments all raw spans through `keyspan.Fragmenter` exactly once per cache generation using `sync.Once`.

State and persistence behavior: the memtable owns a fixed manual arena buffer until `free`. It is append-only; deletes are represented as internal tombstone records. `reserved` pessimistically tracks committed and inflight memory, while `writerRefs` prevents flushing until queued/inflight writers finish. Span caches are atomic and may be populated from a superseded generation, which is acceptable because counts only increase.

Dependencies and integration points: integrates with `Batch`, `flushable`, commit pipeline writer refs, manual memory accounting, `arenaskl`, range deletion/key encoders, comparer split/equality functions, and overlap computation. Flush and iterator paths consume its internal iterators.

Risks and test signals: risks include memory reservation drift, incorrect writer-ref transitions, sequence-number/count mismatches, cache invalidation races, and misclassification of range-key vs range-delete spans. Invariant checks guard range-deletion iterators from accidentally containing range-key kinds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/mem_table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/mem_table_test.go -->
# sources/storage-engines/pebble/mem_table_test.go

Purpose: this file tests and benchmarks memtable behavior, including basic point operations, iteration bounds, range deletion fragmentation, concurrent tombstone cache invalidation, memory reservation, overlap computation, and iterator performance.

Important APIs/types/functions: helper methods `memTable.get`, `memTable.set`, `memTable.count`, and `ikey` simplify direct test access. Unit tests include `TestMemTableBasic`, `TestMemTableCount`, `TestMemTableEmpty`, `TestMemTable1000Entries`, `TestMemTableIter`, `TestMemTableDeleteRange`, `TestMemTableConcurrentDeleteRange`, `TestMemTableReserved`, and datadriven `TestMemTable`. `buildMemTable` and benchmark functions cover seek, bounded seek, successive seek, next, and prev workloads.

Control flow: basic tests insert keys directly and read through skiplist iterators. Datadriven iterator tests define internal keys and delegate operations to `itertest.RunInternalIterCmd`. Range-delete tests apply batches with monotonically increasing sequence numbers, then scan either point keys or range-delete spans. The concurrent range-delete test launches workers that repeatedly apply non-overlapping tombstones and immediately verify their own span counts through `newRangeDelIter`. Reservation tests call `prepare` without apply to verify pessimistic accounting.

State and persistence behavior: tests allocate memtables in process memory and close batches/iterators where needed. Concurrent tests exercise atomic cache invalidation and lazy fragmentation under write/read races. Benchmarks fill a memtable until arena full, then reuse iterators within the benchmark loop.

Dependencies and integration points: uses datadriven fixtures, batch definition helpers, `itertest`, `arenaskl`, range-key helpers, errgroup concurrency, random generators, and testify requirements. Benchmarks simulate workloads relevant to CockroachDB bounded scans and iterator movement.

Risks and test signals: direct `set` bypasses prepare/apply and is intentionally caveated, so some tests focus on skiplist semantics rather than commit-pipeline semantics. Strong signals include concurrent range tombstone cache correctness, memory accounting after prepare, bounds behavior, and performance regressions in common iterator operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/mem_table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merger.go -->
# sources/storage-engines/pebble/merger.go

Purpose: this public API file re-exports Pebble merge operator types from `internal/base` and provides a small helper to finish merge operations that may request deletion of the merged value.

Important APIs/types/functions: `Merge`, `Merger`, `ValueMerger`, and `DeletableValueMerger` are type aliases. `DefaultMerger` exposes the base default. `finishValueMerger` accepts a `ValueMerger` and `includesBase` flag, then calls `DeletableFinish` when the merger implements `DeletableValueMerger`, otherwise falls back to `Finish`.

Control flow: `finishValueMerger` is a two-branch adapter. In the deletable case it returns value, `needDelete`, closer, and error from `DeletableFinish`; in the regular case it returns value, closer, and error from `Finish`, leaving `needDelete` false.

State and persistence behavior: this file stores no mutable state beyond the exported default alias. Merge state is owned by concrete `ValueMerger` implementations provided by options or tests. Any returned closer must be handled by callers.

Dependencies and integration points: merge operators are used by read paths, compaction, and validation code such as `CheckLevels` to combine merge operands with base values. The type aliases keep the public package API stable while implementation types live under `internal/base`.

Risks and test signals: the main risk is caller mishandling of `needDelete` or `closer`, not this adapter itself. Compatibility risk is high for alias changes. Test coverage is indirect through merge behavior tests and checker tests that use failing mergers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merger.go -->
