# subset-b-008536 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter.go -->
# sources/storage-engines/pebble/merging_iter.go

## Purpose
`merging_iter.go` implements Pebble's legacy `mergingIter`, a `base.InternalIterator` that merges multiple ordered child iterators from the LSM into one ordered point-key stream. It handles forward and reverse iteration, snapshot and batch snapshot visibility, prefix seeks, iterator bounds, range deletion shadowing, stats collection, and treesteps/debug integration.

## Important APIs, types, and functions
The central state is `mergingIter`, with `levels []mergingIterLevel`, a `mergingIterHeap`, direction `dir`, sequence visibility fields, bounds, prefix state, and `err`. `mergingIterLevel` couples a point iterator with the current `iterKV`, optional `rangeDelIter`, cached tombstone, generation counter, and optional backing `levelIter`.

Construction flows through `newMergingIter` and `(*mergingIter).init`. Public iterator methods are `SeekGE`, `SeekPrefixGE`, `SeekPrefixGEStrict`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `Prev`, `Error`, `Close`, `SetBounds`, and `SetContext`. Core internal helpers include `seekGE`, `seekLT`, `nextEntry`, `prevEntry`, `findNextEntry`, `findPrevEntry`, `isNextEntryDeleted`, `isPrevEntryDeleted`, and direction-switch helpers `switchToMinHeap` and `switchToMaxHeap`.

## Control flow and state behavior
The iterator keeps one cached key per level. Positioning methods seek every relevant child iterator, build a min or max heap, then call `findNextEntry` or `findPrevEntry` to skip hidden entries. `Next` and `Prev` advance only the current heap root and repair the heap. Direction switches must reposition all levels past the current key so the same internal key is not returned twice.

Range deletion handling is lazy and level-aware. Range deletion iterators are positioned only for levels up to the current heap root. Higher-level tombstones can force lower levels to seek to tombstone bounds; same-level tombstones require sequence-number checks through `CoversAt`. `levelIter` range deletion generation changes force tombstone cache refreshes when table boundaries are crossed. Prefix iteration additionally prevents child iterators from advancing beyond the active prefix, especially under `TrySeekUsingNext`.

State is in-memory iterator state only. Persistence is through underlying sstable/memtable/batch iterators, while this file owns transient heap entries, tombstone caches, stats, and copied seek buffers. `Close` closes child iterators and range deletion iterators.

## Dependencies and integration points
This code integrates with `base.InternalIterator`, `levelIter`, `keyspan.FragmentIterator`, `base.InternalIteratorStats`, `combinedIterState`, `treesteps`, `invariants`, and Pebble comparer/split functions. It is the merge layer used above memtables, batches, L0 sublevels, and L1+ level iterators.

## Risks and test signals
High-risk areas are range tombstone positioning across table boundaries, direction switching, prefix-mode interaction with `TrySeekUsingNext`, sentinel-key handling, and preserving the `InternalIterator` error contract. Test coverage comes from datadriven tests in `merging_iter_test.go`, heap tests in `merging_iter_heap_test.go`, treesteps data, benchmarks for seek/next/prev locality, and broader metamorphic iterator workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_heap.go -->
# sources/storage-engines/pebble/merging_iter_heap.go

## Purpose
`merging_iter_heap.go` provides the specialized heap used by the legacy merging iterator. It orders `mergingIterLevel` entries by their cached internal keys, supporting both forward min-heap and reverse max-heap behavior.

## Important APIs, types, and functions
`mergingIterHeap` stores the comparer, `reverse` mode, and `items []mergingIterHeapItem`. Each item holds a `*mergingIterLevel` and a cached `winnerChild`. `winnerChild` records which child would win during heap descent, reducing repeated comparisons during `down`.

The public-to-package methods are `len`, `clear`, `init`, `fixTop`, and `pop`. Internal helpers are `less`, `swap`, and `down`.

## Control flow and state behavior
`less` compares user keys first, then trailers. In forward mode, lower user keys and higher trailers win. In reverse mode, higher user keys and lower trailers win, matching reverse internal ordering. `init` heapifies in place from the bottom up. `fixTop` repairs the heap after the root's key changes. `pop` swaps the root with the final item, repairs the reduced heap, and shrinks the slice.

The only persistent state is the heap slice and cached winner-child hints. The heap assumes every item has a non-nil `iterKV`; exhaustion is handled by callers before removal. Cached `winnerChild` values are invalidated when swaps alter parent-child relationships. In invariant builds, the cache is checked for consistency.

## Dependencies and integration points
This heap is tightly coupled to `mergingIterLevel.iterKV` from `merging_iter.go` and uses Pebble's `Compare` plus invariant assertions from `internal/invariants`. It is not Go's standard `container/heap`; it is a hand-rolled implementation tuned for the small fixed fan-in of LSM levels.

## Risks and test signals
The main risks are stale `winnerChild` hints, reverse ordering mistakes, duplicate-key tie handling, and callers passing exhausted levels. `merging_iter_heap_test.go` randomly mutates heap roots, pops entries, and validates that the top always matches an independent scan. It also has a comparison-saving init test that exercises heap construction repeatedly.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_heap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_heap_test.go -->
# sources/storage-engines/pebble/merging_iter_heap_test.go

## Purpose
This file validates the custom legacy `mergingIterHeap` implementation. The tests focus on heap ordering under random key generation, forward and reverse modes, top-key mutation, no-op repairs, and popping exhausted iterators.

## Important APIs, types, and functions
`TestMergingIterHeap` constructs random `mergingIterHeapItem` values backed by `mergingIterLevel` objects with synthetic `base.InternalKV` keys. `checkHeap` independently scans the source levels and verifies heap length and root index. `TestMergingIterHeapInit` repeatedly measures and validates heap initialization over randomized heaps.

## Control flow and state behavior
The first test creates 6 to 11 levels, initializes the heap, then runs up to 400 random operations. A small fraction of operations exhausts the root and calls `pop`; another fraction mutates the root key and calls `fixTop`; the rest call `fixTop` without changing the key. After each operation, the test recomputes the expected root outside the heap.

The test tracks uniqueness through a `generatedKeys` map, avoiding duplicate user keys that would obscure the root choice. It toggles `reverse` randomly so the same implementation path is exercised as a min-heap and max-heap.

## Dependencies and integration points
The tests use `math/rand/v2`, `slices.Clone`, `base.DefaultComparer`, `require`, and Pebble's `randStr` helper. They directly instantiate unexported heap and level types, so they are package-level structural tests rather than black-box iterator tests.

## Risks and test signals
Coverage is strong for heap root correctness after common mutations but does not validate trailer tie-breaking because generated user keys are unique. It also does not directly exercise invariant panics for stale `winnerChild` under duplicate boundary-like keys. The init test is both a correctness loop and a signal that the winner-child optimization should reduce comparisons without changing heap semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_heap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_test.go -->
# sources/storage-engines/pebble/merging_iter_test.go

## Purpose
`merging_iter_test.go` provides the main coverage for the legacy merging iterator. It combines generic iterator conformance, datadriven fake-iterator tests, table-backed range deletion tests, and benchmarks that model LSM fan-in, sequential seeks, bounds changes, prefix seeks, and long keys.

## Important APIs, types, and functions
Tests include `TestMergingIter`, `TestMergingIterSeek`, `TestMergingIterNextPrev`, and `TestMergingIterDataDriven`. Helpers include `buildMergingIterTables`, `buildLevelsForMergingIterSeqSeek`, and `buildMergingIter`. Benchmarks include `BenchmarkMergingIterSeekGE`, `BenchmarkMergingIterNext`, `BenchmarkMergingIterPrev`, `BenchmarkMergingIterSeqSeekGEWithBounds`, `BenchmarkMergingIterSeqSeekPrefixGE`, and `BenchmarkMergingIterSeekAndNextWithDominantL6AndLongKey`.

## Control flow and state behavior
The generic tests split sorted key/value data across multiple fake iterators and check merged behavior. Datadriven seek tests parse text fixtures into `base.FakeIter` children. The table-backed datadriven test builds in-memory sstables, writes point keys and fragmented range tombstones, constructs a `manifest.Version`, wires `levelIter` objects into `mergingIterLevel`, and runs internal iterator commands while optionally attaching point and range-deletion probes.

Benchmark helpers create real sstable readers on `vfs.NewMem`, often with cache handles, bloom filters, two-level indexes, range tombstones, and multi-level slices. The sequential seek benchmarks repeatedly update bounds or prefix seek forward, targeting the `TrySeekUsingNext` and file-locality paths used by CockroachDB scans.

## Dependencies and integration points
The file exercises integration with `sstable.Reader`, `RawWriter`, `levelIter`, `manifest.LevelSlice`, `keyspan.Fragmenter`, bloom filters, cache handles, `itertest`, datadriven fixtures under `testdata/merging_iter*`, and `testkeys.Comparer`. It also verifies `SetContext` on the iterator path.

## Risks and test signals
This is the strongest signal for legacy iterator correctness because it uses real table readers and range deletion iterators. Important risk areas are range tombstone truncation to table bounds, sentinel boundary keys, seek optimization safety, bounds reuse, and reverse iteration. Benchmarks are not correctness checks, but they document expected workload shapes and performance-sensitive paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2.go -->
# sources/storage-engines/pebble/merging_iter_v2.go

## Purpose
`merging_iter_v2.go` implements `mergingIterV2`, a newer slab-based point-key merging iterator over `iterv2.Iter` children. It exposes `base.TopLevelIterator`/`base.InternalIterator` behavior while using span metadata from child iterators to filter range-deleted points and park fully shadowed lower levels.

## Important APIs, types, and functions
The main types are `mergingIterV2`, `mergingIterV2Level`, `mergingIterV2Heap`, and `spanKeysChangeDetector`. `mergingIterV2Level` tracks an `iterv2.Iter`, cached `iterKV`, stashed `Span`, visibility interval `[minSeqNum,maxSeqNum)`, parked state, forward-only parking safety, and deferred boundary state.

Core methods include `Init`, `newMergingIterV2`, `First`, `SeekGE`, `SeekPrefixGE`, `SeekPrefixGEStrict`, `SeekLT`, `Last`, `Next`, `NextPrefix`, `Prev`, `Close`, `PrepareForReuse`, `SetBounds`, and `SetContext`. Internal control paths include `seekGE`, `seekLT`, `findNextEntry`, `findPrevEntry`, `advanceSlabForward`, `advanceSlabBackward`, direction switches, single-level fast paths, and batch refresh handling.

## Control flow and state behavior
Positioning calls run `slab.Build` to compute per-level visibility and parked status. Active levels are positioned with `First`, `Last`, `SeekGE`, `SeekPrefixGE`, or `SeekLT`, and then inserted into a min or max heap. `findNextEntry` and `findPrevEntry` consume span-boundary keys internally, advance slabs, and return only point keys whose sequence numbers fall within `[minSeqNum,maxSeqNum)`.

Slab transitions handle co-located boundary keys, skip advancing levels that become parked, and seek unparked lower levels to the boundary. `onlyFwdSinceParked` permits `TrySeekUsingNext` when a parked level has only been logically advanced forward. `SeekGE(TrySeekUsingNext)` includes checks to avoid moving child iterators backward, a single-level fast path when span keys are unchanged, and special `BatchJustRefreshed` logic for indexed batches that may expose newly inserted keys behind the current position.

State is transient and reusable. `PrepareForReuse` preserves backing slices for allocation reduction, `Close` closes child iterators and clears references, and `levelHasError` clears active state when a child errors.

## Dependencies and integration points
The implementation depends on `iterv2.Iter`, `iterv2.Span`, `base.InternalKeyKindSpanBoundary`, `keyspan.Key`, `slabState` from `merging_iter_v2_slab.go`, treesteps, invariants, and Pebble comparers. Range keys are intentionally handled above this iterator, not emitted here.

## Risks and test signals
Risk concentrates around slab boundary correctness, parking/unparking, prefix seek restrictions, batch refresh reseeks, boundary-key tie ordering, and avoiding stale span-key assumptions in fast paths. Tests include datadriven scenarios, randomized comparison against a reference merge, heap benchmarks, and wider metamorphic iterator workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_bench_test.go -->
# sources/storage-engines/pebble/merging_iter_v2_bench_test.go

## Purpose
This benchmark file measures the custom heap inside `mergingIterV2`. It isolates heap initialization and repeated root repair under short and long CockroachDB-style MVCC keys.

## Important APIs, types, and functions
The only benchmark is `BenchmarkMergingIterV2Heap`. It defines short and long `cockroachkvs.KeyGenConfig` cases, then sub-benchmarks `Init` and `FixTop` for each. It directly manipulates `mergingIterV2Level`, `mergingIterV2Heap`, and `base.InternalKV`.

## Control flow and state behavior
The `Init` benchmark repeatedly fills a heap with eight level entries drawn from a shuffled random key pool, then calls `heap.Init`. The `FixTop` benchmark builds level key streams with exponential bias toward lower levels, initializes the heap, and repeatedly advances the top level or pops it when exhausted. This simulates the steady-state merge path where `Next` advances one child and repairs the heap.

No persistent state is created. State under measurement is the heap slice, per-level `iterKV` pointers, and level positions in generated arrays. The benchmark intentionally varies key length to capture compare cost sensitivity.

## Dependencies and integration points
It uses the `cockroachkvs` comparer and random key generator because CockroachDB MVCC keys are a primary Pebble workload. The benchmark is directly tied to `mergingIterV2Heap` internals and does not instantiate a full iterator or slab state.

## Risks and test signals
The benchmark is a performance signal, not a correctness oracle. It may miss correctness problems in boundary-key tie-breaking, parking, or span transitions. It is useful for detecting regressions in heap operations, especially comparison-heavy workloads with long keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_rand_test.go -->
# sources/storage-engines/pebble/merging_iter_v2_rand_test.go

## Purpose
`merging_iter_v2_rand_test.go` performs randomized differential testing of `mergingIterV2`. It generates random levels with point keys, range deletion spans, spurious boundaries, and snapshots, then compares iterator behavior against an independently computed expected point stream through the `iterv2` checker.

## Important APIs, types, and functions
`TestMergingIterV2Rand` runs 200 random seeds. `runMergingIterV2RandomTest` builds the random configuration, expected output, and checker. `randMergingTestLevels` generates level data with non-overlapping per-level sequence-number ranges so LSM ordering assumptions hold.

## Control flow and state behavior
Each run selects a random `iterv2.KeyGenConfig`, constrains sequence numbers, generates up to five levels, and chooses either an all-visible snapshot or a random snapshot. `mergeLevels` from `merging_iter_v2_test.go` computes the expected surviving keys by filtering visible points against visible range deletes. The `mergingIterV2` is wrapped in an `iterv2.InterleavingIter` so the common `iterv2.CheckIter` operation generator can exercise seeks, next/prev, prefix behavior, and `TrySeekUsingNext`.

On failure, the test prints the seed, snapshot, key config, points, and spans, making failures reproducible.

## Dependencies and integration points
The test depends on `iterv2.RandPointKeys`, `iterv2.RandSpans`, `iterv2.CheckIter`, `testkeys.Comparer`, and the test constructor from `merging_iter_v2_test.go`. It explicitly sets `RequirePrefixChangeForTrySeekUsingNext`, matching the invariant enforced by `SeekPrefixGEStrict`.

## Risks and test signals
This is a high-value correctness signal for slab logic because it mixes range deletes, snapshots, spurious span boundaries, and random operations. Gaps remain: lower/upper bounds are noted as TODO, and the reference model checks point results rather than internal parking efficiency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_rand_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_slab.go -->
# sources/storage-engines/pebble/merging_iter_v2_slab.go

## Purpose
`merging_iter_v2_slab.go` owns slab-state computation for `mergingIterV2`. It determines which levels are active or parked, computes per-level sequence-number visibility intervals, and tracks the next unshadowed span boundary.

## Important APIs, types, and functions
`slabState` stores the comparer, read snapshot, batch snapshot, batch level index, alias to `mergingIterV2` levels, and invariant-only `nextBoundary`. `Build(dir int8)` is the primary API and returns an iterator over `(levelIdx, parked)` pairs. `calcNextBoundary`, `assertNextBoundary`, and `visibleRangeDelSeqNum` support boundary and visibility logic.

## Control flow and state behavior
`Build` walks levels from newest to oldest. It yields whether the current level should be parked, expecting the caller to position the level or leave it alone. After the caller resumes, `Build` inspects the level's current span, sets `maxSeqNum` to either `snapshot` or `batchSnapshot`, detects the highest visible range deletion, and assigns `minSeqNum` to shadow lower-level keys. Once a visible range delete is found, all lower levels are parked because LSM ordering guarantees their sequence numbers are lower.

Under invariants, the code asserts that lower-level visible range deletions have smaller sequence numbers than higher-level visible range deletions. `calcNextBoundary` records the nearest non-parked span boundary in the iteration direction, used by `mergingIterV2` to assert boundary-key handling.

State is transient and aliases `m.levels`; there is no persistence. The boundary copy exists only in invariant builds.

## Dependencies and integration points
This file depends on `iter.Seq2`, `iterv2.Span`, `keyspan.Key`, `base.SeqNum`, comparers, and `internal/invariants`. It is called by every v2 positioning operation and slab transition.

## Risks and test signals
The highest-risk logic is the callback-style `Build` contract: callers must position spans before continuing, and mistakes can compute visibility from stale spans. Batch snapshot handling, parked-level propagation, and boundary direction comparisons are also sensitive. Coverage comes indirectly through all v2 datadriven and randomized tests, with invariant builds adding boundary and LSM-order assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_slab.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_test.go -->
# sources/storage-engines/pebble/merging_iter_v2_test.go

## Purpose
This file provides datadriven tests and shared helpers for `mergingIterV2`. It defines an independent reference merge for point visibility under range deletions and converts compact text fixtures into `iterv2.TestIterData`.

## Important APIs, types, and functions
`mergeLevels` computes expected surviving point keys for a snapshot. `newMergingIterV2FromLevels` wraps test levels in `iterv2.NewTestIter`, sometimes layering invalidating and operation-checking wrappers. `parseMergingTestLevels` and `formatMergingTestLevels` support datadriven input/output. `TestMergingIterV2` runs commands from `testdata/merging_iter_v2`.

## Control flow and state behavior
The `define` command parses levels. Each `L` starts a new level; point keys use internal-key strings and spans use `keyspan.ParseSpan`. The `iter` command constructs a fresh v2 iterator at the requested snapshot and delegates command execution to `itertest.RunInternalIterCmd`.

The reference `mergeLevels` first gathers visible range deletions, then scans visible points and filters points shadowed by any visible range delete with a greater sequence number. It sorts survivors by internal key ordering. This is intentionally simpler than slab logic and serves as a correctness oracle for randomized tests as well.

## Dependencies and integration points
The tests use `datadriven`, `itertest`, `iterv2.TestIter`, `keyspan`, `testkeys.Comparer`, and `base.InternalCompare`. Wrapping with invalidating/op-check iterators increases sensitivity to illegal key retention and invalid iterator operation sequences.

## Risks and test signals
The datadriven path provides readable regression fixtures for boundary and range deletion cases. The helper reference model is valuable but assumes LSM-valid level sequence-number ranges in randomized use. It tests returned point streams, not performance properties such as how often lower levels are parked or how many child seeks occur.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/merging_iter_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/build.go -->
# sources/storage-engines/pebble/metamorphic/build.go

## Purpose
`metamorphic/build.go` builds SST files used by Pebble metamorphic tests for regular ingestion, blob-file ingestion, and external-object ingestion emulation. It translates sorted batch/external iterators into ingestible tables while preserving or transforming point keys, range deletes, range keys, synthetic prefixes, synthetic suffixes, and format-version constraints.

## Important APIs, types, and functions
The central helper is `writeSSTForIngestion`, which writes point keys and spans to an `sstable.Writer`. Public-in-package builders include `buildForIngest`, `buildForIngestWithBlobs`, and `buildForIngestExternalEmulation`. Span helpers are `writeRangeDeletes`, `writeRangeKeys`, `openExternalObj`, and `panicIfErr`.

## Control flow and state behavior
`buildForIngest` creates a temp file path, decides whether value separation and format version allow blob-file ingestion, sorts the batch through `private.BatchSort`, and writes an SST. `writeSSTForIngestion` closes its iterators, skips duplicate user keys or prefixes, zeroes sequence numbers, applies synthetic key transforms, downgrades `DeleteSized` when the target format cannot support it, validates keys, writes raw point records, then writes range deletes and range keys.

`buildForIngestWithBlobs` uses `valsep.SSTBlobWriter`, creates blob files on demand, dispatches point operations by kind, then writes range deletes and range keys through the underlying SST writer. `buildForIngestExternalEmulation` opens a remote/external object, truncates iterators to bounds, optionally inverts synthetic prefixes for reads, and rewrites the object into a local SST for ingest emulation.

State persists as files under the metamorphic test temp directory and possibly external/blob objects. In-memory state includes iterators, writer metadata, blob path lists, and key buffers for duplicate suppression.

## Dependencies and integration points
This code integrates with `pebble.Batch`, `private.BatchSort`, `sstable.Writer`, `valsep.SSTBlobWriter`, `objstorage`, `vfs`, `keyspan`, `rangekey.Coalesce`, format major versions, and metamorphic `Test` state. It is directly tied to writer ingest operations generated elsewhere.

## Risks and test signals
Risks include incorrect iterator closure, duplicate suppression under prefix uniqueness, synthetic suffix handling with range deletes/unsets, format-version downgrades, range key coalescing, and bounds truncation of external objects. Coverage is mostly through metamorphic execution paths rather than isolated unit tests, so failures may surface as generated operation mismatches.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/cockroachkvs.go -->
# sources/storage-engines/pebble/metamorphic/cockroachkvs.go

## Purpose
`metamorphic/cockroachkvs.go` defines a metamorphic `KeyFormat` and key generator that mimic CockroachDB MVCC keys. It lets Pebble metamorphic tests exercise comparer behavior, suffix ordering, block-property filters, and timestamp-skewed version histories representative of CockroachDB.

## Important APIs, types, and functions
`CockroachKeyFormat` supplies comparer, key schema, format/parse functions, block property collectors, suffix filters, and generator construction. `cockroachKeyGenerator` implements `KeyGenerator` with `RecordPrecedingKey`, `ExtendPrefix`, `RandKey`, `RandKeyInRange`, `RandPrefix`, `SkewedSuffix`, `IncMaxSuffix`, `SuffixRange`, and `UniformSuffix`. `cockroachSuffixKeyspace` maps one-dimensional `suffixIndex` values to `(wallTime, logical)` MVCC timestamp suffixes.

## Control flow and state behavior
The generator chooses between known keys, existing prefixes with new suffixes, and entirely new prefixes according to `OpConfig`. It uses `keyManager` to avoid or record duplicates and `writeSuffixDist` to skew writes toward recent suffixes. Bounded key generation splits Cockroach keys into prefix and suffix indexes, then generates either an in-range suffix under the same prefix or a random prefix between bounds.

`RecordPrecedingKey` ratchets the suffix distribution upward when prior test state contains larger timestamps, preserving cross-version workload continuity. `SuffixRange` accounts for Cockroach's descending MVCC suffix ordering by returning `(low, high]` in comparer terms.

State is held in the key manager, RNG, op config's mutable suffix distribution, and suffix keyspace mapping. No files are persisted by this source.

## Dependencies and integration points
The file depends on `cockroachkvs`, `testkeys.RandomPrefixInRange`, Pebble key schemas and block-property filters, and metamorphic `keyManager`. It is selected through the key-format registry in `config.go`.

## Risks and test signals
The riskiest areas are suffix ordering, bounded generation under descending timestamp semantics, distribution ratcheting, and consistency between formatted strings and parsed keys. Test signals are indirect through generator/key-manager tests and Cockroach-key metamorphic runs; any comparer or suffix-filter mismatch can produce hard-to-debug nondeterministic failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/cockroachkvs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/config.go -->
# sources/storage-engines/pebble/metamorphic/config.go

## Purpose
`metamorphic/config.go` defines the operation mix and key-format abstraction for Pebble metamorphic tests. It is the central configuration surface controlling which database, iterator, batch, ingest, range-key, and external-object operations are generated and how keys are produced.

## Important APIs, types, and functions
`OpType` enumerates all generated operation kinds. `OpConfig` stores operation weights, new-prefix probability, write suffix distribution, and instance count. Configuration constructors and mutators include `DefaultOpConfig`, `ReadOpConfig`, `WriteOpConfig`, `multiInstanceConfig`, `WithNewPrefixProbability`, and `WithOpWeight`. `KeyFormat` and `KeyGenerator` define the interface for testkeys and Cockroach-style key generation. Registries include `knownKeyFormats` and `keyFormatsByName`.

## Control flow and state behavior
Default config emphasizes iterator and writer operations, with nonzero weights for flushing, restarting, compaction, ingest, range keys, snapshots, and external-file ingestion. Preset configs include a version-heavy workload with low new-prefix probability and reduced deletes. Read-only and write-only configs zero out the other side of the workload. Multi-instance config enables replication while disabling unsupported single deletes, merges, and external ingestion.

`OpConfig` is value-based: mutators return modified copies. The embedded `randvar.Dynamic` suffix distribution is mutable during generation, allowing key generators to expand the suffix range over time.

There is no persistence in this file, but generated operation streams and test options downstream depend on these distributions.

## Dependencies and integration points
The file depends on Pebble operation types, `randvar`, `base.Comparer`, `sstable` block properties, and key formats from testkeys and Cockroach. It is consumed by metamorphic operation generation, command-line/config parsing code, and example tests.

## Risks and test signals
Risks are skewed or invalid operation mixes, stale `NumOpTypes` alignment with the weights array, unsupported operations in special modes, and key-format implementations that do not honor bounds or suffix ordering. Coverage is broad through metamorphic generator/parser/options tests and execution examples, but changes to weights can shift bug-finding power without failing deterministic tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/diagram.go -->
# sources/storage-engines/pebble/metamorphic/diagram.go

## Purpose
`metamorphic/diagram.go` generates compact ASCII diagrams of key ranges touched by metamorphic operations. It is a debugging aid for understanding generated operation sequences and their key-space overlap.

## Important APIs, types, and functions
`TryToGenerateDiagram` parses operation text and returns a diagram string or an empty string when the input is too large or has no diagrammable ranges. `genAxis` builds the axis row, label row, and key-to-column map.

## Control flow and state behavior
`TryToGenerateDiagram` parses operations with key-format-specific parsers, rejects large operation counts above 200, collects all range start/end keys from each operation's `diagramKeyRanges`, sorts the key set with the key format comparer, and calls `genAxis`. If the axis would exceed 200 columns, it returns an empty string. It then renders one row per operation with `|---|` range markers followed by the formatted operation string, and appends the axis rows.

`genAxis` spaces labels by at least two columns and key markers by at least four columns, returning deterministic positions for sorted keys. State is entirely local and in-memory.

## Dependencies and integration points
The file depends on the metamorphic parser, operation formatting methods, `KeyFormat`, sorted-key helpers, and standard `strings.Builder`. It is exercised by datadriven tests and useful when diagnosing generated histories.

## Risks and test signals
Risks are mostly usability issues: unreadable spacing, oversized diagrams, parse failures, or incorrect key ordering under custom comparers. `diagram_test.go` covers fixture-based rendering with `TestkeysKeyFormat`. Cockroach key formatting is supported by the API but not directly covered by this file's small test.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/diagram.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/diagram_test.go -->
# sources/storage-engines/pebble/metamorphic/diagram_test.go

## Purpose
`diagram_test.go` provides datadriven regression coverage for metamorphic ASCII diagram generation.

## Important APIs, types, and functions
The sole test is `TestDiagram`. It runs `datadriven.RunTest` over `testdata/diagram`, handles the `diagram` command, and calls `TryToGenerateDiagram(TestkeysKeyFormat, []byte(d.Input))`.

## Control flow and state behavior
Each fixture input is parsed as metamorphic operations. If diagram generation returns an error, the error string is used as output; otherwise the generated diagram is returned to the datadriven harness. The test has no persistent state and constructs no database.

## Dependencies and integration points
The test depends on the datadriven framework, `TryToGenerateDiagram`, and `TestkeysKeyFormat`. It indirectly covers parser integration, operation `diagramKeyRanges`, formatted operation output, key sorting, and axis spacing.

## Risks and test signals
This is a focused rendering regression test. It does not cover large-input early returns beyond fixture coverage, Cockroach key formatting, or every operation type unless represented in `testdata/diagram`. It is still a useful signal because diagram output is deterministic and easy to diff.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/diagram_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/example_test.go -->
# sources/storage-engines/pebble/metamorphic/example_test.go

## Purpose
`example_test.go` is an executable documentation example for running a Pebble metamorphic test end to end. It demonstrates generating random options and operations, constructing a test, executing it, and expecting a nil error.

## Important APIs, types, and functions
The file defines `ExampleExecute`. It uses `metamorphic.RandomOptions`, `metamorphic.GenerateOps`, `metamorphic.DefaultOpConfig`, `metamorphic.New`, and `metamorphic.Execute`.

## Control flow and state behavior
The example fixes a seed, creates a `math/rand/v2` PCG RNG, selects `TestkeysKeyFormat`, generates options and 10,000 operations, constructs a test with no explicit directory and `io.Discard` output, executes it, and prints the error. The expected output is `<nil>`, so Go's example runner verifies that the execution succeeds.

State is created inside the metamorphic test harness, including temporary DB/test resources managed by `New` and `Execute`. This file itself persists nothing and writes only to the example output stream.

## Dependencies and integration points
The example imports the public `github.com/cockroachdb/pebble/metamorphic` package from an external-test package, which validates that the public-facing metamorphic API is usable outside the package. It also links config defaults from `config.go` to actual execution.

## Risks and test signals
This is a broad smoke test, not a diagnostic unit test. It can catch broken public API wiring or severe execution regressions, but failures may be expensive to localize. Because the seed is fixed, it is deterministic, but it only samples one generated workload.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/example_test.go -->
