# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 47009-55194

## Scope And Purpose

This chunk spans several SQLite amalgamation module boundaries. It begins at the end of the Unix VFS initializer, covers the full Windows VFS implementation (`os_win.c`), then covers the full in-memory database VFS and serialization/deserialization support (`memdb.c`), the full sparse bitmap utility (`bitvec.c`), and the opening comments for the page-cache module (`pcache.c`).

Within the WiredTiger test tree this is vendored SQLite infrastructure used by SQLite tests and by any embedded SQLite execution in the test harness. The code is not WiredTiger-specific, but it is foundational portability logic: it binds SQLite's abstract `sqlite3_vfs` and `sqlite3_io_methods` interfaces to Windows file APIs, implements an optional heap allocator backed by Win32 heaps, supplies public Win32 path/encoding helpers, implements WAL shared-memory on Windows, provides an in-memory VFS used by `sqlite3_serialize()` and `sqlite3_deserialize()`, and implements the `Bitvec` data structure used by pager/transaction code to track page sets.

The chunk ends immediately after the introductory `pcache.c` comments start describing dirty and clean page cache entries. No page-cache implementation is visible in this chunk.

## Unix VFS Tail

The first lines complete Unix VFS registration. The `UNIXVFS(VFSNAME, FINDER)` macro constructs `sqlite3_vfs` objects whose methods point to Unix VFS functions such as `unixOpen`, `unixDelete`, `unixAccess`, `unixFullPathname`, dynamic-loading methods, randomness, sleep, current time, last error, and system-call override hooks. The `aVfs[]` array registers platform-conditional variants including `unix`, `unix-none`, `unix-dotfile`, `unix-excl`, and optional Apple/VxWorks variants such as `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, `unix-proxy`, and `unix-namedsem`.

`sqlite3_os_init()` for Unix registers every VFS in `aVfs[]`, optionally honoring `SQLITE_DEFAULT_UNIX_VFS`, initializes the key-value optional VFS, allocates `unixBigLock`, asserts WAL shared-memory lock byte assumptions, initializes the temp-file directory array, and returns `SQLITE_OK`. `sqlite3_os_end()` for Unix just clears `unixBigLock`. This section integrates with the SQLite core via `sqlite3_vfs_register()` and the global OS lifecycle hooks.

## Windows VFS Data Model

The Windows VFS is compiled under `SQLITE_OS_WIN`. It defines platform availability macros for ANSI and wide APIs, WinRT/WinCE differences, long-path limits, file mapping availability, and deprecated `GetVersionEx` behavior. Many declarations are compile-time gated by `SQLITE_OS_WINNT`, `SQLITE_OS_WINCE`, `SQLITE_OS_WINRT`, `SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_WIN32_MALLOC`, and related feature flags.

Important types in this chunk:

- `winFile`: the concrete subclass of `sqlite3_file`. It stores the Windows `HANDLE`, current SQLite lock level, chosen shared lock byte, control flags (`WINFILE_RDONLY`, `WINFILE_PERSIST_WAL`, `WINFILE_PSOW`), last Win32 error, path, chunk-size hint, optional WAL `winShm`, optional WinCE lock state, optional memory-map state, and optional blocking-lock timeout fields.
- `winVfsAppData`: per-VFS app-data that selects an I/O method table and whether locking is disabled.
- `winceLock`: WinCE-only shared locking state, with reader count and pending/reserved/exclusive booleans.
- `winMemData`: optional Win32 heap allocator state with heap handle, ownership flag, and debug magic values.
- `winShmNode` and `winShm`: WAL shared-memory backing state. `winShmNode` represents the process-wide mapped `*-shm` file and tracks regions, locks, reference count, and read-only/unlocked state. `winShm` is per-open-file shared-memory connection state with lock masks and its own lock handle.
- `EntropyGatherer`: a small randomness accumulator used by `winRandomness()`.

## System Call Indirection

The large `aSyscall[]` table maps symbolic names to overridable Windows and Cygwin system-call pointers. Entries include file APIs (`CreateFileW`, `ReadFile`, `WriteFile`, `DeleteFileW`, `GetFileAttributesExW`, `LockFileEx`, `UnlockFileEx`), heap APIs (`HeapAlloc`, `HeapCreate`, `HeapDestroy`, `HeapReAlloc`, `HeapCompact`), mapping APIs (`CreateFileMapping*`, `MapViewOfFile*`, `FlushViewOfFile`, `UnmapViewOfFile`), dynamic loader APIs, timers, randomness inputs, WinRT APIs, UUID APIs, blocking-lock helpers, and Cygwin helpers (`getenv`, `getcwd`, `readlink`, `lstat`, `cygwin_conv_path`).

`winSetSystemCall()`, `winGetSystemCall()`, and `winNextSystemCall()` implement the `sqlite3_vfs` system-call override API. They allow tests and embedders to inject failures, restore defaults, and enumerate active calls. The `sqlite3_os_init()` assertion that `ArraySize(aSyscall)==89` is a strong test signal that any edit to the table must be accompanied by count updates and wrapper consistency.

## Win32 Memory Allocator

When `SQLITE_WIN32_MALLOC` is enabled, SQLite installs a `sqlite3_mem_methods` implementation backed by either an isolated Win32 heap or the process heap:

- `winMemMalloc()`, `winMemFree()`, `winMemRealloc()`, and `winMemSize()` wrap `HeapAlloc`, `HeapFree`, `HeapReAlloc`, and `HeapSize`, validate debug magic, optionally validate heap integrity, and log Win32 errors through `sqlite3_log()`.
- `winMemInit()` creates an isolated heap when configured, with initial and maximum sizes derived from SQLite global heap/cache settings, or falls back to `GetProcessHeap()`.
- `winMemShutdown()` destroys owned heaps and clears allocator state.
- `sqlite3MemGetWin32()` returns the method table and `sqlite3MemSetDefault()` registers it through `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)`.
- Public helpers `sqlite3_win32_compact_heap()` and `sqlite3_win32_reset_heap()` compact or recreate the heap. Reset is guarded by main and memory mutexes and requires the heap to be owned and `sqlite3_memory_used()==0`.

Risk is concentrated around allocator ownership and lifecycle: `winMemShutdown()` can invalidate all allocations from the isolated heap, so callers must only reset/shutdown under the mutex and zero-allocation conditions enforced here.

## Encoding, Directories, Error Reporting, And Retry Policy

The Windows VFS converts between UTF-8, UTF-16, and ANSI/OEM code pages using SQLite heap allocation:

- `winUtf8ToUnicode()`, `winUnicodeToUtf8()`, `winMbcsToUnicode()`, `winUnicodeToMbcs()`, `winMbcsToUtf8()`, and `winUtf8ToMbcs()` are the internal conversion primitives.
- Public wrappers include `sqlite3_win32_utf8_to_unicode()`, `sqlite3_win32_unicode_to_utf8()`, `sqlite3_win32_mbcs_to_utf8()`, `sqlite3_win32_mbcs_to_utf8_v2()`, `sqlite3_win32_utf8_to_mbcs()`, and `sqlite3_win32_utf8_to_mbcs_v2()`. With API armor, null pointers return misuse.
- `sqlite3_win32_set_directory8()`, `sqlite3_win32_set_directory16()`, and `sqlite3_win32_set_directory()` update `sqlite3_data_directory` or `sqlite3_temp_directory` under `SQLITE_MUTEX_STATIC_TEMPDIR`.

`winGetLastErrorMsg()` converts `FormatMessageW/A()` output into UTF-8. `winLogErrorAtLine()` logs a normalized SQLite error code, Win32 code, function name, path, source line, and message. I/O retry behavior is controlled by `winIoerrRetry`, `winIoerrRetryDelay`, `winIoerrCanRetry1()`, optional `winIoerrCanRetry2()`, `winRetryIoerr()`, and `winLogIoerr()`. The retry policy is aimed at transient sharing, antivirus, device, and network errors. `SQLITE_FCNTL_WIN32_AV_RETRY` exposes the retry count and delay for tuning.

## Windows File I/O And Locking

The main `sqlite3_io_methods` implementation is `winIoMethod`; `winIoNolockMethod` swaps in no-op locking functions but keeps the same read/write/truncate/sync/file-control/mmap methods.

Core file operations:

- `winClose()` unmaps memory, retries `CloseHandle()`, handles WinCE delete-on-close cleanup, destroys WinCE lock state, updates the open counter, and logs close failures.
- `winRead()` uses memory mapping when possible, then `ReadFile()` with overlapped offsets except on WinCE/no-overlapped builds. Short reads zero-fill the unread tail and return `SQLITE_IOERR_SHORT_READ`.
- `winWrite()` optionally writes through an mmap region when writable mapping is enabled, otherwise loops until all bytes are written or an unretryable error occurs. Disk-full Win32 errors map to `SQLITE_FULL`; other failures map to `SQLITE_IOERR_WRITE`.
- `winTruncate()` honors `SQLITE_FCNTL_CHUNK_SIZE`, avoids truncation while `xFetch` mappings are outstanding, unmaps/remaps around `SetEndOfFile()`, and treats `ERROR_USER_MAPPED_FILE` specially.
- `winSync()` flushes mapped views first, then calls `FlushFileBuffers()`, unless `SQLITE_NO_SYNC` is defined. Test counters `sqlite3_sync_count` and `sqlite3_fullsync_count` are incremented under `SQLITE_TEST`.
- `winFileSize()`, `winHandleSeek()`, `winSeekFile()`, `winHandleTruncate()`, `winHandleSize()`, and `winHandleClose()` provide reusable handle-level helpers.

Locking maps SQLite's `NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, and `EXCLUSIVE_LOCK` protocol to Windows byte-range locks. `winLock()` enforces legal transitions, temporarily uses the pending byte while acquiring shared locks, upgrades through pending to exclusive, and falls back to read-lock reacquisition on exclusive-lock failure. `winUnlock()` drops exclusive/shared/reserved/pending byte locks to `SHARED_LOCK` or `NO_LOCK`. `winCheckReservedLock()` probes the reserved byte when the local descriptor does not already hold it.

WinCE lacks native byte-range locking, so `winceCreateLock()`, `winceDestroyLock()`, `winceLockFile()`, and `winceUnlockFile()` emulate lock state with a named mutex and shared file mapping. `winLockFile()` and `winUnlockFile()` route to WinCE emulation, `LockFileEx`/`UnlockFileEx`, or older ANSI APIs depending on platform. `winHandleLockTimeout()` adds optional blocking-lock support via overlapped `LockFileEx()`, events, `WaitForSingleObject`, timeout mapping, and `CancelIo()`.

The no-lock methods (`winNolockLock()`, `winNolockUnlock()`, `winNolockCheckReservedLock()`) are intentionally unsafe for concurrent writers and are only appropriate for read-only/external-locking cases.

## Windows File Control, mmap, And Device Capabilities

`winFileControl()` implements important `xFileControl` operations:

- `SQLITE_FCNTL_LOCKSTATE`, `SQLITE_FCNTL_LAST_ERRNO`, `SQLITE_FCNTL_CHUNK_SIZE`, and `SQLITE_FCNTL_SIZE_HINT`.
- `SQLITE_FCNTL_PERSIST_WAL` and `SQLITE_FCNTL_POWERSAFE_OVERWRITE` through `winModeBit()`.
- `SQLITE_FCNTL_VFSNAME`, `SQLITE_FCNTL_WIN32_AV_RETRY`, `SQLITE_FCNTL_WIN32_GET_HANDLE`, test-only `SQLITE_FCNTL_WIN32_SET_HANDLE`, `SQLITE_FCNTL_NULL_IO`, and `SQLITE_FCNTL_TEMPFILENAME`.
- `SQLITE_FCNTL_MMAP_SIZE`, which caps against `sqlite3GlobalConfig.mxMmap`, handles 32-bit `SIZE_T` limits, and remaps when safe.
- Optional `SQLITE_FCNTL_LOCK_TIMEOUT` and `SQLITE_FCNTL_BLOCK_ON_CONNECT`.

`winSectorSize()` returns `SQLITE_DEFAULT_SECTOR_SIZE`. `winDeviceCharacteristics()` advertises undeletable-when-open and subpage-read, plus powersafe-overwrite when enabled.

Memory-mapped database reads use `winMapfile()`, `winUnmapfile()`, `winFetch()`, and `winUnfetch()`. Mapping size is capped by `mmapSizeMax`, aligned to `winSysInfo.dwPageSize`, and degraded gracefully: create/map failures are logged but normal `xRead`/`xWrite` continues. `winFetch()` requires an extra 256 bytes beyond the requested range to tolerate small parser overreads of corrupt pages and increments `nFetchOut` until `winUnfetch()` releases it.

## Windows WAL Shared Memory

When WAL is enabled, the Windows VFS implements `xShmMap`, `xShmLock`, `xShmBarrier`, and `xShmUnmap`.

`winOpenSharedMemory()` creates or reuses a process-wide `winShmNode` for the `*-shm` path, opens one handle used for mapping and DMS-lock work plus a per-connection handle for locks, initializes node mutexes, and tracks per-node references under `winBigLock`. `winShmPurge()` destroys zero-reference nodes, unmaps all mapped regions, closes mapping handles, optionally deletes the `*-shm` file, and removes the node from `winShmNodeList`.

`winLockSharedMemory()` implements the deadman-switch protocol: it tries for an exclusive DMS lock to detect first opener, truncates the shared-memory file to zero when allowed, releases that lock, then takes a shared DMS lock. Read-only openers that would need initialization return `SQLITE_READONLY_CANTINIT`.

`winShmLock()` maps SQLite shared/exclusive WAL lock requests to byte-range locks beginning at `WIN_SHM_BASE`. It tracks local shared and exclusive lock masks in `winShm`, supports blocking lock timeouts through `winFileBusyTimeout()`, and asserts valid lock-ordering in debug builds. `winShmMap()` lazily creates/truncates the `*-shm` file, grows the `aRegion` array, creates file mappings, maps each region with allocation-granularity offset adjustment, and returns a pointer adjusted to the requested region. If the node is read-only, successful mapping returns `SQLITE_READONLY`.

## Windows VFS Methods And Lifecycle

`winGetTempname()` creates `etilqs_` temporary filenames from `sqlite3_temp_directory`, Cygwin environment variables, Win32 temp paths, or fallbacks, and appends 15 randomized characters salted with the process id. `winIsDir()` checks directory attributes. `winOpen()` converts UTF-8 names to native encoding, rejects directories, translates SQLite open flags to access/share/create/attribute flags, creates temp names when needed, retries transient open failures, downgrades read-write opens to read-only when possible, initializes WinCE locks, sets `winFile` fields and mmap defaults, and returns output flags. The URI parameter `exclusive=1` disables file sharing; `psow` toggles powersafe overwrite for main DBs.

`winDelete()` converts names, rejects directories, retries transient delete failures, maps missing files to `SQLITE_IOERR_DELETE_NOENT`, and logs non-benign failures. `winAccess()` checks existence/read/read-write attributes, treats zero-length files as non-existent for `SQLITE_ACCESS_EXISTS`, and supports the internal `NORETRY` bit to avoid nested antivirus retry loops during `winOpen()` fallback checks.

Path handling includes `winIsLongPathPrefix()`, `winIsDriveLetterAndColon()`, `winIsVerbatimPathname()`, Cygwin `winSimplifyName()`/`mkFullPathname()`, and `winFullPathnameNoMutex()`. Long and UNC paths, `/C:` prefixes, `sqlite3_data_directory`, WinCE/WinRT limitations, Cygwin symlink following, and ANSI/wide full-path APIs are all handled. `winFullPathname()` serializes this through the temp-directory mutex because global directory variables are involved.

Dynamic loading is implemented by `winDlOpen()`, `winDlError()`, `winDlSym()`, and `winDlClose()` unless extension loading is omitted. `winRandomness()` gathers entropy from system time, process id, tick counter, performance counter, and optionally UUID APIs; test or randomness-omitted builds return zero-filled buffers. `winSleep()` rounds microseconds up to milliseconds and calls `sqlite3_win32_sleep()`. `winCurrentTimeInt64()` converts `FILETIME` to SQLite Julian-day milliseconds, with `sqlite3_current_time` overriding under `SQLITE_TEST`; `winCurrentTime()` returns the double Julian-day form. `winGetLastError()` returns `GetLastError()` and formats it if a buffer is provided.

Windows `sqlite3_os_init()` registers four VFS names when available: `win32` as default, `win32-longpath`, `win32-none`, and `win32-longpath-none`. It initializes `winSysInfo` for page size and mapping granularity and allocates `winBigLock` for WAL. `sqlite3_os_end()` closes the WinRT sleep event if allocated and clears `winBigLock`.

## Memdb VFS And Serialization

The `memdb.c` portion is compiled when `SQLITE_OMIT_DESERIALIZE` is not defined. It implements a VFS named `memdb` where database bytes live in a contiguous `MemStore.aData` buffer.

Important types and globals:

- `MemStore`: in-memory file storage with current size, allocation size, maximum size, backing bytes, optional mutex, mmap reference count, deserialize flags, reader/writer lock counters, reference count, and optional shared filename.
- `MemFile`: an open `sqlite3_file` with a `MemStore` pointer and current lock level.
- `memdb_g`: process-global list of shared named `MemStore` objects, protected by `SQLITE_MUTEX_STATIC_VFS1`.
- `memdb_vfs`: VFS object registered by `sqlite3MemdbInit()`. It delegates dynamic loading, randomness, sleep, current time, and last-error behavior to the lower VFS stored in `pAppData`.
- `memdb_io_methods`: in-memory file method table. Shared-memory/WAL methods are null; memdb operates in rollback mode.

`memdbOpen()` creates either a shared store when the filename begins with `/` or `\`, or a separate store for unnamed/private use and `sqlite3_deserialize()`. Shared stores are looked up or inserted in `memdb_g.apMemStore`; separate stores have no global name. New stores default to `SQLITE_DESERIALIZE_RESIZEABLE | SQLITE_DESERIALIZE_FREEONCLOSE` and `sqlite3GlobalConfig.mxMemdbSize`.

`memdbClose()` decrements references, removes the store from the shared array when the final named reference closes, frees `aData` if `SQLITE_DESERIALIZE_FREEONCLOSE` is set, frees the mutex, and frees the store. `memdbRead()` copies from memory and zero-fills short reads. `memdbWrite()` refuses read-only stores, grows the buffer with `memdbEnlarge()` when allowed, zero-fills gaps, and updates `sz`. `memdbTruncate()` only shrinks and returns `SQLITE_CORRUPT` if asked to grow, which should only happen for corrupt WAL-mode input. `memdbSync()` is a no-op, `memdbFileSize()` reports `sz`, and `memdbDeviceCharacteristics()` advertises atomic, powersafe-overwrite, safe-append, and sequential behavior.

`memdbLock()` and `memdbUnlock()` implement SQLite lock levels with `nRdLock` and `nWrLock`; write locks are refused for `SQLITE_DESERIALIZE_READONLY`. `memdbFetch()` exposes direct pointers to immutable/non-resizeable memory and increments `nMmap`; resizeable stores return no mapping so resizing cannot invalidate outstanding pointers. `memdbUnfetch()` decrements `nMmap`.

`memdbFileControl()` supports `SQLITE_FCNTL_VFSNAME` and `SQLITE_FCNTL_SIZE_LIMIT`. Size limits lower than current size are clamped up to current size, and negative input restores the maximum. `memdbAccess()` always reports no disk files, and `memdbFullPathname()` copies the provided name as canonical because memdb names are virtual.

`memdbFromDbSchema()` uses `SQLITE_FCNTL_FILE_POINTER` to retrieve a `MemFile` from a schema and rejects shared named stores. `sqlite3_serialize()` returns the bytes for a memdb database directly, or for ordinary btree-backed schemas computes `PRAGMA page_count`, optionally forces an empty database into existence with `BEGIN IMMEDIATE; COMMIT;`, allocates a buffer, and copies each page through pager APIs. `SQLITE_SERIALIZE_NOCOPY` only succeeds for private memdb stores; ordinary pager-backed databases return null for no-copy mode.

`sqlite3_deserialize()` reopens a schema as memdb by preparing `ATTACH x AS <schema>`, setting `db->init.reopenMemdb`, stepping the statement, locating the resulting `MemFile`, and installing the caller-provided byte buffer plus size, allocation, maximum, and flags. It rejects schema index 1 (`temp`) and invalid sizes under API armor, holds `db->mutex`, and frees `pData` on failure when `SQLITE_DESERIALIZE_FREEONCLOSE` is set. `sqlite3IsMemdb()` tests pointer equality with `memdb_vfs`, and `sqlite3MemdbInit()` registers the VFS above the current default VFS with `szOsFile` large enough for `MemFile`.

## Bitvec Utility

The `bitvec.c` portion implements a fixed-size sparse bitmap whose bits are numbered from 1. SQLite uses it to track pages journaled during a transaction or pages with the pager "dont-write" property. The design optimizes for frequent tests, relatively few sets, rare clears, and very large possible page-number ranges.

`Bitvec` is exactly `BITVEC_SZ` bytes. It has three representations:

- For small ranges (`iSize <= BITVEC_NBIT`), `u.aBitmap[]` is a direct bit array.
- For larger sparse ranges with `iDivisor==0`, `u.aHash[]` is an open-addressed hash table of set bit numbers. `nSet` counts occupied entries.
- When the hash becomes dense (`nSet >= BITVEC_MXHASH`), the object converts to a recursive array of sub-bitmaps in `u.apSub[]`. `iDivisor` defines the range handled by each sub-bitmap.

Public/internal functions:

- `sqlite3BitvecCreate()` allocates and zeroes a bitmap for a maximum bit index.
- `sqlite3BitvecTestNotNull()` and `sqlite3BitvecTest()` test whether a bit is set, walking sub-bitmaps as needed and probing the hash table for sparse large maps.
- `sqlite3BitvecSet()` sets a bit. It recursively creates sub-bitmaps when already subdivided, sets direct bitmap bits for small maps, inserts into the hash for sparse maps, and rehashes into recursive representation once the hash is too full.
- `sqlite3BitvecClear()` clears a bit, walking recursive maps and either clearing a direct bitmap bit or rebuilding the hash table in caller-provided temporary storage.
- `sqlite3BitvecDestroy()` frees recursive sub-bitmaps and the top-level object.
- `sqlite3BitvecSize()` returns the configured maximum.
- `sqlite3BitvecBuiltinTest()` is compiled unless `SQLITE_UNTESTABLE` and executes a small opcode-driven randomized test program against a linear bit-array reference.

Key risks are off-by-one errors because the public bit numbers are 1-based while internal indexes are 0-based, hash-table fullness/rehash behavior, and caller responsibility for valid non-null/range arguments in `sqlite3BitvecSet()` and adequate scratch space in `sqlite3BitvecClear()`.

## State And Persistence Behavior

The Windows VFS persists state in open `winFile` handles, byte-range locks, mapped database views, WAL `*-shm` files, process-global `winShmNodeList`, configurable global retry counters, global temp/data directory strings, optional Win32 heap state, and global VFS registration. File state survives through real filesystem objects, WAL shared-memory files, OS file handles, and memory mappings. The code is careful to unmap before closing/truncating, to close mapping handles, to retry transient sharing violations, and to maintain local lock state in `winFile.locktype`.

The memdb VFS persists database content only in process memory. Shared memdb stores persist while at least one connection references the named store in `memdb_g`; private stores persist only for their owning database connection/file. Deserialized buffers may be owned by SQLite and freed on close, or caller-managed depending on flags. The `nMmap` counter prevents resizing while direct memory pointers are outstanding.

Bitvec state is heap-only and private to its owner. Its representation can mutate from bitmap to hash to recursive sub-bitmaps as density changes, but the externally visible state is just the set of bit numbers up to `iSize`.

## Dependencies And Integration Points

This chunk depends on SQLite core APIs and compile-time configuration: mutex allocation, memory allocation, logging, random bytes, URI parameters, pager/btree APIs, VFS registration, file-control constants, SQLite lock constants, WAL shared-memory constants, and test fault-injection macros (`SimulateIOError`, `SimulateDiskfullError`, `OSTRACE`, `testcase`, `NEVER`, `ALWAYS`).

The Windows VFS integrates directly with Win32/WinRT/WinCE APIs and Cygwin compatibility APIs. Its `sqlite3_vfs` objects are the platform boundary used by all SQLite pager and WAL code on Windows. The memdb VFS integrates with the core VFS registry as a secondary VFS layered over the current default VFS for non-storage services. `sqlite3_serialize()` and `sqlite3_deserialize()` integrate memdb with public SQLite APIs and with btree/pager page access for ordinary database serialization.

The `Bitvec` utility is not a VFS component. It is a pager/transaction support data structure and is expected to be consumed by later chunks that implement journaling and page cache behavior.

## Risks And Edge Cases

- Windows path handling is highly conditional. Long-path prefixes, UNC paths, Cygwin conversion, WinRT relative-path limitations, `sqlite3_data_directory`, and ANSI-vs-wide APIs all have distinct behavior.
- Locking correctness is critical. The byte ranges for pending/reserved/shared locks and WAL locks must match SQLite's cross-process protocol. The no-lock VFS is intentionally dangerous for concurrent writers.
- WinCE lock emulation relies on named mutexes and shared mappings derived from normalized filenames; naming collisions or conversion errors would corrupt lock semantics.
- Retry loops mitigate antivirus/indexer conflicts but can hide timing-sensitive bugs or add latency. `NORETRY` exists to prevent nested retries during access checks.
- mmap logic intentionally degrades to regular I/O on mapping failure, so tests must inspect logs or behavior carefully if mapping coverage matters.
- `winTruncate()` is a no-op when fetch references are outstanding, which can leave files larger than requested but avoids invalidating active mapped cursors.
- `sqlite3_deserialize()` mutates schema state via an internal attach/reopen path and must hold `db->mutex`; failures must free owned buffers exactly once.
- `memdbFetch()` only returns direct pointers for non-resizeable buffers; changing this would risk invalidating outstanding page pointers.
- `Bitvec` has dense/sparse representation transitions and 1-based indexing, both common sources of subtle boundary defects.

## Test Signals

Visible test hooks and signals include:

- `assert(ArraySize(aSyscall)==89)` in Windows `sqlite3_os_init()` and the Unix syscall-count assertion just before this chunk.
- Fault-injection paths through `SimulateIOError`, `SimulateIOErrorBenign`, and `SimulateDiskfullError`.
- Public test globals `sqlite3_sync_count`, `sqlite3_fullsync_count`, `sqlite3_os_type`, and `sqlite3_current_time`.
- VFS system-call override APIs (`xSetSystemCall`, `xGetSystemCall`, `xNextSystemCall`) for injected Win32 failures.
- `SQLITE_FCNTL_WIN32_SET_HANDLE`, `SQLITE_FCNTL_NULL_IO`, `SQLITE_FCNTL_WIN32_AV_RETRY`, lock-timeout controls, mmap-size controls, and file-handle retrieval.
- Logging through `sqlite3_log()` with source line numbers in `winLogErrorAtLine()`.
- `sqlite3BitvecBuiltinTest()`, which compares `Bitvec` operations against a linear bit-array reference and returns the first mismatch.

Practical validation for this chunk should cover Windows VFS open/read/write/truncate/sync/delete/access/full-path behavior, Windows WAL mode and shared-memory locking, WinCE/WinRT/Cygwin conditional builds where supported, memdb shared/private store lifecycle, serialization/deserialization flags and ownership, mmap fetch/unfetch behavior, and Bitvec sparse-to-recursive transition cases.
