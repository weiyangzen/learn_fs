# subset-b-008617 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable.h -->
# sources/storage-engines/rocksdb/db/memtable.h

## Purpose
`memtable.h` declares RocksDB's in-memory write buffer interfaces and the concrete `MemTable` implementation used before data is flushed into SST files. It separates the read-only contract (`ReadOnlyMemTable`) from the mutable `MemTable` so immutable memtables and alternate implementations, such as write-batch-with-index memtables, can be held by `MemTableList` and queried uniformly.

## Important APIs, types, and functions
`ImmutableMemTableOptions` captures the subset of immutable and mutable column-family options needed by memtables: arena sizing, prefix bloom settings, in-place update settings, merge operator, checksum protection, memory paranoia, per-key checksum verification, and batched lookup optimization.

`ReadOnlyMemTable` defines the shared interface for immutable and current memtables. Important read APIs are `NewIterator`, `NewTimestampStrippingIterator`, `NewRangeTombstoneIterator`, `NewTimestampStrippingRangeTombstoneIterator`, point `Get`, and `MultiGet`. Metadata APIs include memory usage, entry/delete/range-delete counts, `GetDataSize`, `GetFirstSequenceNumber`, `GetEarliestSequenceNumber`, `GetMinLogContainingPrepSection`, approximate stats, oldest key time, internal comparator, newest user-defined timestamp, and range tombstone cache readiness.

Flush and lifetime APIs on `ReadOnlyMemTable` include `Ref`, `Unref`, `MarkImmutable`, `MarkFlushed`, `SetID`, `SetNextLogNumber`, `GetEdits`, `SetFlushCompleted`, `SetFlushInProgress`, `SetFileNumber`, and `ReleaseFlushJobInfo`. `ProtectSealedBlobFiles` keeps direct-write blob files live until the memtable is fully unreferenced.

The concrete `MemTable` adds write APIs: `Add`, `Update`, `UpdateCallback`, `CountSuccessiveMergeEntries`, `BatchPostProcess`, dynamic `UpdateWriteBufferSize`, `RefLogContainingPrepSection`, `ShouldScheduleFlush`, `MarkFlushScheduled`, `ConstructFragmentedRangeTombstones`, `AddLogicallyRedundantRangeTombstone`, `BumpIngestSeqnoBarrier`, checksum verification, and newest-UDT tracking.

Static helpers `HandleTypeValue`, `HandleTypeDeletion`, and `HandleTypeMerge` centralize how point lookups interpret value, deletion, and merge records, including full merge invocation and raw operand collection.

## Control flow
Writes enter `MemTable::Add` or update paths, which encode internal keys into `MemTableRep`, update counters and memory estimates, optionally update prefix bloom and insert hints, and eventually mark the memtable for flush when memory/range-delete thresholds are crossed. Concurrent write batches aggregate counter deltas in `MemTablePostProcessInfo` and apply them with `BatchPostProcess`.

Point reads call `Get`, which checks range tombstones, scans the memtable representation for matching internal keys, honors snapshots and read callbacks, resolves blobs when needed, accumulates merge operands in `MergeContext`, and returns once it finds a final value, deletion, merge-in-progress boundary, or error. `MultiGet` applies the same lookup semantics over a `MultiGetContext::Range`.

When a mutable memtable is sealed, higher layers call `ConstructFragmentedRangeTombstones` and `MarkImmutable`; future reads can then reuse fragmented range tombstone structures. Flush code consumes iterators and `VersionEdit` metadata, then calls `MarkFlushed` after persistence is installed.

## State and persistence behavior
This header defines only in-memory structures, but it carries persistence metadata: `VersionEdit edit_`, `mem_next_walfile_number_`, `file_number_`, `atomic_flush_seqno_`, and `flush_job_info_`. These fields bridge the mutable write buffer to MANIFEST edits, WAL retention, atomic flush boundaries, and flush event reporting.

Memory state is tracked through `ConcurrentArena`, `AllocTracker`, table/range-delete reps, `DynamicBloom`, approximate memory counters, and mutable write-buffer size. Sequence state includes first sequence, earliest sequence, creation sequence, ingest barrier sequence, and the minimum WAL containing a prepared transaction section. User-defined timestamp state is stored as an atomic pointer into arena-owned key memory.

## Dependencies and integration points
`MemTable` integrates with `dbformat`, merge logic, range tombstone fragmentation, read callbacks, sequence-to-time mapping, version edits, allocators, concurrent arena, RocksDB options, `MemTableRep`, MultiGet, blob fetchers/partition managers, wide columns, and write-buffer management. `MemTableList` depends on this interface for immutable memtable lifecycle, reads, flush selection, history retention, and WAL recovery edits.

## Risks and edge cases
Most APIs require external synchronization unless the memtable is immutable; violating that contract risks use-after-free, stale range tombstone caches, or inconsistent counters. Merge handling is sensitive to operand order and whether the caller wants merged values or raw operands. Range tombstone conversion must respect the ingest sequence barrier to avoid shadowing newly ingested L0 data. Blob file protection must outlive column-family metadata. User-defined timestamp tracking depends on arena lifetime and atomic max updates.

## Test signals
Relevant coverage comes from `memtable_list_test.cc` for list-level point reads, history retention, flush lifecycle, and newest UDT queries; `merge_helper_test.cc` and `merge_test.cc` for merge semantics used by lookup helpers; and broader RocksDB memtable, write, flush, transaction, blob, timestamp, and range deletion tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable_list.cc -->
# sources/storage-engines/rocksdb/db/memtable_list.cc

## Purpose
`memtable_list.cc` implements immutable memtable list management for a column family. It serves reads from sealed memtables, tracks copy-on-write list versions used by SuperVersion readers, selects memtables for flush, installs flush results into the MANIFEST in recovery-safe order, retains flushed memtable history for transactions, and supports atomic flush across column families.

## Important APIs, types, and functions
Top-level scan helpers `MultiScanOverlapsUserKeyRange`, `MultiScanIteratorOverlapsUserKeyRange`, and `MultiScanIntersectsMemTable` conservatively decide whether a bounded multi-scan can skip an immutable memtable.

`MemTableListVersion` implements `AddMemTable`, `UnrefMemTable`, copy construction with refcount bumps, `Ref`, `Unref`, `Get`, `MultiGet`, `GetMergeOperands`, `GetFromHistory`, `GetFromList`, `AddRangeTombstoneIterators`, iterator addition, aggregate stats, earliest/first sequence queries, `Add`, `Remove`, history trimming, memory-limit checks, and newest UDT selection.

`MemTableList` implements flush state (`IsFlushPending`, `IsFlushPendingOrRunning`), `PickMemtablesToFlush`, `RollbackMemtableFlush`, `TryInstallMemtableFlushResults`, `Add`, `TrimHistory`, cached memory/history values, `InstallNewVersion`, `RemoveMemTablesOrRestoreFlags`, `PrecomputeMinLogContainingPrepSection`, secondary-replay cleanup via `RemoveOldMemTables`, and `GetEditForDroppingCurrentVersion`.

The free function `InstallMemtableAtomicFlushResults` installs multiple column-family flush results as one atomic MANIFEST group.

## Control flow
Reads search immutable memtables newest-to-oldest. `GetFromList` calls each memtable's `Get` with `immutable_memtable=true`, preserving the first visible sequence number and continuing through merge-in-progress statuses until a final value/deletion/error is found or lists are exhausted. `MultiGet` delegates to each memtable and stops once the range is empty. Iterator creation optionally probes bounded scan ranges and adds point and range-tombstone iterators to `MergeIteratorBuilder`.

Adding an immutable memtable calls `InstallNewVersion`, inserts at the front of the list, increments `num_flush_not_started_`, sets `imm_flush_needed` when transitioning from zero pending memtables, trims history if needed, and refreshes cached memory/history flags.

Flush picking iterates from oldest to newest so flush jobs receive increasing memtable IDs. It marks unstarted memtables as in progress, decrements `num_flush_not_started_`, tracks max next WAL number, and avoids selecting non-consecutive memtables when an in-progress flush is sandwiched between candidates.

Flush result installation first marks the flushed memtables complete with a file number. Only one thread enters the MANIFEST commit loop through `commit_in_progress_`. It repeatedly commits the oldest contiguous completed memtables, computes WAL recovery edits, writes `VersionEdit`s through `VersionSet::LogAndApply`, and removes or restores flags in the callback. This preserves FIFO MANIFEST order even when newer flush jobs finish first.

Atomic flush marks all participating memtables complete, builds per-CF edit lists, computes WAL retention for 2PC or non-2PC recovery, marks edits as an atomic group when multiple CFs participate, logs them through `VersionSet::LogAndApply`, then removes memtables or rolls back flags across all lists.

## State and persistence behavior
`MemTableListVersion` is a refcounted immutable view. Mutations install a new version if readers still hold the old one. Unflushed memtables live in `memlist_`; flushed history lives in `memlist_history_` when `max_write_buffer_size_to_maintain_` is positive. Memory accounting is pushed into the parent `MemTableList` usage counter and cached in atomics.

Persistence state is mediated by memtable `VersionEdit`s, file numbers, WAL numbers, `LogsWithPrepTracker`, `VersionSet`, and MANIFEST `LogAndApply`. On success, memtables are marked flushed and either moved to history or unreferenced. On failure or dropped-column-family cases, flags and edits are restored so data remains readable or flushable.

## Dependencies and integration points
This file integrates `ColumnFamilyData`, `VersionSet`, `DBImpl` recovery helpers, `LogsWithPrepTracker`, `RangeDelAggregator`, `MergeIteratorBuilder`, `LogBuffer`, `ThreadStatus`, `FSDirectory`, `FlushJobInfo`, scan range options, snapshots, and test sync points. It is on the critical path for DB reads, flush scheduling, atomic flush, WAL deletion, transaction validation, secondary log replay, and iterator construction.

## Risks and edge cases
Ordering is the main risk. MANIFEST commits must match memtable creation order, even with parallel flush completion. Rollback must restore only appropriate completed or in-progress flags. Dropped column families cannot lose in-memory data before their generated files are discoverable. History trimming must respect refcounts and memory budgets. Scan pruning is conservative because iterator errors, empty probes, and range deletions all force overlap. Copy-on-write versions require external DB mutex discipline.

## Test signals
`memtable_list_test.cc` exercises empty lists, point reads across immutable memtables, history lookups and trimming, flush pending/picking/rollback, out-of-order flush completion, atomic flush across CFs, and user-defined timestamp tracking. Broader signals include flush job, DB open/recovery, transaction validation, secondary instance, atomic flush, range deletion, MultiGet, and iterator tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable_list.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable_list.h -->
# sources/storage-engines/rocksdb/db/memtable_list.h

## Purpose
`memtable_list.h` declares the immutable memtable list abstraction used by RocksDB column families. It exposes read/query APIs through `MemTableListVersion`, mutable lifecycle and flush APIs through `MemTableList`, and the cross-column-family atomic flush install function.

## Important APIs, types, and functions
The scan helper declarations expose conservative overlap tests for bounded `MultiScanArgs`. `MemTableListVersion` is the refcounted read view. Its public APIs are `Get`, `MultiGet`, `GetMergeOperands`, `GetFromHistory`, range tombstone iterator aggregation, point iterator aggregation, aggregate entry/delete/stats queries, earliest/first sequence lookup, list ID accessors, not-flushed/flushed counts, and newest user-defined timestamp lookup.

Private `MemTableListVersion` APIs are available to `MemTableList` and atomic flush: `Add`, `Remove`, `HistoryShouldBeTrimmed`, `TrimHistory`, `GetFromList`, `AddMemTable`, `UnrefMemTable`, `MemoryAllocatedBytesExcludingLast`, `HasHistory`, and `MemtableLimitExceeded`.

`MemTableList` exposes atomics `imm_flush_needed` and `imm_trim_needed`, counts, flush-pending predicates, `PickMemtablesToFlush`, `RollbackMemtableFlush`, `TryInstallMemtableFlushResults`, `Add`, memory/history accessors, `TrimHistory`, unflushed memory/oldest-key-time estimates, explicit `FlushRequested`, trim scheduling, WAL-prep-section computation, memtable ID queries, newest UDT vectors, atomic flush sequence assignment, secondary replay cleanup, and `GetEditForDroppingCurrentVersion`.

`InstallMemtableAtomicFlushResults` is declared as a free function because it coordinates multiple `MemTableList` instances and multiple `ColumnFamilyData` objects.

## Control flow
The header documents the architectural split: `MemTableListVersion` is not thread-safe but immutable while its refcount exceeds one, making it suitable for readers through SuperVersion. `MemTableList` owns the current version and installs a new version under DB mutex when a mutation would otherwise modify a shared view.

Flush flow starts with `imm_flush_needed` or `FlushRequested`, moves through `PickMemtablesToFlush`, then ends in either `TryInstallMemtableFlushResults`, rollback, or atomic install. The public comments specify that memtables can flush concurrently but must be committed to the MANIFEST in FIFO order to preserve crash recovery.

Read flow uses the current version's `Get`, `MultiGet`, `GetMergeOperands`, iterators, and range tombstone aggregators. History flow is explicitly limited to in-memory-only queries such as transaction validation because flushed history duplicates data already persisted in SST files.

## State and persistence behavior
The header identifies the key state variables: `memlist_` for immutable unflushed memtables, `memlist_history_` for flushed retained history, `max_write_buffer_size_to_maintain_` for history memory budgeting, parent memory usage pointer, version refs, and list IDs. `MemTableList` adds minimum merge count, current version pointer, unstarted flush count, commit-in-progress flag, flush-request flag, cached memory/history atomics, and a monotonically increasing list version ID.

Persistence-facing APIs connect immutable memtables to `VersionEdit`, `VersionSet`, WAL retention, prepared transaction tracking, file metadata, DB directory syncing, and flush job info.

## Dependencies and integration points
The declarations depend on logs-with-prep tracking, memtable interfaces, range deletion aggregation, file naming, log buffers, mutexes, RocksDB DB/iterator/options/types, and `autovector`. Forward declarations tie the header to `ColumnFamilyData`, `InternalKeyComparator`, `MergeIteratorBuilder`, `VersionSet`, `FlushJobInfo`, and `FSDirectory`.

## Risks and edge cases
The header's synchronization comments are essential: except for the two atomics, callers must serialize access with DB mutex or write-thread discipline. `FlushRequested` can set the atomic even in benign races, but logic relies on `num_flush_not_started_` for correctness. Atomic flush ID and sequence APIs assume the list is ordered newest-to-oldest. `GetTablesNewestUDT` relies on ascending ID iteration from the back of the list.

## Test signals
`memtable_list_test.cc` maps closely to this API surface. Additional validation should cover SuperVersion ref/unref behavior, iterator reads with range tombstones, transaction validation through history, secondary replay cleanup, atomic flush recovery, and WAL retention with prepared transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable_list_test.cc -->
# sources/storage-engines/rocksdb/db/memtable_list_test.cc

## Purpose
`memtable_list_test.cc` unit-tests immutable memtable list behavior outside the full DB flush machinery. It constructs real `MemTable` objects, mock `VersionSet` state, and test column families to validate reads, history retention, flush scheduling, manifest installation, atomic flush, refcount cleanup, and user-defined timestamp tracking.

## Important APIs, types, and functions
`MemTableListTest` owns temporary DB state, options, column-family handles, and an atomic file-number generator. `CreateDB` opens a DB with default and two additional column families, optionally using a comparator with 64-bit user-defined timestamps.

`Mock_InstallMemtableFlushResults` builds a minimal `VersionSet`, default `ColumnFamilyData`, mutex, log buffer, file number, and flush job list, then invokes `MemTableList::TryInstallMemtableFlushResults`. `Mock_InstallMemtableAtomicFlushResults` creates matching CF metadata, dummy `FileMetaData` objects, and calls `InstallMemtableAtomicFlushResults`.

The tests are `Empty`, `GetTest`, `GetFromHistoryTest`, `FlushPendingTest`, `EmptyAtomicFlushTest`, `AtomicFlushTest`, `GetTableNewestUDT`, and `ConcurrentGetTableNewestUDT`.

## Control flow
`GetTest` starts with an empty list, creates skiplist memtables, inserts deletes, puts, preferred-seqno values, and merge operands, then validates direct memtable reads and list reads. It confirms newer immutable memtables override older ones, historical sequence lookups can see older values, and merge operands across memtables are combined through the configured string append operator.

`GetFromHistoryTest` configures a positive `max_write_buffer_size_to_maintain`, flushes memtables into history through the mock install path, verifies that normal `Get` no longer sees flushed data while `GetFromHistory` does, then adds another memtable to force history trimming and deletion of the oldest retained memtable.

`FlushPendingTest` builds six memtables and exercises transitions between requested flushes, threshold-triggered flushes, picked in-progress memtables, rollback, non-consecutive pick avoidance, out-of-order flush completion, FIFO commit installation, max memtable ID filtering, history retention, and final refcount deletion.

`AtomicFlushTest` constructs three independent `MemTableList`s, selects different flush ranges per column family, installs them atomically, and checks file numbers, not-flushed counts, and cleanup after unref.

Timestamp tests write keys with appended 64-bit timestamps and verify `GetTablesNewestUDT` returns per-table newest values in ascending ID order. The concurrent variant writes from multiple threads with concurrent memtable insert enabled, calls `BatchPostProcess`, and checks the atomically tracked maximum timestamp.

## State and persistence behavior
The tests intentionally exercise state that persists across memtable lifecycle transitions: `flush_in_progress_`, `flush_completed_`, file numbers, memtable IDs, list history, memory retention limits, `imm_flush_needed`, `flush_requested_`, `num_flush_not_started_`, `VersionEdit` installation, and refcounts. Mock `VersionSet::Recover` provides enough MANIFEST/WAL state to validate install logic without a full flush job.

## Dependencies and integration points
The test includes merge context, version set, write controller, write buffer manager, RocksDB DB/status APIs, test harness utilities, string utilities, and merge operators. It depends on real `MemTable` insertion and read code, real `VersionSet` recovery/logging paths, and real column-family handles.

## Risks and edge cases
The mock install helpers assume default CF layout and generated file metadata are sufficient for the install path. Tests directly call internal memtable APIs, so missing calls such as `ConstructFragmentedRangeTombstones` would trip assertions not seen through normal DB code. The out-of-order flush scenarios are critical because an apparent success can still leave newer memtables waiting for older commits.

## Test signals
This file itself is the primary test signal for `memtable_list.{h,cc}`. Passing it gives confidence in point lookup ordering, merge-through-list behavior, history retention/trimming, flush-pending state, rollback, FIFO flush result installation, atomic flush coordination, refcount reclamation, and UDT concurrency. Complementary DB-level tests should still cover crash recovery, actual SST creation, range tombstones, and column-family drop races.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable_list_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_context.h -->
# sources/storage-engines/rocksdb/db/merge_context.h

## Purpose
`merge_context.h` defines `MergeContext`, the small operand accumulator used while resolving RocksDB merge operations in memtables, version reads, and compaction. It preserves merge operands, copies unpinned slices, and can expose operands in either merge order or reverse traversal order.

## Important APIs, types, and functions
`empty_operand_list` is a shared empty vector returned when no operands have been initialized. `MergeContext` exposes a public `GetMergeOperandsOptions* get_merge_operands_options` used by raw merge-operand reads to control continuation.

`Clear` removes stored operands and copied storage without releasing the lazily allocated vectors. `PushOperand` appends a newly encountered operand while setting backward direction, which corresponds to newest-first traversal. `PushOperandBack` appends while setting forward direction. Both accept an `operand_pinned` flag; pinned operands are referenced directly, while unpinned operands are copied into owned `std::string`s.

`GetNumOperands`, `GetOperand`, `GetOperands`, `GetOperandsDirectionForward`, and `GetOperandsDirectionBackward` expose the accumulated operands. The direction accessors mutate internal ordering if needed by reversing `operand_list_`.

Private helpers `Initialize`, `SetDirectionForward`, and `SetDirectionBackward` lazily allocate storage and maintain the `operands_reversed_` flag.

## Control flow
Point lookups and compactions encounter records newest-to-oldest. They call `PushOperand` as merge operands are found, which leaves the logical order reversed/newest-first. When a full merge is attempted, callers use `GetOperands` or `GetOperandsDirectionForward`, causing a reverse if necessary so operands are passed to the merge operator in the documented merge order. When `MergeOperator::ShouldMerge` needs backward ordering, callers use `GetOperandsDirectionBackward`.

If a memtable value is being returned as a raw merge operand with `do_merge=false`, unmerged values can also be pushed into the context. The context copies any operand not pinned by the iterator/memtable so returned slices remain valid until the next mutation or clear.

## State and persistence behavior
`MergeContext` is purely in-memory and per-operation. Its owned strings provide temporary persistence for unpinned slices during a lookup or compaction step. Returned references are explicitly invalidated by subsequent calls that can reverse, clear, or append operands.

## Dependencies and integration points
The type integrates with `rocksdb/db.h` for `GetMergeOperandsOptions`, `rocksdb/slice.h`, memtable `Get`, `MemTableListVersion::GetMergeOperands`, `MergeHelper`, DB point reads, and compaction. It is a key ordering bridge between internal iterators that scan backward by sequence number and user merge operators that expect operands in application order.

## Risks and edge cases
The direction-changing accessors are `const` but mutate internal order. Callers must not hold references across later context calls unless they copy. Pinned operands require the underlying storage to remain valid for the context lifetime. Repeated direction flips reverse the vector in place and can be surprising in debugger traces. The public options pointer is not owned and must outlive the operation.

## Test signals
Merge ordering is indirectly validated by `memtable_list_test.cc`, `merge_helper_test.cc`, and `merge_test.cc`. Important signals are correct string append ordering across memtables, partial-merge output order, raw merge operand reads, and continuation callback behavior in memtable lookup paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_helper.cc -->
# sources/storage-engines/rocksdb/db/merge_helper.cc

## Purpose
`merge_helper.cc` implements merge resolution used mainly by compaction and by point lookup helper wrappers. It turns stacks of merge operands plus optional base values into final values, partial-merge operands, or merge-in-progress outputs while respecting snapshots, range tombstones, blob values, wide columns, compaction filters, user-defined timestamps, and shutdown.

## Important APIs, types, and functions
The constructor stores environment, clock, user comparator, merge operator, optional compaction filter, logger, snapshot state, snapshot checker, compaction level, statistics, shutdown flag, and `allow_single_operand_` from the merge operator.

`TimedFullMergeCommonImpl` invokes `MergeOperator::FullMergeV3`, records read merge operand histograms and merge operation time, maps failures to `Status::Corruption`, and returns the operator failure scope when requested.

Two `TimedFullMergeImpl` overloads translate V3 merge output. The iterator/compaction overload returns serialized data plus `ValueType`, supporting plain values, wide-column entities, and returned operand slices. The point-lookup overload fills either `std::string` or `PinnableWideColumns`, including default-column extraction when the caller requested a plain value.

`MergeUntil` is the main loop. `MergeOutputIterator` iterates the helper's last output. `FilterMerge` applies `CompactionFilter::FilterV4` to merge operands and validates `RemoveAndSkipUntil` targets.

## Control flow
`MergeUntil` starts at a merge record and copies the original internal key because iterator keys are invalidated by movement. It parses each internal key, skips range-delete sentinel keys, checks shutdown, stops at corruption when assertions are disabled, stops at a different user key, stops at timestamp GC boundaries, and stops before entries protected by `stop_before`/snapshot checker.

For non-merge base records, it full-merges queued operands with either no base, a plain value, an unpacked timed value, a fetched blob value, or a resolved wide-column entity. Range tombstones can cause an otherwise present base to be treated as no base. Successful full merge rewrites the newest queued key type to `kTypeValue` or `kTypeWideColumnEntity`, clears the operand stack, stores the result, and advances past the base record. Merge operator failures with `kMustMerge` are downgraded to `MergeInProgress` so operands are preserved.

For merge records, the helper optionally applies compaction filters unless the sequence is protected by the latest snapshot. Range tombstones can remove operands. Kept or changed operands are pushed into `MergeContext` with the matching key. `RemoveAndSkipUntil` clears output and records a skip target.

After iteration stops, the helper returns OK if all operands were filtered. If it is certain it has seen the entire key history (`at_bottom` plus next key/end and timestamp GC eligibility), it full-merges with no base and converts output to a value. Otherwise it returns `MergeInProgress` and attempts `PartialMergeMulti` when enough operands are available or the operator allows a single operand.

## State and persistence behavior
State is per-helper and invalidated on each `MergeUntil`: `keys_`, `merge_context_`, compaction filter skip target/value, filter timer totals, and status. No data is persisted directly, but returned keys/values drive compaction output, so mistakes affect SST contents and future recovery. The helper also updates perf counters, statistics ticks, blob read stats, and filter timing.

## Dependencies and integration points
The implementation depends on blob fetch/index/prefetch code, compaction iteration stats, internal key parsing/updating, wide column serialization/resolution, perf context, statistics, comparator timestamp APIs, internal iterators, range deletion aggregators, and compaction filters. It is used by compaction iterator logic and by memtable read helpers through `TimedFullMerge`.

## Risks and edge cases
Operand ordering, timestamp comparisons, and snapshot boundaries are delicate. Full merge over a base must not cross a visible snapshot. Blob indexes require a valid `BlobFetcher`. Wide-column V2 entity blobs must be resolved before V1 merge input. `RemoveAndSkipUntil` is ignored if it does not advance. Merge outputs larger than 4GB are rejected because block builders use 32-bit sizes. `kMustMerge` failure scope must preserve operands instead of dropping data.

## Test signals
`merge_helper_test.cc` covers bottom-level full merge, merge with base value, snapshot stop, non-partial operators, single operands, deletion bases, corrupt keys, compaction filtering, snapshot-protected filtering, and oversized partial merge rejection. `merge_test.cc` covers `TimedFullMerge` oversized full results and DB-level merge behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_helper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_helper.h -->
# sources/storage-engines/rocksdb/db/merge_helper.h

## Purpose
`merge_helper.h` declares `MergeHelper`, the compaction/read helper that resolves RocksDB merge operands, and `MergeOutputIterator`, a lightweight view over the last merge result. It defines the public merge helper contract, overload tags for base-value shapes, and the state exposed to compaction code.

## Important APIs, types, and functions
The `MergeHelper` constructor accepts `Env`, user comparator, merge operator, optional compaction filter, logger, internal-key assertion mode, latest snapshot, optional `SnapshotChecker`, compaction level, statistics, and shutdown flag.

`NoBaseValueTag`, `PlainBaseValueTag`, and `WideBaseValueTag` disambiguate `TimedFullMerge` overloads. The overloads construct `MergeOperationInputV3::ExistingValue` from no base, a plain slice, serialized wide-column entity, or `WideColumns`, then delegate to `TimedFullMergeImpl`.

`MergeUntil` consumes an `InternalIterator` positioned at a merge record and returns OK, `MergeInProgress`, `Corruption`, or `ShutdownInProgress`. It takes range deletion aggregation, a sequence boundary, bottommost/history certainty, error logging policy, blob fetcher, full-history timestamp lower bound, blob prefetch buffers, and compaction iteration stats.

`FilterMerge`, `keys`, `values`, `TotalFilterTime`, `HasOperator`, and `FilteredUntil` expose compaction-filter and output state. Private `TimedFullMergeCommonImpl` and `TimedFullMergeImpl` overloads perform merge invocation and output conversion. `IsShuttingDown` is a best-effort relaxed atomic check.

`MergeOutputIterator` binds to a `MergeHelper`, seeks to the first output, advances, and exposes key/value slices from reverse iterators over the helper's result containers.

## Control flow
The header documents that `MergeUntil` proceeds through operands until corruption, put/delete, different user key, snapshot boundary, compaction-filter skip, or iterator end. Results are stored in `keys()` and `values()` until the next `MergeUntil`. Successful full merge usually returns one key/value pair with the newest sequence and a value-like type. If a complete merge is impossible, the helper returns merge operands in traversal order for compaction to write forward.

`TimedFullMerge` is used by both compaction and point reads. Compaction uses the overload that exposes a serialized result and value type; point reads use the overload that translates V3 output into a plain value or `PinnableWideColumns`.

## State and persistence behavior
The helper holds transient output state only. `keys_` stores internal keys, and `merge_context_` stores corresponding operands. Filter state includes total nanoseconds, changed value buffer, and skip-until internal key. Although transient, this state determines compaction output records and therefore has persistence consequences when written into SST files.

## Dependencies and integration points
The declaration connects merge code with `MergeContext`, range deletion aggregation, snapshot checking, wide-column serialization, compaction filters, environment/clock timing, RocksDB merge operator APIs, slices, wide columns, stop watches, blob fetching, prefetch buffers, and compaction iteration stats. It is consumed by compaction iterators and memtable point-read helpers.

## Risks and edge cases
`MergeUntil` requires the input iterator's first key to be an uncorrupted merge key. `keys()` and `values()` lifetimes end at the next merge call. The helper's behavior changes based on `at_bottom`, `latest_snapshot_`, `SnapshotChecker`, timestamp lower bounds, and merge operator support for partial/single operand merges. Callers must supply blob fetch infrastructure when blob indexes can be encountered.

## Test signals
`merge_helper_test.cc` is the focused contract test for `MergeUntil` and `MergeOutputIterator`; `merge_test.cc` exercises `TimedFullMerge` and full DB integration. Wide-column and blob merge paths should be covered by broader wide-column/blob compaction tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_helper_test.cc -->
# sources/storage-engines/rocksdb/db/merge_helper_test.cc

## Purpose
`merge_helper_test.cc` validates `MergeHelper::MergeUntil` in controlled iterator scenarios. It uses an in-memory `VectorIterator` over synthetic internal keys to test operand accumulation, full merge, partial merge, snapshot boundaries, compaction filter interactions, corrupt keys, deletion bases, and oversized partial merge result rejection.

## Important APIs, types, and functions
`MergeHelperTest` owns an environment, internal key comparator, vector iterator, merge operator, optional `MergeHelper`, key/value vectors, and optional `test::FilterNumber`. `Run` constructs a `VectorIterator`, creates `MergeHelper`, seeks to first, and invokes `MergeUntil`. `AddKeyVal` appends encoded internal keys and values, with optional corruption of the key type.

Test cases include `MergeAtBottomSuccess`, `MergeValue`, `SnapshotBeforeValue`, `NoPartialMerge`, `SingleOperand`, `MergeDeletion`, `CorruptKey`, `FilterMergeOperands`, `FilterAllMergeOperands`, `FilterFirstMergeOperand`, `DontFilterMergeOperandsBeforeSnapshotTest`, and `LargePartialMergeResultRejected`.

## Control flow
The tests build ordered internal-key streams by hand. Bottom-level tests set `at_bottom=true` and a next user key to prove the helper can full-merge merge-only histories into a `kTypeValue`. Base-value and deletion tests confirm the helper merges queued operands with put/delete records and advances the iterator to the first non-consumed key.

Snapshot tests set `stop_before` so the helper stops before older records and returns `MergeInProgress`, preserving operands rather than crossing snapshot visibility. Non-partial and single-operand tests verify the fallback output when a complete merge is impossible. The corrupt-key test confirms the helper stops before a corrupt record and outputs merge-in-progress data when strict assertion mode is disabled.

Filter tests install `FilterNumber` to remove selected merge operands. They verify mixed filtering changes the final sum, all-filtered operands produce no merge output and leave surviving put/delete records for the caller, filtering can remove leading operands and lower the output sequence number, and operands at or below `latest_snapshot` are not filtered.

The large partial merge test defines a concatenating operator, creates operands around the 4GB boundary, forces the partial-merge path with `at_bottom=false`, and asserts corruption above the block-builder limit while accepting exactly `uint32_t::max()` bytes.

## State and persistence behavior
The test is memory-only, but it directly models compaction output. It checks iterator position after merge, output keys and values in `MergeHelper`, and whether output is OK, merge-in-progress, or corruption. Those are the same signals compaction uses to decide which records to write to new SSTs.

## Dependencies and integration points
The test depends on `dbformat`, RocksDB comparator APIs, test harness/utilities, fixed-width coding helpers, `VectorIterator`, and built-in merge operators. It intentionally bypasses DB and file layers to isolate merge helper decisions.

## Risks and edge cases
Because inputs are synthetic, the test must maintain correct internal-key order to represent real iterator streams. It does not cover blob or wide-column base values, timestamp GC lower bounds, shutdown, or `RemoveAndSkipUntil`; those need separate integration coverage. Big-memory tests are skipped without sufficient memory.

## Test signals
Passing this file gives focused confidence in merge compaction semantics: snapshot isolation, operand order, compaction-filter application, partial merge fallback, deletion base handling, corrupt key stopping, and size-limit enforcement.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_helper_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_operator.cc -->
# sources/storage-engines/rocksdb/db/merge_operator.cc

## Purpose
`merge_operator.cc` provides default backend implementations for RocksDB merge operator API evolution. It adapts older `FullMerge`/`FullMergeV2` operators to `FullMergeV3`, implements default multi-operand partial merging through pairwise `PartialMerge`, and implements associative merge behavior in terms of a simpler `Merge` callback.

## Important APIs, types, and functions
`MergeOperator::FullMergeV2` is the compatibility fallback for operators that only implement legacy `FullMerge`. It copies the `Slice` operand list into `std::deque<std::string>` and calls `FullMerge`.

`MergeOperator::FullMergeV3` adapts V3 inputs with variant existing values. For no base or plain base, it delegates to `FullMergeV2`. For wide-column existing values, it extracts the default column as the V2 base value if present, calls `FullMergeV2`, and then rebuilds a V3 `NewColumns` output preserving non-default columns.

`MergeOperator::PartialMergeMulti` loops over operands and invokes `PartialMerge` pairwise, carrying the latest merged result as the next left operand.

`AssociativeMergeOperator::FullMergeV2` repeatedly calls the user's associative `Merge` function over the existing value and each operand. `AssociativeMergeOperator::PartialMerge` calls `Merge` with the left operand as the existing value.

## Control flow
The compatibility flow always moves from newer API shape to older override when a user operator has not supplied a newer implementation. V3 creates a V2 input/output pair, invokes `FullMergeV2`, propagates failure scope on failure, then maps either `new_value` or `existing_operand` back into the V3 output variant.

For wide columns, only the default column participates in legacy merge semantics. The fallback then emits a new default-column value plus all existing non-default columns. If no default column existed, it adds one before copying existing columns.

Partial merge multi starts from operand zero, merges it with each subsequent operand, swaps the temporary result into `new_value`, and updates the temporary slice to point at the accumulated result. Associative full merge is similar but starts from the optional existing base value and invokes the user's associative `Merge` for each operand.

## State and persistence behavior
This file has no persistent state. It defines semantic defaults that directly affect read and compaction results, which later become persisted values when compaction writes merged output. The wide-column fallback preserves non-default columns by copying names and values into the V3 output.

## Dependencies and integration points
The implementation depends on the public `rocksdb/merge_operator.h`, wide column helper utilities, and a variant `overload` helper. It is used by `MergeHelper::TimedFullMerge`, memtable point lookups, DB reads, and compaction whenever a merge operator does not override the latest API.

## Risks and edge cases
The compatibility path copies operands into strings for legacy `FullMerge`, which can be expensive. Wide-column fallback only gives legacy operators the default column; operators unaware of wide columns cannot inspect or modify non-default columns except through preservation. `PartialMergeMulti` assumes at least two operands and returns false on the first pairwise failure. Returned `existing_operand` slices must point to still-valid operand storage.

## Test signals
`merge_test.cc` directly tests V3 fallback for string new values, returned operand slices, wide-column bases with and without default columns, and failure-scope propagation. DB-level merge tests exercise associative full and partial merge fallbacks through `CountMergeOperator`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_operator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_test.cc -->
# sources/storage-engines/rocksdb/db/merge_test.cc

## Purpose
`merge_test.cc` is the DB-level integration suite for RocksDB merge behavior. It validates merge-based counters through puts, deletes, merges, flushes, compactions, TTL DBs, successive-merge thresholds, partial merge thresholds, manifest concurrency around flush/compaction, `FullMergeV3` compatibility fallback, and oversized merge result rejection.

## Important APIs, types, and functions
`CountMergeOperator` wraps the built-in UInt64Add operator while counting full and partial merge invocations. `EnvMergeTest` wraps the default environment and counts `NowNanos` calls to guard against unnecessary timing overhead. `OpenDb` creates a temporary DB with `CountMergeOperator`, optional TTL, optional `max_successive_merges`, and the counting environment.

`Counters` implements set/remove/get/add using Put/Delete/Get. `MergeBasedCounters` overrides `add` to use DB `Merge`. Helper functions `testCounters`, `testCountersWithFlushAndCompaction`, `testSuccessiveMerge`, `testPartialMerge`, `testSingleBatchSuccessiveMerge`, and `runTest` orchestrate scenarios.

Test cases are `MergeDbTest`, `MergeDbTtlTest`, `MergeWithCompactionAndFlush`, `FullMergeV3FallbackNewValue`, `FullMergeV3FallbackExistingOperand`, `FullMergeV3FallbackFailure`, and `LargeMergeResultRejected`.

## Control flow
Counter tests compare ordinary read-modify-write counters with merge-based counters. They set values, delete missing keys, merge many increments, flush, compact, reopen without merge operator for a negative read check, and verify decoded sums. TTL mode runs the same merge semantics through `DBWithTTL`.

Successive merge tests configure `max_successive_merges` and assert that writes trigger full merge only when the threshold is exceeded, while reads merge the remaining operands. Single-batch tests ensure many merge records in one write batch trigger expected in-mem merge calls and still read back the correct sum.

Partial merge tests flush and compact different operand counts to verify `PartialMergeMulti` is invoked only when operand count reaches the hard-coded minimum and remains below the full-merge threshold. They also confirm no partial merge occurs when a put base exists and that `MergeHelper::FilterMerge` does not call `NowNanos` when detailed timing is disabled.

The flush/compaction concurrency test uses `SyncPoint` callbacks around `VersionSet::LogAndApply` to interleave SetOptions, compaction, background flush, a merge write, and a read. This reproduces a manifest ordering/race scenario and verifies the merged value remains visible.

V3 fallback tests construct merge inputs directly for append, put, and failing operators. They validate no-base, plain-base, wide-column-with-default, and wide-column-without-default cases. The large-result test invokes `MergeHelper::TimedFullMerge` with lazy-zeroed mappings around the 4GB boundary.

## State and persistence behavior
The suite persists data through real DB writes, WAL/memtable state, flushes to SST, compactions, TTL wrappers, MANIFEST updates, and reopen. It observes merge operator call counters and environment timing counters as process-local state. It also validates that an unmerged DB reopened without a merge operator cannot read merge operands as normal values.

## Dependencies and integration points
The test integrates DBImpl, internal formats, merge helper, write batch internals, cache/comparator/env/db/TTL APIs, wide columns, test harness, coding utilities, cast utilities, built-in merge operators, sync points, flush, compaction, SetOptions, and direct `TimedFullMerge`.

## Risks and edge cases
Merge behavior spans memtable reads, compaction, operator compatibility, and recovery. Reopen without merge operator is expected to fail reads where unresolved operands remain. SyncPoint tests depend on internal callback names and old SetOptions manifest behavior restored by a callback. Big-memory tests are skipped when the host lacks enough memory.

## Test signals
Passing this file gives high-level confidence that merge operators work across normal DB writes, TTL DBs, flush/compaction, threshold-triggered full and partial merges, write batches, manifest concurrency, V3 fallback compatibility, wide-column preservation, failure-scope propagation, and 4GB result limits.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/merge_test.cc -->
