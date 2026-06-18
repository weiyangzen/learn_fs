# Research Group subset-b-008534

This grouped report covers Pebble iterator implementation, examples, datadriven iterator history coverage, and iterator unit/benchmark coverage. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/iterator.go -->
# sources/storage-engines/pebble/iterator.go

## Purpose
Implements Pebble's public `Iterator`, the user-facing ordered cursor over visible point keys and range keys. It adapts an internal iterator stack over memtables, indexed batches, sstables, range deletions, range keys, and blob values into stable user-key semantics: hiding obsolete versions, applying tombstones, resolving merges, honoring bounds, supporting prefix seeks, exposing range-key metadata, collecting stats, and closing read-state references.

## Important APIs, Types, And Functions
`Iterator` is the central state object. It owns or references the top-level `internalIterator`, `pointIter`, optional `iteratorRangeKeyState`, optional `iteratorBatchState`, read snapshot/version references, current key/value buffers, lazy value fetchers, bounds buffers, read sampling state, stats, and allocation-pool handles.

`iterPos` records how the internal iterator is positioned relative to the external user key: current forward/reverse, one key ahead/behind, or paused at a limited-iteration boundary. `IterValidityState` distinguishes exhausted, valid, and at-limit states. `lastPositioningOpKind` drives seek optimizations. `IteratorStats`, `IteratorMetrics`, `RangeKeyIteratorStats`, `RangeKeyData`, and `LazyValue` are the main exported observation types.

Public positioning methods include `SeekGE`, `SeekGEWithLimit`, `SeekPrefixGE`, `SeekLT`, `SeekLTWithLimit`, `First`, `Last`, `Next`, `NextWithLimit`, `NextPrefix`, `Prev`, and `PrevWithLimit`. Accessors include `Valid`, `Error`, `Key`, `Value`, `ValueAndErr`, `LazyValue`, `HasPointAndRange`, `RangeBounds`, `RangeKeys`, `RangeKeyChanged`, `Metrics`, `Stats`, and `ResetStats`. Lifecycle/configuration APIs include `Close`, `SetBounds`, `SetContext`, `SetOptions`, `Clone`, `CloneWithContext`, and `CanDeterministicallySingleDelete`.

Internal workhorses are `findNextEntry`, `findPrevEntry`, `nextUserKey`, `prevUserKey`, `mergeForward`, `mergeNext`, `nextPointCurrentUserKey`, `saveRangeKey`, `maybeSampleRead`, `sampleRead`, `maybeRefreshBatchView`, `processBounds`, `invalidate`, `iterFirstWithinBounds`, `iterLastWithinBounds`, `internalNext`, and buffer/pool helpers such as `clearForReuse`, `maybeReuseKeyBuf`, and `rangeKeyBuffers.PrepareForReuse`.

## Control Flow
Forward positioning seeks or steps the internal iterator, then `findNextEntry` loops over internal keys. It skips skipped points, ignores delete/single-delete/delete-sized markers, exposes set values, resolves merge chains through `mergeForward`/`mergeNext`, handles interleaved `RangeKeySet` markers, checks optional exclusive limits, saves range-key state, and converts internal exhaustion or errors into external validity.

Reverse positioning flows through `findPrevEntry`. Because reverse iteration sees older versions in the opposite direction, it clones set values before stepping, accumulates merges with `MergeNewer`, treats deletion markers as clearing visibility, preserves range-key boundary-only positions, and only returns when it has determined the newest visible state for the user key. Direction switches are mediated by `iterPos`: `Next` from a reverse-oriented position first moves the internal iterator back onto or past the current key, while `Prev` from a forward-oriented position moves behind the current key and handles ephemeral synthetic range-key positions specially.

Seek operations reset accumulated errors and prefix mode as appropriate, clamp search keys to configured bounds, update stats, and may use no-op or `TrySeekUsingNext` optimizations when repeated monotonic seeks make reuse safe. `SeekPrefixGE` computes a comparer-defined prefix, enters prefix mode, requires `ImmediateSuccessor` when range keys are enabled, and prevents reverse iteration until another absolute non-prefix positioning operation. Limited iteration returns `IterAtLimit` with paused `iterPos` values, but reverse limited iteration may ignore the limit to ensure overlapping range keys can still be surfaced.

Range-key iteration is interleaved with point iteration. `saveRangeKey` copies the current span's bounds, suffixes, and values into iterator-owned buffers only when stale or changed, updates `RangeKeyChanged` state, and records range-key stats. `HasPointAndRange` and `RangeBounds` distinguish point-only, range-only, and combined positions. `NextPrefix` uses a fast next plus internal `NextPrefix` to skip all keys sharing the current comparer prefix, while rejecting cases where a versioned upper bound would make the operation ambiguous.

`SetBounds` and `SetOptions` always make the iterator appear exhausted externally and require absolute repositioning. Internally, `SetOptions` attempts reuse when options and underlying batch state permit, otherwise closes/rebuilds point and range stacks. Indexed-batch iterators call `maybeRefreshBatchView` to advance their batch snapshot when the mutable batch has changed, update range-del/range-key child iterators if possible, and block unsafe seek no-op optimizations via `batchJustRefreshed`.

`Close` tears down the child iterator stack before releasing read state/version refs, merges pending read-compaction samples into the DB queue, closes blob fetchers and value closers, returns range-key state and iterator allocations to pools, and preserves double-close detection. `CloneWithContext` creates an unpositioned iterator over the same read state or manifest version, optionally refreshing an indexed batch view.

## State And Persistence Behavior
The iterator pins transient DB state through either `readState` or `version`, plus optional indexed-batch snapshot sequence state. It does not itself persist data, but it can enqueue read compaction candidates through `maybeSampleRead`/`sampleRead`; `Close` transfers those candidates into `db.mu.compact.readCompactions` and may schedule asynchronous compaction work.

Current key, bounds, prefixes, range-key data, lazy value buffers, and reverse-iteration values are copied into iterator-owned buffers when the underlying iterator's memory would not remain valid. Bounds use a two-buffer scheme so old and new bounds can coexist during internal iterator bound updates. Large buffers are intentionally not retained when returning allocations to pools.

Errors are sticky for relative movement: absolute positioning clears cached iterator errors, while `Next`/`Prev` return without progress if an error is accumulated. `ValueAndErr` may also store an error and exhaust the iterator if lazy value retrieval fails. `requiresReposition` lets `SetBounds`/`SetOptions` hide an internally reusable position from callers until a fresh absolute positioning call.

## Dependencies And Integration Points
This file sits at the boundary between Pebble's public API and internal iterator stack. It depends on `internal/base` for internal key/value types, lazy values, seek flags, and stats; `keyspan`, `keyspanimpl`, and `rangekeystack` for range-key merging/interleaving; `manifest` and `levelIter` for read sampling; `iterv2` and merging iterators for top-level point iteration; `blob` for separated values; `inflight` for iterator tracking; `bytesprofile` for separated-value retrieval profiling; `treesteps` for debug recordings; and `invariants`/`redact` for assertions and safe formatting.

Construction is performed elsewhere by DB, Batch, Snapshot, and external-iterator creation paths through fields such as `finishInitializingIter`, `tableNewIters`, `newIterRangeKey`, and allocation pools. The iterator honors `IterOptions` features including lower/upper bounds, key-type selection, point/range block-property filters, `SkipPoint`, range-key masking, durable-only reads, L6 filters, and external iter validation.

## Risks And Edge Cases
The highest-risk area is the alignment between `iterPos`, `iterValidityState`, `requiresReposition`, and the actual internal iterator position. Direction switches, limited iteration, merge chains, range-key-only synthetic positions, and SetOptions reuse all depend on these invariants. A stale or over-aggressive seek optimization can skip newly visible batch keys or return an earlier/later key than requested.

Range-key handling is subtle because range-key spans are interleaved at start boundaries, can be surfaced without coincident point keys, can mask point keys, and must still be observed across limited reverse iteration. `RangeKeyChanged` depends on `prevPosHadRangeKey`, `stale`, and `updated`, which the source comments identify as intricate.

Prefix iteration has strict contracts: reverse movement is unsupported, limited `Next` with prefix mode is rejected, range-key prefix truncation requires `ImmediateSuccessor`, and bounds must share the requested prefix. `NextPrefix` is barred with versioned upper bounds because MVCC suffix ordering can split versions around the bound.

Memory and lifecycle risks include double-close misuse, returning slices whose contents change on later movement, lazy values whose fetch can fail after `Valid`, open value closers across movements, and long-lived iterators pinning memtables/sstables or blob mappings. `CanDeterministicallySingleDelete` intentionally exposes nondeterministic internal LSM state and is only meaningful once per forward-oriented external position.

## Test Signals
Direct test coverage in the companion files exercises datadriven iterator semantics, forward/reverse stepping, merges and deletes, bounds, stats formatting/merging, read sampling, block-property filters, seek optimization errors, mutable indexed-batch refresh, bounds slice ownership, `SetOptions` equivalence to rebuilding, range-key masking, prefix seek randomized behavior, separated value retrieval profiling, and durable-only reads. Benchmarks stress scan, seek, prefix seek, range-key masking, fragmented range keys, tombstone-heavy workloads, queue-like delete swaths, and block-property filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/iterator_example_test.go -->
# sources/storage-engines/pebble/iterator_example_test.go

## Purpose
Provides Go documentation examples for common Pebble iterator use. These examples are executable tests that show users how to scan all keys, scan a prefix-like key range through bounds, and seek to the first key greater than or equal to a target.

## Important APIs, Types, And Functions
`ExampleIterator` opens an in-memory Pebble DB, writes three keys, creates `db.NewIter(nil)`, and scans with `First`, `Valid`, `Next`, and `Key`. `ExampleIterator_prefixIteration` demonstrates constructing `IterOptions` with `LowerBound` and `UpperBound`, including a local `keyUpperBound` helper that computes the smallest exclusive upper bound after a byte prefix. `ExampleIterator_SeekGE` demonstrates repeated `SeekGE` calls on a single iterator.

The examples use `pebble.Open`, `pebble.Options`, `vfs.NewMem`, `DB.Set`, `DB.NewIter`, `Iterator.Close`, `DB.Close`, and `pebble.Sync`. They live in package `pebble_test`, so they exercise the public API rather than unexported internals.

## Control Flow
Each example opens an isolated in-memory DB, writes `"hello"`, `"world"`, and `"hello world"`, creates an iterator, performs the targeted scan or seeks, prints keys, closes the iterator, and closes the DB. The expected `// Output:` block checks lexicographic ordering and makes the examples part of normal `go test` validation.

Prefix-style scanning is implemented with normal iterator bounds rather than `SeekPrefixGE`: the helper returns an upper bound by incrementing the last non-`0xff` byte and truncating after it, or nil when no finite upper bound exists. The scan then uses `First`/`Next` over `[prefix, upper)`.

## State And Persistence Behavior
All state is local and in-memory. The examples write transient keys into `vfs.NewMem()` and close all resources. Values are nil because the examples are about key iteration order, not value retrieval.

The key slices printed by `iter.Key()` are consumed immediately before the next iterator movement. No long-lived references to iterator-owned memory are retained.

## Dependencies And Integration Points
These examples integrate public documentation with the test suite. Because they are in `pebble_test`, they verify that external users can import `github.com/cockroachdb/pebble` and `github.com/cockroachdb/pebble/vfs` and perform the documented workflows without internal access.

## Risks And Edge Cases
The examples intentionally avoid errors from `NewIter` by ignoring the returned error, which is acceptable for concise documentation but less complete than production code. The prefix upper-bound helper handles carry and all-`0xff` prefixes, but it demonstrates bytewise-prefix bounds rather than comparer-defined `SeekPrefixGE` prefix iteration.

Resource cleanup is explicit. If future iterator APIs change close/error expectations, these examples are useful smoke tests for public documentation drift.

## Test Signals
`go test` validates the printed ordering exactly: full scan yields `hello`, `hello world`, `world`; bounded prefix scan yields only `hello` and `hello world`; `SeekGE("a")`, `SeekGE("hello w")`, and `SeekGE("w")` land on the expected keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/iterator_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/iterator_histories_test.go -->
# sources/storage-engines/pebble/iterator_histories_test.go

## Purpose
Defines `TestIterHistories`, a large datadriven test harness for reproducible iterator histories. It models sequences of database mutations, ingests, compactions, batches, snapshots, cloned iterators, combined point/range iteration, range-key-only iteration, and iterator commands, then compares stable textual output against files under `testdata/iter_histories`.

## Important APIs, Types, And Functions
`TestIterHistories` is the main entry point. It maintains a current `*DB`, named `*Iterator`s, named indexed `*Batch`es, DB options, probe maps, and a shared output buffer. `newIter` wraps `Reader.NewIter`, stores named iterators, and sets `forceEnableSeekOpt` to make history output deterministic. `parseOpts` configures in-memory storage, `testkeys.Comparer`, block-property collectors, disabled automatic compactions, and the V1 iterator stack. `cleanup` closes batches, iterators, snapshots, the DB, and any replacement cache.

The datadriven commands include `define`, `reopen`, `reset`, `populate`, `batch`, `compact`, `flush`, `disable-flushes`, `enable-flushes`, `get`, `build`, `ingest-existing`, `ingest`, `layout`, `lsm`, `metrics`, `mutate`, `clone`, `commit`, `combined-iter`, `rangekey-iter`, `scan-rangekeys`, `iter`, and `wait-table-stats`. `pluckStringCmdArg` is a small helper for optional string arguments.

Probe support is wired by replacing `d.newIters` in `addProbeInjectingNewIters`, attaching `itertest.Probe`s to point iterators and keyspan probes to range-deletion iterators for selected table numbers. `combined-iter` builds `IterOptions{KeyTypes: IterKeyTypePointsAndRanges}` and supports mask suffix/filter, bounds, reader selection, point-key block-property filters plus `SkipPoint`, snapshots, L6 filters, and probes.

## Control Flow
The test walks every file in `testdata/iter_histories`, skipping `no_invariants` cases when invariant builds would introduce nondeterminism. Each datadriven file starts or resets DB state, then feeds commands to the harness. Commands either mutate durable state, create named live objects, perform iterator operations through `runIterCmd`, or print structural state such as LSM layout and metrics.

Named iterators and batches persist across commands until explicitly closed or until cleanup. This lets test files express long histories such as: open iterator, mutate underlying indexed batch, call `SetOptions` or clone, then continue iteration. `clone` parses optional iterator options from command input and can request `CloneOptions.RefreshBatchView`.

The combined iterator path clears probe maps, parses options, selects a reader (`DB`, batch, or snapshot), constructs an iterator with points and ranges enabled, runs scripted iterator operations, and appends lower-level probe logs. Range-key-only paths exercise `IterKeyTypeRangesOnly` through either `runIterCmd` or a direct scan that prints bounds and range-key data.

## State And Persistence Behavior
The harness uses `vfs.NewMem` and disabled automatic compactions for deterministic state. It may reopen the same in-memory FS through options, build external sstables, ingest them, compact explicit ranges, pause flushes by mutating `d.mu.compact.flushing`, and inspect snapshots by sequence number.

Cleanup is important because tests intentionally keep iterators, batches, and snapshots alive across command boundaries. It closes all named objects, enumerates and closes open snapshots under `d.mu.snapshots`, closes the DB, and unreferences a replacement cache when command-line options installed one.

## Dependencies And Integration Points
The file integrates Pebble's datadriven test utilities, `itertest` parser/probes, `testkeys` comparer and block properties, keyspan probe helpers, run-command helpers from other Pebble tests, `manifest` table metadata, `sstable` test filters, in-memory VFS, and `require` assertions. It is explicitly V1-iterator-stack-specific pending a TODO to port to V2.

It directly exercises public `Reader` interfaces (`DB`, `Batch`, snapshots) and iterator internals needed for deterministic testing (`forceEnableSeekOpt`, `d.newIters` replacement, snapshot list inspection).

## Risks And Edge Cases
The harness has broad mutable shared state, so missing cleanup can leak references and influence later datadriven files. Replacing `d.newIters` is powerful but couples the test to DB internals. Because invariant builds may randomize iterator optimization/reconstruction behavior, the test disables those optimizations on created iterators and skips known nondeterministic files.

Batch mutation and clone histories are especially sensitive to iterator semantics around stale batch views, `SetOptions`, range deletion iterators, and range-key stacks. The point-key-filter command must keep `PointKeyFilters` and `SkipPoint` logically aligned or the test would compare different layers of filtering.

## Test Signals
Failures point to regressions in end-to-end iterator behavior rather than isolated helper logic. The histories can reveal changed key ordering, bounds behavior, range-key surfacing, masking/filtering, batch refresh semantics, clone visibility, probe-level seek/next behavior, LSM layout assumptions, or resource lifecycle. Probe output provides lower-level evidence when internal iterator calls differ while user-visible output remains close.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/iterator_histories_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/iterator_test.go -->
# sources/storage-engines/pebble/iterator_test.go

## Purpose
Contains the primary unit, randomized, datadriven, and benchmark coverage for Pebble iterator behavior. It validates visible-key semantics over internal versions, read sampling, table and block-property filtering, seek optimization correctness, mutable indexed-batch refresh, bounds ownership, stats, separated value profiling, range-key masking, prefix seeking, and performance under tombstone-heavy or range-key-heavy workloads.

## Important APIs, Types, And Functions
`testIterator` is a reusable helper for combined internal iterators, verifying ordered output and close-error propagation across fixed and randomized child splits. `TestIterator` builds a synthetic public `Iterator` over a fake internal iterator and `mergingIter`, then uses `testdata/iterator` to test point-key visibility, merges, deletes, bounds, snapshots, and stats.

`minSeqNumPropertyCollector` and `minSeqNumFilter` define a table property and filter used by `TestReadSampling` and `TestIteratorTableFilter`. `iterSeekOptWrapper` counts `TrySeekUsingNext` propagation for `TestIteratorSeekOpt`. `errorSeekIter` injects seek errors for `TestIteratorSeekOptErrors`. `testBlockIntervalMapper` supports block interval filter tests.

Targeted tests include `TestReadSampling`, `TestIteratorTableFilter`, `TestIteratorNextPrev`, `TestIteratorStats`, `TestIteratorSeekOpt`, `TestIteratorSeekOptErrors`, `TestIteratorBlockIntervalFilter`, `TestIteratorRandomizedBlockIntervalFilter`, `TestIteratorGuaranteedDurable`, `TestSetOptionsBatchRefreshSeekGE`, `TestSetOptionsBatchRefreshRand`, `TestIteratorBoundsLifetimes`, `TestIteratorStatsMerge`, `TestIteratorValueRetrievalProfile`, `TestSetOptionsEquivalence`, `TestRangeKeyMaskingRandomized`, and `TestIteratorSeekPrefixGERandomized`.

Helper constructors and formatters include `iterOptionsString`, `newTestkeysDatabase`, `newPointTestkeysDatabase`, `randStr`, `randValue`, `randKey`, `buildFragmentedRangeKey`, `waitForCompactionsAndTableStats`, `withStateSetup`, `populateKeyspaceSetup`, `deleteGapSetup`, and `runBenchmarkQueueWorkload`.

Benchmarks cover basic `SeekGE`/`Next`/`Prev`, sequential `SeekPrefixGE` with and without blooms/tombstones/two-level indexes, bounded seek loops, SeekGE no-op behavior, block-property filters, range-key masking, full scans, `NextPrefix`, combined point/range seek, fragmented range keys, prefix seeks through tombstone-only files, point-deleted swaths, and queue-like delete/append workloads.

## Control Flow
Datadriven tests create or reset in-memory DBs, ingest/build/flush data, create snapshots or iterators with parsed options, and delegate scripted iteration to `runIterCmd`. Synthetic tests construct fake internal iterators directly so they can precisely control internal key order and injected errors.

Read-sampling tests force sampling on every iterator-returned key, inspect per-iterator pending read compactions, close the iterator, and inspect DB-level read-compaction queues. Table-filter tests approximate snapshot-like filtering by collecting minimum sequence numbers into table properties and passing a filter through `IterOptions.PointKeyFilters`.

Seek optimization tests wrap or fake the lower iterator to count flags and inject errors. The batch-refresh tests create indexed batches, mutate them after an iterator is positioned, call `SetOptions`, and compare subsequent seeks/steps against expected keys or a fresh iterator. The randomized batch-refresh counterpart repeats this with random point writes, range deletes, bounds, and absolute positioning operations.

Bounds lifetime tests mutate caller-provided bound slices after `NewIter`, `SetBounds`, `SetOptions`, and `Clone` to prove the iterator copies bounds into owned buffers. `SetOptions` equivalence repeatedly randomizes key types, bounds, and range-key masking, comparing a long-lived iterator after `SetOptions` against a newly constructed iterator for the same operation and state.

Range-key masking randomized tests build two DBs with identical logical point/range-key contents but different layout and filter settings, then scan both with points-and-ranges plus masking and require identical point/range output while ensuring masked points remain hidden. Prefix seek randomized tests build an expected prefix-to-key map by scanning, then verify `SeekPrefixGE` for random prefixes.

## State And Persistence Behavior
Tests mostly use `vfs.NewMem` or crashable in-memory filesystems. They deliberately control flushes, compactions, target file sizes, block sizes, and iterator stack choice to shape LSM layout. Some benchmarks clone filesystem state to isolate subbenchmarks from mutations.

Several tests inspect or mutate internal DB state under locks, including current versions, allowed seek counters, compaction flags, compacting counts, table stats, snapshots, and read-compaction queues. Randomized tests log seeds so failures can be reproduced. Long-lived iterators and batches are closed with defers, and benchmark state helpers close DBs/readers/caches explicitly.

No production data is persisted by these tests, but they validate persistence-adjacent behavior: flush/ingest/compact layout, durable-only reads, table property persistence in sstables, and blob/separated value retrieval profiling.

## Dependencies And Integration Points
The file ties together most of Pebble's iterator stack: `base` fake/internal iterators and stats, `invalidating` wrappers, `iterv2` key generators and trigger paths, `manifest` levels, `testkeys`, `treesteps`, `sstable` readers/writers/block-property collectors/filters, `cache`, `objstorageprovider`, in-memory VFS, datadriven tests, leak testing, `require`, and concurrency helpers.

It relies on shared test helpers such as `runDBDefineCmd`, `runBuildCmd`, `runIngestCmd`, `runLSMCmd`, `runIterCmd`, `printIterState`, `buildMemTable`, `buildLevelsForMergingIterSeqSeek`, and `buildMergingIter` defined elsewhere in the Pebble test suite. Many cases are deliberately end-to-end across DB, Batch, Snapshot, table writing, and iterator construction.

## Risks And Edge Cases
The tests highlight the iterator's riskiest semantics: merge chains mixed with deletes, direction switches, prefix iteration after bloom-filter misses, seek-using-next no-op paths, limits, bounds changes without external repositioning, mutable indexed batches, range deletes added after iterator creation, range-key masking with block filters, and lazy/separated values.

Randomization increases coverage but can introduce nondeterminism, so tests use fixed seeds where needed, log generated seeds elsewhere, disable automatic compactions in layout-sensitive cases, and sometimes set `forceEnableSeekOpt`. Some benchmark fixtures are large and performance-oriented rather than strict correctness checks; they still encode important workload assumptions around tombstone buildup and fragmented range keys.

Direct use of internal fields such as `d.mu`, `iter.forceEnableSeekOpt`, `iter.merging.forceEnableSeekOpt`, and fake iterators makes the tests sensitive to internal refactors. That is intentional for coverage but raises maintenance cost when iterator stack internals change.

## Test Signals
Failure signals are diverse and strong. Datadriven output changes flag visible semantic drift. Randomized equivalence failures indicate `SetOptions`, range-key masking, or batch refresh divergence from fresh iterators. Seek optimization counters and injected errors detect unsafe flag propagation or stale error handling. Stats tests catch accounting regressions. Bounds lifetime tests catch memory aliasing. Benchmarks provide performance regression signals for scans, prefix seeks, filtered iteration, tombstone swaths, queue workloads, and combined point/range iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/iterator_test.go -->
