# sources/storage-engines/sqlite/src/os_unix.c lines 7630-8604

## Scope

This chunk covers the end of SQLite's Unix VFS implementation. The first major section is the Apple-only proxy-locking implementation for AFP-style deployments, where database locks are redirected through a local proxy lock file coordinated by a "conch" file beside the database. The second section is `sqlite3_os_init()` and `sqlite3_os_end()`, the public Unix OS interface entry points that register available Unix VFS names, allocate static VFS mutexes, validate shared-memory lock layout assumptions, and initialize temporary-file directory state.

## Purpose

- Maintain and acquire proxy-locking conch files that record the owning host id and the selected local proxy lock-file path.
- Detect and break stale conch locks when the same host id still owns an unchanged conch file after retry delays.
- Transform an already-open `unixFile` into a proxy-locking file by replacing its `sqlite3_io_methods` table and preserving the original methods/context for close-time restoration.
- Expose `SQLITE_FCNTL_GET_LOCKPROXYFILE` and `SQLITE_FCNTL_SET_LOCKPROXYFILE` behavior through proxy-file control.
- Implement proxy `xCheckReservedLock`, `xLock`, `xUnlock`, and `xClose` by first taking the conch and then delegating real byte-range locking to the proxy lock file.
- Register the platform-appropriate Unix VFS implementations under names such as `unix`, `unix-none`, `unix-dotfile`, `unix-excl`, `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, and `unix-proxy`.
- Set up Unix VFS global mutex pointers and temp-file directory state at SQLite initialization, and clear mutex globals at shutdown.

## Important APIs, Types, And Functions

- `proxyGetHostID()` finishes in this chunk. On builds with `HAVE_GETHOSTUUID`, it calls `gethostuuid()` with a one-second timeout, reports `errno` through `pError`, and returns `SQLITE_IOERR` on failure. In `SQLITE_TEST`, `sqlite3_hostid_num` perturbs the first host-id byte to simulate multiple hosts.
- `PROXY_CONCHVERSION`, `PROXY_HEADERLEN`, `PROXY_PATHINDEX`, and `PROXY_MAXCONCHLEN` define the on-disk conch record as a one-byte version, a 16-byte host id, and a path string bounded by `MAXPATHLEN`.
- `proxyBreakConchLock(unixFile *pFile, uuid_t myHostID)` copies the current conch contents to a sibling `-break` file, renames that file over the conch path, replaces the open conch descriptor, and closes the old descriptor. `myHostID` is accepted for call-site symmetry but is unused here; the host-id check happens in `proxyConchLock()`.
- `proxyConchLock(unixFile *pFile, uuid_t myHostID, int lockType)` wraps conch-file `xLock()` calls with retry, modification-time checks, host-id verification, and stale-lock breaking.
- `proxyTakeConch(unixFile *pFile)` is the core conch acquisition routine. It reads or creates the conch payload, chooses or validates the proxy lock path, obtains any needed exclusive conch lock, writes and fsyncs updated conch contents, reopens the database descriptor, opens the proxy lock file, and marks `pCtx->conchHeld`.
- `proxyReleaseConch()` unlocks the conch file back to `NO_LOCK` when the proxy context actually holds it.
- `proxyCreateConchPathname(char *dbPath, char **pConchPath)` derives the conch pathname by inserting a dot before the database basename and appending `-conch`, allocating the result with `sqlite3_malloc64()`.
- `switchLockProxyPath()` changes an existing proxy context to a new explicit proxy path only when the database file is currently unlocked. It closes and frees the old proxy lock file and path before storing the new path.
- `proxyGetDbPathForUnixFile()` reconstructs the database path from the pre-proxy locking context. AFP stores it in `afpLockingContext.dbPath`, dotlock stores a dot-lock path that must be trimmed by `DOTLOCK_SUFFIX`, and other styles store the database path directly.
- `proxyTransformUnixFile()` allocates and initializes `proxyLockingContext`, opens the conch file, handles read-only filesystem lockless mode, stores optional explicit lock-proxy path and database path copies, preserves the old methods/context, and installs `proxyIoMethods`.
- `proxyFileControl()` handles proxy-specific file controls: get lock-proxy file, set/switch lock-proxy file, turn proxy locking on, and reject turning proxy locking off once enabled.
- `proxyCheckReservedLock()`, `proxyLock()`, and `proxyUnlock()` are the lock-related methods in `proxyIoMethods`; each calls `proxyTakeConch()` and delegates to `pCtx->lockProxy` if `conchHeld>0`.
- `proxyClose()` closes the proxy lock file, releases and closes the conch file, frees proxy paths and context, restores the original `lockingContext`/`pMethod`, then calls the original close method.
- `sqlite3_os_init()` builds a static mutable `sqlite3_vfs aVfs[]` array using the local `UNIXVFS` initializer macro and registers every compiled-in Unix VFS with SQLite core.
- `sqlite3_os_end()` clears `unixBigLock` and, on VxWorks, `vxworksMutex`, then returns `SQLITE_OK`.

## Control Flow

`proxyConchLock()` first tries the requested conch-file lock through the conch file's own I/O methods. If it sees `SQLITE_BUSY`, it records the conch modification time, sleeps for 0.5 seconds, and retries. On the second busy result, it fails immediately if the modification time changed. If the timestamp is stable, it reads the conch record and only proceeds when the record is long enough, has `PROXY_CONCHVERSION`, and contains the current host id. It then waits 10 seconds and retries. On the third busy result, it calls `proxyBreakConchLock()` and, when breaking succeeds, reacquires a shared lock first for exclusive-lock requests before requesting the final lock type.

`proxyTakeConch()` returns early when `pCtx->conchHeld` is non-zero, so a held conch or read-only lockless state is stable across later lock calls. Otherwise it obtains the current host id, takes a shared conch lock, and reads the conch record. Short reads or version mismatches set `createConch`, while valid records are compared against the current host id and the configured lock-proxy path.

For `:auto:` proxy paths, a matching host id lets SQLite reuse the lock path stored in the conch. If opening that old path later fails for reasons other than `SQLITE_NOMEM`, the routine loops once with `forceNewLockPath` and generates a fresh automatic path with `proxyGetLockPath()`. For explicit proxy paths, both host id and path content must match to accept the existing conch record. When the conch must be changed, read-only conch descriptors fail with `SQLITE_BUSY`; writable conches take an exclusive conch lock, write the version/host/path record, truncate the file to the exact record length, and call `full_fsync()`. Newly created conch files attempt to inherit database read/write permission bits with `fchmod()`.

After conch validation or update, `proxyTakeConch()` reopens the database file using the original `pFile->openFlags`. It then opens the proxy lock file through `proxyCreateUnixFile()`, duplicates any stack/extracted path into `pCtx->lockProxyPath`, marks `conchHeld=1`, and patches AFP proxy contexts so `afpCtx->dbPath` points at the selected lock-proxy path. On failure it unlocks the conch to `NO_LOCK`.

`proxyTransformUnixFile()` is the activation path for proxy locking. It refuses to operate unless the file is unlocked, derives the database path from the current locking style, allocates a new proxy context, derives and opens the conch path, optionally enters lockless mode for read-only opens on read-only filesystems without a conch file, stores the database path, and finally swaps `pFile->pMethod` to `proxyIoMethods`. Any failure before the swap closes the conch file and frees the partially built context.

The proxy I/O methods are thin after conch acquisition. `proxyCheckReservedLock()` delegates to `lockProxy->pMethod->xCheckReservedLock()`. `proxyLock()` and `proxyUnlock()` delegate to the proxy lock file and then mirror `proxy->eFileLock` back into the database `unixFile`. In lockless mode (`conchHeld<0`), these methods do not acquire a proxy lock; `proxyCheckReservedLock()` intends to report no reserved lock.

`sqlite3_os_init()` defines the `UNIXVFS` macro locally, constructs the compiled-in VFS list, asserts that the syscall shim table has the expected size, and registers each VFS. The first VFS in the array becomes the default unless `SQLITE_DEFAULT_UNIX_VFS` names a matching entry. Optional KV VFS initialization runs after registration. The routine then allocates static mutex slots, validates WAL shared-memory lock offsets in non-`SQLITE_OMIT_WAL` builds, initializes the temp-directory list, and returns `SQLITE_OK`.

## State And Persistence Behavior

- Conch files persist beside the database with a transformed name such as `.database-conch`. Their content persists the proxy-lock format version, host id, and lock-proxy path.
- Proxy lock files persist separately, usually under the Darwin user temp directory or configured `LOCKPROXYDIR`, with database path characters transformed by the earlier `proxyGetLockPath()` helper and a `:auto:` suffix for automatic names.
- `proxyLockingContext` owns `conchFile`, `conchFilePath`, `lockProxy`, `lockProxyPath`, `dbPath`, `conchHeld`, the old locking context, and the old I/O methods. This context replaces the original `unixFile.lockingContext` until `proxyClose()` restores it.
- `pCtx->conchHeld` is tri-state in practice: `0` means not held, `1` means conch lock and proxy file are active, and `-1` means read-only filesystem lockless mode.
- `proxyTakeConch()` can close and reopen `pFile->h` to avoid stale descriptors after conch changes or lock-path selection.
- Conch updates are durable at the file level: the code truncates the conch, writes the exact payload through `unixWrite()`, and calls `full_fsync()`.
- When creating a conch file, the code tries to copy database user/group/other read-write permission bits to the conch file. Failures are ignored in non-debug builds.
- `sqlite3_os_init()` stores a static `aVfs[]` array whose `pNext` links are later modified by SQLite core registration. This is process-global registration state, not database-file state.
- `unixBigLock` and `vxworksMutex` are global static mutex pointers allocated during OS init and nulled during OS end. `sqlite3_os_end()` does not free filesystem artifacts.
- `unixTempFileInit()` initializes process-local temp-directory discovery state used by later Unix temp-file operations.

## Dependencies And Integration Points

- The whole proxy-locking block is compiled only for `defined(__APPLE__) && SQLITE_ENABLE_LOCKING_STYLE`, matching the comment that proxy locking is intended for AFP filesystems on macOS.
- Proxy locking depends on the surrounding `proxyLockingContext` definition and earlier helpers `proxyGetLockPath()`, `proxyCreateLockPath()`, and `proxyCreateUnixFile()`.
- The conch and proxy lock files are regular `unixFile` objects filled by `fillInUnixFile()` with a dummy VFS whose finder is `autolockIoFinder`, so their actual locking methods may be AFP, dotfile, flock, POSIX, or other compiled-in styles depending on filesystem detection.
- The proxy methods integrate with the `IOMETHODS()` macro earlier in the file, where `proxyIoMethods` is declared with `proxyClose`, `proxyLock`, `proxyUnlock`, and `proxyCheckReservedLock` and with shared-memory support disabled.
- `unixFileControl()` routes the proxy-specific `SQLITE_FCNTL_GET_LOCKPROXYFILE` and `SQLITE_FCNTL_SET_LOCKPROXYFILE` opcodes to `proxyFileControl()` for files using the proxy method or for activation requests.
- Lock constants `NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, and `EXCLUSIVE_LOCK` follow SQLite's common pager/VFS locking contract; proxy locking preserves the database file's visible `eFileLock` by mirroring the proxy lock file state.
- `proxyTakeConch()` uses low-level OS wrappers and SQLite helpers including `osPread`, `osPwrite`, `seekAndRead`, `robust_open`, `robust_close`, `robust_ftruncate`, `storeLastErrno`, `unixWrite`, `full_fsync`, `osFstat`, `osFchmod`, `osStat`, `futimes`, `statfs`, and `unixSleep`.
- `sqlite3_os_init()` integrates this file with SQLite core by calling `sqlite3_vfs_register()`. Its VFS method table points at Unix VFS entry points from earlier in the file: `unixOpen`, `unixDelete`, `unixAccess`, `unixFullPathname`, dynamic loader methods, randomness, sleep/time methods, last-error reporting, and syscall override APIs.
- Build flags determine VFS availability: Apple locking-style builds expose autolock, AFP, NFS, flock, and proxy variants; VxWorks exposes named semaphores and its own default finder; generic Unix uses POSIX by default plus no-lock, dotfile, exclusive, and sometimes explicit POSIX/flock names.
- Optional `SQLITE_OS_KV_OPTIONAL` integrates `sqlite3KvvfsInit()` into OS initialization.
- Non-`SQLITE_OMIT_WAL` builds rely on the asserted relationship among `SQLITE_SHM_NLOCK`, `UNIX_SHM_BASE`, and `UNIX_SHM_DMS` because WAL shared-memory locking uses fixed byte offsets.

## Risks And Edge Cases

- `proxyBreakConchLock()` assumes the conch path ends with a five-character `conch` suffix and rewrites the last five characters to `break`. Unexpected path shapes fail with a path error, but the logic is tightly coupled to `proxyCreateConchPathname()`.
- Stale conch breaking depends on filesystem modification timestamps and host-id equality. Coarse timestamp resolution, clock/filesystem anomalies, or host-id duplication could cause either false busy results or unsafe lock breaking.
- The conch format stores a path without an explicit trailing NUL in the on-disk record length. Readers cap the copied path and add a local NUL, but path comparison for explicit proxy paths uses `strncmp()` with `readLen-PROXY_PATHINDEX`, so malformed or prefix-like records deserve regression coverage.
- `proxyTakeConch()` calls `futimes(conchFile->h, NULL)` before exclusive locking so other contenders can observe modification-time movement. A failure is ignored, which may weaken stale-lock detection on filesystems where `futimes()` is unsupported or unreliable.
- If another thread in the same process holds a shared conch lock (`pInode->nShared>1`), upgrading to exclusive returns `SQLITE_BUSY`. This avoids self-deadlock but means same-process proxy-lock users can block path changes or conch rewrites.
- `proxyCreateUnixFile()` returns `SQLITE_BUSY` for lock-file open failures after read-write and read-only attempts. `proxyTakeConch()` only retries automatic path generation for old conch paths and non-`SQLITE_NOMEM` failures, so persistent permission/path problems may surface as busy rather than cantopen.
- The lockless read-only filesystem path sets `conchHeld=-1`. In this mode proxy `xLock` and `xUnlock` become no-ops, which is only safe for genuinely read-only database access on read-only media.
- In `proxyCheckReservedLock()`, the lockless branch assigns `pResOut=0` instead of `*pResOut=0`. That statement only changes the local pointer variable and leaves the caller's output untouched, so lockless reserved-lock checks depend on caller initialization or are a latent bug signal.
- `switchLockProxyPath()` can allocate `lockProxyPath` with `sqlite3DbStrDup()` without checking for NULL before returning `SQLITE_OK`. Later conch acquisition may fail or behave as `:auto:` if allocation failed.
- `proxyClose()` returns immediately on unlock/close errors before freeing later resources or restoring original methods. This preserves error reporting but can leave cleanup incomplete if lower-level close operations fail.
- `proxyFileControl()` rejects turning off proxy locking once enabled. Callers that expect `SQLITE_FCNTL_SET_LOCKPROXYFILE` with NULL to disable proxy locking will receive `SQLITE_ERROR`.
- The static assertion `ArraySize(aSyscall)==29` is a maintenance tripwire: adding or removing syscall shim entries elsewhere requires updating this expected count.
- VFS default selection depends on compile-time flags and registration order. Changing `aVfs[]` order or `SQLITE_DEFAULT_UNIX_VFS` handling can alter the default locking behavior for all Unix opens.
- WAL offset assertions are not runtime compatibility negotiation. If constants drift, debug builds fail early; release builds still rely on the same fixed layout.

## Test Signals

- Apple locking-style builds should exercise `unix-proxy` open, close, shared/reserved/exclusive lock transitions, unlock transitions, and reserved-lock checks with a real or mocked proxy lock file.
- `SQLITE_FCNTL_SET_LOCKPROXYFILE` should be covered for activating proxy locking on an unlocked file, switching to a new explicit path while unlocked, no-op behavior for `:auto:` and matching paths, `SQLITE_BUSY` when switching while locked, and `SQLITE_ERROR` when trying to disable proxy locking after activation.
- `SQLITE_FCNTL_GET_LOCKPROXYFILE` should return NULL for non-proxy files, `:auto: (not held)` before an automatic conch path is resolved, and the resolved `lockProxyPath` after conch acquisition.
- Conch-format tests should cover new conch creation, valid host/path reuse, short reads, wrong version bytes, mismatched host ids, explicit path mismatches, and automatic path fallback when a stale conch path cannot be opened.
- Stale-lock tests should simulate repeated `SQLITE_BUSY`, stable and changing conch modification times, matching and mismatching host ids, and successful/failed `proxyBreakConchLock()` rename paths.
- Permission tests should verify that newly created conch files try to inherit database read/write permission bits and that failure to chmod does not abort normal non-debug operation.
- Read-only filesystem tests should cover the branch where the conch does not exist, the database is opened read-only, `statfs()` reports `MNT_RDONLY`, and proxy locking enters `conchHeld=-1` lockless mode.
- OOM and allocation-failure tests should target `proxyCreateConchPathname()`, `proxyTransformUnixFile()`, `sqlite3DbStrDup()` of proxy/database paths, and `proxyCreateUnixFile()` allocation of `unixFile` and `UnixUnusedFd`.
- Close-error tests should verify how proxy resources behave if unlocking or closing the proxy lock file or conch file fails.
- VFS registration tests should verify compiled-in VFS name availability for generic Unix, VxWorks, and Apple locking-style configurations, and that `SQLITE_DEFAULT_UNIX_VFS` selects the named default when configured.
- Initialization tests should run with WAL enabled to hit the shared-memory offset assertions in debug builds, and with `SQLITE_OS_KV_OPTIONAL` to ensure KV VFS initialization still composes with Unix VFS registration.
