# subset-b-008775 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/memdb.c -->
## sources/storage-engines/sqlite/src/memdb.c

Purpose: implements SQLite's `memdb` VFS and the public `sqlite3_serialize()` / `sqlite3_deserialize()` APIs when `SQLITE_OMIT_DESERIALIZE` is not set. The VFS stores each database as one contiguous heap buffer behind a `MemStore`. It supports either private stores, created by deserialize or non-slash names, or shared named stores under `file:/name?vfs=memdb` where names beginning with `/` or `\` are tracked in the process-global `memdb_g.apMemStore` array.

Important types and APIs: `MemStore` owns `aData`, `sz`, `szAlloc`, `szMax`, flags, lock counts, refcount, optional mutex, and optional shared filename. `MemFile` subclasses `sqlite3_file` and points at a `MemStore`. `memdb_vfs` supplies VFS methods and delegates randomness, sleep, dynamic loading, current time, and last-error to `ORIGVFS(pVfs)`. The file exports `sqlite3_serialize()`, `sqlite3_deserialize()`, `sqlite3IsMemdb()`, and `sqlite3MemdbInit()`.

Control flow: `sqlite3MemdbInit()` locates the default VFS, stores it as `pAppData`, sizes `szOsFile` to fit `MemFile`, and registers `memdb`. `memdbOpen()` either finds/creates a shared `MemStore` while holding `SQLITE_MUTEX_STATIC_VFS1`, or creates a private store. File I/O methods then operate directly on the buffer: reads return zero-filled short reads past EOF, writes call `memdbEnlarge()` when resizeable and extend with zero padding, truncation only shrinks, and sync is a no-op. Locking is logical and in-process only: `nRdLock` and `nWrLock` enforce SHARED/RESERVED/PENDING/EXCLUSIVE transitions and readonly stores reject write locks.

State and persistence: all bytes live in memory. Shared stores persist only while at least one open `MemFile` references them; `memdbClose()` removes the store from the global array when the last shared reference closes and frees `aData` only if `SQLITE_DESERIALIZE_FREEONCLOSE` is set. `memdbFetch()` exposes stable direct pointers only for non-resizeable stores and increments `nMmap`, preventing resize through `memdbEnlarge()`. `sqlite3_deserialize()` reopens a schema as a private memdb by preparing an `ATTACH`, setting `db->init.reopenMemdb`, then replacing the store buffer, sizes, max size, and deserialize flags.

Dependencies and integration points: this file depends on core APIs in `sqliteInt.h`, pager/btree accessors for non-memdb serialization, mutex services, `sqlite3_file_control(SQLITE_FCNTL_FILE_POINTER)`, `SQLITE_FCNTL_VFSNAME`, `SQLITE_FCNTL_SIZE_LIMIT`, VFS registration, and global `sqlite3GlobalConfig.mxMemdbSize`. It intentionally omits WAL/shared-memory VFS methods, so pager use is rollback-journal oriented.

Risks: shared stores are process-local and do not coordinate across processes. The resize path relies on the invariant that no mapped pointers exist. `memdbFromDbSchema()` rejects shared named stores for direct serialization/deserialization behavior, so callers expecting `NOCOPY` with shared memdb receive fallback behavior. Incorrect lock count transitions would corrupt the in-process concurrency model. `sqlite3_deserialize()` mutates schema attachment state and must hold `db->mutex`; error paths free caller buffers only under the documented flag.

Test signals: exercise `sqlite3_deserialize()` with readonly, resizeable, free-on-close, and schema-name cases; serialize private memdb with and without `SQLITE_SERIALIZE_NOCOPY`; open two connections to the same `/name` and verify lock busy/readonly transitions; verify size-limit file-control behavior; test mmap fetch/unfetch prevents resizing; and confirm registration delegates lower-VFS services.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/memdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/memjournal.c -->
## sources/storage-engines/sqlite/src/memjournal.c

Purpose: implements an in-memory rollback journal used for `:memory:` databases, `journal_mode=MEMORY`, and small temporary journals that may later spill to disk. It provides a `sqlite3_file` implementation that starts as a linked list of heap chunks and can be converted in-place into a real VFS file.

Important types and APIs: `FileChunk` holds linked chunk data; `FilePoint` is a cursor with logical offset and chunk pointer; `MemJournal` subclasses `sqlite3_file` and stores chunk size, spill threshold, first chunk, endpoint, readpoint, open flags, underlying VFS, and journal filename. Public entry points are `sqlite3JournalOpen()`, `sqlite3MemJournalOpen()`, conditional `sqlite3JournalCreate()`, `sqlite3JournalIsInMemory()`, and `sqlite3JournalSize()`.

Control flow: `sqlite3JournalOpen()` zeroes the supplied file object. With `nSpill==0` it immediately delegates to `sqlite3OsOpen()`. Otherwise it installs `MemJournalMethods`, chooses chunk size from `nSpill` or the default, and records the VFS/name/flags. `memjrnlWrite()` appends into chunks, truncating back to `iOfst` for the limited atomic-write rewrite case. If a positive spill threshold is exceeded, `memjrnlCreateFile()` opens the underlying file, writes all chunks sequentially, frees chunks on success, and leaves the same `sqlite3_file` storage now owned by real VFS methods. If conversion fails, it restores the saved `MemJournal` copy so rollback data remains available.

State and persistence: before spilling, persistence is heap-only and `memjrnlSync()` is a no-op. The endpoint tracks logical size and last chunk. The readpoint accelerates sequential reads by caching the chunk used by the previous read. `memjrnlTruncate()` frees chunks after the truncation point and resets the read cache. Once spilled, all subsequent calls go through the real VFS because `pJfd->pMethods` has changed.

Dependencies and integration points: the pager/journal layer calls `sqlite3JournalOpen()` with VFS, flags, and spill policy. Atomic-write and batch-atomic-write builds use `sqlite3JournalCreate()` to force materialization. The implementation depends on `sqlite3OsOpen()`, `sqlite3OsWrite()`, `sqlite3OsClose()`, `sqlite3_malloc()`, `sqlite3_free()`, and the `sqlite3_io_methods` contract.

Risks: the journal assumes append-mostly writes; unexpected random writes are handled by truncating to the write offset, which is only valid for the documented journal patterns. `memjrnlRead()` returns `SQLITE_IOERR_SHORT_READ` for reads past endpoint and depends on chunk traversal invariants. Spill failure recovery is critical: losing the saved in-memory chunks would break rollback. The `kv` of `nSpill` as both threshold and chunk size for positive values means unusual thresholds change allocation shape.

Test signals: cover `nSpill<0`, `nSpill==0`, and positive spill modes; write/read across chunk boundaries; truncate to zero and mid-file; force OOM during chunk allocation and during spill open/write; test `sqlite3JournalCreate()` under atomic-write builds; and verify `sqlite3JournalSize()` is at least both VFS file size and `MemJournal`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/memjournal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/msvc.h -->
## sources/storage-engines/sqlite/src/msvc.h

Purpose: centralizes small Microsoft Visual C/C++ compatibility settings used by the SQLite source tree. It is a configuration header, not a runtime module.

Important macros: when `_MSC_VER` is defined, the file disables MSVC warnings that SQLite deliberately triggers or accepts, including function-pointer/data-pointer casts, unused parameters, constant conditionals, signed/unsigned conversions, unreachable code, and assignment in conditionals. For 32-bit MSVC it defines `SQLITE_4_BYTE_ALIGNED_MALLOC` after undefining any existing value. For MSVC versions older than 1800, it defines `HAVE_LOG2 0` when not already supplied.

Control flow: all behavior is preprocessor-only. Include guards prevent repeated application. The warning pragmas are active only under MSVC, the malloc alignment setting only under `_MSC_VER && !defined(_WIN64)`, and the `log2()` capability override only for older MSVC.

State and persistence: no state is allocated and no persistence is involved. Its effects are compile-unit configuration and compiler diagnostic behavior.

Dependencies and integration points: included by SQLite's internal configuration path for MSVC builds. `SQLITE_4_BYTE_ALIGNED_MALLOC` affects memory-alignment assumptions elsewhere in SQLite, especially on 32-bit Windows. `HAVE_LOG2` feeds feature-detection branches that decide whether SQLite may call `log2()` directly.

Risks: changing warning suppression can surface noisy build output or hide newly meaningful diagnostics. Incorrect `SQLITE_4_BYTE_ALIGNED_MALLOC` detection can affect code that assumes allocation alignment. The `HAVE_LOG2` fallback must not override a build system that explicitly defines it.

Test signals: compile amalgamation and non-amalgamation builds with 32-bit and 64-bit MSVC; verify no duplicate macro-definition warnings; confirm old MSVC builds avoid missing `log2()` references; and run memory-alignment-sensitive tests on 32-bit Windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/msvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex.c -->
## sources/storage-engines/sqlite/src/mutex.c

Purpose: provides the platform-independent mutex dispatch layer. It chooses the configured mutex implementation, initializes and tears it down, exposes the public `sqlite3_mutex_*` APIs, and optionally wraps the default implementation with contention warnings for misuse detection.

Important APIs and types: `sqlite3MutexInit()`, `sqlite3MutexEnd()`, `sqlite3_mutex_alloc()`, `sqlite3MutexAlloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, and debug-only `sqlite3_mutex_held()` / `sqlite3_mutex_notheld()`. Under `SQLITE_THREAD_MISUSE_WARNINGS`, `CheckMutex` wraps a real mutex and can mark recursive db-handle mutexes as `SQLITE_MUTEX_WARNONCONTENTION` through `sqlite3MutexWarnOnContention()`.

Control flow: `sqlite3MutexInit()` fills `sqlite3GlobalConfig.mutex` if the application did not configure one before initialization. It picks `sqlite3DefaultMutex()` when core mutexes are enabled, or `sqlite3NoopMutex()` when disabled, with an optional `multiThreadedCheckMutex()` wrapper. It copies method pointers, issues a memory barrier, then publishes `xMutexAlloc` last. Allocation uses `sqlite3_initialize()` for dynamic mutexes unless autoinit is omitted; static mutex allocation can call `sqlite3MutexInit()` directly. Runtime operations are thin null-tolerant dispatchers to the configured method table.

State and persistence: the global method table in `sqlite3GlobalConfig.mutex` is the central mutable state. Debug builds also maintain `mutexIsInit` to assert that internal mutex allocation occurs only after initialization. No persistent storage is involved.

Dependencies and integration points: platform backends provide `sqlite3DefaultMutex()` in `mutex_unix.c`, `mutex_w32.c`, or `mutex_noop.c`. The layer depends on `sqlite3GlobalConfig.bCoreMutex`, `sqlite3MemoryBarrier()`, `sqlite3_initialize()`, and SQLite's config-time mutex override API. Assertions and TSAN conditional logic protect debug-only held/notheld checks.

Risks: publishing method pointers out of order could allow another thread to see a partially initialized table, hence the barrier and last assignment to `xMutexAlloc`. Wrapper misuse warnings deliberately log `SQLITE_MISUSE` and may abort when configured. `sqlite3MutexAlloc()` returns null if core mutexes are disabled, so call sites must treat null as a valid no-op mutex.

Test signals: run single-thread, multithread, and serialized SQLite modes; configure custom mutex methods before initialization; enable `SQLITE_THREAD_MISUSE_WARNINGS` and verify contention logs; run debug assertions around static mutex allocation; and run under TSAN to confirm held/notheld checks are suppressed as intended.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex.h -->
## sources/storage-engines/sqlite/src/mutex.h

Purpose: selects the mutex implementation at compile time and defines mutex omission macros for `SQLITE_THREADSAFE=0` builds. It is included indirectly through `sqliteInt.h`.

Important macros: `SQLITE_MUTEX_OMIT` is defined when SQLite is not threadsafe. For threadsafe builds without explicit `SQLITE_MUTEX_NOOP`, the header selects `SQLITE_MUTEX_PTHREADS` on Unix, `SQLITE_MUTEX_W32` on Windows, or `SQLITE_MUTEX_NOOP` for other platforms. When mutexes are omitted, public mutex operations become macros that return a dummy `(sqlite3_mutex*)8`, no-op enter/leave/free, successful try, and true held/notheld checks. `MUTEX_LOGIC(X)` either erases or preserves mutex-only declarations and code.

Control flow: the file has no runtime control flow. Its preprocessor decisions decide which `.c` backend compiles and whether common code emits mutex logic.

State and persistence: no runtime state. The dummy pointer used by omit-mode macros is never dereferenced and exists only to satisfy API shape.

Dependencies and integration points: depends on `SQLITE_THREADSAFE` and OS macros from `os_setup.h` via `os.h`. It declares `sqlite3_mutex_held()` when real mutexes are present. Many core modules use `MUTEX_LOGIC()` and `sqlite3MutexAlloc()` behavior chosen here.

Risks: platform macro misclassification routes builds to the wrong backend or to no-op mutexes. In omit mode, mutex logic is compiled away completely and cannot be replaced at start time, unlike `SQLITE_MUTEX_NOOP`. Code added to the core must respect `MUTEX_LOGIC()` or null/dummy mutex behavior.

Test signals: compile with `SQLITE_THREADSAFE=0`, `SQLITE_THREADSAFE=1` on Unix and Windows, explicit `SQLITE_MUTEX_NOOP`, and `SQLITE_OS_OTHER`; verify only the expected backend symbols are required; and run API tests for mutex calls under omit and no-op modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex_noop.c -->
## sources/storage-engines/sqlite/src/mutex_noop.c

Purpose: implements SQLite's no-op mutex method table for single-threaded or platform-other builds where the mutex subsystem remains configurable but the default implementation provides no mutual exclusion. Debug builds add call-sequence checking without real locking.

Important APIs and types: `sqlite3NoopMutex()` returns the method table. Under `SQLITE_MUTEX_NOOP`, `sqlite3DefaultMutex()` aliases the no-op implementation. In debug builds, `sqlite3_debug_mutex` tracks mutex `id` and entry `cnt`; in non-debug builds, allocation returns the dummy pointer `(sqlite3_mutex*)8`.

Control flow: non-debug methods all succeed and ignore their arguments. Debug allocation returns heap objects for `SQLITE_MUTEX_FAST` and `SQLITE_MUTEX_RECURSIVE`, or entries from a static array for static mutex IDs. Debug enter/try assert that non-recursive mutexes are not already held, increment `cnt`, and always succeed. Debug leave asserts held state, decrements `cnt`, and asserts non-recursive mutexes return to not-held.

State and persistence: non-debug mode has no meaningful state. Debug mode stores dynamic counters per mutex and static counters for static mutexes, but it still does not serialize threads.

Dependencies and integration points: used by `mutex.c` when `sqlite3GlobalConfig.bCoreMutex` is false or by default when `SQLITE_MUTEX_NOOP` is selected. It depends on SQLite allocation helpers, API armor checks for invalid static IDs, and debug assert conventions.

Risks: this implementation is unsafe for concurrent use; it is valid only when the caller has selected single-thread/no-core-mutex behavior or supplied external serialization. Debug checking can catch recursive misuse in one thread but cannot detect cross-thread races. Static mutex misuse under API armor reports `SQLITE_MISUSE_BKPT` instead of freeing.

Test signals: compile with and without `SQLITE_DEBUG`; verify dynamic no-op mutex allocation/free API behavior; assert double-enter on a FAST mutex fails in debug tests; verify recursive enter/leave counts; and run single-thread SQLite suites with `SQLITE_MUTEX_NOOP`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex_noop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex_unix.c -->
## sources/storage-engines/sqlite/src/mutex_unix.c

Purpose: provides the pthread-based default mutex backend for threadsafe Unix builds selected by `SQLITE_MUTEX_PTHREADS`.

Important types and APIs: `struct sqlite3_mutex` wraps a `pthread_mutex_t` plus optional `id`, `nRef`, `owner`, and `trace` fields when debug, API armor, or homegrown recursive mutex support needs them. The exported backend hook is `sqlite3DefaultMutex()`, and the file also defines `sqlite3MemoryBarrier()`.

Control flow: `pthreadMutexAlloc()` returns heap mutexes for `SQLITE_MUTEX_RECURSIVE` and `SQLITE_MUTEX_FAST`, and static cache-line-aligned mutexes for IDs 2 through 13. Recursive mutexes use `PTHREAD_MUTEX_RECURSIVE` unless `SQLITE_HOMEGROWN_RECURSIVE_MUTEX` is defined, in which case owner/nRef emulate recursion on a normal pthread mutex. `pthreadMutexEnter()`, `pthreadMutexTry()`, and `pthreadMutexLeave()` update owner/nRef fields when enabled and delegate to pthread lock primitives. `pthreadMutexFree()` destroys and frees only dynamic mutexes.

State and persistence: static mutexes live for process lifetime in `aMutex[]`; dynamic mutexes are heap allocated. Debug/homegrown builds track owner and recursion count for assertions and recursive behavior. There is no persistent storage.

Dependencies and integration points: depends on `<pthread.h>`, SQLite allocation helpers, API armor, debug asserts, and `GCC_VERSION` for alignment and memory barrier selection. `sqlite3MemoryBarrier()` uses `SQLITE_MEMORY_BARRIER` or GCC `__sync_synchronize()` and is consumed by the mutex dispatch and VFS shared-memory barriers.

Risks: held/notheld checks rely on `pthread_equal()` behaving atomically enough for debug assertions; comments call out HPUX-style risk. Homegrown recursive mutexes assume coherent cache and safe owner comparison. Static mutex array size must match SQLite static mutex IDs. If `pthread_mutexattr_settype(PTHREAD_MUTEX_RECURSIVE)` is unavailable or fails silently, recursive behavior can break.

Test signals: run threaded SQLite tests on Unix with serialized mode; run debug builds to exercise owner/nRef assertions; compile with `SQLITE_HOMEGROWN_RECURSIVE_MUTEX`; verify static mutex IDs under API armor; and run stress tests for recursive db mutex use and `sqlite3_mutex_try()` contention.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex_w32.c -->
## sources/storage-engines/sqlite/src/mutex_w32.c

Purpose: provides the Windows default mutex backend for threadsafe Win32 builds selected by `SQLITE_MUTEX_W32`.

Important types and APIs: `struct sqlite3_mutex` stores either a `CRITICAL_SECTION` for recursive mutexes or an `SRWLOCK` for non-recursive/static mutexes, plus an `id` and debug owner/ref/trace fields. `sqlite3DefaultMutex()` returns the method table. `sqlite3MemoryBarrier()` supplies the platform barrier, and `sqlite3_win32_sleep()` is used while another thread initializes static mutexes.

Control flow: `winMutexInit()` uses `InterlockedCompareExchange()` on `winMutex_lock` so one caller initializes the aligned static mutex array and others wait for `winMutex_isInit`. Static mutexes use SRW locks. `winMutexAlloc()` heap-allocates dynamic FAST or RECURSIVE mutexes, initializes SRW or critical section accordingly, or returns a static entry by ID. Enter/try/leave dispatch on `id`: recursive uses critical-section APIs, all others acquire/release exclusive SRW locks. `winMutexEnd()` resets initialization state.

State and persistence: process-global static mutexes live in `aWindowsMutex[12]`. `winMutex_lock` and `winMutex_isInit` protect backend initialization state. Debug builds track owning thread ID and recursion count for assertions and optional tracing through `OSTRACE`.

Dependencies and integration points: depends on Windows primitives via `os_win.h`, `os_common.h`, MSVC alignment support, SQLite allocation, API armor, and `MSVC_VERSION`. It integrates with the common mutex dispatcher through `sqlite3DefaultMutex()`.

Risks: `winMutexEnd()` assumes shutdown ordering; resetting `winMutex_isInit` while mutex users remain would violate assertions. SRW locks are exclusive-only here and non-recursive, so accidental reentry into FAST/static mutexes is invalid. `TryAcquireSRWLockExclusive()` availability follows supported Windows targets. Static array bounds must track SQLite static mutex IDs.

Test signals: run Windows serialized-mode concurrency tests; build debug with dynamic/static mutex tracing; verify recursive critical-section reentry and FAST non-reentry assertions; test initialization races by parallel `sqlite3_initialize()` calls; and compile with MSVC and MinGW paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mutex_w32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/notify.c -->
## sources/storage-engines/sqlite/src/notify.c

Purpose: implements `sqlite3_unlock_notify()` and support routines for shared-cache lock wait notification when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled.

Important APIs and state: exported/internal routines are `sqlite3_unlock_notify()`, `sqlite3ConnectionBlocked()`, `sqlite3ConnectionUnlocked()`, and `sqlite3ConnectionClosed()`. The central state is `sqlite3BlockedList`, a process-global linked list of connections whose `pBlockingConnection` or `pUnlockConnection` is non-null. Each connection stores callback pointer `xUnlockNotify`, callback argument, blocking connection, unlock connection, and list link.

Control flow: callers record a lock wait with `sqlite3ConnectionBlocked(db, blocker)`, which adds `db` to the blocked list if needed and sets `pBlockingConnection`. `sqlite3_unlock_notify()` holds both `db->mutex` and `SQLITE_MUTEX_STATIC_MAIN`; it cancels when callback is null, invokes immediately if no blocker remains, detects deadlock by walking the unlock chain back toward `db`, or records the desired blocker/callback and groups the connection by callback in the blocked list. `sqlite3ConnectionUnlocked(db)` scans the list when a transaction releases locks, clears references to `db`, batches callback arguments for identical callback functions, removes completed entries, and invokes callbacks. `sqlite3ConnectionClosed()` treats close as unlock, removes the connection, and verifies no remaining blocked entries reference it.

State and persistence: all state is in-process and protected by `STATIC_MAIN`. Debug `checkListProperties()` asserts that entries are meaningful, callback groups are contiguous, and close cleanup removed references.

Dependencies and integration points: depends on `sqliteInt.h`, `btreeInt.h`, SQLite connection fields, mutex subsystem, benign malloc regions, `sqlite3_log()` via error handling, and shared-cache lock conflict paths. It sets database error state through `sqlite3ErrorWithMsg()`.

Risks: callbacks are invoked while `STATIC_MAIN` is still held in this implementation, so callback behavior must respect SQLite's documented restrictions and avoid deadlock-prone reentry. OOM while growing the callback argument array intentionally degrades into multiple smaller callback invocations to avoid lost notifications. Deadlock detection follows only `pUnlockConnection` chains; wrong maintenance of those fields would miss or falsely report deadlocks.

Test signals: enable unlock-notify and shared cache; create two or more blocked connections and verify callback grouping; test immediate notification after blocker release; create deadlock cycles and expect `SQLITE_LOCKED`; simulate OOM during callback argument growth; and close a blocking connection while waiters are registered.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/os.c -->
## sources/storage-engines/sqlite/src/os.c

Purpose: implements common OS/VFS wrapper routines used by the SQLite core, independent of specific Unix/Windows/KV VFS backends. It centralizes `sqlite3_file` method dispatch, VFS registration, deterministic test hooks, and allocation wrappers.

Important APIs and state: `sqlite3OsClose/Read/Write/Truncate/Sync/FileSize/Lock/Unlock/CheckReservedLock/FileControl/FileControlHint/SectorSize/DeviceCharacteristics`, WAL shared-memory wrappers, mmap fetch/unfetch wrappers, VFS wrappers like `sqlite3OsOpen/Delete/Access/FullPathname/DlOpen/Randomness/Sleep/CurrentTimeInt64`, allocation helpers `sqlite3OsOpenMalloc()` and `sqlite3OsCloseFree()`, `sqlite3OsInit()`, `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()`. Test globals track simulated I/O errors, disk-full faults, VFS OOM tests, and open-file count.

Control flow: file wrappers call the corresponding `sqlite3_io_methods` entry with local guards such as no-op sync when flags are zero, fallback sector size, and disabled mmap stubs when `SQLITE_MAX_MMAP_SIZE<=0`. VFS wrappers mask invalid open flags before `xOpen`, set output paths to empty before `xFullPathname`, use deterministic PRNG seed output when configured, and fall back from `xCurrentTimeInt64` to `xCurrentTime`. VFS registration maintains a global linked list under `SQLITE_MUTEX_STATIC_MAIN`, unlinking existing instances before inserting as default or non-default.

State and persistence: global `vfsList` is the persistent process registry of VFS implementations. Test-only globals inject transient failures. No database bytes are persisted here; persistence is delegated to concrete VFS methods.

Dependencies and integration points: includes `sqliteInt.h`, relies on `sqlite3_vfs`, `sqlite3_file`, mutex subsystem, malloc subsystem, loadable-extension configuration, WAL/mmap compile flags, `sqlite3_os_init()` supplied by platform VFS files, and `sqlite3JournalIsInMemory()` to avoid some OOM injection against memory journals.

Risks: wrapper behavior is part of SQLite's internal ABI; changing return-code handling can affect pager correctness. Fault injection deliberately excludes some file-controls because simulated post-commit failures would confuse transaction tests. `sqlite3OsOpen()` masks flags with a hard-coded valid VFS flag mask. VFS list mutation must remain mutex-protected and autoinit-safe.

Test signals: run core I/O fault-injection suites with `SQLITE_TEST`; test VFS registration order and default selection; verify open flag masking; run WAL and mmap builds; test deterministic `iPrngSeed`; force malloc failure in `sqlite3OsInit()` and `sqlite3OsOpenMalloc()`; and verify time fallback for VFS iVersion 1.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/os.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/os.h -->
## sources/storage-engines/sqlite/src/os.h

Purpose: declares SQLite's internal OS abstraction layer and common file-locking constants. It is included by `sqliteInt.h`, making its definitions widely visible across the core.

Important declarations and macros: includes `os_setup.h`, supplies defaults for `SET_FULLSYNC`, `SQLITE_MAX_PATHLEN`, `SQLITE_MAX_SYMLINK`, `SQLITE_DEFAULT_SECTOR_SIZE`, and `SQLITE_TEMP_FILE_PREFIX`. Defines lock levels `NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`; lock-byte layout `PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, and `SHARED_SIZE`; and declares all `sqlite3Os*` file/VFS wrapper functions. It also declares `SQLITE_FCNTL_DB_UNCHANGED`.

Control flow: no runtime code. The header establishes contracts consumed by pager, btree, WAL, and VFS code. The lock-byte comments define cross-platform file-locking semantics used by Unix and Windows backends.

State and persistence: no state. `PENDING_BYTE` may be fixed or refer to `sqlite3PendingByte` depending on `SQLITE_OMIT_WSD`, affecting where lock bytes reside in database files.

Dependencies and integration points: depends on standard `FILENAME_MAX`, SQLite integer typedefs, `sqlite3_file`, `sqlite3_vfs`, and compile-time OS selection from `os_setup.h`. The lock constants are integral to database file format compatibility because the pager avoids allocating lock-byte pages.

Risks: changing `PENDING_BYTE` or related byte ranges can create subtle database compatibility changes. Defaults like sector size and temp prefix affect platform behavior and tests. The declarations must match `os.c`; mismatches would surface as build or ABI issues.

Test signals: compile all VFS backends against the header; run locking tests on Unix/Windows; run tests with low `PENDING_BYTE`; verify temp-file behavior with default and overridden prefix; and build with `SQLITE_OMIT_WAL` / mmap variations to check conditional declarations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/os_common.h -->
## sources/storage-engines/sqlite/src/os_common.h

Purpose: provides macros and small helpers shared by platform-specific `os_*.c` files. It is intentionally not a general-purpose header.

Important macros and state: rejects obsolete `MEMORY_DEBUG`, defines optional `TIMER_START`, `TIMER_END`, and `TIMER_ELAPSED` for `SQLITE_PERFORMANCE_TRACE`, declares test globals for I/O errors and disk-full simulation, and defines `SimulateIOErrorBenign()`, `SimulateIOError()`, `SimulateDiskfullError()`, and `OpenCounter()`. `local_ioerr()` increments hit counters and hard-hit counters for non-benign faults.

Control flow: in test builds, the simulate macros inject caller-provided code when pending or persistent counters indicate an error should occur. In non-test builds, all simulation and open-counter macros compile away. Performance timers compile to hardware-time reads only when explicitly enabled.

State and persistence: test-only global counters are shared with `os.c`. They are transient process state used by regression tests, not persisted.

Dependencies and integration points: used by concrete VFS implementations such as Unix and Windows. It depends on `IOTRACE`, `sqlite3Hwtime()`, and the test globals defined in `os.c`. `OpenCounter()` lets VFS code update `sqlite3_open_file_count`.

Risks: simulation macros execute arbitrary caller code and must be placed only where the VFS can safely abort with the intended error. Non-test builds must stay side-effect-free. The obsolete macro check intentionally fails old build configurations.

Test signals: run `SQLITE_TEST` I/O error and disk-full suites; verify benign errors do not increment hard-hit count; build with `SQLITE_PERFORMANCE_TRACE`; and compile platform VFS files in non-test mode to ensure macros disappear cleanly.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/os_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/os_kv.c -->
## sources/storage-engines/sqlite/src/os_kv.c

Purpose: implements the experimental `kvvfs` VFS for text-only key/value storage, primarily for WASM/JavaScript storage but also optionally testable on Unix by mapping keys to local files. It supports a database file and rollback journal represented as keys rather than a byte-addressed filesystem.

Important types and APIs: `KVVfsFile` subclasses `sqlite3_file` and stores storage class, journal flag, journal buffer, page size, cached database size, and scratch data buffer. `sqlite3_kvvfs_methods` is an indirection table with record read/write/delete callbacks, buffer sizes, VFS pointer, and IO method pointers; in WASM builds JavaScript can replace callbacks. Public registration is `sqlite3_os_init()` when `SQLITE_OS_KV` is the platform, or `sqlite3KvvfsInit()` when optional on Unix. Utility functions `kvvfsEncode()` and `kvvfsDecode()` convert binary pages/journals to pure text.

Control flow: `kvvfsOpen()` classifies names ending in `-journal` as journal files, maps `local-journal` and `session-journal` to their backing storage classes, initializes buffers, and installs db or journal IO methods. Database reads compute page number from offset/page-size constraints, read a text record by page key, decode into caller buffer, and zero-fill short reads. Database writes assert power-of-two page sizes between 512 and 65536, encode one page, write it under page-number key, and update cached `szDb`. Journal writes accumulate binary data in memory; journal sync encodes length plus payload into the `jrnl` key; journal reads lazily load and decode that key.

State and persistence: database pages persist as one key per page plus a `sz` key for file size. Journal content persists under `jrnl` only after `xSync`. `kvvfsTruncateDb()` deletes page keys beyond the new size and rewrites `sz`; `kvvfsTruncateJrnl()` deletes `jrnl` and clears the heap journal. Lock/unlock do not enforce inter-client locking; lock refreshes cached size and unlock-to-none invalidates it.

Dependencies and integration points: depends on SQLite VFS interfaces, key/value callbacks supplied by C stdio test shims or WASM JavaScript, text encoding helpers, and rollback-journal pager mode. `os_setup.h` forces `SQLITE_OMIT_WAL`, `SQLITE_TEMP_STORE=3`, `SQLITE_OMIT_SHARED_CACHE`, and related options for `SQLITE_OS_KV`, aligning the core with this limited VFS.

Risks: the native `kvrecordMakeKey()` uses a fixed key buffer (`KVRECORD_KEY_SZ`, default 32), and comments warn long database names can malfunction. There is no real locking, WAL, dynamic loading, randomness, or sleeping. `kvvfsDecodeJournal()` contains delicate base-26 length parsing and must reject malformed text. The VFS assumes full-page database I/O and rollback journaling; unexpected offset/size patterns return I/O errors.

Test signals: use Unix optional mode with short database names; test encode/decode round-trips including zero runs and malformed inputs; verify page read/write/truncate deletes expected keys; test journal write/sync/read/truncate recovery; test local/session name mapping; run WASM storage tests with JavaScript callbacks; and verify unsupported WAL/shared-cache paths remain disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/os_kv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/os_setup.h -->
## sources/storage-engines/sqlite/src/os_setup.h

Purpose: normalizes compile-time operating-system selection for SQLite. After preprocessing, exactly one of `SQLITE_OS_KV`, `SQLITE_OS_OTHER`, `SQLITE_OS_UNIX`, or `SQLITE_OS_WIN` should be active, with the others forced to zero.

Important macros: if no OS macro is predefined, Windows-like compiler/platform macros select `SQLITE_OS_WIN=1`; otherwise Unix is selected. Explicit `SQLITE_OS_OTHER`, `SQLITE_OS_KV`, `SQLITE_OS_UNIX`, or `SQLITE_OS_WIN` overrides clear the other OS flags. `SQLITE_OS_KV` additionally defines storage-engine-limiting options: omit loadable extensions, WAL, deprecated APIs, shared cache, and autoinit; force memory temp store; and set `SQLITE_DQS=0`.

Control flow: all behavior is preprocessor logic. The `+1<=1` and `+1>1` tests distinguish undefined/zero from positive macro values without requiring prior definitions.

State and persistence: no runtime state. The selected macros determine which VFS, mutex backend, and feature set are compiled.

Dependencies and integration points: included by `os.h` before mutex selection in `mutex.h` relies on `SQLITE_OS_UNIX` or `SQLITE_OS_WIN`. It governs compilation of platform files such as `os_unix.c`, `os_win.c`, and `os_kv.c`.

Risks: incorrect or conflicting OS macro definitions can compile the wrong VFS or disable required features. `SQLITE_OS_KV` is intentionally restrictive; enabling it in a normal native build would omit WAL, shared cache, autoinit, and extension loading. Build systems must define only one positive OS target.

Test signals: preprocess builds for Windows, Unix, OS_OTHER, and OS_KV and inspect macro results; compile minimal custom-VFS builds with `SQLITE_OS_OTHER=1`; run kvvfs builds to verify the forced feature omissions; and check mutex backend selection after OS detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/os_setup.h -->
