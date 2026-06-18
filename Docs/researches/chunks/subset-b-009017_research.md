# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 39366-47008

## Chunk Purpose

This chunk is the main Unix VFS implementation from SQLite's amalgamated `os_unix.c` section. It connects SQLite's generic `sqlite3_vfs` and `sqlite3_file` interfaces to Unix-like system calls, implements database file locking, ordinary file I/O, WAL shared-memory mapping, mmap-backed fetches, temporary file naming, path canonicalization, dynamic extension loading, randomness/time/sleep services, and Unix VFS registration.

The code is compiled under `SQLITE_OS_UNIX` and is heavily feature-gated for POSIX, VxWorks, macOS locking styles, WAL, mmap, QNX, WASI, F2FS batch atomic write support, loadable extensions, and SQLite test/debug builds. In this vendored copy under WiredTiger tests, it supplies SQLite's storage-facing Unix behavior whenever the test build uses this embedded SQLite source.

## Important APIs, Types, and Functions

- System-call override layer: `aSyscall[]` entries are exposed through macros such as `osRmdir`, `osFchown`, `osMmap`, `osMunmap`, `osMremap`, `osGetpagesize`, `osReadlink`, `osLstat`, and `osIoctl`. `unixSetSystemCall()`, `unixGetSystemCall()`, and `unixNextSystemCall()` implement the `sqlite3_vfs` xSetSystemCall/xGetSystemCall/xNextSystemCall hooks used by tests, embedders, and sandboxes to replace or inspect low-level calls.
- Robust syscall wrappers: `robust_open()` retries EINTR, avoids file descriptors below `SQLITE_MINIMUM_FILE_DESCRIPTOR`, enforces exact journal/WAL permissions when requested, and sets close-on-exec. `robust_ftruncate()` retries EINTR and avoids unsafe >2GiB truncation on Android. `robust_close()` logs but does not retry close failures. `robustFchown()` only calls `fchown()` as root to avoid security-log noise.
- Global and per-inode locking state: `unixBigLock` protects process-wide inode/shared-memory lists; `unixFileId` identifies files by device and inode or by VxWorks canonical path; `unixInodeInfo` tracks per-inode locks, reference counts, deferred close descriptors, optional WAL shared-memory node, and platform-specific state.
- VxWorks canonical IDs: `vxworksFileId`, `vxworksSimplifyName()`, `vxworksFindFileId()`, and `vxworksReleaseFileId()` replace inode identity with canonical absolute path identity on VxWorks.
- POSIX locking methods: `unixCheckReservedLock()`, `unixFileLock()`, `unixLock()`, `posixUnlock()`, `unixUnlock()`, and `unixClose()` implement SQLite's lock ladder over POSIX byte-range locks (`NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`).
- Alternate locking methods: `nolock*` ignores locks; `dotlock*` uses a sibling `.lock` directory; `flock*` uses `flock()` when `SQLITE_ENABLE_LOCKING_STYLE`; `semX*` uses named semaphores on VxWorks; `afp*` uses macOS AFP byte-range locking through `fsctl`; `nfsUnlock()` uses a two-phase downgrade to work around macOS/BSD NFS lockd behavior.
- File I/O methods: `seekAndRead()`, `unixRead()`, `seekAndWriteFd()`, `seekAndWrite()`, `unixWrite()`, `full_fsync()`, `openDirectory()`, `unixSync()`, `unixTruncate()`, `unixFileSize()`, and `unixFileControl()` implement `sqlite3_io_methods` operations.
- Capacity and file-control helpers: `fcntlSizeHint()` expands files/chunks and may map them; `unixModeBit()` handles query/set file-control bits; `setDeviceCharacteristics()`, `unixSectorSize()`, and `unixDeviceCharacteristics()` advertise sector and `SQLITE_IOCAP_*` flags, including powersafe overwrite, subpage read, QNX filesystem characteristics, and optional F2FS atomic batches.
- WAL shared-memory types: `unixShmNode` is the process-wide representation of a `*-shm` wal-index file for one inode; `unixShm` is the per-connection handle. Lock arrays and masks record local shared/exclusive locks for `SQLITE_SHM_NLOCK` slots.
- WAL shared-memory functions: `unixFcntlExternalReader()`, `unixShmSystemLock()`, `unixShmRegionPerMap()`, `unixShmPurge()`, `unixLockSharedMemory()`, `unixOpenSharedMemory()`, `unixShmMap()`, `unixShmLock()`, `unixShmBarrier()`, and `unixShmUnmap()` implement xShmMap/xShmLock/xShmBarrier/xShmUnmap.
- Mmap fetch functions: `unixUnmapfile()`, `unixRemapfile()`, `unixMapfile()`, `unixFetch()`, and `unixUnfetch()` implement xFetch/xUnfetch when `SQLITE_MAX_MMAP_SIZE>0`.
- I/O method registration: the `IOMETHODS` macro constructs `sqlite3_io_methods` tables and finder functions for POSIX, no-lock, dotfile, flock, semaphore, AFP, NFS, and proxy modes. `autolockIoFinderImpl()` and `vxworksIoFinderImpl()` choose methods based on filesystem or fcntl support.
- VFS operations: `fillInUnixFile()`, `unixOpen()`, `unixDelete()`, `unixAccess()`, `unixFullPathname()`, `unixDlOpen()`, `unixDlError()`, `unixDlSym()`, `unixDlClose()`, `unixRandomness()`, `unixSleep()`, `unixCurrentTimeInt64()`, `unixCurrentTime()`, and `unixGetLastError()` provide the Unix `sqlite3_vfs` method table.
- macOS proxy locking: `proxyLockingContext`, `proxyGetLockPath()`, `proxyCreateLockPath()`, `proxyCreateUnixFile()`, `proxyGetHostID()`, `proxyBreakConchLock()`, `proxyConchLock()`, `proxyTakeConch()`, `proxyReleaseConch()`, `proxyCreateConchPathname()`, `switchLockProxyPath()`, `proxyGetDbPathForUnixFile()`, `proxyTransformUnixFile()`, `proxyFileControl()`, `proxyCheckReservedLock()`, `proxyLock()`, `proxyUnlock()`, and `proxyClose()` move database locks to a local proxy file while coordinating host ownership through a conch file.
- VFS lifecycle: `sqlite3_os_init()` registers Unix VFS variants (`unix`, `unix-none`, `unix-dotfile`, `unix-excl`, and optionally `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, `unix-proxy`, `unix-namedsem`) and initializes `unixBigLock` and temp directories. `sqlite3_os_end()` clears `unixBigLock`.

## Control Flow

Opening starts in `unixOpen()`. It validates SQLite open flags, resets randomness after fork/pid change, optionally reuses deferred file descriptors for main DB files, creates a temp name for unnamed temp files, converts SQLite flags to POSIX flags, determines creation mode/owner from the database for WAL/journals through `findCreateFileMode()`, opens with `robust_open()`, falls back from read-write to read-only when allowed, applies delete-on-close handling, captures filesystem flags, sets `UNIXFILE_*` control bits, optionally enables proxy locking, then delegates to `fillInUnixFile()`.

`fillInUnixFile()` stores the descriptor and VFS pointers in `unixFile`, chooses a locking implementation through the VFS finder, allocates per-inode state when required, creates platform-specific contexts such as AFP, dotlock, or VxWorks semaphores, installs the selected `sqlite3_io_methods`, and verifies the database file for hard-link, symlink, and moved-file hazards.

The POSIX lock path uses in-memory inode state to compensate for POSIX advisory-lock semantics. `unixLock()` checks requested lock ordering, serializes on `pInode->pLockMutex`, returns `SQLITE_BUSY` if another connection in the same process has an incompatible lock, coalesces shared locks within the same process, and only calls `fcntl()` when the process-level state actually transitions. It takes PENDING before SHARED or before upgrading RESERVED to EXCLUSIVE, read-locks the shared range for SHARED, write-locks the reserved byte for RESERVED, and write-locks the shared range for EXCLUSIVE. `posixUnlock()` reverses this, optionally using an NFS-specific split downgrade on macOS, and defers descriptor close until all locks on the inode are gone.

The normal read/write path is direct `pread`/`pwrite` or seek-plus-read/write depending on platform macros. `unixRead()` first satisfies reads from an active mmap region when possible, then calls `seekAndRead()`, zero-filling short reads and distinguishing corrupt filesystem errors. `unixWrite()` tracks debug transaction-counter invariants, writes through mmap when enabled for read-write mappings, loops until the request is complete, and maps short/non-space writes to `SQLITE_FULL` or I/O errors. Sync, truncate, and file-size calls update persistence guarantees and mmap bounds.

WAL shared memory opens lazily on first `unixShmMap()`. `unixOpenSharedMemory()` creates or reuses a `unixShmNode` per inode, opens `<db>-shm` or a configured shared-memory directory file, copies permissions/ownership from the DB, locks the deadman switch through `unixLockSharedMemory()`, then links a per-connection `unixShm`. `unixShmMap()` extends and maps 32KiB regions in page-size-aligned groups, writing the last byte of each new page to reduce later SIGBUS risk. `unixShmLock()` maintains both process-local lock masks and system `fcntl()` locks; in `SQLITE_ENABLE_SETLK_TIMEOUT` builds it uses per-slot mutexes and try-lock behavior to avoid blocking-lock deadlocks.

Mmap fetch control is separate from WAL shared memory. `unixFetch()` maps the database file on demand through `unixMapfile()` and returns a pointer only if the mapping covers the requested bytes plus a 256-byte EOF safety buffer. `unixUnfetch()` decrements outstanding fetch references or unmaps the file on invalidation. Remapping is disabled while fetch references are outstanding.

For macOS proxy locking, a file can be transformed after open. `proxyTakeConch()` obtains or updates the conch file, validates host ID and proxy path, creates/opens the local proxy file, reopens the database descriptor if necessary, and then later `proxyLock()`/`proxyUnlock()` forward lock operations to the proxy file. Stale conch locks may be broken only after host ID and modification-time checks.

`sqlite3_os_init()` builds static VFS tables with xOpen/xDelete/xAccess/xFullPathname/xDl*/xRandomness/xSleep/xCurrentTime/xSetSystemCall hooks and registers each configured Unix VFS with SQLite. The next chunk starts the Windows VFS; this chunk ends the Unix implementation.

## State and Persistence Behavior

- File descriptor state lives in `unixFile`: descriptor `h`, selected VFS, path, lock level, control flags, last errno, directory-sync state, chunk size, mmap fields, and optional locking contexts.
- Cross-connection state for a database inode lives in `unixInodeInfo`, including process-local lock counters, the highest lock level, outstanding lock count, deferred descriptors in `pUnused`, and optional `pShmNode`.
- POSIX locks are persisted in the kernel on fixed byte ranges of the database file. SQLite mirrors them in `unixInodeInfo` to avoid same-process POSIX lock surprises and to avoid close() on one descriptor silently dropping another descriptor's locks.
- Dotlock locking persists as a `"<db>.lock"` directory. Failure to remove it can leave a stale exclusive lock.
- WAL shared memory persists as `"<db>-shm"` unless `unix-excl` simulates shared memory with heap memory. The DMS byte is used to detect first opener and force safe truncation/reinitialization.
- Journal/WAL creation attempts to copy permissions and ownership from the associated database file, preserving recoverability for other users that can write the DB.
- `unixSync()` fsyncs the file and one-time fsyncs the containing directory for newly created journals/WAL files when `UNIXFILE_DIRSYNC` is set.
- Temporary file directory preference is `sqlite3_temp_directory`, `SQLITE_TMPDIR`, `TMPDIR`, `/var/tmp`, `/usr/tmp`, `/tmp`, then `.`.
- Mmap state (`pMapRegion`, `mmapSize`, `mmapSizeActual`, `mmapSizeMax`, `nFetchOut`) is process-local and is dropped on close, truncate shrink, failed mapping, or explicit unfetch invalidation.
- Proxy locking persists a conch file beside the DB and a proxy lock file under the configured or generated local proxy directory. These files are intentionally not deleted.

## Dependencies and Integration Points

- Integrates with SQLite core through `sqlite3_vfs`, `sqlite3_io_methods`, `sqlite3_file_control()` opcodes, SQLite memory allocators, mutexes, random number generation, URI parameter access, logging, and error-code conventions.
- Uses POSIX/Unix APIs: `open`, `close`, `read`, `write`, `pread`, `pwrite`, `lseek`, `fcntl`, `fsync`/`fdatasync`, `ftruncate`, `fstat`, `stat`, `lstat`, `readlink`, `access`, `unlink`, `rmdir`, `mkdir`, `mmap`, `munmap`, optional `mremap`, `getcwd`, `gettimeofday`, `nanosleep`/`usleep`/`sleep`, `dlopen`/`dlsym`/`dlclose`, and platform-specific calls like `fsctl`, `statfs`, `confstr`, `gethostuuid`, `sem_open`, and Linux F2FS `ioctl`.
- WAL integration depends on `SQLITE_SHM_NLOCK==8`, `UNIX_SHM_BASE==120`, and `UNIX_SHM_DMS==128`; `sqlite3_os_init()` asserts those assumptions.
- File-control integration includes lock state, last errno, chunk size, size hints, persistent WAL, powersafe overwrite, VFS name, temp filename generation, moved-file detection, mmap-size limit, lock timeout, block-on-connect, proxy lock file get/set, and external-reader detection.
- Test/debug integrations include `SimulateIOError`, `SimulateDiskfullError`, sync counters, fake current time, deterministic randomness under `SQLITE_TEST`, host-id perturbation for proxy tests, OSTRACE, lock tracing, and debug assertions around transaction-counter updates.

## Risks and Edge Cases

- Lock correctness is the dominant risk. POSIX locks are process-scoped and close-sensitive, so bugs in `nShared`, `nLock`, `eFileLock`, or deferred-close handling can lead to dropped locks or false `SQLITE_BUSY` results.
- Multiple fallback locking modes intentionally reduce concurrency. `nolock`, dotlock, flock, sem, AFP, NFS, and proxy behavior differ substantially; choosing the wrong finder for a filesystem may trade safety, availability, or performance.
- `robust_open()` deliberately rejects file descriptors 0, 1, and 2 and opens `/dev/null` to move past them. This avoids confusing stdin/stdout/stderr with database handles but can fail in constrained environments.
- Directory fsync is best-effort. Some systems cannot fsync directories and the code ignores that failure, leaving a residual crash-recovery risk on filesystems that need directory persistence.
- Short reads are converted to zero-filled buffers with `SQLITE_IOERR_SHORT_READ`, which upper layers expect. Any caller that ignores the return code could consume synthetic zeros.
- `unixRead()` maps selected low-level errors (`ERANGE`, `EIO`, `ENXIO`, `EDEVERR`) to `SQLITE_IOERR_CORRUPTFS`, allowing the higher API exit path to convert them to corruption signals.
- WAL shared-memory initialization carefully avoids using a stale or crash-corrupted `*-shm` file by using the DMS byte and truncating first-open files. Any change to this flow risks database corruption after power loss.
- `unixShmMap()` assumes page writes during extension prevent later SIGBUS. Filesystems with unusual allocation behavior remain a risk.
- Mmap is disabled after a failed mapping by setting `mmapSizeMax=0`; this protects correctness but can cause silent performance fallback.
- Proxy locking is complex and macOS-specific. Stale conch breaking, host ID matching, database descriptor reopening, and proxy path switching are all sensitive to races and filesystem semantics.
- In `proxyCheckReservedLock()`, the lockless branch assigns `pResOut=0` rather than `*pResOut=0`. This is a visible local bug pattern: it does not update the caller's output value if `conchHeld<0`.
- `unixAccess()` only asserts `EXISTS` and `READWRITE` even though comments mention `READONLY`; the implementation treats non-EXISTS as read-write.
- Compile-time feature combinations change behavior heavily. WASI disables Unix mmap/WAL syscalls; Android avoids >2GiB truncate; QNX reports special device capabilities; macOS enables AFP/NFS/proxy/autolock branches.

## Test Signals

- Existing SQLite test hooks are embedded directly: syscall override APIs, `SimulateIOError`, `SimulateDiskfullError`, benign I/O error regions, sync counters, fake current time, deterministic randomness, `sqlite3_hostid_num`, OSTRACE, lock tracing, and many assertions.
- Meaningful tests for this chunk should exercise:
  - VFS registration and default VFS selection under `sqlite3_os_init()`.
  - `xSetSystemCall`/`xGetSystemCall`/`xNextSystemCall` replacement and reset behavior.
  - Opening main DB, WAL, journal, temp, read-only fallback, delete-on-close, and reusable deferred descriptors.
  - POSIX lock transitions, same-process multi-connection shared locks, RESERVED/EXCLUSIVE contention, and close deferral while locks remain.
  - Dotlock/flock/nolock/proxy behavior when those compile-time modes are enabled.
  - Crash-persistence paths: `unixSync()` full/data-only sync, directory sync, journal/WAL ownership/mode preservation, and `unixDelete()` dirsync.
  - Short read zero-fill and corrupt-filesystem error mapping.
  - WAL shared-memory open, DMS first-opener truncation, read-only SHM handling, region extension/mapping, lock slot transitions, external-reader detection, and unmap/delete behavior.
  - Mmap fetch/unfetch reference counting, remap limits, failed mmap fallback, and truncation below mapped size.
  - Path canonicalization, symlink resolution, maximum symlink handling, temp-name collision retries, and dynamic loader error reporting.

## Unresolved Cross-Chunk References

- The definitions of `unixFile`, `UnixUnusedFd`, `sqlite3FileSuffix3()`, global variables such as `randomnessPid`, constants like `PENDING_BYTE`, `SHARED_FIRST`, `SQLITE_OPEN_*`, and many SQLite core helpers are outside this chunk and must be reconciled with earlier amalgamation chunks.
- The Windows VFS starts immediately after this chunk, so any final per-file report should contrast this Unix implementation with later OS-specific implementations only after the Windows chunks are read.
