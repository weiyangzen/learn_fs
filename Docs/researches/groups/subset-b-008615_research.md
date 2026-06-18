# subset-b-008615 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/internal_stats.cc -->
# sources/storage-engines/rocksdb/db/internal_stats.cc

## Purpose

`internal_stats.cc` implements RocksDB's internal property and statistics plumbing for column families and DB instances. It turns live `ColumnFamilyData`, `VersionStorageInfo`, `DBImpl`, cache, blob, memtable, write-stall, and compaction state into user-visible `DB::Properties` strings, integer values, and map properties. It also owns the formatter logic for compaction level tables, DB/CF cumulative and interval stats, file read latency histograms, block-cache entry role accounting, blob stats, and integer property aggregation across column families.

This file is not a persistence layer itself. Its state is in-memory telemetry attached to `InternalStats`; the persisted data it reports comes from `Version`, MANIFEST-derived `VersionStorageInfo`, table properties, WAL counters, and DB runtime controllers.

## Important APIs, types, and functions

- `InternalStats::compaction_level_stats` and `db_stats_type_to_info` define the property-name vocabulary for level compaction metrics and DB counters.
- `DB::Properties::k...` string constants are defined here from the `rocksdb.` prefix plus property suffixes. They are the public property keys consumed by `DB::GetProperty`, `GetIntProperty`, and `GetMapProperty`.
- `InternalStats::ppt_name_to_info` is the central dispatch table from property name to `DBPropertyInfo`, selecting one of string, integer, map, or `DBImpl` string handlers and marking whether the property must be collected outside the DB mutex.
- `GetPropertyInfo()` strips a trailing numeric suffix and resolves the property in the dispatch table.
- `InternalStats::GetStringProperty()`, `GetMapProperty()`, `GetIntProperty()`, and `GetIntPropertyOutOfMutex()` route property requests to the registered handler.
- Formatting helpers `PrepareLevelStats()`, `PrintLevelStatsHeader()`, and `PrintLevelStats()` compute and render level, priority, and summary compaction rows.
- `DumpCFMapStats()`, `DumpCFStatsNoFileHistogram()`, `DumpCFFileHistogram()`, `DumpDBMapStats()`, and `DumpDBStats()` are the core emission paths.
- `CacheEntryRoleStats::{BeginCollection,GetEntryCallback,EndCollection,SkippedCollection,ToString,ToMap}` provide block-cache entry role collection output for `CacheEntryStatsCollector`.
- Blob handlers expose blob-file counts, total/live/garbage size, blob stats text, and blob-cache capacity/usage/pinned usage.
- `CreateIntPropertyAggregator()` returns either a normal summing aggregator or a block-cache aggregator that de-duplicates shared cache instances across column families.

## Control flow

Property lookup starts with `GetPropertyInfo()`, which uses `GetPropertyNameAndArg()` to separate a trailing decimal argument from the property key. The caller then invokes the correct `InternalStats::Get*Property` method. String and map properties receive the suffix directly; integer properties either require `DBImpl::mutex_` or, for the small set marked `need_out_of_mutex`, receive a stable `Version*`.

For CF stats, handlers call `DumpCFMapStats()` or `DumpCFStats()`. The map path computes per-level metrics from current `VersionStorageInfo`, current compaction stats, L0/flush ingest counters, file sizes, compaction scores, files being compacted, and write-stall counters. The string path renders the same data, adds interval stats by subtracting `cf_stats_snapshot_`, emits priority-grouped compaction rows, blob summary, uptime, ingest and compaction bandwidth, pending compaction bytes, write-stall text, and the latest cached block-cache entry role stats when recent enough. File-read histograms are appended separately.

For DB stats, `DumpDBStats()` reads atomic DB counters, computes cumulative and interval write/WAL/stall rates, formats write-stall count breakdowns, and then updates `db_stats_snapshot_` so the next call reports a new interval. `DumpDBMapStats()` emits current raw counters plus uptime without updating interval snapshots.

The periodic CF handler uses `has_cf_change_since_dump_`, `last_histogram_num`, `no_cf_change_period_since_dump_`, and `kMaxNoChangePeriodSinceDump` to avoid emitting unchanged stats every period while still forcing an occasional dump.

## State and persistence behavior

Most counters are in-memory: `db_stats_` atomics, `cf_stats_value_`, `cf_stats_count_`, `comp_stats_`, `comp_stats_by_pri_`, `per_key_placement_comp_stats_`, read latency histograms, background error count, and running sorted-run count. `started_at_` anchors uptime. `db_stats_snapshot_` and `cf_stats_snapshot_` are mutable interval baselines; calls to `DumpDBStats()` and periodic CF dumps can change future output.

The file reads persisted metadata indirectly through `cfd_->current()`, `VersionStorageInfo`, table properties collection, blob file metadata, and `DBImpl` file-number/log state. It does not write on-disk state. The block-cache stats collector is held by `shared_ptr` and may be pinned in cache so subsequent stats calls can reuse previous scans.

## Dependencies and integration points

The implementation depends on `DBImpl`, `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `MemTableList`, compaction picker state, write controller state, `WriteStallStatsMapKeys`, table properties APIs, block-based table cache options, blob metadata, `CacheEntryStatsCollector`, `HistogramImpl`, and formatting helpers from `util/string_util.h`.

It integrates with the public RocksDB property APIs through `DB::Properties` constants and `DBPropertyInfo`; with write/flush/compaction code through `InternalStats::Add*` methods declared in the header; with cache code through `CacheEntryStatsCollector`; with multi-CF property aggregation through `IntPropertyAggregator`; and with DB mutex discipline through `need_out_of_mutex` and the assertion in `GetIntProperty()`.

## Risks and edge cases

- `GetPropertyNameAndArg()` treats any trailing digits as a suffix and assumes property base names do not end in digits. Adding a digit-ending property name would break lookup unless the convention is preserved.
- Some stats reads mutate interval snapshots. Repeated calls to textual DB stats or periodic CF stats are observably stateful.
- `AddDBStats(..., concurrent=false)` performs load-plus-store with relaxed atomics and is only safe where callers already serialize updates.
- Several handlers dereference `cfd_->current()` and related metadata under assumptions supplied by higher-level locking or version lifetime management.
- `HandleEstimateTableReadersMem()` returns `0` if no `Version*` is supplied, so using it through the wrong path would silently under-report.
- Cache entry stats can be stale by design. Fast/background paths intentionally stretch collection intervals to limit scan overhead.
- The map/string stats logic uses many manual divisions and counters; zero denominators are mostly guarded with `max()` or explicit checks, but changes to interval logic can reintroduce divide-by-zero or misleading rates.

## Test signals

The nearest direct coverage is usually in DB property, options/statistics, blob, write-stall, and cache tests rather than this file alone. Useful signals include tests that verify `DB::Properties` keys, map property names, block-cache capacity aggregation across column families, blob file stats, write-stall counters, compaction reason counts, table properties aggregation, and periodic stats output. `listener_test.cc` in this work item indirectly validates some data surfaced here, such as compaction job stats, blob file metadata, and table properties in event callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/internal_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/internal_stats.h -->
# sources/storage-engines/rocksdb/db/internal_stats.h

## Purpose

`internal_stats.h` declares the `InternalStats` class, related property dispatch metadata, compaction and cache statistics containers, and integer property aggregation interface used by RocksDB DB/column-family property reporting. It is the shared contract between code that records runtime counters and code that exposes those counters through `DB::Properties`.

The header centralizes in-memory DB/CF telemetry shape: write-stall counters, compaction byte and record counters, flush and external file ingestion counters, read latency histograms, blob read/write stats, cache entry role summaries, interval snapshots, and background error counts.

## Important APIs, types, and functions

- `DBPropertyInfo` stores the dispatch metadata for one property: mutex requirements and exactly one handler pointer for string, integer, map, or `DBImpl`-owned string properties.
- `GetPropertyInfo(const Slice&)` returns the dispatch metadata for a public property key.
- `LevelStatType`, `LevelStat`, and `DBStatInfo` define typed stat identifiers and public map/header names.
- `InternalStats::InternalCFStatsType` enumerates CF counters for write stalls, flush bytes, external file ingestion, file counts, and key counts.
- `InternalStats::InternalDBStatsType` enumerates DB counters for WAL bytes/syncs, write bytes/keys/groups, writes with WAL, write stall micros, and write-buffer-manager stops.
- `CompactionStats` stores per-output-level compaction counters and per-`CompactionReason` counts. It implements copy/assignment, `Clear()`, `Add()`, `Subtract()`, and `ResetCompactionReason()`.
- `CompactionStatsFull` wraps primary and optional proximal-level output stats for per-key-placement compaction and exposes `TotalBytesWritten()`, `DroppedRecords()`, `SetMicros()`, and `AddCpuMicros()`.
- `CacheEntryRoleStats` is the value type collected by `CacheEntryStatsCollector`; it can emit text and map forms.
- Public mutators such as `AddCompactionStats()`, `IncBytesMoved()`, `AddCFStats()`, `AddDBStats()`, and running sorted-run increment/decrement methods are the recording API.
- Property handlers are private methods named `Handle...` and are bound from the `.cc` property table.
- `IntPropertyAggregator` and `CreateIntPropertyAggregator()` define aggregation behavior across column families.

## Control flow

DB and compaction subsystems update `InternalStats` as work completes or runtime conditions change. Compactions add `CompactionStats` to a level and priority bucket. Flush and ingestion paths increment CF stat values and counts. DB writes increment atomic DB counters. Read paths update histograms through `GetFileReadHist()` and `GetBlobFileReadHist()`. Background errors are counted through `BumpAndGetBackgroundErrorCount()`.

Property reads enter through dispatch helpers declared here. String and map properties are served by private formatting handlers; integer properties may be served either while holding the DB mutex or outside the mutex with a supplied `Version*`, depending on `DBPropertyInfo::need_out_of_mutex`.

`Clear()` resets DB and CF counters, compaction stats, histograms, interval snapshots, background error count, uptime baseline, and periodic dump dirty state. It intentionally leaves the running compaction sorted-run atomic out of the generic reset path because that metric can both increment and decrement and should not be zeroed at periodic intervals.

## State and persistence behavior

`InternalStats` stores volatile telemetry only. Counters and snapshots live in memory and reset with `Clear()` or DB/CF object lifetime. Persistent file, table, blob, and version metadata are held elsewhere and only referenced through `ColumnFamilyData`, `Version`, and `VersionStorageInfo` in the implementation.

The class owns arrays of atomics for DB stats, raw arrays for CF counters, per-level and per-priority compaction vectors, read latency histograms, cache stats collector pointer, interval snapshots, and pointers to `SystemClock` and `ColumnFamilyData`. Because `cfd_` and `clock_` are raw pointers, lifetime is expected to be managed by the DB/column-family owner.

## Dependencies and integration points

The header depends on cache entry roles, `VersionSet`/`ColumnFamilyData`, `SystemClock`, RocksDB cache APIs, histograms, compaction reason enums, write-stall enums, table property types, and hash containers. It is included by DB implementation, compaction, flush, property, and test code that needs to update or inspect internal statistics.

The `TEST_` accessors expose CF stat arrays, compaction stats, per-key-placement compaction stats, and cache entry stats for unit tests. `IntPropertyAggregator` supports DBImpl-level aggregation of integer properties across all column families.

## Risks and edge cases

- Raw arrays are indexed by enum values; enum ordering and `*_ENUM_MAX` sentinels must remain consistent with array sizes.
- `CompactionStats::Subtract()` uses unsigned fields and assumes the subtracted snapshot is not newer/larger than the current stats. Incorrect ordering can underflow.
- `CompactionStatsFull::DroppedRecords()` only compares primary input records against combined outputs; users need to understand how proximal outputs affect drop accounting.
- `AddDBStats(concurrent=false)` is not an atomic read-modify-write despite using atomics. Callers must choose the concurrent mode correctly.
- `Clear()` resets interval baselines and most telemetry, making post-clear stats discontinuous.
- `CacheEntryRoleStats::ToMap()` computes used percent from cache capacity; callers should avoid zero-capacity cache configurations or be prepared for unusual floating output.

## Test signals

Relevant tests should exercise property lookup, counter increments, compaction stat accumulation/subtraction, reason counts, per-key-placement proximal stats, cache entry stats collection, write-stall stat mapping, and DB/CF stat clearing. Existing RocksDB DB property and listener tests provide indirect coverage by checking compaction payloads, table properties, blob stats, and write-stall pressure notifications.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/internal_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/job_context.h -->
# sources/storage-engines/rocksdb/db/job_context.h

## Purpose

`job_context.h` defines small containers used by RocksDB background and foreground DB jobs to move slow cleanup, deletion, snapshot release, SuperVersion destruction, WAL writer destruction, and listener notifications out from under the DB mutex. It is a lifetime-management and deferred-work contract, not a persistence format.

`SuperVersionContext` groups pending SuperVersion frees and write-stall notifications. `JobContext` groups obsolete file candidates, live-file snapshots, deletion queues, memtables/WAL writers to free, manifest/log number snapshots, direct-write blob-file protection state, and snapshot context used by flush/compaction jobs.

## Important APIs, types, and functions

- `SuperVersionContext::WriteStallNotification` stores `WriteStallInfo` plus the `ImmutableOptions` whose listeners should be notified.
- `SuperVersionContext::superversions_to_free`, `write_stall_notifications`, and `new_superversion` carry deferred SuperVersion work.
- `SuperVersionContext::NewSuperVersion()`, `HaveSomethingToDelete()`, `PushWriteStallNotification()`, and `Clean()` are the main operations.
- `JobContext::HaveSomethingToDelete()` checks file-deletion queues.
- `JobContext::HaveSomethingToClean()` checks memtables, WAL writers, job snapshot, and nested SuperVersion contexts.
- `GetJobSnapshotSequence()`, `GetLatestSnapshotSequence()`, and `GetEarliestSnapshotSequence()` expose the snapshot boundaries used by jobs.
- `InitSnapshotContext()` initializes snapshot checker, managed snapshot, earliest write-conflict snapshot, and ordered snapshot sequence list once.
- `CandidateFileInfo` represents a filesystem candidate discovered during a full obsolete-file scan.
- Deletion state includes `full_scan_candidate_files`, `sst_live`, `sst_delete_files`, `blob_live`, `blob_delete_files`, `log_delete_files`, `log_recycle_files`, `manifest_delete_files`, and `files_to_quarantine`.
- Direct-write blob protection state includes `active_blob_direct_write_files` and `min_blob_file_number_to_keep`.
- `JobContext::Clean()` performs deferred deletion of SuperVersions, memtables, WAL writers, and managed snapshot release.

## Control flow

DB code constructs a `JobContext` with a job id and optional preallocated SuperVersion. While the DB mutex is held, code populates the context with file numbers and names to preserve or delete, memtables and WAL writers to free, superversions to release, notifications to deliver, and snapshot state needed by a job. Once mutex-protected state has been updated, callers release the DB mutex and invoke `Clean()` or use the deletion queues in purge logic.

`SuperVersionContext::Clean()` first emits write-stall listener callbacks when notifications are enabled, then deletes old `SuperVersion` objects and clears vectors. `JobContext::Clean()` delegates to all SuperVersion contexts, deletes pending read-only memtables and log writers, clears those containers, and resets `job_snapshot`.

Snapshot helper methods require `snapshot_context_initialized` except for `GetJobSnapshotSequence()`, which returns `kMaxSequenceNumber` when no managed snapshot exists. `InitSnapshotContext()` is idempotent: after initialization, later calls return without changing existing context.

## State and persistence behavior

The context stores transient snapshots of persistent state, such as manifest file numbers, log numbers, live SST/blob file numbers, and candidate obsolete file names. It does not itself commit, delete, or persist files. Deletion and purge code consumes the vectors later.

`files_to_quarantine` captures file numbers whose MANIFEST or CURRENT persistence status is ambiguous, preventing premature deletion of newly generated SST/blob files or certain manifest transitions. WAL logs are excluded from this quarantine because minimum WAL retention is updated after successful manifest commits.

The managed snapshot in `job_snapshot` temporarily preserves a sequence boundary for compaction/flush work and is released during `Clean()`.

## Dependencies and integration points

The header depends on column-family definitions, log writer, version set metadata, `autovector`, hash containers, `ManagedSnapshot`, `SnapshotChecker`, `ReadOnlyMemTable`, `SuperVersion`, obsolete file info types, and event listener/write-stall types.

It integrates with `DBImpl::FindObsoleteFiles`, `PurgeObsoleteFiles`, flush jobs, compaction jobs, SuperVersion installation, write-stall notification delivery, WAL recycling/deletion, remote compaction OPTIONS retention, and transaction snapshot conflict logic.

## Risks and edge cases

- Destructors assert cleanup has already happened. Callers must invoke `Clean()` at least once for non-empty contexts and must do it after releasing the DB mutex.
- Listener callbacks in `SuperVersionContext::Clean()` run outside the mutex but can execute arbitrary user code; the context must already contain all information needed for safe notification.
- `InitSnapshotContext()` silently ignores repeated calls, so callers must ensure the first initialization is authoritative.
- `GetLatestSnapshotSequence()` and `GetEarliestSnapshotSequence()` assert initialization; using them before `InitSnapshotContext()` is a debug failure and may hide release-build misuse.
- `min_blob_file_number_to_keep` and `active_blob_direct_write_files` prevent races with direct-write blob files. Incorrect population can either leak obsolete blobs or delete active blobs too early.
- Move construction is supported for `SuperVersionContext`; copying is disabled to avoid double deletion.

## Test signals

Useful coverage includes tests for obsolete file purging, WAL recycling, direct-write blob retention, failed flush/compaction cleanup, SuperVersion install and deferred deletion, write-stall notification order, and snapshot-boundary behavior in compaction. Listener tests that assert write-stall, shutdown, flush, compaction, and background error callbacks also exercise the cleanup/notification design indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/job_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/kv_checksum.h -->
# sources/storage-engines/rocksdb/db/kv_checksum.h

## Purpose

`kv_checksum.h` implements lightweight, non-persistent protection tokens for individual key/value entries as they move through RocksDB internals. The `ProtectionInfo...` template classes represent XORs of independently seeded hashes over selected fields: key (`K`), value (`V`), operation/value type (`O`), sequence number (`S`), and column-family id (`C`).

The goal is to detect accidental corruption, field swaps, or mismatched metadata across internal transformations without imposing a persistent wire format. The file explicitly notes that integer fields are hashed in native byte order, so generated values are endianness-dependent and should not be stored as durable data.

## Important APIs, types, and functions

- `ProtectionInfo<T>` is the base token, with `GetStatus()`, `ProtectKVO()`, `ProtectKV()`, private `Encode()`, `Verify()`, and value accessors.
- `ProtectionInfoKVO<T>` represents a token that includes key, value, and op type. It can `StripKVO()`, `ProtectC()`, `ProtectS()`, update individual K/V/O fields, encode, and verify.
- `ProtectionInfoKVOC<T>` extends KVO with column-family id. It can `StripC()`, update K/V/O through the KVO member, update C, encode, and verify.
- `ProtectionInfoKVOS<T>` extends KVO with sequence number. It can `StripS()`, update K/V/O through the KVO member, update S, encode, and verify.
- `ProtectionInfoKV<T>` protects only key and value and supports encode/verify.
- Aliases `ProtectionInfo64`, `ProtectionInfoKVO64`, `ProtectionInfoKVOC64`, and `ProtectionInfoKVOS64` provide the common 64-bit form.
- Seed constants `kSeedK`, `kSeedV`, `kSeedO`, `kSeedS`, and `kSeedC` intentionally differ by a large odd increment to reduce swapped-field collisions.

## Control flow

A caller starts with default `ProtectionInfo<T>` value zero. Calling `ProtectKVO()` or `ProtectKV()` XORs the current token with seeded non-persistent hashes of the selected fields and returns a more specific protection type. `ProtectC()` and `ProtectS()` add column-family id or sequence number respectively. `Strip...()` methods apply the same hashes again to remove fields, returning to a less-specific type; after all protected fields are stripped, `GetStatus()` returns `OK` only if the value is back to zero.

Update methods support in-place transformations without fully stripping and re-protecting. For example, `UpdateK(old_key, new_key)` XORs out the old key hash and XORs in the new key hash. Slice and `SliceParts` overloads allow callers to protect contiguous and fragmented key/value representations.

`Encode(len, dst)` writes the low `len` bytes of the token using fixed-width little-endian encoders for 2/4/8 byte lengths, or a single byte for length 1. `Verify(len, checksum_ptr)` decodes the stored bytes and compares against the low bits of the current token.

## State and persistence behavior

Each protection class is intended to be exactly the size of `T`, enforced with `static_assert` in constructors. State is only the current XOR value. The template assumes unsigned integer types up to 64 bits, and truncates hash values when `T` is narrower than 64 bits.

Protection values are non-persistent. They depend on native byte order for integer fields such as `ValueType`, `SequenceNumber`, and `ColumnFamilyId`, and are based on `NPHash64`, which is suitable for in-process protection rather than stable storage checksums.

## Dependencies and integration points

The file depends on `db/dbformat.h` for `ValueType`, encoding helpers, and sequence types, `rocksdb/types.h` for `ColumnFamilyId`, and `util/hash.h` for `NPHash64`, `GetSliceNPHash64`, and `GetSlicePartsNPHash64`.

It integrates with write batch processing, memtable/table builders, compaction, and other internal paths that need to carry and verify per-entry protection across representation changes. The class names encode which fields are currently covered, giving compile-time structure to legal protect/strip transitions.

## Risks and edge cases

- This is not a cryptographic checksum. XOR composition can miss paired errors that cancel out, and narrower `T` values reduce detection strength.
- Integer hashing is endian-dependent, so encoded protection values must not be persisted or compared across architectures.
- `Encode()` and `Verify()` assert that `len <= sizeof(T)` and support only 1, 2, 4, or 8 byte lengths.
- The code uses `reinterpret_cast<char*>` on integer fields for hashing native memory bytes. Changes to type size or representation affect computed values.
- Correctness relies on callers applying update/strip operations with exactly the old and new field values. A wrong old value will make later verification fail or, in rare collision cases, falsely pass.

## Test signals

Relevant tests should cover KVO, KVOC, KVOS, and KV flows; `Slice` and `SliceParts` equivalence; update methods matching strip/re-protect behavior; encode/verify lengths; status returning corruption for mismatches; and intentional field swaps. Endianness non-persistence should be documented rather than tested as a stable cross-platform value.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/kv_checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/listener_test.cc -->
# sources/storage-engines/rocksdb/db/listener_test.cc

## Purpose

`listener_test.cc` is a RocksDB test suite for `EventListener` callback behavior. It validates callback ordering, callback payload completeness, thread ids, table properties, blob metadata, file operation notifications, background error suppression, shutdown notification semantics, column-family handle deletion notifications, and background job pressure snapshots.

The file is behavioral test code rather than production logic. It creates small DBs and column families, forces flushes/compactions/blob garbage collection, injects filesystem failures, blocks background jobs with sync points or sleeping tasks, and asserts listener-observed data against DB metadata.

## Important APIs, types, and functions

- `EventListenerTest` derives from `DBTestBase` and provides `BlobStr()` for generating blob index values plus a 110 KB write-buffer constant.
- `TestPropertiesCollector` and `TestPropertiesCollectorFactory` attach user-collected table properties used by listener assertions.
- `TestCompactionListener` checks `OnCompactionCompleted` payloads: input/output file info, file levels/numbers, table properties, thread id, DB pointer, and oldest blob file number.
- `TestCompactionPreCommitListener` verifies `OnCompactionBegin`, `OnCompactionPreCommit`, and `OnCompactionCompleted` ordering and checks that input files are still marked `being_compacted` at pre-commit time.
- `TestDBShutdownBeginListener` verifies shutdown callback count and DB pointer for cancel/close and failed open.
- `TestFlushListener` checks `OnTableFileCreated` and `OnFlushCompleted` payloads, thread status, slowdown/stop flags, table properties, file number, CF id/name, and oldest blob file number.
- `TableFileCreationListener` validates started/created/failure callbacks for flush and compaction table files, including injected filesystem failures and aborted empty output files.
- `BackgroundErrorListener` suppresses the first background error and lets retry succeed.
- `TestFileOperationListener` opts into file I/O notifications and counts read/write/flush/close/sync/truncate callbacks, including blob-file-specific counts.
- `BlobDBJobLevelEventListenerTest` checks blob file addition and garbage info in flush/compaction job-level callbacks and `CompactFiles()` output.
- `BlobDBFileLevelEventListener` checks blob file started/created/deleted callbacks.
- `BackgroundJobPressureTestListener` records background job pressure snapshots for later invariant checks.

## Control flow

Each `TEST_F` configures `Options`, installs one or more listeners, opens or reopens a test DB, performs writes, flushes, compactions, `CompactFiles()`, close/reopen, or failure injection, then checks listener state. Tests use `TEST_WaitForFlushMemTable()`, `TEST_WaitForCompact()`, and `TEST_WaitForBackgroundWork()` to avoid racing asynchronous callbacks.

Compaction tests create enough L0 files or manual compactions to force callbacks and reason codes. Sync points enforce ordering for pre-commit notification. Flush tests use multiple column families and table property collectors to verify callback sequence and payload. Multi-DB tests install many listeners across several DBs and verify callback ordering by column family and DB.

Failure tests use `FaultInjectionTestFS`, `SpecialEnv::drop_writes_`, and a custom `FileSystemWrapper` to make open, flush, or compaction fail, then assert notification counts and statuses. Blob tests enable blob files and garbage collection, then flush/compact to force blob additions, garbage records, file-level creation, and deletion notifications. Background pressure tests block low-priority compaction work, build L0 pressure through flushes, then unblock compaction and verify pressure rises and falls.

## State and persistence behavior

The test DB writes real SST, WAL, MANIFEST, and blob files under the test directory, but only as fixtures. Listener instances store observed callback state in vectors, atomics, counters, mutex-protected fields, and statuses. Some tests intentionally close and reopen DBs to verify recovery file reads and shutdown semantics.

The suite checks persistent metadata indirectly by comparing callback file numbers and blob file metadata against `TEST_GetFilesMetaData()`, `VersionStorageInfo`, table properties, and column-family metadata. It also verifies user-collected properties survive into listener payloads.

## Dependencies and integration points

The file depends on RocksDB DB test utilities, DBImpl internals, `VersionSet`, blob index encoding, write batch internals, file naming helpers, statistics/perf context headers, cache/table/options APIs, sync points, special/fault-injection environments, rate limiter utilities, and merge operator utilities.

It integrates with many EventListener hooks: compaction begin/pre-commit/completed, DB shutdown begin, table file creation started/created, flush completed, memtable sealed, column-family handle deletion started, background error, file operation finish callbacks, blob file creation/deletion, and background job pressure changed.

## Risks and edge cases

- Listener callbacks can run asynchronously on background threads. Tests must wait for background work before reading listener state; the file contains several explicit waits for this reason.
- Some listener implementations use mutexes, but not all counters are protected in the same way. Tests are written around expected callback sequencing; future parallelism changes may require stronger synchronization.
- `TestFlushListener` assumes only one flush at a time and stores a single previous table creation info object.
- Callback assertions that inspect `DBTestBase::db_` are skipped or guarded for multi-DB/close cases because the DB pointer can differ or be closing.
- Failure injection around filesystem activity and background retries is timing-sensitive; sync points and mock sleep are used to stabilize expected behavior.
- The tests assert `kUnknownFileChecksum` and `kUnknownFileChecksumFuncName`, so enabling real file checksums in these paths would require updating expected listener payloads.
- Background job pressure tests depend on scheduler behavior and L0 thresholds; changes to compaction scheduling or pressure semantics can break expectations.

## Test signals

This file is itself the test signal for listener behavior. It covers single and multi-CF flush/compaction, multiple DBs and listeners, compaction reasons for level/universal/FIFO/manual compactions, table creation success/failure/aborted outputs, memtable sealing sequence bounds, background error suppression and retry, file I/O callback opt-in, manifest reads during recovery, blob job and file callbacks, `CompactFiles()` blob output reporting, shutdown notifications on cancel/close/failed open, and background job pressure invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/listener_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_format.h -->
# sources/storage-engines/rocksdb/db/log_format.h

## Purpose

`log_format.h` defines the shared WAL/log record format constants used by RocksDB log readers and writers. It contains the record type enum, safe-ignore mask, maximum record type, block size, and header sizes for normal and recyclable log records.

The file is a compact wire-format contract. Changes here affect compatibility between WAL writers, WAL readers, recovery, recyclable log handling, compression records, user-defined timestamp size records, and WAL verification metadata.

## Important APIs, types, and functions

- `log::RecordType` is an 8-bit enum.
- `kZeroType` marks preallocated file space.
- `kFullType`, `kFirstType`, `kMiddleType`, and `kLastType` represent normal complete or fragmented records.
- `kRecyclableFullType`, `kRecyclableFirstType`, `kRecyclableMiddleType`, and `kRecyclableLastType` are recyclable log variants that carry a log number in the larger header.
- `kSetCompressionType` identifies compression type changes.
- `kUserDefinedTimestampSizeType` and `kRecyclableUserDefinedTimestampSizeType` store timestamp-size metadata; comments note that for values at or above 10, bit 0 indicates whether the record is recyclable.
- `kPredecessorWALInfoType` and `kRecyclePredecessorWALInfoType` support WAL verification.
- `kRecordTypeSafeIgnoreMask` is bit 7; unknown record types with this bit set may be ignored safely.
- `kMaxRecordType` is currently `kRecyclePredecessorWALInfoType`.
- `kBlockSize` is 32768 bytes.
- `kHeaderSize` is 7 bytes: checksum, length, and type.
- `kRecyclableHeaderSize` is 11 bytes: normal header plus 4-byte log number.

## Control flow

Log writers choose a `RecordType` based on whether a logical record fits in one block, needs fragmentation, belongs to a recyclable WAL, changes compression/timestamp metadata, or records WAL verification information. Log readers interpret the type byte using this enum and the corresponding header size. Fragmented records are reconstructed from first/middle/last sequences; full records stand alone.

The safe-ignore mask gives readers a way to skip newer unknown record types when bit 7 is set. `kMaxRecordType` bounds the currently known type range for validation.

## State and persistence behavior

All constants here define persistent WAL bytes. Normal records store a 4-byte checksum, 2-byte length, and 1-byte type. Recyclable records add a 4-byte log number. `kBlockSize` fixes the fragmentation and padding unit. `kZeroType` allows preallocated zeroed regions.

Because these constants are persistent-format contracts, changing numeric enum values, block size, or header sizes can break recovery compatibility with existing WAL files.

## Dependencies and integration points

The file only depends on `<cstdint>` and `rocksdb/rocksdb_namespace.h`. It is included by log reader and writer implementations, DB recovery, WAL recycling code, compression/timestamp metadata handling, and WAL verification code.

It also points maintainers to `../doc/log_format.txt` for detailed format documentation.

## Risks and edge cases

- Numeric enum values are compatibility-sensitive and should not be reordered.
- Unknown types without `kRecordTypeSafeIgnoreMask` should be treated as errors by readers; new ignorable extensions need the high bit set.
- Recyclable and non-recyclable record pairs must stay aligned with header parsing logic.
- Fragmentation correctness depends on `kBlockSize` and `kHeaderSize`; changing either affects every reader/writer boundary calculation.
- Values `>= 10` use bit 0 as recyclable indication by convention, so future type allocation must preserve that scheme where applicable.

## Test signals

Relevant tests include WAL writer/reader round trips for full and fragmented records, recyclable WAL recovery, preallocated zero handling, compression and user-defined timestamp records, safe-ignore behavior for unknown high-bit types, corrupted header detection, and predecessor WAL info verification. Recovery tests should include old WALs to guard format compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_format.h -->
