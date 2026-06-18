# subset-b-008635 Research

Work item: `subset-b-008635`

Scope: RocksDB environment file-system tracing, POSIX filesystem adapters, on-demand/remap/read-only wrappers, and POSIX I/O tests under `sources/storage-engines/rocksdb/env/`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/file_system_tracer.cc -->
# sources/storage-engines/rocksdb/env/file_system_tracer.cc

## Purpose
Implements the tracing wrappers declared in `file_system_tracer.h`. Each overridden filesystem or file operation delegates to the wrapped implementation, measures elapsed nanoseconds with `StopWatchNano`, creates an `IOTraceRecord`, and writes it through `IOTracer`. The implementation is intentionally transparent: it does not change I/O semantics, only observes status, latency, basename, length, offset, or file size where available.

## Important APIs and Functions
- `FileSystemTracingWrapper::{NewSequentialFile,NewRandomAccessFile,NewWritableFile,ReopenWritableFile,ReuseWritableFile,NewRandomRWFile,NewDirectory,GetChildren,DeleteFile,CreateDir,CreateDirIfMissing,DeleteDir,GetFileSize,Truncate}` trace top-level `FileSystem` operations.
- `FSSequentialFileTracingWrapper::{Read,PositionedRead,InvalidateCache}` traces sequential file data paths and cache invalidation.
- `FSRandomAccessFileTracingWrapper::{Read,MultiRead,Prefetch,InvalidateCache,ReadAsync,ReadAsyncCallback}` traces random reads, batched reads, prefetch, cache invalidation, and async completions.
- `FSWritableFileTracingWrapper::{Append,PositionedAppend,Truncate,Close,GetFileSize,InvalidateCache}` traces write-side operations.
- `FSRandomRWFileTracingWrapper::{Write,Read,Flush,Close,Sync,Fsync}` traces read/write file operations.

## Control Flow
Most methods follow the same sequence: start a timer, call `target()->...`, compute elapsed time, encode fields in `io_op_data`, build an `IOTraceRecord`, call `io_tracer_->WriteIOOp`, then return the original status or result. Data operations set `kIOLen` and/or `kIOOffset`; file-size operations set `kIOFileSize`. `MultiRead` records one trace row per request using each request's individual status. `ReadAsync` allocates callback state, swaps in a wrapper callback, and records the operation only when the underlying async read invokes `ReadAsyncCallback`.

## State and Persistence
The file stores no persistent state. Runtime state consists of wrapper members inherited from the header, per-call timers, and async callback heap state. Trace persistence is delegated to `IOTracer`, so this layer depends on the tracer's lifetime and output policy. Async callback info is deleted after callback execution, and is also deleted if the underlying `ReadAsync` submission immediately fails.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`, `rocksdb/system_clock.h`, `rocksdb/trace_record.h`, and `trace_replay/io_tracer.h`. It integrates with RocksDB's filesystem abstraction through wrapper classes and with replay/diagnostics through `IOTraceRecord` and `IOTracer::WriteIOOp`. Debug context is forwarded to both real I/O and trace writing where applicable.

## Risks and Edge Cases
- All implementation methods dereference `io_tracer_` unconditionally; callers must only route through tracing wrappers when a tracer exists and tracing is enabled.
- Several records use requested length (`n`) while others use returned length (`result->size()`), so analysis consumers must understand the per-operation encoding.
- Async tracing lifetime depends on the underlying implementation eventually invoking the callback after accepting the request. If an implementation accepts and later drops a callback, the wrapper leaks callback info and loses a trace event.
- Basename extraction uses `find_last_of("/\\") + 1`; paths without separators produce the full string, which is fine, but trace output intentionally omits directory context.

## Test Signals
No direct tests in this group target `file_system_tracer.cc`. Indirect coverage comes from RocksDB I/O tracing and replay tests elsewhere. Risk-sensitive paths worth testing are async failure cleanup, `MultiRead` per-request status recording, and null/disabled tracer routing through `FileSystemPtr` and file pointer wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/file_system_tracer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/file_system_tracer.h -->
# sources/storage-engines/rocksdb/env/file_system_tracer.h

## Purpose
Declares RocksDB filesystem/file wrappers that add binary I/O tracing around selected `FileSystem`, `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, and `FSRandomRWFile` operations. It also declares pointer adapters that choose the tracing wrapper only when `IOTracer::is_tracing_enabled()` is true, avoiding wrapper overhead in the disabled case.

## Important APIs and Types
- `FileSystemTracingWrapper : FileSystemWrapper` wraps a full `FileSystem` and overrides selected creation, directory, deletion, size, and truncate calls.
- `FileSystemPtr` holds both the base `FileSystem` and a tracing wrapper; `operator->()` and `get()` choose between them dynamically.
- `FSSequentialFileTracingWrapper`, `FSRandomAccessFileTracingWrapper`, `FSWritableFileTracingWrapper`, and `FSRandomRWFileTracingWrapper` own/wrap underlying file objects and override trace-worthy methods.
- `FSSequentialFilePtr`, `FSRandomAccessFilePtr`, `FSWritableFilePtr`, and `FSRandomRWFilePtr` provide dynamic dispatch between the tracing wrapper and the raw target.
- `FSRandomAccessFileTracingWrapper::ReadAsyncCallbackInfo` stores callback, callback arg, start time, and file operation name for async completion tracing.

## Control Flow
Construction captures the underlying object, the shared tracer, a `SystemClock` pointer, and usually the basename of the file. Pointer adapter access checks `io_tracer_ && io_tracer_->is_tracing_enabled()` on every access. If enabled, callers operate through the tracing wrapper; otherwise they operate directly on `target()`. Writable pointers own the wrapper via `unique_ptr` and expose a `reset()` method because writable file lifetime is often explicitly cleared.

## State and Persistence
All state is in-memory. The wrappers retain `shared_ptr<IOTracer>`, so a tracer stays alive while wrappers exist. File wrappers keep only basename strings, not full paths. No durable data is written by the header itself; durable trace output is produced by the `.cc` implementation through `IOTracer`.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`, `rocksdb/system_clock.h`, and `trace_replay/io_tracer.h`. These wrappers integrate with RocksDB environments that need I/O trace capture without replacing the underlying storage engine. They rely on wrapper base classes such as `FileSystemWrapper`, `FSSequentialFileOwnerWrapper`, `FSRandomAccessFileOwnerWrapper`, `FSWritableFileOwnerWrapper`, and `FSRandomRWFileOwnerWrapper`.

## Risks and Edge Cases
- Pointer adapters return raw pointers into wrapper-owned objects; users must not outlive the owning adapter.
- The enabled/disabled choice is dynamic, so the same `FileSystemPtr` or file pointer can expose different virtual dispatch targets over time if tracing is toggled.
- `FSWritableFilePtr::get()` can return `nullptr` after `reset()`, unlike the other pointer wrappers.
- Because only basenames are stored, trace consumers cannot distinguish same-named files in different directories without external context.

## Test Signals
This header has no local unit test in the listed files. Useful tests would assert disabled-mode bypass, enabled-mode wrapper routing, writable pointer reset behavior, and async callback state cleanup. Integration tests should verify trace records are emitted for all declared overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/file_system_tracer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_on_demand.cc -->
# sources/storage-engines/rocksdb/env/fs_on_demand.cc

## Purpose
Implements an on-demand filesystem view for read-only/follower-style RocksDB use. It maps a local destination path to a remote source path. Table files are hard-linked into the local directory when first needed, while appendable or rename-sensitive metadata files such as WAL, MANIFEST, CURRENT, IDENTITY, and OPTIONS are read in place from the remote directory.

## Important APIs and Functions
- `OnDemandFileSystem::CheckPathAndAdjust` rewrites a path prefix from local to remote or remote to local.
- `LookupFileType` parses RocksDB filenames with `ParseFileName`.
- `NewSequentialFile` supports WAL, descriptor, CURRENT, IDENTITY, and OPTIONS files; descriptor files are wrapped in `OnDemandSequentialFile`.
- `NewRandomAccessFile`, `FileExists`, and `GetFileSize` link remote table files locally before opening or sizing them.
- `GetChildren` and `GetChildrenFileAttributes` merge local and remote directory listings.
- `OnDemandSequentialFile::{Read,Skip,use_direct_io,GetRequiredBufferAlignment,GetTemperature}` delegates to the active sequential file while tracking EOF and offset.
- `NewOnDemandFileSystem` constructs the wrapper.

## Control Flow
Operations first validate the RocksDB file type. For local-path inputs, `CheckPathAndAdjust(local_path_, remote_path_, path)` creates the remote equivalent. Directory caches for remote paths are discarded before remote lookups. SST random-access reads check the local file, hard-link from remote on not-found/path-not-found, then open locally. Directory listing reads both sides, rewrites remote names to local names, sorts, and merges with `std::set_union`. `OnDemandSequentialFile::Read` reopens and skips to the saved offset after EOF before retrying reads so distributed filesystems can reveal appended data.

## State and Persistence
Persistent effects are hard links created from remote SSTs to local paths and local info LOG writes. The wrapper stores immutable `remote_path_` and `local_path_`. `OnDemandSequentialFile` stores the current `file_`, `path_`, `file_opts_`, `eof_`, and `offset_`; it reopens the remote file after EOF and advances using `Skip(offset_)`.

## Dependencies and Integration Points
Depends on `file/filename.h` for RocksDB file classification, `rocksdb/types.h`, `rocksdb/file_system.h`, and the wrapped `FileSystem` for all actual I/O. It integrates with read-only DB open/recovery flows that list files, replay manifests, verify SST existence, and read metadata files that can grow remotely.

## Risks and Edge Cases
- `LookupFileType` uses `name.substr(found)` where `found` can be `npos` if the path has no slash; that can throw instead of returning unsupported.
- `CheckPathAndAdjust` performs prefix replacement without a path-component boundary check, so paths like `/local_db2/...` can match `/local_db`.
- Hard linking requires same filesystem support; `LinkFile` failures propagate and can prevent table reads.
- `NewWritableFile` permits only info LOG files and rejects writing if the remote equivalent exists; typo in the error text does not affect behavior.
- `OnDemandSequentialFile::Read` calls `fs_->NewSequentialFile(path_, ...)`, which re-enters file-type and path adjustment logic; this is intentional but recursion-sensitive if wrapper rules change.

## Test Signals
No local tests are listed for `fs_on_demand.cc`. High-value tests would cover SST link-on-existence-check, merged listings with duplicate names, descriptor EOF/reopen behavior, unsupported file types, no-slash paths, and hard-link failure propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_on_demand.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_on_demand.h -->
# sources/storage-engines/rocksdb/env/fs_on_demand.h

## Purpose
Declares `OnDemandFileSystem`, a `FileSystemWrapper` that presents a local RocksDB directory backed by a remote/source directory, linking immutable table files on demand and reading mutable metadata remotely. Also declares `OnDemandSequentialFile`, which reopens appendable remote sequential files after EOF.

## Important APIs and Types
- `OnDemandFileSystem` overrides sequential/random/writable file creation, directory creation, existence, children listing, attributes listing, and file-size lookup.
- `ReuseWritableFile` is explicitly unsupported.
- Private helpers `CheckPathAndAdjust` and `LookupFileType` drive path mapping and file-type policy.
- `OnDemandSequentialFile : FSSequentialFile` wraps a sequential file and overrides `Read`, `Skip`, direct-I/O metadata, `InvalidateCache`, `PositionedRead`, and `GetTemperature`.
- `NewOnDemandFileSystem` is the public factory.

## Control Flow
The header establishes a policy split: appendable/renameable RocksDB files are read from remote storage; SST/table files are linked locally; writable creation is only expected for info logs. `OnDemandSequentialFile` tracks `eof_` and `offset_`; after a short read marks EOF, the next read can reopen and skip back to the last offset.

## State and Persistence
`OnDemandFileSystem` stores immutable remote and local root strings. `OnDemandSequentialFile` owns the current inner file and stores a non-owning pointer to its `OnDemandFileSystem`, copied `FileOptions`, remote path, EOF flag, and logical offset. Persistent changes are performed by the `.cc` implementation through link and write operations on the target filesystem.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h` and RocksDB file type conventions. It integrates with read-only or follower DB workflows where a local directory should lazily materialize immutable SSTs while reading mutable manifest/current/log state remotely.

## Risks and Edge Cases
- The sequential wrapper stores a raw pointer to `OnDemandFileSystem`; it assumes the filesystem wrapper outlives any open file.
- `InvalidateCache` and `PositionedRead` are unsupported on `OnDemandSequentialFile`, which may surprise generic sequential-file users that expect positioned reads.
- The design comment notes future mirroring of read-in-place files is not implemented, so local diagnostic directories may be incomplete.

## Test Signals
No direct tests are present. Header-level behavior should be validated through DB open/recovery scenarios plus focused filesystem tests for unsupported APIs and file lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_on_demand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_posix.cc -->
# sources/storage-engines/rocksdb/env/fs_posix.cc

## Purpose
Implements RocksDB's default non-Windows `FileSystem` on top of POSIX APIs. It creates the concrete file classes from `io_posix.{h,cc}`, implements metadata operations, locks, directory operations, direct-I/O/mmap/io_uring feature selection, path registration for logical block-size caching, and registers the `posix://` filesystem factory.

## Important APIs and Types
- Anonymous `PosixFileSystem : FileSystem` implements `NewSequentialFile`, `NewRandomAccessFile`, `OpenWritableFile`, `NewWritableFile`, `ReopenWritableFile`, `ReuseWritableFile`, `NewRandomRWFile`, `NewMemoryMappedFileBuffer`, `NewDirectory`, and metadata operations.
- `PosixFileLock` and `LockOrUnlock` implement process-level lock handling with a process-local `locked_files` map.
- `OptimizeForLogWrite`, `OptimizeForManifestWrite`, and `OptimizeForCompactionTableRead` adjust `FileOptions`.
- `RegisterDbPaths`/`UnregisterDbPaths` manage Linux logical block-size cache references.
- `Poll`, `AbortIO`, and `SupportedOps` expose optional io_uring async I/O support.
- `FileSystem::Default()` returns a singleton `PosixFileSystem`; object registry adds a `posix://` factory.

## Control Flow
File-open methods build POSIX flags from `FileOptions`, retry `open` on `EINTR`, set close-on-exec, then instantiate a matching `io_posix` class. Direct reads/writes use `O_DIRECT` except on platform-specific alternatives; macOS uses `F_NOCACHE`, Solaris can call `directio`. mmap reads map the full opened file; mmap writes are disabled once if the backing filesystem does not support fast allocation. `ReuseWritableFile` opens the old file, renames it into the target name, and wraps the already-open descriptor. Metadata operations map directly to `access`, `opendir/readdir/closedir`, `unlink`, `mkdir`, `rmdir`, `stat`, `rename`, `link`, `statvfs`, `open/fstat`, and related POSIX calls. Async `Poll` waits for io_uring CQEs and finalizes matching handles; `AbortIO` submits cancel SQEs and waits for original plus cancel completions for aborted handles.

## State and Persistence
Persistent effects include file creation/truncation, renames, links, deletes, directory creation/removal, advisory locks, mmap writes, preallocation, and syncs. Runtime process state includes `locked_files`, `forceMmapOff_`, `page_size_`, `allow_non_owner_access_`, optional thread-local io_uring rings, and the static Linux `LogicalBlockSizeCache`. The default filesystem singleton persists for process lifetime.

## Dependencies and Integration Points
Depends on `env/io_posix.h` classes, `monitoring/iostats_context_imp.h`, RocksDB options, `ObjectLibrary`, sync points, thread-local helpers, and many POSIX/kernel headers. It is the primary integration point between RocksDB's abstract `FileSystem` API and platform storage. It also plugs into the object registry for URI-based construction.

## Risks and Edge Cases
- `GetAbsolutePath` returns the current working directory for any relative DB path without appending the relative path; callers expecting a full absolute path must account for this behavior.
- `FileExists` maps several access errors, including `EACCES`, to `NotFound`, which can hide permission problems behind existence checks.
- `OpenWritableFile` with reopen uses `O_CREAT | O_APPEND` without `O_WRONLY` in the non-direct/non-mmap path until the later branch adds only for alternatives; this relies on platform flag behavior and deserves scrutiny.
- Locking must maintain the process-local map before opening because POSIX locks are per-process; incorrect removal would release locks unexpectedly.
- Async io_uring support is gated by compile-time support, a weak `RocksDbIOUringEnable()` hook, constructor probing, and per-thread initialization. Any ring mismatch returns generic `IOError("")` in some paths.
- mmap write support is disabled globally after a one-time filesystem probe on the default filesystem.

## Test Signals
`io_posix_test.cc` indirectly exercises the default filesystem for writable truncate/append seek behavior and directory fsync behavior through `FileSystem::Default()`. Other RocksDB env tests likely cover metadata and locking. Important gaps for this file are `ReuseWritableFile`, `GetAbsolutePath`, URI factory construction, io_uring `Poll`/`AbortIO`, direct-I/O flag selection, and logical block-size registration lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_posix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_readonly.h -->
# sources/storage-engines/rocksdb/env/fs_readonly.h

## Purpose
Declares `ReadOnlyFileSystem`, a simple `FileSystemWrapper` that blocks write-like operations while forwarding read-only operations through the base wrapper. It is intended to provide a read-only filesystem view, though the comments explicitly say it has not been fully analyzed as a security boundary.

## Important APIs and Types
- `ReadOnlyFileSystem : FileSystemWrapper` with `Name()` returning `ReadOnlyFileSystem`.
- `FailReadOnly()` builds a non-retryable `IOStatus::IOError("Attempted write to ReadOnlyFileSystem")`.
- Overridden mutating operations include writable/random-RW file creation, directory creation object creation, delete/create/delete dir, rename, link, sync, lock, and logger creation.
- `CreateDirIfMissing` is special-cased to return OK if the directory already exists and is a directory.

## Control Flow
All blocked operations immediately return `FailReadOnly()` without invoking the target filesystem. `CreateDirIfMissing` calls `IsDirectory` first; if the path is an existing directory, it allows the call as a no-op, otherwise it fails as read-only.

## State and Persistence
The wrapper stores only the base filesystem through `FileSystemWrapper`. It should not create, delete, link, sync, lock, or write files through its overrides. Read-only operations not overridden are forwarded to the target.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`. It integrates anywhere RocksDB accepts a `FileSystem` and a caller wants to prevent writes at the abstraction layer, such as read-only DB opens or tests.

## Risks and Edge Cases
- Not a hard security sandbox; operations not overridden by this wrapper may still expose behavior inherited from `FileSystemWrapper`.
- `LockFile` is blocked, which can affect code paths that use locks even for read-only coordination.
- `CreateDirIfMissing` depends on the target `IsDirectory` result; permission or path errors become read-only failures rather than preserving the original status.

## Test Signals
No direct tests are listed. Useful tests should assert every mutating override fails, `CreateDirIfMissing` succeeds for an existing directory, and ordinary read operations still pass through.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_readonly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_remap.cc -->
# sources/storage-engines/rocksdb/env/fs_remap.cc

## Purpose
Implements the path-remapping filesystem wrapper declared in `fs_remap.h`. It translates user-visible paths through subclass-provided `EncodePath` or `EncodePathWithNewBasename`, then delegates the operation to `FileSystemWrapper`. It is a base for views such as chroot-like, encrypted-name, or otherwise transformed filesystems.

## Important APIs and Functions
- `EncodePathWithNewBasename` defaults to `EncodePath`.
- `RegisterDbPaths` and `UnregisterDbPaths` encode path vectors before forwarding.
- All file open/create/delete/query methods encode relevant paths and forward to the wrapped filesystem.
- `NewDirectory` wraps returned `FSDirectory` in a local `RemapFSDirectory` so `DirFsyncOptions::renamed_new_name` is encoded before directory fsync.
- `RenameFile` and `LinkFile` encode both source and destination with correct existing/new-basename semantics.

## Control Flow
Each method computes an encoded path pair, returns the non-OK status immediately if encoding fails, then delegates. Existing paths generally use `EncodePath`; paths that may not yet exist use `EncodePathWithNewBasename`. `RenameFile` converts a source `NotFound` from encoding into `PathNotFound` before returning. `NewDirectory` encodes the directory path, opens the wrapped directory, and then interposes only the fsync-with-options path mapping.

## State and Persistence
This class stores no additional state beyond the wrapped filesystem. Persistent effects are those of the delegated operations after path translation: file creation, rename, link, delete, sync, lock, and logger creation.

## Dependencies and Integration Points
Depends on `env/fs_remap.h` and `rocksdb/file_system.h`. It is designed for subclasses that define the actual path mapping policy. Integration points include DB path registration, file creation/open paths, directory fsync metadata, and file locking.

## Risks and Edge Cases
- `ReuseWritableFile` appears to compute both the new encoded path and old encoded path, but forwards `status_and_old_enc_path.second` as both arguments. That means the requested new name is ignored and reuse/rename behavior is likely wrong for remapped filesystems.
- `GetChildren` and `GetChildrenFileAttributes` return wrapped filesystem names without decoding them back to logical names; subclasses or callers must tolerate encoded child names, or this base class is incomplete for list operations.
- The class comment warns it has not been fully analyzed for strong security guarantees.
- Any subclass that allows partial mappings must carefully distinguish `EncodePath` and `EncodePathWithNewBasename` to avoid creating outside the intended view.

## Test Signals
No local tests are listed. High-priority tests should cover `ReuseWritableFile` path arguments, directory fsync rename-name mapping, list output expectations, rename `NotFound` to `PathNotFound`, and register/unregister mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_remap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_remap.h -->
# sources/storage-engines/rocksdb/env/fs_remap.h

## Purpose
Declares `RemapFileSystem`, an abstract `FileSystemWrapper` that maps logical paths to paths in an underlying filesystem. Subclasses implement `EncodePath`, and optionally `EncodePathWithNewBasename`, to define the mapping policy.

## Important APIs and Types
- `RemapFileSystem(const std::shared_ptr<FileSystem>& base)` wraps a base filesystem.
- Pure virtual `EncodePath(const std::string& path)` returns `{IOStatus, mapped_path}`.
- Virtual `EncodePathWithNewBasename` supports operations where the leaf path may not exist yet.
- Overrides cover DB path registration, file creation/open, directory operations, existence/listing/attributes, deletion, size/time/is-directory, rename/link, sync, lock, logger, and absolute path.
- `IsInstanceOf` recognizes `RemapFileSystem` in addition to wrapper/base identities.

## Control Flow
The header defines the contract: before any operation reaches the target filesystem, logical paths must be encoded. For create-like operations, subclasses can permit a new basename while still validating the parent. For existing-object operations, encoding failure prevents delegation.

## State and Persistence
No remap state is declared in the base class. Subclasses carry any mapping state. Persistent effects are delegated to the wrapped filesystem after path translation.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`. It integrates with RocksDB's filesystem abstraction as a reusable base for path-virtualizing filesystems. It also affects DB path registration, file locks, logger paths, and directory fsync metadata.

## Risks and Edge Cases
- The class is explicitly not a proven security boundary.
- Listing APIs expose a contract ambiguity: the base declares overrides but does not require decoded child names.
- Subclasses must preserve path normalization and parent validation; otherwise `EncodePathWithNewBasename` can become an escape vector.

## Test Signals
No direct tests are listed. Subclass tests should use a fake mapping filesystem and assert every override passes exactly the expected mapped paths to a fake target, especially create-vs-existing operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/fs_remap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/io_posix.cc -->
# sources/storage-engines/rocksdb/env/io_posix.cc

## Purpose
Implements concrete POSIX file and directory classes used by `fs_posix.cc`: sequential reads, random reads, mmap reads/writes, writable files, random read/write files, memory-mapped buffers, directory fsync, direct-I/O helpers, logical-block-size lookup, preallocation, range sync, and optional io_uring batched/async read support.

## Important APIs and Functions
- `IOErrorMsg` and `IOError` translate errno values to `IOStatus`, including retryable `NoSpace`, stale file, and path-not-found handling.
- `Fadvise`, `Madvise`, `PosixWrite`, and `PosixPositionedWrite` wrap platform behavior and large write chunking.
- `LogicalBlockSizeCache` and `PosixHelper` read `/sys/dev/block/.../queue/{logical_block_size,max_sectors_kb}` with defaults.
- `PosixSequentialFile::{Read,PositionedRead,Skip,InvalidateCache}` implements buffered and direct sequential access.
- `PosixRandomAccessFile::{Read,MultiRead,Prefetch,ReadAsync,GetFileSize,Hint,InvalidateCache}` implements pread, io_uring batching, async read, and cache hints.
- `PosixMmapReadableFile` and `PosixMmapFile` implement mmap read and mmap write.
- `PosixWritableFile` implements append, positioned append, truncate, close, sync/fsync, fallocate, range sync, write lifetime hints, cache invalidation, and unique IDs.
- `PosixRandomRWFile`, `PosixMemoryMappedFileBuffer`, and `PosixDirectory` cover random RW, raw mmap buffer cleanup, and directory sync semantics.

## Control Flow
Read paths loop on `EINTR` and stop on EOF or short direct-I/O sectors. `MultiRead` uses a thread-local io_uring when available: prepares SQEs up to queue capacity, submits with `io_uring_submit_and_wait`, reaps CQEs, resubmits short or transient requests, and falls back to serialized reads when ring initialization is unavailable. `ReadAsync` allocates a `Posix_IOHandle`, prepares one read SQE, submits it, and returns a handle/deleter for `Poll`/`AbortIO`. mmap writes allocate/map regions, append via `memcpy`, sync with `msync` plus fd sync, unmap, and truncate unused preallocated space on close. Directory fsync skips or redirects some btrfs cases, especially syncing the renamed new file for rename operations.

## State and Persistence
Persistent effects include file writes, truncation, preallocation/hole punching, mmap-backed writes, sync/fsync/fdatasync, range sync, and directory fsync. Runtime state includes file descriptors, `FILE*`, logical sector size, direct-I/O flags, mmap pointers and offsets, writable `filesize_`, fallocate/range-sync capability flags, io_uring handles, and directory filesystem type.

## Dependencies and Integration Points
Depends on Linux/macOS/AIX/POSIX syscalls (`pread`, `write`, `pwrite`, `mmap`, `msync`, `fsync`, `fdatasync`, `fallocate`, `sync_file_range`, `statfs`, `ioctl`, `fcntl`, `readahead`, `posix_fadvise`, `posix_madvise`) plus RocksDB helpers for I/O stats, coding, sync points, and slices. It is instantiated by `PosixFileSystem` in `fs_posix.cc` and implements the low-level behavior behind RocksDB `FS*File` interfaces.

## Risks and Edge Cases
- Direct I/O alignment is enforced with assertions, so release builds may rely on kernel errors if callers pass unaligned buffers/offsets.
- `PosixWrite` and `PosixPositionedWrite` do not explicitly handle a zero-byte successful write while bytes remain; such behavior would spin, though regular files should not return zero for nonzero writes.
- `MultiRead` is complex and must maintain io_uring queue accounting precisely; error teardown destroys the thread-local ring to avoid stale SQEs.
- `ReadAsync` returns `Busy` if no SQE is available and must not publish a handle in that case.
- `PosixMmapFile::Close` computes `unused = limit_ - dst_`; this assumes a region has been mapped before close, which is normally true after append but is a fragile invariant for empty mmap files.
- Directory fsync behavior is filesystem-specific; btrfs rename handling intentionally syncs the new file instead of the directory.

## Test Signals
`io_posix_test.cc` covers `LogicalBlockSizeCache` caching/refcount behavior, `PosixWritableFile::Truncate` seek positioning after shrink and extend, and btrfs rename fsync error preservation. Additional valuable tests would cover io_uring `MultiRead` partial reads/errors, `ReadAsync` SQ-full behavior, mmap empty-file close, direct-I/O alignment failures, ZFS/WSL `sync_file_range` fallback, and write zero-progress handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/io_posix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/io_posix.h -->
# sources/storage-engines/rocksdb/env/io_posix.h

## Purpose
Declares POSIX-backed implementations of RocksDB file interfaces and helper utilities used by the POSIX filesystem. It also declares optional io_uring request state, TSAN mmap annotations, direct-I/O alignment helpers, logical block-size caching, and platform fallback constants for fadvise/madvise.

## Important APIs and Types
- `IOErrorMsg` and `IOError` are shared status builders.
- `TsanMappedMemoryInfo` and `TsanAnnotateMappedMemory` reset TSAN shadow state for new mmap/io_uring mappings and expose sync-point payloads.
- `PosixHelper` provides unique file IDs and logical-block/max-sector lookup.
- `LogicalBlockSizeCache` caches per-directory logical block sizes with refcounts on Linux.
- `Posix_IOHandle`, `UpdateResult`, and `FinalizeAsyncRead` support io_uring async completion.
- Concrete classes: `PosixSequentialFile`, `PosixRandomAccessFile`, `PosixWritableFile`, `PosixMmapReadableFile`, `PosixMmapFile`, `PosixRandomRWFile`, `PosixMemoryMappedFileBuffer`, and `PosixDirectory`.

## Control Flow
The header defines interface contracts and state fields. Direct-I/O helpers test power-of-two sector alignment. io_uring helpers translate CQE results into `FSReadRequest` status/result and invoke callbacks. Concrete classes expose RocksDB virtual methods that are implemented in `io_posix.cc`; constructors capture descriptors, filenames, options, and alignment values.

## State and Persistence
Declared runtime state includes file descriptors, `FILE*`, direct-I/O flags, logical sector sizes, mmap region pointers, file offsets, preallocation flags, range-sync support, thread-local io_uring pointers, writable file sizes, and directory btrfs detection. Persistent effects are performed by the implementations.

## Dependencies and Integration Points
Includes optional `liburing`, pthread, sys/uio, `rocksdb/env.h`, `rocksdb/file_system.h`, `rocksdb/io_status.h`, sync points, mutex/thread-local utilities, and platform headers. These classes are consumed by `fs_posix.cc` and surfaced through RocksDB's `FS*File` abstractions.

## Risks and Edge Cases
- Compatibility macros define newer io_uring setup flags when older headers lack them; runtime kernels can still reject the flags.
- `UpdateResult` has nuanced behavior for zero-byte CQEs, partial direct-I/O sectors, async versus synchronous callers, and fallback read-again signaling.
- `LogicalBlockSizeCache::Size()` does not lock in the header declaration, while other accessors do; implementation/use should consider concurrent reads.
- The file includes test utilities in production declarations for sync-point instrumentation.

## Test Signals
`io_posix_test.cc` directly covers `LogicalBlockSizeCache` and indirectly exercises `PosixWritableFile`/`PosixDirectory` through the default filesystem. Sync-point hooks also support deterministic tests for TSAN annotation and io_uring branches elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/io_posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/io_posix_test.cc -->
# sources/storage-engines/rocksdb/env/io_posix_test.cc

## Purpose
Provides focused unit tests for selected POSIX I/O behaviors when `ROCKSDB_LIB_IO_POSIX` is enabled. Linux-only tests validate logical block-size cache semantics and btrfs directory fsync error handling. Cross-platform POSIX tests validate writable-file seek behavior after truncate/extend.

## Important APIs and Tests
- `LogicalBlockSizeCacheTest.Cache` verifies uncached fd fallback, directory registration, trailing slash normalization, cached lookup avoidance, and multiple cached directories.
- `LogicalBlockSizeCacheTest.Ref` verifies refcount increment/decrement and eviction at zero references.
- `PosixWritableFileTest.SeekAfterTruncate` writes, truncates smaller, appends, closes, and asserts final size.
- `PosixWritableFileTest.SeekAfterExtend` writes, truncates larger, appends, closes, and asserts final size.
- `PosixDirectoryTest.BtrfsFsyncFailedOpenDoesNotCloseInvalidFd` forces the btrfs branch via `SyncPoint` and asserts the original open error is preserved rather than overwritten by `close(-1)`.

## Control Flow
The tests use `FileSystem::Default()` and per-thread test DB paths for real filesystem interactions. Logical block-size cache tests inject lambdas instead of reading sysfs. The btrfs test creates a directory, opens `FSDirectory`, installs a sync-point callback to force `is_btrfs_`, calls `FsyncWithDirOptions` with a nonexistent renamed file, checks the error string, clears sync points, closes, and deletes the directory.

## State and Persistence
Tests create temporary files/directories under RocksDB's per-thread test path and delete them after assertions. SyncPoint global state is enabled and then cleared in the btrfs test. Logical block-size tests use local in-memory maps and counters.

## Dependencies and Integration Points
Depends on `test_util/testharness.h`, `test_util/sync_point.h`, `util/random.h`, `env/io_posix.h`, and `rocksdb/file_system.h`. It integrates with `fs_posix.cc` through `FileSystem::Default()` and with `io_posix.h` internals because the tests compile in the same namespace/configuration.

## Risks and Edge Cases
- The tests are gated by `ROCKSDB_LIB_IO_POSIX`; Linux-specific coverage is further gated by `OS_LINUX`.
- File path names for the two writable tests both include `PosixWritableFileTest_SeekAfterTruncate`, which is harmless but slightly confusing for diagnostics.
- The btrfs test checks substrings in `IOStatus::ToString()`, so wording changes can break it even if behavior remains correct.

## Test Signals
These tests provide regression signals for direct state tracked in `io_posix.cc`: truncate must reposition the fd to the logical file size before subsequent append, block-size cache must not recompute cached directories and must evict on zero refs, and btrfs rename fsync must not close an invalid descriptor or mask the open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/io_posix_test.cc -->
