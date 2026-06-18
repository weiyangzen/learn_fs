# Research: subset-b-008709

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/backup/backup_engine_test.cc -->
# sources/storage-engines/rocksdb/utilities/backup/backup_engine_test.cc

## Purpose
This is the main non-Windows unit/integration test file for RocksDB's `BackupEngine` and `BackupEngineReadOnly`. It drives backup creation, restore, verification, metadata parsing, shared-file naming, corruption handling, rate limiting, direct I/O, file temperature preservation, file exclusion, concurrency, and lifecycle interruption behavior. The file is intentionally broad: it builds a chrooted DB and backup filesystem, injects failure modes through wrappers and sync points, then verifies both public API outcomes and persisted backup directory layout.

## Important APIs, Types, and Helpers
`DummyDB` is a `StackableDB` shim used when tests need synthetic live files without a full DB. Its `GetLiveFilesStorageInfo()` maps mocked filenames to `LiveFileStorageInfo`, assigns file types, sizes, and optional unknown checksum metadata, and validates file-name parsing.

`TestFs` wraps `FileSystem` to simulate write/delete/read/listing/directory failures, track written files, enforce file write/delete limits, count direct-I/O file opens, inject dummy sequential files, and provide mocked file attributes for synthetic DB files. `FileManager` wraps `Env` with backup-directory utilities for random file selection, deletion, append, content corruption, checksum-field corruption in metadata, and simple file writes.

`BackupEngineTest` owns the core fixture state: chrooted DB and backup environments, `TestFs` wrappers, `Options`, `BackupEngineOptions`, live `DB`, optional `DummyDB`, and `BackupEngine`. Key fixture methods include `SetEnvsFromFileSystems()`, `OpenDB()`, `CloseAndReopenDB()`, `InitializeDBAndBackupEngine()`, `OpenDBAndBackupEngine()`, `OpenBackupEngine()`, `AssertBackupInfoConsistency()`, `AssertBackupConsistency()`, `GetDataFilesInDB()`, `GetRandomDataFileInDB()`, and `CorruptRandomDataFileInDB()`.

Shared helpers `FillDB()`, `AssertExists()`, and `AssertEmpty()` create deterministic key ranges and verify restored contents. `BackupEngineTestWithParam` runs major scenarios with `share_files_with_checksum` both off and on. Rate-limiting parameterized fixtures vary custom vs legacy rate limiter configuration, single vs multi-thread backup, and byte limits.

## Control Flow and Test Coverage
The early tests validate basic backup semantics. `IncrementalRestore` creates SST and blob files, tests excluded-file callbacks, clean restores, incremental restore with missing SST/blob files, and corruption-sensitive restore modes (`kPurgeAllFiles`, `kKeepLatestDbSessionIdFiles`, `kVerifyChecksum`). `FileCollision`, `NoDoubleCopy_And_AutoGC`, `NoShareTableFiles`, and the share-with-checksum tests assert that shared table/blob files are reused, collisions are detected when checksum metadata is insufficient, and garbage collection removes only unreferenced shared files.

Corruption scenarios cover backup metadata damage, missing private files, backup-file content changes with preserved size, DB table/blob corruption before backup, corruption during copying through `SyncPoint`, and properties-block corruption. Tests explicitly distinguish what file-size verification can catch from what checksum verification can catch. Naming-option tests exercise legacy CRC32C+size names, DB session ID names, size indicators, old pre-6.12 table properties, transition/upgrade paths, and incremental behavior when DB-side files or backed-up shared files are corrupt.

Lifecycle and persistence tests cover interrupted backup creation, stale temporary file cleanup through `GarbageCollect()`, `DeleteBackup()`, `PurgeOldBackups()`, and `CreateNewBackup()`, options-file backup, set-options races during checkpoint creation, manifest rollover during backup, metadata strings including binary metadata and size limits, schema version 2 compatibility, and unsupported schema fields. Read-only tests verify that read-only engines do not delete files, can restore, can expose backups as read-only DBs through `BackupInfo::name_for_open` and `env_for_open`, and honor `max_valid_backups_to_open` only in read-only mode.

The tail tests stress operational concerns: progress callback behavior and exception-to-aborted conversion, env error propagation, creation when latest backup metadata is corrupted, write-only engines with `max_valid_backups_to_open = 0`, direct I/O readers/writers, background thread CPU priority demotion, `BACKUP_READ_BYTES`/`BACKUP_WRITE_BYTES` statistics, file temperatures during backup/restore, `exclude_files_callback` with alternate backup directories, I/O buffer-size selection from defaults/options/rate limiter burst size, and randomized stop points via `BackupEngineImpl::ShouldStopBackup`.

## State and Persistence Behavior
The tests model the backup directory as a persistent tree under chrooted `backupdir_`, especially `meta/<id>`, `private/<id>`, `shared`, and `shared_checksum`. Assertions check persisted file existence, file sizes, temporary dot-prefixed files, metadata contents, backup ID allocation, corrupted-backup discovery, and whether shared files survive deletion of individual backups. Restore tests repeatedly destroy the DB directory, restore a chosen backup or latest backup, then reopen RocksDB to verify key ranges and checksum outcomes.

Several tests depend on metadata schema details. Schema version 2 records file sizes, excluded files, app metadata, and temperature-related data; tests deliberately write old/minimal/future-compatible metadata using test hooks. Backup file details are expected to report `FileType` correctly for SST, WAL, MANIFEST, CURRENT, and OPTIONS. Excluded files are treated as weak references: they can be restored only when available from alternate backup engines and do not prevent deletion when no included backup still owns the file.

## Dependencies and Integration Points
This file integrates public RocksDB APIs (`DB`, `BackupEngine`, `BackupEngineReadOnly`, `RestoreOptions`, `CreateBackupOptions`, `BackupInfo`, `RateLimiter`, `Statistics`) with internal test and implementation hooks (`DBImpl`, `BackupEngineImpl`, `TEST_SetBackupMetaSchemaOptions`, `TEST_SetDefaultRateLimitersClock`, `SyncPoint`, `SpecialEnv`, `FileTemperatureTestFS`). It relies on DB file naming helpers, file checksum factories, live file storage metadata, chroot/composite environments, direct I/O support checks, and RocksDB's custom test harness.

## Risks and Edge Cases
The tests expose backup risks around stale shared files, file-name collision, backup-vs-DB corruption ambiguity, partial backup cleanup, exceptions in user callbacks, unsupported metadata versions, direct I/O fallback, rate-limiter accounting, and concurrent readers/writers on the same backup directory. Some comments document intentional trade-offs, such as DB session ID naming avoiding full rescans and `kKeepLatestDbSessionIdFiles` being more prone to subtle corruption than checksum verification. Several tests are skipped or gated under valgrind/direct-I/O/platform conditions because runtime or filesystem capabilities affect signal quality.

## Test Signals
The file itself is test signal: it contains dozens of `TEST_F`/`TEST_P` cases and a `main()` registering GoogleTest on non-Windows. Important signals are public `Status` classes (`OK`, `NotFound`, `Corruption`, `InvalidArgument`, `Aborted`, `Incomplete`), backup info/file-detail consistency, restored key-range assertions, filesystem write lists, direct-I/O counters, ticker statistics, rate-limited mock time deltas, and sync-point-controlled race/corruption outcomes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/backup/backup_engine_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.cc -->
# sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.cc

## Purpose
This file implements BlobDB's internal compaction filters. The filters remove expired or evicted blob indexes from the base DB, optionally apply the user's compaction filter to values stored in blob files, and, when garbage collection is enabled, relocate live blobs from old blob files into newly created blob files during compaction.

## Important APIs and Functions
`BlobIndexCompactionFilterBase::~BlobIndexCompactionFilterBase()` closes and registers any open output blob file, then records expired and evicted blob-index counters. `FilterV2()` is the central base-DB compaction path. Non-blob values are either kept or passed to the user compaction filter. Blob-index values are decoded with `BlobIndex::DecodeFrom()`, removed if TTL has expired, removed if their file number predates `next_file_number` and is absent from `current_blob_files`, or read from the old blob file before passing the actual blob value to the user's filter.

`HandleValueChange()` rewrites a user-modified value into a new blob file and replaces the base DB value with a new encoded blob index, returning `kChangeBlobIndex`. `OpenNewBlobFileIfNeeded()`, `ReadBlobFromOldFile()`, `WriteBlobToNewFile()`, `CloseAndRegisterNewBlobFileIfNeeded()`, and `CloseAndRegisterNewBlobFile()` encapsulate BlobDBImpl interaction for blob file creation, raw blob reads, blob log writes, output size tracking, close, and registration.

`BlobIndexCompactionFilterGC::~BlobIndexCompactionFilterGC()` logs one-pass GC stats and records GC tickers. `PrepareBlobOutput()` implements the integrated GC relocation path for compaction: decode the existing blob index, count it, keep TTL blobs and new-enough files, otherwise read the old blob, write it to a new file, encode the replacement blob index, and return `BlobDecision::kChangeValue`. `BlobIndexCompactionFilterFactory` and `BlobIndexCompactionFilterFactoryGC` build filter instances after reading current time and compaction context from `BlobDBImpl`.

## Control Flow
Base filtering starts by branching on `ValueType`. A value of `kBlobIndex` takes the internal BlobDB path; anything else is delegated to the user filter if present. For blob indexes, decode failure is conservative and keeps the value in the normal filter path. TTL expiration removes the index regardless of snapshots because the base class reports `IgnoreSnapshots() = true`. Eviction removal uses a compaction context snapshot of live blob files. If a non-TTL blob needs user filtering, the code parses the internal key to get the user key and sequence context, reads the raw blob from its file, runs the user's `FilterV2()` as a normal `kValue`, and, if changed, writes the modified value back out as a blob.

GC relocation follows a stricter path. Decode failure sets an error and returns `kCorruption`. TTL blobs are kept because this pass focuses on non-TTL stale-file cleanup. Blob files newer than or equal to `cutoff_file_number` are kept. Older blobs are copied into an output blob file, possibly rolling to a new one when `blob_file_size` is reached, and the base DB entry is updated to point at the new blob location.

## State and Persistence Behavior
The filter holds mutable `blob_file_` and `writer_` because RocksDB invokes the filter through logically const methods. New blob files remain unregistered until closed under `BlobDBImpl::mutex_`; this delays visibility until the file is immutable. `WriteBlobToNewFile()` updates the `BlobFile` record count/size and increments `BlobDBImpl::total_blob_size_`. Destructors are important persistence boundaries: any open output blob file is closed and registered even if the file never reached the target size.

The base filter accumulates expired/evicted counts and sizes, while the GC subclass accumulates all/relocated blob counts, relocated bytes, new-file count, and error state in `BlobDBGarbageCollectionStats`.

## Dependencies and Integration Points
The implementation depends on `BlobDBImpl` internals (`CreateBlobFileAndWriter`, `GetRawBlobFromFile`, `CloseBlobFile`, `RegisterBlobFile`, options, mutex, total size), `BlobFile`, `BlobLogWriter`, `BlobLogRecord`, `BlobIndex`, `ParsedInternalKey`, RocksDB compaction filter APIs, statistics tickers, `SystemClock`, logging, and `SyncPoint` test hooks.

## Risks and Edge Cases
Decode behavior differs by path: regular filtering keeps undecodable blob indexes, while GC reports corruption. User filter integration requires parsing an internal key; parse failure asserts and keeps the value. The comments note that compaction-filter instances are not called from multiple threads, so mutable counters are non-atomic. Output blob files can become numerous because each compaction can create its own files, though bounded by compaction count and configured blob size. Error handling is largely boolean and mapped to compaction decisions, so logging and ticker stats are important for diagnosis.

## Test Signals
Direct test hooks include `TEST_SYNC_POINT("BlobIndexCompactionFilterBase::WriteBlobToNewFile")`. Expected signals include blob DB ticker counters for expired/evicted indexes and GC relocation/new-file/failure counts, info/error logs during open/read/write/close failures, and compaction output decisions (`kRemove`, `kKeep`, `kChangeBlobIndex`, `kIOError`, `kChangeValue`, `kCorruption`).
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.h -->
# sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.h

## Purpose
This header declares the BlobDB compaction-filter stack used to interpret blob-index values during RocksDB compaction. It provides non-GC and GC variants plus factories that wrap any user-defined compaction filter while preserving BlobDB's internal cleanup rules.

## Important APIs and Types
`BlobCompactionContext` is the per-compaction snapshot provided by `BlobDBImpl`; it carries the owning implementation pointer, `next_file_number`, and the set of currently live blob files. `BlobCompactionContextGC` carries a `cutoff_file_number` used by garbage collection to decide which non-TTL blobs are old enough to relocate.

`BlobIndexCompactionFilterBase` derives from `LayeredCompactionFilterBase`. It overrides `IgnoreSnapshots()` to return true, `FilterV2()` to handle `kBlobIndex` entries, and `IsStackedBlobDbInternalCompactionFilter()` to identify itself as BlobDB's internal stacked filter. Protected helpers open output blob files, read old blobs, write relocated/changed blobs, and close/register output files. It stores BlobDB context, the compaction-time clock value, optional statistics, mutable output file/writer handles, and counters for expired/evicted blob indexes.

`BlobIndexCompactionFilter` is the non-GC concrete filter. `BlobIndexCompactionFilterGC` adds `BlobCompactionContextGC`, a mutable `BlobDBGarbageCollectionStats`, a destructor that reports GC stats, an override of `PrepareBlobOutput()`, and an output-file open override that counts created files.

`BlobIndexCompactionFilterFactoryBase` stores `BlobDBImpl`, `SystemClock`, `Statistics`, direct user compaction filter, and user compaction filter factory from `ColumnFamilyOptions`. `BlobIndexCompactionFilterFactory` and `BlobIndexCompactionFilterFactoryGC` create the corresponding filter types.

## Control Flow Contract
The factories are called by RocksDB during compaction setup. They obtain current time from `SystemClock`, ask `BlobDBImpl` for compaction context, optionally construct a per-compaction user filter from the user's factory, and return a BlobDB internal filter that layers user behavior under BlobDB's expiration/eviction/relocation rules.

## State and Persistence Behavior
The header makes clear that compaction filters manage persistent blob-file side effects in addition to returning filter decisions. Output file and writer members are mutable because compaction callback methods are const. The comment on counters states the instance is factory-created and not called from multiple threads, so counter updates are intentionally not atomic.

## Dependencies and Integration Points
The declarations depend on internal blob index encoding, `BlobDBImpl`, `BlobDBGarbageCollectionStats`, `LayeredCompactionFilterBase`, RocksDB compaction filter interfaces, statistics, and `SystemClock`. The API is not a public BlobDB user surface; it is a bridge between BlobDB's internal file lifecycle and RocksDB's compaction machinery.

## Risks and Test Signals
The main risks are lifetime and ownership of user filters, const-but-mutating file handles, non-atomic counters, and ensuring user compaction filters see real blob values while RocksDB persists blob indexes. Test and runtime signals come from concrete `Name()` strings, statistics tickers in the implementation, and the filter's special `IsStackedBlobDbInternalCompactionFilter()` marker.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db.cc -->
# sources/storage-engines/rocksdb/utilities/blob_db/blob_db.cc

## Purpose
This file implements the public `BlobDB` opening helpers and option logging. It is the narrow factory layer that validates BlobDB's column-family restrictions, constructs `BlobDBImpl`, delegates initialization, and cleans up partially opened state on failure.

## Important APIs and Functions
`BlobDB::Open(const Options&, const BlobDBOptions&, const std::string&, BlobDB**)` adapts the single-`Options` convenience API into `DBOptions` plus one default `ColumnFamilyDescriptor`. On success it deletes the returned default column-family handle because `DBImpl` retains a reference to the default column family.

`BlobDB::Open(const DBOptions&, const BlobDBOptions&, const std::string&, const std::vector<ColumnFamilyDescriptor>&, std::vector<ColumnFamilyHandle*>*, BlobDB**)` is the main open path. It rejects any configuration that does not contain exactly one descriptor named `kDefaultColumnFamilyName`. It allocates a `BlobDBImpl`, calls `Open(handles)`, casts it to `BlobDB` on success, and on failure destroys any handles created by the implementation, clears the handle vector, deletes the implementation, and returns a null output pointer.

`BlobDB::BlobDB()` initializes `StackableDB` with a null wrapped DB pointer; the concrete implementation later owns the actual base DB. `BlobDBOptions::Dump()` logs all BlobDB-specific options with `ROCKS_LOG_HEADER`.

## Control Flow
Open always sets `*blob_db` to null before work begins. The convenience overload builds the default CF descriptor, delegates to the full overload, and performs default-handle cleanup only after successful open. The full overload performs validation before allocation; all post-allocation failures go through explicit cleanup to avoid leaking handles or the implementation object.

## State and Persistence Behavior
This file does not directly persist data. Its state behavior is ownership-oriented: `BlobDBImpl` is either handed to the caller as a `BlobDB*` or fully destroyed. Option dumping records effective settings for debugging, including max DB size, TTL bucket range, blob file size, GC enablement, and background-task disabling.

## Dependencies and Integration Points
The file depends on public `BlobDB` declarations, logging utilities, and `utilities/blob_db/blob_db_impl.h`. It integrates public RocksDB options and column-family descriptors with the internal `BlobDBImpl` constructor/open contract.

## Risks and Test Signals
The key behavioral restriction is no non-default column-family support. Callers passing multiple CFs or a renamed default receive `Status::NotSupported`. The most important failure-path signal is that `handles` is cleared and `*blob_db` remains null after open failure. Option dump output is the main runtime observability in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db.h -->
# sources/storage-engines/rocksdb/utilities/blob_db/blob_db.h

## Purpose
This header declares the public BlobDB API, a `StackableDB` wrapper that stores large values in separate blob log files while storing blob indexes in the underlying RocksDB instance. It also defines BlobDB-specific constants and options.

## Important APIs and Types
Constants include `kNoExpiration` for non-TTL blobs, `kBlobDirName` for the blob directory under the base DB, and `kBytesPerSync` for incremental OS sync behavior. `BlobDBOptions` configures `max_db_size`, `ttl_range_secs`, target `blob_file_size`, `enable_garbage_collection`, `disable_background_tasks`, and supports `Dump(Logger*)`.

`BlobDB` extends `StackableDB` and restricts support to the default column family. It declares pure virtual core operations implemented by `BlobDBImpl`: default-CF `Put`, `PutWithTTL`, `Get` returning a `PinnableSlice` and optional timestamp, `Get` returning expiration, `Write`, `NewIterator`, `CompactFiles`, and `Close`. Column-family overloads check the handle ID against `DefaultColumnFamily()` and return `NotSupported` or null for non-default handles.

The class exposes two static `Open()` overloads: one for simple `Options`, and one for `DBOptions` plus a vector of column-family descriptors/handles. `DestroyBlobDB()` is declared to destroy both base DB and BlobDB content using `BlobDBOptions`.

## Control Flow Contract
Users open BlobDB through the static factory and then use it like a RocksDB wrapper with additional TTL-aware operations. Writes place values in blob files and indexes in the base DB; reads resolve indexes back to blob values. Unsupported operations such as `SingleDelete` and `Merge` return `NotSupported` because BlobDB cannot safely express their semantics against external blob storage.

## State and Persistence Behavior
The header documents the persistence model: blobs live under `blob_dir` while the base DB stores locations. TTL range controls bucketing of blob files by expiration window, and `blob_file_size` controls when a file becomes immutable. Garbage collection, when enabled, rewrites live blobs from stale non-TTL files during compaction. `Close()` is pure virtual, signaling that implementations must explicitly flush/close both base DB and blob state.

## Dependencies and Integration Points
This is a public utility header depending on `rocksdb/db.h`, `rocksdb/status.h`, and `StackableDB`. It integrates with standard RocksDB write/read/iterator/compaction APIs while intentionally narrowing column-family and operation support.

## Risks and Test Signals
The main API risks are accidental use with non-default column families, unsupported merge/single-delete expectations, TTL expiration semantics, and the split persistence boundary between base DB and blob files. Tests should check status returns for unsupported CFs/operations, TTL reads with expiration output, iterator behavior over blob-backed values, compaction/GC side effects, and `DestroyBlobDB()` cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_gc_stats.h -->
# sources/storage-engines/rocksdb/utilities/blob_db/blob_db_gc_stats.h

## Purpose
This header defines `BlobDBGarbageCollectionStats`, a compact per-GC-pass accumulator used by BlobDB compaction-time garbage collection to report how much blob data was encountered, relocated, and whether the pass hit an error.

## Important APIs and Types
The class exposes read accessors `AllBlobs()`, `AllBytes()`, `RelocatedBlobs()`, `RelocatedBytes()`, `NewFiles()`, and `HasError()`. Mutators are intentionally small and monotonic: `AddBlob(size)` increments total encountered blob count and bytes, `AddRelocatedBlob(size)` increments relocated count and bytes, `AddNewFile()` increments created output files, and `SetError()` marks the pass as failed.

## Control Flow and State
Instances start at zero counts with `error_ = false`. During a GC compaction pass, the compaction filter calls `AddBlob()` after decoding each blob index, `AddNewFile()` when it opens a new output blob file, `AddRelocatedBlob()` after a successful relocation, and `SetError()` when decode/read/write/close fails. The object does not reset itself; it is intended to have one instance per filter/pass.

## Persistence and Dependencies
The class has no direct persistence behavior and depends only on `<cstdint>` plus the RocksDB namespace header. Its values become observable when `BlobIndexCompactionFilterGC` logs them and records statistics tickers in its destructor.

## Risks and Test Signals
The class is not synchronized, matching the compaction-filter assumption that one filter instance is not invoked concurrently. Its counters can reveal partial progress when `HasError()` is true, so tests should check both relocation counts and failure flag. Since all methods are inline, misuse risk is mostly semantic: callers must pass blob payload sizes consistently and call `AddRelocatedBlob()` only after successful durable write/update steps.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_gc_stats.h -->
