# Research Group subset-b-008611

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/error_handler_fs_test.cc -->
# sources/storage-engines/rocksdb/db/error_handler_fs_test.cc

## Purpose

This file is a RocksDB gtest suite for DB background error handling when the active `FileSystem` or `Env` reports write, read, manifest, compaction, WAL, retryable, no-space, corruption, and fenced I/O failures. It uses `FaultInjectionTestFS`, `CompositeEnvWrapper`, sync points, and listener callbacks to force failures at precise DB implementation boundaries, then verifies `Status::Severity`, manual `Resume()`, automatic retry/recovery, data visibility, WAL durability, manifest replacement, quarantine cleanup, and statistics counters.

The tests exercise both ordinary single-DB operation and multi-column-family / multi-DB interactions. Later parameterized tests specifically assert that `IOFenced` errors become fatal and cannot be cleared by `Resume()`.

## Important APIs, Types, and Functions

- `DBErrorHandlingFSTest : DBTestBase` constructs a fault-injection file system over the base test environment and exposes `GetManifestNameFromLiveFiles()` to identify the live descriptor file after recovery.
- `ErrorHandlerFSListener : EventListener` is the central test probe. It observes table creation starts, background errors, recovery begin/end notifications, can disable auto recovery, override the background error status, and inject a filesystem error after a configurable number of table-creation callbacks.
- `OnTableFileCreationStarted()` toggles the fault filesystem inactive once `file_count_` reaches zero, allowing multi-DB tests to fail during a specific SST creation.
- `OnErrorRecoveryBegin()` can set `*auto_recovery = false`, testing user listener veto of automatic recovery.
- `OnBackgroundError()` can replace the error observed by RocksDB with a test-provided `Status`, allowing compaction paths to be forced into hard/soft severity cases.
- `OnErrorRecoveryEnd()` records completion and the new background error so tests can assert successful recovery, aborted recovery, or shutdown-in-progress races.
- `WaitForRecovery()` and `WaitForTableFileCreationStarted()` use `InstrumentedMutex`/`InstrumentedCondVar` to synchronize tests with asynchronous recovery and table creation.
- The suite uses `SyncPoint::SetCallBack`, `LoadDependency`, `TEST_SYNC_POINT`, and named production sync points such as `BuildTable:BeforeFinishBuildTable`, `VersionSet::LogAndApply:WriteManifest`, `WritableFileWriter::Append:BeforePrepareWrite`, and `NotifyOnErrorRecoveryEnd:MutexUnlocked:*`.

## Control Flow and Test Coverage

Early flush tests inject errors around SST build lifecycle points. `FlushWriteError` and `FlushWriteNoSpaceError` assert no-space flush errors become hard errors and require manual `Resume()`. `FlushWriteRetryableError` checks retryable generic I/O failures at finish, sync, and close table-file points become soft errors. `FlushWriteFileScopeError` verifies file-scoped data-loss errors are also treated as soft/recoverable for table output failure scenarios.

WAL/flush interactions are split by WAL settings. `FlushWALWriteRetryableError` and `FlushWALAtomicWriteRetryableError` inject failure while syncing closed WALs and expect hard errors even when the underlying status is retryable. The no-WAL flush tests verify soft severity and continued in-memory write/read behavior when `WriteOptions::disableWAL` is true.

Manifest tests inject failures in `VersionSet::LogAndApply:WriteManifest`. They verify hard/no-space, retryable, file-scope, no-WAL retryable, and double-failure behavior. Successful recovery must produce a different live manifest and clear `TEST_GetFilesToQuarantine()`, preserving keys across reopen. `DoubleManifestWriteError` deliberately fails the first recovery `Resume()` and then succeeds after callbacks are cleared.

Compaction tests cover manifest append failures and output-file failures in background compaction. Sync-point dependencies force compaction to reach the failing state while foreground flush operations proceed. The suite checks soft retryable errors, hard overrides, disabled flaky variants for retryable/file-scope compaction write errors, and unrecoverable corruption. Compaction recovery cases verify rescheduling and eventual successful compaction.

WAL write tests inject append failures after partial successful WAL writes. They assert corrupted second batches are not visible or recovered, earlier synced batches remain durable, and later writes after `Resume()` or auto-recovery are durable. Multi-CF WAL tests ensure all column families flush consistent state after recovery.

Multi-DB tests share an `SstFileManager` and a default `FaultInjectionTestEnv` across three DB instances. Per-DB `FaultInjectionTestFS` wrappers simulate different failure timing. The tests verify that one DB can soft-recover, one can hard-recover, and another can proceed without error while shared file-manager state remains closeable.

Auto-recovery tests configure `max_bgerror_resume_count` and `bgerror_resume_retry_interval`, then coordinate retry loops with sync points. They cover successful and failed auto recovery for no-WAL flush, normal flush, manifest writes, compaction manifest writes, compaction output writes, WAL append failures, aborted recovery after retry exhaustion, and races between recovery threads and DB destruction.

Read-error tests inject retryable read-like validation failures in `BuildTable:BeforeOutputValidation` and compaction read points. They validate that the background error is cleared after auto recovery, counters are incremented, and data remains available after reopen. Atomic flush variants cover multi-CF atomic flush read/no-space failures.

The parameterized `DBErrorHandlingFencingTest` runs under both `paranoid_checks` values and covers flush, manifest, compaction, and WAL `IOFenced` failures. Each asserts fatal severity, `IsIOFenced()`, and that subsequent `Resume()` or writes remain fenced rather than clearing the fatal state.

## State and Persistence Behavior

The tests deliberately transition the DB through active, background-error, recovery-in-progress, resumed, closed, destroyed, and reopened states. Persistence expectations are explicit: data flushed before an error must survive reopen; data from partially failed WAL batches must not become visible; no-WAL writes remain visible in memory through soft flush failure and are persisted after recovery/flush; manifest recovery replaces the descriptor file and empties quarantine state.

The fixture-level `FaultInjectionTestFS` controls filesystem activity and error status. Several tests disable the FS until a production path hits the failing sync point, then reactivate it before manual resume or auto-recovery. The listener tracks `new_bg_error_` to distinguish successful recovery (`OK`), aborted recovery, shutdown-in-progress, and unrecoverable/fatal errors.

Statistics counters are a persistence-adjacent signal for DB error-handler state transitions: `ERROR_HANDLER_BG_ERROR_COUNT`, `ERROR_HANDLER_BG_IO_ERROR_COUNT`, `ERROR_HANDLER_BG_RETRYABLE_IO_ERROR_COUNT`, `ERROR_HANDLER_AUTORESUME_COUNT`, retry totals, success counts, and the auto-resume retry histogram are asserted in selected tests.

## Dependencies and Integration Points

This test file integrates with `DBTestBase`, `DBImpl` test-only methods (`TEST_GetBGError`, `TEST_GetFilesToQuarantine`, `TEST_WaitForCompact`), `SstFileManagerImpl`, `FaultInjectionTestFS`, `FaultInjectionTestEnv`, RocksDB listeners, `IOStatus` metadata (`SetRetryable`, `SetScope`, `SetDataLoss`, `IOFenced`), and the sync-point test framework.

The production integration points under test include flush jobs, table building and validation, WAL append/sync paths, manifest log-and-apply, compaction scheduling/output, auto-recovery loops, error listener notification in `EventHelpers`, and DB destruction/close coordination with recovery threads.

## Risks and Maintenance Notes

The suite is highly timing-sensitive. Many tests depend on exact sync-point names inside production code; refactors that rename or move sync points can silently invalidate intended failure timing. Tests that sleep via retry intervals or wait for asynchronous recovery can be slow or flaky on constrained environments.

Several tests skip under `mem_env_` because real filesystem behavior is required. Disabled compaction write retryable/file-scope tests signal known instability or incomplete coverage in those scenarios.

There are typo-like test names (`FlushWrit...`, `fromt`, `cleand`, `sucessful`) that do not affect behavior but can complicate searching. Manual ownership appears in multi-DB tests (`new FaultInjectionTestEnv`, raw `FaultInjectionTestFS*`, explicit `delete def_env`), so cleanup paths must stay exception/assert-safe enough for gtest process semantics.

Fencing tests encode a strong contract: once `IOFenced` is observed, recovery must not downgrade it. Changes to error severity mapping must preserve this fatal behavior.

## Test Signals

The file itself is test coverage. It should be run via the RocksDB gtest target for `error_handler_fs_test` on a non-mock filesystem environment. Passing signals include expected status severities, successful/manual `Resume()` outcomes, recovery listener notifications, stable post-reopen reads, manifest replacement, quarantine cleanup, expected L0/L1 file counts after compaction, and precise error-handler statistic counters.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/error_handler_fs_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/event_helpers.cc -->
# sources/storage-engines/rocksdb/db/event_helpers.cc

## Purpose

This file implements RocksDB event-helper routines that centralize listener notification and event logging for table-file creation/deletion, blob-file creation/deletion, background errors, and error-recovery completion. It also wires `EventListener::CreateFromString()` through the customizable object loader.

The implementation is pure glue: it packages internal DB event data into listener-facing structs, emits JSON records through `EventLogger`, and carefully releases the DB mutex around callbacks that may call back into user code.

## Important APIs, Types, and Functions

- `EventListener::CreateFromString()` calls `LoadSharedObject<EventListener>()`, enabling listener creation from the RocksDB customization registry.
- `SafeDivide()` returns zero on a zero denominator and is used for average key/value sizes in table-property JSON.
- `EventHelpers::AppendCurrentTime()` writes `time_micros` based on `std::chrono::system_clock`.
- `NotifyTableFileCreationStarted()` builds `TableFileCreationBriefInfo` and invokes `OnTableFileCreationStarted()` on all listeners.
- `NotifyOnBackgroundError()` asserts the DB mutex is held, unlocks it, invokes `OnBackgroundError()`, permits unchecked status handling, optionally invokes `OnErrorRecoveryBegin()`, and relocks the mutex.
- `LogAndNotifyTableFileCreationFinished()` logs rich table-file creation JSON and sends `TableFileCreationInfo` to `OnTableFileCreated()`.
- `LogAndNotifyTableFileDeletion()` logs deletion JSON and sends `TableFileDeletionInfo`.
- `NotifyOnErrorRecoveryEnd()` copies old/new background errors under mutex, unlocks, emits legacy and newer recovery-end callbacks, and relocks.
- Blob helpers mirror the table-file flow for `BlobFileCreationBriefInfo`, `BlobFileCreationInfo`, and `BlobFileDeletionInfo`.

## Control Flow and State Behavior

Every helper has a fast exit when both logging and listener notification are unnecessary. If no logger/listener consumes a `Status`, the code calls `PermitUncheckedError()` so RocksDB's unchecked-status diagnostics do not fire for intentionally ignored values.

Logging paths allocate a local `JSONWriter`, append the timestamp, then serialize event-specific fields before calling `event_logger->Log()`. Table creation logging includes file descriptor metadata, checksum information, sequence-number bounds, blob-file linkage, full `TableProperties`, user-readable properties, and a decoded human-readable `seqno_to_time_mapping` when possible.

Listener paths fill concrete listener info structs after logging. Status objects copied into those structs are also permitted as unchecked after callbacks return. Background-error and recovery-end notification paths intentionally release `db_mutex` while invoking arbitrary listener code; recovery-end copies statuses first to avoid races while the lock is released.

## Persistence and External Effects

This file does not persist data directly. Its external effects are event-log records and calls into user-supplied `EventListener` implementations. Event logs become operational observability data for table/blob creation and deletion. Listener callbacks can mutate control state: notably `NotifyOnBackgroundError()` passes a mutable `Status* bg_error` and `bool* auto_recovery`, allowing a listener to override error severity/status or veto automatic recovery.

## Dependencies and Integration Points

The implementation depends on `db/event_helpers.h`, `rocksdb/listener.h`, `logging/event_logger.h`, `rocksdb/convenience.h`, `rocksdb/utilities/customizable_util.h`, table properties, file descriptors, and mutex instrumentation. `TEST_SYNC_POINT` calls in `NotifyOnErrorRecoveryEnd()` are consumed by tests such as `error_handler_fs_test.cc` to force races while the DB mutex is unlocked.

Production callers include flush/table-build, compaction, blob-file, manifest/error-handler, and file-deletion paths that need consistent listener and JSON behavior.

## Risks and Maintenance Notes

The mutex-unlock sections are correctness-sensitive because listener code is arbitrary. Any new callback added here must avoid using references to mutable DB state after unlocking unless it first makes stable copies.

JSON field names are operationally visible. There is a likely field swap in the creation-time block: `"oldest_key_time"` is populated from `newest_key_time` and `"newest_key_time"` from `oldest_key_time`; changing it may affect log consumers but leaving it may mislead diagnostics.

`NotifyOnBackgroundError()` invokes `OnErrorRecoveryBegin()` only if `*auto_recovery` is still true after `OnBackgroundError()`, so listener ordering can affect recovery policy. Blob creation logs do not hex-escape `file_checksum` unlike table creation, which may be intentional but is a consistency risk for binary checksum strings.

## Test Signals

Direct signals are the DB listener and error-handling tests. `error_handler_fs_test.cc` validates background error mutation, auto-recovery veto, recovery-end callbacks, and mutex-release race handling. Event log correctness is indirectly covered by table/blob event tests elsewhere; useful assertions include JSON field presence, status propagation, and callbacks firing exactly once per event.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/event_helpers.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/event_helpers.h -->
# sources/storage-engines/rocksdb/db/event_helpers.h

## Purpose

This header declares the `EventHelpers` utility class used by RocksDB DB internals to log event records and notify `EventListener` instances for table files, blob files, background errors, and recovery lifecycle events. It provides a narrow static API that keeps event packaging out of the individual DB code paths.

## Important APIs and Types

- `AppendCurrentTime(JSONWriter*)` appends the common timestamp field used by event-log records.
- `NotifyTableFileCreationStarted()` emits the lightweight pre-creation listener event with DB name, column family name, file path, job id, and `TableFileCreationReason`.
- `NotifyOnBackgroundError()` lets listeners observe and mutate a background error and auto-recovery decision while coordinating with `InstrumentedMutex`.
- `LogAndNotifyTableFileCreationFinished()` records and reports full SST creation metadata including `FileDescriptor`, oldest linked blob file number, `TableProperties`, status, and file checksum fields.
- `LogAndNotifyTableFileDeletion()` records and reports table deletion metadata.
- `NotifyOnErrorRecoveryEnd()` reports old and new background error state after recovery finishes.
- `NotifyBlobFileCreationStarted()`, `LogAndNotifyBlobFileCreationFinished()`, and `LogAndNotifyBlobFileDeletion()` are the blob-file analogs.
- Private `LogAndNotifyTableFileCreation()` is declared as an internal helper taking a `TableFileCreationInfo`, but it is not implemented or used in the paired `.cc` file in this snapshot.

## Control Flow and State Expectations

All methods are static and stateless. Callers pass listener vectors, logger pointers, DB/CF names, file identifiers, status objects, and mutex pointers. The contract implied by the header is that DB code remains owner of lifecycle state, while `EventHelpers` handles fan-out and observability.

The background-error and recovery-end APIs explicitly accept `InstrumentedMutex*`, signaling that implementations may unlock around callbacks. Callers must hold the mutex as required by the implementation and must tolerate listener-side changes to background error and auto-recovery flags.

## Dependencies and Integration Points

The header depends on `db/column_family.h`, `db/version_edit.h`, `logging/event_logger.h`, `rocksdb/listener.h`, and `rocksdb/table_properties.h`. It is included by DB implementation files that need listener notification without exposing all event-construction details inline.

It forms the public internal contract used by tests like `error_handler_fs_test.cc`, which relies on recovery begin/end and table-creation-started notifications to coordinate fault injection.

## Risks and Maintenance Notes

Because this header sits between core DB state machines and arbitrary listener code, signature changes have broad impact across flush, compaction, blob, deletion, and error-handler call sites. New fields should be added in a way that preserves listener ABI/API expectations.

The private `LogAndNotifyTableFileCreation()` declaration appears stale in this snapshot. If it remains unused, it can confuse maintainers looking for a shared implementation path. If revived, it should preserve the current logging and listener status-handling behavior in `event_helpers.cc`.

## Test Signals

Compile coverage is the primary header-level signal. Behavioral signals come from listener tests, event log tests, blob/table creation tests, and the background error recovery suite. Important assertions include that callbacks receive complete DB/CF/file/status metadata and that background-error callbacks can safely alter recovery decisions.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/event_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/experimental.cc -->
# sources/storage-engines/rocksdb/db/experimental.cc

## Purpose

This file implements APIs in `ROCKSDB_NAMESPACE::experimental`. It has two major areas: thin experimental DB utilities for compaction, manifest checksum retrieval, and offline manifest repair; and a larger experimental SST query-filter framework that serializes table-property filters and builds range-query table filters from them.

The SST query-filter code introduces configurable key-segment extraction, filter input selection, bytewise min/max filters, category/extractor wrappers, collector factories, versioned configuration lookup, and range-time filter evaluation.

## Important APIs, Types, and Functions

- `SuggestCompactRange(DB*, ColumnFamilyHandle*, const Slice*, const Slice*)` validates `db != nullptr` and delegates to `DB::SuggestCompactRange()`.
- `PromoteL0(DB*, ColumnFamilyHandle*, int)` validates `db != nullptr` and delegates to `DB::PromoteL0()`.
- The overload `SuggestCompactRange(DB*, const Slice*, const Slice*)` uses `db->DefaultColumnFamily()` and assumes `db` is non-null before the helper validates it, which is a null-dereference risk.
- `GetFileChecksumsFromCurrentManifest()` locates the current manifest, opens it as an optimized manifest read, iterates records with `FileChecksumRetriever`, and fills `FileChecksumList`.
- `UpdateManifestForFilesState()` uses `OfflineManifestWriter` to recover versions, scans live SST files, opens them through `FileSystem`, compares actual file temperature with manifest temperature, writes replacement `VersionEdit` entries when needed, and logs success/failure.
- `SemiStaticCappedKeySegmentsExtractor<N>` and `DynamicCappedKeySegmentsExtractor` implement `KeySegmentsExtractor` by splitting keys at cumulative byte widths, capping segment ends to short key length, and producing stable extractor ids such as `CappedKeySegmentsExtractor4b8b`.
- `GetFilterInput()` selects the whole key, a segment, or a segment range from a key and extracted segment ends, and returns both selected input and the lead-up prefix before that input.
- `SerializeFilterInput()`, `DeserializeFilterInput()`, and `GetFilterInputSerializedLength()` encode/decode one-byte selector forms for whole key, legacy prefix, user timestamp, column name, first 16 single segments, and selected small segment ranges.
- `CategorySetToUint()` and `UintToCategorySet()` reinterpret category bitsets as `uint64_t` and back.
- `BuiltinSstQueryFilters` defines serialized filter tags for extractor/category wrappers and bytewise min/max filters.
- `SstQueryFilterBuilder` and `SstQueryFilterConfigImpl` are internal polymorphic interfaces for constructing encoded filters.
- `CategoryScopeFilterWrapperBuilder` wraps another builder so it only sees keys from selected extractor categories, and serializes category scope plus one nested filter.
- `BytewiseMinMaxSstQueryFilterConfig` builds a filter recording smallest/largest non-empty selected inputs and a separate empty-input flag; reverse mode inverts min/max interpretation for reverse-ordered segments.
- `SstQueryFilterConfigsManagerImpl` stores versioned named filter configs, creates table-property collector factories, and produces range-query table filters.
- Public factories include `MakeSharedCappedKeySegmentsExtractor()`, `MakeSharedBytewiseMinMaxSQFC()`, `MakeSharedReverseBytewiseMinMaxSQFC()`, and `SstQueryFilterConfigsManager::MakeShared()`.

## Control Flow and State Behavior

Manifest checksum retrieval first resolves `CURRENT` to a manifest path, resets the caller-provided checksum list, creates a `SequentialFileReader`, and scans all manifest log records. Corruption callbacks update the local status if still OK. The function returns retriever status before fetching the checksum list.

`UpdateManifestForFilesState()` recovers the offline manifest, then iterates initialized, non-dropped column families and their levels. For each SST, it builds a table filename and opens it with `Temperature::kUnknown` so the filesystem can search all tiers. If temperature repair is enabled and actual temperature differs from manifest metadata, it deletes and re-adds the file in a `VersionEdit` preserving all other metadata. Non-empty edits are applied through `OfflineManifestWriter::LogAndApply()` with a DB directory handle. Counters track updated files and column families.

The filter-building path starts with versioned `SstQueryFilterConfigs`. A factory creates `MyCollector` for the active version/config name. Each user key is extracted into segments/categories if an extractor exists. Sanity checks enforce category contiguity and selected-input ordering. Builders accumulate min/max state. On `Finish()`, the collector computes exact encoded size, optionally wraps filters with extractor/category metadata, writes schema version `1`, serializes filter counts and lengths, and stores the resulting bytes in user-collected table property `rocksdb.sqfc`.

The range-query read path creates a `RangeQueryFilterReader` capturing inclusive lower and exclusive upper bounds, the current extractor, and the manager's extractor map. For each table, the table-filter lambda looks for `rocksdb.sqfc`, validates schema version, and parses nested filters. Unknown, corrupt, unsupported, or mismatched filters intentionally return `true` so RocksDB reads the table rather than incorrectly filtering it out. A bytewise min/max filter can return `false` when both bounds and recorded table min/max prove no overlap.

Config population requires filtering versions to be contiguous, nonzero, and duplicate-free per version/config name. Factories use a relaxed atomic filtering version; version zero is a special empty configuration. For a requested version, `GetConfigs()` uses the greatest configuration version less than or equal to the active version for that config name.

## Persistence and Encoded Data

The manifest functions directly read and update RocksDB persistent metadata. `UpdateManifestForFilesState()` can append new manifest edits offline, so incorrect metadata preservation would affect DB reopen behavior.

The SST query-filter framework persists encoded filter bytes in table properties under `rocksdb.sqfc`. The encoded format includes a schema byte, varint filter counts/lengths, wrapper tags, extractor ids, category sets, filter input selector bytes, empty-input flags, and min/max selected input values. This is durable per SST and consumed later by range query table filtering.

## Dependencies and Integration Points

The utility portion depends on `DB`, `DBImpl`, manifest helpers, `VersionEdit`, `OfflineManifestWriter`, `VersionSet`/column-family metadata, `FileSystem`, manifest log readers, `FileChecksumRetriever`, and logging.

The query-filter portion depends on experimental public types declared in `rocksdb/experimental.h`, `TablePropertiesCollector`, user-collected table properties, `Slice`, varint coding helpers, `RelaxedAtomic`, unordered maps/sets, and table-filter hooks returned by `TablePropertiesCollectorFactory::Factory`.

Integration points include DB option plumbing for collector factories, range-query code that can use `GetTableFilterForRangeQuery()`, and object lifetime assumptions for captured `Slice` bounds and shared manager/extractor objects.

## Risks and Maintenance Notes

The overload `SuggestCompactRange(DB*, const Slice*, const Slice*)` dereferences `db` before the null check in the three-argument helper. Passing null to that overload can crash instead of returning `InvalidArgument`.

Several selector variants in `GetFilterInput()` (`SelectLegacyKeyPrefix`, `SelectUserTimestamp`, `SelectColumnName`) contain `assert(false)` and return an empty slice. In release builds, malformed or prematurely enabled configs using those selectors could silently degrade to unsafe/no-op behavior.

`CategorySetToUint()` and `UintToCategorySet()` rely on `reinterpret_cast` between category set storage and `uint64_t`. Static size checks help, but aliasing/representation assumptions are still delicate.

The serialized filter format is intentionally permissive on read: corruption or unknown types fall back to "may match." That protects correctness but can hide encoding bugs as lost optimization. Many TODO/FIXME comments call out missing unit tests, unsupported expanded selector cases, legacy/user timestamp/column-name support, filter-length subtleties, and partial-failure reporting in collectors.

`GetTableFilterForRangeQuery()` captures `Slice` objects whose backing buffers must outlive read operations; callers must honor the comment or risk dangling references. Collector sanity checks return corruption if category or segment ordering invariants are violated, so custom extractors must preserve those ordering contracts.

`UpdateManifestForFilesState()` opens every live SST through the filesystem and writes manifest edits offline. Failures midway stop processing; only edits already applied before a later failure persist. Callers should treat this as an administrative repair operation requiring careful DB-closed/offline assumptions from `OfflineManifestWriter`.

## Test Signals

Useful tests for the utility functions include null DB validation, current-manifest checksum extraction over valid and corrupted manifests, temperature repair with files on different filesystem tiers, and no-op repair when manifest temperature already matches.

Useful tests for query filters include capped extractor segment ends for short and long keys, selector serialization/deserialization boundaries, min/max filters for forward and reverse order, empty selected inputs, category scope behavior, corrupt/unknown encoded filters falling back to may-match, collector finish encoding size consistency, version population validation, `SetFilteringVersion()` bounds, and lifetime-safe table-filter use across multiple SST properties.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/experimental.cc -->
