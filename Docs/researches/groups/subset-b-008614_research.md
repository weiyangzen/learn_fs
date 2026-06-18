# subset-b-008614 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_job.cc -->
# sources/storage-engines/rocksdb/db/flush_job.cc

## Purpose
Implements RocksDB `FlushJob`, the background job that turns selected immutable memtables into a level-0 table file or, when the experimental mempurge path succeeds, into a smaller immutable memtable. It also builds the `VersionEdit` side effects needed for WAL recovery boundaries, SST metadata, blob metadata, flush statistics, event logging, UDT history cutoff advancement, and tiering metadata.

## Important APIs and functions
`GetFlushReasonString()` maps public/internal `FlushReason` values to event-log strings. The constructor captures DB/CF options, directories, job context, compression, thread priority, IO tracing, DB/session IDs, `SeqnoToTimeMapping`, optional full-history timestamp low watermark, optional blob callback, and fast-SST-open mode. `PickMemTable()` must run under `db_mutex_`; it picks immutable memtables up to `max_memtable_id_`, initializes `edit_`, assigns a new file number and epoch, refs the base `Version`, records input size, and precomputes UDT/tiering cutoffs. `Run()` is the top-level state machine. `WriteLevel0Table()` builds the actual SST through `BuildTable()`. `MemPurge()` and `MemPurgeDecider()` implement the overwrite-heavy in-memory purge alternative. `GetRateLimiterPriority()`, `GetFlushJobInfo()`, `GetEffectiveCutoffUDTForPickedMemTables()`, `GetPrecludeLastLevelMinSeqno()`, and `MaybeIncreaseFullHistoryTsLowToAboveCutoffUDT()` are supporting policy/metadata helpers.

## Control flow
The normal lifecycle is construct, `PickMemTable()`, then either `Run()` or `Cancel()`. `Run()` handles empty selections, optionally enables detailed perf counters, decides whether mempurge is eligible for write-buffer-full flushes, runs mempurge or writes L0, checks CF dropped/shutdown states, may raise full-history timestamp low, rolls back picked memtables on failure, and installs results through `TryInstallMemtableFlushResults()` when this job owns manifest writes. The L0 path releases the DB mutex while creating iterators, merging memtables, gathering range deletions, building table properties, writing SST/blob outputs, fsyncing the output directory, and then reacquires the mutex to update the edit and stats. The mempurge path also releases the mutex, compacts visible payload into a new memtable using `CompactionIterator`, handles range tombstones, aborts if the output exceeds one memtable, and readds a successful compacted memtable without scheduling another flush.

## State and persistence behavior
Persistent effects are concentrated in `VersionEdit`: WAL log number advancement, L0 file additions, blob-file additions/garbage, and full-history timestamp updates. `meta_` captures file number, epoch, bounds, sequence range, file size, temperature, creation time, oldest ancestor time, and blob references. Empty SSTs are not added to the manifest, but blob metadata may still be committed. Directory fsync is conditional for atomic flush coordination. On failed install after table creation, the table cache entry is evicted as an obsolete uninstalled file. External write-path blob metadata is stashed before flush and either moved into the edit or returned by `TakeExternal...`.

## Dependencies and integration points
This file ties together `ColumnFamilyData`, `MemTableList`, `VersionSet`, `VersionEdit`, `TableCache`, `BuildTable`, `CompactionIterator`, range tombstone aggregation, blob callbacks, `ErrorHandler`, `LogsWithPrepTracker`, `InternalStats`, event logging, perf/IO stats, `ThreadStatusUtil`, and filesystem directory syncing. Atomic flush callers use `write_manifest_=false` and install combined results elsewhere. Flush info is piggybacked on the first flushed memtable for listener notification.

## Risks
The code relies on strict mutex handoff and `base_` ref ownership; missing `Run()`/`Cancel()` after `PickMemTable()` leaks or misorders state. Mempurge is explicitly experimental and has many unsupported or approximate paths: sampled garbage estimation, compaction-filter constraints, new memtable ID repair after mutex release, and fallback to normal flush on abort. UDT stripping can permanently advance `full_history_ts_low`; correctness depends on timestamp comparator semantics and cutoff encoding. Build/stat verification can become corruption only when `flush_verify_memtable_count` is enabled. Blob metadata paths must keep SST and blob edits atomic.

## Test signals
`flush_job_test.cc` directly validates empty and non-empty flushes, selected memtable subsets, multi-CF atomic installation, snapshot retention, rate limiter priority, preferred-seqno conversion using `SeqnoToTimeMapping`, and UDT stripping/full-history behavior. Sync points in this file also expose hooks for broader DB tests around flush start/end, mempurge success/failure, build-table status, output compression, and file creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_job.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_job.h -->
# sources/storage-engines/rocksdb/db/flush_job.h

## Purpose
Declares `FlushJob`, RocksDB's flush work object for a single column family. The class encapsulates picked immutable memtables, file metadata, manifest edit state, flush/mempurge execution, blob side effects, statistics, and listener information until the flush is installed, canceled, or atomically combined with other flush jobs.

## Important APIs and types
The public constructor takes DB name, `ColumnFamilyData`, immutable and mutable options, a maximum memtable ID, file options, `VersionSet`, DB mutex, shutdown flag, `JobContext`, `FlushReason`, logging/directories, output compression, stats/event logger flags, sync/manifest policy, thread priority, `IOTracer`, `SeqnoToTimeMapping`, DB/session identifiers, optional UDT history watermark, blob completion callback, and fast-SST-open flag. `PickMemTable()` selects the memtables under mutex. `Run()` executes and optionally returns `FileMetaData`, mempurge/skipped flags, and error-handler state. `Cancel()` releases picked state. `GetMemTables()`, `GetLogNumber()`, external blob addition/garbage transfer methods, and `GetCommittedFlushJobsInfo()` expose state to atomic flush and listener code.

## Control flow and invariants
The header documents the key invariant: after `PickMemTable()` the caller must call `Run()` or `Cancel()`. `mutable_cf_options_` must outlive the job. Most private helpers assume the DB mutex is held at entry, while table building and mempurge release it internally. `pick_memtable_called`, `edit_`, `base_`, `mems_`, and `meta_` represent the transition from unpicked to executable state.

## State and persistence behavior
Members record persistent metadata before it is committed: `VersionEdit* edit_`, `FileMetaData meta_`, selected memtables, `base_` version reference, external blob additions/garbage, `table_properties_`, cutoff UDT, preclude-last-level sequence, and shared `SeqnoToTimeMapping`. The `sync_output_directory_` and `write_manifest_` booleans encode whether this job commits independently or participates in atomic flush. `committed_flush_jobs_info_` stores listener payloads for this job and any concurrent flush result it commits.

## Dependencies and integration points
The declaration imports RocksDB DB internals: column-family metadata, flush scheduler, memtable list, version edits, job context, logs-with-prepared tracker, snapshots, write controller/thread, event logger, IO tracing, seqno-to-time mapping, blob callbacks, and filesystem directories. It is constructed by DB flush scheduling code and consumed by memtable installation and atomic flush paths.

## Risks
The constructor has many cross-subsystem parameters and lifetime assumptions, especially references to options, mutex, directories, and job context. `GetLogNumber()` assumes `PickMemTable()` initialized `edit_`. Blob addition/garbage vectors are move-only side channels that must be consumed or returned exactly once. Atomic flush safety depends on callers setting sync/manifest flags consistently.

## Test signals
`FlushJobTest_GetRateLimiterPriorityForWrite_Test` is a friend for private priority testing. The rest of the API is exercised through `flush_job_test.cc`, especially public lifecycle methods, atomic flush accessors, and returned file metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_job_test.cc -->
# sources/storage-engines/rocksdb/db/flush_job_test.cc

## Purpose
Unit and integration-style tests for `FlushJob`. The file constructs a lightweight RocksDB `VersionSet`, mock table factory, memtables, and job contexts to verify flush metadata, output contents, atomic flush behavior, timestamp handling, and rate-limiter priority without opening a full DB for every case.

## Important APIs and fixtures
`FlushJobTestBase` creates a test DB directory, writes an initial MANIFEST/CURRENT, configures column families, initializes `VersionSet`, and owns shared objects such as `TableCache`, `WriteBufferManager`, `WriteController`, mutex, shutdown flag, and `mock::MockTableFactory`. `ValueWithWriteTime()` and `ValueWithPreferredSeqno()` encode test values used by preferred-seqno rewriting. `FlushJobTest` uses bytewise comparison; `FlushJobTimestampTest` parameterizes paranoid file checks and user-defined timestamp persistence/stripping.

## Test control flow
Tests explicitly add constructed memtables into `cfd->imm()`, call `PickMemTable()` and `Run()` under the instrumented mutex, and then inspect output metadata or mock-table contents. `FlushMemtablesMultipleColumnFamilies` builds one flush job per CF with `write_manifest_=false`, gathers each job's memtables and file metadata, and installs all results through `InstallMemtableAtomicFlushResults()`. Timestamp tests use a comparator with U64 timestamps and verify both installed file key bounds and `full_history_ts_low`.

## State and persistence behavior covered
`Empty` verifies no-op flushes. `NonEmpty` verifies key ordering, range tombstone output, blob index oldest-file tracking, histograms, and file metadata. `FlushMemTablesSingleColumnFamily` checks `max_memtable_id_` selection. `Snapshots` confirms older versions protected by snapshots remain in flush output. `ReplaceTimedPutWriteTimeWithPreferredSeqno` verifies time-to-seqno mapping for `kTypeValuePreferredSeqno`. Timestamp cases distinguish persisted UDTs from stripped UDTs and validate history-low advancement only when needed.

## Dependencies and integration points
The tests depend on RocksDB internal manifest writing, `VersionSet::Recover`, memtable construction, mock table building, stats histograms, and the write controller. They are a bridge between pure unit tests and DB integration because flush installation touches version state and manifest behavior.

## Risks and gaps
Mempurge behavior is not directly covered in this file despite being a major branch in `FlushJob::Run()`. Error-handler skipping, directory fsync failures, table-cache eviction after failed manifest install, blob file completion callbacks, and fast-SST-open behavior are not targeted here. The mock table factory may hide table-format-specific properties except where explicit checks are made.

## Test signals
This file is the primary direct test signal for `flush_job.cc`/`.h`. It should fail on regressions in memtable selection, metadata bounds, snapshot visibility, atomic flush installation, write-controller priority mapping, preferred seqno encoding, and UDT strip/persist semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_job_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_scheduler.cc -->
# sources/storage-engines/rocksdb/db/flush_scheduler.cc

## Purpose
Implements `FlushScheduler`, a small lock-free stack of column families whose memtables may require flushing. It is used by DB flush scheduling to decouple producers that mark a column family as needing flush from consumers that pick the next column family to process.

## Important APIs and functions
`ScheduleWork(ColumnFamilyData*)` refs a column family and pushes a heap-allocated `Node` onto the atomic head with compare-exchange. `TakeNextColumnFamily()` pops the current head, deletes the node, filters dropped column families, and returns a still-Ref'ed live `ColumnFamilyData*` that the caller must `Unref()`. `Empty()` checks the atomic head. `Clear()` drains the scheduler and unrefs every returned CF.

## Control flow
Scheduling is LIFO. `ScheduleWork()` uses relaxed atomics because callers normally synchronize externally with the DB mutex, and the header allows concurrent calls only with restrictions. `TakeNextColumnFamily()` loops until it finds a live CF or the stack becomes empty; dropped CFs are unrefed and skipped. `Clear()` repeatedly calls the same pop path, so dropped filtering and ref release are centralized.

## State and persistence behavior
There is no persistent state. Runtime state is an atomic singly linked list. In debug builds, `checking_set_` and `checking_mutex_` assert that a CF is not scheduled twice and that the linked-list state agrees with the debug set, subject to the documented race in `Empty()`.

## Dependencies and integration points
The scheduler only depends on `ColumnFamilyData` ref counting and dropped-state checks. It integrates with the DB mutex discipline and with recovery/single-threaded contexts that need to schedule flush work without the usual background scheduling machinery.

## Risks
Memory ownership is manual: every scheduled node must eventually be popped or cleared, and every successful schedule increments a CF ref. Duplicate scheduling is only asserted in debug builds. The relaxed atomic operations assume external synchronization for visibility outside the specifically allowed concurrent `ScheduleWork()`/`Empty()` pattern. The implementation uses a stack, so fairness is LIFO rather than FIFO.

## Test signals
No dedicated test file is in this work item. Behavior is indirectly exercised by DB flush scheduling tests elsewhere that rely on pending flush CFs being delivered once, skipped after drop, and unrefed during cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_scheduler.h -->
# sources/storage-engines/rocksdb/db/flush_scheduler.h

## Purpose
Declares `FlushScheduler`, the pending-flush column-family queue. The comments define its concurrency contract: most methods require the DB mutex or single-threaded recovery context, while `ScheduleWork()` may be called concurrently with itself and `Empty()` may race with scheduling with reduced precision.

## Important APIs and types
The public methods are `ScheduleWork()`, `TakeNextColumnFamily()`, `Empty()`, and `Clear()`. `TakeNextColumnFamily()` returns a Ref'ed `ColumnFamilyData*` and transfers the unref obligation to the caller. The private `Node` stores one column-family pointer and the next node. `head_` is an `std::atomic<Node*>`. Debug-only `checking_set_` tracks duplicate schedules.

## Control flow and state
The header presents a minimal stack-based scheduler. A scheduled CF enters the atomic linked list with an added reference. Consumers pop nodes until a live, non-dropped CF is found. `Clear()` is the cleanup path when scheduler state is abandoned or DB shutdown/recovery clears pending work.

## Dependencies and integration points
The declaration depends on `ColumnFamilyData` only by forward declaration, plus standard atomics/mutex/set and RocksDB `autovector` include. It is included by flush job and DB scheduling code that need to track CFs with full memtables.

## Risks
The API does not encode ownership in a smart pointer, so caller discipline is critical. The concurrency contract is intentionally narrow; using `TakeNextColumnFamily()` concurrently with scheduling outside the documented synchronization would risk dropped work, leaks, or stale pointers. Debug duplicate detection is absent in release builds.

## Test signals
The header itself has no direct tests in this subset. Correctness signals come from callers that expect scheduled CFs to be ref-stable until taken and unrefed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/flush_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/forward_iterator.cc -->
# sources/storage-engines/rocksdb/db/forward_iterator.cc

## Purpose
Implements `ForwardIterator`, an internal forward-only/tailing iterator optimized for `Seek()` and `Next()` over the mutable memtable, immutable memtables, L0 files, and sorted higher-level files. It avoids repeatedly reseeking immutable sources while moving forward, refreshes on SuperVersion changes, handles upper-bound trimming, async IO retry seeks, pinning, and cleanup of referenced SuperVersions.

## Important APIs and types
The file defines private `ForwardLevelIterator`, an `InternalIterator` over non-overlapping files in one level. `ForwardIterator` implements `SeekToFirst()`, `Seek()`, `Next()`, `Valid()`, `key()`, `value()`, `write_unix_time()`, `status()`, `PrepareValue()`, pinning APIs, property lookup for `rocksdb.iterator.super-version-number`, and `TEST_CheckDeletedIters()`. Internal helpers include `RebuildIterators()`, `RenewIterators()`, `ResetIncompleteIterators()`, `SeekInternal()`, `UpdateCurrent()`, `NeedToSeekImmutable()`, `DeleteCurrentIter()`, `FindFileInRange()`, and SuperVersion cleanup callbacks.

## Control flow
Construction optionally receives a current `SuperVersion` and builds child iterators. `Seek()`/`SeekToFirst()` refresh or renew iterators when needed, reset incomplete iterators, then call `SeekInternal()`. `SeekInternal()` seeks mutable state, decides whether immutable iterators need seeking, rebuilds the min-heap, trims iterators that cannot contribute under `iterate_upper_bound`, and runs a second pass for async IO `TryAgain`. `Next()` advances the current child, updates the cached previous-key interval when traversing immutable data, reseeks the mutable iterator as needed, pushes still-valid immutable children back into the heap, and chooses the next smallest internal key through `UpdateCurrent()`.

## State and persistence behavior
There is no persisted state. Runtime state includes a referenced `SuperVersion`, arena-owned memtable iterators, heap-managed immutable iterators, table-cache iterators for L0, `ForwardLevelIterator`s for L1+, current iterator pointer, cached previous internal key interval, aggregate immutable status, upper-bound trim flags, pinning manager, and arena storage. SuperVersion release can be deferred via `PinnedIteratorsManager` so pinned key/value slices remain valid.

## Dependencies and integration points
The iterator integrates with `DBImpl`, `ColumnFamilyData`, SuperVersion lifecycle, memtable iterators, immutable memtable list, `VersionStorageInfo`, table cache, range tombstone aggregation, prefix extractors, async IO feature checks, and pinned iterator cleanup. It explicitly rejects range tombstones unless ignored because forward iterator does not support them.

## Risks
Correctness depends on internal-key ordering and on maintaining `prev_key_` interval invariants; a bad interval could skip immutable data or reseek too often. Range tombstone presence converts the iterator to `NotSupported`, which callers must surface. Upper-bound trimming deletes child iterators and later rebuilds them only when seeking backward relative to the cached range. SuperVersion renewal reuses L0 iterators by file metadata pointer identity; stale pinning/cleanup mistakes can cause lifetime bugs. Async IO requires a two-pass seek and correct propagation of `TryAgain`/`Incomplete`.

## Test signals
No direct test file is included here, but the implementation contains sync points and `TEST_CheckDeletedIters()` for iterator tests elsewhere. `forward_iterator_bench.cc` provides workload pressure for tailing scans, cache-only reads, upper bounds, concurrent writes, and incomplete cache-tier reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/forward_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/forward_iterator.h -->
# sources/storage-engines/rocksdb/db/forward_iterator.h

## Purpose
Declares `ForwardIterator`, a forward-only `InternalIterator` intended as a faster tailing-style iterator by keeping direct access to DB, SuperVersion, memtable, and file iterators. It supports `Seek()`, `SeekToFirst()`, and `Next()`, while `Prev()`, `SeekForPrev()`, and `SeekToLast()` are explicitly unsupported.

## Important APIs and types
`MinIterComparator` and `MinIterHeap` define the heap used to merge immutable sources by smallest internal key. The `ForwardIterator` constructor takes `DBImpl`, `ReadOptions`, `ColumnFamilyData`, optional current `SuperVersion`, and an `allow_unprepared_value` flag. Public overrides expose validity, key/value, write time, status, `PrepareValue()`, iterator property retrieval, pinning, and test-only deleted-iterator accounting.

## Control flow and state
Private helpers divide responsibilities: cleanup and SuperVersion release, iterator rebuild/renewal, level iterator construction, incomplete iterator reset, seeking, current-source selection, immutable seek avoidance, file-range binary search, upper-bound checks, and deletion through pinning-aware paths. Members hold DB/CF pointers, read options, comparator/prefix extractor pointers, current SuperVersion, mutable/immutable/L0/level child iterators, min heap, current pointer, validity/status flags, cached previous key, pinning manager, and arena.

## Dependencies and integration points
The header depends on RocksDB iterator and table internals, `Arena`, comparators, DB read options, and version storage declarations. `DBImpl::NewIterator`-style paths can use it when `ReadOptions::tailing` or internal forward iteration is selected.

## Risks
The class exposes only a subset of `InternalIterator`; callers expecting reverse iteration will receive `NotSupported` and invalidation. It stores raw pointers to many DB-owned structures and relies on SuperVersion ref counting plus explicit cleanup. Prefix extractor use is part of the seek-avoidance invariant and must match the SuperVersion's mutable options.

## Test signals
The header's test hook `TEST_CheckDeletedIters()` supports validation of upper-bound trimming. Benchmarks and broader iterator tests exercise the declared behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/forward_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/forward_iterator_bench.cc -->
# sources/storage-engines/rocksdb/db/forward_iterator_bench.cc

## Purpose
Standalone benchmark for tailing/forward iterator behavior under concurrent writers and readers. It is compiled only when gflags is available and not on macOS/Windows; otherwise it emits a small placeholder `main`.

## Important APIs and types
Gflags configure writer/reader counts, write rate, value size, shard count, memtable size, block cache size, block size, runtime, cache-only-first behavior, and iterate upper-bound usage. `Stats` holds padded atomics for writes, reads, and cache misses. `Key` encodes shard and sequence number in big-endian order. `ShardState` stores per-shard last-written/read counters, iterators, and optional upper-bound slice. `Reader`, `Writer`, and `StatsThread` model workload actors.

## Control flow
`main()` opens a DB with no compression, no compaction style, high L0 triggers, direct IO for flush/compaction, configured memtable/block cache sizes, then creates readers and writers. Writers rate-limit themselves by filling a time queue, choose assigned shards randomly, write monotonic `(shard, seqno)` keys, and notify the shard's reader. Readers keep per-shard tailing iterators, optionally try a block-cache-tier iterator first, seek to the next unread key, then use `Next()` until caught up or an incomplete cache miss occurs. `StatsThread` prints one-second throughput counters.

## State and persistence behavior
The benchmark destroys and recreates a per-thread DB path. Persistent DB state is just generated key/value data; benchmark state lives in atomics, iterators, queues, semaphores, and threads. `iterate_upper_bound` constrains each shard iterator to its key range.

## Dependencies and integration points
It depends on RocksDB public DB APIs, block-based table options, cache creation, test path helpers, gflags compatibility, POSIX semaphores, and RocksDB `port::Thread`. It indirectly exercises `ForwardIterator` when RocksDB chooses tailing iterator internals.

## Risks
This is a benchmark, not a deterministic test: assertions validate monotonic reads but coverage depends on runtime flags and platform. It uses packed binary keys and direct memory casts, so portability is intentionally limited by compile guards. Infinite runtime is possible with negative `runtime`. Cache-tier misses are counted but not failures.

## Test signals
Useful signals are throughput, cache misses, and assertion failures under concurrent write/read pressure. It is especially relevant for forward iterator upper-bound trimming, SuperVersion renewal during writes/flushes, and cache-only `Incomplete` handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/forward_iterator_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/history_trimming_iterator.h -->
# sources/storage-engines/rocksdb/db/history_trimming_iterator.h

## Purpose
Defines `HistoryTrimmingIterator`, a thin `InternalIterator` wrapper that skips records whose user-defined timestamp is newer than a configured cutoff. It is used where RocksDB needs to trim historical versions according to timestamp history retention.

## Important APIs and types
The constructor takes an input `InternalIterator*`, a timestamp-aware `Comparator*`, and a non-empty cutoff timestamp string. `filter()` reads the current key timestamp with `ExtractTimestampFromKey()` and keeps entries whose timestamp compares less than or equal to `filter_ts_`. The class forwards validity, key/value, status, pinning checks, delete-range sentinel checks, and all movement methods to the input while looping past filtered-out entries.

## Control flow
Each seek method positions the input iterator, then advances in the same direction until `filter()` returns true. `Next()` and `Prev()` always move at least once, then continue while the current key is newer than the cutoff. If the input becomes invalid, `filter()` returns true so the loops stop.

## State and persistence behavior
The wrapper owns no persisted state and does not own the input pointer. Runtime state is only the input iterator pointer, copied cutoff timestamp, and comparator pointer. It does not modify keys or values; it only hides entries from iteration.

## Dependencies and integration points
It depends on timestamp extraction from `dbformat.h`, RocksDB comparator timestamp support, and `InternalIterator`. It can wrap table/memtable/internal iterators in history-trimming flows where timestamp retention is enforced above the child iterator.

## Risks
The constructor asserts timestamp support and non-empty cutoff but does not enforce ownership of `input_`. Movement loops assume the child iterator's `Next()`/`Prev()` eventually invalidates or reaches an allowed key; a buggy child could loop indefinitely. The wrapper does not override `PrepareValue()`, `write_unix_time()`, or property APIs, so callers needing those may lose child-specific behavior. Timestamp extraction assumes keys include timestamps of the comparator's configured size.

## Test signals
No direct tests are in this subset. Relevant coverage would be timestamp-history iterator tests that seek forward/backward across keys on both sides of the cutoff and verify status/pinning forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/history_trimming_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/import_column_family_job.cc -->
# sources/storage-engines/rocksdb/db/import_column_family_job.cc

## Purpose
Implements `ImportColumnFamilyJob`, which imports existing SST files into a newly created column family without rewriting table contents. It validates metadata, copies or hardlinks external files into the DB, builds a `VersionEdit` that adds them at their original levels, repairs epoch numbers for multi-CF imports, and cleans up on failure or move-file success.

## Important APIs and functions
`Prepare(next_file_number, sv)` reads all `LiveFileMetaData`, calls `GetIngestedFileInfo()` for each file, rejects empty/corrupt files, computes each imported CF's overall key range, rejects overlapping CF ranges, and copies/links files into DB table-file paths. `Run()` constructs dummy version builders/storage for each imported CF, adds files with metadata, recovers epoch numbers, populates this job's `edit_`, and advances the DB last sequence if imported files have larger sequence numbers. `Cleanup(status)` deletes copied DB files on failure or original links after successful move import. `GetIngestedFileInfo()` opens table readers and derives size, bounds, properties, unique ID, and range-tombstone-aware smallest/largest keys.

## Control flow
Preparation is outside the manifest edit: gather metadata, validate per-file entries and bounds, validate non-overlap across provided CF export sets, then materialize files inside the DB. Hardlinking is attempted when `move_files` is true and falls back to copy when unsupported. `Run()` must execute while the DB has exclusive writer/nonmem-writer ownership. It simulates version construction per imported CF so consistency checks and epoch recovery run before adding all files to the real edit.

## State and persistence behavior
`files_to_import_` stores `IngestedFileInfo` grouped per imported source CF. Persistent DB state changes are represented by `edit_` file additions and version sequence advancement. Files are physically linked/copied during prepare before manifest application; cleanup compensates if later steps fail. `oldest_ancester_time` and `file_creation_time` are set to import time. Imported file unique IDs are derived from table properties when available.

## Dependencies and integration points
The job depends on `VersionSet`, `ColumnFamilyData`, filesystem APIs, `CopyFile`, `TableReader`, table properties, range tombstone iterators, `VersionBuilder`, `VersionStorageInfo`, epoch-number recovery, and checkpoint/export metadata. It mirrors some external SST ingestion logic but targets creating a new CF from exported/imported file sets.

## Risks
Prepare performs file materialization before manifest success, so cleanup must be comprehensive. Multi-CF non-overlap uses overall user-key ranges, rejecting any overlapping imported CF ranges. Range tombstone bounds are subtle and must include serialized start/end keys, including tombstone-only files. UDT import is explicitly not fully supported by a TODO in table reader options. PlainTable lacks `SeekToLast()`, requiring a full scan for largest key. Epoch recovery is necessary to prevent later compaction corruption when files from different CFs have duplicate epochs.

## Test signals
`import_column_family_test.cc` covers imports from `SstFileWriter`, overlapping files, range tombstones, exports from another CF/DB, move vs copy behavior, negative cases, multi-CF imports, overlap rejection, endpoint overlaps within a level, and epoch reassignment under concurrent compaction pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/import_column_family_job.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/import_column_family_job.h -->
# sources/storage-engines/rocksdb/db/import_column_family_job.h

## Purpose
Declares `ImportColumnFamilyJob`, the job object used to import one or more exported SST file sets into a new column family. The class carries immutable DB/import options, source metadata, file-system access, generated ingested-file metadata, and the `VersionEdit` to apply after import preparation.

## Important APIs and types
`ColumnFamilyIngestFileInfo` records the smallest/largest internal keys for one imported CF group so cross-CF range overlap can be checked. The constructor stores `VersionSet`, target `ColumnFamilyData`, DB/env options, `ImportColumnFamilyOptions`, a vector of metadata groups, and `IOTracer`. `Prepare()` copies or links files into the DB and fills `files_to_import_`. `Run()` prepares `edit_`. `Cleanup()` compensates after success or failure. `edit()` and `files_to_import()` expose prepared results.

## Control flow and state
The lifecycle is `Prepare()` before manifest application, `Run()` under DB write exclusion, then `Cleanup()`. Members include `clock_`, `versions_`, `cfd_`, options references, `FileSystemPtr`, grouped `files_to_import_`, `VersionEdit edit_`, source `metadatas_`, and `io_tracer_`.

## Dependencies and integration points
The header depends on column-family internals, external SST ingestion types, snapshots, DB/import public options, metadata, SST file writer metadata conventions, `VersionEdit`, and filesystem env options. It is called from DB column-family creation with import metadata.

## Risks
The API separates physical file preparation from edit installation; callers must invoke cleanup with the final status. Option and metadata references must outlive the job. Exposed `VersionEdit*` is mutable and assumes a single caller controls application. Multi-CF input order and grouping must stay aligned with `metadatas_` and `files_to_import_`.

## Test signals
The corresponding test file exercises the lifecycle through public `DB::CreateColumnFamilyWithImport()` rather than directly instantiating the job.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/import_column_family_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/import_column_family_test.cc -->
# sources/storage-engines/rocksdb/db/import_column_family_test.cc

## Purpose
Integration tests for `CreateColumnFamilyWithImport()` and `ImportColumnFamilyJob`. The suite creates SSTs via `SstFileWriter` or exported checkpoints, imports them into new column families or new DBs, and verifies read semantics, metadata bounds, move/copy cleanup behavior, negative validation, multi-CF merging, and epoch-number repair.

## Important APIs and fixtures
`ImportColumnFamilyTest` extends `DBTestBase`, manages external SST/export directories, imported CF handles, and export metadata pointers. `LiveFileMetaDataInit()` creates minimal metadata entries for manually written SSTs. Tests use `SstFileWriter`, `Checkpoint::ExportColumnFamily()`, `DB::CreateColumnFamilyWithImport()` overloads, `Flush()`, `CompactRange()`, snapshots, metadata inspection, and sync points.

## Test control flow
The simple import test writes standalone SSTs and imports them with matching comparator metadata. Overlap tests import staged files across levels and verify latest values survive flush and compaction. Export tests checkpoint an existing CF, import into another CF or another DB, then compare reads with the source. Negative tests attempt existing CF names, empty file lists, same-level overlapping keys, comparator mismatch, missing files, and retry after failure. Multi-CF tests import two exported CF metadata sets into one new CF and reject overlapping source ranges. The epoch test forces files from two CFs with overlapping L0 epoch patterns, imports both, and waits for background compactions.

## State and persistence behavior covered
The tests validate imported files are visible immediately through normal reads, survive subsequent writes, flushes, compactions, snapshots, and DB reopen with unique-ID verification. Range tombstone tests confirm smallest/largest metadata includes tombstone endpoints and tombstone-only files preserve snapshot visibility. Move/copy variants ensure source file handling works for both hardlink/copy import modes. Epoch reassignment is tested by making compaction order expose duplicate-epoch corruption.

## Dependencies and integration points
These tests exercise the public DB API, checkpoint export format, table metadata, column-family metadata, filesystem directories, snapshots, compaction scheduler, and import job internals indirectly. They are the primary regression suite for import job behavior.

## Risks and gaps
Tests are broad but mostly end-to-end, so failures may require tracing through DB creation, manifest application, table reading, and compaction. UDT import is not covered, matching the TODO in the job implementation. File-link fallback behavior is not explicitly forced across filesystems. Corrupt table property and unique-ID warning paths are lightly covered at best.

## Test signals
Strong signals include value equality with source CF/DB after import, expected `InvalidArgument` or comparator/missing-file errors, metadata largest-key checks for range tombstones, reopen success with manifest unique-ID verification, and successful `WaitForCompact()` after epoch repair.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/import_column_family_test.cc -->
