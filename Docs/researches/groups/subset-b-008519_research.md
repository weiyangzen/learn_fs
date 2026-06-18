# subset-b-008519 research

Grouped research report for Pebble compaction scheduling, execution, delete-only compactions, and compaction picking. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction.go -->
# sources/storage-engines/pebble/compaction.go

## Purpose
`compaction.go` is Pebble's main compaction and flush execution engine. It models flushes, regular table compactions, move/copy optimizations, delete-only dispatch, ingested flushables, read-triggered compactions, and blob-producing compactions behind a shared `compaction` interface. The file bridges picker output into durable LSM changes by constructing compaction state, marking inputs as in-progress, building iterators over point keys, range deletions, and range keys, writing output table/blob objects, forming `manifest.VersionEdit` records, installing those edits, updating metrics, and cleaning up obsolete objects.

## Important APIs, Types, And Functions
The core type is `tableCompaction`, which implements `compaction` through `AddInProgressLocked`, `Execute`, `Info`, `PprofLabels`, `Tables`, `RecordError`, `Cancel`, and related accessors. It owns the version reference, input/output levels, bounds, grandparent overlap limits, tombstone elision policy, flush/delete-only-specific state, iterator state, metrics, grant handle, object creation options, and annotations.

Important supporting types and constants include `compactionKind`, `ErrCancelledCompaction`, `errEmptyTable`, `compactionLevel`, `compactionWritable`, `compactionMetrics`, `manualCompaction`, and `readCompaction`. Construction helpers include `newCompaction`, `newFlush`, `maybeSwitchToMoveOrCopy`, `adjustGrandparentOverlapBytesForFlush`, `newInputIters`, and `newRangeDelIter`.

Scheduling and lifecycle entry points are `maybeScheduleFlush`, `flush`, `flush1`, `maybeScheduleCompaction`, `makeCompactionEnvLocked`, `pickAnyCompaction`, `runPickedCompaction`, `Schedule`, `GetWaitingCompaction`, `GetAllowedWithoutPermission`, `tryScheduleDownloadCompactions`, `pickManualCompaction`, `compact`, `compact1`, `clearCompactingState`, `handleCompactFailure`, and `cleanupVersionEdit`.

Execution paths are split across `runCompaction`, `runDefaultTableCompaction`, `compactAndWrite`, `runMoveCompaction`, `runCopyCompaction`, `runIngestFlush`, and the delete-only hook in `compaction_delete.go`. Output and manifest helpers include `makeVersionEdit`, `newCompactionOutputTable`, `newCompactionOutputBlob`, `newCompactionOutputObj`, `validateVersionEdit`, and `getDiskWriteCategoryForCompaction`.

## Control Flow
Automatic compaction scheduling starts in `maybeScheduleCompaction` under `DB.mu` and the version-set log lock. It builds a `compactionEnv`, repeatedly schedules cheap delete-only compactions first, then download compactions, then delegates ordinary work to `CompactionScheduler`. If a picked compaction cannot run immediately, it is stored in `pickedCompactionCache` and later consumed through `Schedule`/`GetWaitingCompaction`. `runPickedCompaction` converts a `pickedCompaction` into a concrete `compaction`, marks it in progress, and starts `DB.compact` in a goroutine.

Flush scheduling starts with `maybeScheduleFlush`, which checks immutable memtables and `passedFlushThreshold`, sets the single flushing flag, and starts `flush`. `flush1` chooses either a prefix of regular flushables or exactly one `ingestedFlushable`, constructs `newFlush`, marks it in progress, writes normal flush output with `runCompaction` or builds ingest placement edits with `runIngestFlush`, then installs the version edit with `UpdateVersionLocked`. It updates `MinUnflushedLogNum`, flush metrics, read state, table stats, file-only snapshot transitions, flushable references, obsolete file deletion, and `flushed` notifications.

Normal compactions run through `compact1`. It emits `CompactionBegin`, calls `runCompaction`, translates close-time context cancellation into `ErrCancelledCompaction`, and, on success, validates and installs the version edit. During manifest application it checks `c.cancel` so concurrent excise or ingest-split operations can force a retry and clean up newly created objects. It then clears compacting state, updates compaction metrics, decrements in-progress write bytes, emits `CompactionEnd`, updates read state/table stats on success, and returns.

`runCompaction` dispatches by compaction kind. Delete-only compactions are handled in `compaction_delete.go`; move compactions produce only a manifest edit that deletes the input level entry and adds the same metadata at the output level; copy compactions allocate a new table number and either copy an external virtual span through `sstable.CopySpan` or link/copy a local table into shared storage; default compactions release `DB.mu`, run `compactAndWrite`, and re-acquire the mutex before returning.

`compactAndWrite` builds a compaction iterator stack over point keys, range deletions, and range keys, configures `compact.IterConfig` with snapshots, tombstone/range-key elision, bottommost-data-layer detection, and API-misuse callbacks, and drives `compact.Runner`. For each output span it consults `SpanPolicyFunc`, chooses table writer options and value-separation policy, creates a table object, and writes through `runner.WriteTable`. It checks `c.cancel` between outputs and syncs the object provider after a successful run.

Input iterator construction validates manifest ordering, expands L0 input slices into sublevels, creates level iterators for point keys, opens range deletion iterators per file so they can be merged independently, opens level-style range-key iterators when needed, and uses no-close wrappers so keyspan iterators remain alive until compaction completion. Flushes instead build iterators directly from flushables. Multiple point iterators are merged with `newMergingIter`; range deletion and range key iterators are merged with `keyspanimpl.MergingIter`, with range keys additionally defragmented.

## State And Persistence Behavior
The persistent output of a successful compaction is a `manifest.VersionEdit` plus newly created table/blob objects. `makeVersionEdit` records deleted input tables, new blob files, new output tables with bounds/stats/blob references/sequence metadata, and metrics for bytes read, bytes written, tables compacted, and blob bytes compacted or flushed. `runMoveCompaction`, `runCopyCompaction`, `runIngestFlush`, and `runDeleteOnlyCompaction` produce specialized edits.

`tableCompaction.version.Ref()` pins the version and all referenced table/blob metadata until `Execute` finishes. Input `TableMetadata` entries are marked `CompactionStateCompacting` in `AddInProgressLocked`; successful normal compactions move them to `CompactionStateCompacted`, while move and delete-only compactions revert them to not compacting because the same table metadata may remain usable. Rollbacks always reset to not compacting. L0-specific organizer state is updated when L0 compactions start and reinitialized when compacting state is cleared.

`compactionWritable` increments both per-compaction bytes and version-set in-progress compaction bytes on every write. `clearCompactingState`, `incrementCompactions`, `incrementCompactionBytes`, and duration accounting feed the metrics layer. `calculateDiskAvailableBytes` refreshes cached free-space state after compactions/flushes and reports low-space signals through the event listener.

Failure cleanup is explicit. If `runDefaultTableCompaction` creates output objects but cannot produce a valid edit, it records those objects as obsolete and zombie so the version set can delete them later. If a version edit is constructed but later cancelled during manifest application, `cleanupVersionEdit` marks new tables, new blobs, and unused backings obsolete. Obsolete file deletion is delayed until after read-state changes drop old-version references.

## Dependencies And Integration Points
This file is integrated with most of Pebble's storage core: `manifest.Version`, `VersionEdit`, `L0Organizer`, table metadata and level slices; `compact.Iter`, `compact.Runner`, snapshots, tombstone elision, and value separation; `sstable` readers/writers, block read environments, blob value fetching, table copying, and writer options; `objstorage.Provider` object creation, linking, removal, syncing, tracing, and shared/external placement; DB mutexes, version-set log lock, compaction scheduler grants, event listeners, problem spans, file cache stats, snapshots, memtable flush queues, WAL log numbers, ingest split/excise machinery, and metrics.

The picker contract comes from `pickedCompaction`/`pickedTableCompaction` in `compaction_picker.go`, while delete-only execution comes from `compaction_delete.go`. Blob-file rewrite compactions satisfy the same `compaction` interface elsewhere. External API surfaces include flush, manual compaction, download, read-triggered compaction scheduling, and event listener `FlushBegin/End`, `CompactionBegin/End`, `TableCreated`, and `BlobFileCreated` callbacks.

## Risks
The main correctness risk is concurrency around `DB.mu`, the version-set log lock, input compacting flags, and manifest installation. A compaction may release `DB.mu` while doing IO, so every persisted change must be validated against cancellation and installed only under `UpdateVersionLocked`. Missing a cancellation after an excise or ingest split could write or install files covering deleted/replaced key ranges.

Move and copy compactions are optimization paths with strict preconditions: exactly one start-level input, no output overlap, no extra-level data, acceptable grandparent overlap, and storage-placement constraints. Copy compactions additionally reject blob references and shared-table copies. Any relaxation must preserve table identity, cache semantics, blob reference accounting, and object cleanup.

Range tombstone and range key handling is subtle. The file intentionally avoids a single level iterator for range deletions because file-local tombstone ordering may not match level order after previous compaction splitting. Prematurely closing keyspan iterators or assuming range tombstones are globally ordered can corrupt compaction iteration.

Flush behavior must preserve WAL invariants. Large batches sharing a WAL with a memtable must flush with that memtable, `MinUnflushedLogNum` must advance only after durable output, and ingested flushables must be flushed one at a time because target level selection depends on the current LSM after earlier queue entries.

Disk-space heuristics are approximate. `expandedCompactionByteSizeLimit` and flush grandparent overlap adjustment reduce but do not eliminate the chance of overly wide or overly numerous output files. `calculateDiskAvailableBytes` may be stale when disk usage is changing quickly.

## Test Signals
Strong test coverage should exercise regular compactions, L0-to-base compactions, intra-L0 compactions, multi-level compactions, move/copy compactions across local/shared/external storage, blob references and value separation, range deletion/range key inputs, split user-key prevention, manual compaction retry, read-triggered compaction width limiting, flush WAL invariants, ingested flushables, excise cancellation, and failure cleanup of partially created objects.

Existing signals referenced by the file include compaction kind string synchronization through `AllCompactionKindStrings`, metamorphic tests for unusual range tombstone ordering, event-listener-driven tests for compaction/flush summaries, and delete-only tests in `compaction_delete_test.go`. Useful fault-injection tests should force object creation errors, object sync errors, manifest update cancellation, DB close during compaction, and low-disk-space reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_delete.go -->
# sources/storage-engines/pebble/compaction_delete.go

## Purpose
`compaction_delete.go` implements Pebble's delete-only compaction kind. A delete-only compaction is a cheap space-reclamation operation driven by wide tombstone hints: if a range tombstone fully covers a table, Pebble can remove the whole table from the LSM, or, when the tombstone covers an edge span and virtual SSTables are available, excise the covered span and keep the remaining portion as a virtual table. Unlike normal compactions, it does not merge keys or write replacement data through the compaction runner.

## Important APIs, Types, And Functions
`tryScheduleDeleteOnlyCompaction` checks feature flags and concurrency, asks `d.mu.compact.wideTombstones.PickCompaction` for a candidate, constructs `newDeleteOnlyCompaction`, marks it in progress, and starts the common `DB.compact` lifecycle.

`newDeleteOnlyCompaction` creates a `tableCompaction` with `compactionKindDeleteOnly`, one input level containing the selected table, `deleteOnly` metadata from `tombspan.DeleteOnlyCompaction`, a no-op grant handle, a referenced current version, and bounds equal to the selected table's user-key bounds.

`runDeleteOnlyCompaction` produces the durable manifest edit. It either adds the selected table to `DeletedTables` and increments `TablesDeleted`, or calls `exciseTable`, applies the resulting left/right replacement through `applyExciseToVersionEdit`, increments `TablesExcised`, and annotates the compaction as `[excise]`.

`tombstoneKeyTypeFromKeys` converts a set of `keyspan.Key` tombstone kinds into the manifest key-type enum used by wide tombstone hinting, distinguishing point-range-delete-only, range-key-delete-only, and mixed cases.

## Control Flow
Scheduling requires delete-only compactions to be enabled, automatic compactions to be enabled, and `d.mu.compact.compactingCount` to be below the configured maximum compaction concurrency. Excise support is gated by `FormatVirtualSSTables` and the optional `EnableDeleteOnlyCompactionExcises` setting. The wide tombstone picker receives the current version and the excise-allowed flag, then returns either no candidate or a `tombspan.DeleteOnlyCompaction`.

Once launched, delete-only compactions use the same goroutine and event lifecycle as other table compactions through `DB.compact` and `compact1`. During execution, `runCompaction` dispatches `compactionKindDeleteOnly` to `runDeleteOnlyCompaction`. That function releases `DB.mu` while doing possible excise IO, constructs a `VersionEdit`, refreshes available disk bytes, and returns to the common manifest-application path in `compact1`.

For a full-table delete, no replacement table is created: the edit simply removes `{Level, FileNum}`. For an excise, the code validates the format version, calls `d.exciseTable` with tight bounds, rejects middle-of-table excises that would produce both left and right replacements, and applies the excise into the version edit. Delete-only excises therefore appear intended for tombstones covering a table prefix or suffix rather than splitting a table into two live fragments.

## State And Persistence Behavior
Delete-only compactions persist only manifest metadata changes. A full-table delete records the input table in `VersionEdit.DeletedTables`. An excise records deletion of the old table and addition of zero or one replacement virtual table, depending on `applyExciseToVersionEdit`. The underlying table backing may remain referenced by virtual metadata after an excise, so physical deletion is governed by version-set obsolete-file tracking after version installation.

The selected version is explicitly referenced in `newDeleteOnlyCompaction`, matching normal table compactions. Input table metadata is marked compacting through `AddInProgressLocked`, but `clearCompactingState` treats delete-only as special and resets inputs to not compacting on success because some delete-only operations can leave the file untouched, for example if loose bounds prevent a removal.

Metrics are stored in `c.metrics.perLevel` for the selected level. Full deletes increment `TablesDeleted`; excises increment `TablesExcised` and add a compaction annotation. No output blob list and no `compact.Stats` are produced.

## Dependencies And Integration Points
This file depends on the common compaction lifecycle from `compaction.go`, tombstone hint selection from `internal/tombspan`, range key/tombstone kinds from `internal/keyspan` and `internal/base`, manifest edit structures, and DB excise helpers. It is called before scheduler-mediated compactions in `maybeScheduleCompaction`, reflecting the expectation that delete-only compactions are cheap and reduce later compaction work.

It also interacts with options and format gates: `DisableAutomaticCompactions`, `private.disableDeleteOnlyCompactions`, `CompactionConcurrencyRange`, `FormatVirtualSSTables`, and `EnableDeleteOnlyCompactionExcises`.

## Risks
The delete-only path bypasses normal key merging, so the correctness of candidate selection is critical. `wideTombstones.PickCompaction` must only return tables whose contents are fully obsolete or safely excisable under the current snapshots, bounds, and format version.

Excise handling intentionally rejects middle excises. If the picker ever returns a candidate requiring both left and right replacements, this path fails with an assertion error rather than producing a two-sided split. Format gating is also strict: an excise candidate below `FormatVirtualSSTables` panics.

Because delete-only compactions are scheduled outside `CompactionScheduler`, their concurrency check is a direct count against `maxConcurrency`. The loop in `maybeScheduleCompaction` can start multiple delete-only compactions as long as capacity remains, so wide tombstone picker overlap checks and compacting-state markings must prevent duplicate or conflicting deletes.

## Test Signals
Useful tests should cover full-table deletion, prefix/suffix excise, snapshots that prevent deletion, mixed point/range tombstone hint types, disabled feature flags, disabled automatic compactions, concurrency saturation, and format-version gating. `compaction_delete_test.go` provides datadriven coverage for hint collection, scheduling, excise annotations, LSM descriptions, snapshot closure, ingest interactions, and resulting compaction summaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_delete_test.go -->
# sources/storage-engines/pebble/compaction_delete_test.go

## Purpose
`compaction_delete_test.go` defines datadriven coverage for delete-only compaction hints and execution. It constructs in-memory Pebble DB states, forces table-stat collection to populate wide tombstone hints, triggers scheduling, inspects hint state, inspects compaction event summaries, verifies LSM layout changes, and exercises interactions with snapshots, flushes, batches, ingests, and manual compactions.

## Important APIs, Types, And Functions
The single test is `TestCompactionDeleteOnlyHints`. It uses `datadriven.RunTest` with commands `reset`, `define`, `batch`, `flush`, `get-hints`, `maybe-compact`, `compact`, `close-snapshot`, `iter`, `snapshot`, `ingest`, and `describe-lsm`.

The `reset` helper closes any previous DB and snapshots, creates an in-memory `vfs.NewMem` filesystem, enables newest format, enables delete-only excises, sets `DebugCheckLevels`, disables table stats by default for deterministic scheduling, configures single compaction concurrency, and installs an event listener that records `CompactionEnd`.

The `compactionString` helper waits for active compaction goroutines through `d.mu.compact.cond`, normalizes job IDs, durations, and file numbers, sorts compaction summary strings, clears the capture buffer, and returns deterministic text for datadriven comparison.

## Control Flow
Each datadriven command mutates or inspects the shared DB. `define` builds a DB from textual state and returns the current version string. `batch`, `flush`, `compact`, `ingest`, and `iter` delegate to existing test helpers. `snapshot` leaks the snapshot intentionally within the test scope so later `close-snapshot` can locate it by sequence number and test whether closing it unblocks delete-only compaction.

`get-hints` temporarily enables table stats and disables automatic compactions while forcing `collectTableStats` or waiting for an existing stats job. This isolates hint collection from actual compaction scheduling. It then returns `d.mu.compact.wideTombstones.String()`.

`maybe-compact` calls `d.maybeScheduleCompaction()` under `DB.mu`, prints the remaining wide tombstone hints, then prints normalized compaction summaries after waiting for launched jobs. `close-snapshot` closes a selected snapshot and returns any compaction summaries triggered by that closure. `describe-lsm` normalizes nondeterministic file numbers with a regexp.

## State And Persistence Behavior
Test state is entirely in-memory through `vfs.NewMem`, but it exercises the same manifest/version state as production Pebble. Captured `CompactionInfo` records are normalized before comparison. `compactInfo` is reset after each summary-producing command to keep datadriven outputs local to the command.

The test deliberately toggles `DisableTableStats` and `DisableAutomaticCompactions` around stats collection, because table stats are both the source of wide tombstone hints and a potential trigger for background compactions. It also closes all snapshots before DB reset/close to avoid leaking protected sequence numbers across test cases.

## Dependencies And Integration Points
The test integrates with Pebble's datadriven test infrastructure, DB definition/build/ingest/compact helper commands, leak detection, the in-memory VFS, event listeners, snapshot list internals, table stats collection, wide tombstone hint state, and compaction scheduling. It is the direct test signal for the production code in `compaction_delete.go` and for the wide-tombstone hint data maintained elsewhere.

## Risks
The test reaches into DB internals under `d.mu`, including snapshot lists, version strings, compact condition variables, and wide tombstone state. That gives strong coverage but makes the test sensitive to internal formatting, event summary text, and scheduling order. It mitigates nondeterminism by forcing single compaction concurrency, sorting compaction summaries, and replacing file numbers.

The helper intentionally lets snapshots remain unclosed until a later command, so any command sequence that forgets cleanup relies on the deferred `closeAllSnapshots`. The `get-hints` command unlocks around `collectTableStats` to avoid deadlock, which mirrors production lock concerns but requires careful relocking.

## Test Signals
Passing this datadriven test indicates that wide tombstone hints are collected deterministically from table stats, that delete-only compactions remove or excise the expected files, that snapshots delay deletion until safe, that compaction events are emitted with reason `delete-only` and excise annotations when appropriate, and that the LSM remains valid under debug level checks after flush, ingest, compact, and iterator verification commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/compaction_picker.go -->
# sources/storage-engines/pebble/compaction_picker.go

## Purpose
`compaction_picker.go` chooses which compaction Pebble should run next. It computes LSM shape targets, scores levels, accounts for in-progress compactions, picks L0/base/intra-L0 work, chooses positive-level seed files, expands compaction inputs safely, optionally upgrades single-level compactions to multi-level compactions, and selects lower-priority maintenance work such as elision-only, tombstone-density, virtual-SST rewrite, blob-file rewrite, read-triggered, marked-for-rewrite, manual, and download compactions.

## Important APIs, Types, And Functions
`compactionEnv` is the picker input snapshot: disk availability, earliest unflushed/snapshot sequence numbers, in-progress compaction summaries, read-compaction queue state, and problem spans. `compactionPicker` defines the picker interface used by the version set. `pickedCompaction` is the scheduler-facing abstraction that can report manual ID, construct a concrete compaction, and describe scheduler priority.

`pickedTableCompaction` is the main picked result. It holds kind, score, manual ID, start/output levels, inputs, base level, L0 compaction files, bounds, version, L0 organizer, and picker metrics. It is constructed by `newPickedTableCompaction`, `newPickedCompactionFromL0`, `newPickedManualCompaction`, `pickDownloadCompaction`, `pickAutoLPositive`, `pickL0`, and `pickedCompactionFromCandidateFile`.

`compactionPickerByScore` owns the current version, mutable latest-version state, base level, per-level max-byte targets, and DB size. Important methods include `initLevelMaxBytes`, `getMetrics`, `getBaseLevel`, `estimatedCompactionDebt`, `calculateLevelScores`, `getCompactionConcurrency`, `pickHighPrioritySpaceCompaction`, `pickAutoScore`, `pickAutoNonScore`, `pickElisionOnlyCompaction`, `pickRewriteCompaction`, `pickVirtualRewriteCompaction`, `pickBlobFileRewriteCompactionHighPriority`, `pickBlobFileRewriteCompactionLowPriority`, `pickTombstoneDensityCompaction`, `pickReadTriggeredCompaction`, and `forceBaseLevel1`.

Input expansion and conflict helpers include `setupInputs`, `maybeGrow`, `maybeGrowL0ForBase`, `setupMultiLevelCandidate`, `canCompactTables`, `outputKeyRangeAlreadyCompacting`, `conflictsWithInProgress`, and `areUserKeysOverlapping`. Scoring helpers include `calculateLevelSizes`, `calculateSizeAdjust`, `calculateL0FillFactor`, `pickCompactionSeedFile`, `tableCompensatedSize`, `tableTombstoneCompensation`, `totalCompensatedSize`, and `responsibleForGarbageBytes`. Multi-level policy is abstracted through `MultiLevelHeuristic`, `NoMultiLevel`, and `WriteAmpHeuristic`.

## Control Flow
A new `compactionPickerByScore` is created for the latest version under the version-set log lock. `initLevelMaxBytes` computes the first non-empty level, total DB size, base level, and per-level max sizes, taking in-progress L0 output into account. `calculateLevelScores` then computes L0 fill factor from L0 sublevel depth and file count, computes L1+ fill factors from compensated sizes and in-progress adjustments, divides by next-level fill factor to prioritize lower levels, applies compensated thresholds, and returns candidates sorted by descending score.

`pickAutoScore` iterates scored candidates. For L0 it calls `pickL0`, which first asks `L0Organizer.PickBaseCompaction` for L0-to-base work using base-level files and problem spans, then falls back to `PickIntraL0Compaction` if a base compaction cannot be chosen. For L1+ it selects a seed file with `pickCompactionSeedFile`, builds a compaction with `pickAutoLPositive`, and optionally calls `maybeAddLevel` for multi-level expansion.

`setupInputs` is the central safety step. It rejects already compacting files and problem-span overlaps, extends bounds from input files, finds overlapping output-level files, rejects compacting/problem output files, optionally expands inputs without increasing output overlap, generates L0 sublevel info for L0 inputs, and rejects output key ranges already being written by another in-progress compaction. Multi-level setup appends the next level and reruns `setupInputs` for the intermediate-to-new-output pair.

Seed selection for positive levels scans start-level files and output-level overlap in order. It skips compacting/problem files, computes overlapping output bytes, subtracts bottommost range-deletion estimates when snapshots permit, and picks the lowest scaled overlap ratio using a compensated input size that includes file size, estimated tombstone benefit, estimated external reference size, and virtual-backing garbage responsibility.

If no score-based work is found, `pickAutoNonScore` tries maintenance compactions in priority order: tombstone-density compactions, bottommost elision-only compactions, virtual SST rewrites, low-priority blob-file rewrites, read-triggered compactions, and marked-for-compaction rewrites. It also toggles read-compaction rescheduling when no read compaction is selected.

Manual compaction picking computes the appropriate output level, detects conflicts with in-progress compactions so the manual request can retry rather than disappear, uses overlaps in the requested range as inputs, ignores problem spans, and may use multi-level expansion. Download compactions rewrite or copy one file in place and ignore problem spans while preserving conflict checks through `setupInputs`.

## State And Persistence Behavior
The picker itself persists no manifest changes. Its outputs are in-memory `pickedCompaction` objects consumed by `compaction.go`. It does, however, derive decisions from persisted manifest state: level slices, table metadata stats/properties, marked-for-compaction flags, virtual backing usage, blob file stats, L0 organizer state, and sequence-number bounds.

In-progress compaction state affects scoring and selection. `calculateSizeAdjust` models outgoing and incoming bytes unless the in-progress compaction's version edit is already applied. `calculateL0FillFactor` subtracts in-progress L0 inputs from the file-count score. `outputKeyRangeAlreadyCompacting` prevents two compactions from writing overlapping key ranges to the same output level even if their input files do not overlap. `getCompactionConcurrency` derives allowed concurrency from configured lower/upper bounds, L0 read amplification, estimated compaction debt, and compactable garbage fraction.

Picked compactions carry metrics such as level scores and overlapping ratios into `tableCompaction.makeInfo`, making picker decisions visible through compaction events. They also preserve L0 sublevel information needed later by iterator construction.

## Dependencies And Integration Points
This file is tightly coupled to `manifest.Version`, `manifest.LevelSlice`, `manifest.L0Organizer`, table metadata annotations, virtual backings, blob file metadata, deletion-byte annotators, and problem spans. It integrates with `Options` for level sizing, compaction concurrency, L0 thresholds, tombstone-density thresholds, virtual-SST rewrite thresholds, value-separation policy, deprecated scoring behavior, and multi-level heuristics.

The scheduler-facing integration is through `WaitingCompaction` and `scheduledCompactionMap`, while execution integration is through `pickedTableCompaction.ConstructCompaction`, which calls `newCompaction` in `compaction.go`. Manual compactions use `manualCompaction` state from `compaction.go`; read-triggered compactions use `readCompactionQueue`; blob-file rewrite picking returns `pickedBlobFileCompaction` defined elsewhere.

## Risks
Picker correctness depends on choosing inputs that preserve LSM invariants and avoid concurrent output overlap. The L0 path is especially subtle because L0 files may overlap and are organized by sublevels; missing L0 sublevel expansion or base-level conflict information can reduce concurrency or produce overlapping outputs.

Scoring and compensation are heuristic. Tombstone estimates, virtual-backing garbage responsibility, external reference sizes, and next-level fill-factor division can over- or under-prioritize space reclamation. Several thresholds are intentionally approximate, such as the L0 score formula, tombstone-density overlap cap, and high/low-priority blob garbage ratios.

The picker runs while holding important locks, so algorithms that scan levels or annotations must remain bounded. `pickCompactionSeedFile` is linear in start and output levels; multi-level picking clones compactions and reruns setup; comments explicitly call out the need to keep this path fast.

Manual and read-triggered compactions must not silently disappear. Manual conflicts return `retryLater`; read-triggered compactions verify the target file is still present and cap output overlap width. Errors in these guards could lead to surprising no-ops or excessive write amplification.

## Test Signals
Strong tests should cover base-level calculation, per-level score ordering, L0 file-count and sublevel-depth scoring, in-progress size adjustment, problem-span exclusion, output key-range conflict detection, L0-to-base and intra-L0 picking, positive-level seed selection, multi-level heuristic choices, manual retry semantics, read-triggered width limits, elision-only snapshot gating, tombstone-density thresholds, virtual-SST rewrite thresholds, blob-file rewrite priority thresholds, and marked-for-compaction rewrites.

Useful integration signals include compaction event metrics showing selected scores and overlapping ratios, scheduler waiting priorities for each compaction kind, invariant checks that picked inputs are ordered and non-overlapping where required, and randomized/metamorphic tests that run concurrent flush, ingest, manual compaction, excise, and automatic compaction scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/compaction_picker.go -->
