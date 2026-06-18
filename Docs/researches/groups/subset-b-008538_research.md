# Research Report: subset-b-008538

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser.go -->
## sources/storage-engines/pebble/metamorphic/parser.go

Purpose: implements the text parser for Pebble metamorphic test operations. The textual operation format is intentionally Go-like, allowing `go/scanner` and `go/token` to tokenize operation logs produced by `formatOps` and `op.String()`.

Important APIs and types: `parse(src, parserOpts)` is the entry point. `parserOpts` provides formatted user-key/suffix parsers and an `allowUndefinedObjs` compatibility mode. `methodInfo`, `makeMethod`, the `methods` map, and `opArgs` define the grammar binding between operation names, valid receiver object tags, receiver/target object IDs, and typed argument fields. `ignoreExtraArgs` preserves mixed-version compatibility for older operation arities.

Control flow: `parse` initializes the object table with `db1` and `db2`, scans operations until EOF, then calls `computeDerivedFields`. `parseOp` recognizes `Init(args)`, `obj.Method(args)`, and `target = obj.Method(args)`. `makeOp` validates method existence, receiver tag compatibility, assignment requirements, and argument syntax before constructing the concrete `op`. `parseArgs` handles fixed args plus supported variadic/list args: iterator flags, object IDs, key ranges, checkpoint/download spans, and external objects with bounds.

State and persistence: the parser maintains only in-memory object-definition state and derived relationship maps. It does not persist data, but parsed operations drive later DB, batch, iterator, snapshot, and external-object state.

Dependencies and integration: depends on Pebble operation types in the metamorphic package, `pebble.KeyRange`, `CheckpointSpan`, `DownloadSpan`, `blockiter.SyntheticPrefix/Suffix`, and `parseObjID` from `utils.go`. It integrates tightly with `formatOps`, operation `rewriteKeys`, and concurrent execution through derived fields.

Risks and edge cases: panics are converted to parse errors only at the top level, so helper assertions must be carefully contextualized. Synthetic-prefix validation assumes bounds share the prefix. `parseList` only accepts strings, identifiers, and integers. Derived-field computation silently depends on earlier object-creation operations; malformed but syntactically valid orderings may leave zero derived IDs.

Test signals: `parser_test.go` covers datadriven parsing, 10k-operation random round trips, multi-instance operation streams, and preservation of nil iterator bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser_test.go -->
## sources/storage-engines/pebble/metamorphic/parser_test.go

Purpose: verifies that the metamorphic operation parser accepts the textual format used by generated and persisted operation streams and round-trips back through `formatOps`.

Important APIs and functions: `TestParser` runs datadriven `parse` commands over `testdata/parser` using `TestkeysKeyFormat` formatted key and suffix parsers. `TestParserRandom` generates 10,000 operations under both default and multi-instance configs and checks parsed operations equal the generated operations. `TestParserNilBounds` specifically verifies that formatting and parsing an iterator with nil lower/upper bounds preserves nil rather than converting them to empty byte slices.

Control flow: datadriven inputs are parsed with formatted testkey parsing; errors are returned as test output to lock down diagnostics. The randomized test builds a `keyManager`, random generator, operation sequence, formats it, parses it with default parser options, and uses `require.Equal` on operation structs.

State and persistence: the tests are in-memory. They exercise parser object-state tracking indirectly through generated operation sequences containing DBs, batches, iterators, snapshots, and multi-instance object IDs.

Dependencies and integration: depends on `datadriven`, `randvar.NewRand`, `newGenerator`, `multiInstanceConfig`, `DefaultOpConfig`, and `TestkeysKeyFormat`. This makes it an integration test between generation, formatting, parser construction, object-ID utilities, and derived-field computation.

Risks and gaps: randomized coverage is strong for generated legal operations but does not independently fuzz malformed syntax or every compatibility path. Datadriven coverage is only as broad as `testdata/parser`.

Test signals: the file itself is the primary parser test signal, especially the equality round-trip and nil-bound regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/retryable.go -->
## sources/storage-engines/pebble/metamorphic/retryable.go

Purpose: provides retry semantics for metamorphic tests running under injected filesystem errors, especially iterator operations that may fail transiently and need to be retried without changing expected test history.

Important APIs and types: `RetryPolicy` decides whether an error is retryable. `NeverRetry` and `RetryInjected` are built-in policies, with `RetryInjected` matching `errorfs.ErrInjected`. `withRetries` repeatedly invokes a function until the returned error is not retryable. `retryableIter` wraps `*pebble.Iterator` and implements the subset of iterator methods used by metamorphic ops.

Control flow: `retryableIter.withRetry` runs an iterator action, inspects `iter.Error`, and if retryable keeps repositioning with `SeekGE(lastKey)` until the iterator clears the retryable error. It then records the current key as the new `lastKey` if valid. Positioning methods (`First`, `Last`, `Next`, `Prev`, `SeekGE`, `SeekLT`, limit variants, `NextPrefix`, `SeekPrefixGE`) all delegate through `withRetry`; accessors and option setters pass through directly.

State and persistence: `lastKey` is the only local state. It represents the successful post-operation iterator position used to reconstruct pre-operation state during retries. No persistent state is written.

Dependencies and integration: used by `Test.setIter` in `test.go`; retry policies are supplied by `TestOptions`. Depends on Pebble iterator APIs and `vfs/errorfs` injected errors.

Risks and edge cases: retry recovery assumes `SeekGE(lastKey)` is a valid way to return to the previous state, which may not model all reverse-iteration states perfectly. A retry policy that returns true forever could loop indefinitely. `SetBounds` and `SetOptions` are not retried here.

Test signals: coverage is indirect through metamorphic tests using injected errors; this file has no dedicated unit test in the listed set.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/retryable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify.go -->
## sources/storage-engines/pebble/metamorphic/simplify.go

Purpose: rewrites metamorphic operation streams to use a smaller ordered key set, making failing histories easier to inspect and reduce. The simplification is intentionally not guaranteed to preserve semantics.

Important APIs and functions: `TryToSimplifyKeys(keyFormat, opsData, retainSuffixes)` parses formatted operation data, discovers distinct keys or distinct prefixes, maps them to lowercase letters `a` through `z`, rewrites operation keys in-place through each op's `rewriteKeys`, and returns reformatted operations. `sortedKeys` sorts discovered keys with the key format comparer.

Control flow: the function parses with the supplied formatted key and suffix parsers. It makes a first rewrite pass only to collect keys while returning the original key. If there are more than 26 distinct rewrite targets it returns nil. It sorts keys by the configured comparer, assigns ordinal letters, then makes a second rewrite pass. With `retainSuffixes`, only prefixes are ordinalized and suffix bytes are appended unchanged.

State and persistence: all state is transient maps/slices and parsed operations. It does not write files; callers decide how to use returned operation data.

Dependencies and integration: depends on parser correctness, operation `rewriteKeys` implementations, `formatOps`, and `KeyFormat.Comparer.Split/Compare`. Integrates with testkey/cockroach key formats through formatted parser hooks.

Risks and edge cases: the semantic warning is important: collapsing key bytes can change prefix relationships, separator behavior, and range interactions. Returning nil on more than 26 keys can surprise callers that do not distinguish nil from an empty operation stream.

Test signals: `simplify_test.go` uses datadriven cases in `testdata/simplify`, including the suffix-retention mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify_test.go -->
## sources/storage-engines/pebble/metamorphic/simplify_test.go

Purpose: datadriven tests for key simplification of metamorphic operation streams.

Important APIs and functions: `TestSimplifyKeys` runs `simplify-keys` commands from `testdata/simplify`. It passes `TestkeysKeyFormat` and toggles suffix-preserving behavior when the datadriven command has a `retain-suffixes` argument.

Control flow: each datadriven command invokes `TryToSimplifyKeys`, converts the resulting bytes to string, and returns them for golden comparison. Unknown commands produce a diagnostic string.

State and persistence: no persistent state. The test validates pure parse/rewrite/format behavior over fixture inputs.

Dependencies and integration: integrates `TryToSimplifyKeys`, parser formatted-key hooks, `TestkeysKeyFormat`, operation key rewriting, and datadriven expected output files.

Risks and gaps: the test exercises fixture cases, not exhaustive generated operation streams. It does not explicitly assert the nil-return path for more than 26 distinct keys unless covered in fixture data.

Test signals: golden output captures ordering, suffix retention, and formatting stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/test.go -->
## sources/storage-engines/pebble/metamorphic/test.go

Purpose: defines the runtime harness that executes parsed/generated metamorphic operations against one or more Pebble DB instances while recording deterministic history and handling test-specific filesystem, remote-storage, retry, and synchronization behavior.

Important APIs and types: `New` constructs a single-instance `Test`. `Test` stores operations, synchronization data, options, DB handles, object slots for batches/iterators/snapshots/external objects, and remote external storage. Key methods include `init`, `finalizeOptions`, `restartDB`, `Step`, `runOp`, object slot setters/getters, and `computeSynchronizationPoints`.

Control flow: `init` clones and finalizes options, wraps listeners to fail on background errors, opens custom options, opens each DB, initializes shared/external storage, and creates temporary directories. `Step` runs one operation through `runOp`; `runOp` applies timeout multipliers for slow operations and optional treesteps recording before invoking `op.run`. `computeSynchronizationPoints` computes wait dependencies from each op's receiver and synchronization objects for parallel execution.

State and persistence: the harness owns live DB, batch, iterator, snapshot, and external object state. In strict FS mode it syncs directories and supports crash-clone restarts on in-memory FS. On serious background errors it clones in-memory data to disk for debugging and exits. Shared/external storage is represented by local directories and `remote.Storage` factories.

Dependencies and integration: integrates with Pebble `Options`, event listeners, `objstorageprovider`, `remote`, `vfs`, `errorfs`, operation implementations, history logging, and custom option hooks. `retryableIter` is installed by `setIter`.

Risks and edge cases: background errors call `os.Exit(1)`, which is appropriate for metamorphic binaries but hostile to library-style callers. Multi-DB restart is disabled because DBs share FS. Object slots are assertion-heavy; stale IDs panic. Synchronization depends on every op reporting correct `receiver` and `syncObjs`.

Test signals: broad metamorphic integration tests exercise this harness; listed parser tests verify operation-derived fields used by synchronization and execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/testkeys.go -->
## sources/storage-engines/pebble/metamorphic/testkeys.go

Purpose: defines the `testkeys` key format and random key generator used by metamorphic tests to exercise prefix/suffix-aware Pebble behavior, block property filters, masking filters, and MVCC-like suffix ordering.

Important APIs and types: `TestkeysKeyFormat` supplies comparer, columnar key schema, test-key block property collector/filter/mask, formatting/parsing hooks, and generator factory. `testkeyKeyGenerator` implements `KeyGenerator` methods including `RecordPrecedingKey`, `ExtendPrefix`, `RandKey`, `RandKeyInRange`, `RandPrefix`, `SkewedSuffix`, `UniformSuffix`, `SuffixRange`, `IncMaxSuffix`, and helpers for comparison/splitting/parsing.

Control flow: key generation usually reuses known keys unless probabilities choose a new key/prefix. New suffixes are drawn from configured write suffix distributions, with occasional `IncMax` growth. Range-bound generation handles same-prefix suffix ranges and cross-prefix ranges separately, validating the final key lies within bounds. Existing prefixes may be combined with new suffixes; duplicate or out-of-range attempts increase the suffix max and retry.

State and persistence: state lives in `keyManager`, RNG, and mutable `OpConfig` suffix distribution. `RecordPrecedingKey` ratchets the max suffix upward when external prior keys are observed. No data is persisted directly.

Dependencies and integration: depends on `internal/testkeys`, `sstable` test-key block properties, `colblk.KeySchema`, Pebble block property filter interfaces, and metamorphic operation generation.

Risks and edge cases: suffix ordering is descending, so comparisons are non-intuitive and carefully handled by `cmpSuffix`. Range generation has retry fallbacks after 10 attempts. `uniformSuffixInt` uses `Int64N(maxVal)` and assumes a positive max. Generated keys may rarely already exist in bounded mode and are tolerated.

Test signals: parser random tests use this generator heavily; broader metamorphic suites validate generated operation streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/testkeys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/utils.go -->
## sources/storage-engines/pebble/metamorphic/utils.go

Purpose: provides low-level object ID and small collection helpers for the metamorphic framework.

Important APIs and types: `objTag` enumerates DB, batch, iterator, snapshot, and external object tags. `objID` packs a 4-bit tag and 28-bit slot. `makeObjID`, `tag`, `slot`, `String`, and `parseObjID` convert between packed IDs and textual IDs like `db1`, `batch0`, `iter3`, `snap2`, and `external4`. `objIDSlice` supports sort.Interface, removal, and random selection. `objIDSet.sorted` returns deterministic sorted IDs. `firstError` returns the first non-nil error.

Control flow: `parseObjID` special-cases legacy `db` to `db1`, then finds a known prefix and parses the numeric suffix. `objIDSlice.remove` swaps the removed element with the tail for O(n) deletion without preserving order. `sorted` copies map keys and sorts by packed ID.

State and persistence: no persistent state. The packed ID representation is in-memory but also defines the textual operation format consumed by parser and formatter.

Dependencies and integration: used throughout metamorphic parser, generator, operation execution, and object slot management. Depends on `math/rand/v2`, `sort`, string parsing, and Cockroach errors.

Risks and edge cases: `String` indexes `objTagPrefix` by tag and assumes valid tags. `parseObjID` accepts any parsed 32-bit slot and does not reject zero DB slots, leaving semantic validation to callers. Removal silently does nothing when the ID is absent.

Test signals: parser tests and generated operation round-trips indirectly exercise object ID formatting and parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics.go -->
## sources/storage-engines/pebble/metrics.go

Purpose: defines Pebble's public `Metrics` model, per-level counters, compaction/flush/ingest/WAL/cache/table/blob statistics, and human-readable formatting for diagnostic output.

Important APIs and types: aliases expose cache, filter, throughput, and secondary-cache metrics. `LevelMetrics` tracks LSM size, virtual tables, value-separation references, compaction/flush/ingest counters, read/write bytes, multilevel stats, and additional block-write stats. `Metrics` aggregates subsystem metrics. Helpers include `DiskSpaceUsage`, `NumVirtual`, `VirtualSize`, `ReadAmp`, `Total`, `RemoteTablesTotal`, `SafeFormat`, `String`, `StringForTests`, `AllLevelMetrics.Total`, `AllLevelMetrics.Iter`, and `levelMetricsDelta`.

Control flow: metrics are mostly passive data. `LevelMetrics.Add` accumulates counters; `WriteAmp` divides physical bytes written by logical bytes in. `Metrics.DiskSpaceUsage` sums local WAL, table, blob, options, manifest, and in-progress compaction bytes. `RemoteTablesTotal` adds live/obsolete/zombie table placements and returns shared plus external totals. `String` builds multiple ASCII tables for LSM, compactions, commit pipeline, caches, iterators, file usage, blob values, memory, keys, compression, compression counters, and delete pacer.

State and persistence: metrics represent in-memory snapshots derived from DB state; cumulative counters are monotonic where documented. They do not persist themselves, but they include on-disk sizes and remote-placement accounting.

Dependencies and integration: integrates with manifest levels, cache hit/miss structures, WAL failover stats, table/blob compression stats, Prometheus histograms, manual memory accounting, delete pacer metrics, and `metrics.CountAndSizeByPlacement`.

Risks and edge cases: formatting is broad and brittle to table layout changes. `DiskSpaceUsage` intentionally excludes remote bytes and has a TODO for in-progress remote distinction. `AllLevelMetrics.Total` folds WAL bytes into L0-style flushed bytes to compute write amp, which callers must understand. Category registration is package-global.

Test signals: `metrics_test.go` has golden datadriven output, remote virtual-table regression coverage, WAL write monotonicity, disabled-WAL write amp, and cumulative flushable memory checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement.go -->
## sources/storage-engines/pebble/metrics/by_placement.go

Purpose: provides reusable metric containers for count/size accounting by storage placement and file type.

Important APIs and types: `CountAndSizeByPlacement` embeds `ByPlacement[CountAndSize]` with `Inc`, `Dec`, `Accumulate`, `Deduct`, `Total`, `String`, and `SafeFormat`. Generic `ByPlacement[T]` provides `Get`, `Set`, and `Ptr` over `base.Local`, `base.Shared`, and `base.External`. `FileCountsAndSizes` groups table, blob, and other-file counts with aggregate and formatting helpers.

Control flow: placement-specific methods dispatch by `base.Placement`. Invalid placements panic only under invariants builds and otherwise fall back to local. File-type methods send tables and blobs through placement accounting and all other file types through local-only `Other`.

State and persistence: pure in-memory counters used by DB metrics and delete-pacer metrics. No persistence.

Dependencies and integration: depends on `base.Placement`, `base.FileType`, `invariants`, `redact`, and `CountAndSize`. It is consumed by `Metrics.Table.Physical`, `Metrics.BlobFiles`, and delete-pacer summaries.

Risks and edge cases: non-invariants fallback to local can hide invalid placement bugs in production builds. `SafeFormat` for placement only shows local detail when remote/shared counts exist, which is concise but lossy for shared vs external.

Test signals: `by_placement_test.go` covers placement accessors, pointer mutation, inc/dec, accumulation/deduction, totals, and formatted strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement_test.go -->
## sources/storage-engines/pebble/metrics/by_placement_test.go

Purpose: verifies placement-aware and file-type-aware metric arithmetic and safe formatting behavior.

Important APIs and functions: tests cover `CountAndSizeByPlacement.Get`, `Ptr`, `Inc`, `Dec`, `Accumulate`, `Deduct`, `Total`, plus `FileCountsAndSizes.Inc`, `Dec`, `Accumulate`, `Deduct`, `Total`, and `String`.

Control flow: each test constructs small explicit counters and checks exact structs after operations. String tests use table-driven cases for empty metrics, local-only tables, shared tables, blob files, other files, and combinations.

State and persistence: no persistent state; only pure metric structs.

Dependencies and integration: depends on `base.FileType`, `base.Placement`, `CountAndSize`, `CountAndSizeByPlacement`, and `testify/require`.

Risks and gaps: invalid placement behavior under invariants is not tested here. Underflow behavior is mostly delegated to `CountAndSize` and covered by its tests, not specifically by placement wrappers.

Test signals: direct unit coverage locks down arithmetic and user-facing string summaries such as `tables: 5 (1KB) [local: 3 (512B)]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/by_placement_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size.go -->
## sources/storage-engines/pebble/metrics/count_and_size.go

Purpose: defines the primitive count-plus-byte-size metric used throughout Pebble metrics.

Important APIs and types: `CountAndSize` has `Count` and `Bytes`. Methods include `Inc`, `Dec`, `Accumulate`, `Deduct`, `IsZero`, `Sum`, `String`, and `SafeFormat`.

Control flow: `Inc` increments count and adds file size. `Dec` and `Deduct` use `invariants.SafeSub` for count and byte subtraction, providing assertion/guard behavior against underflow depending on build settings. `Sum` returns a new struct without mutating operands. `SafeFormat` formats as count plus humanized bytes.

State and persistence: pure in-memory value type. It is often embedded inside larger persistent-state-derived metrics, but it does not persist data itself.

Dependencies and integration: used by level metrics, placement metrics, delete pacer, object and file accounting. Depends on `crhumanize`, `invariants`, and `redact`.

Risks and edge cases: arithmetic is unsigned; caller mistakes can underflow in non-invariants behavior depending on `SafeSub` semantics. Formatting omits binary `i` suffix by design, so output stability depends on `crhumanize`.

Test signals: `count_and_size_test.go` covers increment, decrement, accumulate, deduct, non-mutating sum, and zero detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size_test.go -->
## sources/storage-engines/pebble/metrics/count_and_size_test.go

Purpose: unit tests for the primitive `CountAndSize` metric arithmetic.

Important APIs and functions: `expect` is a helper asserting exact count and byte values. Tests cover `Inc`, `Dec`, `Accumulate`, `Deduct`, `Sum`, and `IsZero`.

Control flow: each test initializes a counter, performs one or more operations, and uses `require.Equal` through `expect`. `TestCountAndSize_Sum` also verifies operands are unchanged after summing.

State and persistence: no persistent state; all tests operate on value structs.

Dependencies and integration: depends only on the metrics package and `testify/require`.

Risks and gaps: tests do not exercise underflow or invariants behavior for invalid `Dec`/`Deduct` inputs. Formatting is not directly tested here; placement tests indirectly cover formatted `CountAndSize` output.

Test signals: direct arithmetic coverage ensures the building block used by file, table, blob, and placement metrics behaves predictably.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/doc.go -->
## sources/storage-engines/pebble/metrics/doc.go

Purpose: package documentation stub for the `metrics` subpackage.

Important APIs and types: declares package `metrics` and documents it as defining types and helpers used for metrics.

Control flow: none.

State and persistence: none.

Dependencies and integration: affects Go package documentation and godoc output. The actual exported APIs are in sibling files such as `count_and_size.go`, `by_placement.go`, and `value_retrieval_profile.go`.

Risks and edge cases: no behavioral risk. Documentation is minimal and may not communicate the package's role in placement accounting or value-retrieval profiling.

Test signals: no direct tests needed.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/value_retrieval_profile.go -->
## sources/storage-engines/pebble/metrics/value_retrieval_profile.go

Purpose: exposes a metric/profile type for separated value retrievals.

Important APIs and types: `ValueRetrievalProfile` is a type alias to `bytesprofile.Profile`, making the internal profile type available under the public metrics package namespace.

Control flow: none; this is a compile-time alias.

State and persistence: profile state is owned by `bytesprofile.Profile`; this file does not add state or persistence behavior.

Dependencies and integration: depends on `github.com/cockroachdb/pebble/internal/bytesprofile`. It is a public metrics integration point for code that reports or consumes separated value retrieval profiles without importing the internal package.

Risks and edge cases: as a type alias, API compatibility follows the internal profile type exactly. Changes to `bytesprofile.Profile` are exposed through this alias.

Test signals: no direct tests in the listed set.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/value_retrieval_profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics_test.go -->
## sources/storage-engines/pebble/metrics_test.go

Purpose: validates Pebble metrics formatting, metric values under DB operations, and several metric regressions.

Important APIs and functions: `exampleMetrics` constructs a populated `Metrics` snapshot for golden output. `TestMetrics` is datadriven over `testdata/metrics` with commands for DB initialization, batches, building SSTs, compaction, delayed flush state, flush, ingest, LSM dump, iterator open/close, metric rendering, metric value extraction, disk usage, additional block-write metrics, and problem spans. Regression tests cover remote table totals with virtual SSTables, write amp with WAL disabled, WAL bytes written monotonicity, and cumulative flushable memory bytes.

Control flow: `TestMetrics` opens DBs over MemFS with deterministic options, optional shared storage, value separation enabled, automatic compactions disabled, and high `MaxOpenFiles`. It waits for table stats before reading metrics, zeroes known nondeterministic cache/delete-pacer fields when commanded, and compares formatted output. Regression tests build focused DB states and assert exact invariants.

State and persistence: uses in-memory FS and remote storage, but exercises real Pebble state transitions: writes, flushes, compactions, ingests, virtual tables, iterators pinning obsolete files, and reopen stats loading.

Dependencies and integration: integrates metrics with DB operations, object storage provider, remote storage, vfs/errorfs latency injection, cache, delete pacer, block categories, testkeys comparer, and datadriven fixtures.

Risks and edge cases: golden metrics output can be brittle across architecture, timing, and reader-size changes; `StringForTests` normalizes several fields. The monotonic WAL test is time-bound and concurrency-sensitive.

Test signals: this is the primary behavioral signal for `metrics.go`, including redaction equivalence, remote virtual-table underflow regression, WAL monotonicity, and flushable memory accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/mid_key.go -->
## sources/storage-engines/pebble/mid_key.go

Purpose: implements `DB.ApproximateMidKey`, which returns an approximate key that bisects estimated disk usage within a key range using SST metadata and index blocks rather than data blocks.

Important APIs and types: `ApproximateMidKey(ctx, kr, epsilon)` returns `midKey`, estimated left-side size, and error. Internal helpers are `midKeySST`, `collectMidKeySSTs`, `resolveEdgeSizes`, `findMidKey`, and `mergeWalkStraddlers`.

Control flow: the public method validates DB open state and range order, loads the read state, collects overlapping SSTs across L0 sublevels and lower levels, resolves partial edge SST sizes until uncertainty is bounded by `2*epsilon`, rejects ranges too small relative to epsilon, then finds a mid key. `findMidKey` sorts SSTs by upper bound, accumulates effective sizes, returns an SST upper bound if within epsilon, or refines overshooting SSTs through `mergeWalkStraddlers`. The merge walk reads block index entries for sufficiently large straddlers and advances the smallest separator across files until the size deficit is reached.

State and persistence: no mutation or persistence. It reads current version metadata and index blocks through the file cache.

Dependencies and integration: depends on manifest table metadata, version overlap iteration, file-cache `estimateSize` and `collectBlockEntries`, sstable block entries, Pebble comparer, and `EstimateDiskUsage` semantics.

Risks and edge cases: result is approximate and may be nil for empty, tiny, or poorly splittable ranges. Edge-size scaling uses table size ratios for reference-inclusive size estimates. L0 is handled specially to avoid transitive bound expansion. Rounding can consume all SSTs without finding a key.

Test signals: `mid_key_test.go` exercises empty spans, tiny ranges, single SST, multiple L0 SSTs, multiple levels, and tight epsilon.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/mid_key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/mid_key_test.go -->
## sources/storage-engines/pebble/mid_key_test.go

Purpose: integration test for approximate disk-usage bisection by key.

Important APIs and functions: `TestApproximateMidKey` opens a MemFS Pebble DB with compression disabled and automatic compactions disabled, writes structured key ranges, then calls `ApproximateMidKey` for multiple scenarios.

Control flow: the test creates one large single-SST `b` range, four flushed L0 `c` SSTs, a `d` range split across L6 and L0 through compaction plus later flush, and a tiny `e` range. Cases assert nil for empty and tiny spans, and non-nil interior mid keys for single-SST, multiple-SST, multiple-level, and tight-epsilon ranges. For non-nil keys it estimates left and right disk usage and checks the left fraction is between 15% and 85%.

State and persistence: uses an in-memory DB but real flush/compaction state and SST index structures. Random 4KB values encourage one data block per key, improving index-block bisection coverage.

Dependencies and integration: integrates `ApproximateMidKey`, `EstimateDiskUsage`, flush/compaction, SST indexing, comparer ordering, and vfs MemFS.

Risks and gaps: thresholds are intentionally broad, so precision regressions within the 15%-85% band may pass. It does not test invalid range error handling or context cancellation during index reads.

Test signals: good coverage for the main algorithmic branches: no data, too small for epsilon, coarse SST-boundary split, merge-walk refinement, and multi-level overlap.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/mid_key_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/noop_readahead.go -->
## sources/storage-engines/pebble/objstorage/noop_readahead.go

Purpose: provides a trivial `ReadHandle` implementation for `Readable` implementations that do not support readahead or sequential-read optimization.

Important APIs and types: `NoopReadHandle` stores a `Readable`. `MakeNoopReadHandle` constructs it. Methods implement `ReadHandle`: `ReadAt`, `Close`, `SetupForCompaction`, and `RecordCacheHit`.

Control flow: `ReadAt` delegates directly to the underlying `Readable.ReadAt`. `Close`, `SetupForCompaction`, and `RecordCacheHit` are no-ops.

State and persistence: only holds a reference to the wrapped readable. It performs no buffering and persists nothing.

Dependencies and integration: used by `SimpleReadable.NewReadHandle` in `objstorage.go` and any simple object readers that cannot benefit from readahead.

Risks and edge cases: because `Close` is a no-op, lifetime remains governed by the underlying `Readable`. Implementations returning the same no-op handle must still respect concurrency expectations of `ReadHandle` callers.

Test signals: no direct tests in the listed set; behavior is indirectly covered through object readers using `SimpleReadable`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/noop_readahead.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorage.go -->
## sources/storage-engines/pebble/objstorage/objstorage.go

Purpose: defines Pebble's object-storage abstraction for immutable files such as SSTables and blob files, including read/write handles, metadata, provider operations, remote backing, and simple file-backed readable support.

Important APIs and types: `Readable`, `ReadHandle`, and `Writable` define object I/O contracts. `ReadBeforeSize` constants communicate readahead/read-before hints. `ObjectMetadata` identifies local, shared, and external objects. `CreatorID`, `SharedCleanupMethod`, `OpenOptions`, `CreateOptions`, `Provider`, `RemoteObjectBacking`, `RemoteObjectBackingHandle`, and `RemoteObjectToAttach` define provider-level management. Helpers include `Copy`, `IsLocalTable`, `IsExternalTable`, `Placement`, `NewSimpleReadable`, and `SimpleReadable`.

Control flow: `ObjectMetadata` methods classify placement and validate required fields. `Copy` loops in 256KiB chunks from a `ReadHandle` to a `Writable`. `Placement` treats provider lookup failures as local to handle disappeared local objects after reopen. `NewSimpleReadable` records file size, wraps a `ReadableFile`, and returns no-op read handles.

State and persistence: the interfaces define durability boundaries: writes become durable at `Writable.Finish`, object create/remove metadata durability requires provider `Sync`, and provider state may include local catalogs or remote metadata. `SimpleReadable` stores file handle and size only.

Dependencies and integration: central dependency for `objstorageprovider`, SST writers/readers, remote storage, shared cache metrics, vfs, and DB file placement metrics.

Risks and edge cases: `Writable.Write` may mutate input slices, which callers must respect. `ReadHandle` disallows parallel `ReadAt` calls. `SimpleReadable.NewReadHandle` returns the same no-op handle pointer, relying on statelessness. Unknown object placement defaults local, which is intentional but can hide catalog misses.

Test signals: provider and DB integration tests indirectly exercise these contracts; no direct tests in the listed file set.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_readable.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/cold_readable.go

Purpose: implements a readable wrapper for cold-tier objects whose metadata suffix has been copied to a hot local file for cheaper small metadata reads.

Important APIs and types: `newColdReadableWithHotMeta` constructs `coldReadableWithHotMeta`. The wrapper implements `objstorage.Readable`. `coldReadHandle` implements `objstorage.ReadHandle` over the same split-storage behavior.

Control flow: reads with offsets before `metaStartOffset` go to the wrapped cold readable. Reads entirely in the metadata suffix go to `readMetaAt`, which lazily opens the hot metadata file once via `sync.Once`. Reads that span both regions are conservatively served from cold storage because the full object exists there. Read handles ignore read-before optimization for metadata and create a cold read handle with `NoReadBefore`.

State and persistence: stores the cold readable, metadata FS/path/start offset, and lazily opened metadata file/error. Closing closes both cold and hot files if opened.

Dependencies and integration: used by the object storage provider's cold-tier path. Depends on `objstorage`, `vfs`, and `firstError` from provider utilities.

Risks and edge cases: split reads are not optimized and go cold. Hot metadata open errors are cached by `sync.Once`; transient open failures persist for the wrapper lifetime. `RecordCacheHit` clips reports to the cold portion only.

Test signals: no direct listed tests; cold-tier provider tests elsewhere would be expected to cover sidecar metadata reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_readable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_writable.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/cold_writable.go

Purpose: implements a writable wrapper that writes the full object to cold storage while duplicating the metadata suffix to a hot local metadata file after `StartMetadataPortion`.

Important APIs and types: `newColdWritable` constructs `coldWritable`, which implements `objstorage.Writable`. Key methods are `Write`, `StartMetadataPortion`, `flushMeta`, `Finish`, `Abort`, `deleteMetaFile`, and `metaPath`.

Control flow: before metadata starts, `Write` forwards to cold storage and increments `startOffset`. After metadata starts, `Write` copies bytes into an internal 4KiB buffer and flushes to the hot metadata file as needed, then writes to cold storage. `StartMetadataPortion` creates the hot metadata file and forwards the signal to the cold writer. `Finish` flushes/syncs/closes metadata first, finishes cold storage, then registers the metadata sidecar with the provider. `Abort` closes/removes the metadata file and aborts cold storage.

State and persistence: tracks metadata start offset, hot file handle, buffer, and sticky error. Durability is carefully ordered so a crash leaves either no metadata file or one discoverable/cleanable with the cold object.

Dependencies and integration: used by provider cold-tier creation. Depends on provider metadata path/registration methods, `vfs.File`, `objstorage.Writable`, and `firstError`.

Risks and edge cases: local `vfs.File.Write` may mangle input buffers, so the code copies before writing. Once `w.err` is set, subsequent calls return it. `StartMetadataPortion` is idempotent but repeated calls do not signal cold writer again.

Test signals: no direct listed tests; correctness should be covered by cold-tier creation/reopen/delete integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_writable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing.go

Purpose: defines the object-I/O tracing event schema shared by tracing-enabled and tracing-disabled builds.

Important APIs and types: `OpType` enumerates read, write, cache-hit, and setup-for-compaction operations. `Reason` captures high-level context such as flush, compaction, and ingestion. `Event` is the on-disk binary event format, including timestamp, op, reason, block kind, LSM level plus one, file number, read-handle ID, offset, and size.

Control flow: none; this file is schema declarations.

State and persistence: `Event` is explicitly the persisted trace record shape. Padding is hardcoded so struct layout is architecture-stable for trace files.

Dependencies and integration: used by `obj_io_tracing_on.go`, `obj_io_tracing_off.go`, trace-processing tools, and tracing tests. Depends on `base.DiskFileNum` and `blockkind.Kind`.

Risks and edge cases: binary trace compatibility depends on field layout and `unsafe` serialization in the on-build implementation. Adding fields or changing types requires trace reader coordination.

Test signals: `obj_io_tracing_test.go` reads raw trace files back into `Event` slices using `unsafe.Sizeof(Event{})`, validating the schema under the tracing build tag.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_off.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_off.go

Purpose: provides the no-op implementation of object-I/O tracing for normal builds without the `pebble_obj_io_tracing` build tag.

Important APIs and types: `Enabled` is false. `Tracer` is an empty struct. `Open` returns nil; `Close` is no-op; `WrapReadable` and `WrapWritable` return their inputs; `WithReason`, `WithBlockKind`, and `WithLevel` return the original context unchanged.

Control flow: all functions are pass-throughs to remove tracing overhead and side effects.

State and persistence: none. No trace files are created.

Dependencies and integration: selected by build constraint `!pebble_obj_io_tracing`. Provider code checks `objiotracing.Enabled` before opening/using a tracer, allowing tracing calls to compile away in regular builds.

Risks and edge cases: callers must guard nil tracer use through `Enabled`, as `Open` returns nil. Context metadata is intentionally discarded, so code must not rely on it outside tracing.

Test signals: `obj_io_tracing_test.go` skips when `Enabled` is false.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_on.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_on.go

Purpose: implements binary object-I/O tracing when built with `pebble_obj_io_tracing`, wrapping object readers, read handles, and writers to emit `Event` records to `IOTRACES-*` files.

Important APIs and types: `Enabled` is true. `Tracer` owns the filesystem, output directory, atomic handle IDs, worker channels, and worker goroutine. Wrappers `writable`, `readable`, and `readHandle` implement the object I/O interfaces. Context helpers store `ctxInfo` for reason, block kind, and level. `eventGenerator` buffers events locally before sending `eventBuf`s to the worker.

Control flow: `Open` starts the worker. Wrapper methods record events before delegating to underlying I/O; `Finish`, `Abort`, `Close`, and read-handle `Close` flush local buffers. Context metadata is merged with wrapper base metadata. The worker writes raw in-memory `Event` bytes through a buffered writer, rotates files after about 256MiB of events, and syncs/closes on shutdown.

State and persistence: persistent output is binary `IOTRACES-*` files in the provider directory. In-memory state includes per-wrapper event buffers, channel buffers, current trace file, and random/atomic handle IDs.

Dependencies and integration: used by `objstorageprovider.provider` when tracing is enabled. Depends on `unsafe` serialization, `vfs.NewSyncingFile`, context propagation from higher-level Pebble read/write paths, and `blockkind` metadata.

Risks and edge cases: worker errors panic. `readable.Close` flushes without locking around `mu.g`, so it assumes no concurrent reads during close. Channel send in `flush` can block under extreme event volume. Binary format assumes `Event` layout stability.

Test signals: tracing build-tag test checks reads, writes, flush/compaction reasons, L0/L6 levels, offsets, file numbers, and data-block reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_test.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_test.go

Purpose: integration test for object-I/O tracing under the `pebble_obj_io_tracing` build tag.

Important APIs and functions: `TestTracing` writes, flushes, compacts, closes, reads raw `IOTRACES-*` files back into `objiotracing.Event` values, and asserts important event fields.

Control flow: the test skips if tracing is disabled. It creates a MemFS DB, performs writes/flushes/compactions to generate read and write I/O, closes the DB to flush traces, collects and deletes trace files, counts matching events, then reopens and performs Gets to verify data-block read metadata.

State and persistence: trace files are persisted in MemFS as raw binary events. `collectEvents` reads whole files, checks their byte length is a multiple of event size, converts bytes to `Event` slices with `unsafe`, and removes files to isolate phases.

Dependencies and integration: integrates Pebble DB operations, object storage provider tracing wrappers, `vfs`, `blockkind`, and raw event schema layout.

Risks and gaps: assertions are mostly lower-bound existence checks rather than exact event sequences. It does not validate ordering or every context field. Unsafe conversion relies on event alignment and layout.

Test signals: confirms tracing captures reads and writes, file numbers, nonzero offsets, flush and compaction reasons, writes at L0 and L6, and L6 SSTable data-block reads after reopening.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/provider.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/provider.go

Purpose: implements the concrete `objstorage.Provider` coordinating local filesystem objects, optional cold tier, optional shared/remote storage, shared-cache metrics, object metadata cataloging, durability syncs, checkpoint protection, and optional object I/O tracing.

Important APIs and types: `provider` stores settings, tracer, local/remote subsystems, known object metadata, and protected object counts. `Settings` configures local FS, cold tier, cleaner, sync behavior, readahead, and remote cache/shared-storage settings. `ReadaheadConfig` atomically stores informed/speculative modes. Public provider methods include `Open`, `Close`, `OpenForReading`, `Create`, `Remove`, `Sync`, `LinkOrCopyFromLocal`, `Lookup`, `Path`, `Size`, `List`, `Metrics`, and `CheckpointState`; metadata helpers manage known/protected objects.

Control flow: `open` fills defaults, initializes maps, starts tracing if enabled, then initializes local and remote subsystems. `Create` chooses shared remote storage when preferred/configured, otherwise local/cold VFS creation, adds metadata, and wraps tracing. `OpenForReading` looks up metadata, opens local or remote readable, maps missing remote objects to not-exist/corruption errors where appropriate, and wraps tracing. `Remove` removes local files or unreferences shared objects, preserving metadata on retryable removal failures. `LinkOrCopyFromLocal` hard-links/copies locally when possible, otherwise streams through provider create/finish. `CheckpointState` validates and protects listed files, then checkpoints the remote catalog.

State and persistence: `knownObjects` is the in-memory provider catalog initialized from local listings and remote catalog. `Sync` persists local and shared metadata changes. Protected counts prevent remote unref while backing handles or checkpoints need objects retained. Local/cold file durability uses syncing files and provider subsystem syncs.

Dependencies and integration: central implementation of `objstorage.Provider`; depends on local and remote subsystems, `remote.StorageFactory`, `vfs`, `objstorage` contracts, shared cache, tracing, Pebble base file numbering/types, and invariants.

Risks and edge cases: `knownObjects` is keyed only by `DiskFileNum`, with file-type mismatch checked at lookup. Remote removal has TODOs around deferred unref for protected objects. Failed local link/copy or streamed copy paths require callers to handle partially created objects. `isProtected` uses a full lock despite being read-like.

Test signals: object provider behavior is exercised by DB/object-storage integration tests; listed metrics tests use `objstorageprovider.Open` for shared storage and SST writing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/provider.go -->
