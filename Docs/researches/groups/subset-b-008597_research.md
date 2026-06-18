# subset-b-008597 Research

Grouped research report for the RocksDB files assigned to `subset-b-008597`. Each section is source-tree-aligned and wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.cc -->
## sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.cc

### Purpose

`db_impl_secondary.cc` implements RocksDB secondary-mode database behavior and the remote-compaction worker path built on top of it. A secondary DB shares the primary DB's storage, opens with a private `secondary_path_`, replays MANIFEST state through `ReactiveVersionSet`, optionally tails WALs into local memtables, exposes read APIs over the reconstructed state, and rejects normal mutation APIs at the header level. The same implementation is also used by `DB::OpenAndCompact()` to open primary metadata as a secondary, run a compaction into an output directory, and serialize a `CompactionServiceResult` without installing generated files into the source DB.

### Important APIs, Types, And Functions

- `DBImplSecondary::DBImplSecondary()` delegates to `DBImpl` in secondary/read-only-oriented mode, stores `secondary_path_`, and logs the secondary open.
- `Recover()` replays MANIFEST only via `ReactiveVersionSet::Recover()`, initializes `max_total_in_memory_state_`, and creates the default column-family handle.
- `FindNewLogNumbers()`, `MaybeInitLogReader()`, and `RecoverLogFiles()` discover WALs, cache `log::FragmentBufferedReader`s in `log_readers_`, verify timestamp-size metadata, and insert replayed batches into `column_family_memtables_`.
- `GetImpl()`, `NewIterator()`, `NewIteratorImpl()`, and `NewIterators()` provide point and iterator reads against the secondary's current SuperVersions. They validate user-defined timestamp compatibility, disallow snapshots/tailing iterators in secondary mode, and use `versions_->LastSequence()` as the read snapshot.
- `TryCatchUpWithPrimary()` is the explicit refresh operation: apply more MANIFEST records, replay WALs, install new SuperVersions for changed column families, and purge obsolete local references.
- `DB::OpenAsSecondary()` overloads and `DBImplSecondary::OpenAsSecondaryImpl()` construct the secondary DB, create a logger under the secondary path if needed, recover MANIFEST/WAL state, build requested column-family handles, and publish SuperVersions.
- Remote compaction helpers include `OpenAndCompact()`, `CompactWithoutInstallation()`, `InitializeCompactionWorkspace()`, `PrepareCompactionProgressState()`, `ParseCompactionProgressFile()`, `FinalizeCompactionProgressWriter()`, and cleanup helpers for progress and SST output files.

### Control Flow

Open-as-secondary first adapts options, warns when `max_open_files != -1` because the primary can delete files while the secondary still needs them, creates `DBImplSecondary`, replaces the version set with `ReactiveVersionSet`, initializes column-family memtable access, and locks the DB mutex for recovery. `Recover()` reads only MANIFEST state. `OpenAsSecondaryImpl()` then optionally calls `FindAndRecoverLogFiles()` when `recover_wal` is true; this is used for normal secondaries but skipped by `OpenAndCompact()` because remote compaction only needs installed LSM state, not unflushed WAL data.

Catch-up follows the same ordering. `TryCatchUpWithPrimary()` holds the mutex while `ReactiveVersionSet::ReadAndApply()` consumes new MANIFEST edits, logs updated level summaries, discovers WAL files, and replays any useful records. It then removes old immutable memtables for changed column families, installs fresh SuperVersions, drops the mutex, cleans job state, and separately runs obsolete-file discovery/purge for secondary-owned references.

WAL replay is careful about ordering and partial primary activity. `FindNewLogNumbers()` uses `versions_->min_log_number_to_keep()` and the lowest cached log reader to avoid assuming a newer WAL means older current WALs are closed. `RecoverLogFiles()` initializes readers for all candidate logs, marks WAL file numbers as used, decodes each record as a `WriteBatch`, verifies timestamp-size consistency against running column-family metadata, skips records whose sequence is already covered by L0 files, switches a column family's active memtable when replay moves to a new WAL, and updates `LastAllocatedSequence`, `LastPublishedSequence`, and `LastSequence` after successful inserts.

Reads are DBImpl-like but secondary-specific. Point lookups build a timestamp-aware `LookupKey` at `versions_->LastSequence()`, check mutable and immutable memtables first, optionally resolve blob-backed memtable values through `BlobFetcher`, then consult current SST versions. Iterators reject tailing and explicit snapshots, acquire referenced SuperVersions, check timestamp history collapse, and call `NewArenaWrappedDbIterator()` with `allow_mark_memtable_for_flush=false`.

`OpenAndCompact()` deserializes `CompactionServiceInput`, loads the primary options file, applies `CompactionServiceOptionsOverride`, opens only default plus target column family as a secondary with WAL recovery disabled, locates the target handle, runs `CompactWithoutInstallation()`, writes the result, and closes handles/DB. The compaction path builds a compaction from input file numbers, prepares an output directory in `secondary_path_`, optionally loads persisted progress for resumption, constructs `CompactionServiceCompactionJob`, runs it outside the mutex, cleans up metadata, records resumed bytes, and returns the compaction status in the result.

### State And Persistence Behavior

The secondary's durable input state is owned by the primary: MANIFEST, SSTs, WALs, OPTIONS, and blob files. The secondary maintains local in-memory state in `ReactiveVersionSet`, SuperVersions, `log_readers_`, `cfd_to_current_log_`, memtables rebuilt from WALs, and `compaction_progress_`. It does not own normal DB tables/logs (`OwnTablesAndLogs()` returns false), and `FlushForGetLiveFiles()` is a no-op.

The `secondary_path_` is persistent workspace for secondary logs and remote-compaction output. Remote compaction can create table files, compaction-progress log files, temporary progress files, and a local info log there. Resumable compaction persists `VersionEdit` records containing `SubcompactionProgress` to a log-style progress file, syncs the initial progress, renames from temp to final progress filename, then reopens a writer on the finalized file. Startup scans the workspace once, keeps only the newest progress file when resuming, deletes old/temp progress files, preserves output files referenced by parsed progress, and removes extra SSTs.

### Dependencies And Integration Points

This file is tightly coupled to `DBImpl`, `ReactiveVersionSet`, `ColumnFamilyData`, `SuperVersion`, `WriteBatchInternal`, WAL `log::Reader`/`FragmentBufferedReader`, `WritableFileWriter`, `VersionEdit`, `CompactionServiceInput/Result`, `CompactionServiceCompactionJob`, and RocksDB file naming helpers. Public integration surfaces are declared in `include/rocksdb/db.h` and exposed through the C API in `db/c.cc`. Tests and sync points are concentrated in `db_secondary_test.cc`, with named sync points around WAL catch-up and OpenAndCompact option loading/opening.

### Risks And Edge Cases

- Secondary reads can return `IOError` if the primary deletes SST/blob/WAL files before the secondary has opened or replayed them. The code logs a warning and suggests coordination, custom FS/Env retention, or `max_open_files=-1`, but this only helps table files already held open.
- `TryCatchUpWithPrimary()` treats `IsPathNotFound()` during WAL replay as OK because primary WALs may already be purged, which favors availability but can leave the secondary without unflushed primary writes until they appear in MANIFEST/SST form.
- Secondary iterators do not support explicit snapshots or tailing mode; reads always use latest sequence at call construction time.
- WAL replay ignores missing column families and skips batches covered by existing L0 sequence ranges. These behaviors are necessary for dropped CFs and MANIFEST/WAL overlap, but bugs here would cause duplicate or missing visible writes.
- User-defined timestamp consistency is verified during WAL replay and reads; comparator/CF timestamp-size drift is a high-risk compatibility surface.
- Remote-compaction resumption currently supports only a single subcompaction in progress parsing/persisting and is disabled when output hash verification is enabled. Multi-subcompaction or hash-state resumption would need additional persisted state.
- Progress cleanup can partially delete files before an error returns. The comments explicitly note a partially modified filesystem may require manual cleanup of `secondary_path_`.
- Progress-writer failure paths log that compaction will start without progress persistence, but the helper returns cleanup status to its caller. Tests should pin intended fallback-vs-fail behavior.

### Test Signals

Relevant existing signals include `db_secondary_test.cc` coverage for `OpenAsSecondary`, repeated `TryCatchUpWithPrimary()`, WAL tailing, dropped column families, remote compaction, cancellation, and compaction-progress/resumption behavior. Additional high-value tests should simulate primary file deletion, WAL purge races, timestamp-size changes, blob-backed memtable reads, multi-CF catch-up, invalid progress files with stray SSTs, progress-file rename/sync failures, and resumption disabled by output verification. Static research only; no build or test command was run for this report.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.h -->
## sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.h

### Purpose

`db_impl_secondary.h` declares the secondary-mode `DBImpl` subclass and a small WAL-reader owner used by the implementation. It defines the contract for a read-only secondary instance that can replay primary MANIFEST/WAL state without coordinating through the primary's process and rejects all user mutations. It also declares the private helpers used by remote compaction through `DB::OpenAndCompact()`.

### Important APIs, Types, And Functions

- `LogReaderContainer` owns a `log::FragmentBufferedReader`, its reporter, and a `Status` recording WAL corruption. Its nested reporter logs dropped bytes and stores the first corruption status.
- `DBImplSecondary` derives from `DBImpl` and overrides recovery, reads, iterators, write/mutation APIs, file deletion toggles, flush/options changes, WAL sync, external-file ingestion, and catch-up.
- `Recover()` is declared to replay MANIFEST only and initialize `manifest_reader_` for later catch-up.
- `GetImpl()`, `NewIterator()`, `NewIteratorImpl()`, and `NewIterators()` provide the read surface.
- Mutation APIs such as `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `Write`, `CompactRange`, `CompactFiles`, `Flush`, `SetDBOptions`, `SetOptions`, `SyncWAL`, and file ingestion APIs return `Status::NotSupported("Not supported operation in secondary mode.")`.
- `TryCatchUpWithPrimary()` is the public secondary refresh hook.
- `TEST_CompactWithoutInstallation()` exposes remote compaction internals in debug builds.
- `CompactionProgressFilesScan` captures one scan of the secondary workspace: latest progress file, old progress files, temp progress files, and table-file numbers.

### Control Flow

The header makes secondary behavior explicit before the implementation starts. Normal `DBImpl` overloads are brought into scope with `using`, then write-like overloads are overridden inline to fail fast. This prevents accidental mutation through a secondary pointer even though `DBImplSecondary` still inherits the full `DBImpl` machinery. Reads and catch-up are declared for implementation in the `.cc` file, while `FlushForGetLiveFiles()` is overridden as a read-only no-op and `OwnTablesAndLogs()` is overridden to return false.

Remote compaction helpers are private and friend-only through `DB`, so the public API remains `DB::OpenAndCompact()` rather than direct `DBImplSecondary` construction. `OpenAsSecondaryImpl()` accepts `recover_wal` so one implementation can serve both normal secondaries and remote compaction.

### State And Persistence Behavior

`manifest_reader_`, `manifest_reporter_`, and `manifest_reader_status_` keep MANIFEST tailing state between catch-up attempts. `log_readers_` caches WAL readers by log number so repeated catch-up can continue reading existing WALs instead of reopening from the beginning. `cfd_to_current_log_` tracks which WAL populated each column family's active memtable. `secondary_path_` is the persistent workspace path for secondary metadata/logs and remote compaction outputs. `compaction_progress_` is in-memory progress loaded from or persisted to compaction-progress files.

`LogReaderContainer` deliberately enables WAL checksumming even when paranoid checks would otherwise be false, because replaying corrupt sequence metadata into a secondary could make future reads unsafe. The reporter stores errors in its owned `Status` until the implementation consumes or permits them.

### Dependencies And Integration Points

The header depends on `db/db_impl/db_impl.h`, RocksDB logging, log reader types, `Status`, `ColumnFamilyData`, `CompactionServiceInput/Result`, and option/read/write API types inherited from `DBImpl` and `DB`. Its public behavior matches comments in `include/rocksdb/db.h` for `OpenAsSecondary()` and `TryCatchUpWithPrimary()`.

### Risks And Edge Cases

- Because `DBImplSecondary` inherits a large mutable base class, missing an override for a newly added mutation API could accidentally expose writes in secondary mode. Future DB API additions should be audited against this class.
- `OwnTablesAndLogs() == false` is a core safety assumption: cleanup must not delete primary-owned files. Any future secondary-owned linking/copying feature must revisit this.
- `LogReaderContainer` uses raw pointers internally and deletes them in its destructor. Ownership is simple but non-RAII within the class body, so constructor changes must preserve exception/error safety assumptions used by C++ builds without exceptions.
- The comments mention a workaround through `max_open_files=-1`, but typo-level drift in comments ("talbe") signals this area is operationally subtle and should be kept clear in user-facing docs.
- Progress scanning stores filenames and file numbers from one directory snapshot. Callers must avoid assuming it remains current after concurrent filesystem changes.

### Test Signals

Compile coverage is important for this header because it overrides many virtual APIs. Behavioral tests should attempt every mutation class against an opened secondary and assert `NotSupported`, exercise `GetLiveFiles()` without flushing, verify `TryCatchUpWithPrimary()` remains exposed through `DB`/`StackableDB`/C API surfaces, and run remote-compaction debug tests that use `TEST_CompactWithoutInstallation()`. Static research only; no build or test command was run for this report.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_write.cc -->
## sources/storage-engines/rocksdb/db/db_impl/db_impl_write.cc

### Purpose

`db_impl_write.cc` is RocksDB's central DB write-path implementation. It turns public `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `DeleteRange`, `Write`, `WriteWithCallback`, and `IngestWriteBatchWithIndex` calls into ordered WAL records, sequence-number assignment, memtable inserts, optional blob direct writes, write throttling/stalling, WAL switching, flush scheduling, recoverable transaction-state publication, and convenience default `DB` method implementations.

### Important APIs, Types, And Functions

- Public and DBImpl convenience methods validate timestamp compatibility and construct `WriteBatch` wrappers for single-key operations.
- `BlobWriteRollbackGuard` rolls back blob direct-write garbage accounting unless the write completes successfully.
- `PutEntityFastPathWriteCallback` disables batching for deferred `PutEntity` materialization.
- `BlobDirectWriteContext` caches per-CF referenced SuperVersions, blob partition managers, direct-write settings, touched managers, and rollback metadata.
- `MaybeTransformBatchForBlobDirectWrite()`, `AppendPreprocessedPutEntityToBatch()`, `AppendSortedPutEntityToBatch()`, `PutEntityFastPath()`, `WritePreprocessedPutEntityBatch()`, and `SyncBlobDirectWriteManagers()` implement wide-column/blob direct-write preprocessing.
- `WriteImpl()` is the main write state machine and dispatches to unordered, pipelined, two-queue WAL-only, or normal group-write paths.
- `PipelinedWriteImpl()`, `UnorderedWriteMemtable()`, and `WriteImplWALOnly()` implement specialized write modes.
- `PreprocessWrite()` handles background-error checks, WAL pressure, write-buffer-manager flushes/stalls, flush scheduling, memtable-history trimming, and WAL sync preparation.
- `MergeBatch()`, `WriteToWAL()`, `WriteGroupToWAL()`, and `ConcurrentWriteGroupToWAL()` flatten write groups, verify checksums, append to WAL, sync WALs/dirs, update WAL sizes, and cache recoverable state.
- `WriteRecoverableState()`, `SelectColumnFamiliesForAtomicFlush()`, `AssignAtomicFlushSeq()`, `SwitchWAL()`, `HandleWriteBufferManagerFlush()`, `DelayWrite()`, `WriteBufferManagerStallWrites()`, `ScheduleFlushes()`, `SwitchMemtable()`, and `GetWalPreallocateBlockSize()` maintain write-side persistence and flow control.

### Control Flow

Single-operation public methods first validate timestamp expectations (`FailIfCfHasTs()` or `FailIfTsMismatchCf()`), then call default `DB` methods that build small `WriteBatch` objects and eventually call `Write()`. `Write()` and `WriteWithCallback()` add per-key protection metadata when requested and delegate to `WriteImpl()`.

`WriteImpl()` begins with guardrails: null batch, missing timestamps, rate-limiter constraints, sync-without-WAL, incompatible pipelined/two-queue/unordered modes, unsupported `DeleteRange` plus row cache, and `WriteBatchWithIndex` restrictions. It traces early when write order need not be preserved, throttles low-priority writes if compaction is behind, handles two-write-queue WAL-only prepares, then prepares blob direct-write state if any CF supports it.

The main mode split is:

- `unordered_write`: write WAL through `WriteImplWALOnly()` with order assignment and publish-last-sequence, then later insert into memtable through `UnorderedWriteMemtable()`.
- `enable_pipelined_write`: `PipelinedWriteImpl()` separates WAL group leadership from memtable writer leadership so WAL and memtable phases can overlap.
- normal path: join `write_thread_`, let followers perform parallel memtable writes when selected, or let the group leader run `PreprocessWrite()`, enter a write group, optionally materialize deferred `PutEntity` and blob-index transformations, assign sequences, write/sync WAL, run pre-release callbacks, insert into memtables serially or in parallel, ingest WBWI data when present, publish `versions_->SetLastSequence()`, and exit the write group.

`PreprocessWrite()` runs before group WAL/memtable application. It checks existing background error state, flushes CFs when WAL bytes exceed `GetMaxTotalWalSize()`, asks the write buffer manager to switch selected memtables when memory pressure is high, trims immutable memtable history, drains the flush scheduler, applies write-controller delay/stall policy, blocks on global write-buffer-manager stalls, and prepares the WAL writer/sync bookkeeping under `wal_write_mutex_`.

WAL writing goes through `MergeBatch()` when a group has multiple valid writers or needs WAL-only append semantics. `WriteToWAL()` verifies the merged batch checksum, emits timestamp-size records when needed, appends to the current log with the assigned sequence, updates `wals_total_size_` and `alive_wal_files_` size state, and records the WAL number. Synchronous writes then sync all relevant logs and optionally fsync the WAL directory before manifesting synced-WAL state.

Memtable switching starts with `WriteRecoverableState()` so transaction recoverable state is present in memtables before an old WAL can be released. `SwitchMemtable()` may wait for an async-precreated WAL or create/recycle one outside the DB mutex, constructs the new memtable, marks the old memtable immutable and fragments range tombstones outside the mutex, installs the new WAL and memtable under locks, updates empty-CF WAL metadata and manifest WAL-deletion records when tracking is enabled, rotates blob direct-write generations, adds old/current and optional WBWI memtables to the immutable list, installs a SuperVersion, schedules async WAL precreation, and notifies listeners.

### State And Persistence Behavior

Persistent state changes include WAL records, optional WAL sync and WAL-directory fsync, MANIFEST edits for synced WAL additions/deletions, memtable contents later flushed to SSTs, blob direct-write files and partition-manager accounting, and persistent stats CF writes. In-memory state includes write-thread queues, `versions_` sequence counters (`LastAllocatedSequence`, `LastPublishedSequence`, `LastSequence`), `logs_`, `alive_wal_files_`, `cur_wal_number_`, `wal_empty_`, `wal_dir_synced_`, `wals_total_size_`, `cached_recoverable_state_`, flush/trim schedulers, write-controller stalls, and SuperVersion/memtable references.

The code is designed so WAL durability precedes memtable publication for normal writes. It avoids publishing `LastSequence` on partial memtable insert failure and escalates WAL or memtable divergence through `error_handler_`. `disableWAL` writes set `has_unpersisted_data_`. Blob direct-write bytes are flushed or synced before the transformed blob indexes are committed; rollback metadata marks blob writes as garbage if later write phases fail.

### Dependencies And Integration Points

The file integrates with `WriteThread`, `WriteBatchInternal`, `ColumnFamilyMemTablesImpl`, `ColumnFamilyData`, `VersionSet`, WAL `log::Writer`, `WritableFileWriter`, `ErrorHandler`, `WriteController`, `WriteBufferManager`, `FlushScheduler`, `TrimHistoryScheduler`, blob direct-write managers/transformers, `WBWIMemTable`, transaction callbacks, tracing, event listeners, statistics/histograms, and sync-point testing. Public API declarations live in `include/rocksdb/db.h`; option constraints interact with `column_family.cc`, `advanced_options.h`, and timestamp comparator settings.

### Risks And Edge Cases

- This file is the correctness boundary between WAL durability, sequence assignment, and memtable visibility. Any mismatch between `seq_per_batch_`, batch counts, `InsertInto()` sequence advancement, and WAL recovery ordering can create lost or duplicated versions.
- `IngestWriteBatchWithIndex()` checks `if (!write_options.disableWAL)` but returns a message saying it does not support `disableWAL=true`; that diagnostic appears inverted relative to the condition and can mislead operators/tests.
- Blob direct-write transformation is intentionally delayed until after `PreprocessWrite()` in the normal path so blob generation matches the target memtable. Reordering this code can make blob indexes point into the wrong generation.
- The comments note `tracer_` bool checks may be thread-unsafe before taking `trace_mutex_`. Existing locking narrows the race for use, but the optimization remains a known concern.
- `WriteToWAL()` returns early on timestamp-size-record failure before releasing `wal_write_mutex_` when `manual_wal_flush_ && !two_write_queues_` if that failure happens after explicit lock acquisition. This path should be scrutinized in tests or refactoring because early returns in locked regions are high risk.
- `SwitchMemtable()` comments flag unresolved earliest-sequence semantics for new memtables and sequence-consuming operations such as ingestion.
- Write stalls use prior batch size for delay decisions; comments acknowledge possible fairness issues where smaller writes expire while larger writes proceed.
- Failure after WAL write but before memtable insert intentionally sets background errors; recovery assumptions depend on callers closing/reopening rather than continuing with divergent in-memory state.
- `WriteStatusCheck()` and `WALIOStatusCheck()` treat some `Busy`/`Incomplete` statuses as non-fatal. Tests must distinguish transient throttling from corruption/IO-fenced failures.

### Test Signals

High-value existing tests are in `db_write_test.cc` for `IngestWriteBatchWithIndex`, write batching, callbacks, WAL behavior, low-priority/no-slowdown behavior, and transaction-related writes; `db_secondary_test.cc` covers WAL replay consumers; blob direct-write tests exercise transformation and garbage accounting; `db_inplace_update_test.cc` covers the concurrency restriction around in-place updates. Additional signals should include fault injection at WAL append/sync, timestamp-size record emission, manual WAL flush locking, blob direct-write post-transform failures, WBWI commit ingestion, atomic flush selection, WAL recycling, async WAL precreate cleanup, and memtable-switch listener callbacks. Static research only; no build or test command was run for this report.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_write.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_info_dumper.cc -->
## sources/storage-engines/rocksdb/db/db_info_dumper.cc

### Purpose

`db_info_dumper.cc` implements `DumpDBFileSummary()`, a startup/diagnostic logging helper that summarizes visible RocksDB files in the DB directory, configured DB paths, and WAL directory. It writes human-readable state to `ImmutableDBOptions::info_log` so an opened DB log captures host/session identity and the current file layout.

### Important APIs, Types, And Functions

- `DumpDBFileSummary(const ImmutableDBOptions& options, const std::string& dbname, const std::string& session_id)` is the only function in the file.
- It uses `Header()` and `Error()` logging helpers, `Env::GetHostNameString()`, `Env::GetChildren()`, `Env::GetFileSize()`, `ImmutableDBOptions::GetWalDir()`, `IsWalDirSameAsDBPath()`, and `ParseFileName()` from `file/filename.h`.
- File types handled explicitly are `kCurrentFile`, `kIdentityFile`, `kDescriptorFile`, `kWalFile`, and `kTableFile`.

### Control Flow

The function exits immediately if `options.info_log` is null. It logs a DB summary header, host name when available, and session ID. It lists `dbname`, sorts children for stable output, parses RocksDB file names, logs CURRENT and IDENTITY names, logs MANIFEST size, accumulates WAL filename/size strings, and records up to the first nine SST file names for the DB directory.

It then iterates `options.db_paths`. For each non-`dbname` path it lists and sorts children, gracefully logs missing directories, accumulates SST file names and a count, and emits a per-path SST summary. Finally it handles `wal_dir`: if WAL dir differs from DB path, it lists that directory and rebuilds `wal_info`; missing WAL dir is reported as a header instead of an error. If WAL info should be logged, it writes the final WAL summary.

### State And Persistence Behavior

The function is read-only with respect to the DB filesystem. It persists only log output in the info log. In-memory state is limited to reusable `files`, counters, and string accumulators. It does not acquire DB mutexes and therefore reports a best-effort snapshot that may race with concurrent file creation/deletion.

### Dependencies And Integration Points

This helper is part of DB open diagnostics and depends on `ImmutableDBOptions`, `Env`, file naming conventions, and logging. It is a low-level observer used to make support/debug logs more actionable, especially when multiple DB paths or a separate WAL directory are configured.

### Risks And Edge Cases

- File listings are non-transactional; counts and sample filenames can be stale by the time they are logged.
- Only the first nine SST filenames are included because the code increments before checking `< 10`; the total count is more useful than the sample list for large DBs.
- The `files` vector is reused. `Env::GetChildren()` implementations are expected to fill/replace it; if a custom Env appended instead of clearing, summaries could include stale names.
- WAL info is accumulated in a single string with no size cap. A DB with many WALs can produce a long log line.
- Missing DB path and WAL path are treated differently from other listing errors, which is appropriate for optional directories but can hide configuration mistakes if users do not inspect info logs.

### Test Signals

Tests should use a mock or temporary Env with CURRENT, IDENTITY, MANIFEST, WAL, SST, unknown files, multiple `db_paths`, missing paths, and separate WAL directory. Assertions should check stable sorted output, missing-directory messages, file-size error logging, info-log-null no-op behavior, and large-WAL log behavior. Static research only; no build or test command was run for this report.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_info_dumper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_info_dumper.h -->
## sources/storage-engines/rocksdb/db/db_info_dumper.h

### Purpose

`db_info_dumper.h` declares the DB file summary logging helper used by RocksDB open/diagnostic paths. It keeps the logging API small: callers provide immutable DB options, the DB name/path, and an optional session ID.

### Important APIs, Types, And Functions

- `void DumpDBFileSummary(const ImmutableDBOptions& options, const std::string& dbname, const std::string& session_id = "");`
- The header includes `<string>` and `options/db_options.h` for `ImmutableDBOptions`.

### Control Flow

There is no executable control flow in the header. The default empty `session_id` lets older or simpler callers log a summary without constructing session metadata, while newer DB-open paths can pass a real session identifier.

### State And Persistence Behavior

The declaration itself has no state. The implementation logs to `options.info_log` and reads filesystem state through `options.env`.

### Dependencies And Integration Points

This header is an internal DB component rather than a public RocksDB API. Its main dependency is the internal immutable options type, which gives the implementation access to `Env`, info log, DB paths, and WAL directory policy.

### Risks And Edge Cases

- Because `session_id` defaults to an empty string, call sites that forget to pass the generated DB session ID still compile and produce less useful diagnostics.
- The function takes `dbname` as a plain string; callers must pass the canonical DB path expected by `ImmutableDBOptions::GetWalDir()`/`IsWalDirSameAsDBPath()` to avoid misleading path summaries.

### Test Signals

Compile tests should include this header from DB implementation units. Runtime tests belong with `db_info_dumper.cc` and should validate default session ID logging as well as explicit session IDs. Static research only; no build or test command was run for this report.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_info_dumper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_inplace_update_test.cc -->
## sources/storage-engines/rocksdb/db/db_inplace_update_test.cc

### Purpose

`db_inplace_update_test.cc` is a GoogleTest suite for RocksDB memtable in-place update behavior. It verifies that enabling `Options::inplace_update_support` lets same-key updates overwrite existing memtable entries when the new encoded value fits, falls back to additional entries when it does not, applies configured `inplace_callback` decisions, handles wide-column `PutEntity`, and reflects the feature's incompatibility with snapshots.

### Important APIs, Types, And Functions

- `DBTestInPlaceUpdate` derives from `DBTestBase` with test name `db_inplace_update_test` and fsync-enabled environment.
- Tests use `CurrentOptions()`, `Reopen()`, `CreateAndReopenWithCF()`, `Put()`, `Get()`, `db_->PutEntity()`, `DummyString()`, `validateNumberOfEntries()`, and `ChangeCompactOptions()`.
- Callback tests use `DBTestBase` helper callbacks: `updateInPlaceSmallerSize`, `updateInPlaceSmallerVarintSize`, `updateInPlaceLargerSize`, and `updateInPlaceNoAction`.
- `main()` installs RocksDB's stack trace handler and runs GoogleTest.

### Control Flow

Each test runs inside a `do { ... } while (ChangeCompactOptions())` loop to repeat under different compaction-option configurations. The setup enables `create_if_missing`, `inplace_update_support`, the test env, and `allow_concurrent_memtable_write=false`, then opens the DB and creates/reopens a non-default column family named `pikachu`.

`InPlaceUpdate` writes decreasing value sizes to the same key and expects reads to return the latest value while the internal-entry count remains one. `InPlaceUpdateLargeNewValue` writes increasing value sizes and expects all updates to remain as separate internal entries. The two `PutEntity` tests repeat that smaller/larger pattern for wide-column entities and validate internal-entry counts, with TODOs noting entity `Get` coverage is not yet available there.

The callback tests configure `options.inplace_callback`. Smaller-size and smaller-varint callbacks transform stored values and still keep one internal entry. Larger-size callback prevents in-place overwrite and leaves all updates as new puts. No-action callback causes a put to result in no visible value. The snapshot test confirms `GetSnapshot()` returns `nullptr` with in-place update support and that releasing the null snapshot is harmless.

### State And Persistence Behavior

The tests create real DB state under the fixture directory, write to a secondary column family, and inspect memtable/internal iterator state through `validateNumberOfEntries()`. They intentionally keep updates in memory with a large enough `write_buffer_size` in value tests and disable concurrent memtable writes because in-place update support is incompatible with concurrent memtable insertion. The test DB is reopened across option changes through the fixture utilities.

### Dependencies And Integration Points

The suite depends on `db/db_test_util.h`, `DBTestBase`, test callback helpers, GoogleTest macros, and `port/stack_trace.h`. It validates behavior implemented in memtable insertion/update code and guarded by write-path comments in `db_impl_write.cc` saying puts are not eligible for concurrent memtable writes when `inplace_update_support` is enabled. It also intersects with option parsing and snapshot support constraints documented in RocksDB options and DB APIs.

### Risks And Edge Cases

- Wide-column `PutEntity` tests only validate internal entry counts; they do not read back entity values because the TODO says entity `Get` support is missing in this test path.
- Tests force `allow_concurrent_memtable_write=false`; they do not prove the option validator rejects or adjusts unsafe concurrent settings.
- The snapshot test only checks `GetSnapshot()` returns null and release is harmless; it does not cover attempted snapshot reads because snapshots are unsupported with in-place update support.
- Value-size boundaries depend on encoded length and varint length. The smaller-varint callback test covers a 265-byte boundary, but additional exact boundary cases around varint transitions could catch regressions.
- Durability/recovery is not the focus: these are primarily memtable behavior tests, not WAL replay or flush-compaction validation.

### Test Signals

Useful signals are successful execution of `db_inplace_update_test`, preserved expected `validateNumberOfEntries()` counts, visible callback-transformed values for plain `Put`, no visible value for no-action callback, and null snapshots under in-place update support. Additional tests should add entity reads when supported, option incompatibility checks, flush/reopen behavior after in-place updates, merge/delete interactions, and boundary sizes around serialized entity/value length changes. Static research only; no build or test command was run for this report.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_inplace_update_test.cc -->
