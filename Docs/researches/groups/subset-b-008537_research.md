# sources/storage-engines/pebble/metamorphic subset-b-008537 Research

Grouped research for Pebble metamorphic generator, operation execution, history comparison, key-manager invariants, run orchestration, and options generation.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/generator.go -->
# sources/storage-engines/pebble/metamorphic/generator.go

## Purpose
`generator.go` builds the randomized operation stream consumed by Pebble's metamorphic tests. It owns generation-time object lifetimes, random operation selection, iterator option mutation, key distribution calls, DB/batch/snapshot/external-object relationships, and deterministic cleanup operations. The generator deliberately constrains some random choices so replay remains comparable across many Pebble option configurations.

## Important APIs, Types, and Functions
- `GenerateOps(rng, n, kf, cfg) Ops` is the public entry point for producing an `Ops` slice from a `KeyFormat` and `OpConfig`.
- `generator` stores `cfg`, `rng`, `init`, generated `ops`, `keyManager`, `keyGenerator`, live object sets, object-to-DB maps, reader/iterator maps, snapshot bounds, iterator last options, and cached visible-key sets for prefix seeks.
- `iterOpts` and `iterFlags` model generated iterator bounds, key-type modes, masking suffixes, point suffix filters, L6 filter enablement, and maximum-suffix property use. `IsZero` and `String` preserve clone/default-option formatting behavior.
- `generate` maps `OpType` weights to generator methods, draws from `randvar.NewDeck`, appends final close operations through `dbClose`, and calls `computeDerivedFields`.
- Object lifecycle methods include `newBatch`, `newIndexedBatch`, `removeBatchFromGenerator`, `batchAbort`, `batchCommit`, `dbClose`, `dbRestart`, `newIter`, `newIterUsingClone`, `iterClose`, `newSnapshot`, `snapshotClose`, and `newExternalObj`.
- Writer/read operation generators include point writes, range tombstones, range keys, log data, apply/commit, ingest, ingest-and-excise, external file ingestion, gets, iterator movement, checkpoints, compactions, downloads, flushes, format ratchets, estimates, and replication.
- Utility methods `prefixKeyRange`, `generateDisjointKeyRanges`, `uniqueKeys`, `expRandInt`, `cmp`, `prefix`, and `resizeBuffer` support sorted valid key spans and low-allocation key construction.

## Control Flow and State
Generation starts with `initOp`, one or more DB IDs, and DBs in both `liveReaders` and `liveWriters`. Each generated operation is appended through `add`, which immediately updates `keyManager` so future generation has the expected key state. Random op choice uses a weighted deck, not independent draws, giving balanced TPCC-style operation coverage.

The live-object sets are the central safety mechanism. Batches are writers, indexed batches are readers and writers, snapshots are readers, and iterators are attached to readers. Closing or applying a batch removes it from all live sets and closes its iterators. Snapshot close similarly removes child iterators. `dbRestart` and final `dbClose` drain iterators, snapshots, and batches before closing/restarting DBs.

Iterator generation snapshots the reader's visible keys at creation time for better `SeekPrefixGE` target selection. `mutateOptions` and `iterSetOptions` vary bounds, key types, masking, suffix filters, L6 filters, and maximum-suffix properties while forcing a subsequent absolute positioning operation because relative iterator movement after `SetOptions` requires re-positioning. Bounded snapshots constrain iterator bounds and gets to generated disjoint spans.

Writer operations coordinate with `keyManager` to preserve user-level determinism. Single deletes are only generated for keys that the manager considers eligible. Applying, committing, ingesting, ingest-and-excising, or external-ingesting a batch may first synthesize point `Delete` operations for keys whose single-delete history would otherwise become nondeterministic after merging histories into the destination.

## State and Persistence Behavior
This file does not execute Pebble persistence itself; it emits operation objects that later do. It still models persistent effects at generation time through `keyManager.update`, object bounds, and object-to-DB association. External objects are represented as generated `externalObjTag` IDs after converting a batch into a reusable external SST object. Ingest and replication choices account for whether generated SST bounds overlap because failed ingestions must not mutate generation-time state.

## Dependencies and Integration Points
The generator depends on `ops.go` op structs and `OpType` values, `key_manager.go` for write history and eligible keys, key-format implementations for random keys and suffixes, `options.go` format-version constants, and parser-derived-field logic for replay. It imports Pebble APIs for key ranges and iterator key type constants, `sstable` for synthetic prefix/suffix metadata, `randvar` for deck distributions, and `base.Compare` utilities.

## Risks and Edge Cases
- The generation-time model must match runtime behavior closely; any operation that can fail after `keyManager.update` would desynchronize later single-delete and ingest decisions.
- Range delete tracking is discretized over known keys; comments note that batch range deletions may not cover keys generated later.
- External-file synthetic suffixes are disallowed when range deletes, range-key unsets, or overlapping range-key sets would make transformed keys ambiguous.
- Iterator bounds passed to eventually-file-only snapshots must remain within snapshot consistency ranges.
- `uniqueKeys` can panic after many failed attempts, so key generators must have enough keyspace.
- Multi-instance runs require same-DB batch applies and special config limitations.

## Test Signals
`generator_test.go` directly checks live-object bookkeeping for batches, indexed batches, snapshots, iterators, applies, and aborts; deterministic generation from the same seed; non-overlap from `generateDisjointKeyRanges`; and Cockroach suffix keyspace round-tripping. `key_manager_test.go` indirectly tests generator assumptions around preceding-key loading and single-delete conflicts.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/generator_test.go -->
# sources/storage-engines/pebble/metamorphic/generator_test.go

## Purpose
`generator_test.go` validates the random operation generator's determinism and its object-lifetime bookkeeping. It also tests helper behavior for disjoint snapshot ranges and CockroachDB-style suffix keyspace materialization.

## Important Tests and Helpers
- `TestGenerator` manually exercises `newBatch`, `newIndexedBatch`, `newIter`, `batchAbort`, `newSnapshot`, `snapshotClose`, and `writerApply` to verify live sets and maps are drained correctly.
- `TestGeneratorRandom` generates 1k-10k operations from a fixed seed across default and multi-instance configs, then regenerates ten times and diffs formatted operations.
- `TestGenerateDisjointKeyRanges` repeatedly checks that generated ranges are ordered and non-overlapping.
- `TestCockroachSuffixKeyspace` checks `cockroachSuffixKeyspace` conversion between `suffixIndex` and formatted MVCC suffix strings for several maximum logical timestamp values.

## Control Flow and State
The tests build generators with `randvar.NewRand`, `DefaultOpConfig`, `multiInstanceConfig`, and `newKeyManager`. `TestGenerator` inspects internal generator fields such as `liveBatches`, `batches`, `readers`, `liveIters`, `iters`, `liveSnapshots`, `snapshots`, and `liveWriters`, ensuring close/remove paths erase secondary indexes as well as primary live lists.

`TestGeneratorRandom` intentionally reconstructs the RNG with `rand.NewPCG(0, seed)` for each generation and asserts formatted operation streams are byte-identical. That catches accidental use of global randomness inside generation paths.

## Dependencies and Integration Points
The file uses `cockroachkvs` formatting for suffix tests, `randvar` for deterministic random helpers, `difflib` for readable operation diffs, and `testify/require` assertions. It targets unexported generator internals within the same package, so it is tightly coupled to generator field names and lifecycle invariants.

## Risks and Edge Cases
- The deterministic generation test does not assert semantic quality of every generated operation, but it is strong at detecting hidden non-deterministic RNG sources.
- The lifecycle tests focus on representative close paths; new object kinds or live-object indexes should add analogous assertions.
- Disjoint key range testing samples generated ranges but does not prove all key formats and distributions.

## Test Signals
This is itself the test signal for `generator.go`. Failures here usually mean operation streams cannot be reproduced, object closure could race or leak, bounded snapshot ranges can overlap, or suffix-format assumptions changed.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/generator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/history.go -->
# sources/storage-engines/pebble/metamorphic/history.go

## Purpose
`history.go` records operation results and Pebble log output for metamorphic runs, normalizes concurrent histories into operation order, and compares histories from different option configurations. It is the deterministic observation layer that turns random execution into comparable text.

## Important APIs, Types, and Functions
- `history` wraps a stdlib `log.Logger`, an atomic error slot, an optional failure regexp, and a mutex-protected closed bit.
- `newHistory`, `Close`, `Recordf`, `Infof`, `Errorf`, `Fatalf`, and `Error` implement recording plus Pebble logger behavior.
- `historyRecorder` binds a `history` to one operation index and exposes `Recordf` and `Error` to individual op `run` methods.
- `CompareHistories` reads all history files, strips comment lines, reorders by operation index, and returns the first differing run plus a focused diff.
- `reorderHistory`, `extractOp`, and `readHistory` implement the normalization pipeline for multi-threaded operation output.

## Control Flow and State
Operations record one non-comment line through `historyRecorder.Recordf`; `history.Recordf` appends a trailing `#<op>` marker so later diffs can identify the logical operation even after comments are stripped. Pebble logger methods write comment-prefixed timestamped lines that are ignored by `readHistory` during comparison.

The mutex serializes writes and rejects operation records after `Close`, while informational/error log calls after close are suppressed. `Fatalf` records a comment log and stores the first fatal error. `Recordf` scans formatted output against `failRE`; a match stores a failure error used by execution loops to stop.

## State and Persistence Behavior
The file itself writes to any `io.Writer` passed into `newHistory`; in normal runs this includes an on-disk `history` file and optionally stdout. The comparison logic reads persisted history files from run directories. It deliberately strips `//` comment logs to prevent nondeterministic logging noise from affecting metamorphic equality.

## Dependencies and Integration Points
`history` implements Pebble's logger interface and is installed by `RunOnce` in `meta.go`. Every op in `ops.go` records through `historyRecorder`. `CompareHistories` is used by `Compare` and `RunAndCompare` to identify divergent option configurations. The file uses `crstrings.LinesSeq`, Cockroach errors, `difflib.SplitLines`, and `testify/require` for file-read assertions.

## Risks and Edge Cases
- `Recordf` panics if the format string contains newlines, because each operation must map to one reorderable history line.
- `extractOp` assumes every non-comment history line contains a trailing `#<op>` marker.
- `reorderHistory` panics if an operation index exceeds the number of lines, which indicates incomplete output despite successful execution.
- Comment stripping means differences only visible in Pebble logger output are intentionally ignored unless they trigger `failRE` or fatal state.

## Test Signals
`history_test.go` verifies comment log formatting, failure regexp detection, and data-driven history reordering. `meta.go` exercises the comparison pipeline during full metamorphic runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/history_test.go -->
# sources/storage-engines/pebble/metamorphic/history_test.go

## Purpose
`history_test.go` validates the history logger and reordering support used to compare metamorphic runs under concurrent execution.

## Important Tests
- `TestHistoryLogger` writes multi-line `Infof` and `Fatalf` messages, normalizes timestamps with a regexp, and checks exact `// HH:MM:SS.mmm TYPE: line` formatting.
- `TestHistoryFail` verifies `failRE` does not fail unmatched output, then stores an error when a recorded operation line matches.
- `TestReorderHistory` uses datadriven inputs in `testdata/reorder_history` to check operation-index reordering.

## Control Flow and State
The tests construct in-memory `bytes.Buffer` histories, call public methods, and inspect buffered strings or `h.Error()`. The reorder test delegates to `reorderHistory` after splitting input lines with `difflib.SplitLines`, mirroring production comparison.

## Dependencies and Integration Points
The file depends on `datadriven`, `difflib`, `testify/require`, and standard regex/string utilities. It is package-internal and directly tests unexported history helpers.

## Risks and Edge Cases
- Timestamp normalization keeps formatting deterministic while still checking that timestamps are present.
- The tests do not cover `Recordf after Close` panic behavior or `extractOp` malformed-line panics.
- The datadriven corpus is the main coverage for out-of-order concurrent history lines.

## Test Signals
Passing tests indicate comment log output remains ignorable, failure regexes are wired into `history.Error`, and concurrent execution histories can be normalized before comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/history_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/key_manager.go -->
# sources/storage-engines/pebble/metamorphic/key_manager.go

## Purpose
`key_manager.go` maintains generation-time metadata about keys, object histories, bounds, range-key usage, and single-delete eligibility. Its main job is preserving deterministic operation streams despite Pebble APIs whose results depend on user-level invariants, especially `SingleDelete` and ingest semantics.

## Important APIs, Types, and Functions
- `keyMeta` tracks one `(objID, key)` history; `keyHistory` and `keyHistoryItem` represent chronological write operations.
- `bounds` models inclusive or end-exclusive object key bounds with validation, overlap checks, and expansion.
- `keyManager` owns `byObj`, sorted global keys, global key maps, sorted prefixes, and prefix maps for a `KeyFormat`.
- `objKeyMeta` stores per-object key histories, object bounds, range tombstone/range-key flags, and range-key-set spans.
- Public-to-generator methods include `SortedKeysForObj`, `InRangeKeysForObj`, `KeysForExternalIngest`, `ExternalObjectHasOverlappingRangeKeySets`, `getSetOfVisibleKeys`, `addNewKey`, `checkForSingleDelConflicts`, `update`, `knownKeys`, `knownKeysInRange`, `prefixes`, `prefixExists`, and `eligibleSingleDeleteKeys`.
- Helpers `loadPrecedingKeys`, `opWrittenKeys`, and `insertSorted` seed later cross-version runs from prior ops.

## Control Flow and State
Each generated op is fed to `keyManager.update`. Point sets and merges append value operations. Deletes clear DB histories or append delete markers on batches. Range deletions are discretized over known keys in range and expand object bounds. Range-key operations expand bounds and set flags. Applies and commits merge batch metadata into the destination writer and remove source batch metadata. Ingests collapse batch histories first, skip state mutation for predicted overlapping-SST failures, and merge only successful source objects into the target DB.

Single-delete safety is modeled in two layers. `eligibleSingleDeleteKeys` enforces an object-local invariant by checking the tail of each key's history. `checkForSingleDelConflicts` evaluates whether merging a source object's history into a destination could expose more than one value before an unbounded single delete; generator code uses returned keys to insert regular deletes before the risky merge.

External ingestion logic transforms keys with synthetic prefixes/suffixes, restricts them to generated bounds, retains only one key per prefix for external-object construction, and checks for duplicate resulting keys. Synthetic suffix use is rejected when range delete/unset or overlapping range-key sets could create invalid logical conflicts.

## State and Persistence Behavior
The manager is an in-memory model of runtime persistence effects. It records only metadata needed for future generation, not values. Bounds approximate SST key coverage to predict ingest overlap failures. After `loadPrecedingKeys`, non-DB object metadata is discarded so subsequent runs retain previous DB state while avoiding conflicts with old transient object IDs.

## Dependencies and Integration Points
The manager consumes op structs from `ops.go`, `OpType` helpers, `KeyFormat` comparers, Pebble key ranges, and generator external-object metadata. It is called by `generator.add`, key generators for global-key registration, cross-version setup in `meta.go`, and tests. Its correctness is coupled to actual runtime semantics in `ops.go` for batch collapse, ingest, delete clearing, and external ingestion.

## Risks and Edge Cases
- Range deletions are approximated by known keys only; comments flag incomplete modeling for keys generated after a batch range deletion.
- `getSetOfVisibleKeys` uses unsafe conversion from map string keys to byte slices; callers must treat returned keys as read-only.
- `ExternalObjectHasOverlappingRangeKeySets` sorts `meta.rangeKeySets` in place, mutating stored order.
- Generation assumes `update` is called only for operations whose effects are predictable; runtime failures can invalidate manager state.
- Ingest collapse semantics must stay aligned with `ingestOp.collapseBatch`.

## Test Signals
`key_manager_test.go` checks key/prefix insertion, datadriven single-delete and bounds behavior, `opWrittenKeys` coverage for all method constructors, preceding-key loading, and random key-in-range generation. Generator tests and full metamorphic runs provide integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/key_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/key_manager_test.go -->
# sources/storage-engines/pebble/metamorphic/key_manager_test.go

## Purpose
`key_manager_test.go` validates key-manager bookkeeping, single-delete invariants, operation key extraction, prior-run key seeding, and key-generator in-range behavior.

## Important Tests and Helpers
- `TestKeyManager_AddKey` verifies sorted global keys, prefix extraction through the key format, duplicate suppression, and `prefixExists`.
- `mustParseObjID` and `printKeys` support datadriven commands.
- `TestKeyManager` runs `testdata/key_manager` commands for reset, add-new-key, bounds, keys, singledel-keys, conflicts, and parsed op updates.
- `TestOpWrittenKeys` iterates over `methods` constructors to ensure every operation type is accepted by `opWrittenKeys`.
- `TestLoadPrecedingKeys` generates ops, loads them into a new manager/key generator, and checks previous keys/prefixes are represented.
- `TestGenerateRandKeyInRange` tests all known key formats by generating random ranges with distinct prefixes and asserting generated keys fall within `[start,end)`.

## Control Flow and State
The datadriven test mutates a shared `keyManager` across commands until `reset`. For `op` commands, it parses formatted operation text with undefined objects allowed, updates the key manager, and echoes the formatted operation. This exercises the same parse/update path used when seeding cross-version runs from prior ops.

## Dependencies and Integration Points
The file uses `datadriven`, `crstrings.LinesSeq`, Pebble key ranges, `randvar`, parser support, and `knownKeyFormats`. It is tightly coupled to method registration through `methods`, because `TestOpWrittenKeys` is intended to fail when a new operation lacks `opWrittenKeys` handling.

## Risks and Edge Cases
- Datadriven coverage is only as complete as `testdata/key_manager`.
- `TestLoadPrecedingKeys` uses subset checks because original generation may create keys that never appear in operations and may not sample distribution maxima.
- Range generation tests avoid equal prefixes because `RandKeyInRange` requires distinct split prefixes.

## Test Signals
Passing tests signal that the generator can safely choose single deletes, that cross-version runs can import previous interesting keys, and that new op types are not silently omitted from preceding-key discovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/key_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/meta.go -->
# sources/storage-engines/pebble/metamorphic/meta.go

## Purpose
`meta.go` orchestrates full metamorphic test runs: building options, generating operations, launching child test executions, replaying one run, comparing histories, and providing run-level options. It is the package's top-level harness for "same logical operations under different Pebble configurations should produce equivalent histories."

## Important APIs, Types, and Functions
- `RunOption` and implementations configure `RunAndCompare`: `Seed`, `ExtendPreviousRun`, `UseDisk`, `UseInMemory`, `OpCount`, `RuntimeTrace`, `InnerBinary`, `ParseCustomTestOption`, `AddCustomRun`, `KeepData`, `InjectErrorsRate`, `MaxThreads`, `OpTimeout`, `FailOnMatch`, `MultiInstance`, and `TreeStepsMode`.
- `runAndCompareOptions`, `buildRunAndCompareOpts`, and `buildOptions` collect defaults, custom runs, standard options, random options, previous-run metadata, and initial state.
- `RunAndCompare` generates ops, writes the shared `ops` file, writes each run's `OPTIONS`, invokes child test processes in parallel, and compares histories.
- `RunOnce` is the child-run entry point. It reads `ops` and `OPTIONS`, parses them, configures FS/error injection/latency/initial state, initializes a `Test`, executes ops, and persists history.
- `Execute` replays operations serially or across goroutines using receiver-based hashing and `opsWaitOn` dependencies.
- `Compare`, `CompareHistories`, `lineByLineDiff`, `hashThread`, `readFile`, and `TestingT` support comparison and testing integration.

## Control Flow and State
`RunAndCompare` chooses a seed, creates a timestamped meta directory, chooses an op count and preset config, optionally loads prior ops through `loadPrecedingKeys`, generates formatted ops, and writes them once for all child runs. It builds a deterministic list of standard, custom, and random option names, then starts one child process per option under an `execution` subtest. Each child re-enters the top-level test with `--run-dir` pointing at its run directory.

After executions finish, `RunAndCompare` compares every history against the first option's history after comment stripping and operation reordering. On divergence it prints seed, focused diff, option strings, ops path, and a reduction command before exiting.

`RunOnce` does the actual replay. It parses serialized options into `defaultTestOptions`, wraps the configured filesystem with latency and injected read errors, handles tree-steps single-threading, bounds configured thread count, clones initial state if requested, fixes WAL failover/multi-instance incompatibilities, opens the history file, initializes `Test`, and executes. It prints LSM details for unclosed DBs and saves in-memory data on failure or keep mode.

`Execute` serially steps when `Threads <= 1`; otherwise each goroutine owns operations whose receiver hashes to its thread and waits on dependency channels computed by `newTest`/`computeDerivedFields`.

## State and Persistence Behavior
The harness writes a meta directory containing `ops`, one run directory per option, each run's `OPTIONS`, histories, data directories, optional runtime traces, and kept in-memory FS snapshots. It removes the meta directory after success unless `KeepData` is set. Initial-state extension copies prior persisted data and uses previous ops to seed interesting keys.

## Dependencies and Integration Points
This file integrates every other assigned file: `generator.go` for ops, `options.go` for test options, `ops.go` for replay, `history.go` for recording/comparison, and `key_manager.go` for preceding-key load. It also depends on parser support, `Test` construction/execution helpers, Pebble VFS/errorfs, randvar distributions, `errgroup`, and Go test subprocess behavior.

## Risks and Edge Cases
- Child process failures are reported with truncated history tail, but `os.Exit(1)` in compare paths bypasses normal `testing.T` cleanup.
- Multi-instance mode disables or adjusts WAL-related behavior and uses a restricted preset config.
- Error injection wraps read operations and must be paired with op retry behavior to avoid false divergences.
- History comparison ignores logger comment lines, so only recorded op outcomes participate in equality.
- `RunOnce` exits the process on replay error, which is appropriate for child mode but important for callers.

## Test Signals
This file is primarily covered by package-level metamorphic tests and options tests. `history_test.go` covers comparison primitives; `options_test.go` exercises `RunOnce` in `TestBlockPropertiesParse`; generator/key-manager tests cover operation construction used by `RunAndCompare`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/meta.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/ops.go -->
# sources/storage-engines/pebble/metamorphic/ops.go

## Purpose
`ops.go` defines the operation interface and all concrete operations replayed by the metamorphic harness. Each operation knows how to format itself, run against a `Test`, expose synchronization dependencies, rewrite its user keys for reduction/simplification, and provide diagram ranges.

## Important APIs, Types, and Functions
- `Ops`, `op`, `treeStepsOp`, `UserKey`, and `UserKeySuffix` define the shared operation model.
- Initialization and lifecycle operations: `initOp`, `newBatchOp`, `newIndexedBatchOp`, `batchCommitOp`, `closeOp`, `newSnapshotOp`, `newExternalObjOp`, `dbRestartOp`.
- Writer operations: `applyOp`, `deleteOp`, `singleDeleteOp`, `deleteRangeOp`, `flushOp`, `mergeOp`, `setOp`, `rangeKeyDeleteOp`, `rangeKeySetOp`, `rangeKeyUnsetOp`, `logDataOp`.
- Ingestion/replication operations: `ingestOp`, `ingestAndExciseOp`, `ingestExternalFilesOp`, `replicateOp`, `externalObjWithBounds`.
- Reader/iterator operations: `getOp`, `newIterOp`, `newIterUsingCloneOp`, `iterSetBoundsOp`, `iterSetOptionsOp`, `iterSeekGEOp`, `iterSeekPrefixGEOp`, `iterSeekLTOp`, `iterFirstOp`, `iterLastOp`, `iterNextOp`, `iterNextPrefixOp`, `iterCanSingleDelOp`, `iterPrevOp`.
- DB operations: `checkpointOp`, `downloadOp`, `compactOp`, `dbRatchetFormatMajorVersionOp`, `estimateDiskUsageOp`.
- Helpers include `formatOps`, `iterOptions`, `iteratorPos`, `validityStateToStr`, `onlyBatchIDs`, `closeIters`, `ingestOp.collapseBatch`, shared/external replicate helpers, and `hashSize`.

## Control Flow and State
Every `run` method retrieves objects from `Test`, calls the relevant Pebble API, and records a formatted outcome through `historyRecorder`. `formattedString` must be parseable by the metamorphic parser and stable across runs. `receiver` and `syncObjs` drive concurrent execution ordering: operations with the same receiver hash to the same thread, while additional dependencies prevent races with batches, DBs, snapshots, external objects, and newly created IDs.

Write operations use runtime test options to select variants such as `DeleteSized`, `SingleDelete` replacement, `ApplyNoSyncWait`, ingest-via-apply, excise simulation, shared/external replication, downloads disabled, and EFOS snapshots. Iterator operations serialize validity and position, including point value, range bounds, range keys, and `RangeKeyChanged`. Limit-based iterator operations map both exhausted and at-limit states to a deterministic `"invalid"` string.

Ingestion paths are complex. `ingestOp.run` either collapses a single batch and applies it, or builds local SSTs with blobs, closes batches, and calls `IngestAndExciseWithBlobs` without an excise span. `collapseBatch` reproduces ingest semantics by applying range deletions first, keeping only the latest point op per user key, and copying range keys verbatim from the batch. `ingestAndExciseOp` builds one ingest SST, optionally performs real `IngestAndExciseWithBlobs`, or simulates the excise through `DeleteRange` plus `RangeKeyDelete` before ingest.

External ingestion either emulates external-file ingest by building local truncated SSTs and calling `Ingest`, or constructs Pebble `ExternalFile` metadata with locator, object name, bounds, flags, and synthetic prefix/suffix. `replicateOp` scans a source DB over a span and either writes local SST contents for ordinary ingest after deleting destination range state, or preserves shared/external files through `ScanInternal` visitors and `IngestAndExcise`.

## State and Persistence Behavior
Operations mutate actual Pebble DBs, batches, snapshots, iterators, external storage, temporary SSTs, WALs, and histories. `initOp` sizes runtime object slots. `closeOp` clears `Test` object slots and flushes WAL-disabled DBs before close so kept data directories can seed later runs. Checkpoints write into `data/checkpoints/op-######`; ingest and replication create SST/blob files in test temporary storage; external-object creation writes remote SST objects.

## Dependencies and Integration Points
This file is the central integration layer with the Pebble public API, internal batch sorting, keyspan/rangekey internals, object storage providers, remote locators, VFS/errorfs, table writers, and treesteps. It consumes options from `TestOptions`, key formatting from `KeyFormat`, history recording, `Test` object accessors, retry policy, and generated fields computed after parsing/generation.

## Risks and Edge Cases
- `formattedString`, parser logic, and derived fields must stay in lockstep for reproducible reduce/compare workflows.
- Some API outcomes are nondeterministic by design; the code avoids recording nondeterministic return values for `CanDeterministicallySingleDelete` and normalizes iterator at-limit vs exhausted.
- Bounds slices passed to iterators are intentionally trashed after use to test Pebble's copying/lifetime assumptions.
- Checkpoint is no-op under shared/external storage because unsupported configurations would otherwise diverge.
- External object names include `rand.Uint64` to avoid collisions with initial state; formatted operation output does not include that object name, only the logical external object ID.
- Replication and excise no-op cases synthesize delete/range-key-delete behavior to preserve logical equivalence.

## Test Signals
`generator_test.go` and parser/reducer tests exercise formatting and generation. `options_test.go::TestBlockPropertiesParse` runs a small operation stream through `RunOnce`. Full metamorphic test suites are the primary coverage for the runtime behavior, with history diffs exposing divergence across option configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/options.go -->
# sources/storage-engines/pebble/metamorphic/options.go

## Purpose
`options.go` defines, serializes, parses, and randomizes the Pebble and test-only options used by metamorphic runs. It ensures every child run can persist an `OPTIONS` file, reconstruct a `TestOptions` value, and exercise a wide matrix of filesystem, compaction, WAL, iterator, remote-storage, value-block, and format-version behavior.

## Important APIs, Types, and Functions
- Constants `minimumFormatMajorVersion`, `defaultFormatMajorVersion`, and `newestFormatMajorVersionToTest` define the format-version range under test.
- `parseOptions` parses Pebble options plus `[TestOptions]` keys using `pebble.ParseHooks`, known key formats, filter policies, key schemas, and custom option parsers.
- `optionsToString` serializes Pebble options plus test-only fields and custom options.
- `defaultTestOptions` and `defaultOptions` build baseline options with mem FS, archive cleaner, key schema/comparer, block property collectors, bloom filter, ingest split default, value separation policy, and debug checking.
- `TestOptions` stores a `*pebble.Options`, replay thread count, retry policy, key format, custom options, and many test-only toggles.
- `CustomOption` allows external tests to serialize custom named options and hook close/open around DB restarts.
- `standardOptions` returns a fixed set of option variants.
- `RandomOptions` mutates a baseline into one randomized configuration.
- Utility functions include `expRandDuration`, `setupInitialState`, `filterPolicyFromName`, `randInRange`, and `randPowerOf2`.

## Control Flow and State
Serialized options are Pebble's `Options.String()` plus a `[TestOptions]` stanza. Parsing starts from defaults and lets unknown parse-hook entries toggle test-only behavior. Some toggles also update `pebble.Options` immediately, such as strict crashable FS, disk FS, block-property collector disablement, value block enablement, shared/external storage format requirements, secondary cache size, ingest split, excise enablement, delete-only compaction excises, and jemalloc size classes.

`RandomOptions` first optionally parses private options that are not exposed through public setters, then randomizes scalar Pebble options, closures, WAL failover, iterator stack, compaction heuristics, allocator classes, level options, compression, filter policies, FS mode, latency injection, thread count, ingest/delete/single-delete options, block properties, value blocks, remote storage, value separation, iterator tracking, EFOS seed, ingest splits, excise, delete-only compaction excises, and downloads. It calls `EnsureDefaults` at the end.

`setupInitialState` clones a prior run's `data` directory into the current FS while skipping archive/checkpoints/tmp, parses the previous OPTIONS file, and adjusts WAL recovery dirs so runs can switch between store-local WALs and separate WAL dirs or WAL failover.

## State and Persistence Behavior
Options are persisted as text `OPTIONS` files in each run directory and parsed by `RunOnce`. `setupInitialState` performs real VFS cloning from a previous on-disk state into the configured test FS. Default and random options choose between in-memory, crashable in-memory, and default disk filesystems; remote-storage toggles influence later object storage setup in `Test` and op behavior.

## Dependencies and Integration Points
The file integrates with Pebble options parsing/serialization, key formats and schemas, table filters, bloom/binaryfuse policies, WAL failover, VFS, remote storage options, value separation, sstable settings, and run orchestration in `meta.go`. Operation behavior in `ops.go` reads many `TestOptions` booleans to choose runtime code paths.

## Risks and Edge Cases
- Round-tripping closure-valued options requires tests to compare return values rather than function identity.
- Some booleans serialize only when true, and `parseOptions` panics if a test-only boolean is explicitly set to false.
- Random format versions must be raised when features require newer formats, such as shared objects, synthetic prefix/suffix, value separation, or virtual SSTables.
- WALDir and WAL failover compatibility during initial-state cloning is strict and returns errors on unexpected directory names.
- Random extremely small sizes improve coverage but can create many files; code adjusts L0 stop-write thresholds to reduce stalls.

## Test Signals
`options_test.go` validates initial-state cloning, full options round-trip for standard and random options, block property collector presence after `RunOnce`, and custom option parsing/serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/options_test.go -->
# sources/storage-engines/pebble/metamorphic/options_test.go

## Purpose
`options_test.go` validates option serialization/parsing, initial-state setup, block-property collector wiring, and custom test option support for the metamorphic harness.

## Important Tests and Helpers
- `TestSetupInitialState` builds a small on-disk Pebble DB, then checks `setupInitialState` clones its directory contents into the configured test FS.
- `TestOptionsRoundtrip` serializes every standard option and 100 random options, parses them back, reserializes, compares closure return values, and diffs `pebble.Options` while ignoring inherently non-comparable fields.
- `expectEqualFn` and `expectEqualValue` compare closure outputs, structs, and approximate float64s.
- `TestBlockPropertiesParse` runs generated ops through one `RunOnce`, walks produced SSTs, opens them, and asserts the default block-property collector wrote user properties.
- `TestCustomOptionParser` validates custom parser registration, custom option serialization through `optionsToString`, and reparse retention.
- `testCustomOption` is a simple `CustomOption` implementation.

## Control Flow and State
The round-trip test starts from `optionsToString`, parses into `defaultTestOptions`, and requires the serialized string to be stable. It then checks specific closure-valued fields including value blocks, ingest-as-flushable, ingest split, compaction concurrency, tombstone thresholds, value separation, deletion pacing, per-level compression/filter policy, max downloads, and block-property collector count.

`TestBlockPropertiesParse` creates a temporary meta directory, writes an `ops` file and a run `OPTIONS` file, executes `RunOnce` with `KeepData`, then scans the `data` directory for `.sst` files and opens them with the same reader options to find the collector property.

## Dependencies and Integration Points
The file uses real Pebble DB open/write/flush/close operations, VFS default and mem filesystems, `testkeys`, object storage readable wrappers, sstable readers, `pretty.Diff`, and the metamorphic `RunOnce` path. It is the main direct test for `options.go` and also lightly exercises `generator.go`, `ops.go`, and `meta.go`.

## Risks and Edge Cases
- Some option fields are ignored in diffs because they are pointers, closures, floats, or otherwise expected to differ by identity after parsing.
- Random options are time-seeded, so failures may need test logs to reproduce the serialized option.
- `TestBlockPropertiesParse` depends on generated operations producing at least one SST with the property; it uses 10k ops and archive cleaner to reduce flakiness.
- Initial-state cloning coverage checks directory entries but not every WAL recovery compatibility branch.

## Test Signals
Passing tests show `OPTIONS` files are stable, random option coverage remains parseable, default block-property collectors are active, and custom options survive the serialize/parse cycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/options_test.go -->
