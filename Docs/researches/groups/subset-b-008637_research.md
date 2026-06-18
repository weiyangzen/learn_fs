# Research: subset-b-008637

Grouped research for RocksDB file utilities, filename handling, line readers, random-access readers, readahead wrappers, and prefetch tests. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_util.h -->
# sources/storage-engines/rocksdb/file/file_util.h

## Purpose

`file_util.h` is a shared file-operation helper interface for RocksDB internals. It declares copy/create/delete/checksum helpers and small option-conversion utilities that bridge public `ReadOptions`/`WriteOptions` to lower-level `IOOptions`. It also exposes a test-only destructive directory cleanup helper and a filesystem feature probe.

## Important APIs, Types, and Functions

- `CopyFile(...)` has two overload families: one copies from a source path into an existing `WritableFileWriter`, and another opens/writes a destination path with destination `Temperature`. Both accept source/destination temperature hints, target size, fsync behavior, `IOTracer`, read/write `IOOptions`, and a maximum read buffer size.
- `CreateFile(...)` writes a full string to a destination file and optionally fsyncs.
- `DeleteDBFile(...)` and `DeleteUnaccountedDBFile(...)` centralize DB-file deletion while respecting `ImmutableDBOptions`, foreground/background deletion policy, directory sync paths, and optional slow-deletion trash buckets.
- `GenerateOneFileChecksum(...)` computes one file checksum using a `FileChecksumGenFactory`, requested checksum function name, readahead size, mmap policy, tracing, rate limiting, statistics, clock, read options, and file options.
- `PrepareIOFromReadOptions(...)` maps `ReadOptions` request id, deadline, `io_timeout`, rate limiter priority, and IO activity onto `IOOptions` and `IODebugContext`.
- `PrepareIOFromWriteOptions(...)` maps write rate limiter priority and IO activity.
- `DestroyDir(...)` is explicitly destructive and intended only for tests.
- `CheckFSFeatureSupport(...)` queries `FileSystem::SupportedOps` and checks the bit for a `FSSupportedOps` enum value.

## Control Flow and State

Most declarations defer implementation to corresponding `.cc` files. The inline path in `PrepareIOFromReadOptions` first propagates `request_id` into debug context if unset, then computes remaining deadline using `SystemClock::NowMicros()`. If the deadline has already passed, it returns `IOStatus::TimedOut`; otherwise it uses the tighter timeout between absolute deadline remainder and relative `io_timeout`. The function finally copies priority and activity fields. `PrepareIOFromWriteOptions` is simpler and has no failure path today.

The helpers do not own persistent state. They pass through filesystem handles, tracing, stats, and rate limiters. Persistence behavior is delegated to implementations: copy/create operations can fsync based on `use_fsync`; deletion helpers coordinate with `SstFileManager`/delete scheduler expectations; checksum generation performs read-only scans.

## Dependencies and Integration Points

This header depends on RocksDB file naming, DB options, `Env`, `FileSystem`, SST writer options, statistics, status, clocks, and IO tracing. It is included by `filename.cc` for `PrepareIOFromWriteOptions` and file writing; `random_access_file_reader.cc` for read option preparation; tests for `DestroyDir`; and readahead code for debug-only sector-alignment assertions.

## Risks and Edge Cases

- Passing a null or stale `SystemClock` into `PrepareIOFromReadOptions` would break deadline handling; callers generally use DB/system clocks.
- A deadline equal to or earlier than `NowMicros()` returns timeout intentionally to avoid passing zero timeout, which would mean no timeout.
- Deletion helpers rely on callers correctly classifying tracked versus unaccounted SST/blob files; using the wrong helper can skew size/trash accounting.
- `CheckFSFeatureSupport` assumes the enum value maps to a supported-ops bit position.

## Test Signals

`DestroyDir` is used in local tests such as `random_access_file_reader_test.cc` and `prefetch_test.cc` cleanup. `PrepareIOFromReadOptions` is indirectly exercised by random-access reads and tests that pass `IOOptions`/`ReadOptions` through reader paths. Deletion and checksum declarations need implementation-level coverage outside this header.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/filename.cc -->
# sources/storage-engines/rocksdb/file/filename.cc

## Purpose

`filename.cc` implements RocksDB's canonical file naming, filename parsing, and durable updates for key metadata files such as `CURRENT`, `IDENTITY`, manifests, options files, compaction-progress files, WALs, SSTs, blob files, and info logs. It is a central integration point between DB metadata, filesystem layout, and crash-safe state transitions.

## Important APIs, Types, and Functions

- Constants: `kCurrentFileName`, `kOptionsFileNamePrefix`, `kCompactionProgressFileNamePrefix`, `kTempFileNameSuffix`, plus internal extensions for `.sst`, `.ldb`, `.blob`, and `archive`.
- Name builders: `LogFileName`, `BlobFileName`, `ArchivalDirectory`, `ArchivedLogFileName`, `MakeTableFileName`, `TableFileName`, `DescriptorFileName`, `CurrentFileName`, `LockFileName`, `TempFileName`, `OptionsFileName`, `TempOptionsFileName`, `CompactionProgressFileName`, `TempCompactionProgressFileName`, `MetaDatabaseName`, and `IdentityFileName`.
- Conversion helpers: `Rocks2LevelTableFileName`, `TableFileNameToNumber`, `FormatFileNumber`, `NormalizePath`.
- `InfoLogPrefix` and `GetInfoLogPrefix(...)` flatten DB absolute paths for info logs stored outside the DB directory.
- `ParseFileName(...)` classifies known RocksDB filenames into `FileType`, numeric id/timestamp, and optional WAL archival state.
- `SetCurrentFile(...)` writes a temp file containing the active manifest basename, renames it to `CURRENT`, and optionally fsyncs the containing directory.
- `SetIdentityFile(...)` writes or generates the DB identity, renames it into place, fsyncs the DB directory, and closes the directory if supported.
- `SyncManifest(...)` syncs a `WritableFileWriter` with the DB's fsync policy and records `MANIFEST_FILE_SYNC_MICROS`.
- `GetInfoLogFiles(...)` lists files in either `db_log_dir` or the DB path and filters using `ParseFileName`.

## Control Flow and State

Name builders format numbers with fixed six-digit file ids for numbered data/log/temp files and prefixes for manifest/options/progress files. `TableFileName` chooses a path by `path_id`, falling back to the last configured DB path if the id is out of range.

`ParseFileName` strips one leading slash, then checks exact metadata names, info-log prefixes, manifest/metadb/options/progress prefixes, and finally numeric files with suffixes. It intentionally uses `ConsumeDecimalNumber` rather than locale-sensitive conversion. Archived WALs are recognized by the `archive/` prefix and must have `.log` suffix; archived table/blob/temp files are rejected.

`SetCurrentFile` is the crash-sensitive path. It formats the manifest name, writes `dbname/<number>.dbtmp` with a trailing newline, injects test sync/kill points, renames the temp file to `CURRENT`, optionally fsyncs the directory, and best-effort deletes the temp file on failure. `SetIdentityFile` similarly writes temp `000000.dbtmp`, renames to `IDENTITY`, fsyncs the directory, tolerates `Close()` not-supported, and cleans up temp on failure.

Persistent state touched by this file is DB directory metadata: `CURRENT`, `IDENTITY`, option/progress/temp names, and file paths used by manifests, WALs, SSTs, blobs, and info logs. Pure name builders have no process state; `InfoLogPrefix` stores a fixed buffer and `Slice` view.

## Dependencies and Integration Points

The file depends on `file_util.h` for write option preparation, `writable_file_writer.h`, `FileSystem`, `Env`, sync-point testing hooks, stop watches, and string utilities. It is consumed broadly by DB open/recovery, manifest management, logging, compaction, backup/restore, and file deletion code. Test sync points named around `SetCurrentFile`, `SyncManifest`, and `FileMetaData` allow crash and upgrade tests to inject behavior.

## Risks and Edge Cases

- `ParseFileName` returns true after exact and prefix cases, but for malformed info-log prefixes that partially match and then do not satisfy old-log forms, callers should rely on initialized outputs only on recognized types.
- `TableFileNameToNumber` parses digits before the last dot and returns zero for malformed names; callers needing strict validation should use `ParseFileName`.
- `InfoLogPrefix` has a 260-byte fixed buffer and truncates by construction to leave room for `_LOG`; very long DB paths can collide after flattening/truncation.
- `SetCurrentFile` and `SetIdentityFile` rely on rename atomicity and directory fsync support; unsupported close is tolerated, but fsync errors propagate.
- Path construction mostly uses `/` directly even though `kFilePathSeparator` exists for normalization, so cross-platform semantics depend on RocksDB's path conventions and filesystem wrappers.

## Test Signals

Sync points and random kill hooks support crash-consistency tests around `CURRENT` updates and manifest sync. `prefetch_test.cc` uses a `FileMetaData` sync point to simulate missing file tail sizes during upgrade, indirectly relying on filename/manifest metadata behavior. Filename parsing and construction are typically covered by RocksDB filename tests outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/filename.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/filename.h -->
# sources/storage-engines/rocksdb/file/filename.h

## Purpose

`filename.h` declares the filename contract for RocksDB database files. It defines the public internal interface for constructing, parsing, and committing file names used by WALs, SSTs, blobs, manifests, options snapshots, compaction-progress files, info logs, lock files, metadata databases, `CURRENT`, and `IDENTITY`.

## Important APIs, Types, and Functions

- `kFilePathSeparator` abstracts the platform separator for path normalization.
- WAL/blob/table builders include `LogFileName`, `BlobFileName`, `ArchivedLogFileName`, `MakeTableFileName`, `Rocks2LevelTableFileName`, `TableFileNameToNumber`, `TableFileName`, and `FormatFileNumber`.
- DB metadata builders include `DescriptorFileName`, `CurrentFileName`, `LockFileName`, `TempFileName`, `OptionsFileName`, `TempOptionsFileName`, `CompactionProgressFileName`, `TempCompactionProgressFileName`, `MetaDatabaseName`, and `IdentityFileName`.
- `InfoLogPrefix` stores a fixed buffer and a `Slice` naming prefix for regular or external log directories.
- `ParseFileName` has an overload that accepts `info_log_name_prefix` and one that skips info-log files.
- Mutating APIs include `SetCurrentFile`, `SetIdentityFile`, and `SyncManifest`.
- `GetInfoLogFiles` enumerates recognized info logs in a parent directory.
- `NormalizePath` collapses repeated separators while preserving UNC path prefix shape.

## Control Flow and State

The header itself has no implementation beyond declarations and constants. It defines which filename forms the implementation must produce and parse. The stateful operations it declares update persisted DB metadata (`CURRENT`, `IDENTITY`, manifest sync) through `FileSystem`, `Env`, `WritableFileWriter`, and directory handles.

## Dependencies and Integration Points

The declarations depend on DB path options, platform helpers, `FileSystem`, public `Options`, `Slice`, `Status`, and transaction-log file types. DB open/recovery, version-set/manifest code, WAL management, logging, and table-file placement all consume these APIs, making this header part of RocksDB's storage layout ABI.

## Risks and Edge Cases

- Any change to generated names or parse rules can affect recovery, backup compatibility, log discovery, and external tools.
- The overload that skips info logs is useful for callers that enumerate DB-owned numbered files but can surprise callers expecting `LOG` recognition.
- `SetCurrentFile` requires a valid directory handle when the caller wants directory fsync; omitting it trades durability for caller-managed sync semantics.
- The path-normalization contract is intentionally narrow and should not be treated as full canonicalization.

## Test Signals

Most tests are indirect: DB reopen, recovery, flush/compaction, manifest sync, and log listing all depend on these declarations. The corresponding implementation contains sync points used by crash/upgrade tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/filename.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/line_file_reader.cc -->
# sources/storage-engines/rocksdb/file/line_file_reader.cc

## Purpose

`line_file_reader.cc` implements a small buffered line reader over RocksDB's `SequentialFileReader`. It is used for text-like files where callers need newline-delimited records and RocksDB IO accounting/rate-limiting behavior.

## Important APIs, Types, and Functions

- `LineFileReader::Create(...)` opens an `FSSequentialFile` from a `FileSystem`, wraps it in `LineFileReader`, and passes through debug context and rate limiter.
- `LineFileReader::ReadLine(...)` reads the next line into an output string, excluding the `\n` delimiter, and charges reads at the requested `Env::IOPriority`.

## Control Flow and State

`Create` calls `fs->NewSequentialFile`; on success it constructs `LineFileReader` with the file, filename, no IO tracer, no listeners, and the optional rate limiter.

`ReadLine` first rejects calls after a stored IO error. It clears the output and searches the existing buffer with `memchr` for `\n`. On delimiter hit it appends bytes before the delimiter, advances `buf_begin_`, increments `line_number_`, and returns true. Without a delimiter, it appends all buffered bytes. If EOF was already observed, it returns false with OK status. Otherwise it refills the 8192-byte buffer via `SequentialFileReader::Read`, records `bytes_read`, stores any IO error permanently, and treats a short read as EOF. A final unterminated line is returned on the iteration where data is read; the following call returns false.

The object keeps volatile read state only: the buffer, begin/end pointers into the current `Slice`, line number, EOF flag, and permanent `IOStatus`.

## Dependencies and Integration Points

It depends on `line_file_reader.h`, `SequentialFileReader`, filesystem APIs, `IOSTATS_ADD`, and rate limiting through the sequential reader. It integrates with code that reads plain RocksDB metadata or diagnostic files without exposing raw `SequentialFile` handling.

## Risks and Edge Cases

- Lines longer than 8192 bytes are supported by repeated append/refill, but cause repeated string growth.
- The method returns false for both EOF and IO error; callers must inspect `GetStatus()`.
- A permanent IO error cannot be retried with the same reader.
- `buf_begin_` points to `result.data()` from the sequential reader; correctness assumes that data remains valid until the next read through the reader wrapper.

## Test Signals

No direct tests are in this subset. The implementation is straightforward but should be covered by tests for newline-delimited files, last line without newline, empty files, IO errors, and long lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/line_file_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/line_file_reader.h -->
# sources/storage-engines/rocksdb/file/line_file_reader.h

## Purpose

`line_file_reader.h` declares `LineFileReader`, a non-copyable wrapper around `SequentialFileReader` for newline-delimited text reads using RocksDB filesystem, IO status, and rate-limiting conventions.

## Important APIs, Types, and Functions

- Internal fields: `std::array<char, 8192> buf_`, `SequentialFileReader sfr_`, `IOStatus io_status_`, buffer begin/end pointers, `line_number_`, and `at_eof_`.
- Variadic constructor forwards arguments to `SequentialFileReader`.
- Static `Create(...)` opens and wraps a file via `FileSystem`.
- `ReadLine(std::string*, Env::IOPriority)` returns the next line without delimiter.
- `GetLineNumber()` reports the most recently returned line count.
- `GetStatus()` exposes the permanent read status.

## Control Flow and State

The header defines the reader's state model: one buffered sequential scan with monotonically increasing line number and no recovery after IO error. It prevents copying so buffer pointers and file-reader ownership cannot be duplicated accidentally.

## Dependencies and Integration Points

The header depends on `file/sequence_file_reader.h`, which supplies the actual sequential file wrapper and IO/rate-limiter behavior. Consumers get a simple line API without depending directly on `FSSequentialFile`.

## Risks and Edge Cases

- `GetLineNumber()` is unspecified after IO-error false returns, so callers should check `GetStatus()`.
- The `ReadLine` contract requires callers to distinguish EOF from failure.
- The forwarding constructor makes construction flexible but also means invalid `SequentialFileReader` argument combinations are diagnosed by that lower layer.

## Test Signals

Direct tests are not present in this subset. Coverage should focus on EOF semantics, delimiter stripping, line counting, rate-limiter priority forwarding, and permanent error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/line_file_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/prefetch_test.cc -->
# sources/storage-engines/rocksdb/file/prefetch_test.cc

## Purpose

`prefetch_test.cc` is an extensive integration and unit test suite for RocksDB prefetch behavior. It validates filesystem prefetch selection, `FilePrefetchBuffer`, tail prefetch during table open/verification, adaptive and implicit readahead, block cache interactions, iterator seek/scan behavior, async IO/io_uring paths, poll error propagation, IO tracing, and filesystem-buffer reuse.

## Important APIs, Types, and Fixtures

- `MockRandomAccessFile` wraps `FSRandomAccessFile`, optionally supports `Prefetch`, counts prefetch calls, and can force buffer alignment to 1.
- `MockFS` wraps a filesystem and returns `MockRandomAccessFile`; it exposes `ClearPrefetchCount`, `IsPrefetchCalled`, and `GetPrefetchCount`.
- `PrefetchTest` is a `DBTestBase` parameterized by filesystem-prefetch support and direct IO. It configures DB/table options and provides correctness helpers `VerifyScan` and `VerifySeekPrevSeek`.
- `PrefetchTailTest` extends `PrefetchTest` with helpers for tail-prefetch scenarios and partitioned index/filter options.
- `PrefetchTrimReadaheadTestParam` tests readahead trimming with different index shortening modes and auto-readahead settings.
- `PrefetchTest1` focuses on async seek parallelization and adaptive readahead.
- `FilePrefetchBufferTest` directly exercises `FilePrefetchBuffer` using a `RandomAccessFileReader`.
- `FSBufferPrefetchTest` tests buffer reuse and async/sync prefetch internals, including a custom `BufferReuseFS` that advertises `kFSBuffer`.

## Control Flow and State

The tests repeatedly build small RocksDB instances with deterministic keys and values, flush or compact to create SST layouts, then read through iterators or direct `FilePrefetchBuffer` calls while sync-point callbacks count internal events. The primary state observed is prefetch counters, RocksDB statistics histograms/tickers, perf context counters, buffer offsets/sizes, iterator validity/status, and file contents read from prefetch buffers.

Core scenarios include:

- Basic selection: when filesystem prefetch is supported and direct IO is disabled, RocksDB should call filesystem `Prefetch`; otherwise it should use `FilePrefetchBuffer`.
- Tail prefetch: table verification/open should use prefetched tails to reduce extra reads, and upgrade logic should handle missing manifest tail-size metadata without per-partition read explosion.
- Dynamic readahead settings: mutable `block_based_table_factory` options for max/initial auto readahead and number of file reads are refreshed and affect iterator prefetch behavior.
- Reseek heuristics: sequential block reads enable prefetch; non-sequential reads and single-block rereads do not; cached blocks can suppress or reduce readahead.
- Trimming: auto readahead is trimmed by `prefix_same_as_start` or iterate upper bound, recorded by `READAHEAD_TRIMMED`.
- Adaptive readahead: sequential scans carry readahead state across SST files; non-sequential moves fall back to initial size.
- Async IO: `ReadOptions::async_io`, io_uring availability, seek parallelization, extra prefetch on seek, async byte histograms, and fallback when io_uring is disabled are all validated.
- Error handling: injected `Poll()` IO errors must propagate to iterator status or direct `FilePrefetchBuffer` status and must not corrupt retry reads.
- Direct buffer tests: `FilePrefetchBuffer` tests validate alignment, overlap buffer reuse, useful-byte stats, sync fallback, compaction mode, and randomized read sequences.

## Dependencies and Integration Points

The suite touches DB internals, block-based table options, file prefetch buffer implementation, file utilities, filesystem wrappers, sync points, io tracer parser tooling when `GFLAGS` is enabled, direct IO test mocking, statistics, perf context, caches, compaction, flush, iterators, and Posix filesystem async behavior. Because it drives real DB operations, it is a broad integration signal for table readers, block cache, and storage-engine file IO.

## Risks and Edge Cases

- Many expectations depend on exact block layouts, data sizes, and partitioned index behavior; small production changes can require test updates.
- Tests often bypass when direct IO or async IO is unsupported, so platform coverage varies.
- Sync-point counters can be brittle if internal function names or call counts change.
- Some tests distinguish filesystem prefetch versus RocksDB buffer prefetch, which is sensitive to mock filesystem capability reporting.
- Async tests must handle io_uring fallback cleanly; false assumptions about async availability would cause flaky assertions.
- Direct internal buffer assertions are valuable but tightly coupled to `FilePrefetchBuffer` layout and alignment policy.

## Test Signals

This file is itself the test signal for the prefetch subsystem. It verifies correctness by comparing iterator output to baseline iterators, matching file content slices, checking IO statuses, and asserting statistics such as `TABLE_OPEN_PREFETCH_TAIL_READ_BYTES`, `COMPACTION_PREFETCH_BYTES`, `FILE_READ_*_MICROS`, `ASYNC_READ_BYTES`, `READ_ASYNC_MICROS`, `PREFETCH_HITS`, `PREFETCH_BYTES_USEFUL`, `PREFETCHED_BYTES_DISCARDED`, `READAHEAD_TRIMMED`, and block-cache miss counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/prefetch_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/random_access_file_reader.cc -->
# sources/storage-engines/rocksdb/file/random_access_file_reader.cc

## Purpose

`random_access_file_reader.cc` implements `RandomAccessFileReader`, RocksDB's instrumentation and policy wrapper around `FSRandomAccessFile`. It handles direct-I/O alignment, rate limiting, multi-read request alignment/merging, async read callbacks, IO statistics, file-temperature accounting, operation histograms, perf context, IO tracing through the wrapped pointer, and listener notifications.

## Important APIs, Types, and Functions

- `GetFileReadHistograms(...)` maps `Env::IOActivity` to detailed histogram buckets when enabled.
- `RecordIOStats(...)` records bytes/read counts for last-level versus non-last-level files and by `Temperature`.
- `RandomAccessFileReader::Create(...)` opens an `FSRandomAccessFile` and wraps it.
- `Read(...)` performs one random read with direct-I/O alignment/copy handling, optional external aligned allocation, rate limiting, stats, and listener notifications.
- `Align(...)` page-aligns a `FSReadRequest`.
- `TryMerge(...)` merges overlapping or adjacent read intervals.
- `MultiRead(...)` handles batches, including direct-I/O alignment and merged filesystem requests.
- `PrepareIOOptions(...)` converts `ReadOptions` to `IOOptions` using the configured clock or default clock.
- `ReadAsync(...)` submits async reads and prepares callback state for unaligned direct I/O.
- `ReadAsyncCallback(...)` maps aligned async results back to user offsets/buffers, records stats, notifies listeners, and frees callback state.

## Control Flow and State

`Read` first perturbs the scratch byte to avoid stale-data false positives, calculates required alignment, and branches on direct I/O with unaligned inputs. In the unaligned direct-I/O branch, it rounds offset/length to alignment, allocates either an internal or caller-provided aligned buffer, reads in rate-limited chunks, optionally notifies listeners per filesystem read, then returns the requested subrange either by pointing into external aligned storage or copying into scratch. In the normal/aligned branch, it loops until requested bytes are read, rate limiting each chunk and preserving mmap result pointers when the filesystem returns memory outside scratch.

`MultiRead` asserts ordered requests, perturbs scratches, and for direct I/O aligns each request, merges overlapping/adjacent aligned intervals, allocates one large aligned buffer, assigns scratch pointers, and calls `file_->MultiRead`. It then maps filesystem results back to original unaligned requests. It charges rate limiter tokens for the total batch up front and records per-request notifications and byte stats.

`ReadAsync` allocates `ReadAsyncInfo`, records start time/listener start, and for unaligned direct I/O creates an aligned request with aligned storage. On submit failure it deletes callback state. `ReadAsyncCallback` reconstructs the user-visible request, copies or transfers buffer ownership as needed, calls the user callback, records async histograms/error tickers, notifies listeners, records IO stats, and deletes the callback info.

Persistent state is not modified. The reader owns a traced `FSRandomAccessFilePtr`, file name, optional clock/stats/histogram/rate limiter, filtered event listeners, file temperature, and last-level flag. Async operations temporarily own callback metadata and possibly aligned buffers until completion.

## Dependencies and Integration Points

The implementation depends on `file_util.h`, RocksDB histograms/statistics, IO stats context, perf-level helpers, table format constants, sync points, random test hooks, and rate limiter implementation. It is used by table readers, file prefetch buffers, checksum verification, and other code paths needing random file reads with RocksDB observability.

## Risks and Edge Cases

- Direct-I/O code assumes power-of-two alignment semantics through bit masks; invalid filesystem alignment values would break checks.
- Unaligned direct reads can allocate larger rounded buffers, so callers must manage memory pressure and external allocation lifetimes.
- Async direct-I/O callback uses caller-owned scratch or aligned buffer contracts; freeing buffers before callback completion is unsafe.
- `MultiRead` requires sorted non-overlapping input; debug asserts catch order but release builds rely on callers.
- Rate limiting in `MultiRead` charges total bytes in bursts before the call; a TODO notes this can cause burstiness for large batches.
- Listener notification status must be permitted unchecked after callbacks; the implementation does so to avoid status-check assertions.
- `Read` returns an empty result on IO error even if partial bytes were read.

## Test Signals

`random_access_file_reader_test.cc` directly covers direct-I/O read copying, external aligned allocation, multiread alignment/merge behavior, `Align`, and `TryMerge`. `prefetch_test.cc` exercises `ReadAsync`, direct reads through `FilePrefetchBuffer`, async fallback, poll error propagation, and stats integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/random_access_file_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/random_access_file_reader.h -->
# sources/storage-engines/rocksdb/file/random_access_file_reader.h

## Purpose

`random_access_file_reader.h` declares the RocksDB wrapper around `FSRandomAccessFile`. The wrapper presents synchronous, batched, prefetch, and asynchronous random-read APIs while centralizing direct-I/O handling, rate limiting, listener notification, IO tracing, and statistics.

## Important APIs, Types, and Functions

- `using AlignedBuf = FSAllocationPtr` names ownership returned for aligned async buffers.
- `AlignedBufferAllocationContext` lets callers provide an `AlignedBuffer` and optional allocator for direct-I/O result storage.
- `Align(...)` and `TryMerge(...)` are helper APIs for `FSReadRequest` intervals.
- `RandomAccessFileReader` constructor accepts an `FSRandomAccessFile`, file name, clock, IO tracer, stats/histogram handles, rate limiter, event listeners, file temperature, and last-level flag.
- `Read(...)` supports scratch or direct-I/O allocation-context result storage.
- `MultiRead(...)` supports ordered batches and direct-I/O shared aligned buffers.
- `Prefetch(...)` forwards to the underlying file.
- `PrepareIOOptions(...)` maps `ReadOptions` to `IOOptions`.
- `ReadAsync(...)` and `ReadAsyncCallback(...)` wrap asynchronous random reads.
- Private `NotifyOnFileReadFinish` and `NotifyOnIOError` adapt read events to `EventListener`.

## Control Flow and State

The header establishes ownership and lifetime contracts. The reader is non-copyable and owns its low-level file through `FSRandomAccessFilePtr`, which also carries tracing context. It stores only borrowed pointers for clock, stats, histograms, and rate limiter. It filters listeners to those interested in file IO. `ReadAsyncInfo` owns callback state and, for direct-I/O unaligned reads, may own an `AlignedBuffer` until the callback completes.

## Dependencies and Integration Points

It depends on file-system tracing, platform helpers, `FileSystem`, listeners, options, rate limiting, and aligned buffers. Table readers and file prefetch code use it instead of raw `FSRandomAccessFile` to preserve RocksDB-level IO accounting and listener behavior.

## Risks and Edge Cases

- The direct-I/O allocation context is non-owning with respect to allocator and buffer lifetime; callers must keep them valid for the duration of read submission and result use.
- Async direct-I/O storage may be referenced by completion callbacks, so caller-provided buffers must outlive async operations.
- `MultiRead` requires increasing non-overlapping requests and a non-null direct-I/O buffer context in direct mode.
- The `file()` accessor exposes a mutable raw pointer, so callers can bypass wrapper policy if misused.

## Test Signals

The companion test file validates public helpers and direct-I/O behavior. Prefetch tests exercise the async and prefetch-facing APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/random_access_file_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/random_access_file_reader_test.cc -->
# sources/storage-engines/rocksdb/file/random_access_file_reader_test.cc

## Purpose

`random_access_file_reader_test.cc` unit-tests `RandomAccessFileReader` direct-I/O behavior and helper interval logic. It focuses on correctness of unaligned reads, scratch copying, external allocation, multi-read alignment/merging, and helper functions.

## Important APIs, Types, and Functions

- `RandomAccessFileReaderTest` fixture creates a per-thread DB path, uses `SetupSyncPointsToMockDirectIO`, writes test files, opens readers with direct-read options, and validates request results.
- `ReadDirectIO` verifies unaligned direct-I/O reads return the requested substring when using an external aligned buffer context and both low and total rate-limiter priorities.
- `ReadDirectIOCopiesToScratch` verifies unaligned direct reads copy back into caller scratch when no direct buffer context is supplied.
- `ReadDirectIOUsesExternalBuffer` verifies an external `AlignedBuffer::Allocator` is used once with page-size alignment and that result data points into the external storage.
- `MultiReadDirectIO` validates aligned request construction and merging for multiple request layouts using the `RandomAccessFileReader::MultiRead:AlignedReqs` sync point.
- `MultiReadDirectIOUsesExternalBuffer` checks one external allocation for multiple direct-I/O requests and verifies result slices live inside that storage.
- `FSReadRequest.Align` and `FSReadRequest.TryMerge` test alignment and interval merge semantics.

## Control Flow and State

Each test writes deterministic random content, opens a random-access reader, computes the filesystem alignment, performs reads at deliberately unaligned offsets/lengths, and compares returned slices to substrings. The multi-read test captures internal aligned requests via sync point after `MultiRead` builds them, then asserts whether separate user requests collapse to one or multiple filesystem reads.

The fixture owns only test directory, env, and filesystem state. Test files are removed with `DestroyDir` in teardown.

## Dependencies and Integration Points

The tests depend on `file_util.h` for cleanup, `SetupSyncPointsToMockDirectIO`, default filesystem/env, RocksDB test harness, random data generation, and sync points. They are tightly coupled to `RandomAccessFileReader` direct-I/O internals and default page-size alignment.

## Risks and Edge Cases

- Tests skip only implicitly through mocked direct IO setup; real platform direct-I/O quirks are abstracted by test sync points.
- Expected merged intervals rely on adjacent intervals being mergeable, matching `TryMerge`'s inclusive/adjacent logic.
- External allocator tests use a no-op owner around external storage; production callers must ensure true lifetime ownership.

## Test Signals

This file provides direct regression coverage for subtle data-corruption risks in direct I/O: stale scratch data, wrong subrange extraction, incorrect merged batch offsets, and allocator misuse. It complements broader async/prefetch coverage in `prefetch_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/random_access_file_reader_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/read_write_util.cc -->
# sources/storage-engines/rocksdb/file/read_write_util.cc

## Purpose

`read_write_util.cc` implements small filesystem utility functions used by RocksDB file readers/writers. It wraps writable-file creation for test instrumentation, implements robust file-size discovery from an open file or path fallback, and provides a debug-only sector-alignment predicate.

## Important APIs, Types, and Functions

- `NewWritableFile(...)` calls `FileSystem::NewWritableFile` with test sync-point exposure of `FileOptions.temperature` and random kill injection.
- `GetFileSizeFromOpenFileOrPath(...)` first asks an already-open `FSRandomAccessFile` for size, then optionally falls back to `FileSystem::GetFileSize`.
- `IsFileSectorAligned(...)` returns whether an offset is a multiple of sector/alignment size in debug builds.

## Control Flow and State

`NewWritableFile` is a straight wrapper: expose temperature via sync point, create file, inject a test kill point, and return status.

`GetFileSizeFromOpenFileOrPath` asserts non-null inputs, calls `file->GetFileSize`, and returns immediately on success. If the open-file size call fails with `NotSupported`, or if the caller selected `FileSizeFallback::kAnyOpenFileError`, it invokes the optional `before_path_fallback` callback and asks the filesystem for the path size. Otherwise it returns the original open-file error.

There is no persistent state. Side effects are file creation and optional test process termination through kill hooks.

## Dependencies and Integration Points

The implementation depends on `read_write_util.h`, assertions, sync points, `FileSystem`, `FSRandomAccessFile`, and `IOOptions`. `readahead_raf.cc` uses the debug alignment helper. File creation wrappers are used by code paths that need RocksDB test hooks around writable files.

## Risks and Edge Cases

- The fallback callback runs only when path fallback will be attempted; callers can use it for synchronization or instrumentation.
- Falling back on any open-file error can hide real open-handle failures if used too broadly.
- Debug-only alignment assertions disappear in release builds.

## Test Signals

Sync points and kill hooks support fault-injection tests. The alignment helper is asserted in `readahead_raf.cc` buffer reads under debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/read_write_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/read_write_util.h -->
# sources/storage-engines/rocksdb/file/read_write_util.h

## Purpose

`read_write_util.h` declares low-level read/write helper APIs for RocksDB's file layer: writable-file creation, fallback file-size lookup, and debug-only sector alignment checks.

## Important APIs, Types, and Functions

- `NewWritableFile(FileSystem*, const std::string&, std::unique_ptr<FSWritableFile>*, const FileOptions&)`.
- `enum class FileSizeFallback` with `kNotSupportedOnly` and `kAnyOpenFileError`.
- `using BeforePathFileSizeFallback = void (*)()`.
- `GetFileSizeFromOpenFileOrPath(...)`.
- Debug-only `IsFileSectorAligned(...)`.

## Control Flow and State

The header declares stateless utilities. The file-size API encodes a two-stage strategy: prefer an open random-access file, then use path lookup according to fallback policy. It exposes a callback hook before path fallback without tying callers to a particular callback object type.

## Dependencies and Integration Points

It includes `sequence_file_reader.h`, `rocksdb/env.h`, and `rocksdb/file_system.h`. The helpers are used by file wrappers, readahead code, and tests needing consistent RocksDB filesystem behavior.

## Risks and Edge Cases

- The callback type is a raw function pointer, so capturing lambdas cannot be passed directly.
- Callers must pass non-null file, filesystem, and output size pointers.
- The debug-only alignment function should not be used as the only production validation.

## Test Signals

Coverage is indirect through readahead direct-buffer assertions and file-creation fault-injection tests. File-size fallback behavior should be covered with mock filesystems that return `NotSupported` and other errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/read_write_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/readahead_file_info.h -->
# sources/storage-engines/rocksdb/file/readahead_file_info.h

## Purpose

`readahead_file_info.h` defines a small state carrier for readahead information passed between files during iteration. Its goal is to let iterators continue an established automatic prefetch size and read count when moving to the next file in a level, instead of restarting from the initial readahead state.

## Important APIs, Types, and Functions

- `struct ReadaheadFileInfo` contains two `ReadaheadInfo` members:
  - `data_block_readahead_info` for data block iterators.
  - `index_block_readahead_info` for index block iterators.
- Nested `struct ReadaheadInfo` stores:
  - `size_t readahead_size = 0`.
  - `int64_t num_file_reads = 0`.

## Control Flow and State

The header has no functions. It defines plain value state that can be copied or updated by iterator/prefetch components. The state is in-memory only and is not persisted to DB files or manifests.

## Dependencies and Integration Points

It depends only on standard integer/size headers and the RocksDB namespace header. It integrates with block iterators and prefetchers that need separate carry-over state for data and index block read streams.

## Risks and Edge Cases

- Both counters default to zero, so callers must distinguish uninitialized/new-file state from a deliberate zero readahead policy.
- Data and index streams are separate; mixing them would produce incorrect adaptive behavior.
- The struct has no synchronization; it should be updated according to iterator ownership/threading rules.

## Test Signals

`prefetch_test.cc` verifies this behavior indirectly in `DBIterLevelReadAhead` and `DBIterLevelReadAheadWithAsyncIO`, where sync points assert readahead state is carried to subsequent files and grows beyond the initial 8 KiB size during sequential scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/readahead_file_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/readahead_raf.cc -->
# sources/storage-engines/rocksdb/file/readahead_raf.cc

## Purpose

`readahead_raf.cc` implements `NewReadaheadRandomAccessFile`, a wrapper that adds fixed-size read-ahead caching on top of an `FSRandomAccessFile`. It is mainly used by compaction table readers to fetch extra data with reads and reduce repeated filesystem calls during sequential-ish access.

## Important APIs, Types, and Functions

- Internal `ReadaheadRandomAccessFile` derives from `FSRandomAccessFile`.
- Constructor stores the wrapped file, required alignment, rounded readahead size, aligned buffer, and initial buffer offset.
- `Read(...)` serves data from the cache when possible, otherwise reads an aligned readahead chunk into the internal buffer and copies requested bytes to caller scratch.
- `Prefetch(...)` fills the internal buffer, but ignores requests smaller than configured readahead size.
- Forwarders: `GetUniqueId`, `Hint`, `InvalidateCache`, `use_direct_io`, and `GetFileSize`.
- Private `TryReadFromCache(...)` copies cached bytes.
- Private `ReadIntoBuffer(...)` reads aligned data into `buffer_` and updates `buffer_offset_`/size.
- `NewReadaheadRandomAccessFile(...)` constructs the wrapper.

## Control Flow and State

The constructor rounds `readahead_size` up to filesystem alignment, sets buffer alignment, and allocates the buffer. `Read` bypasses readahead when the caller's request is too large to leave useful slack. Otherwise it locks, tries to copy a complete or partial cache hit, and returns immediately if the full request is satisfied or the short buffer indicates EOF. On miss/partial hit it advances to the first uncached byte, truncates to an aligned chunk offset, reads up to the configured readahead size into the cache, then copies the remaining requested bytes from cache.

`Prefetch` refuses smaller-than-configured prefetches because `Read` treats a buffer shorter than `readahead_size_` as EOF. For valid requests it aligns the offset, skips if already at the same buffer offset, and reads the requested aligned range capped by buffer capacity.

The wrapper maintains mutable in-memory cache state protected by a mutex: `buffer_` and `buffer_offset_`. It does not persist anything.

## Dependencies and Integration Points

It depends on `read_write_util.h` for debug alignment assertions, `FSRandomAccessFile`, `AlignedBuffer`, and rate-limiter utilities for rounding helpers. It integrates as a drop-in `FSRandomAccessFile` wrapper, preserving unique id, hints, direct-IO mode, and file size behavior from the target.

## Risks and Edge Cases

- `Read` copies into caller scratch, so scratch must be large enough even when cache hits span partial buffers.
- Requests with `n + alignment >= readahead_size_` bypass the cache, so small readahead sizes can disable benefits.
- `Prefetch` no-ops for small requests by design; callers expecting exact prefetch length may be surprised.
- The implementation assumes aligned offset/length for buffer reads and asserts in debug.
- `offset + n` arithmetic is converted through `size_t`; extremely large offsets could be risky on 32-bit platforms.

## Test Signals

Direct tests are not in this subset, but `prefetch_test.cc` covers broader prefetch behavior and `read_write_util` alignment assertions protect this implementation in debug builds. Compaction table-reader tests should observe reduced read calls when this wrapper is active.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/readahead_raf.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/readahead_raf.h -->
# sources/storage-engines/rocksdb/file/readahead_raf.h

## Purpose

`readahead_raf.h` declares a factory for wrapping an `FSRandomAccessFile` with fixed read-ahead behavior. It is a compact public-internal entry point for compaction table readers and other code that wants automatic extra reads behind the random-access-file interface.

## Important APIs, Types, and Functions

- Forward declaration of `FSRandomAccessFile`.
- `NewReadaheadRandomAccessFile(std::unique_ptr<FSRandomAccessFile>&&, size_t readahead_size)` returns a new `FSRandomAccessFile` wrapper.

## Control Flow and State

The header has no implementation. Ownership of the input file is transferred into the returned wrapper. Runtime state is managed by the implementation's internal cache buffer and lock.

## Dependencies and Integration Points

It depends only on `<memory>` and RocksDB namespace declaration. The comments place it beside other file-layer wrappers such as `SequentialFileReader`, `RandomAccessFileReader`, and `WritableFileWriter`, and identify compaction table readers as the main consumer.

## Risks and Edge Cases

- Callers should not use the input file after moving it into the factory.
- A zero or tiny `readahead_size` would be rounded/allocated by the implementation and may not provide useful caching.
- The wrapper preserves the `FSRandomAccessFile` abstraction, so callers do not get direct access to cache internals.

## Test Signals

Coverage is indirect through compaction and prefetch tests. Dedicated tests would validate cache hits, partial hits, EOF, invalidation, direct-IO alignment, and small-request prefetch no-op behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/readahead_raf.h -->
