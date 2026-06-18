# subset-b-008638 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.cc -->
# sources/storage-engines/rocksdb/file/sequence_file_reader.cc

## Purpose

`sequence_file_reader.cc` implements `SequentialFileReader`, RocksDB's production wrapper around `FSSequentialFile`. It normalizes sequential reads across buffered I/O, direct I/O, optional read-ahead, rate limiting, IO stats, IO tracing, data verification/reconstruction flags, and file-I/O event listeners. The file is on the ingestion/recovery/read side of the storage stack where readers consume WALs, MANIFESTs, table-building inputs, or other sequential files through a consistent API.

## Important APIs, Types, and Functions

- `SequentialFileReader::Create()` opens an `FSSequentialFile` through `FileSystem::NewSequentialFile` and wraps it with a reader carrying a rate limiter.
- `SequentialFileReader::Read(size_t, Slice*, char*, Env::IOPriority)` is the main read path. It builds `IOOptions`, applies `verify_and_reconstruct_read_`, handles direct-vs-buffered I/O, charges the rate limiter, updates `IOSTATS_ADD(bytes_read, ...)`, and notifies listeners.
- `SequentialFileReader::Skip(uint64_t)` advances the tracked direct-I/O offset locally or delegates to `FSSequentialFile::Skip` for buffered files.
- `SequentialFileReader::NewReadaheadSequentialFile()` conditionally wraps the underlying sequential file in an internal `ReadaheadSequentialFile`.
- The anonymous `ReadaheadSequentialFile` class maintains an aligned prefetch buffer, a `buffer_offset_`, and a logical `read_offset_` protected by a mutex.

## Control Flow

`Create()` is straightforward: ask the filesystem for a sequential file, then build a `SequentialFileReader` when that succeeds. `Read()` first sets `rate_limiter_priority` and `verify_and_reconstruct_read` in `IOOptions`. In direct-I/O mode it atomically reserves the logical range by `offset_.fetch_add(n)`, rounds the physical read range to file-buffer alignment, allocates an `AlignedBuffer`, and repeatedly issues `PositionedRead()` calls until the aligned range is filled, an error occurs, or EOF/short read is reached. It copies only the requested unaligned subrange into caller scratch before returning.

In buffered mode `Read()` perturbs `scratch[0]` for paranoia when possible, then loops on `file_->Read()` until `n` bytes, EOF, or error. Listener offsets are based on `offset_.fetch_add(tmp.size())`, so notifications reflect bytes actually returned. Rate limiting can split both buffered and direct reads into smaller underlying file operations unless `Env::IO_TOTAL` bypasses the limiter.

`ReadaheadSequentialFile::Read()` first attempts to satisfy the request from the prefetch buffer. If a complete hit occurs, or the prefetch buffer had reached EOF, it returns immediately. For large reads that would consume almost the full prefetch window, it reads directly from the underlying file and clears the cache. Otherwise it fills the cache with `readahead_size_` bytes and then copies the requested bytes out. `Skip()` consumes cached bytes first, delegates any remainder to the underlying file, and clears stale cache state.

## State and Persistence Behavior

The reader does not persist metadata, but it is stateful. `offset_` is the reader-visible sequential offset and is especially important for direct I/O because direct mode uses positional reads rather than advancing the file object. `ReadaheadSequentialFile` keeps its own `read_offset_` and buffer range to avoid extra remote/file-system calls. Neither wrapper owns durable state; all durable effects are limited to the filesystem data being read and any underlying verification/reconstruction side effects requested through `IOOptions`.

## Dependencies and Integration Points

The implementation depends on `FileSystem`, `FSSequentialFile`, `FSSequentialFilePtr` tracing wrappers, `AlignedBuffer`, rate limiter APIs, `IOOptions`, file-operation listeners, sync points, and `IOSTATS`. It integrates with RocksDB callers that need direct-I/O-safe sequential reads and with event listeners observing file reads. The read-ahead wrapper is an internal adapter used by the constructor overload in the header.

## Risks and Edge Cases

The direct-I/O path is sensitive to alignment math: the physical read range can be larger than the logical request, and only the requested subsection can be returned. Short reads must not copy beyond valid bytes. The `offset_` update happens before direct reads complete, so concurrent calls receive disjoint logical ranges but errors still advance the offset. Buffered listener offsets only advance when listeners are present, while the underlying sequential file advances regardless; this is acceptable for notification accounting but makes listener offset maintenance a separate state path. The read-ahead wrapper has EOF-specific behavior when the buffer fills less than `readahead_size_`, and skip-after-cache logic depends on monotonic `read_offset_`.

## Test Signals

Useful signals include direct-I/O sequential read tests with unaligned logical offsets, EOF short reads, rate-limited multi-token reads, read-ahead cache-hit and cache-miss paths, `Skip()` across cached and uncached ranges, listener callback offset/length assertions, and IO-stat byte counts. Sync-point labels and filesystem wrappers can expose race and error behavior around underlying reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.h -->
# sources/storage-engines/rocksdb/file/sequence_file_reader.h

## Purpose

`sequence_file_reader.h` declares `SequentialFileReader`, the public internal wrapper RocksDB uses instead of calling `FSSequentialFile` directly. The class centralizes direct I/O handling, optional readahead wrapping, rate limiter charging, IO tracing, listener notification, and IO stats for sequential read consumers.

## Important APIs, Types, and Functions

- Constructors accept a unique `FSSequentialFile`, file name, optional `IOTracer`, event listeners, optional `RateLimiter`, and `verify_and_reconstruct_read` flag. One overload also accepts a readahead size and wraps the file.
- `static IOStatus Create(...)` opens through a `FileSystem` and returns a ready reader.
- `IOStatus Read(size_t n, Slice* result, char* scratch, Env::IOPriority)` is the main API, with explicit rate-limiter priority.
- `IOStatus Skip(uint64_t n)` advances the sequential position.
- `FSSequentialFile* file()`, `std::string file_name()`, and `bool use_direct_io()` expose underlying state to callers.
- Private `NotifyOnFileReadFinish()`, `AddFileIOListeners()`, and `ShouldNotifyListeners()` implement event-listener integration.
- Private `NewReadaheadSequentialFile()` produces the internal prefetch adapter.

## Control Flow

The header establishes construction-time filtering of listeners: only listeners returning `ShouldBeNotifiedOnFileIO()` are retained. The `Read()` implementation is responsible for deciding whether buffered or direct I/O rules apply. The class stores the rate limiter and verification flag rather than requiring all callers to thread those settings through every read.

## State and Persistence Behavior

`file_name_` is used for diagnostics and listener events. `file_` owns the underlying sequential file through a tracing-aware pointer. `offset_` tracks the reader's sequential offset and is atomic so multiple readers through the same wrapper can reserve offsets without data races. `listeners_`, `rate_limiter_`, and `verify_and_reconstruct_read_` are configuration state. The class itself has no durable persistence behavior.

## Dependencies and Integration Points

The declaration pulls in `env/file_system_tracer.h`, `rocksdb/env.h`, `rocksdb/file_system.h`, `EventListener`, `FileOperationInfo`, `RateLimiter`, and RocksDB port abstractions. It is used by code that needs an `FSSequentialFile` plus RocksDB instrumentation semantics, including WAL/MANIFEST/table-building readers and tests using custom filesystems.

## Risks and Edge Cases

The API assumes caller-provided `scratch` remains valid and large enough for requested output. The rate limiter priority contract notes that the limiter can be charged for `n` even when EOF returns fewer bytes, so callers wanting exact charge should cap `n` by known file size. Direct I/O correctness depends on callers respecting `use_direct_io()` implications indirectly through this wrapper. Listener callbacks must not throw or block unexpectedly, because they run inline on I/O completion.

## Test Signals

Signals include successful creation failure propagation, listener filtering, direct-I/O reads with aligned buffers, rate-limiter bypass with `Env::IO_TOTAL`, verification flag propagation through `IOOptions`, skip behavior, and readahead constructor behavior when the readahead size is too small to be useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sequence_file_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.cc -->
# sources/storage-engines/rocksdb/file/sst_file_manager_impl.cc

## Purpose

`sst_file_manager_impl.cc` implements `SstFileManagerImpl`, RocksDB's concrete manager for tracking SST/blob file disk usage, enforcing configured space limits, throttling file deletion through `DeleteScheduler`, and coordinating no-space error recovery across DB instances. It is a production boundary between DB version/file lifecycle code and filesystem capacity/deletion behavior.

## Important APIs, Types, and Functions

- Constructor/destructor/`Close()` initialize deletion scheduling, counters, mutex/condition variable state, and the background recovery thread lifetime.
- `OnAddFile()`, `OnAddFile(file_size)`, `OnDeleteFile()`, `OnMoveFile()`, and `OnUntrackFile()` maintain `tracked_files_` and `total_files_size_`.
- `SetMaxAllowedSpaceUsage()`, `IsMaxAllowedSpaceReached()`, and `IsMaxAllowedSpaceReachedIncludingCompactions()` enforce configured SST/blob space caps.
- `EnoughRoomForCompaction()` reserves approximate compaction input size as temporary headroom before a compaction starts.
- `OnCompactionCompletion()` releases compaction reservation after completion.
- `ReserveDiskBuffer()`, `StartErrorRecovery()`, `CancelErrorRecovery()`, and `ClearError()` implement no-space recovery polling across `ErrorHandler` instances.
- `ScheduleFileDeletion()`, `ScheduleUnaccountedFileDeletion()`, `WaitForEmptyTrash()`, `NewTrashBucket()`, and `WaitForEmptyTrashBucket()` delegate to `DeleteScheduler`.
- `NewSstFileManager()` overloads create the implementation and optionally schedule deletion of legacy trash-dir files.

## Control Flow

File tracking operations acquire `mu_` and call small internal helpers. `OnAddFile()` optionally queries file size through the filesystem, while the overload trusts a caller-supplied size. `OnMoveFile()` adds the new path with the old tracked size and then removes the old path. Delete and untrack are identical for accounting.

`EnoughRoomForCompaction()` sums all compaction input file sizes, rejects the compaction if tracked size plus existing reservation plus this compaction plus `compaction_buffer_size_` exceeds `max_allowed_space_`, and applies a stricter free-space check after a DB has seen a no-space soft error. In soft-error mode it calls `GetFreeSpace()` on a representative table filename and requires enough headroom for current reservations plus this compaction, and possibly the reserved disk buffer. On success it increments `cur_compactions_reserved_size_` and snapshots `free_space_trigger_`.

Error recovery starts when DB error handling reports a soft or hard no-space error. `StartErrorRecovery()` records the most severe relevant background error, queues the `ErrorHandler`, joins any previous recovery thread, and starts a new `port::Thread` running `ClearError()`. `ClearError()` loops while handlers remain: it checks free space against hard-error reserved buffer or soft-error trigger, invokes `RecoverFromBGError()` outside the mutex for the front handler, removes handlers that recovered, shut down, or escalated to fatal, waits between attempts, and clears `bg_err_` when the queue drains. `CancelErrorRecovery()` removes a handler from the queue or nulls `cur_instance_` if the thread is currently working on it.

## State and Persistence Behavior

The manager maintains in-memory state only: tracked file path-to-size map, total tracked size, configured max allowed space, compaction reserved bytes, deletion scheduler state, reserved disk buffer, free-space trigger, current background error, and queued `ErrorHandler` pointers. The durable effects are filesystem deletes/trash scheduling and DB error recovery attempts. Tracking state is rebuilt by DB instances through lifecycle callbacks; it is not itself persisted.

## Dependencies and Integration Points

This implementation depends on `DeleteScheduler`, `FileSystem`, `SystemClock`, `Logger`, `ErrorHandler`, compaction metadata (`Compaction`, `CompactionInputFiles`, `FileMetaData`), table filename helpers, `Status` severity/subcode semantics, RocksDB mutex/condition variable wrappers, and sync points. DBImpl and column-family code call it when SST/blob files are created, moved, deleted, untracked, or when compaction and no-space recovery decisions are needed.

## Risks and Edge Cases

Accounting correctness depends on all DB file lifecycle paths calling the matching add/delete/move/untrack methods exactly once. `OnMoveFile()` indexes `tracked_files_[old_path]`, which inserts a zero-size entry if the old path was missing before adding the new path; callers must only move tracked files. Compaction reservation is conservative and based on input sizes, so it can reject compactions even when output would be smaller. Soft-error recovery is intentionally per-SFM and can throttle compactions of a DB that has reported no-space while trying not to penalize unrelated DBs. `ClearError()` carefully releases the mutex before DB recovery callbacks, but lifetime safety relies on `ErrorHandler`'s recovery-in-progress coordination and `CancelErrorRecovery()` semantics.

## Test Signals

Signals include tracked size changes on add/delete/move, max-space rejection behavior with and without compaction reservations, reservation release after `OnCompactionCompletion()`, delete scheduler trash size and bucket behavior, no-space soft/hard recovery callbacks, cancellation while a handler is current, legacy trash cleanup during `NewSstFileManager()`, and sync-point-observable file lifecycle callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.h -->
# sources/storage-engines/rocksdb/file/sst_file_manager_impl.h

## Purpose

`sst_file_manager_impl.h` declares `SstFileManagerImpl`, the concrete `SstFileManager` used to track SST/blob disk usage, throttle deletes, enforce maximum allowed RocksDB space usage, reserve compaction headroom, and coordinate recovery after disk-full errors.

## Important APIs, Types, and Functions

- Public file lifecycle hooks: `OnAddFile`, `OnDeleteFile`, `OnMoveFile`, `OnUntrackFile`.
- Space-limit APIs overriding `SstFileManager`: `SetMaxAllowedSpaceUsage`, `GetTotalSize`, `GetTrackedFiles`, `IsMaxAllowedSpaceReached`, and `IsMaxAllowedSpaceReachedIncludingCompactions`.
- Compaction admission APIs: `SetCompactionBufferSize`, `EnoughRoomForCompaction`, `OnCompactionCompletion`, `GetCompactionsReservedSize`.
- Deletion APIs: `GetDeleteRateBytesPerSecond`, `SetDeleteRateBytesPerSecond`, `GetMaxTrashDBRatio`, `SetMaxTrashDBRatio`, `GetTotalTrashSize`, `ScheduleFileDeletion`, `ScheduleUnaccountedFileDeletion`, trash waiting/bucket APIs, and `delete_scheduler()`.
- Error recovery APIs: `ReserveDiskBuffer`, `StartErrorRecovery`, `CancelErrorRecovery`, and `Close`.
- Private helpers `OnAddFileImpl`, `OnDeleteFileImpl`, `ClearError`, and `CheckFreeSpace`.

## Control Flow

The header defines a thread-safe manager with one mutex protecting most accounting and recovery state. Public methods either mutate tracked-file accounting, delegate deletion to `DeleteScheduler`, adjust options, or participate in compaction/error recovery. `Close()` is part of the lifecycle contract and should be called before destruction to stop the background error-recovery thread.

## State and Persistence Behavior

Important state includes `total_files_size_`, `compaction_buffer_size_`, `cur_compactions_reserved_size_`, `tracked_files_`, `max_allowed_space_`, `delete_scheduler_`, recovery-thread closure state, `path_` for free-space probes, `bg_err_`, `reserved_disk_buffer_`, `free_space_trigger_`, the handler queue, and `cur_instance_`. This state is process-local bookkeeping around durable files; persistence of actual SST/blob files remains in the filesystem and DB manifest/version metadata.

## Dependencies and Integration Points

The class depends on `rocksdb/sst_file_manager.h`, `file/delete_scheduler.h`, compaction metadata declarations, `FileSystem`, `SystemClock`, `Logger`, and `ErrorHandler`. It is the internal implementation behind the public `NewSstFileManager` factory and integrates with DBImpl file lifecycle, compaction scheduling, and background error handling.

## Risks and Edge Cases

All public functions are intended to be thread-safe, so new state must join the mutex discipline. Error recovery stores raw `ErrorHandler*` values and must cooperate with DB shutdown. Exposing `delete_scheduler()` gives internal callers direct access to deletion machinery, which can bypass higher-level policy if misused. The class tracks only files reported to it; external filesystem changes or missed callbacks can make accounting approximate.

## Test Signals

Header-level contracts are validated by tests that instantiate `SstFileManager`, exercise file lifecycle hooks, query size maps, set delete rates and trash ratios, gate compactions, and simulate DB error recovery. Thread-safety tests should stress concurrent add/delete/query and close/recovery interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.cc -->
# sources/storage-engines/rocksdb/file/writable_file_writer.cc

## Purpose

`writable_file_writer.cc` implements `WritableFileWriter`, RocksDB's central wrapper around `FSWritableFile`. It handles buffered and direct writes, rate limiting, data verification checksum handoff, file checksum generation, flush/sync/range-sync/close semantics, direct-I/O padding/truncation, IO stats, histograms, and listener notifications. It is a critical write-path component for WALs, MANIFESTs, SSTs, blob files, and other durable outputs.

## Important APIs, Types, and Functions

- `Create()` validates direct-write buffer configuration, opens a writable file, and constructs the writer.
- `Append()` buffers or writes input data, updates file checksums, calls `PrepareWrite()`, maintains `filesize_`, and handles verification checksums.
- `Pad()` appends zero bytes through the buffer and checksum path.
- `Flush()` writes buffered data to the underlying file, calls `FSWritableFile::Flush`, and optionally issues `RangeSync()` according to `bytes_per_sync_`.
- `Close()` flushes, truncates/fsyncs direct-I/O files to logical size, closes the file, and finalizes file checksum generation.
- `Sync()` flushes then syncs/fsyncs buffered files when needed; `SyncWithoutFlush()` syncs only already-flushed bytes if the underlying file supports thread-safe sync.
- `WriteBuffered()`, `WriteBufferedWithChecksum()`, `WriteDirect()`, and `WriteDirectWithChecksum()` are the lower-level write engines.
- `RangeSync()`, `SyncInternal()`, `FinalizeIOOptions()`, `DecideRateLimiterPriority()`, and checksum helpers support the main operations.

## Control Flow

`Append()` rejects calls after a previous error, starts timing, finalizes IO priority from operation and file priorities, marks `pending_sync_`, updates the optional file checksum generator, and calls `PrepareWrite()` with the current logical size. It grows the internal buffer up to `writable_file_max_buffer_size` when that avoids a flush. For buffered I/O, it flushes existing data if the incoming data will not fit, then either accumulates data into the buffer or writes a large chunk directly to `WriteBuffered*`. For direct I/O, data always accumulates in `AlignedBuffer` and gets flushed through positional writes. With data verification and caller-provided crc32c, it preserves whole-buffer checksums so the filesystem can verify the exact byte range.

`Flush()` chooses the appropriate write engine based on direct I/O and checksum handoff, then calls the underlying file's `Flush()`. For buffered I/O with `bytes_per_sync_`, it range-syncs older data while deliberately avoiding the most recent 1 MiB and aligning sync ranges to 4 KiB.

`WriteBuffered()` loops under the rate limiter, calls `Append()` on the underlying file, optionally supplies `DataVerificationInfo`, emits listener callbacks, updates `flushed_size_`, and clears the buffer after success. `WriteBufferedWithChecksum()` first waits until the rate limiter has granted the whole buffer so one checksum covers one append. Direct writes pad to alignment, issue `PositionedAppend()` calls, update flushed bytes, then refit the unaligned tail back to the front of the buffer for a later rewrite. `Close()` flushes, truncates direct-I/O files to `filesize_`, fsyncs direct-I/O output after truncation, closes the underlying file, and finalizes the file checksum only on success.

## State and Persistence Behavior

The writer's state tracks logical size (`filesize_`), flushed physical size (`flushed_size_`), next aligned direct-write offset (`next_write_offset_`), buffered bytes, pending sync status, last range-sync offset, previous-error state, optional checksum generator, buffered crc32c checksum, and file temperature. Durable effects are appends, positioned appends, flushes, sync/fsync calls, range syncs, truncation, and close on the filesystem. After an error, `seen_error_` prevents further normal writes because the underlying file may have partially accepted data; callers can explicitly reset the error for relaxed-consistency cases.

## Dependencies and Integration Points

The implementation depends on `FSWritableFile`, `FileOptions`, `IOOptions`, `WriteOptions` conversion, `AlignedBuffer`, `RateLimiter`, `Statistics`, `StopWatch`, histograms, `IOSTATS`, `crc32c`, file checksum generators, `EventListener`, `FileOperationInfo`, thread-status test helpers, and sync points. It is used by RocksDB table builders, WAL/manifest writers, blob writers, and tests/fault-injection filesystems.

## Risks and Edge Cases

Direct I/O is the highest-risk area: writes must be aligned and positional, tails are padded and later rewritten, and `Close()` must truncate to logical size to hide padding. `flushed_size_` can include padded direct-I/O bytes while `filesize_` is logical data size, so callers must use the right metric. On underlying append failure the buffer is cleared to avoid duplicate data in later retries, which sacrifices transparent retry at this layer. Checksum handoff has two modes: per-chunk checksum calculation and whole-buffer checksum reuse; rate-limited writes with whole-buffer checksum intentionally wait for the full buffer. Listener callbacks receive inline statuses and offsets and must tolerate failures. `SyncWithoutFlush()` is only safe when `IsSyncThreadSafe()` is true.

## Test Signals

Signals include buffered append/flush/sync behavior, direct-I/O tail rewrite and close truncation, `bytes_per_sync_` range-sync offsets, file checksum finalization, data verification checksum handoff, prior-error blocking and injected-error messages, listener notification operation types and offsets, rate-limited write chunking, `GetFileSize()` vs `GetFlushedSize()`, and fault-injection tests ensuring no duplicate buffered data after append failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.h -->
# sources/storage-engines/rocksdb/file/writable_file_writer.h

## Purpose

`writable_file_writer.h` declares `WritableFileWriter`, RocksDB's internal write-path abstraction over `FSWritableFile`. The class gives higher layers one API for buffered/direct writes, rate limiting, flushing, syncing, file checksums, data verification, listener notifications, and error-state management.

## Important APIs, Types, and Functions

- The constructor wraps a unique `FSWritableFile`, applies `FileOptions`, attaches tracing, stats, listeners, checksum generator factory, verification flags, and optional initial file size.
- `static Create()` opens a new writable file through `FileSystem`.
- `static PrepareIOOptions()` converts public `WriteOptions` into lower-level `IOOptions`.
- Public operations: `Append`, `Pad`, `Flush`, `Close`, `Sync`, `SyncWithoutFlush`, `InvalidateCache`.
- Query/accessors: `file_name`, `GetFileSize`, `GetFlushedSize`, `writable_file`, `use_direct_io`, `BufferIsEmpty`, `IsClosed`, `GetFileChecksum`, `GetFileChecksumFuncName`, `seen_error`.
- Test/error hooks: `TEST_SetFileChecksumGenerator`, `reset_seen_error`, `set_seen_error`, `GetWriterHasPreviousErrorStatus`, and debug-only `seen_injected_error`.
- Private write engines and notification helpers cover buffered writes, direct writes, checksum handoff, range sync, sync internals, and IO option finalization.

## Control Flow

The header shows the intended lifecycle: construct/open, call `Append()`/`Pad()` repeatedly, `Flush()` and `Sync()` as durability policy requires, and `Close()` explicitly or via destructor. The destructor attempts `Close()` with an IO activity value adjusted for stress tests. All public write/sync methods consult `seen_error_`, so most failures make the writer fail-closed until a caller deliberately resets the flag.

## State and Persistence Behavior

Important state includes the wrapped file, aligned write buffer, maximum buffer size, logical/flushed sizes, direct-I/O offset, pending sync flag, last range-sync size, rate limiter, stats/histogram settings, event listeners, checksum generator finalization state, data-verification flags, buffered checksum, and temperature. The class tracks durable write progress so callers can reason about logical file length and flushed lower bounds, but the actual persistence is performed by the underlying filesystem object.

## Dependencies and Integration Points

The declaration depends on version edit definitions for file metadata constants, file-system tracing wrappers, thread-status utilities, file checksum APIs, listener APIs, rate limiter APIs, aligned buffers, sync points, and fault-injection filesystem helpers in debug builds. It is a shared low-level component for DB logging, table building, blob writing, manifest writes, and file-system integration tests.

## Risks and Edge Cases

`initial_file_size` allows wrapping reopened append targets; incorrect values would corrupt logical/flushed offset accounting. Direct writes require a nonzero max buffer size, asserted at construction and validated by `Create()`. Event listener notification helpers are private but numerous, so new file operations need matching listener/error notification to preserve observability. `reset_seen_error()` is explicitly for relaxed-consistency callers and can be unsafe if used after ambiguous partial writes.

## Test Signals

Tests should verify lifecycle idempotence around destructor/`Close()`, direct-write constructor validation, append-after-error behavior, checksum generator injection and finalization, sync-without-flush support checks, listener filtering and callbacks, `GetFlushedSize()` agreement with the underlying file, and debug injected-error reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/writable_file_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/folly.mk -->
# sources/storage-engines/rocksdb/folly.mk

## Purpose

`folly.mk` centralizes RocksDB's Makefile integration for Folly. It supports two modes: linking against a full Folly build (`USE_FOLLY=1`) or compiling a lightweight source-picked Folly variant (`USE_FOLLY_LITE=1`). It also defines checkout/build targets and cache helpers so CI can pin and build a known Folly revision.

## Important APIs, Types, and Functions

- `USE_FOLLY` and `USE_FOLLY_LITE` are mutually exclusive build modes.
- `FOLLY_PATH`, `BOOST_PATH`, `DBL_CONV_PATH`, `GFLAGS_PATH`, `GLOG_PATH`, `LIBEVENT_PATH`, `XZ_PATH`, `LIBSODIUM_PATH`, and `FMT_PATH` drive include/library discovery for full Folly builds.
- `PLATFORM_CCFLAGS`, `PLATFORM_CXXFLAGS`, and `PLATFORM_LDFLAGS` are augmented with include paths, defines, libraries, and rpaths.
- `FOLLY_COMMIT_HASH` pins public CI to a specific Folly revision.
- `restore_folly_getdeps_downloads` and `cache_folly_getdeps_downloads` are make macros for download cache reuse and fallback mirrors.
- `checkout_folly` clones/fetches Folly, resets to the pinned commit, applies local source patches, and fetches boost/fmt.
- `build_folly` clears the getdeps install root, restores downloads, runs getdeps build, and patches rpath for glog/gflags.

## Control Flow

When `USE_FOLLY=1`, the Makefile rejects simultaneous `USE_FOLLY_LITE=1`, discovers dependency paths relative to `FOLLY_PATH` if set, adds include flags with AIX-specific `-I` handling, links static Folly/dependencies plus debug or release variants of fmt/glog/gflags, and defines `USE_FOLLY`/`FOLLY_NO_CONFIG`.

When `USE_FOLLY_LITE=1`, it uses `third-party/folly` as source, optionally discovers boost and fmt source includes, adds Folly include flags and defines, and links `-lglog`. The `checkout_folly` target ensures the source tree is present and pinned, modifies two Folly files for RocksDB's CI compatibility, restores/fetches dependency downloads, and refreshes the cache. `build_folly` rebuilds via getdeps with flags matching RocksDB debug mode and compiler `-m*` flags.

## State and Persistence Behavior

This file mutates the working tree and `/tmp/rocksdb-getdeps-cache` when checkout/build targets run. It creates or updates `third-party/folly`, resets it to a pinned commit, patches source files in place, populates getdeps downloads/install directories, and can remove the previous getdeps install root before rebuild. Build variables affect later RocksDB compile/link commands but are not persisted except through generated/build outputs.

## Dependencies and Integration Points

It integrates with RocksDB's top-level Makefile and `make_config.mk`, Git, Python getdeps, pkg/build tooling, patchelf, fallback mirror script `build_tools/getdeps_fallback_mirror.py`, platform detection, and CI cache actions. It assumes Folly's getdeps directory layout and dependency naming conventions.

## Risks and Edge Cases

The full Folly path discovery uses shell `ls -d` patterns and can break if dependency directory names change or multiple matches produce ambiguous whitespace. `checkout_folly` runs `git reset --hard` inside `third-party/folly`, which is intentional but destructive to local Folly edits. Local Perl patches are brittle against upstream file changes. Debug/release library name differences and rpath handling are platform-sensitive. The file itself says the integration simulates Meta-internal Folly and is not validated for general use.

## Test Signals

Signals are successful `make checkout_folly`, `make build_folly`, RocksDB build with `USE_FOLLY=1`, RocksDB build with `USE_FOLLY_LITE=1`, cache hit/miss behavior when `folly.mk` changes, AIX include handling, debug/release link success, and runtime resolution of glog/gflags shared libraries after patchelf.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/folly.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/Makefile -->
# sources/storage-engines/rocksdb/fuzz/Makefile

## Purpose

`fuzz/Makefile` builds RocksDB's libFuzzer targets under either a local sanitizer environment or OSS-Fuzz. It wires protobuf/libprotobuf-mutator code generation, RocksDB include/library paths, sanitizer flags, and target-specific build rules for DB and SST fuzzers.

## Important APIs, Types, and Functions

- `ROOT_DIR` points at the RocksDB root and includes `make_config.mk`.
- `PROTOBUF_CFLAGS/LDFLAGS` and `PROTOBUF_MUTATOR_CFLAGS/LDFLAGS` come from `pkg-config`.
- `PROTO_IN` is `fuzz/proto`; `PROTO_OUT` is `fuzz/proto/gen`.
- `FUZZ_ENV=ossfuzz` switches from local `-fsanitize=address,fuzzer` flags to OSS-Fuzz-provided `CXXFLAGS` and `LIB_FUZZING_ENGINE`.
- `PROTOC_BIN` is configurable for `gen_proto`.
- Targets: `gen_proto`, `clean`, `db_fuzzer`, `db_map_fuzzer`, and `sst_file_writer_fuzzer`.

## Control Flow

For non-OSS-Fuzz builds the file sets `CC=$(CXX)`, adds ASan/libFuzzer flags, includes RocksDB root/include/proto output paths, links protobuf-mutator/protobuf and `-lrocksdb`. In OSS-Fuzz mode it respects externally supplied compiler and sanitizer flags while still adding generated proto and RocksDB includes. `gen_proto` creates the output directory and runs `protoc` over all proto inputs. The proto-based fuzzers depend on generated code and compile `proto/gen/db_operation.pb.cc` into the target.

## State and Persistence Behavior

The Makefile creates generated C++ protobuf files under `fuzz/proto/gen` and fuzzer binaries in the fuzz directory. `clean` removes the three fuzzer binaries and generated proto output. It does not modify source files outside generated artifacts.

## Dependencies and Integration Points

It depends on RocksDB's built `librocksdb`, `pkg-config`, protobuf, libprotobuf-mutator, libFuzzer-compatible compiler support, and `make_config.mk` platform flags. It integrates with OSS-Fuzz by consuming its standard environment variables and with local developer fuzzing via default sanitizer flags.

## Risks and Edge Cases

If RocksDB has not been built or `pkg-config` cannot find protobuf/libprotobuf-mutator, targets fail at compile/link time. The local mode hardcodes ASan plus libFuzzer, which may not suit all compiler setups. Generated proto paths are included as `-I$(PROTO_OUT)`, so stale generated files can mask proto changes unless `gen_proto` reruns. `clean` removes generated proto output wholesale.

## Test Signals

Signals include `make -C fuzz gen_proto`, successful builds of all three fuzzers in local mode, successful OSS-Fuzz environment builds, correct regeneration after proto edits, and fuzzer startup without missing RocksDB/protobuf symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_fuzzer.cc -->
# sources/storage-engines/rocksdb/fuzz/db_fuzzer.cc

## Purpose

`db_fuzzer.cc` is a byte-oriented libFuzzer harness that interprets input as a sequence of RocksDB API operations against a temporary DB. Its goal is sanitizer-driven discovery of memory safety, undefined behavior, and API-state bugs across basic DB operations, iteration, snapshots, column families, compaction, and reopen paths.

## Important APIs, Types, and Functions

- `OperationType` enumerates supported operations: put, get, delete, property read, iterator, snapshot, open/close, column family, compact range, seek-for-prev, and count.
- `LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)` is the libFuzzer entry point.
- It uses `FuzzedDataProvider` to consume random-length strings for keys, values, properties, and range bounds.
- RocksDB APIs exercised include `DB::Open`, `Put`, `Get`, `Delete`, `GetProperty`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `Close`, `CreateColumnFamily`, multi-CF `Open`, `DropColumnFamily`, `DestroyColumnFamilyHandle`, `CompactRange`, `SeekForPrev`, and `DestroyDB`.

## Control Flow

The harness opens `/tmp/testdb` with `create_if_missing=true`, then sets `max_iter` from the first input byte and loops over at most `size` operations. Each iteration maps the current byte to an `OperationType` and consumes additional strings from `FuzzedDataProvider` as needed. Some operations intentionally ignore returned statuses. The column-family case creates `new_cf`, closes/reopens the DB with both default and new column families, performs a put/get/drop on the second handle, destroys handles, and falls back to a normal reopen if multi-CF open fails. At the end it closes and destroys the DB.

## State and Persistence Behavior

The fuzzer creates durable temporary state under `/tmp/testdb` for each input and destroys it at the end. Reopen and column-family operations deliberately persist manifest/data state across closes within one fuzz iteration. Snapshot and iterator operations exercise in-memory references, but the snapshot case releases the snapshot before deleting the iterator, which is an aggressive lifetime pattern for sanitizer coverage.

## Dependencies and Integration Points

It depends on libFuzzer's `FuzzedDataProvider` and RocksDB public `DB` APIs. It is built by `fuzz/Makefile` and linked against RocksDB. It integrates broad public API state transitions rather than checking semantic equivalence.

## Risks and Edge Cases

The harness reads `data[0]` without first checking `size > 0`, so empty inputs can trigger an out-of-bounds read in the harness itself. It uses a fixed `/tmp/testdb`, which is problematic for parallel fuzzer processes or stale preexisting state. Several statuses and possibly uninitialized handles are not defensively checked, especially in the column-family branch after `CreateColumnFamily`. The snapshot branch releases a snapshot before iterator deletion, which may or may not match intended API lifetime but is useful as a stress case.

## Test Signals

Signals are sanitizer findings, crashes, hangs, leaks, and assertion failures from random API sequences. Useful harness-health checks include running with an empty input, parallel corpus execution, and detecting leftover `/tmp/testdb` after failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_fuzzer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_map_fuzzer.cc -->
# sources/storage-engines/rocksdb/fuzz/db_map_fuzzer.cc

## Purpose

`db_map_fuzzer.cc` is a protobuf-mutator fuzz harness that compares RocksDB's persisted key/value state against a `std::map` model after a generated sequence of point puts, deletes, and range deletes. Unlike `db_fuzzer.cc`, it checks semantic correctness by reopening the DB and iterating all keys.

## Important APIs, Types, and Functions

- A `PostProcessorRegistration<DBOperations>` normalizes generated `DELETE_RANGE` operations so begin is less than or equal to end according to `BytewiseComparator`.
- `DEFINE_PROTO_FUZZER(DBOperations& input)` is the libprotobuf-mutator entry point.
- The model is `std::map<std::string, std::string> kv`.
- RocksDB APIs exercised include `FileSystem::Default`, `FileExists`, `DB::Open`, `Put`, `Delete`, `DeleteRange`, `Close`, `NewIterator`, iterator seek/next/key/value, and `DestroyDB`.
- `CHECK_OK`, `CHECK_EQ`, and `CHECK_TRUE` macros abort on mismatch.

## Control Flow

The harness ignores empty operation lists, rejects a preexisting `/tmp/db_map_fuzzer_test` path, opens a new DB, and applies each proto operation. PUT updates both DB and map; DELETE removes from both; DELETE_RANGE deletes `[key, value)` in RocksDB and erases the same range in the map. MERGE is defined in the proto but skipped here. After closing and reopening, it iterates RocksDB from first key and compares every key/value pair to the map, then asserts the map is exhausted and destroys the DB.

## State and Persistence Behavior

Each fuzz input creates a temporary persistent DB, closes it, reopens it, validates recovered/manifest state through iteration, and destroys it. The model state is in-memory only. Range deletes are persisted as RocksDB tombstones but modeled as immediate map erasure under bytewise order.

## Dependencies and Integration Points

The harness depends on generated `db_operation.pb.h`, protobuf-mutator macros, RocksDB public DB and filesystem APIs, and `util.h` check macros. It integrates with the fuzz Makefile's proto generation and links with libprotobuf-mutator.

## Risks and Edge Cases

The fixed DB path prevents safe parallel execution and aborts if stale state exists. MERGE operations are silently ignored, which means generated MERGE inputs do not expand semantic coverage. The model assumes default bytewise comparator and default merge/compaction behavior. Range-delete normalization swaps local copies then writes them back, which is correct, but the proto comment says `[key, value]` while the implementation and RocksDB use `[begin, end)`.

## Test Signals

Primary signals are aborts from `CHECK_*` mismatches after reopen, sanitizer crashes, and stale-path aborts. Strong coverage includes mixed PUT/DELETE/DELETE_RANGE sequences, empty and equal range bounds, duplicate keys, keys with embedded nulls, and reopen after many tombstones.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/db_map_fuzzer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/proto/db_operation.proto -->
# sources/storage-engines/rocksdb/fuzz/proto/db_operation.proto

## Purpose

`db_operation.proto` defines the protobuf-mutator input schema shared by RocksDB fuzzers that generate DB-like operations. It gives fuzzers structured operation sequences instead of raw byte interpretation.

## Important APIs, Types, and Functions

- `syntax = "proto2"` enables required fields and proto2 semantics.
- `enum OpType` defines `PUT`, `MERGE`, `DELETE`, and `DELETE_RANGE`.
- `message DBOperation` has required `key`, optional `value`, and required `type`.
- `message DBOperations` contains repeated `DBOperation operations`.

## Control Flow

There is no runtime control flow in the proto itself. Protobuf-mutator generates `DBOperations`; individual fuzzers post-process and interpret the sequence. `value` is used as a value for PUT/MERGE and as the end bound for DELETE_RANGE, while DELETE ignores it.

## State and Persistence Behavior

The schema represents transient fuzz input. Persistence is determined by harnesses that apply operations to RocksDB and generated C++ code under `fuzz/proto/gen`.

## Dependencies and Integration Points

It integrates with `fuzz/Makefile`'s `gen_proto` target, generated `db_operation.pb.cc/.h`, `db_map_fuzzer.cc`, and `sst_file_writer_fuzzer.cc`. The operation enum must stay aligned with each fuzzer's switch statements and post-processors.

## Risks and Edge Cases

The comment says `[key, value]` is the range for DELETE_RANGE, while fuzzer code treats it as `[key, value)`, matching RocksDB's API. Required fields can constrain mutator behavior and cause parsing failures for malformed serialized inputs. Adding enum values requires every harness to handle or intentionally reject them.

## Test Signals

Signals include successful proto generation, fuzzer builds after schema changes, post-processor compatibility, and harness behavior for every enum value including future unknown/default cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/proto/db_operation.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc -->
# sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc

## Purpose

`sst_file_writer_fuzzer.cc` is a protobuf-mutator harness that drives `SstFileWriter` with sorted unique operations, opens the generated SST through the internal table reader path, verifies checksums, and checks internal keys and values. It targets table-builder/SST writer correctness, internal-key encoding, and table-reader compatibility.

## Important APIs, Types, and Functions

- A `PostProcessorRegistration<DBOperations>` normalizes range bounds, sorts operations by key, and removes duplicate keys to satisfy `SstFileWriter`'s sorted-unique key requirement.
- `NewTableReader()` mirrors `SstFileReader::Open`: gets file size, creates `RandomAccessFileReader`, builds `TableReaderOptions`, and calls the table factory.
- `ToValueType(OpType)` maps proto operations to RocksDB internal value types.
- `DEFINE_PROTO_FUZZER(DBOperations& input)` writes the SST and verifies it.
- APIs include `SstFileWriter::Open/Put/Merge/Delete/DeleteRange/Finish`, `TableReader::VerifyChecksum`, `TableReader::NewIterator`, `ParseInternalKey`, and filesystem test directory lookup.

## Control Flow

The post-processor first ensures each DELETE_RANGE has ordered bounds, then sorts all operations by user key and erases duplicate-key operations. The fuzzer gets a test directory, writes a fixed SST filename, constructs default `Options`, `EnvOptions`, and `ImmutableCFOptions`, opens an `SstFileWriter`, applies every operation, and finishes the file. It then opens the generated table with a `TableReader`, verifies full-file checksums, creates an internal iterator with filters skipped, and walks expected operations. DELETE_RANGE entries are skipped because this iterator path does not expose range tombstone entries. For other operations it parses the internal key, checks user key, sequence zero, value type, and value when applicable. Finally it removes the SST file.

## State and Persistence Behavior

The harness creates one SST file in the filesystem test directory and deletes it at the end. It does not create a DB. The SST contains sequence-zero external file entries and possibly range-deletion metadata. Persistent state under test is the table file's on-disk block/index/filter/checksum/internal-key representation.

## Dependencies and Integration Points

It depends on generated proto classes, protobuf-mutator, `SstFileWriter`, table reader/builder internals, default table factory, `RandomAccessFileReader`, internal key parsing, comparators, and `util.h` check macros. It exercises public external-SST writing and internal table-reader validation in one harness.

## Risks and Edge Cases

The fixed filename in the test directory can collide under parallel fuzzing. Duplicate-key erasure keeps the first operation after sort, which may reduce coverage of overwrite-like cases but is required by writer ordering constraints. DELETE_RANGE output is only indirectly covered by `Finish()` and checksum verification because normal internal iteration skips range tombstones. `TableReaderOptions` passes a null compression manager and default options, so custom compression paths are not covered.

## Test Signals

Signals include aborts from writer/table status failures, checksum verification failures, internal-key parse errors, key/type/value mismatches, sanitizer findings, and leftover SST files after crashes. Good corpora should cover all operation types, empty keys/values, adjacent range bounds, and large value payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/sst_file_writer_fuzzer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/util.h -->
# sources/storage-engines/rocksdb/fuzz/util.h

## Purpose

`fuzz/util.h` provides small abort-on-failure assertion macros used by RocksDB fuzz harnesses. They keep harness code compact while converting semantic mismatches or bad statuses into fuzzer-detectable crashes.

## Important APIs, Types, and Functions

- `CHECK_OK(expression)` evaluates a RocksDB-style status expression, prints `ToString()` on failure, and aborts.
- `CHECK_EQ(a, b)` compares two expressions with `!=`, prints both expression names and values, and aborts on mismatch.
- `CHECK_TRUE(cond)` aborts when a condition is false.

## Control Flow

Each macro is inline preprocessor control flow. `CHECK_OK` uses a `do { ... } while (0)` wrapper and stores the evaluated status once. `CHECK_EQ` and `CHECK_TRUE` expand to simple `if` statements that print to `std::cerr` then abort.

## State and Persistence Behavior

The macros have no persistent state. Their side effects are diagnostic writes to stderr and process aborts, which libFuzzer treats as findings.

## Dependencies and Integration Points

They assume included code has access to `std::cerr`, `std::endl`, and `abort()`, and that status objects expose `ok()` and `ToString()`. They are used by proto fuzzers such as `db_map_fuzzer.cc` and `sst_file_writer_fuzzer.cc`.

## Risks and Edge Cases

`CHECK_EQ` evaluates `a` and `b` more than once when the comparison fails because it also prints them, so arguments should be side-effect-free. The macros are intentionally fatal and unsuitable for tests that need cleanup or multiple failure aggregation. Missing includes are tolerated only because current users include iostream/cstdlib indirectly or directly.

## Test Signals

Signals are straightforward: bad statuses and mismatches abort with useful diagnostics, while success paths add minimal overhead. Harness review should ensure macro arguments are side-effect-free.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/githooks/pre-push -->
# sources/storage-engines/rocksdb/githooks/pre-push

## Purpose

`githooks/pre-push` is a developer-side Git hook that blocks pushes on two common issues: untracked source files inside tracked directories and formatting failures from `make check-format`. It is intended to catch local mistakes before code reaches CI.

## Important APIs, Types, and Functions

- Bash with `set -e`.
- TTY/automation gate: exits unless stdout is a terminal or `ROCKSDB_FORMAT_HOOK` is set.
- `git ls-files --others --exclude-standard` finds untracked files.
- `grep -E '\.(cc|cpp|c|h|hpp|java|py|mk|sh)$'` limits suspects to source-like extensions.
- A loop checks whether the top-level directory is tracked before reporting the untracked file.
- `make check-format` enforces formatting.
- `FAILED` accumulates whether any check failed and becomes the exit code.

## Control Flow

The hook first skips non-interactive pushes unless explicitly enabled. It gathers suspect untracked files outside `third-party/` whose top-level directory is already tracked, prints a blocking message if any are found, and sets `FAILED=1`. It then always runs `make check-format`; a failure prints remediation guidance and sets `FAILED=1`, while success prints a clean message. The script exits with the accumulated status.

## State and Persistence Behavior

The hook does not modify repository state. It reads Git index/worktree state and runs the format checker, which should be read-only. It can prevent a push by exiting nonzero.

## Dependencies and Integration Points

It depends on Git, grep, sed, head, make, and the RocksDB `check-format` target. Comments note it becomes active via `make all` / `make check` setting `core.hooksPath`. It integrates with developer pushes and can be bypassed with `git push --no-verify`.

## Risks and Edge Cases

Because `set -e` and pipelines are used without `pipefail`, failures inside some pipeline elements may not behave as expected, while `grep` no-match behavior in command substitution is usually tolerated by the assignment. Filenames with unusual newlines are not handled robustly. The TTY gate means CI/automated pushes skip the hook unless `ROCKSDB_FORMAT_HOOK` is set. Running `make check-format` on every interactive push can be slow but gives strong local signal.

## Test Signals

Signals include hook exit zero with clean tree/format, nonzero with untracked source files in tracked directories, ignoring `third-party` untracked files, nonzero on format failures, skip behavior in non-TTY contexts, and forced execution via `ROCKSDB_FORMAT_HOOK=1`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/githooks/pre-push -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_cache.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_cache.h

## Purpose

`advanced_cache.h` declares RocksDB's expert cache customization API. It defines the abstract `Cache` contract used by block cache implementations, secondary cache promotion/demotion callbacks, reference-counted handles, asynchronous lookup hooks, cache wrappers, and memory allocator integration. It is intentionally unstable compared with simpler public cache factory APIs.

## Important APIs, Types, and Functions

- `Cache` derives from `Customizable` and exposes opaque `Handle`, `ObjectPtr`, and `CreateContext` types.
- `Cache::Priority` defines `HIGH`, `LOW`, and `BOTTOM` eviction priority classes.
- `CacheItemHelper` stores C-style callbacks: deleter, size, save-to, create-from-secondary, entry role, and a no-secondary-compatible helper.
- Core cache operations: `Insert`, `CreateStandalone`, `Lookup`, `BasicLookup`, `Ref`, `Release`, `Value`, `Erase`, `NewId`, capacity/strict-limit controls, usage/pinned/charge queries, helper query, `EraseUnRefEntries`.
- Introspection/walking APIs: `ApplyToAllEntries`, `ApplyToHandle`, occupancy/address-count queries, printable options, `ReportProblems`, `GetHashSeed`.
- Secondary-cache capacity/pinned queries default to `NotSupported`.
- Experimental async APIs: `AsyncLookupHandle`, `StartAsyncLookup`, `Wait`, `WaitAll`, release-with-usefulness, and eviction callback.
- `CacheWrapper` forwards operations to a wrapped `Cache` and is the preferred base for instrumentation/customization.
- `kNoopCacheItemHelper` is an extern helper for entries needing no cleanup.

## Control Flow

The header defines contracts rather than implementation flow. Insertions take ownership of objects only on OK status and may attempt secondary-cache insertion when helper callbacks support it. Lookups first query primary cache and may query secondary cache when helper/create context are supplied. Returned handles must be released exactly once unless ownership is transferred through documented APIs. Async lookup handles are populated by callers, passed to `StartAsyncLookup()`, waited on with `Wait()`/`WaitAll()` when pending, and then consumed through `Result()`.

`CacheWrapper` forwards almost every virtual call to `target_`, including async methods and problem reporting. `ApplyToHandle()` unwraps a wrapper cache pointer before forwarding to the target so callbacks see target-compatible handles.

## State and Persistence Behavior

Cache implementations own in-memory cache entries and optionally coordinate with secondary caches that can persist serialized objects across process or system restarts. The API makes key repeatability and global uniqueness a caller responsibility when secondary caches are shared. Refcounts and handles define object lifetime. `DisownData()` deliberately leaks data during process shutdown for faster teardown and makes later cache use invalid.

## Dependencies and Integration Points

The header depends on `rocksdb/cache.h`, compression types, memory allocator APIs, options/config customization, slices, status, and cache entry roles. It integrates with block/table cache code, compressed and tiered secondary caches, memory reservation helpers, table readers, blob cache users, and custom cache implementations.

## Risks and Edge Cases

This is a sharp API. Callback exceptions are explicitly forbidden because RocksDB is not exception-safe. `CacheItemHelper` instances must outlive the cache and cached entries. Objects compatible with secondary cache cannot be null because null has sentinel meaning. Handle lifetime rules are strict: release-after-release, value access after release, or destroying a pending async handle are undefined. Secondary-cache create callbacks must copy input data and clean up after failed creation. Wrapper authors must override new virtual methods when the base `Cache` API grows, as the comment warns.

## Test Signals

Signals include cache insert/lookup/release ownership behavior, strict capacity failures, standalone charge behavior, deleter invocation, secondary-cache save/promote paths, async pending/ready/wait flows, wrapper forwarding correctness, apply-to-all iteration under concurrency, eviction callback ownership transfer, pinned usage accounting, and problem reporting from concrete caches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_compression.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_compression.h

## Purpose

`advanced_compression.h` declares RocksDB's experimental advanced compression customization API. It separates compression strategy (`Compressor`), decompression schema (`Decompressor`), and manager/factory compatibility (`CompressionManager`), with explicit support for dictionaries, working areas, custom compression type schemas, and wrapper composition.

## Important APIs, Types, and Functions

- `Compressor` defines dictionary guidance/config variants (`DictDisabled`, `DictSampling`, `DictPreDefined`, `DictSamples`, `DictConfig`, `DictConfigArgs`), `WorkingArea`, `ManagedWorkingArea`, cloning/specialization, compression, preferred type, recommended parallelism, serialized dictionary access, and optimized decompressor access.
- `Decompressor` defines working areas, dictionary cloning through `MaybeCloneForDict`, owned-memory reporting, `Args`, `ExtractUncompressedSize`, and `DecompressBlock`.
- `CompressionManager` derives from `Customizable` and `enable_shared_from_this`, exposes `CompatibilityName`, compatibility lookup, string creation, supported type checks, compression-type naming, compressor creation for SST/generic use, and decompressor selection optimized by type set.
- `CompressorWrapper`, `DecompressorWrapper`, and `CompressionManagerWrapper` forward to wrapped implementations for instrumentation or policy layering.
- Factories expose `GetBuiltinV2CompressionManager()`, `CreateAutoSkipCompressionManager()`, and `CreateCostAwareCompressionManager()`.

## Control Flow

A write path asks a `CompressionManager` for a `Compressor` based on options and preferred `CompressionType`. The compressor may recommend dictionary handling for a block role through `GetDictGuidance()`. The caller can collect samples or pass a predefined dictionary into `MaybeCloneSpecialized()`/`CloneMaybeSpecialized()`, then call `CompressBlock()` repeatedly, optionally with a per-thread working area. The compressor returns both bytes and the compression type that must later guide decompression; `kNoCompression` with OK status means compression was declined rather than failed.

A read path gets a compatible `Decompressor` from a manager, optionally optimized for expected types or cloned for a serialized dictionary. It calls `ExtractUncompressedSize()` to parse/strip size metadata and then `DecompressBlock()` into caller-allocated output. Compatibility is mediated by `CompressionManager::CompatibilityName()` so persisted data can be decoded by functionally equivalent managers.

## State and Persistence Behavior

Compression choices become durable because SST/block data stores compressed bytes, compression types, and possibly dictionary blocks. Compatibility names and compression-type mappings must therefore remain stable: expanding support is acceptable, but changing the mapping from type/dictionary/data to output would risk corruption. Compressors for data files are expected to be per-file so strategy can be reconsidered for each file; decompressors without dictionaries can be shared, while dictionary-specific decompressors often reference externally managed dictionary bytes and must not outlive them.

## Dependencies and Integration Points

The API depends on compression type definitions, cache entry roles, data-structure `ManagedPtr`, `CompressionOptions`, `FilterBuildingContext`, and RocksDB customization/config machinery. It integrates with table builders/readers, block compression/decompression, dictionary training, compression manager registry/string creation, and wrapper-based strategy layers.

## Risks and Edge Cases

The file repeatedly warns that exceptions must not escape overridden functions. Dictionary lifetimes are subtle: `MaybeCloneForDict()` clones may reference the supplied `Slice`, so the caller must manage the raw dictionary bytes. `CompressionType` is part of the persisted schema; custom managers must not repurpose types incompatibly under the same compatibility name. `CompressBlock()` OK with `kNoCompression` is not a failure, and callers must correctly fall back to uncompressed data. Working areas are single-thread use even when compressors/decompressors are generally thread-safe.

## Test Signals

Signals include round-trip compression/decompression for every supported type, compatibility lookup by name, dictionary sampling/predefined specialization, serialized dictionary persistence, decompressor clone lifetime tests, working-area reuse and release, wrapper forwarding, `kNoCompression` bypass semantics, corrupt compressed data rejection in `ExtractUncompressedSize()`/`DecompressBlock()`, and SST read/write compatibility across manager instances.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_compression.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_iterator.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_iterator.h

## Purpose

`advanced_iterator.h` declares small advanced iterator result types used by lower-level table iterators to communicate bound-check and lazy-value state to RocksDB iterator code. It supports optimized `NextAndGetResult()`-style paths without forcing immediate value materialization.

## Important APIs, Types, and Functions

- `enum class IterBoundCheck : char` has `kUnknown`, `kOutOfBound`, and `kInbound`.
- `struct IterateResult` contains `Slice key`, `IterBoundCheck bound_check_result`, and `bool value_prepared`.

## Control Flow

The header contains no executable flow. A table iterator returns an `IterateResult` after advancing. If it remains valid, it should set `bound_check_result` to `kInbound`; if it becomes invalid because the next key is outside an upper/lower bound, it can report `kOutOfBound`; otherwise EOF/unknown invalidation remains `kUnknown`. If `value_prepared` is false, higher iterator layers must call `PrepareValue()` before reading `value()`.

## State and Persistence Behavior

`IterateResult::key` is a borrowed `Slice` whose lifetime is guaranteed only until the next `Next()` or `NextAndGetResult()` call. The struct carries transient iterator state only and has no persistence behavior.

## Dependencies and Integration Points

It depends only on `rocksdb/slice.h` and is consumed by advanced/table iterator implementations that can separate key movement from value preparation. It integrates with iterator bound checking and lazy value materialization in table readers.

## Risks and Edge Cases

Misreporting `value_prepared` can cause callers to read an unmaterialized value or redundantly prepare one. Misreporting `kOutOfBound` versus `kUnknown` can affect upper-layer iterator control flow and performance. The borrowed key lifetime is short and must not be stored by callers beyond the next iterator movement.

## Test Signals

Signals include iterator tests for `NextAndGetResult()` across valid keys, EOF, bound exits, and lazy value paths where `PrepareValue()` is required exactly before `value()` access.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_iterator.h -->
