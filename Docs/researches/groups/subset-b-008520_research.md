# subset-b-008520 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_picker_test.go -->
## sources/storage-engines/pebble/compaction_picker_test.go

Purpose: This file is a broad test suite for Pebble's compaction picker. It verifies level sizing, base-level and target-level choice, L0 sublevel handling, in-progress compaction exclusion, compaction concurrency, read-triggered and tombstone-density compactions, selected input expansion, output file size limits, compensated size accounting, and score reporting. It is test-only code, but it is tightly coupled to production picker types such as `compactionPickerByScore`, `pickedTableCompaction`, `compactionEnv`, `compactionInfo`, `manualCompaction`, and manifest metadata.

Important APIs/types/functions: `loadVersion` constructs synthetic versions from datadriven level-size descriptions. `parseTableMeta` and `parseCompactionLines` build `manifest.TableMetadata` and in-progress compaction records. The major tests are `TestCompactionPickerByScoreLevelMaxBytes`, `TestCompactionPickerTargetLevel`, `TestCompactionPickerEstimatedCompactionDebt`, `TestCompactionPickerL0`, `TestCompactionPickerConcurrency`, `TestCompactionPickerPickReadTriggered`, `TestPickedCompactionSetupInputs`, `TestPickedCompactionExpandInputs`, `TestCompactionOutputFileSize`, `TestCompactionPickerCompensatedSize`, `TestCompactionPickerPickFile`, and `TestCompactionPickerScores`. `alwaysMultiLevel` is a small heuristic forcing multi-level candidates. `pausableCleaner` lets score tests hold obsolete file cleanup.

Control flow: Most tests are datadriven. They parse an input LSM, create a `manifest.Version` and `latestVersionState`, initialize a picker, then issue commands such as `queue`, `pick`, `pick-auto`, `pick_manual`, `mark-for-compaction`, `problem-spans`, and `scores`. The test flow repeatedly marks chosen files compacting, updates L0 organizer state for started compactions, and resets compacting state between commands. Some tests use a real `DB` through `runDBDefineCmd` to exercise picker behavior with table stats, ingests, excises, and background scheduling.

State and persistence: Synthetic state lives in `manifest.Version`, `latestVersionState.l0Organizer`, `MarkedForCompaction`, file metadata compaction flags, and optional problem spans. The live DB tests use in-memory VFS state and deliberately pause cleaner behavior to observe score and file-size effects. No durable external state is created outside test files.

Dependencies and integration: The tests integrate with `manifest`, `problemspans`, `sstable` properties, `testkeys`, `datadriven`, and helper functions from `compaction_test.go` and `data_test.go` such as `newVersionWithLatest`, `runDBDefineCmd`, `runBuildCmd`, `runIngestCmd`, and `runTableFileSizesCmd`. They verify that picker order agrees with scheduler priority comments in `compaction_scheduler.go`.

Risks: The tests reach into internal fields and depend on exact string output, so harmless formatting changes or metadata ordering changes can break expectations. Picker tests also assume deterministic compaction selection after manually mutating `CompactionState`; missing L0 organizer updates would produce false failures. Real-DB tests can be sensitive to asynchronous table stats and cleaner timing, mitigated by explicit waits and the pausable cleaner.

Test signals: Strong coverage for level scoring, L0 compaction semantics, concurrency caps, read-triggered queue picking, multi-level heuristics, table boundary checks, compensated size from deletion estimates, marked-for-compaction behavior, problem span avoidance, and score metric output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_picker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_scheduler.go -->
## sources/storage-engines/pebble/compaction_scheduler.go

Purpose: This file defines the experimental compaction scheduling interface and Pebble's default `ConcurrencyLimitScheduler`. It lets a DB coordinate automatic/manual compactions with a scheduler that can enforce local or node-wide concurrency, while exposing grant handles for started compactions.

Important APIs/types/functions: `CompactionScheduler` declares `Register`, `Unregister`, `TrySchedule`, and `UpdateGetAllowedWithoutPermission`. `DBForCompaction` is the DB callback surface: `GetAllowedWithoutPermission`, `GetWaitingCompaction`, and `Schedule`. `WaitingCompaction` carries optionality, priority, and score for cross-work prioritization. `scheduledCompactionMap` and `manualCompactionPriority` map compaction kinds to ordering values. `noopGrantHandle` implements `CompactionGrantHandle` for paths without scheduler coordination. `pickedCompactionCache` caches a picked compaction when scheduling is denied. `ConcurrencyLimitScheduler` implements the scheduler and grant handle.

Control flow: `Register` stores the DB and starts a 100 ms periodic granter unless constructed for tests without periodic granting. `TrySchedule` samples `GetAllowedWithoutPermission`, grants immediately when allowed exceeds running count, and returns itself as the handle. `Done` decrements running count and enters `tryGrantLockedAndUnlock`, which serializes grant attempts, samples allowance, asks the DB whether a compaction is waiting, calls `Schedule`, and increments running count for each accepted grant. `UpdateGetAllowedWithoutPermission` samples allowance and pokes the periodic granter when the limit increased.

State and persistence: All state is in memory. Scheduler state includes `runningCompactions`, `unregistered`, `isGranting`, `lastAllowedWithoutPermission`, and poke/stop channels. `pickedCompactionCache` tracks `waiting` and an optional `pickedCompaction`; invalidation clears the picked compaction but intentionally preserves waiting status.

Dependencies and integration: The scheduler depends on `internal/base` grant-handle types and DB compaction internals for compaction kinds and picked compactions. It is called from DB scheduling paths and DB callbacks call back into scheduler grant handles. Comments document lock ordering: scheduler mutexes are generally after DBForCompaction mutexes, with explicit exceptions.

Risks: Deadlock risk is central because scheduler and DB call into each other. `Unregister` must wait for in-flight granting without holding DB locks. Incorrect `Done` accounting can overgrant or undergrant. If periodic granting or explicit pokes lag after flushes, cached compactions may wait despite increased allowance. The interface is experimental and may need richer priority/resource information.

Test signals: `compaction_scheduler_test.go` exercises immediate grants, periodic grants, explicit allowance updates, compaction completion, waiting counts, and unregister behavior through deterministic datadriven commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_scheduler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_scheduler_test.go -->
## sources/storage-engines/pebble/compaction_scheduler_test.go

Purpose: This file datadriven-tests `ConcurrencyLimitScheduler` using a fake DB and fake time source. It validates scheduler grant accounting and interaction with waiting compactions without depending on real compaction work.

Important APIs/types/functions: `testTimeSource` and `testTicker` implement `schedulerTimeSource` and `schedulerTicker`, exposing a manually driven channel. `testDBForCompaction` implements `DBForCompaction` and records `GetAllowedWithoutPermission`, `GetWaitingCompaction`, and `Schedule` calls into a string builder. `ongoingCompaction` stores a synthetic compaction index and grant handle. `TestConcurrencyLimitScheduler` handles datadriven commands: `init`, `set-allowed`, `set-waiting-count`, `try-schedule`, `tick`, `compaction-done`, and `unregister`.

Control flow: `init` constructs the scheduler with fake time, registers the fake DB, and enables `periodicGranterRanChForTesting`. `try-schedule` calls `TrySchedule`; on success the fake DB records a handle as running. `set-allowed` mutates the fake DB allowance and optionally calls `UpdateGetAllowedWithoutPermission`, waiting for the periodic granter if requested. `tick` manually sends a ticker event and waits for the scheduler to finish a grant pass. `compaction-done` looks up the stored handle and calls `Done`, which may synchronously schedule more work. `printAndReset` emits ongoing and waiting synthetic compactions after each step.

State and persistence: All state is in memory. The fake DB tracks `allowed`, `waitingCount`, `nextIndex`, and active handles. The scheduler tracks its internal running count independently; the test verifies consistency by observing scheduled handles and emitted callback traces.

Dependencies and integration: The test uses `datadriven`, `leaktest`, `slices.Delete`, and the production scheduler interfaces. It is isolated from the real DB but validates the exact callback order consumed by DB scheduling code.

Risks: The test checks textual call traces, so changes to callback ordering can require fixture updates. It does not exercise multi-DB/global schedulers, CPU measurement, or richer `WaitingCompaction` priority comparisons. It assumes that fake ticker sends and testing notification channel avoid races.

Test signals: Strong signal for the default scheduler's core behaviors: immediate admission under allowance, no admission when at limit, grant-on-Done, grant-on-periodic tick, grant-on-allowance-increase poke, and shutdown through `Unregister`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_scheduler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_test.go -->
## sources/storage-engines/pebble/compaction_test.go

Purpose: This is the main compaction behavior test suite. It validates compaction selection and execution, automatic flush/compaction behavior, manual compaction mechanics, version edit validation, tombstone and read-triggered compactions, corruption recovery, error cleanup/stat accounting, shared-object deletion pacing, marked-for-compaction persistence, value-separation related compactions, and tombstone-density move optimization.

Important APIs/types/functions: `newVersion` and `newVersionWithLatest` build manifest versions for picker tests. `compactionPickerForTesting` is a stub picker. `TestPickCompaction`, `TestAutomaticFlush`, `TestValidateVersionEdit`, `runCompactionTest`, `TestCompaction`, `TestCompactionOutputLevel`, `TestCompactionTombstones`, `TestCompactionReadTriggeredQueue`, `TestCompactionReadTriggered`, `TestCompactionAllowZeroSeqNum`, `TestCompactionErrorOnUserKeyOverlap`, `TestCompactionErrorCleanup`, `TestCompactionCheckOrdering`, `TestCompactFlushQueuedMemTableAndFlushMetrics`, `TestCompactFlushQueuedLargeBatch`, `TestFlushError`, `TestAdjustGrandparentOverlapBytesForFlush`, `TestCompactionInvalidBounds`, `TestMarkedForCompaction`, `TestCompaction_UpdateVersionFails`, `TestSharedObjectDeletePacing`, `TestCompactionErrorStats`, `TestCompactionCorruption`, and tombstone-density move tests are the key entry points.

Control flow: The file mixes table-driven tests with large datadriven harnesses. `runCompactionTest` opens an in-memory DB with deterministic event listeners and no periodic scheduler, then handles commands including `define`, `batch`, `build`, `compact`, `auto-compact`, `async-compact`, `async-compact-with-cancellation`, `add-ongoing-compaction`, `run-blob-rewrite-compaction`, `run-virtual-rewrite-compaction`, `set-span-policies`, logs, metrics, ingests, excises, and validation commands. Several tests create synthetic versions and compactions directly to validate picker and compaction object invariants. Error tests wrap VFS with injectors to force table-write or manifest-create failures.

State and persistence: Most persistent behavior uses `vfs.NewMem`, manifest `VersionEdit`, table/blob metadata, snapshots, table stats, object provider state, and remote in-memory storage. Tests deliberately mutate `d.mu` protected fields to create in-progress compactions, queued manual compactions, disabled auto compactions, fake span policies, and compaction scheduler counts.

Dependencies and integration: This file integrates nearly every compaction subsystem: `manifest`, `compact` tombstone elision, `objstorage`, `remote`, `sstable`, blob readers, error VFS, event listeners, snapshots, table stats, problem spans, and helpers from `data_test.go`. It also supplies helper constructors consumed by picker tests.

Risks: Many tests depend on asynchronous compaction/flush state and lock ordering. They mitigate nondeterminism through no-periodic scheduler construction, explicit condition waits, deterministic event formatting, fake time, and in-memory storage. The corruption test is intentionally long-running and skipped in slow builds. Direct mutation of DB internals means production refactors may require coordinated test updates.

Test signals: Very broad behavioral coverage for compaction correctness, manual/automatic scheduling interaction, cancellation, output cleanup, stats consistency after failures, manifest fatal errors, blob/virtual rewrites, external-file corruption handling, and tombstone-density move optimization boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_value_separation.go -->
## sources/storage-engines/pebble/compaction_value_separation.go

Purpose: This file decides how compactions interact with Pebble's value separation feature. It chooses between never separating values, preserving existing hot blob references, or writing values to new blob files, and computes blob reference depth for compaction inputs.

Important APIs/types/functions: `neverSeparateValues` is a `getValueSeparation` function returning `valsep.NeverSeparateValues`. `DB.determineCompactionValueSeparation` is the top-level decision point for table compactions and flushes. `shouldWriteBlobFiles` decides whether new blob files should be written and returns the output reference depth when preserving references. `compactionBlobReferenceDepth` computes a conservative depth from input levels. `uniqueInputBlobMetadatas` collects physical blob file metadata referenced by input tables and panics on missing blob files.

Control flow: `determineCompactionValueSeparation` first gates on format version, configured policy, and policy enabled flag. It gathers input blob metadata for non-flush compactions. It calls `shouldWriteBlobFiles`; if false, it constructs `valsep.NewPreserveAllHotBlobReferences` with the input blob set, reference depth, and policy thresholds. If true, it constructs `valsep.NewWriteNewBlobFiles` with comparer, blob object creation callback, blob writer options, policy thresholds, input physical files, short-attribute extractor, and an invalid-value misuse callback.

State and persistence: The function may create new blob files through `d.newCompactionOutputBlob`, updating compaction metrics bytes-written through the callback. Preserving references uses existing `manifest.BlobFileSet` metadata. `shouldWriteBlobFiles` mutates `c.annotations` with reason strings such as input depth zero, depth exceeded, min-size mismatch, suffix-disabled mismatch, and multiple span policies.

Dependencies and integration: It depends on `ValueSeparationPolicy`, `SpanPolicyFunc`, table metadata properties, `manifest.BlobReferenceDepth`, `objstorage`, `valsep`, and the event listener's `PossibleAPIMisuse` path for invalid short attribute extraction values. It is invoked by compaction construction/run paths whenever output table format supports value separation.

Risks: Policy comparison is subtle. Tables written with value separation disabled are intentionally tolerated until depth pressure requires rewrite. Span policy coverage is range-sensitive; if a file now spans multiple policies, values must be rewritten. L0 depth is approximated by summing sublevel maxima, while other levels sum per-level maxima, which is conservative rather than exact. Missing blob metadata triggers an assertion panic.

Test signals: `compaction_value_separation_test.go` covers flushes, virtual rewrites, low and exceeded reference depths, pre/post value-separation mixes, min-size mismatch, suffix mismatch, multiple span policies, and all-matching preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_value_separation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_value_separation_test.go -->
## sources/storage-engines/pebble/compaction_value_separation_test.go

Purpose: This file unit-tests `shouldWriteBlobFiles`, the core policy decision for compaction value separation. It verifies when compactions should preserve existing blob references versus rewrite values into new blob files.

Important APIs/types/functions: `makeTestTableMeta` constructs `manifest.TableMetadata` with point-key bounds, physical backing, blob reference depth, and value-separation-related sstable properties. `TestShouldWriteBlobFiles` defines a table of cases using `ValueSeparationPolicy`, `SpanPolicyFunc`, `compactionKind`, `compactionLevel`, and expected annotations.

Control flow: The test builds internal keys with `base.MakeInternalKey`, defines a default enabled policy with `MinimumSize` 512 and `MaxBlobReferenceDepth` 5, and uses a default span policy function that returns an empty policy. Each case builds a `tableCompaction`, calls `shouldWriteBlobFiles`, and asserts the boolean, returned reference depth, and mutation of `c.annotations`.

State and persistence: State is synthetic and in memory. The relevant mutable state is the `tableCompaction.annotations` slice and table metadata backing properties. No DB, filesystem, or blob files are created.

Dependencies and integration: The test depends on `internal/base`, `manifest`, `sstable.Properties`, and `require`. It directly targets production policy logic without involving `DB.determineCompactionValueSeparation` or `valsep` writer implementations.

Risks: The tests focus on single-file or simple two-level inputs and do not explicitly cover L0 sublevel depth summation, missing/invalid backing properties, span policy errors, `MinimumMVCCGarbageSize`, short attribute extractor callbacks, or `uniqueInputBlobMetadatas`. Because cases assert exact annotation strings and order, reason-label changes require test updates.

Test signals: The coverage is precise for decision boundaries: flush always writes, virtual rewrite preserves, low depth preserves, all pre-valsep writes, mixed pre/post does not eagerly rewrite, depth over max writes, property mismatches write, span policy coverage mismatch writes, and matching properties preserve with summed reference depth.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_value_separation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/comparer.go -->
## sources/storage-engines/pebble/comparer.go

Purpose: This small public API file re-exports comparer-related types and defaults from `internal/base` through the `pebble` package. It lets external users configure ordering, equality, abbreviated keys, separators, successors, and key splitting without importing internal packages.

Important APIs/types/functions: Type aliases expose `Compare`, `Equal`, `AbbreviatedKey`, `Separator`, `Successor`, `Split`, and `Comparer`. Variables expose `DefaultComparer` and `CheckComparer` from `base`.

Control flow: There is no runtime control flow beyond package initialization of the exported variables. Type aliases preserve identity with the internal base types.

State and persistence: No state is persisted. `DefaultComparer` and `CheckComparer` reference base package implementations and are shared configuration values used throughout DB options and test setup.

Dependencies and integration: The file depends only on `github.com/cockroachdb/pebble/internal/base`. It is an integration boundary between public Pebble APIs and internal key comparison code. Many files in this subset use `DefaultComparer.Compare` or `Options.Comparer`.

Risks: Since these are public exports, renaming/removing aliases would be API-breaking. Because aliases expose internal type identity, changes to `base.Comparer` shape propagate directly to public users. Tests in this subset assume `DefaultComparer` behavior for manifest ordering and boundary checks.

Test signals: No direct tests in this file. It is exercised indirectly by almost every compaction and datadriven test that constructs options, internal keys, versions, or table metadata with the default comparer.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/comparer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/data_test.go -->
## sources/storage-engines/pebble/data_test.go

Purpose: This file is the shared datadriven command harness used across Pebble tests. For this subset, it is especially important because compaction and picker tests use it to define DB state, build SSTs, run compactions, inspect layout/metadata/properties, ingest/excise files, parse DB options, and create synthetic value-separation blob references.

Important APIs/types/functions: Read commands include `runGetCmd`, `runIterCmd`, `parseIterOptions`, and `printIterState`. Data construction includes `runBatchDefineCmd`, `runBuildCmd`, `runBuildSSTCmd`, `runBuildRemoteCmd`, `runDBDefineCmd`, and `runPopulateCmd`. Compaction and LSM helpers include `runCompactCmdFn`, `runCompactCmd`, `runWaitForTableStatsCmd`, `runTableFileSizesCmd`, `runVersionFileSizes`, `runMetadataCommand`, `runSSTablePropertiesCmd`, `runLayoutCmd`, `runLSMCmd`, and `describeLSM`. Ingestion/excision helpers include `runExciseCmd`, `runExciseDryRunCmd`, `runIngestAndExciseCmd`, `runIngestCmd`, and `runIngestExternalCmd`. `parseDBOptionsArgs` maps datadriven args to `Options`. `defineDBValueSeparator` implements `valsep.ValueSeparation` for readable blob-reference fixtures.

Control flow: Command helpers parse datadriven input line-by-line, convert textual internal keys/range keys/blob references into Pebble operations, and return deterministic string output. `runDBDefineCmd` is the most complex path: it opens a DB, manually creates memtables/SSTables per declared level, simulates flush compactions, rewrites version edits to the requested level, ratchets sequence numbers, fabricates blob metadata when needed, applies a `VersionEdit`, updates read state, and waits for table stats.

State and persistence: Tests usually use in-memory VFS and remote storage, but the helpers create real table/blob objects inside that VFS. They mutate DB internals under `d.mu`, including versions, memtable queues, snapshots, table stats flags, span policy functions, and sequence numbers. `defineDBValueSeparator` accumulates blob metadata and blobtest values so datadriven fixtures can reference blob handles.

Dependencies and integration: This file integrates with `datadriven`, `crstrings`, `manifest`, `keyspan`, `rangekey`, `sstable`, `objstorage`, `remote`, `blobtest`, `valsep`, `wal`, `errorfs`, test key utilities, and public DB APIs. It is a central dependency for many tests beyond this subset.

Risks: The helpers intentionally permit invalid DB states so debug checks can catch them; this makes misuse easy. Direct internal mutation can fall out of sync with production invariants. String parsing is broad and must remain compatible with many fixture formats. Async table stats require explicit waits. Value-separation fixture logic fabricates metadata and should not be confused with production blob writing.

Test signals: Although not a test suite by itself, it enables high-signal datadriven tests for iteration, compaction, ingestion, table stats, value separation, external files, virtual tables, excision, and option parsing. Its command outputs form many golden-file assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/data_test.go -->
