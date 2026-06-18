# subset-b-008710 research

Grouped research for RocksDB utility files. Each section preserves the original source path and is intended to be split into the source-tree-aligned per-file report named by the work item.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl.cc -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl.cc`

Purpose: implements the legacy `blob_db::BlobDBImpl` stackable DB wrapper. It stores user values in append-only blob log files under `blob_dir`, stores blob indexes in the base RocksDB instance, and coordinates TTL expiration, optional non-TTL garbage collection, snapshots, file deletion, and blob-aware reads/iterators.

Important APIs and functions: `Open()` creates the blob directory, scans existing `.blob` files, installs either `BlobDBListener` plus `BlobIndexCompactionFilterFactory` or their GC variants, opens the base DB, validates that `blob_dir` is not a base CF path, initializes blob-file-to-SST mapping for GC, cleans trash through `DeleteScheduler`, and starts timer tasks. `Put()`, `PutWithTTL()`, and `Write()` build a temporary `WriteBatch` containing blob indexes via `PutBlobValue()`. `MultiGet()`, `Get()`, `GetImpl()`, `GetBlobValue()`, and `GetRawBlobFromFile()` turn base DB blob indexes back into values. `CompactFiles()` forwards compaction to the base DB and processes compaction metadata when GC is enabled. `CloseBlobFile()`, `EvictExpiredFiles()`, `DeleteObsoleteFiles()`, and `MarkUnreferencedBlobFilesObsolete()` drive lifecycle transitions. Debug-only `TEST_*` helpers expose file state for tests.

Control flow: writes serialize on `write_mutex_`, construct a blob record header, enforce `max_db_size`, choose a non-TTL or TTL-range blob file, append to its `BlobLogWriter`, update file and global size counters, possibly close oversized files, and insert a `BlobIndex` into the base DB batch. The code intentionally releases `write_mutex_` before `db_->Write()` because flush-begin listeners may need that mutex to sync blob files. Reads validate `ReadOptions::io_activity`, create a snapshot when the caller did not provide one, fetch the base value with `DBImpl::GetImpl(... is_blob_index ...)`, then either return the inline value or decode and fetch the blob from its file. Blob-file reads validate the blob offset, open/cache a random access reader, read checksum plus key plus value, verify crc32c, and pin the returned value.

State and persistence: durable state is split between blob files and the base LSM blob indexes. `blob_files_` tracks all known live/obsolete file objects by file number, `open_non_ttl_file_` tracks the mutable non-TTL file, `open_ttl_files_` is ordered by expiration range, `live_imm_non_ttl_blob_files_` is the GC candidate set, and `obsolete_files_` is pending physical deletion. `next_file_number_`, `total_blob_size_`, `live_sst_size_`, open reader count, flush sequence, and deletion disable count are in-memory coordination state. Open recovers metadata from blob file headers/footers; corrupt/incomplete files are made obsolete rather than registered as live. Directory fsyncs are used after blob sync and delete operations.

Dependencies and integration: this file integrates with `DBImpl`, `WriteBatchInternal::PutBlobIndex`, `BlobIndex`, `BlobLogWriter`, `BlobFile`, `BlobDBIterator`, `BlobDBListener`, compaction-filter wrappers, `TimerQueue`, `DeleteScheduler`, `SstFileManagerImpl`, RocksDB statistics/histograms, sync points, and filesystem abstractions. GC relies on `FlushJobInfo::oldest_blob_file_number`, `CompactionJobInfo` input/output file metadata, and snapshots from `DBImpl`.

Risks: the implementation has multiple lock domains (`write_mutex_`, `mutex_`, per-file mutexes, `delete_file_mutex_`, and DBImpl mutex). Wrong lock ordering can deadlock, especially around flush listeners and deletion. Blob index and blob file updates are not a single atomic write; failures after appending but before base DB write can leave unreferenced blob data. Snapshot protection is conservative and can delay deletion. TTL grouping depends on coarse `ttl_range_secs`; a file is evicted only after the whole range expires. `GetRawBlobFromFile()` trusts blob index sizes enough to allocate/read that range and returns corruption for short reads or CRC mismatch. `BlobFile` destructor has a fallback direct delete for obsolete files, so ownership/deletion paths must stay clear.

Test signals: `blob_db_test.cc` exercises normal puts, TTL puts, stackable DB gets, expiration retrieval, I/O errors, batches, deletes, overrides, concurrent writers, SstFileManager trash scheduling, restart cleanup, snapshot-protected GC deletion, non-default-column-family rejection, live-file metadata, migration from plain RocksDB, max DB size failures, user compaction filters, compaction-filter I/O failures, expired blob index filtering, missing blob files, full GC relocation/failure stats, TTL eviction, deletion disable nesting, mapping maintenance, shutdown races, and sync-before-close behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl.h -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl.h`

Purpose: declares `BlobDBImpl`, its comparators, state fields, public DB API overrides, private blob-file lifecycle helpers, GC mapping helpers, and test-only inspection hooks. The header is the contract between the BlobDB wrapper, blob files, iterators, event listeners, and compaction filters.

Important APIs and types: `BlobFileComparatorTTL` orders TTL files by lower expiration bound and file number; `BlobFileComparator` orders by descending file number. `BlobDBImpl` overrides `Put`, `PutWithTTL`, `Write`, `Get`, `MultiGet`, `NewIterator`, `CompactFiles`, `Close`, live-file APIs, and file deletion toggles. Public `Open()` initializes the wrapped base DB. `GetCompactionContext()` variants provide compaction filters with the current file set and, under GC, the cutoff file number. `TEST_*` methods expose blob value decoding, dummy file injection, file lists, live SST size, flush/compaction processing, and forced eviction/deletion.

Control flow represented by declarations: writes go through `PutBlobValue()`, `SelectBlobFile()` or `SelectBlobFileTTL()`, `AppendBlob()`, and `CloseBlobFileIfNeeded()`. Reads go through `SetSnapshotIfNeeded()`, `GetImpl()`, `GetBlobValue()`, `GetRawBlobFromFile()`, and `GetBlobFileReader()`. File lifecycle runs through `NewBlobFile()`, `RegisterBlobFile()`, `CreateWriterLocked()`, `CheckOrCreateWriterLocked()`, `CloseBlobFile()`, `ObsoleteBlobFile()`, `VisibleToActiveSnapshot()`, and the timer task callbacks. GC metadata maintenance is declared as initialization, link/unlink, flush processing, compaction processing, and mark-unreferenced flows.

State and persistence: the header makes the central invariants visible. `blob_dir_` and `dir_ent_` are filesystem roots; `blob_files_`, `open_ttl_files_`, `open_non_ttl_file_`, `live_imm_non_ttl_blob_files_`, and `obsolete_files_` are the in-memory mirror of persistent blob logs. `next_file_number_`, `flush_sequence_`, `total_blob_size_`, `live_sst_size_`, and `open_file_count_` are atomics/counters derived from writes, live file metadata, and open readers. `closed_`, `tqueue_`, and `disable_file_deletions_` coordinate shutdown and deletion.

Dependencies and integration: includes RocksDB DB, filesystem, listener, options, statistics, `TimerQueue`, `BlobDB` public wrapper API, `BlobFile`, `BlobLogWriter`, and DB iterator internals. Friends include `BlobFile`, `BlobDBIterator`, event listeners, and blob index compaction filters, signaling tight integration with the rest of `utilities/blob_db`.

Risks: many methods have lock preconditions expressed only in comments, such as holding `write_mutex_`, DB `mutex_`, and/or a blob file mutex before closing a file. Misuse by friend classes could break state consistency. The class supports only the default column family, so callers using inherited `StackableDB` surfaces need runtime errors. Several state fields are raw pointers or references owned elsewhere (`db_impl_`, `env_`, `clock_`, `statistics_`), so open/close ordering is essential.

Test signals: debug-only methods are heavily used by `blob_db_test.cc` to validate blob file lists, obsolete lists, mapping transitions, forced file closure, eviction, deletion, and direct blob-index reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl_filesnapshot.cc -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl_filesnapshot.cc`

Purpose: implements BlobDB live-file and deletion snapshot APIs used by backup, checkpoint, replication, and storage inventory paths. It extends base DB live-file output with blob files and coordinates blob-file deletion disable/enable with the base DB.

Important APIs and functions: `DisableFileDeletions()` calls `db_impl_->DisableFileDeletions()` and then increments `disable_file_deletions_` under `delete_file_mutex_`. `EnableFileDeletions()` calls the base enable path and decrements the BlobDB disable counter. `GetLiveFiles()` locks BlobDB metadata, delegates to `db_->GetLiveFiles()`, and appends blob file names relative to the DB root. `GetLiveFilesMetaData()` appends `LiveFileMetaData` for each blob file, including size, relative name, file number, TTL-derived `oldest_ancester_time`, and default CF name. `GetLiveFilesStorageInfo()` appends `LiveFileStorageInfo` entries with directory, relative filename, file type `kBlobFile`, size, and `trim_to_size`.

Control flow: all live-file enumeration begins with a read lock on `mutex_` to avoid concurrent blob file registration/deletion while the base DB and blob file lists are combined. Deletion disable is two-layered: the base DB is disabled first, then BlobDB deletion state is incremented while holding `delete_file_mutex_` so `DeleteObsoleteFiles()` cannot race through the gap.

State and persistence behavior: no new persistent data is written. The code exposes the current in-memory `blob_files_` map as file snapshots and blocks physical deletion by increasing `disable_file_deletions_`. `DeleteObsoleteFiles()` in the implementation honors that counter, so obsolete files remain listed until re-enabled and deleted.

Dependencies and integration: relies on `BlobFileName`, logging, `ColumnFamilyHandleImpl` casts, base DB live-file APIs, `LiveFileMetaData`, `LiveFileStorageInfo`, and BlobDB locking fields declared in `blob_db_impl.h`.

Risks: holding BlobDB `mutex_` around base DB live-file calls keeps snapshots consistent but can increase contention. `EnableFileDeletions()` only decrements if positive; mismatched enable/disable calls can leave deletions enabled earlier or later than intended depending on base DB state. The code assumes BlobDB supports only the default CF when filling metadata.

Test signals: `GetLiveFilesMetaData` in `blob_db_test.cc` verifies blob metadata names, file numbers, TTL ancestor time, CF names, live-file list appends, and storage-info entries. `DisableFileDeletions` verifies nested disable counts block and later permit obsolete blob file deletion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl_filesnapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_iterator.h -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_iterator.h`

Purpose: defines `BlobDBIterator`, an `Iterator` wrapper that exposes user values from a base DB iterator whose values may be blob indexes. It is the iterator read-side bridge from LSM entries to blob-file payloads.

Important APIs and functions: constructor takes an optional owned `ManagedSnapshot`, an `ArenaWrappedDBIter`, the owning `BlobDBImpl`, `SystemClock`, and statistics. Standard iterator methods delegate positioning to the base iterator and then call `UpdateBlobValue()`. `value()` returns `iter_->value()` for inline values or the cached `PinnableSlice value_` for blob entries. `status()` combines base iterator status with blob value fetch status.

Control flow: `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, and `Prev` all record statistics, move the base iterator, and loop while `UpdateBlobValue()` returns true. `UpdateBlobValue()` resets cached value/status, checks `iter_->IsBlob()`, and calls `blob_db_->GetBlobValue(iter_->key(), iter_->value(), &value_)`. If the blob lookup returns `NotFound`, usually due to TTL expiry or missing file, it tells the caller to advance again; other non-OK status stops iteration and is surfaced.

State and persistence behavior: the iterator owns or borrows a snapshot supplied by `BlobDBImpl::NewIterator()`, ensuring blob files remain protected consistently with the base iterator sequence. It does not mutate persistent state. It stores only the current blob payload and error status.

Dependencies and integration: depends on `ArenaWrappedDBIter`, `ManagedSnapshot`, BlobDB implementation internals, `StopWatch`, statistics tickers, and `PinnableSlice`. It is constructed by `BlobDBImpl::NewIterator()` with `expose_blob_index=true` so it can see and decode blob index entries.

Risks: iterator refresh is unsupported. Expired/missing blob values are silently skipped as `NotFound`, which matches TTL semantics but can hide file disappearance as an absent key during iteration. Any blob read corruption becomes iterator status and invalidates `Valid()`. The class holds raw pointers to `BlobDBImpl`, clock, and statistics; lifetime is safe only while the DB remains open.

Test signals: `BlobDBTest::VerifyDB()` validates forward iteration against expected maps across many tests. TTL tests indirectly verify expired entries are skipped rather than returned.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_listener.h -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_listener.h`

Purpose: defines event listeners that connect base DB flush/compaction events back into BlobDB state. They keep blob files durable before flush and keep size and GC mapping metadata current after flushes and compactions.

Important APIs and types: `BlobDBListener` implements `OnFlushBegin`, `OnFlushCompleted`, `OnCompactionCompleted`, `Name`, and `kClassName`. `BlobDBListenerGC` extends it and overrides completed flush/compaction callbacks to invoke GC mapping updates. Both store a raw `BlobDBImpl*`.

Control flow: on flush begin, BlobDB syncs currently open blob files with `WriteOptions(Env::IOActivity::kFlush)` before the base DB flush publishes SSTs containing blob indexes. On flush completion and compaction completion, the base listener updates the live SST size used by `max_db_size` accounting. The GC listener then processes `FlushJobInfo` or `CompactionJobInfo` to link or unlink SST file numbers from oldest blob file numbers and mark unreferenced non-TTL blob files obsolete.

State and persistence behavior: listeners do not persist directly except through `SyncBlobFiles()` on flush begin. They mutate `live_sst_size_`, `flush_sequence_`, SST link sets inside `BlobFile`, and obsolete file lists through `BlobDBImpl`.

Dependencies and integration: integrates with RocksDB `EventListener`, `FlushJobInfo`, `CompactionJobInfo`, and BlobDB implementation private methods. `BlobDBImpl::Open()` installs either this listener or the GC variant depending on `enable_garbage_collection`.

Risks: callbacks use a raw DB implementation pointer and must not outlive `BlobDBImpl`; `CloseImpl()` closes the base DB before clearing `db_impl_` to stop listener and compaction-filter calls. `OnFlushBegin()` ignores sync errors via `PermitUncheckedError()`, so a durability failure is logged inside lower layers but not propagated through the callback. Locking can race with writes if `write_mutex_` ordering changes.

Test signals: BlobDB tests exercise listener effects through GC mapping maintenance, live SST size updates, sync-before-close counters, and max-size accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_listener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_test.cc -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_test.cc`

Purpose: comprehensive unit and integration tests for legacy BlobDB behavior. The file validates basic API semantics, blob index encoding, TTL expiration, I/O failure handling, file lifecycle, snapshot protection, user compaction filters, garbage collection, live-file metadata, and unsupported surfaces.

Important APIs and helpers: `BlobDBTest` owns temporary DB paths, mock and fault-injection envs, `TryOpen`, `Open`, `Reopen`, `Close`, `Destroy`, typed access to `BlobDBImpl`, write/delete helpers, random value helpers, `VerifyDB`, `VerifyBaseDB`, `VerifyBaseDBBlobIndex`, and `InsertBlobs`. `BlobIndexVersion` describes expected base DB blob-index metadata for verification.

Control flow: individual tests open BlobDB with targeted `BlobDBOptions` and RocksDB `Options`, write values through `Put`, `PutWithTTL`, or `WriteBatch`, sometimes force blob file closure via `TEST_CloseBlobFile`, then verify both user-visible DB output and base DB internal versions. Tests use mock time to make TTL deterministic, fault-injection envs and sync points to induce I/O failures, and manual compaction/flush helpers to trigger compaction filters and GC.

State and persistence behavior: tests inspect blob file number allocation, footer closure, expiration ranges, live immutable non-TTL sets, obsolete lists, SST link sets, deletion disable counters, live-file metadata, and statistics counters. Restart tests verify trash cleanup and migration from plain RocksDB to BlobDB. Snapshot tests verify obsolete files remain physically present until snapshots that might see old blob indexes are released.

Dependencies and integration: pulls in BlobDB public API, `BlobDBImpl` debug hooks, `BlobIndex`, `DBTestUtil` helpers, `SstFileManagerImpl`, `MockSystemClock`, `FaultInjectionTestEnv`, `SyncPoint`, `Random`, and RocksDB compaction/filter APIs. It uses the base DB directly for internal verification.

Risks covered: unsupported non-default column family operations, snapshot races during GC deletion, I/O failures during get/put/compaction close/write, expired index filtering despite snapshots, missing blob-file indexes, max DB size limit returning no-space I/O status, concurrent writers, shutdown while background eviction is running, and user compaction filters modifying or dropping blob values.

Test signal summary: this is the primary regression suite for `utilities/blob_db`. It covers broad behavior but is oriented around deterministic unit setups; performance, crash-recovery windows between blob append and base DB write, and multi-CF support remain outside the intended contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_db_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.cc -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.cc`

Purpose: implements `BlobDumpTool`, a command-style reader for RocksDB blob log files. It prints blob log header/footer metadata, optionally prints records in raw/hex/detail form, can decompress values for display/summary, and produces aggregate record/key/value sizes.

Important APIs and functions: `Run()` opens a file with default filesystem APIs, wraps it in a 2 MiB readahead random access file, reads header and footer, iterates records until the footer offset, and prints summary counters. `Read()` manages a reusable buffer and enforces exact-size reads. `DumpBlobLogHeader()` decodes `BlobLogHeader` and prints version, column family, compression, and expiration range. `DumpBlobLogFooter()` decodes `BlobLogFooter` when present and otherwise treats the file as lacking a footer. `DumpRecord()` decodes record headers, reads key/value payloads, optionally decompresses, prints selected fields, and advances offsets. `DumpSlice()` formats bytes.

Control flow: file scanning starts at offset zero. Header size establishes the first record offset, footer detection establishes the stopping offset, and each record advances by `BlobLogRecord::kHeaderSize + key_size + value_size`. Decompression is conditional on file-level compression and requested uncompressed output or summary. The function stops and returns an error if a record read, decode, unsupported compression, or decompression fails.

State and persistence behavior: this file is read-only. The only mutable state is the tool's `reader_`, buffer allocation, and buffer size. It relies on persisted blob log wire format from `db/blob/blob_log_format.h`.

Dependencies and integration: uses `FileSystem::Default`, `RandomAccessFileReader`, `NewReadaheadRandomAccessFile`, blob log format structs, compression manager, table format constants, and `Slice` string/hex conversion. It is paired with `blob_dump_tool.h`.

Risks: `DumpSlice(kRaw)` prints arbitrary bytes as a string, which can be unsafe for terminals or binary data. The detail formatter is manual and easy to regress. Summary of uncompressed bytes requires successful decompression and may fail on unknown compression. The tool treats malformed footer as absent, which is useful for open/incomplete files but can hide footer corruption during diagnostics.

Test signals: no direct test file in this work item, but blob file format is indirectly exercised by BlobDB tests and `BlobFile::ReadMetadata`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.h -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.h`

Purpose: declares the blob log dump utility interface and display modes. It is a small diagnostic API for inspecting persisted `.blob` files outside the normal DB read path.

Important APIs and types: `BlobDumpTool::DisplayType` supports `kNone`, `kRaw`, `kHex`, and `kDetail`. `Run()` is the public entry point taking a filename, key/blob/uncompressed display choices, and summary flag. Private helpers read exact byte ranges, dump header/footer/records, format slices, and format numeric ranges.

Control flow represented by declarations: `Run()` owns the high-level scan; `DumpBlobLogHeader()` and `DumpBlobLogFooter()` bracket record iteration; `DumpRecord()` consumes one record and updates aggregate counters; `Read()` hides buffer management for random reads.

State and persistence behavior: `reader_`, `buffer_`, and `buffer_size_` are transient. The utility does not write or repair files. It depends on blob log header/footer and record layout for interpretation.

Dependencies and integration: includes blob log format, `RandomAccessFileReader`, `Slice`, and `Status`. It is under `blob_db` namespace and is implemented entirely in `blob_dump_tool.cc`.

Risks: the public API prints to stdout rather than returning structured data, so callers cannot easily consume parsed output. There is no explicit configuration for filesystem, file options, or output stream. Display type choices apply independently to key, blob, and uncompressed blob and need to be kept consistent with implementation behavior.

Test signals: coverage is indirect through format readers; no dedicated tests are present in the listed files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_file.cc -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_file.cc`

Purpose: implements `BlobFile`, the in-memory handle for one persisted BlobDB log file. It owns metadata, optional append writer, cached random access reader, footer/header parsing, immutability/obsolete transitions, and file-state diagnostics.

Important APIs and functions: constructors initialize existing-file or new-file metadata. `PathName()` derives the absolute blob filename. `DumpState()` emits a debug summary. `MarkObsolete()` stores obsolete sequence. `WriteFooterAndCloseLocked()` appends `BlobLogFooter`, marks the file immutable, updates file size, and drops the writer. `ReadFooter()` reads and decodes the footer using the cached reader. `Fsync()` syncs the writer if present. `CloseRandomAccessLocked()` drops the cached reader. `GetReader()` lazily opens and caches a `RandomAccessFileReader`. `ReadMetadata()` reads file size, header, and optional footer from persistent storage.

Control flow: new mutable files are created by `BlobDBImpl`, then writers append records. On close, the footer captures blob count and TTL expiration range, then the writer is reset. On reads, `GetReader()` first tries a read lock for an existing reader, then upgrades to a write lock to open one exactly once. On DB open, `ReadMetadata()` validates the header, marks header state, then decodes a footer if the file is large enough and the footer is valid; absent/malformed footer is tolerated as an open/incomplete file state.

State and persistence behavior: persistent fields are represented by blob file path/number, header column family id, compression, TTL flag/range, record count, file size, and footer fields. In-memory-only fields include linked SST file set, writer, reader, closed flag, immutable/obsolete sequence numbers, access timestamp, and validity flags. `BlobRecordAdded()` increments count and file size after physical record append.

Dependencies and integration: uses blob log format/writer, `BlobFileName`, `RandomAccessFileReader`, file system APIs, readahead support, logging, DB format sequence numbers, and `BlobDBImpl` for friendship and file options.

Risks: destructor attempts to delete obsolete files through `Env::Default()` as a fallback, which can differ from the DB env. Header corruption during open is fatal/corrupt; footer corruption is tolerated, so later logic must handle missing footer counts. Reader caching affects open file count in `BlobDBImpl`; stale counts can arise if readers are closed outside expected paths. Per-file methods rely on external locking comments rather than internal enforcement for several transitions.

Test signals: BlobDB tests inspect file number, TTL flag/range, size, immutability, obsolete state, linked SSTs, reader lifecycle indirectly, footer sync counters, and metadata across reopen/trash scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_file.h -->
## `sources/storage-engines/rocksdb/utilities/blob_db/blob_file.h`

Purpose: declares `BlobFile`, the central metadata and I/O handle for BlobDB log files. It captures persistent blob-log identity and transient access state while exposing controlled lifecycle methods to `BlobDBImpl` and compaction filters.

Important APIs and types: public methods include constructors, destructor, `PathName`, `BlobFileNumber`, SST link/unlink accessors, `BlobCount`, `DumpState`, `Immutable`, `MarkImmutable`, immutable/obsolete sequence accessors, `MarkObsolete`, `Fsync`, `GetFileSize`, expiration accessors, TTL flag accessors, writer getter, `ReadMetadata`, and `GetReader`. Private methods include `ReadFooter`, `WriteFooterAndCloseLocked`, `CloseRandomAccessLocked`, `SetFromFooterLocked`, setters, and `BlobRecordAdded`.

Control flow represented by declarations: `BlobDBImpl` creates a new file with header metadata, appends records through a writer, closes it by footer append, and later opens random readers for reads. GC and TTL eviction mark immutable files obsolete; deletion waits until no active snapshots can see them. SST link sets are maintained when GC is enabled to know whether old non-TTL files can be obsoleted.

State and persistence behavior: fields include immutable identity (`path_to_dir_`, `file_number_`), persistent/log-derived metadata (`column_family_id_`, `has_ttl_`, `expiration_range_`, `blob_count_`, `file_size_`, `header_`), lifecycle state (`closed_`, `immutable_sequence_`, `obsolete_`, `obsolete_sequence_`), and transient resources (`log_writer_`, `ra_file_reader_`, `last_access_`). Header/footer validity flags track recovery quality.

Dependencies and integration: includes blob log format/writer, random access file reader, RocksDB env/file system/options, port mutexes, and friendship with `BlobDBImpl`, comparators, and blob-index compaction filters.

Risks: the class exposes several atomic getters without locks but other fields require caller-held locks; this mixed model can be misused. `linked_sst_files_` is not internally synchronized. Obsolete implies immutable by assertion, so any path that marks a mutable file obsolete must close it first. TTL range extension mutates a pair directly and requires a file lock externally.

Test signals: file state is directly checked throughout `blob_db_test.cc`, especially GC mapping, TTL eviction, deletion disable, and live metadata tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/blob_db/blob_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cache_dump_load.cc -->
## `sources/storage-engines/rocksdb/utilities/cache_dump_load.cc`

Purpose: provides public factory functions for default cache dump/load components. It bridges the `rocksdb/utilities/cache_dump_load.h` API to concrete file-backed readers/writers and default dumper/loader implementations.

Important APIs and functions: `NewToFileCacheDumpWriter()` creates a `WritableFileWriter` for a named file and wraps it in `ToFileCacheDumpWriter`. `NewFromFileCacheDumpReader()` creates a `RandomAccessFileReader` and wraps it in `FromFileCacheDumpReader`. `NewDefaultCacheDumper()` allocates `CacheDumperImpl`. `NewDefaultCacheDumpedLoader()` allocates `CacheDumpedLoaderImpl`.

Control flow: each factory constructs the lower-level file reader/writer first and returns early on I/O status failure. Ownership is moved into the concrete wrapper through `std::unique_ptr`. The dumper/loader factories are status-only constructors and do not perform dump/load work themselves.

State and persistence behavior: the writer factory creates/opens a dump target file; the reader factory opens an existing dump file. No cache entries are serialized here; persistence format is implemented by `cache_dump_load_impl.*`.

Dependencies and integration: depends on RocksDB public cache dump/load declarations, `WritableFileWriter`, `RandomAccessFileReader`, env/file system/file options, table options, and the implementation header. These functions are likely the public extension points used by tools or DB warmup paths.

Risks: factories do not validate null output pointer arguments. They pass `nullptr` tracing/rate-limiter contexts to file reader/writer creation. `NewDefaultCacheDumpedLoader()` accepts `BlockBasedTableOptions` but the current implementation ignores it, which can surprise callers expecting table-option-specific behavior.

Test signals: no listed direct tests; behavior would be covered by cache dump/load tests elsewhere if present.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cache_dump_load.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.cc -->
## `sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.cc`

Purpose: implements block-cache dump and restore. The dumper iterates cache entries, serializes supported block roles to a writer with metadata and checksums, optionally filters entries by DB/table stable cache-key prefixes, and the loader reads the stream back into a secondary cache.

Important APIs and functions: `CacheDumperImpl::SetDumpFilter()` builds a set of stable `OffsetableCacheKey` common prefixes from table properties across DBs. `DumpCacheEntriesToWriter()` validates inputs, initializes clock/deadline/sequence, writes header, applies a callback to all cache entries, writes footer, and closes the writer. `DumpOneBlockCallBack()` filters unsupported helpers/roles, max size, deadline, and DB prefix; serializes cache values through helper callbacks; and calls `WriteBlock()`. `WriteBlock()` builds `DumpUnit`, encodes it, computes checksums, writes metadata then packet. Loader methods `RestoreCacheEntriesToSecondaryCache()`, `ReadHeader()`, `ReadCacheBlock()`, `ReadDumpUnitMeta()`, and `ReadDumpUnit()` validate stream order and checksums before `secondary_cache_->InsertSaved()`.

Control flow: dump format is header unit, zero or more block units, footer unit. Each unit is preceded by a fixed-size encoded `DumpUnitMeta` containing sequence number, dump-unit checksum, and serialized unit size. The writer abstraction receives size-prefixed metadata and packet strings. Restore reads header first, loops until footer, and stops on read error or footer. Only data, filter, filter-meta, and index block roles are currently dumped.

State and persistence behavior: persisted state is a sequential cache dump file containing encoded `DumpUnitMeta` and `DumpUnit` pairs. `sequence_num_` is monotonic in dump order. `dumped_size_bytes_` tracks approximate emitted value bytes for `max_size_bytes`, while `deadline_` limits dumping by timestamp. The loader does not reconstruct primary cache state directly; it inserts saved blocks into a `SecondaryCache`.

Dependencies and integration: uses cache helper callbacks and roles, `OffsetableCacheKey`, table properties, `BlockBasedTable::SetupBaseCacheKey`, RocksDB trace/version constants, crc32c, block-based table types, and secondary cache APIs. It relies on `CacheDumpWriter`/`CacheDumpReader` implementations declared in the header.

Risks: callback write errors are ignored with `PermitUncheckedError()`, so `DumpCacheEntriesToWriter()` can still write a footer after failed block writes unless the writer stores an error internally. `max_size_bytes` check uses `>` before adding current block, so it can exceed the limit by one block. Header version is not validated by loader yet. `DecodeDumpUnit()` stores `value` as a pointer into the backing string supplied by the caller, so that string must outlive `InsertSaved()` consumption. Filtering only dumps stable cache keys; non-stable entries are intentionally skipped when DB filters are set.

Test signals: no direct listed tests. Useful future tests would corrupt metadata checksums, packet sizes, unsupported roles, deadline/max-size boundaries, and secondary cache insertion failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.h -->
## `sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.h`

Purpose: declares the concrete cache dump/load format, default dumper/loader classes, file-backed reader/writer classes, and helper encode/decode routines.

Important APIs and types: `CacheDumpUnitType` enumerates header, footer, data, filter, properties, compression dictionary, range deletion, hash index, meta/index, deprecated filter, filter metadata, and max marker values. `DumpUnitMeta` holds sequence number, checksum, and serialized unit size. `DumpUnit` holds timestamp, type, cache key, value length/checksum, and value pointer. `CacheDumperImpl` and `CacheDumpedLoaderImpl` implement public interfaces. `ToFileCacheDumpWriter` and `FromFileCacheDumpReader` implement size-prefixed stream I/O. `CacheDumperHelper` encodes and decodes metadata and units.

Control flow represented by declarations: dumpers call `WriteHeader()`, `DumpOneBlockCallBack()`, `WriteBlock()`, and `WriteFooter()`. Loaders call `ReadHeader()`, then repeated `ReadCacheBlock()`. File writer methods write a 4-byte size prefix before metadata or packet data; file reader methods maintain a running offset and read in 1 KiB chunks.

State and persistence behavior: the on-disk stream is a sequence of length-prefixed metadata and packet records. Metadata encoding is fixed 16 bytes. Dump unit encoding stores timestamp, one-byte type, length-prefixed key, fixed value length/checksum, and length-prefixed value bytes. Reader state is `offset_`, reusable buffer, and last `Slice` result.

Dependencies and integration: includes file readers/writers, public cache dump/load API, block-based table blocks/readers, filter blocks, cache key utilities, and hash containers.

Risks: `DumpUnit::value` is a raw pointer and changes ownership semantics between dumping and loading. `FromFileCacheDumpReader::Read()` appends into the destination string without clearing it, so callers must clear strings before reuse; current loader does. The reader casts requested length to `unsigned int`, which is a boundary risk for very large packets. `DecodeDumpUnit()` indexes `encoded_slice[0]` without first checking non-empty after timestamp decode.

Test signals: no direct tests in this subset; the encode/decode helpers and file reader/writer are key candidates for corruption and boundary tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.cc -->
## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.cc`

Purpose: implements Cassandra row-value compaction filtering and object-library registration for Cassandra merge/filter components. The filter removes or rewrites expired columns and tombstones during RocksDB compaction.

Important APIs and functions: `cassandra_filter_type_info` describes configurable options for RocksDB's options registry. `CassandraCompactionFilter` constructor stores options and registers them for introspection. `FilterV2()` deserializes `RowValue`, either removes expired columns or converts them to tombstones depending on `purge_ttl_on_expiration`, removes collectable tombstones when the input is a normal `kValue`, and returns remove/change/keep decisions. `CassandraCompactionFilterFactory` creates filters with stored options. `RegisterCassandraObjects()` registers factories for `CassandraValueMergeOperator`, `CassandraCompactionFilter`, and `CassandraCompactionFilterFactory`.

Control flow: `FilterV2()` always deserializes the existing value into a Cassandra `RowValue`. It first handles TTL expiry according to policy, then applies tombstone GC only for compacted full values, not merge operands. Empty compacted rows are removed. Non-empty changed rows are serialized into `new_value`; unchanged rows are kept.

State and persistence behavior: persistent RocksDB values are rewritten from serialized Cassandra row format to either a changed row format or removed. The filter's only state is `CassandraOptions`, including GC grace period and TTL purge policy.

Dependencies and integration: depends on RocksDB compaction filter APIs, object registry/options type reflection, Cassandra `format.h`, and Cassandra merge operator registration. It is loaded dynamically in tests through `ConfigOptions.registry->AddLibrary()`.

Risks: deserialization assumes all values reaching the filter are valid Cassandra row values. Enabling `purge_ttl_on_expiration` is explicitly dangerous unless all writes share the same TTL behavior because purging expired columns can allow older values to reappear. `FilterV2()` ignores `skip_until` and level/key. Default registered factory instances use zeroed options unless overridden by string configuration.

Test signals: `cassandra_functional_test.cc` verifies compaction conversion to tombstones, purging expired columns, row removal when all columns expire, tombstone GC after grace period, tombstone removal from put values, and registry loading/configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.h -->
## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.h`

Purpose: declares Cassandra compaction filter and factory types. It documents TTL/tombstone compaction policy and exposes names used by RocksDB object creation.

Important APIs and types: `CassandraCompactionFilter` extends `CompactionFilter`, provides constructor parameters `purge_ttl_on_expiration` and `gc_grace_period_in_seconds`, `kClassName()`, `Name()`, and `FilterV2()`. `CassandraCompactionFilterFactory` extends `CompactionFilterFactory`, stores the same options, implements `CreateCompactionFilter()`, and exposes class name metadata.

Control flow represented by declarations: RocksDB calls the factory per compaction context to obtain a filter. The filter uses `FilterV2()` to decide keep, remove, or change-value for each Cassandra row value.

State and persistence behavior: both classes embed `CassandraOptions`. The filter can rewrite serialized row values or remove keys during compaction; the factory itself is configuration state only.

Dependencies and integration: includes RocksDB compaction filter and slice APIs plus `cassandra_options.h`. Its class names are used by object registry tests and configuration strings.

Risks: comments repeat the important correctness condition that direct TTL purging should be used only when writes have the same TTL setting. The API does not enforce that condition. The filter is designed for Cassandra-formatted values only; applying it to arbitrary values would corrupt or fail compaction behavior.

Test signals: functional tests load the filter and factory by name and verify configured option values through `GetOptions<CassandraOptions>()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_format_test.cc -->
## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_format_test.cc`

Purpose: unit tests Cassandra row serialization and local compaction helpers. It validates binary layout for columns, expiring columns, tombstones, row tombstones, rows with columns, TTL purging, and TTL-to-tombstone conversion.

Important test cases: `ColumnTest.Column` verifies mask/index/timestamp/size fields, serialization bytes, and deserialization through both `Column` and `ColumnBase`. `ExpiringColumnTest.ExpiringColumn` adds TTL serialization. `TombstoneTest.TombstoneCollectable` validates GC grace timing, and `TombstoneTest.Tombstone` validates deletion-time and marked-for-delete layout. `RowValueTest.RowTombstone` verifies row tombstone layout. `RowValueTest.RowWithColumns` validates row metadata sentinels and ordered serialized columns. TTL tests validate `RemoveExpiredColumns()` and `ConvertExpiredColumnsToTombstones()`.

Control flow: tests construct small in-memory rows using real constructors and test utilities, serialize into strings, manually deserialize primitive fields by offset, then run class deserializers and reserialize to assert byte-for-byte equality. TTL tests use `time(nullptr)`, helper constants, and verification helpers to compare resulting column types/indexes/timestamps.

State and persistence behavior: the tests define the expected persistent byte layout for Cassandra value format. Any production format change should break these tests unless migration/compatibility is added.

Dependencies and integration: uses RocksDB test harness, Cassandra `format.h`, `serialize.h`, and `test_utils.h`. The `main()` installs stack trace handling and runs GoogleTest.

Risks: several tests depend on wall-clock `time(nullptr)`, but only relative comparisons are used. The test name `PurgeTtlShouldRemvoeAllColumnsExpired` has a typo but still compiles. Coverage focuses on happy-path deserialization and does not test malformed byte strings or overflow/truncation behavior.

Test signals: this file is itself the test signal for Cassandra wire format and local row cleanup semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_format_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_functional_test.cc -->
## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_functional_test.cc`

Purpose: DB-level integration tests for Cassandra merge operator, compaction filter, and object-registry loading. It validates that serialized `RowValue` merge operands and put values behave correctly through real RocksDB flush, compaction, get, and dynamic option parsing paths.

Important APIs and helpers: `CassandraStore` wraps `DB` with `Append()` using `Merge`, `Put()`, `Flush()`, `Compact()`, and `Get()` returning deserialized `RowValue`. `TestCompactionFilterFactory` creates `CassandraCompactionFilter` instances from test flags. `CassandraFunctionalTest::OpenDb()` creates a fresh DB with `CassandraValueMergeOperator` and the test compaction filter factory.

Control flow: tests append serialized row mutations, optionally flush between operands to force persistent files, then compact and read results. `SimpleMergeTest` checks merge resolution without compaction. TTL compaction tests check conversion to tombstones, direct purge when enabled, complete row removal when all columns expire, tombstone GC after grace period, and tombstone removal from a put value. Registry tests first assert class-name creation fails before registering the Cassandra library, then registers `RegisterCassandraObjects` and validates default and configured objects.

State and persistence behavior: values are persisted in RocksDB as Cassandra row serialization. Merge operands are combined by `CassandraValueMergeOperator`; compaction rewrites or removes rows through `CassandraCompactionFilter`. Tests use a per-thread DB path and destroy it before each test.

Dependencies and integration: uses `DBImpl` test flush/compact helpers, RocksDB DB/options, merge operator APIs, object registry, utility merge operators include, Cassandra compaction filter/merge operator/test utilities, and stack trace test harness.

Risks: time-dependent TTL tests use current time and a generous `kTestTimeoutSecs` to avoid expiry during test execution. The helper prints errors to `stderr` and returns booleans rather than asserting inside wrappers. These tests do not cover malformed Cassandra values or concurrent merges.

Test signals: strong integration coverage for the Cassandra plugin path, especially options string parsing and compaction effects after flush/compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_functional_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_options.h -->
## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_options.h`

Purpose: defines shared Cassandra configuration used by the merge operator, compaction filter, and object registry. It is the options payload exposed through RocksDB configurable-object infrastructure.

Important APIs and types: `CassandraOptions` has `kName()`, constructor, `operands_limit`, `gc_grace_period_in_seconds`, and `purge_ttl_on_expiration`. The header also declares C-linkage `RegisterCassandraObjects(ObjectLibrary&, const std::string&)`.

Control flow represented by declarations: producers construct `CassandraOptions` with merge operand limits, tombstone GC grace period, and TTL purge policy. `RegisterCassandraObjects` is called by RocksDB object-library loading to register Cassandra merge/filter classes.

State and persistence behavior: the struct is runtime configuration only. It affects persistent output indirectly by limiting merge behavior and deciding whether expired columns become tombstones or are purged during compaction.

Dependencies and integration: includes RocksDB namespace support and forward declares `ObjectLibrary`. `cassandra_compaction_filter.cc` registers two of these fields for compaction filter/factory option parsing; merge operator code outside this work item uses `operands_limit`.

Risks: `purge_ttl_on_expiration` comment documents a correctness hazard: direct purge can bring old data back unless TTL settings are uniform. The constructor requires all values and provides no default constructor, so option-registration code must create valid initial values.

Test signals: `cassandra_functional_test.cc` verifies parsed options for merge operator, compaction filter, and compaction filter factory.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_row_merge_test.cc -->
## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_row_merge_test.cc`

Purpose: focused unit tests for `RowValue::Merge()`. It validates column-level timestamp conflict resolution and row tombstone handling independent of a live RocksDB instance.

Important test cases: `RowValueMergeTest.Merge` merges three row values containing normal columns, expiring columns, and tombstones at overlapping indexes, expecting the highest-timestamp mutation per column and preserving distinct indexes. `RowValueMergeTest.MergeWithRowTombstone` checks that a row tombstone suppresses older columns, allows newer columns, and wins entirely when the latest mutation is a row tombstone.

Control flow: tests build `std::vector<RowValue>` with helper-created rows, call `RowValue::Merge(std::move(row_values))`, and verify the resulting row shape and ordered columns with `VerifyRowValueColumns()`. The second test reuses the vector after move by adding new tombstone values and checking latest tombstone behavior.

State and persistence behavior: no DB persistence occurs. The tests define semantic merge output for serialized row values that the merge operator later depends on.

Dependencies and integration: uses RocksDB test harness, Cassandra `format.h`, and `test_utils.h`. It has its own GoogleTest `main()`.

Risks: coverage is compact and deterministic but does not test malformed rows, duplicate equal timestamps, or very large operand lists. The vector reuse after move is valid because the moved-from vector is reused by pushing new values, but it is a pattern worth reading carefully.

Test signals: this is the direct regression signal for row merge semantics used by Cassandra merge operator and functional DB tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_row_merge_test.cc -->
