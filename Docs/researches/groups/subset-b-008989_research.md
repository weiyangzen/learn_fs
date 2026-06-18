<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_fs.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_fs.c

## Purpose
Implements WiredTiger's default POSIX `WT_FILE_SYSTEM` and POSIX `WT_FILE_HANDLE` methods: existence, open, remove, rename, size/free-space, read/write, sync, truncate/extend, file locking, and optional mmap-backed file I/O.

## Important APIs, Types, and Functions
`__wt_os_posix` builds the file-system jump table. `WT_FILE_HANDLE_POSIX` carries the fd plus mmap state. `__posix_open_file`, `__posix_file_read`, `__posix_file_write`, `__posix_file_sync`, `__posix_file_truncate`, `__posix_fs_remove`, and `__posix_fs_rename` implement the main operations. `__wti_posix_prepare_remap_resize_file`, `__wti_posix_release_without_remap`, and `__wti_posix_remap_resize_file` coordinate mmap resize.

## Control Flow
Open translates WiredTiger flags to POSIX `open` flags, applies close-on-exec, optional `O_DSYNC` for logs, fadvise hints, durable directory sync, and installs handle methods. Reads/writes are chunked at 1GB. If connection-wide mmap I/O is enabled, file I/O first tries mapped memory and falls back to syscalls. Truncate prepares mmap remap, calls `ftruncate`, and either remaps or releases the resize flag. Durable remove/rename sync backing directories on Linux.

## State and Persistence Behavior
The layer treats sync failure as fatal/panic rather than retryable. `WT_DISAGG_NO_SYNC` can suppress flushes. Linux durable operations fsync containing directories. mmap I/O protects mapped buffers with `mmap_resizing` and `mmap_usecount`, preventing remap while readers/writers copy from a mapping.

## Dependencies and Integration Points
Depends on POSIX syscalls, `statvfs`, `posix_fadvise`, `sync_file_range`, mmap, WiredTiger stats, verbosity, block-manager file handles, log manager sync configuration, and `os_dir.c` directory-list hooks.

## Risks and Edge Cases
fdatasync/fsync errors panic; tests should include fault injection. `O_NOATIME`, `F_FULLFSYNC`, `sync_file_range`, and directory fsync vary by platform. mmap remap races are subtle, especially when writes extend files. Read/write stat increments happen after length is consumed, so instrumentation should be checked carefully if changed.

## Test Signals
Useful signals are crash-recovery tests around durable create/remove/rename, direct syscall fault tests, mmap-all stress with concurrent file growth/truncation, lock-open conflict tests, and platform matrix coverage for fadvise and sync variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_getenv.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_getenv.c

## Purpose
Provides the POSIX implementation of `__wt_getenv`, returning a WiredTiger-owned copy of a non-empty environment variable.

## Important APIs, Types, and Functions
`__wt_getenv(WT_SESSION_IMPL *, const char *, const char **)` wraps C `getenv` and `__wt_strdup`.

## Control Flow
The output is initialized to `NULL`. If `getenv(variable)` returns a non-NULL string with length greater than zero, the value is duplicated through the session allocator and returned; otherwise the call succeeds with `*envp == NULL`.

## State and Persistence Behavior
No persistent state is written. The returned value is heap/session allocated, decoupling callers from process environment storage and leaving ownership with WiredTiger memory management.

## Dependencies and Integration Points
Used by platform-independent configuration paths that need environment variables without exposing raw libc pointers. Error behavior depends on `__wt_strdup`.

## Risks and Edge Cases
Empty environment variables are intentionally treated as absent. Callers must free the duplicated result. Environment mutation by other threads is outside this wrapper's control.

## Test Signals
Tests should cover missing, empty, and non-empty variables, including allocator failure injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_getenv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_map.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_map.c

## Purpose
Implements explicit POSIX memory-map operations exposed through file handles for block-manager read paths and mapped-file optimizations.

## Important APIs, Types, and Functions
`__wti_posix_map`, `__wti_posix_unmap`, and, when `HAVE_POSIX_MADVISE` is available, `__wti_posix_map_preload` and `__wti_posix_map_discard`.

## Control Flow
`__wti_posix_map` gets current file size from `fh_size`, calls `mmap` using handle protection/flags, and returns region plus length. Preload/discard align addresses down to connection page size before issuing `posix_madvise`. Preload expands sequential scan hints for `WT_SESSION_READ_WONT_NEED`. Unmap logs and calls `munmap`.

## State and Persistence Behavior
No WiredTiger metadata is persisted. Mapped bytes reflect the backing file. The caller must ensure the underlying file does not change inconsistently while mapped; this layer intentionally has no locking.

## Dependencies and Integration Points
Installed by `os_fs.c` as `fh_map`/`fh_unmap` and optional `fh_map_preload`/`fh_map_discard`. It relies on `WT_FILE_HANDLE_POSIX`, connection page size, block manager map bounds, and POSIX mmap/madvise.

## Risks and Edge Cases
Mapping zero-length files and files that resize underneath the caller are caller responsibilities. Alignment math affects madvise correctness. `MAP_NOCORE` is conditional and platform-specific.

## Test Signals
Mapped reads, scan-preload behavior, discard calls, zero-length/error paths, and map/unmap leak checks are relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_mtx_cond.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_mtx_cond.c

## Purpose
Provides POSIX condition-variable allocation, timed/untimed wait, broadcast signal, and destruction for WiredTiger's `WT_CONDVAR`.

## Important APIs, Types, and Functions
`__wt_cond_alloc`, `__wt_cond_wait_signal`, `__wt_cond_signal`, and `__wt_cond_destroy` wrap pthread mutex/condition primitives and maintain `cond->waiters`.

## Control Flow
Allocation initializes a mutex and a condition variable, preferring `CLOCK_MONOTONIC` when configured. Wait increments `waiters`; if the prior value indicates a stored signal, it returns immediately. Otherwise it locks, optionally checks `run_func`, calculates an absolute timeout, waits, treats timeout/EINTR as unsignalled, decrements waiters, unlocks, and panics on unexpected pthread errors. Signal uses a full memory barrier, records a fast-path signal when no waiters exist, or broadcasts under the mutex.

## State and Persistence Behavior
Only in-memory synchronization state changes. `waiters == -1` represents a pending signal for the next waiter, avoiding lost wakeups in common exit paths.

## Dependencies and Integration Points
Used broadly by eviction, checkpoint, logging, and service threads. Integrates with tracking macros, stats, verbose mutex logging, and `__wt_epoch_raw` fallback for timed waits.

## Risks and Edge Cases
Lost wakeup avoidance depends on `waiters` atomic transitions and the optional `run_func`. Timed waits without monotonic pthread support can be affected by wall-clock changes. Destroy panics on live/invalid primitives.

## Test Signals
Threaded wake/wait tests, timeout behavior, stored-signal fast path, run-function cancellation, and sanitizer runs for destroy races are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_mtx_cond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_once.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_once.c

## Purpose
Provides process-wide one-time initialization for POSIX builds.

## Important APIs, Types, and Functions
`__wt_once(void (*init_routine)(void))` wraps `pthread_once` with a static `pthread_once_t`.

## Control Flow
Every call passes the same static once control object to `pthread_once`, so the first successful call invokes the supplied routine and subsequent calls return without invoking it again.

## State and Persistence Behavior
The only state is the process-local `pthread_once_t`; nothing is persisted. Because the control object is shared, this wrapper supports a single global initialization site, not one distinct once state per caller.

## Dependencies and Integration Points
Used by code that requires platform-independent one-time initialization. Relies on pthread semantics for thread safety and memory ordering.

## Risks and Edge Cases
Passing different routines after the first call will not run them. Errors are returned directly from `pthread_once` and should be rare.

## Test Signals
Concurrent multi-thread invocation should run the routine exactly once and propagate pthread errors if injected.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_once.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_pagesize.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_pagesize.c

## Purpose
Reports the system virtual-memory page size for POSIX builds.

## Important APIs, Types, and Functions
`__wt_get_vm_pagesize(void)` returns `getpagesize()`.

## Control Flow
The function directly calls libc and returns the integer result.

## State and Persistence Behavior
No state is changed. The value influences mmap alignment, allocation assumptions, and page-size-aware hints elsewhere.

## Dependencies and Integration Points
Consumed during connection/platform initialization and by mmap advice alignment logic.

## Risks and Edge Cases
No error handling is present because `getpagesize` is expected to be reliable. Portability depends on the platform exposing it.

## Test Signals
Startup/platform tests should confirm a positive page size and consistency with map alignment assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_pagesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_path.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_path.c

## Purpose
Provides POSIX path semantics for absolute-path detection and path separators.

## Important APIs, Types, and Functions
`__wt_absolute_path` checks for leading `/`; `__wt_path_separator` returns `/`.

## Control Flow
Both functions are direct helpers with no allocation or error path.

## State and Persistence Behavior
No state is read or written. Their output affects how WiredTiger builds filenames under home directories.

## Dependencies and Integration Points
Used by portable path-construction code and filesystem configuration.

## Risks and Edge Cases
Relative paths beginning with other platform syntaxes are not treated as absolute on POSIX. Null path inputs are not guarded.

## Test Signals
Path utility tests should cover absolute, relative, empty, and nested POSIX paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_priv.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_priv.c

## Purpose
Detects whether the process is running with elevated or changed effective POSIX privileges.

## Important APIs, Types, and Functions
`__wt_has_priv` compares real/effective UID and GID via `getuid`, `geteuid`, `getgid`, and `getegid`.

## Control Flow
Returns true when either UID or GID differs, false otherwise.

## State and Persistence Behavior
No persistent state. The result can influence security-sensitive configuration decisions.

## Dependencies and Integration Points
Integrated into portable security checks that should behave differently for setuid/setgid processes.

## Risks and Edge Cases
It detects changed effective IDs, not every possible privilege mechanism such as capabilities or platform ACLs.

## Test Signals
Unit tests can mock or run under controlled IDs; integration should verify behavior in setuid/setgid-like environments where available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_priv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_setvbuf.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_setvbuf.c

## Purpose
Centralizes stream-buffering changes so portable code avoids direct `setvbuf` calls that behave differently on Windows.

## Important APIs, Types, and Functions
`__wt_stream_set_line_buffer(FILE *)` and `__wt_stream_set_no_buffer(FILE *)`.

## Control Flow
Line buffering calls `setvbuf(fp, NULL, _IOLBF, 1024)`; no buffering calls `setvbuf(fp, NULL, _IONBF, 0)`. Return values are ignored.

## State and Persistence Behavior
Only the C runtime buffering mode for the provided stream changes. No file content is flushed explicitly here beyond libc side effects.

## Dependencies and Integration Points
Used by logging/diagnostic output setup and extension-visible helpers where consistent stream behavior matters.

## Risks and Edge Cases
Ignored errors mean callers cannot detect unsupported streams. Existing buffered data ordering depends on libc behavior around mode changes.

## Test Signals
Output buffering tests should verify prompt visibility for diagnostics and no regression on POSIX/Windows compatibility assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_setvbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_sleep.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_sleep.c

## Purpose
Implements a portable sleep helper for POSIX builds.

## Important APIs, Types, and Functions
`__wt_sleep(uint64_t seconds, uint64_t micro_seconds)` converts to `timeval` and calls `select`.

## Control Flow
The function issues a full memory barrier, normalizes microseconds into seconds plus remainder, then sleeps with `select(0, NULL, NULL, NULL, &t)`.

## State and Persistence Behavior
No persistent state. The barrier is part of the synchronization contract for callers that sleep while waiting for state changes.

## Dependencies and Integration Points
Used by retry loops, backoff, tests, and service threads that need subsecond sleeps without exposing platform APIs.

## Risks and Edge Cases
`select` interruptions are ignored, so sleeps may end early. Very large inputs rely on `time_t`/`suseconds_t` conversion ranges.

## Test Signals
Backoff timing tests, EINTR stress, and memory-order-sensitive wake/sleep tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_snprintf.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_snprintf.c

## Purpose
Wraps POSIX `vsnprintf` while accumulating the formatted length in a caller-supplied counter.

## Important APIs, Types, and Functions
`__wt_vsnprintf_len_incr(char *, size_t, size_t *, const char *, va_list)`.

## Control Flow
Calls `vsnprintf`; on non-negative return, adds that length to `*retsizep` and succeeds. On failure, returns current errno through `__wt_errno`.

## State and Persistence Behavior
Only caller buffers and counters are affected. No persistent state.

## Dependencies and Integration Points
Used by portable formatted-buffer builders that need both truncating writes and total required length accounting.

## Risks and Edge Cases
Behavior follows POSIX `vsnprintf`; callers must manage `va_list` lifetime. Counter growth can overflow if caller does not bound it.

## Test Signals
Tests should cover exact fit, truncation, zero-size buffers, invalid format failure, and cumulative length accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_snprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_thread.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_thread.c

## Purpose
Provides POSIX thread creation, join, identity, process ID, and Linux thread-name support.

## Important APIs, Types, and Functions
`__wt_thread_create`, `__wt_thread_join`, `__wt_thread_id`, `__wt_thread_str`, and `__wt_process_id`; Linux builds also use internal thread-name setup.

## Control Flow
Thread creation initializes attributes, sets joinable state, creates the pthread, optionally names it from session/thread metadata, and destroys attributes. Join calls `pthread_join`. Thread ID is derived from `pthread_self` into `uintmax_t`; string form formats that ID. Process ID returns `getpid`.

## State and Persistence Behavior
Creates and joins OS threads but writes no WiredTiger persistent state. Thread naming affects OS diagnostics only.

## Dependencies and Integration Points
Used by background services, worker threads, and diagnostics. Integrates with session names and portable type `wt_thread_t`.

## Risks and Edge Cases
Thread ID formatting assumes `pthread_t` can be represented as copied bytes/number on supported platforms. Naming truncation is platform-limited. Attribute setup failures must not leak attributes.

## Test Signals
Thread lifecycle tests, join error/failure injection, thread ID uniqueness, and Linux name visibility tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_time.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_time.c

## Purpose
Provides raw epoch time and thread-safe local-time conversion for POSIX builds.

## Important APIs, Types, and Functions
`__wt_epoch_raw` uses `clock_gettime(CLOCK_REALTIME)` when available or `gettimeofday`; `__wt_localtime` wraps `localtime_r`.

## Control Flow
Epoch initializes the output to zero, retries the selected syscall, fills seconds/nanoseconds, and panics on failure. Localtime returns success if `localtime_r` returns non-NULL, otherwise reports errno.

## State and Persistence Behavior
No state is persisted. The returned wall-clock time feeds timestamps, diagnostics, and timeout calculations where monotonic time is unavailable.

## Dependencies and Integration Points
Used by condition variables, logging, statistics, and time utilities. Depends on configure-time availability of `clock_gettime` or `gettimeofday`.

## Risks and Edge Cases
Wall-clock adjustments can affect callers using epoch time for intervals. `__wt_epoch_raw` panics on errors to simplify callers.

## Test Signals
Platform startup tests should validate nonzero epoch values and localtime failure handling through fault injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_yield.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_yield.c

## Purpose
Provides a portable thread-yield helper for POSIX builds.

## Important APIs, Types, and Functions
`__wt_yield(void)` wraps `sched_yield`.

## Control Flow
Issues a full memory barrier and calls `sched_yield`, ignoring the return.

## State and Persistence Behavior
No persisted state. The barrier plus scheduler yield supports spin/backoff loops and cooperative waiting.

## Dependencies and Integration Points
Used by low-level synchronization paths such as reconcile child-state loops and remap waiting.

## Risks and Edge Cases
Scheduler behavior is platform-dependent and may not provide fairness. Ignored errors mean no caller-visible failure.

## Test Signals
Contention/backoff stress tests and sanitizer runs for spin-wait loops are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dir.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_dir.c

## Purpose
Implements Windows directory listing for WiredTiger's file-system abstraction, including prefix filtering and single-result mode.

## Important APIs, Types, and Functions
`__directory_list_worker`, `__wti_win_directory_list`, `__wti_win_directory_list_single`, and `__wti_win_directory_list_free`.

## Control Flow
The worker normalizes the directory, builds a `\*` search path, converts path and prefix to UTF-16, iterates `FindFirstFileW`/`FindNextFileW`, skips `.`/`..`, applies optional prefix matching, converts matched names back to UTF-8, duplicates them into a growable array, and frees partial results on error.

## State and Persistence Behavior
No persistent state is changed. Returned file-name arrays are heap allocated and must be freed by the paired free function.

## Dependencies and Integration Points
Installed by `os_win/os_fs.c` in the Windows `WT_FILE_SYSTEM`. Relies on UTF conversion helpers and Windows error mapping.

## Risks and Edge Cases
Prefix conversion is performed even when prefix may be NULL, so correctness depends on helper/caller expectations. Errors during cleanup can overwrite return codes. Directory order is filesystem-defined.

## Test Signals
Tests should cover empty directories, prefix filters, Unicode names, single-result mode, cleanup on mid-iteration allocation failure, and Windows error mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dlopen.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_dlopen.c

## Purpose
Provides Windows dynamic-symbol lookup support for the extension API, currently supporting symbols in the current binary.

## Important APIs, Types, and Functions
`__wt_dlopen`, `__wt_dlsym`, and `__wt_dlclose` operate on `WT_DLH`.

## Control Flow
`__wt_dlopen` allocates a handle structure, stores a display name, and for `path == NULL` uses `GetModuleHandleExW`; non-NULL DLL loading is marked TODO and breaks into the debugger. `__wt_dlsym` calls `GetProcAddress`, optionally errors if missing. `__wt_dlclose` calls `FreeLibrary` and frees memory.

## State and Persistence Behavior
Only process module handles and memory are affected. No persistent state.

## Dependencies and Integration Points
Used by extension loading and symbol lookup on Windows. Integrates with Windows error formatting/mapping.

## Risks and Edge Cases
Non-NULL path support is incomplete. The implementation duplicates `dlh->name` twice, leaking the first allocation unless hidden by allocator behavior. Closing a handle obtained from the current process module needs careful Windows reference-count semantics.

## Test Signals
Tests should cover local symbol lookup, missing optional/required symbols, non-NULL path behavior, and leak detection around open/close.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dlopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_fs.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_fs.c

## Purpose
Implements Windows `WT_FILE_SYSTEM` and file-handle operations for create/open, read/write, sync, size, rename/remove, locking, mapping hooks, and free-space queries.

## Important APIs, Types, and Functions
`__wt_os_win` installs the file-system jump table. `__win_open_file`, `__win_file_read`, `__win_file_write`, `__win_file_sync`, `__win_file_set_end`, `__win_file_lock`, `__win_fs_remove`, `__win_fs_rename`, and `__wti_win_fs_size` implement core operations. `WT_WINCALL_RETRY` retries access-denied operations.

## Control Flow
Path-taking operations convert UTF-8 to UTF-16. Open maps WiredTiger flags to `CreateFileW` access, share, disposition, write-through, random/sequential hints, and opens a secondary handle for truncation/extension. I/O uses `ReadFile`/`WriteFile` with `OVERLAPPED` offsets and 1GB chunks. Remove/rename retry transient `ERROR_ACCESS_DENIED`, useful for virus scanners. Rename uses `MoveFileExW` with replacement and write-through.

## State and Persistence Behavior
`FlushFileBuffers` provides file flushes; Windows directory handles are not opened for durability. Secondary handles allow file-size changes without moving the main I/O pointer. No WiredTiger metadata is persisted directly.

## Dependencies and Integration Points
Uses UTF conversion, Windows error mapping, directory-list hooks, map/unmap hooks, log sync configuration, connection write-through flags, and standard WiredTiger allocation/error macros.

## Risks and Edge Cases
Create flag handling is easy to misread: exclusive/create disposition behavior needs tests. Windows rename is not documented as atomic across all cases, so code avoids copy fallback. Secondary-handle failures disable truncate/extend. Access-denied retries can mask external interference only briefly.

## Test Signals
Windows filesystem tests should cover Unicode paths, open/create/exclusive combinations, concurrent extension with reads, rename/remove under sharing conflicts, free-space queries, and write-through/sync behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_futex.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_futex.c

## Purpose
Implements WiredTiger futex-style wait/wake primitives on Windows using `WaitOnAddress` and wake-by-address APIs.

## Important APIs, Types, and Functions
`__wt_futex_wait` and `__wt_futex_wake` operate on `WT_FUTEX_WORD`.

## Control Flow
Wait converts a positive microsecond timeout to at least one millisecond, waits while the address equals the expected value, returns the observed wake value on success, and maps Windows errors to `errno` on failure. Wake atomically exchanges the futex word to the wake value and wakes either one or all waiters.

## State and Persistence Behavior
Only the in-memory futex word changes. The implementation relies on x86 TSO memory ordering for seeing wake writes.

## Dependencies and Integration Points
Used by lower-level synchronization code where POSIX builds may use futex syscalls. Links `Synchronization.Lib`.

## Risks and Edge Cases
Comments explicitly note Windows ARM would require review. Timeout precision is millisecond-granularity. Error handling sets global `errno`.

## Test Signals
Concurrency tests should cover one/all wake, timeout, observed wake values, and stress under high contention.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_getenv.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_getenv.c

## Purpose
Provides Windows environment-variable retrieval with WiredTiger-owned output storage.

## Important APIs, Types, and Functions
`__wt_getenv` uses `getenv_s` sizing and value retrieval.

## Control Flow
The function initializes `*envp` to NULL, queries the required length, returns absent for errors or zero-length values, allocates that size, then calls `getenv_s` again to populate the buffer.

## State and Persistence Behavior
No persistent state. Returned memory is allocated through WiredTiger and must be freed by callers.

## Dependencies and Integration Points
Used by portable environment configuration paths. Depends on MSVC secure CRT behavior and WiredTiger allocation.

## Risks and Edge Cases
The environment can change between sizing and retrieval. Empty values are treated as absent. CRT errors are silently converted to absence in the sizing step.

## Test Signals
Tests should cover absent, empty, non-empty, long variables, and injected allocation/retrieval failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_getenv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_map.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_map.c

## Purpose
Implements Windows explicit memory mapping and unmapping for file handles.

## Important APIs, Types, and Functions
`__wti_win_map` uses `CreateFileMappingW` and `MapViewOfFile`; `__wti_win_unmap` uses `UnmapViewOfFile` and `CloseHandle`.

## Control Flow
Map gets file size, chooses read-only or read/write mapping protections from handle access, creates a mapping object, maps a view for the full file length, and returns both the view and mapping cookie. Unmap releases the view and closes the mapping handle.

## State and Persistence Behavior
No WiredTiger state is persisted. The mapping cookie is required to close the kernel mapping object after unmapping.

## Dependencies and Integration Points
Installed into Windows file handles by `os_fs.c`. Depends on `WT_FILE_HANDLE_WIN`, `__wti_win_fs_size`, and Windows error formatting.

## Risks and Edge Cases
Callers must prevent concurrent incompatible file-size changes. `__wti_win_unmap` treats `mapped_cookie` as a pointer to a handle slot, which must match the caller's cookie storage convention. Zero-length file mapping behavior needs coverage.

## Test Signals
Mapped read/write tests, unmap cleanup checks, zero-length/error paths, and cookie-handle leak tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_cond.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_mtx_cond.c

## Purpose
Provides Windows condition-variable support for WiredTiger using `CRITICAL_SECTION` and native condition variables.

## Important APIs, Types, and Functions
`__wt_cond_alloc`, `__wt_cond_wait_signal`, `__wt_cond_signal`, and `__wt_cond_destroy`.

## Control Flow
Allocation initializes a critical section and condition variable. Wait increments `waiters`, returns on stored signal, enters the critical section, optionally checks `run_func`, converts microseconds to milliseconds with minimum 1ms and overflow cap, waits, handles timeout as unsignalled, decrements waiters, and panics on unexpected failure. Signal uses a full barrier, stores a signal if no waiters exist, or wakes all under the critical section.

## State and Persistence Behavior
Only in-memory synchronization state changes. `waiters == -1` records a pending signal for the next waiter.

## Dependencies and Integration Points
Used by cross-platform background-thread coordination. Mirrors POSIX condition semantics closely while adapting timeout units.

## Risks and Edge Cases
Timeout rounding can lengthen short waits. The fast-path waiter state must remain consistent with atomic operations. Windows errors other than timeout panic.

## Test Signals
Thread wake/timeout tests, stored-signal tests, run-function cancellation, and high-contention stress are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_cond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_sem.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_mtx_sem.c

## Purpose
Implements WiredTiger semaphore primitives on Windows.

## Important APIs, Types, and Functions
`__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait`.

## Control Flow
Init creates a Windows semaphore with the requested initial count and max `INT32_MAX`. Destroy closes the handle and clears the structure. Post releases one count. Wait blocks indefinitely with `WaitForSingleObject` and maps failures.

## State and Persistence Behavior
Only kernel semaphore state and the `WT_SEMAPHORE` structure change; no persistent state is written.

## Dependencies and Integration Points
Used where POSIX builds use semaphores or equivalent synchronization. Error messages use Windows formatting.

## Risks and Edge Cases
Counts are limited to `INT32_MAX`. Wait has no timeout/cancel path here. Destroying while waiters exist is unsafe and must be prevented by callers.

## Test Signals
Producer/consumer semaphore tests, post/wait ordering, destroy failure injection, and count-limit checks are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_once.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_once.c

## Purpose
Provides one-time process initialization for Windows builds.

## Important APIs, Types, and Functions
`__wt_once` uses Windows one-time initialization support around a caller routine.

## Control Flow
The implementation stores the routine in static state and uses the Windows init-once callback path to run it once for the process.

## State and Persistence Behavior
State is process-local and static. No persistent data is written.

## Dependencies and Integration Points
Used by portable one-time initialization paths that call `__wt_once` without exposing platform-specific primitives.

## Risks and Edge Cases
Like the POSIX wrapper, a single static once state means later different routines are not independently executed. Callback error propagation is limited by Windows `InitOnce` semantics.

## Test Signals
Multi-threaded calls should execute exactly once and leave initialized state visible to all callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_once.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_pagesize.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_pagesize.c

## Purpose
Reports Windows virtual-memory page size.

## Important APIs, Types, and Functions
`__wt_get_vm_pagesize` calls `GetSystemInfo` and returns `dwPageSize`.

## Control Flow
The function fills a `SYSTEM_INFO` structure and returns the page-size field.

## State and Persistence Behavior
No state changes. The result is used for memory mapping and page-aligned operations.

## Dependencies and Integration Points
Used by platform initialization and mapping helpers that need page-size alignment.

## Risks and Edge Cases
Assumes `dwPageSize` fits in `int`, which is true for normal Windows systems.

## Test Signals
Startup tests should validate a positive page size and consistency with allocation granularity assumptions where relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_pagesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_path.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_path.c

## Purpose
Provides Windows absolute-path and path-separator helpers.

## Important APIs, Types, and Functions
`__wt_absolute_path` and `__wt_path_separator`.

## Control Flow
Absolute detection recognizes drive-rooted paths like `C:\...`, drive-relative absolute-ish paths, and UNC-style leading separators. Separator returns `\`.

## State and Persistence Behavior
No state changes. Results guide filename construction under WiredTiger home directories.

## Dependencies and Integration Points
Used by portable path normalization and filesystem code before UTF-16 conversion.

## Risks and Edge Cases
Windows path grammar is broad; device paths and mixed slashes need coverage. Null/short inputs must satisfy assumptions in the implementation.

## Test Signals
Tests should cover drive paths, UNC paths, relative paths, slash variants, and empty strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_priv.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_priv.c

## Purpose
Provides the Windows implementation of privilege detection.

## Important APIs, Types, and Functions
`__wt_has_priv(void)` currently returns false.

## Control Flow
There is no probing; Windows builds report no special POSIX-style privilege state.

## State and Persistence Behavior
No state changes.

## Dependencies and Integration Points
Satisfies the portable privilege-check API for callers shared with POSIX.

## Risks and Edge Cases
This does not detect Administrator elevation, service accounts, privileges, or token changes. Callers needing Windows-specific security must not rely on this alone.

## Test Signals
Compatibility tests should assert the stable false result; security-sensitive Windows behavior needs separate coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_priv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_setvbuf.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_setvbuf.c

## Purpose
Centralizes stream-buffering changes for Windows, accounting for MSVC's lack of true line buffering.

## Important APIs, Types, and Functions
`__wt_stream_set_line_buffer` and `__wt_stream_set_no_buffer`.

## Control Flow
Line buffering delegates to no-buffering because MSVC treats line buffering as full buffering. No-buffering calls `setvbuf(fp, NULL, _IONBF, 0)`.

## State and Persistence Behavior
Only the C runtime buffering mode for the provided stream changes.

## Dependencies and Integration Points
Used by diagnostics and logging setup shared with POSIX code.

## Risks and Edge Cases
Return values are ignored. Choosing no buffering for line-buffer requests can affect performance but preserves prompt output.

## Test Signals
Diagnostic-output tests on Windows should verify immediate flush behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_setvbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_sleep.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_sleep.c

## Purpose
Implements portable sleep for Windows builds.

## Important APIs, Types, and Functions
`__wt_sleep(uint64_t seconds, uint64_t micro_seconds)` wraps `Sleep`.

## Control Flow
Issues a full memory barrier, rounds sub-millisecond sleeps up to one millisecond, converts seconds and microseconds to milliseconds, and calls `Sleep`.

## State and Persistence Behavior
No persistent state. The barrier supports synchronization expectations around sleeping.

## Dependencies and Integration Points
Used by retry/backoff loops and platform-independent sleeps.

## Risks and Edge Cases
Conversion to `DWORD` can overflow for very large sleeps. Windows scheduler granularity can exceed requested time.

## Test Signals
Backoff tests, short-sleep rounding checks, and overflow boundary review are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_snprintf.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_snprintf.c

## Purpose
Provides MSVC-compatible formatted-output length accounting matching POSIX-style callers.

## Important APIs, Types, and Functions
`__wt_vsnprintf_len_incr` uses `_vscprintf` and `_vsnprintf_s`.

## Control Flow
For size zero, it only calculates required length. For nonzero size, it rejects NULL buffer/format, writes with `_TRUNCATE`, adds written length on success, and when truncated adds the required length from `_vscprintf`.

## State and Persistence Behavior
Only caller buffers and counters are affected.

## Dependencies and Integration Points
Used by portable string-formatting helpers that expect consistent count accumulation across POSIX and Windows.

## Risks and Edge Cases
The function returns success on truncation after adding required length, so callers must interpret the aggregate size. Invalid parameter handler avoidance depends on explicit NULL/size checks.

## Test Signals
Tests should cover zero-size sizing, exact fit, truncation, NULL inputs, and cumulative count behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_snprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_thread.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_thread.c

## Purpose
Provides Windows thread creation, join, thread ID/string, and process ID helpers.

## Important APIs, Types, and Functions
`__wt_thread_create`, `__wt_thread_join`, `__wt_thread_id`, `__wt_thread_str`, and `__wt_process_id`.

## Control Flow
Create starts a thread with `_beginthreadex` and stores the handle/id. Join waits indefinitely, closes the handle, and clears the thread object. ID helpers use `GetCurrentThreadId`; process ID uses `GetCurrentProcessId`.

## State and Persistence Behavior
Creates OS threads and releases handles; no persistent state. Correct handle closure prevents kernel object leaks.

## Dependencies and Integration Points
Used by background services and diagnostics through portable `wt_thread_t`.

## Risks and Edge Cases
Thread start failures map CRT/Windows errors. Join must only run on valid joinable handles. Thread functions must match `_beginthreadex` calling conventions.

## Test Signals
Thread lifecycle tests, join failure injection, handle leak checks, and ID formatting tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_time.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_time.c

## Purpose
Provides Windows epoch time and local broken-down time conversion.

## Important APIs, Types, and Functions
`__wt_epoch_raw` uses `GetSystemTimeAsFileTime`; `__wt_localtime` wraps `localtime_s`.

## Control Flow
Epoch converts Windows 100ns intervals since 1601 to Unix seconds/nanoseconds by subtracting the Unix epoch offset. Localtime returns success for `localtime_s == 0`, otherwise reports the CRT errno.

## State and Persistence Behavior
No state changes. Wall-clock output feeds diagnostics and time utilities.

## Dependencies and Integration Points
Used by portable time APIs and any Windows fallback timing paths.

## Risks and Edge Cases
Wall-clock changes affect results. Arithmetic assumes standard FILETIME epoch conversion constants and signed range adequacy.

## Test Signals
Tests should compare epoch output with system time tolerance and cover localtime error paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_utf8.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_utf8.c

## Purpose
Converts between WiredTiger's UTF-8 paths/strings and Windows UTF-16 strings.

## Important APIs, Types, and Functions
`__wti_to_utf16_string` wraps `MultiByteToWideChar`; `__wti_to_utf8_string` wraps `WideCharToMultiByte`.

## Control Flow
Each function first queries required buffer size, allocates a scratch buffer, performs conversion including the terminating NUL, sets `WT_ITEM.size`, and frees the scratch buffer on conversion failure.

## State and Persistence Behavior
No persistent state. Returned scratch buffers are session-owned temporaries freed by callers with `__wt_scr_free`.

## Dependencies and Integration Points
Used throughout Windows filesystem and directory code before calling wide-character Win32 APIs.

## Risks and Edge Cases
The error check expects `ERROR_INSUFFICIENT_BUFFER` patterns that sizing calls may not actually set; malformed UTF-8/wide strings must be tested. `WT_ITEM.size` is a count returned by Windows, not necessarily byte semantics for UTF-16 callers.

## Test Signals
Unicode path tests, invalid encoding tests, allocation failure, and round-trip conversion coverage are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_utf8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_winerr.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_winerr.c

## Purpose
Normalizes Windows error reporting into WiredTiger/POSIX-style errors and formatted messages.

## Important APIs, Types, and Functions
`__wt_getlasterror`, `__wt_map_windows_error`, and `__wt_formatmessage`.

## Control Flow
`__wt_getlasterror` returns `GetLastError` but substitutes `ERROR_INVALID_PARAMETER` for `ERROR_SUCCESS`. Mapping scans a fixed table of common Windows errors to errno values and returns `WT_ERROR` otherwise. Formatting grows/uses the session error buffer and calls `FormatMessageA`, with a fallback string if unavailable.

## State and Persistence Behavior
Only the session error buffer may be modified. No persistent state.

## Dependencies and Integration Points
Used by nearly every Windows OS wrapper for consistent error messages and return values.

## Risks and Edge Cases
Unknown Windows errors collapse to `WT_ERROR`, losing specificity. Formatting must tolerate `session == NULL`. Using `__wt_getlasterror` after CRT failures can produce generic errors.

## Test Signals
Mapping-table tests, unknown-error tests, null-session formatting, and post-error message propagation are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_winerr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_yield.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_yield.c

## Purpose
Provides a Windows thread-yield helper.

## Important APIs, Types, and Functions
`__wt_yield(void)` calls `SwitchToThread`.

## Control Flow
Issues a full memory barrier and yields the remainder of the thread's time slice if another ready thread can run.

## State and Persistence Behavior
No persistent state. The barrier contributes to spin-loop synchronization.

## Dependencies and Integration Points
Used by portable backoff and wait loops.

## Risks and Edge Cases
`SwitchToThread` may return without yielding if no suitable thread is ready; the return is ignored.

## Test Signals
Contention stress and progress tests in synchronization-heavy code are the relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_api.c -->
# sources/storage-engines/wiredtiger/src/packing/pack_api.c

## Purpose
Exposes public and extension varargs wrappers for WiredTiger's structure packing, sizing, and unpacking APIs.

## Important APIs, Types, and Functions
`wiredtiger_struct_pack`, `wiredtiger_struct_size`, `wiredtiger_struct_unpack`, plus extension methods `__wt_ext_struct_pack`, `__wt_ext_struct_size`, and `__wt_ext_struct_unpack`.

## Control Flow
Each wrapper converts `WT_SESSION` to `WT_SESSION_IMPL`, starts a `va_list`, delegates to the corresponding `__wt_struct_*v` implementation, ends the `va_list`, and returns the result. Extension wrappers use the connection default session when the extension passes NULL.

## State and Persistence Behavior
Only caller-provided buffers are packed/unpacked; no persistent metadata is written.

## Dependencies and Integration Points
This is the ABI-facing shim over internal pack implementation used by applications and extensions.

## Risks and Edge Cases
Varargs must match the format string exactly; this layer cannot type-check them. NULL extension sessions intentionally use the default session, which affects error context and allocation.

## Test Signals
API compatibility tests, extension NULL-session paths, varargs format mismatch errors, and boundary buffer sizes are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_impl.c -->
# sources/storage-engines/wiredtiger/src/packing/pack_impl.c

## Purpose
Implements internal non-streaming struct packing helpers and format validation wrappers.

## Important APIs, Types, and Functions
`__struct_check`, `__wt_struct_confchk`, `__wt_struct_size`, `__wt_struct_pack`, `__wt_struct_unpack`, and `__wt_struct_repack`.

## Control Flow
Format checking initializes a `WT_PACK`, iterates `__pack_next` until not found, and optionally reports fixed-size bitfield status for empty or single `t` formats. Pack/size/unpack/repack functions wrap varargs and delegate to `__wt_struct_*v` or repack implementation.

## State and Persistence Behavior
No persistent state. Output buffers are filled according to format definitions, and validation results guide configuration acceptance.

## Dependencies and Integration Points
Depends on the lower-level pack parser/read/write implementation and configuration validation paths.

## Risks and Edge Cases
Format parser changes can affect both data encoding and config validation. Fixed-bitfield detection only recognizes the narrow empty/single-`t` cases.

## Test Signals
Format validation tests, fixed-bitfield config cases, size/pack/unpack round trips, and repack compatibility tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_stream.c -->
# sources/storage-engines/wiredtiger/src/packing/pack_stream.c

## Purpose
Implements one-field-at-a-time streaming pack/unpack APIs for applications and extensions.

## Important APIs, Types, and Functions
`WT_PACK_STREAM` stores parser state and buffer pointers. Public methods include `wiredtiger_pack_start`, `wiredtiger_unpack_start`, close, item/int/str/uint packers, and matching unpackers. Extension wrappers `__wt_ext_pack_*` and `__wt_ext_unpack_*` delegate to public methods.

## Control Flow
Start allocates a stream, initializes format parsing, and sets start/current/end pointers. Each pack/unpack method checks remaining space, advances to the next format field, verifies the requested type class, and calls `__pack_write` or `__unpack_read`. Close optionally reports bytes used and frees the stream.

## State and Persistence Behavior
Stream state is in memory and progresses monotonically through the format and buffer. No persistent state is written.

## Dependencies and Integration Points
Used by public WiredTiger APIs and extension API tables. Depends on lower-level packing parser and value encoders.

## Risks and Edge Cases
The zero-length check prevents lower layers from treating zero as unchecked. Type mismatches return illegal-value errors. Callers must not use a closed stream or mutate the backing buffer unexpectedly.

## Test Signals
Streaming round trips, type mismatch errors, buffer boundary/ENOMEM cases, bytes-used reporting, and extension default-session paths should be covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_txn.c -->
# sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_txn.c

## Purpose
Maintains pending prepared-transaction artifacts discovered during recovery/checkpoint walking, including restoration to ingest tables for disaggregated followers.

## Important APIs, Types, and Functions
`__wt_prepared_discover_find_item`, `__wt_prepared_discover_remove_item`, `__wti_prepared_discover_add_artifact_upd`, and `__wti_prepared_discover_restore_and_add_artifact_upd`. Helpers allocate prepared `WT_UPDATE`s and initialize the pending-prepared hash map.

## Control Flow
Find hashes `prepared_id` into a power-of-two bucket. Find-or-create lazily initializes a 256-bucket map, allocates `WT_PENDING_PREPARED_ITEM`, and inserts it. Adding an artifact allocates the next pending transaction op and records the update with btree/key context. Restoration builds an in-progress prepared update from an on-disk time window, searches/modifies the ingest btree under the ingest dhandle, then registers the artifact.

## State and Persistence Behavior
Updates in-memory transaction-global pending prepared state. In disaggregated follower mode it also writes restored updates into the ingest table so later prepare resolution can commit/rollback them.

## Dependencies and Integration Points
Integrates with transaction global state, update allocation, row search/modify, pending prepared op arrays, ingest/stable layered tables, and prepare timestamp/ID fields.

## Risks and Edge Cases
Stop-prepare tombstones are represented as standard updates carrying a special tombstone value because ingest cannot accept tombstones in this flow. Remove asserts `mod_count == 0`, so ownership transfer must be complete. Cursor hazard release before reused searches is critical.

## Test Signals
Prepared recovery tests, disaggregated follower stable-to-ingest restoration, stop-prepare handling, hash collisions, and pending item removal assertions are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_txn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_walk.c -->
# sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_walk.c

## Purpose
Scans metadata and btrees to discover prepared updates after startup/recovery and attach them to pending transaction structures.

## Important APIs, Types, and Functions
`__wt_prepared_discover_filter_apply_handles` is the entry point. Helpers parse checkpoint metadata, decide disaggregated follower stable walks, open ingest cursors, inspect on-disk cells/update lists/insert lists, skip tree branches without prepare metadata, and walk one tree.

## Control Flow
The entry point iterates metadata btree URIs, filters those whose checkpoint config has `prepare=true`, converts stable follower URIs to a latest-checkpoint URI, and walks each tree. Tree walking opens the dhandle, optionally opens the paired ingest cursor, uses `__wt_tree_walk_custom_skip` with visible-all/no-evict flags, and processes leaf pages. Row-store pages scan insert lists, update chains, and disk cells; prepared update chains stop at the first non-prepared update.

## State and Persistence Behavior
Discovers and records in-memory pending prepared operations. On disaggregated followers, on-disk stable prepared cells are restored into ingest before registration. History-store artifacts are ignored unless associated data-store records are found.

## Dependencies and Integration Points
Depends on metadata cursors, checkpoint metadata parsing, tree walk, page/cell unpacking, update visibility, row-store keys, prepared-discover transaction helpers, and layered table naming conventions.

## Risks and Edge Cases
Column-store prepared discovery and prepared truncate are explicitly unsupported and assert. Skipping relies on time-aggregate prepare bits; wrong metadata can miss pages. Follower restoration assumes `.wt_stable` to `.wt_ingest` URI derivation.

## Test Signals
Recovery tests with prepared row-store updates, disaggregated follower restore tests, metadata prepare filtering, branch-skip correctness, unsupported column/truncate fatal paths, and history-store interactions are key.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_walk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_child.c -->
# sources/storage-engines/wiredtiger/src/reconcile/rec_child.c

## Purpose
Determines how an internal-page reconciliation should represent each child reference: original address, modified replacement, proxy fast-delete cell, ignore, or error.

## Important APIs, Types, and Functions
`__wti_rec_child_modify` is the exported decision function. `__rec_child_deleted` handles `WT_REF_DELETED` and instantiated fast-truncate cases. Key state is returned through `WTI_CHILD_MODIFY_STATE`.

## Control Flow
For disk refs, it keeps the original address. Deleted refs are locked and evaluated for visibility, global visibility, prepared state, precise checkpoint timestamp, and previously-selected proxy state. Memory refs may get hazard pointers and inspect `page->modify->rec_result`; instantiated deleted pages are reevaluated as fast deletes. Modified children can be empty, multiblock, or replace. Split/locked states cause wait/retry or diagnostic errors depending on eviction/checkpoint context.

## State and Persistence Behavior
May free globally visible deleted child blocks and clear `ref->page_del`. May set `page_del->selected_for_write` and `r->leave_dirty`. It can force full images instead of deltas to avoid parent deltas referencing freed proxy cells.

## Dependencies and Integration Points
Central to internal-page reconciliation, checkpoint, eviction, fast truncate, rollback-to-stable safety, delta building, page hazard management, and block freeing.

## Risks and Edge Cases
Prepared truncates and uncommitted deletes require strict ordering and locking. Visibility decisions differ for checkpoints, eviction, and no-snapshot reconciliation. Mishandling instantiated deletes can resurrect freed pages or lose truncates.

## Test Signals
Fast-truncate checkpoint/eviction tests, prepared truncate visibility tests, precise checkpoint timestamp tests, delta-vs-full-image regressions, and concurrent page-state transition stress are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_col.c -->
# sources/storage-engines/wiredtiger/src/reconcile/rec_col.c

## Purpose
Reconciles column-store pages, including bulk variable-length inserts, column internal pages, and variable-length column-store leaf pages.

## Important APIs, Types, and Functions
`__wt_bulk_insert_var`, `__wti_rec_col_int`, and `__wti_rec_col_var` are the main entry points. Helpers include `__rec_col_merge` and `__rec_col_var_helper`.

## Control Flow
Bulk insert builds delete or value cells, optionally dictionary-compresses, copies into the reconciliation image, updates time aggregates, and advances record numbers. Internal reconciliation walks child refs, asks `__wti_rec_child_modify` for state, merges multiblock children, builds/copies address/proxy cells, updates aggregates, and splits as needed. VLCS leaf reconciliation walks on-page RLE cells and append lists, selects visible updates, reconstructs modifies, handles stale values/tombstones, manages overflow reuse/removal, coalesces equal adjacent values into RLE runs, and writes the final split image.

## State and Persistence Behavior
Produces new disk images and parent time aggregates. It removes unused overflow blocks, clears stale on-disk values, may clear history-store entries for no-timestamp tombstones, and can convert all-deleted pages to empty namespace gaps when safe.

## Dependencies and Integration Points
Depends on update selection, time windows, dictionary replacement, split machinery, overflow management, history-store cleanup, salvage cookies, column insert lists, and child reconciliation.

## Risks and Edge Cases
VLCS gaps, UINT64_MAX record numbers, overflow values reused across RLE entries, skipped aborted prepared updates, and salvage trimming are all delicate. Prepared preservation asserts prevent leaking on-page prepared updates.

## Test Signals
Column-store reconciliation tests should cover RLE coalescing, append gaps, overflow reuse/removal, modify reconstruction, no-timestamp tombstone cleanup, salvage, all-deleted page emptying, and prepared-preserve scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_col.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_dictionary.c -->
# sources/storage-engines/wiredtiger/src/reconcile/rec_dictionary.c

## Purpose
Maintains the per-page reconciliation dictionary used to replace repeated values with copy cells.

## Important APIs, Types, and Functions
`__wti_rec_dictionary_init`, `__wti_rec_dictionary_free`, `__wti_rec_dictionary_reset`, and `__wti_rec_dictionary_lookup`. Internal skiplist helpers search, build insert stacks, and insert by hash.

## Control Flow
Initialization frees any prior dictionary, allocates a fixed slot array, and gives each slot a random skiplist depth. Reset clears the skiplist heads and next-slot counter at restart/page boundary. Lookup hashes the candidate value, scans matching hashes, uses `__wt_cell_pack_value_match` to confirm exact packed-cell equality, returns a match if found, or inserts a new dictionary entry if slots remain.

## State and Persistence Behavior
Dictionary state is in-memory and scoped to the current reconciliation page. Matching entries cause output cells to reference earlier values in the same disk image; no standalone persistent dictionary exists.

## Dependencies and Integration Points
Used by reconciliation value-cell builders for row/column pages when dictionary compression is enabled. Depends on CityHash, skiplist depth selection, and current reconciliation image offsets.

## Risks and Edge Cases
Hash collisions require exact cell comparison. Once slots are exhausted, new values are not added but existing entries remain usable. Reset must happen at page boundaries to avoid cross-page references.

## Test Signals
Dictionary compression tests should include repeated values, hash collision simulation, slot exhaustion, restart/reset behavior, and validation that copy offsets refer to same-page cells.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_dictionary.c -->
