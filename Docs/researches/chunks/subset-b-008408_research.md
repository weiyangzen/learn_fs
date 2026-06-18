# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 14969-22849

## Scope And Purpose

This chunk spans several independent pieces of the vendored SQLite amalgamation used under FoundationDB's `contrib/sqlite` tree. It begins in the tail of `hash.c`, covers the generated opcode-name table, includes the full OS/2 VFS implementation, and then covers most of the Unix VFS implementation through the beginning of Mac OS X proxy-locking conch acquisition.

The largest behavioral surface is the VFS layer. The OS/2 section maps SQLite's `sqlite3_vfs` and `sqlite3_io_methods` contracts onto `Dos*` APIs, including path-codepage conversion, byte-range locking, dynamic extension loading, randomness, sleep, and current-time methods. The Unix section implements file open/read/write/sync/truncate/delete/access, POSIX advisory locking, alternative locking styles, WAL shared-memory mapping, filesystem-specific method selection, temporary-file naming, and the first half of proxy-lock support.

The chunk is source-tree-aligned to the amalgamation rather than a final per-file report. It stops mid-function inside `proxyConchLock()`, so proxy-lock control flow after stale-conch breaking must be reconciled by the following chunk.

## Important APIs, Types, And Functions

The hash-table tail exposes `sqlite3HashFind()` and `sqlite3HashInsert()` over the internal `Hash`, `HashElem`, and `_ht` bucket structures. The local helpers `rehash()`, `findElementGivenHash()`, and `removeElementGivenHash()` resize buckets, locate case-insensitive string keys, update the doubly linked insertion list, and clear the table when the last element is removed.

`sqlite3OpcodeName()` is a debug/explain/profile helper generated from opcode metadata. It returns the string name for VDBE opcodes such as `Goto`, `Column`, `Transaction`, `OpenRead`, `ResultRow`, and virtual-table opcodes when explain/debug support is compiled in.

The OS-common include contributes diagnostics and test hooks shared by OS backends: `OSTRACE`, optional `sqlite3Hwtime()` performance timing, simulated I/O and disk-full failure counters (`sqlite3_io_error_pending`, `sqlite3_diskfull_pending`, etc.), and `sqlite3_open_file_count`.

The OS/2 VFS uses `os2File`, a `sqlite3_file` subclass containing an OS/2 `HFILE`, optional delete-on-close path, and current SQLite lock level. Its main file methods are `os2Close`, `os2Read`, `os2Write`, `os2Truncate`, `os2Sync`, `os2FileSize`, `os2Lock`, `os2Unlock`, `os2CheckReservedLock`, `os2FileControl`, `os2SectorSize`, and `os2DeviceCharacteristics`.

OS/2 path and VFS helpers include `initUconvObjects()`, `freeUconvObjects()`, `convertUtf8PathToCp()`, `convertCpPathToUtf8()`, `getTempname()`, `os2FullPathname()`, `os2Open()`, `os2Delete()`, `os2Access()`, `os2DlOpen()`/`os2DlSym()`/`os2DlClose()`, `os2Randomness()`, `os2Sleep()`, `os2CurrentTime()`, `os2CurrentTimeInt64()`, `sqlite3_os_init()`, and `sqlite3_os_end()`.

The Unix VFS defines `unixFile`, `UnixUnusedFd`, `unixFileId`, `unixInodeInfo`, `unixShmNode`, and `unixShm`. `unixFile` stores the file descriptor, directory descriptor, lock state, inode lock object, last errno, lock-specific context, WAL shared-memory handle, chunk-size hint, cached filesystem flags, and debug transaction-counter tracking state. `unixInodeInfo` is the process-local coordination object that prevents POSIX locks from being accidentally dropped by another file descriptor in the same process.

The Unix system-call override table `aSyscall[]` provides VFS-level test injection for `open`, `close`, `access`, `getcwd`, `stat`, `fstat`, `ftruncate`, `fcntl`, `read`, `pread`, `write`, `pwrite`, `fchmod`, and optional `posix_fallocate`. It is managed through `unixSetSystemCall()`, `unixGetSystemCall()`, and `unixNextSystemCall()`.

Unix file I/O methods include `unixRead()`, `unixWrite()`, `unixSync()`, `unixTruncate()`, `unixFileSize()`, `unixFileControl()`, `unixSectorSize()`, and `unixDeviceCharacteristics()`. Lower-level wrappers such as `robust_open()`, `robust_close()`, `robust_ftruncate()`, `seekAndRead()`, `seekAndWrite()`, `full_fsync()`, and `unixLogErrorAtLine()` centralize EINTR handling, close semantics, fsync behavior, and error logging.

The locking backends in this range include:

- POSIX byte-range locking: `findInodeInfo()`, `unixCheckReservedLock()`, `unixFileLock()`, `unixLock()`, `posixUnlock()`, `unixUnlock()`, and `unixClose()`.
- No-op locking: `nolockCheckReservedLock()`, `nolockLock()`, `nolockUnlock()`, and `nolockClose()`.
- Dot-file locking: `dotlockCheckReservedLock()`, `dotlockLock()`, `dotlockUnlock()`, and `dotlockClose()`.
- `flock()` locking when enabled: `flockCheckReservedLock()`, `flockLock()`, `flockUnlock()`, and `flockClose()`.
- VxWorks semaphore locking when enabled: `semCheckReservedLock()`, `semLock()`, `semUnlock()`, and `semClose()`.
- Apple AFP locking when enabled: `afpSetLock()`, `afpCheckReservedLock()`, `afpLock()`, `afpUnlock()`, and `afpClose()`.
- Apple NFS special unlock handling through `nfsUnlock()`, which delegates to `posixUnlock()` with the NFS workaround enabled.

WAL shared-memory support, compiled when WAL is not omitted, is implemented by `unixOpenSharedMemory()`, `unixShmSystemLock()`, `unixShmPurge()`, `unixShmMap()`, `unixShmLock()`, `unixShmBarrier()`, and `unixShmUnmap()`.

Method dispatch is built by the `IOMETHODS` macro, which creates `sqlite3_io_methods` tables and finder functions for `posix`, `nolock`, `dotlock`, `flock`, `sem`, `afp`, `proxy`, and `nfs` styles as applicable. `autolockIoFinderImpl()` chooses lock methods by filesystem type and lock support on Apple and VxWorks builds.

Unix VFS-level entry points covered here include `fillInUnixFile()`, `openDirectory()`, `unixTempFileDir()`, `unixGetTempname()`, `findReusableFd()`, `findCreateFileMode()`, `unixOpen()`, `unixDelete()`, `unixAccess()`, `unixFullPathname()`, dynamic loader wrappers, `unixRandomness()`, `unixSleep()`, `unixCurrentTimeInt64()`, `unixCurrentTime()`, and `unixGetLastError()`.

The proxy-locking portion begins with `proxyLockingContext`, `proxyGetLockPath()`, `proxyCreateLockPath()`, `proxyCreateUnixFile()`, `proxyGetHostID()`, `proxyBreakConchLock()`, and the first part of `proxyConchLock()`.

## Control Flow

Hash lookup computes a case-insensitive string hash modulo the current bucket count when buckets exist, then calls `findElementGivenHash()`. Without buckets, lookup scans the single linked list. Insertion first searches for an existing key. A non-null `data` replaces existing data or allocates a new `HashElem`; a null `data` removes the matching element. Once the table reaches at least 10 entries and more than twice the current bucket count, `rehash()` allocates a larger benign-malloc bucket array and reinserts all existing elements.

The OS/2 open path validates SQLite open flags, creates a temp filename when `zName` is null, translates the UTF-8 filename into the active OS/2 codepage, computes `DosOpen()` action and sharing modes, and falls back from read/write to read-only if needed. Delete-on-close stores a converted absolute path so `os2Close()` can force-delete it after closing the handle. Reads and writes seek with `DosSetFilePtr()` and call `DosRead()`/`DosWrite()`, with short reads zero-filling the unread buffer.

OS/2 locking raises the file's lock state through SQLite's standard sequence: `NO_LOCK -> SHARED_LOCK -> RESERVED_LOCK/PENDING_LOCK -> EXCLUSIVE_LOCK`. Shared locks use the SQLite shared lock range, reserved/pending/exclusive locks use fixed bytes, and unlock collapses state back to `NO_LOCK` or `SHARED_LOCK` depending on the request. `os2CheckReservedLock()` probes whether a reserved lock is held by this or another process.

Unix initialization starts with compile-time feature selection: large-file flags, optional locking styles, VxWorks handling, WAL mmap support, and Apple filesystem APIs. It defines a `unixFile` object for all Unix-family VFSes and a system-call dispatch table so tests can override kernel calls without replacing the whole VFS.

POSIX lock acquisition in `unixLock()` is process-aware. It enters the global Unix mutex, checks `unixInodeInfo` to see whether another handle in the same process already holds an incompatible lock, then performs the minimal `fcntl(F_SETLK)` transitions. A shared lock first takes a temporary lock on `PENDING_BYTE`, then locks one or all bytes in the shared range and releases pending. Reserved locks take `RESERVED_BYTE`. Exclusive locks take a pending lock and then write-lock the full shared range. If exclusive acquisition fails after pending is held, the file remains at `PENDING_LOCK`.

Unlocking in `posixUnlock()` downgrades higher locks to shared or no-lock. It has a special Apple/NFS path that clears and reestablishes parts of the shared range to work around lockd behavior. When the last process-local shared lock is released, it clears the OS lock and closes any file descriptors deferred in `unixInodeInfo.pUnused`.

`unixClose()` first unlocks the file, then avoids directly closing a descriptor if doing so would drop POSIX locks still held by another connection on the same inode. Such descriptors are put on the inode's pending-unused list and are either reused by `findReusableFd()` during a later open of the same database or closed when the last lock is gone.

Alternative Unix lock backends flatten or adapt the same SQLite lock states. No-op locking only updates no state and is intended for read-only or externally synchronized use. Dot-file locking creates and deletes a `*.lock` file, mapping all lock levels to an exclusive lock. `flock()` and VxWorks semaphores also collapse all held states into a single exclusive OS-level lock while tracking SQLite's intermediate levels in memory. AFP locking uses `fsctl()` byte-range locks, with a randomly selected shared byte and a full shared range for exclusive locking.

Unix reads and writes are offset-based through `pread`/`pwrite` or seek plus `read`/`write`. `unixRead()` returns `SQLITE_IOERR_SHORT_READ` after zero-filling missing bytes. `unixWrite()` loops until the requested write completes or an error/full condition occurs, and debug builds track whether writes changed the database transaction counter. `unixSync()` calls `full_fsync()` on the file and, for newly created journal/WAL/master-journal files, fsyncs and closes the parent directory descriptor once.

WAL shared memory opens lazily on first `unixShmMap()`. `unixOpenSharedMemory()` reuses one `unixShmNode` per inode in the process, creates or opens the `-shm` file next to the database unless the `unix-excl` process lock makes heap-backed memory sufficient, truncates stale shm files if it can take the dead-man switch, and links a per-connection `unixShm`. `unixShmMap()` extends and mmaps regions on demand. `unixShmLock()` enforces local sibling conflicts with bitmasks before taking or releasing fcntl locks on the shm file. `unixShmUnmap()` unlinks the connection, decrements the node reference count, optionally deletes the shm file, and purges mmap regions and the descriptor when the last connection closes.

`unixOpen()` is the main `sqlite3_vfs.xOpen` path. It validates flag combinations, optionally reuses a deferred database file descriptor, creates a temporary name for anonymous temp files, computes POSIX open flags and permissions, falls back to read-only when read/write open fails, unlinks delete-on-close files, opens a directory descriptor for created journal/WAL files that need directory sync, marks close-on-exec, detects MS-DOS filesystems for Apple workarounds, optionally transforms non-local files into proxy-locking files, and finally calls `fillInUnixFile()`.

`fillInUnixFile()` selects a locking method from the VFS `pAppData` finder, initializes inode state for locking styles that need it, allocates lock-specific contexts for dotlock and AFP, opens VxWorks semaphores when needed, stores read-only/exclusive flags, sets the final `sqlite3_io_methods`, and increments the open-file test counter. Error paths close descriptors carefully and release allocated locking context.

The proxy-locking setup builds a local lock-proxy path from either `LOCKPROXYDIR`, Darwin's user temp directory, or `/tmp`, creates missing lock directories, opens helper `unixFile` objects for conch or lock files, and obtains a host UUID. `proxyBreakConchLock()` tries to replace a stale conch file by copying it through a sibling `-break` file and renaming it back. `proxyConchLock()` then attempts a conch lock, waits 0.5 seconds after the first busy result, verifies the conch modification time and host id on the second busy result, waits 10 seconds, and on the third attempt may break a stale lock. The chunk ends before this function's final return path.

## State And Persistence Behavior

The hash table owns `HashElem` allocations and the bucket array, but it does not copy key strings. `sqlite3HashInsert()` stores the caller's `pKey` pointer directly and only replaces the stored key pointer when replacing data for an existing key. Callers must keep key storage valid for the lifetime of the hash entry.

OS/2 file state is mostly volatile inside `os2File`, but it mutates persistent filesystem state through writes, truncates, syncs, deletes, and byte-range locks. Delete-on-close persists only until `os2Close()`, where the saved path is force-deleted. Temporary names are generated under `sqlite3_temp_directory`, `TEMP`, `TMP`, `TMPDIR`, or the current drive.

Unix persistent state includes database, journal, WAL, shm, temp, dot-lock, proxy-lock, and conch files. Database file bytes are changed by `unixWrite()` and `unixTruncate()`, while durability is controlled by `unixSync()` and directory syncs. Delete operations optionally sync the containing directory to make journal removal durable.

Unix lock state is split between OS-level locks and in-process metadata. `unixInodeInfo.eFileLock`, `nShared`, `nLock`, `bProcessLock`, and `pUnused` model the effective lock state for all `unixFile` handles in the process that refer to the same inode. This state is guarded by SQLite's static master mutex and is not persisted. OS-level locks are byte-range locks on the database or shm file, `flock()` locks, semaphores, dot-lock files, AFP byte locks, or proxy helper locks depending on method.

The WAL shared-memory file is persistent filesystem state but is treated as rebuildable coordination data. If no other process holds the dead-man switch, a newly opened `unixShmNode` truncates the shm file to zero. In `unix-excl` mode, no shm file is created and the regions are heap allocations attached to the single-process inode state.

Open-file reuse is process-local state. A descriptor that cannot be closed safely due to POSIX lock semantics is detached from a closing `unixFile`, stored on `unixInodeInfo.pUnused`, and later reused only when the path resolves to the same device/inode and the flags match.

File creation modes preserve database-adjacent permissions. Temporary delete-on-close files are `0600`; database and master-journal files use `SQLITE_DEFAULT_FILE_PERMISSIONS`; WAL and main-journal files try to copy permissions from the corresponding database file.

Proxy locking persists two helper files. The conch file lives beside the database and records a version byte, host id, and proxy lock path. The proxy lock file lives in a local lock directory and is used as the target of normal SQLite advisory locks after the conch says this host owns proxy access. This range includes path creation and stale-conch breaking but not the full proxy acquisition/update workflow.

## Dependencies And Integration Points

The VFS code is the lower boundary used by the pager through `sqlite3Os*` wrappers. The pager depends on this chunk for file descriptors, byte-accurate reads and writes, sync semantics, file-size queries, truncation, open flags, deletion, access checks, randomness, sleep, current time, dynamic extension loading, WAL shared-memory methods, and lock-state transitions.

The lock constants (`NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`, `PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, and `SHARED_SIZE`) are shared with pager locking rules. Correct pager behavior assumes the VFS implements the documented transition order and returns `SQLITE_BUSY` rather than hard I/O errors for normal lock contention.

Testing integrates through `SQLITE_TEST` globals for simulated I/O errors, disk-full errors, fake current time, sync counts, open-file counts, and host-id perturbation for proxy locking. The Unix system-call override API is another key integration point for fault injection and sandboxing.

Platform dependencies are extensive. OS/2 depends on `DosOpen`, `DosRead`, `DosWrite`, `DosSetFileLocks`, `DosQueryPathInfo`, `DosLoadModule`, ULS conversion APIs, and OS/2 time/randomness sources. Unix depends on POSIX file APIs, optional `pread`/`pwrite`, `mmap`, `fcntl`, `fsync`/`fdatasync`, `dlopen`, `gettimeofday`, `statfs`, `flock`, VxWorks semaphores, Apple `fsctl`, Darwin temp-directory and host-UUID APIs, and compile-time macros controlling availability.

The method-finder design integrates with `sqlite3_vfs.pAppData`: VFS objects store a pointer to a finder-function pointer, not the function pointer directly, to satisfy C90 restrictions on casting `void *` to a function pointer. `fillInUnixFile()` relies on that convention.

WAL integration depends on `sqlite3_io_methods.iVersion == 2` for POSIX methods with shared-memory callbacks. Locking styles that do not support shared memory use method version 1 and null out WAL shm methods through the generated table.

FoundationDB integration in this chunk is indirect. This is a vendored SQLite OS layer without explicit FoundationDB calls. Its correctness still affects FoundationDB's SQLite-backed storage behavior because all pager durability, lock coordination, WAL shared memory, and fault-injection behavior flows through these VFS methods.

## Risks And Edge Cases

The Unix POSIX lock workaround is fragile by design. Closing any descriptor for an inode can release process-owned POSIX locks, so `unixClose()`, `findReusableFd()`, `releaseInodeInfo()`, and `closePendingFds()` must remain consistent. A missed reference count or premature close can silently drop locks held by other SQLite connections in the same process.

Network filesystem behavior is a major risk. Dot-file, AFP, NFS, flock, no-op, and proxy styles all trade off correctness and concurrency differently. Autodetection depends on `statfs()` results and probing `fcntl()`. A wrong choice can cause database corruption, poor concurrency, or severe performance loss.

The no-op lock style is intentionally unsafe for multiple writers. It is appropriate only for read-only databases or when external synchronization is guaranteed. Any path that accidentally selects `nolockIoMethods` for a writable shared database is high risk.

WAL shared memory depends on all processes using the same shm path and compatible build flags. `SQLITE_SHM_DIRECTORY` can redirect shm files away from the database directory; comments state this is unsupported and incompatible across builds because two processes may then coordinate through different shm files.

`unixShmLock()` maintains both process-local lock masks and OS locks. Bugs in sibling-mask conflict detection can permit incompatible locks in one process even if OS-level locks would not catch them. Conversely, failure to release system locks when the last local holder unlocks can wedge WAL access.

Short-read semantics are deliberate. Both OS/2 and Unix zero-fill unread portions and return `SQLITE_IOERR_SHORT_READ`. Pager callers must treat this as a recoverable condition in cases where reading beyond EOF is expected.

`unixSync()` ignores directory fsync failures in some cases by design, based on historical filesystem behavior. This reduces false failures but weakens the diagnostic signal for filesystems where directory sync really is required for crash durability.

The Apple MS-DOS filesystem workaround in `findInodeInfo()` writes one byte to zero-size files so that inode numbers become stable. `unixFileSize()` then reports size 0 when the actual size is 1. This is subtle cross-layer state; changes can affect empty-database open behavior.

Compile-gated paths deserve direct scrutiny. In the `HAVE_POSIX_FALLOCATE` branch, the shown amalgamation contains suspicious code in `fcntlSizeHint()` (`pFile->.h` and assignment-like `errno=EINTR`) and the `osFallocate` macro text is malformed-looking. These may be hidden on builds without `HAVE_POSIX_FALLOCATE`, but enabling that feature should be compile-tested.

`unixNextSystemCall()` appears to iterate using `aSyscall[0]` instead of `aSyscall[i]` in the loop body. That would make system-call enumeration return the first entry repeatedly rather than the next live syscall, reducing the usefulness of the VFS override introspection API.

`proxyCreateUnixFile()` allocates `pUnused` before some error returns. The `fd<0` branch that returns `SQLITE_BUSY`, `SQLITE_PERM`, `SQLITE_IOERR_LOCK`, or `SQLITE_CANTOPEN_BKPT` should be checked for leaks of that allocation in the compiled proxy-lock path.

`proxyBreakConchLock()` reports directly to `stderr`. That is unusual in a library VFS path and can surprise embedders. It also relies on atomic-enough rename semantics and on the conch contents being long enough and version-compatible.

The chunk ends inside `proxyConchLock()`. Any conclusion about full proxy-lock correctness, conch upgrade/downgrade persistence, and proxy method close/unlock behavior requires the next chunk.

## Test Signals

Hash-table tests should cover case-insensitive key lookup, insertion without key copying, replacement returning old data, deletion by inserting null data, resizing under benign malloc failure, and clearing after the final removal.

OS/2 coverage, if the platform is supported, should exercise read/write/truncate/sync/file-size operations, short-read zero fill, lock escalation and unlock, reserved-lock probing, delete-on-close, UTF-8 to codepage path conversion, temp-file naming, dynamic extension loading, randomness, fake current time, and simulated I/O/disk-full errors.

Unix file-I/O tests should cover read-only fallback, exclusive create with `O_NOFOLLOW`, temp-file creation, delete-on-close unlinking, directory fsync for journals and WAL files, short reads, partial writes, disk-full simulation, chunk-size and size-hint behavior, file-size after truncation, access checks treating zero-size files as non-existent for existence checks, and full path resolution after current-directory errors.

Locking tests should cover POSIX same-process multiple connections on hard links or symlinks to the same inode, shared-to-reserved-to-exclusive transitions, failed exclusive leaving pending state, downgrade to shared, close with outstanding locks, reuse of deferred descriptors, and lock conflict translation from errno to `SQLITE_BUSY` or I/O codes.

Alternative locking tests should exercise dot-lock stale files, `flock()` contention, VxWorks semaphore contention if available, AFP shared-byte selection and reserved-lock tracking, NFS downgrade behavior, read-only filesystem autoselection, and explicit `unix-none`/external-synchronization scenarios.

WAL tests should cover shm file creation and truncation under the dead-man switch, mapping region 0 without extension, extending to later regions, heap-backed shared memory under `unix-excl`, shared and exclusive shm locks across sibling connections, unmap with and without delete, and recovery from mmap/ftruncate/open failures.

System-call override tests should call `xSetSystemCall`, `xGetSystemCall`, and `xNextSystemCall`, inject failing `open`, `fcntl`, `ftruncate`, `pread`, `pwrite`, and `close` behavior, and verify `lastErrno` and SQLite result-code mapping.

Proxy-lock tests for Apple builds should cover `:auto:` path generation, lock directory creation, helper `unixFile` creation, read-only fallback, simulated alternate host IDs, stale conch break decisions, conch modification-time races, and allocation cleanup on open failures. Full proxy-lock tests need the following chunk as well.

Portability build tests should compile this amalgamation with combinations of `SQLITE_OS_OS2`, `SQLITE_OS_UNIX`, `SQLITE_ENABLE_LOCKING_STYLE`, `SQLITE_OMIT_WAL`, `OS_VXWORKS`, `__APPLE__`, `HAVE_POSIX_FALLOCATE`, `USE_PREAD`, `USE_PREAD64`, `SQLITE_NO_SYNC`, and `SQLITE_TEST` to expose compile-gated branches that normal Linux builds skip.
