# Grouped Research: subset-b-007809

This grouped report covers the requested OpenAFS utility and venus build files. Each file section is bounded by reconciliation markers so the section can be split into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/dirpath.c -->
# sources/distributed-fs/openafs/src/util/dirpath.c

Purpose: Implements the runtime directory path table used by OpenAFS utilities and servers to map canonical AFS paths such as `/usr/afs/bin` and `/usr/afs/etc` onto local install paths. It exists primarily to support Windows installations with configurable roots while preserving Unix and wire-format path compatibility.

Important APIs and functions: `initAFSDirPath()` initializes the path table and returns `AFSDIR_CLIENT_PATHS_OK` / `AFSDIR_SERVER_PATHS_OK`; `afs_getDirPath()` exposes indexed strings; Windows also exports `getDirPath()` for ABI compatibility. `ConstructLocalPath()`, `ConstructLocalBinPath()`, and `ConstructLocalLogPath()` convert canonical or relative paths into allocated local paths. Internal helpers include `initDirPathArray()` and `LocalizePathHead()`.

Control flow and state: The module maintains static `dirPathArray`, `initFlag`, `initStatus`, and top-level server/client path buffers. Under pthreads, initialization is guarded by `pthread_once`; otherwise it is lazy but not otherwise synchronized. Windows initialization reads server/client install/config paths through `afssw_GetServerInstallDir()` and `afssw_GetClientCellServDBDir()`, normalizes paths, derives short-path variants, then populates every path id. Unix uses compile-time canonical paths, with Darwin alternate client paths if present.

Dependencies and integration: Depends on `afsutil.h`, `fileutil.h`, roken, `afs/opr.h`, Windows registry/install APIs under `AFS_NT40_ENV`, and path macro/id definitions from `dirpath_nt.h`. Other subsystems use the exported macros to locate logs, databases, cell config, server binaries, and migration files.

Risks and test signals: The static arrays are fixed-size and rely on `strcompose`, `strcpy`, `strcat`, and `sprintf` usage staying within `AFSDIR_PATH_MAX`. Invalid `afsdir_id_t` values are not bounds checked. `ConstructLocalPath()` returns allocated memory that callers must free. `util/test/dirpath_test.c` exercises path table output and local path construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/dirpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/dirpath_nt.h -->
# sources/distributed-fs/openafs/src/util/dirpath_nt.h

Purpose: Defines the OpenAFS directory path contract: canonical path constants, file-name constants, path id enumeration, and convenience macros that route local paths through `afs_getDirPath()`. Despite the `_nt` suffix, it is the primary public header for the dirpath abstraction across platforms.

Important APIs and types: Declares `initAFSDirPath()`, `ConstructLocalPath()`, `ConstructLocalBinPath()`, `ConstructLocalLogPath()`, `afs_getDirPath()`, and legacy `getDirPath()`. Defines `afsdir_id_t`, with ids for server directories, client directories, and many server/client files such as `AFSDIR_SERVER_KEY_FILEPATH_ID`, `AFSDIR_CLIENT_CELLSERVDB_FILEPATH_ID`, and `AFSDIR_SERVER_EXT_KEY_FILEPATH_ID`.

Control flow and state: This header has no runtime state, but it defines the index order that must exactly match `dirpath.c` population. Macros like `AFSDIR_SERVER_LOGS_DIRPATH` perform a function call into the initialized table, so callers implicitly depend on lazy initialization and the static table lifetime.

Dependencies and integration: Includes `afs/param.h`, `limits.h`, and `windef.h` on Windows. It is central to server logging, config lookup, bosserver-related code, cache-manager config, and command-line tools that need canonical versus local path behavior.

Risks and test signals: The enum is an ABI/behavioral contract; adding or reordering ids without updating `dirpath.c` breaks macro results. Some macros are duplicated (`AFSDIR_SERVER_LOCAL_DIRPATH`, `AFSDIR_SERVER_MIGRATE_DIRPATH`), which is harmless for preprocessing but a maintenance smell. `dirpath_test` prints many macros and gives a direct smoke test for header/table consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/dirpath_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/errmap_nt.c -->
# sources/distributed-fs/openafs/src/util/errmap_nt.c

Purpose: Provides a small Windows-to-POSIX error translation routine so NT platform code can report Unix-like `errno` values to the rest of OpenAFS.

Important APIs and state: Exports `nterr_nt2unix(long ntErr, int defaultErr)`. Also defines global `nterr_lastNTError`, intentionally useful in core dumps for older LWP-based binaries.

Control flow: The function stores the incoming NT error code in `nterr_lastNTError`, then maps selected Win32 errors to POSIX-style values: invalid parameters to `EINVAL`, missing files/paths/drives to `ENOENT`, access denial to `EACCES`, disk full to `ENOSPC`, memory failures to `ENOMEM`, pipe errors to `EPIPE`, sharing/pipe busy to `EBUSY`, and so on. Unknown errors return the caller-provided default.

Dependencies and integration: Includes `windows.h` and `afs/errmap_nt.h`. Used by Windows shims such as `readdir_nt.c` and other code needing stable cross-platform error semantics.

Risks and test signals: The mapping is intentionally incomplete; callers must choose a sensible `defaultErr`. `nterr_lastNTError` is global and unsynchronized, so it is diagnostic only in threaded code. There is no local unit test in this subset; Windows directory and socket error paths indirectly exercise it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/errmap_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/errmap_nt.h -->
# sources/distributed-fs/openafs/src/util/errmap_nt.h

Purpose: Declares NT error translation and fills in POSIX `errno` constants missing from some Microsoft C runtime versions, using Winsock values or OpenAFS private values.

Important APIs and macros: Declares `nterr_nt2unix(long ntErr, int defaultErr)`. Defines socket-related errno aliases such as `EWOULDBLOCK`, `EINPROGRESS`, `ENOTSOCK`, `ECONNRESET`, `EHOSTUNREACH`, and private additions based at `AFS_NT_ERRNO_BASE` for `EOVERFLOW`, `ENOMSG`, `ETIME`, and `ENOTBLK`.

Control flow and state: Header-only compatibility layer. It is conditionally additive: values are defined only when the platform headers do not define them.

Dependencies and integration: Includes `<errno.h>` and expects Winsock constants like `WSAEWOULDBLOCK` and `WSABASEERR` to be visible through Windows networking headers in the including translation unit. Windows portability files include it before converting `GetLastError()` or socket errors.

Risks and test signals: The private errno namespace assumes no collision above `WSABASEERR + 1100`. Because the header references Winsock names, include ordering matters on Windows. No direct tests are present; compile coverage across Visual Studio variants is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/errmap_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/errors.h -->
# sources/distributed-fs/openafs/src/util/errors.h

Purpose: Defines historical OpenAFS/VICE volume and server error codes used across volume, fileserver, and client-facing paths.

Important constants: Maps `VREADONLY` to `EROFS`; defines special volume errors starting at `VICE_SPECIAL_ERRORS` including `VSALVAGE`, `VNOVNODE`, `VNOVOL`, `VVOLEXISTS`, `VNOSERVICE`, `VOFFLINE`, `VONLINE`, `VDISKFULL`, `VOVERQUOTA`, `VBUSY`, `VMOVED`, `VIO`, `VSALVAGING`, `VRESTRICTED`, and negative `VRESTARTING`.

Control flow and state: Header-only constants, no runtime control flow or state. The numeric values are part of the protocol/behavioral contract between OpenAFS components.

Dependencies and integration: Relies on platform errno definitions such as `EROFS`. Included by components that need common error codes for volume operations and file-server responses.

Risks and test signals: Changing values would be wire/protocol incompatible. Some comments describe semantic distinctions, for example retryable busy/restarting versus offline/restricted states; callers must preserve these semantics. Tests are indirect through volume-server, cache-manager, and command behavior rather than this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/exec.c -->
# sources/distributed-fs/openafs/src/util/exec.c

Purpose: Implements helper logic for re-executing an alternate variant of the current program, for example a DAFS versus non-DAFS or architecture-specific executable.

Important APIs and functions: Public `afs_exec_alt(int argc, char **argv, const char *prefix, const char *suffix)` constructs an alternate `argv[0]` by inserting a prefix before the basename and appending a suffix. Private `construct_alt()` performs the basename manipulation.

Control flow and state: `afs_exec_alt()` normalizes null prefix/suffix to empty strings, rejects an empty prefix plus empty suffix with `EINVAL`, allocates a new argv vector, duplicates all arguments, and calls `execvp()`. On success it never returns. On failure it preserves `errno`, frees duplicated arguments except the alternate program string, and returns that allocated string for caller diagnostics.

Dependencies and integration: Uses roken/libc memory and process APIs. This is useful in command-line tools that can delegate to sibling binaries without manually reconstructing command lines.

Risks and test signals: The function assumes `argc` and `argv` are valid and that `argv[0]` is non-null. Callers must free the returned alternate program name on failure. There are no direct tests in this subset; behavior is usually tested through tools that attempt alternate executable dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/fileutil.c -->
# sources/distributed-fs/openafs/src/util/fileutil.c

Purpose: Provides low-level file path normalization and buffered file-descriptor reading without using `FILE *`, preserving compatibility with historical fileserver limitations and Windows CRT differences.

Important APIs: `FilepathNormalizeEx(char *path, int slashType)` rewrites slashes, collapses repeated separators, and removes a trailing separator except root/drive-root cases. `FilepathNormalize()` selects forward slashes. `BufioOpen()`, `BufioGets()`, and `BufioClose()` implement a small buffered line reader over `open`/`read`/`close` or `_open`/`_read`/`_close`.

Control flow and state: `BufioOpen()` allocates a `bufio_t`, opens the file, and initializes `pos`, `len`, and `eof`. `BufioGets()` refills the 4096-byte buffer as needed, copies until newline or caller buffer limit, null terminates, and returns length or `-1` for EOF/error. It does not strip carriage returns despite the comment saying so; it only terminates at `\n`.

Dependencies and integration: Includes `fileutil.h`, roken, `afs/stds.h`, and `errmap_nt.h` on Windows. `dirpath.c`, host temp-dir logic, and config readers depend on normalized slash conventions.

Risks and test signals: `FilepathNormalizeEx()` decrements `pP` even for an empty string, which can underflow before comparing; callers should avoid empty mutable strings. `BufioGets()` truncates long lines without signaling that truncation occurred. Direct tests are not present here, but path normalization is exercised by `dirpath_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/fileutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/fileutil.h -->
# sources/distributed-fs/openafs/src/util/fileutil.h

Purpose: Public declaration of file path normalization and descriptor-buffered I/O helpers.

Important APIs and types: Defines `FPN_FORWARD_SLASHES`, `FPN_BACK_SLASHES`, `BUFIO_FD`, `BUFIO_INVALID_FD`, `BUFIO_BUFSIZE`, and `bufio_t`/`bufio_p`. Declares `FilepathNormalizeEx()`, `FilepathNormalize()`, `BufioOpen()`, `BufioGets()`, and `BufioClose()`.

Control flow and state: Header-only declarations. The `bufio_t` structure exposes file descriptor, buffer offsets, EOF flag, and fixed-size internal buffer to callers that include the header.

Dependencies and integration: Used by path initialization, config parsing, and other utilities that need old-style fd I/O. The design avoids stdio for environments where `FILE` descriptor width or CRT behavior is problematic.

Risks and test signals: Because `bufio_t` is public, callers can mutate internal fields and break invariants. The fixed 4096-byte buffer and integer offsets are simple but not appropriate for binary streaming or explicit long-line handling. Compile-time coverage and `dirpath_test` are the available local signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/fileutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/flipbase64.c -->
# sources/distributed-fs/openafs/src/util/flipbase64.c

Purpose: Implements "flipped" base64 conversion for 64-bit integers, encoding from low-order bits to high-order bits instead of the usual high-to-low direction.

Important APIs: `int64_to_flipbase64(lb64_string_t s, afs_uint64 a)` writes an encoded string into caller storage. `flipbase64_to_int64(char *s)` decodes a string back into an integer. The translation tables differ on Darwin versus other platforms.

Control flow and state: Encoding repeatedly masks the low 6 bits, emits one table character, shifts right by 6, and terminates with NUL. Zero maps to the first alphabet character. Decoding iterates over the input, looks up each character in `c_reverse`, ignores illegal values (`>= 64`), shifts by cumulative 6-bit offsets, and ORs into the result.

Dependencies and integration: Includes `afsutil.h` for typedefs like `lb64_string_t` and AFS integer types. The `util/test/fb64.c` command-line utility exercises conversion, round-trip checks, and range verification.

Risks and test signals: Invalid characters are silently skipped, which can hide corrupted input. The return type is signed `afs_int64` even though encoding takes `afs_uint64`, so values with the high bit set may need careful interpretation. The `fb64` test is the direct test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/flipbase64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/fstab.c -->
# sources/distributed-fs/openafs/src/util/fstab.c

Purpose: Provides Darwin-specific compatibility implementations for fstab-style iteration over mounted filesystems using `getfsstat()`.

Important APIs: Under `AFS_DARWIN_ENV`, defines `mntinfo(struct statfs **mntbuffer)`, `getfsent()`, `setfsent()`, and `endfsent()`. These mimic BSD fstab iteration while exposing current mount information.

Control flow and state: `setfsent()` frees any previous static mount buffer, calls `mntinfo()` to allocate and populate a `statfs` array, and initializes static cursor state. `getfsent()` builds a static `struct fstab` view over the current `statfs` entry, sets read-only/read-write type from flags, advances the cursor, and decrements count. `endfsent()` releases the buffer and resets static state.

Dependencies and integration: Darwin-only code includes `<sys/mount.h>` and `<fstab.h>`. This supports code that expects fstab APIs on platforms where the mounted filesystem list is the relevant source.

Risks and test signals: Static global cursor state is not thread-safe. `mntinfo()` stores allocation in a static `origbuf` but `setfsent()` manages `mntbuf`, so ownership is implicit. Error paths call `err(1, ...)`, which exits the process. Test signals are platform build and filesystem enumeration behavior on Darwin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/fstab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/hostparse.c -->
# sources/distributed-fs/openafs/src/util/hostparse.c

Purpose: Provides host/address parsing utilities, reverse lookup formatting, dotted-quad extraction, and temporary-directory discovery.

Important APIs: `hostutil_GetHostByName()` accepts names and numeric dotted IPv4 strings. `hostutil_GetNameByINet()` returns a static hostname or dotted address. `extractAddr()` parses a dotted IPv4 address from a line and returns network byte order or invalid sentinel values. `afs_inet_ntoa_r()` formats an address into caller storage. `gettmpdir()` returns a persistent temp directory string.

Control flow and state: Numeric hostname parsing builds a fake static `hostent` backed by static address storage. Non-numeric lookup calls `gethostbyname()` after Winsock init on Windows. `extractAddr()` tokenizes each byte field manually, validates digit-only fields, and uses `strtol()` before composing with `htonl()`. Windows `gettmpdir()` lazily allocates a directory string and publishes it with `InterlockedCompareExchangePointer`.

Dependencies and integration: Depends on roken, AFS integer types, Winsock init on Windows, and `FilepathNormalize()` for temp paths. Used by network config parsing and address display.

Risks and test signals: Several APIs return static storage and are not reentrant. `hostutil_GetHostByName()` does not check numeric octets are <= 255 before storing in `char`. `extractAddr()` similarly composes parsed byte values without upper-bound checks. Tests are indirect through NetInfo/NetRestrict parsing and host display behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/hostparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/hputil.c -->
# sources/distributed-fs/openafs/src/util/hputil.c

Purpose: Supplies missing compatibility routines for HP-UX builds.

Important APIs: Under `AFS_HPUX_ENV`, defines `utimes()` for pre-HPUX 10.20 using `utime()`, `setlinebuf()` using `setbuf(file, NULL)`, and `psignal()` that prints a simple signal message to stderr.

Control flow and state: No persistent state. Each helper is a thin wrapper around the available libc API.

Dependencies and integration: Includes `<utime.h>` when compiling for HP-UX and OpenAFS platform config headers. These functions allow common code to compile without platform-specific call-site branches.

Risks and test signals: The `utimes()` shim loses microsecond precision because `utime()` only preserves seconds. `psignal()` does not translate signal names. Build coverage on HP-UX is the main signal; there are no local tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/hputil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/krb5_nt.c -->
# sources/distributed-fs/openafs/src/util/krb5_nt.c

Purpose: Windows Kerberos helper for initializing delayed Kerberos support and fetching Kerberos error messages.

Important APIs and state: `initialize_krb5()` attempts `DelayLoadHeimdal()` and sets static `krb5_initialized` on success. `fetch_krb5_error_message(afs_uint32 code)` returns a pointer to a static buffer containing the Kerberos error text when initialization and context creation succeed.

Control flow: Initialization prints to stderr if neither Kerberos for Windows nor Heimdal is available. Error-message lookup creates a `krb5_context`, calls `krb5_get_error_message()`, copies into `errorText[1024]`, frees the Kerberos message and context, and returns the static buffer pointer. If not initialized or context creation fails, returns NULL.

Dependencies and integration: Windows-only code includes `windows.h`, `krb5_nt.h`, MIT/Heimdal Kerberos headers, and com_err. Used by Windows command and auth code to present better Kerberos diagnostics.

Risks and test signals: The static error buffer is not thread-safe and can be overwritten by concurrent calls. `strncpy()` truncates long messages. Initialization state is process-global and not synchronized. Test signals are Windows Kerberos availability and command error-display behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/krb5_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/krb5_nt.h -->
# sources/distributed-fs/openafs/src/util/krb5_nt.h

Purpose: Declares Windows-only Kerberos helper functions.

Important APIs: Under `AFS_NT40_ENV`, declares `initialize_krb5(void)` and `fetch_krb5_error_message(afs_uint32)`.

Control flow and state: Header-only declarations; all state lives in `krb5_nt.c`.

Dependencies and integration: Assumes `afs_uint32` is already defined by included OpenAFS platform headers. Included by Windows code that needs optional Kerberos initialization or error translation.

Risks and test signals: The header has no include guard, so repeated inclusion relies on declarations being identical. It is effectively inert on non-Windows platforms. Compile coverage in Windows builds is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/krb5_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/kreltime.c -->
# sources/distributed-fs/openafs/src/util/kreltime.c

Purpose: Implements relative date parsing, encoding, display, and addition for AFS time utilities.

Important APIs: `ktimeRelDate_ToInt32()` encodes year/month/day relative fields. `Int32To_ktimeRelDate()` decodes them. `ktimeDate_FromInt32()` converts absolute seconds to `struct ktime_date`. `ParseRelDate()` parses `<n>y<n>m<n>d` style strings. `RelDatetoString()` formats a relative date. `Add_RelDate_to_Time()` adds a relative date to an absolute time.

Control flow and state: Parsing walks fields in the fixed order year, month, day, accepts up to four digits per component, and enforces month/day maxima. Addition first converts the base time to a local calendar date, adds years and months at calendar granularity, converts back through `ktime_InterpretDate()`, then adds days/hours/min/sec in seconds.

Dependencies and integration: Includes `ktime.h` and `afsutil.h`; relies on `ktime_InterpretDate()` from `ktime.c`. Used by expiration/relative-date command parsing.

Risks and test signals: `RelDatetoString()` returns static storage and is not thread-safe. Month overflow handling treats month `12` specially via modulo and may produce subtle calendar behavior. Day additions use 24-hour seconds, so DST transitions can differ from calendar-day semantics. Test signals are date parsing and expiration behavior in commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/kreltime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/ktime.c -->
# sources/distributed-fs/openafs/src/util/ktime.c

Purpose: Implements absolute and periodic time parsing, display, and conversion routines for OpenAFS command and scheduling code.

Important APIs: `ktime_SetTestTime()` sets a test clock override. `ktime_DateOf()` formats an `afs_int32` epoch value. `ktime_Str2int32()` parses `hh[:mm[:ss]]`. `ktime_ParsePeriodic()` parses `now`, `never`, `at`, `every`, weekdays, times, and am/pm. `ktime_DisplayString()` formats periodic times. `ktime_next()` computes the next matching event after an offset from now. `ktime_DateToInt32()`, `ktime_GetDateUsage()`, and `ktime_InterpretDate()` handle absolute dates.

Control flow and state: A static token list parser splits periodic strings. `ktime_ParsePeriodic()` applies tokens in sequence, setting mask bits and adjusting am/pm. `ktime_next()` iterates local days by 23 hours to avoid skipping spring DST days, patches desired time fields into a `ktime_date`, then converts to epoch. `ktime_InterpretDate()` binary-searches signed 31-bit time space using `localtime()` and `KDateCmp()`.

Dependencies and integration: Uses `ktime.h`, `afsutil.h`, roken, ctype, localtime/ctime. Relative time code in `kreltime.c` depends on its date interpretation.

Risks and test signals: `ktime_ParsePeriodic()` frees only from the current token pointer at exit, so on successful full iteration it can leak the earlier token list. `LocalParseLine()` can return after allocating partial tokens without freeing on token-too-long. Static buffers in `ktime_DateOf()` are not reentrant. `ktime_SetTestTime()` is process-global. Date tests should cover DST, `never`/`now`, ISO and legacy mm/dd/yy formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/ktime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/ktime.h -->
# sources/distributed-fs/openafs/src/util/ktime.h

Purpose: Defines the data structures and mask constants shared by absolute, relative, and periodic time utilities.

Important types and constants: `struct ktime_date` holds mask, year, month, day, hour, min, and sec. `struct ktime` holds periodic mask, time-of-day, and weekday. Defines `KTIMEDATE_*` field and special flags, `KTIMEDATE_NEVERDATE`, `KTIME_*` field/special flags, `KTIME_NEVERTIME`, and `KTIME_NOWTIME`.

Control flow and state: Header-only type contract; runtime logic is in `ktime.c` and `kreltime.c`.

Dependencies and integration: Requires AFS integer typedefs to be available. Included by date parsers, relative expiration logic, and command modules that need stable time encoding.

Risks and test signals: Comments note that `KTIMEDATE_NEVERDATE` differs from the value used by periodic parsing, so callers must not mix absolute and periodic sentinel values blindly. Field ranges are documented loosely but enforced in implementation. Tests should verify mask interpretation and sentinel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/ktime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/pthread_glock.c -->
# sources/distributed-fs/openafs/src/util/pthread_glock.c

Purpose: Implements a process-global recursive mutex used to port older LWP-style code to pthreads.

Important APIs and state: Defines global `pthread_recursive_mutex_t grmutex` under pthread builds. Implements `pthread_recursive_mutex_lock()` and `pthread_recursive_mutex_unlock()`. Static `pthread_once_t glock_init_once` initializes `grmutex` lazily.

Control flow: Locking initializes the global lock on first use. If the mutex is already locked by the current thread, it increments `times_inside` and returns. Otherwise it blocks on the underlying pthread mutex and records owner/locked/count state. Unlocking decrements recursion count for the owning thread and releases the underlying mutex when the count reaches zero.

Dependencies and integration: Includes `afs/pthread_glock.h`, pthreads, roken, and OpenAFS platform config. Consumers use `LOCK_GLOBAL_MUTEX` and `UNLOCK_GLOBAL_MUTEX` macros.

Risks and test signals: The implementation is a custom recursive mutex rather than using pthread recursive attributes; owner/locked/count fields are volatile but not independently synchronized outside the underlying mutex, making correctness dependent on simple usage patterns. Unlock by a non-owner returns `-1`. Tests are indirect via pthread builds of converted code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/pthread_glock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/pthread_glock.h -->
# sources/distributed-fs/openafs/src/util/pthread_glock.h

Purpose: Declares the global recursive lock abstraction and no-op fallbacks for non-pthread or kernel builds.

Important APIs and types: Defines `pthread_recursive_mutex_t` with underlying `pthread_mutex_t`, owner, locked flag, and recursion count. Declares/imports `grmutex`, `pthread_recursive_mutex_lock()`, and `pthread_recursive_mutex_unlock()`. Defines `LOCK_GLOBAL_MUTEX` and `UNLOCK_GLOBAL_MUTEX` using `opr_Verify()`.

Control flow and state: Header-only macro layer. Under non-pthread or kernel builds the lock/unlock macros expand to nothing.

Dependencies and integration: Includes pthread and `afs/opr.h` for user-space pthread builds. Windows DLL import/export is controlled by `AFS_GRMUTEX_DECLSPEC`.

Risks and test signals: Macro no-op behavior means callers must not assume locking in non-pthread builds. The exported symbol contract differs on Windows due to declspec. Compile coverage and converted old-code behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/pthread_glock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/pthread_nosigs.h -->
# sources/distributed-fs/openafs/src/util/pthread_nosigs.h

Purpose: Provides macros to temporarily block most signals around `pthread_create()` so child threads do not receive process signals intended for the main thread.

Important macros: `AFS_SIGSET_DECL` declares saved and temporary signal sets, or a dummy integer on Windows. `AFS_SIGSET_CLEAR()` fills a signal set, removes fatal/debug signals such as `SIGSEGV`, `SIGBUS`, `SIGILL`, `SIGTRAP`, `SIGABRT`, and `SIGFPE` when present, and blocks it. `AFS_SIGSET_RESTORE()` restores the old mask.

Control flow and state: Header-only macro flow; callers wrap thread creation with clear/restore. On AIX it uses `sigthreadmask`; elsewhere pthread builds use `pthread_sigmask`. Windows macros only adjust a dummy variable.

Dependencies and integration: Requires signal and pthread types from surrounding includes plus `opr_Assert()`. Used by server threading setup and pthread worker creation.

Risks and test signals: Macro use requires correct lexical scope because declarations and temporary variables are emitted at call sites. Fatal signals are intentionally left unblocked for diagnostics. Test signals are signal handling behavior in pthreaded servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/pthread_nosigs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/readdir_nt.c -->
# sources/distributed-fs/openafs/src/util/readdir_nt.c

Purpose: Implements minimal POSIX-like `opendir()`, `readdir()`, and `closedir()` for Windows.

Important APIs: `opendir(const char *path)` opens a `FindFirstFile(path\\*)` handle. `readdir(DIR *dir)` returns a pointer to a reusable `struct dirent` stored inside the `DIR`. `closedir(DIR *dir)` closes the Windows handle and frees the `DIR`.

Control flow and state: `opendir()` handles some Windows errors specially, including checking whether an empty root-like directory exists when `FindFirstFile` reports missing file/path. `readdir()` skips `.` and `..`, advances via `FindNextFile()`, maps errors through `nterr_nt2unix()`, and returns NULL at end. The current find data and dirent live in the `DIR` object.

Dependencies and integration: Includes roken, Windows APIs, `winbase.h`, and `afs/errmap_nt.h`. This supports code written against POSIX directory iteration.

Risks and test signals: `opendir()` uses `strcpy`/`strcat` into `MAX_PATH` storage without length checks. `readdir()` uses assignment in the `while (rc = FindNextFile(...))` condition intentionally but is easy to misread. Directory entries are invalidated by the next `readdir()` call. Tests are indirect through Windows directory traversal consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/readdir_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/regex.c -->
# sources/distributed-fs/openafs/src/util/regex.c

Purpose: Provides a historical V6 ed-style regular expression compiler and executor for platforms or code paths that use `re_comp()` / `re_exec()`.

Important APIs and state: `re_comp(const char *sp)` compiles into static `expbuf[512]`; `re_exec(const char *p1)` matches the last compiled expression. Static state includes capture start/end arrays, compiled buffer, and anchor flag.

Control flow: Compilation tokenizes special constructs for dot, character classes, anchors, grouping, backreferences, and `*`, emitting bytecode-like opcodes. Execution clears capture arrays, optionally enforces leading anchor, applies a fast first-character scan for literal-leading regexes, and recursively advances through the compiled program with greedy star handling and backreference comparison.

Dependencies and integration: Only depends on OpenAFS platform config. It supplies old libc-compatible entry points.

Risks and test signals: All regex state is static and non-thread-safe. Pattern size and capture count are fixed (`ESIZE`, `NBRA`). The syntax is not POSIX extended regex, so users must expect old ed semantics. Malformed internal state can return `-1` from matching. There are no local tests in this subset; consumers should test representative legacy patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/regex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/secutil_nt.c -->
# sources/distributed-fs/openafs/src/util/secutil_nt.c

Purpose: Provides Windows security utilities, currently focused on adding an ACE to an object's DACL for well-known trustees.

Important APIs and helpers: Public `ObjectDaclEntryAdd()` adds access for `WorldGroup` or `LocalAdministratorsGroup`. Private `WorldGroupSidAllocate()`, `LocalAdminsGroupSidAllocate()`, and `BuildExplicitAccessWithSid()` build SID and `EXPLICIT_ACCESS` structures.

Control flow: The public function allocates a SID for the requested trustee, builds an access entry, retrieves the current DACL with `GetSecurityInfo()`, merges using `SetEntriesInAcl()`, and writes the new DACL back. It has a special path for `SE_KERNEL_OBJECT` because historical Windows service packs mishandled named pipes with `SetSecurityInfo()`, so it updates the security descriptor and calls `SetKernelObjectSecurity()`.

Dependencies and integration: Includes Windows `aclapi.h`, `windows.h`, and `secutil_nt.h`. Used by Windows server/client code that needs predictable ACL changes on objects such as files, services, or kernel objects.

Risks and test signals: Caller must pass a handle with `READ_CONTROL`/`WRITE_DAC` rights. Only two trustee ids are supported; other values return `ERROR_INVALID_PARAMETER`. Memory ownership uses `LocalFree()` for ACL/security descriptors and `FreeSid()` for SIDs. Tests are Windows ACL behavior and access checks after object creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/secutil_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/secutil_nt.h -->
# sources/distributed-fs/openafs/src/util/secutil_nt.h

Purpose: Public header for Windows security helper APIs.

Important APIs and types: Defines `WELLKNOWN_TRUSTEE_ID` with `WorldGroup` and `LocalAdministratorsGroup`. Declares `ObjectDaclEntryAdd(HANDLE, SE_OBJECT_TYPE, WELLKNOWN_TRUSTEE_ID, DWORD, ACCESS_MODE, DWORD)`.

Control flow and state: Header-only declarations; all state is per-call in `secutil_nt.c`.

Dependencies and integration: Includes `windows.h` and `aclapi.h`, so it is Windows-specific. Consumers use it when they need to add standard ACL entries without duplicating SID construction.

Risks and test signals: The enum is intentionally small; adding trustees requires implementation support. Including this header in non-Windows code would fail. Tests should verify that resulting DACLs grant expected access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/secutil_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/serverLog.c -->
# sources/distributed-fs/openafs/src/util/serverLog.c

Purpose: Implements server logging, log-file rotation/reopen, signal-driven debug-level control, optional thread id logging, stdout/stderr redirection, and syslog support.

Important APIs and state: Public APIs include `OpenLog()`, `CloseLog()`, `ReOpenLog()`, `FSLog()`, `vFSLog()`, `WriteLogBuffer()`, `LogCommandLine()`, `GetLogLevel()`, `GetLogDest()`, `GetLogFilename()`, `SetLogThreadNumProgram()`, `SetupLogSignals()`, and pthread `SetupLogSoftSignals()`. Static state includes `serverLogFD`, `serverLogOpts`, `ourName`, `logTime`, `threadIdLogs`, `resetSignals`, and a pthread mutex initialized via `pthread_once`.

Control flow: `OpenLog()` copies options, sets `LogLevel`, chooses file or syslog destination, rotates on open when requested, opens append/truncate mode, redirects stdout/stderr, and stores the filename for reopen. `vFSLog()` builds a timestamp/thread prefix, formats into a fixed buffer, and writes under lock to fd or syslog. Signal handlers raise/reset debug level and reopen/rotate logs. `RenameLogFile()` supports `.old` and timestamp styles.

Dependencies and integration: Uses roken, `afsutil.h`, `fileutil.h`, LWP/procmgmt, pthread/softsig where enabled, and optional syslog. Server processes call this early during startup.

Risks and test signals: `vFSLog()` truncates messages to 1024 bytes. Traditional `.old` rotation can overwrite older logs. FIFO handling avoids rotation and opens nonblocking. Signal behavior differs between pthread soft signals and legacy LWP. Tests should cover file logging, syslog builds, rotation styles, reopen after external rotation, and debug signal changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/serverLog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/sys.c -->
# sources/distributed-fs/openafs/src/util/sys.c

Purpose: Tiny utility program that prints the configured OpenAFS `SYS_NAME`.

Important API/function: `main()` prints `SYS_NAME` followed by a newline and exits successfully.

Control flow and state: No persistent state; includes generated `AFS_component_version_number.c` for version metadata side effects used by the build.

Dependencies and integration: Includes OpenAFS config headers and stdio. Built as a utility to expose platform/system naming.

Risks and test signals: Behavior depends entirely on the configured `SYS_NAME` macro. Tests are simple execution output checks after configure/build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/tabular_output.c -->
# sources/distributed-fs/openafs/src/util/tabular_output.c

Purpose: Implements a small table builder/printer supporting ASCII, CSV, and HTML output with optional row sorting.

Important APIs and types: Public functions include `util_newTable()`, `util_newCellContents()`, `util_setTableHeader()`, `util_setTableFooter()`, `util_setTableBodyRow()`, `util_addTableBodyRow()`, `util_printTable*()`, and `util_freeTable()`. Private `struct util_Table` stores output type, dimensions, column metadata, rows, footer/header, and function pointers. `struct util_TableRow` owns per-cell strings.

Control flow and state: `util_newTable()` validates type/sort key, initializes function pointers, creates a header row, and stores caller-provided column metadata. Adding a body row grows the row array in chunks, creates a temporary row for sort placement, shifts existing content if sorted, copies content into the selected row, and updates `RowLength`. Print functions dispatch by type. Sorting uses binary search and either string compare or `util_GetInt64()`.

Dependencies and integration: Includes `afs/tabular_output.h`, `afs/afsutil.h`, roken, and `opr_min`. Consumers are command-line tools that need formatted output.

Risks and test signals: `util_setTableFooter()` appears inverted: it allocates a footer only when `Footer != NULL`, then dereferences `Table->Footer`, so initial footer setting can crash. `do_setTableRow()` uses `strcpy()` into fixed 30-byte cells, while `util_addTableBodyRow()` later uses `strncpy()`, so long content can overflow in setters/header. `util_freeTable()` calls `freeTableRow()` on possibly NULL footer. CSV/HTML output does not escape cell content. Tests should cover footer use, long cells, sorting, and all output types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/tabular_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/tabular_output.h -->
# sources/distributed-fs/openafs/src/util/tabular_output.h

Purpose: Defines constants for the table output utility.

Important constants: Cell and allocation bounds are `UTIL_T_MAX_CELLS`, `UTIL_T_MAX_CELLCONTENT_LEN`, and `UTIL_T_NUMALLOC_ROW`. Content types are string and numeric. Output types are ASCII, CSV, and HTML. ASCII separators and command-help strings are also defined.

Control flow and state: Header-only constants; public function prototypes are not present in this header, so callers likely rely on prototypes from another aggregate header such as `afsutil.h`.

Dependencies and integration: Used by `tabular_output.c` and command-line tools that accept output-format or sort options.

Risks and test signals: The fixed 30-character cell size is a behavioral limit and a safety risk when implementation uses unchecked copies. `UTIL_T_TYPE_MAX` must track output-type constants. Tests are compile coverage and formatting tests through command consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/tabular_output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/Makefile.in -->
# sources/distributed-fs/openafs/src/util/test/Makefile.in

Purpose: Builds utility test programs for dirpath and base conversion helpers.

Important targets: `all` / `tests` build `dirpath_test`, `b64`, and `fb64`. Each target links its object with `../util.a`, `libopr.a`, roken, and platform libraries. `clean` removes objects and generated test binaries.

Control flow and state: Makefile template includes configured `Makefile.config` and `Makefile.lwp`, then relies on standard OpenAFS build variables such as `AFS_LDRULE`, `TOP_LIBDIR`, `LIB_roken`, and `XLIBS`.

Dependencies and integration: Lives under `src/util/test` and validates parts of the utility library. It does not build `b32` in the listed `all` target even though `b32.c` exists.

Risks and test signals: The test set is narrow and largely command-line round-trip validation. Platform guards in individual test files may cause a built test to print "not required" and exit nonzero on unsupported platforms. Running `make tests` in this directory is the direct signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/b32.c -->
# sources/distributed-fs/openafs/src/util/test/b32.c

Purpose: Command-line test utility for OpenAFS base32 integer conversion, enabled only on Windows builds.

Important functions: `main()` dispatches to `itob()`, `btoi()`, `check()`, or `verifyRange()` based on `-s`, `-i`, `-c`, or `-r`. `Usage()` prints command syntax. Conversion calls `int_to_base32()` and `base32_to_int()` from the utility library.

Control flow and state: On non-Windows builds, `main()` prints that `b32` is not required and returns 1. On Windows, single-value and multi-value modes print conversion results. Range verification loops from low to high by increment, round-trips each value, prints progress every million iterations, and exits on mismatch.

Dependencies and integration: Includes `afs/afsutil.h`, roken, and stdio. Complements base32 implementation not included in this subset.

Risks and test signals: Uses `atoi()` with no validation, so invalid test input can silently become zero. Range loops can overflow or never terminate if increment is zero or values wrap. It is not listed in this subset's test Makefile `all` target, so it may require explicit build wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/b32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/b64.c -->
# sources/distributed-fs/openafs/src/util/test/b64.c

Purpose: Command-line test utility for OpenAFS base64 integer conversion in SGI XFS IOPS environments.

Important functions: `main()` selects `itob()`, `btoi()`, `check()`, or `verifyRange()`. These call `int_to_base64()` and `base64_to_int()`.

Control flow and state: On platforms without `AFS_SGI_XFS_IOPS_ENV`, the program reports that `b64` is not required and returns 1. In active builds it supports one or many values and a range verifier that round-trips values, prints progress every million iterations, and exits with error on mismatch.

Dependencies and integration: Includes OpenAFS utility headers and stdio. Built by `util/test/Makefile.in`.

Risks and test signals: Input parsing uses `atoi()` without error detection. Range verification can hang with zero increment or wraparound. The main test signal is successful round-trip verification across representative ranges on the platform where this encoding matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/b64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/dirpath_test.c -->
# sources/distributed-fs/openafs/src/util/test/dirpath_test.c

Purpose: Manual/smoke test for dirpath initialization, exported path macros, local path construction, and temp-directory lookup.

Important behavior: `main()` calls `initAFSDirPath()`, reports missing client/server path status flags, prints many `AFSDIR_*` macro results, tests `ConstructLocalPath()`, `ConstructLocalBinPath()`, `ConstructLocalLogPath()`, and prints `gettmpdir()`.

Control flow and state: The test allocates path buffers via construct functions, prints them, and frees them. It includes a Windows-only fully qualified drive path case. It does not assert expected values; it is observational.

Dependencies and integration: Includes `afs/afsutil.h`, roken, and stdio. Built by `util/test/Makefile.in` against `util.a` and `libopr.a`.

Risks and test signals: Because it prints rather than verifies, automated use needs output comparison or simple success checks. It exercises initialization side effects, canonical/local translation, and allocation ownership, making it useful after dirpath macro changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/dirpath_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/fb64.c -->
# sources/distributed-fs/openafs/src/util/test/fb64.c

Purpose: Command-line test utility for flipped base64 64-bit conversion.

Important functions: `main()` dispatches on `-s`, `-i`, `-c`, and `-r`. `itob()` parses 64-bit values and calls `int64_to_flipbase64()`. `btoi()` calls `flipbase64_to_int64()`. `check()` prints round trips, and `verifyRange()` validates a low/high/increment range.

Control flow and state: Unlike `b32`/`b64`, this utility is not platform-disabled. Range verification increments from low to high, prints progress every million values, and exits on the first mismatch.

Dependencies and integration: Includes `afs/afsutil.h`, roken, stdio, and conversion APIs from `flipbase64.c`. Built by `util/test/Makefile.in`.

Risks and test signals: Uses `%llu`/`%lld` scanning into `afs_int64` variables, which can be format-sensitive across compilers. No validation for zero increment or malformed input. Successful `-c` and `-r` runs are the direct test signals for `flipbase64.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/test/fb64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/uuid.c -->
# sources/distributed-fs/openafs/src/util/uuid.c

Purpose: Implements OpenAFS UUID generation, comparison, byte-order conversion, string conversion, hashing, and platform-specific node/time acquisition.

Important APIs and state: Public APIs include `afs_uuid_equal()`, `afs_uuid_is_nil()`, `afs_htonuuid()`, `afs_ntohuuid()`, `afsUUID_from_string()`, `afsUUID_to_string()`, `afs_uuid_create()`, and `afs_uuid_hash()`. Global `afs_uuid_g_nil_uuid` represents nil UUID. Static state includes last/current UUID time, adjustment counter, clock sequence, pseudo-random state, and initialization flag.

Control flow: Non-Windows UUID creation lazily seeds pseudo-random state from time and pid, gets a node address from hostname/IP or kernel interface, reads OS time, handles clock rollback by incrementing the clock sequence, increments `uuid_time_adjust` for same-tick UUIDs, then fills a version-1 UUID layout. Windows delegates to `UuidCreate()`. String parsing and formatting use canonical 8-4-4-2-2-12 hex fields. Hashing unrolls a checksum-style loop over 16 bytes.

Dependencies and integration: Uses roken and networking headers in userland; kernel/UKERNEL paths use OpenAFS kernel includes and rx helpers. UUIDs identify servers, volumes, or other distributed objects.

Risks and test signals: Static creation state is not protected by locks, so concurrent UUID creation can race. Node id is derived from IPv4 address plus fixed bytes, not a hardware MAC in userland. `afs_uuid_hash()` depends on in-memory byte order. Tests should cover string round trips, uniqueness under rapid calls, nil handling, byte-order conversions, and hash stability where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/uuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/vice.h -->
# sources/distributed-fs/openafs/src/util/vice.h

Purpose: Defines pioctl data structures and ioctl-construction macros for AFS user/kernel communication.

Important types and macros: Defines kernel `struct ViceIoctl32` with fixed-width pointer fields and user-space `struct ViceIoctl` on non-Windows. Defines `_VICEIOCTL(id)`, `_VICEIOCTL2(dev, id)`, `_CVICEIOCTL(id)`, and `_OVICEIOCTL(id)` using `_IOW()` with the appropriate structure type.

Control flow and state: Header-only ABI definitions. It encodes structure size into ioctl numbers so kernel code can identify argument layout.

Dependencies and integration: Includes system ioctl headers on non-Windows depending on platform/kernel configuration. Used by cache-manager pioctl interfaces and command tools.

Risks and test signals: ABI sensitivity is high: pointer-size differences and Alpha/Digital Unix exceptions are explicitly handled. Windows uses a different structure in `sys/pioctl_nt.h`. Tests are pioctl command behavior across 32/64-bit user/kernel combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/vice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/volparse.c -->
# sources/distributed-fs/openafs/src/util/volparse.c

Purpose: Provides partition-name parsing/formatting and robust integer parsing helpers for OpenAFS command-line and volume utilities.

Important APIs: `volutil_GetPartitionID()` maps numeric ids, `a`, `aa`, `vicepa`, and `/vicepa` forms to partition indexes. `volutil_PartitionName2_r()`, `volutil_PartitionName_r()`, and non-reentrant `volutil_PartitionName()` convert ids back to `/vicep*`. Numeric parsers include `util_GetInt32()`, `util_GetUInt32()`, `util_GetHumanInt32()`, `util_GetInt64()`, and `util_GetUInt64()`.

Control flow and state: Partition parsing accepts 0..254 and one/two-letter suffixes. Number parsing skips leading spaces/tabs, supports decimal, octal, and hex prefixes, checks digits for the inferred base, and uses rearranged overflow tests before multiply/add. Human int parsing uses `strtol()` plus `K`, `M`, `G`, or `T` binary multipliers.

Dependencies and integration: Includes `afsutil.h`; used by bos/vol/vos-style command parsing and table sorting (`tabular_output.c` uses `util_GetInt64()`).

Risks and test signals: Unsigned parsers do not accept a leading plus or minus. Empty numeric strings can parse as zero because no digit-count check occurs after prefix handling. `volutil_PartitionName()` uses static storage. Tests should cover partition boundaries (`z`, `aa`, max 254), invalid suffixes, numeric overflows, bases, and human suffixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/volparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/winsock_nt.c -->
# sources/distributed-fs/openafs/src/util/winsock_nt.c

Purpose: Provides Windows Winsock initialization/cleanup wrappers and an exported `afs_gettimeofday()` shim.

Important APIs: Under `AFS_NT40_ENV`, defines `afs_winsockInit()`, `afs_winsockCleanup()`, and `afs_gettimeofday(struct timeval *, struct timezone *)`.

Control flow and state: `afs_winsockInit()` calls `WSAStartup()` requesting version 2 and returns `-1` if startup fails or the negotiated version is not 2. Cleanup calls `WSACleanup()`. `afs_gettimeofday()` delegates to roken `rk_gettimeofday()`.

Dependencies and integration: Includes Windows socket types through platform headers, `<sys/timeb.h>`, and `afs/afsutil.h`. Used by Windows networking utilities such as host parsing and UUID generation.

Risks and test signals: Repeated `WSAStartup()` calls require balanced cleanup in Windows semantics, but this wrapper does not refcount. It checks `data.wVersion != 2` rather than using `LOBYTE/HIBYTE`, which assumes version layout expectations. Tests are Windows network startup and host lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/winsock_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue.c -->
# sources/distributed-fs/openafs/src/util/work_queue.c

Purpose: Implements a pthread-based dependency-aware work queue with ready, blocked, and done lists; callback execution; flow-control thresholds; shutdown; node waits; and reference-managed work nodes.

Important APIs: Queue lifecycle: `afs_wq_opts_init()`, `afs_wq_opts_calc_thresh()`, `afs_wq_create()`, `afs_wq_destroy()`, `afs_wq_shutdown()`. Node lifecycle/config: `afs_wq_node_alloc()`, `afs_wq_node_get()`, `afs_wq_node_put()`, `afs_wq_node_set_callback()`, `afs_wq_node_set_detached()`, dependency add/delete, block/unblock. Scheduling/execution: `afs_wq_add_opts_init()`, `afs_wq_add()`, `afs_wq_do()`, `afs_wq_do_nowait()`, `afs_wq_wait_all()`, and `afs_wq_node_wait()`.

Control flow and state: `afs_work_queue` owns three locked lists plus queue counters and condition variables. Nodes own a lock, state CV, queue/list id, callback, callback rock/destructor, refcount, block/error counters, dependency children, detach flag, and retcode. Adding a node increments pending count unless throttled by high/low thresholds, chooses ready/blocked/done based on block/error counts, and enqueues. Workers dequeue ready nodes, run callbacks unlocked, choose next state from callback return (`0`, `AFS_WQ_ERROR_RESCHEDULE`, or error), decrement pending on terminal states, propagate completion/error through dependency children, and enqueue to the next list or free detached nodes.

Concurrency dependencies: Uses `opr_mutex`, `opr_cv`, rx queues, and a custom two-node multilock with trylock and exponential backoff to avoid undefined lock hierarchy deadlocks during dependency operations. Shutdown drains lists, marks nodes error, wakes waiters, and waits for running callbacks in `afs_wq_wait_all()`.

Risks and test signals: The checked-out file contains an apparent compile-breaking typo at line 1900, `if (retcowait{`, likely intended to check `retcode`. `afs_wq_del()` is unimplemented (`ENOTSUP`). Detached nodes are freed automatically; non-detached nodes require wait/put discipline. Dependency mutation is allowed only in init or running states. Tests should cover dependency propagation, reschedule, external block/unblock, detached cleanup, shutdown during wait/add/do, high/low threshold drain, and node wait removal from done list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue.h -->
# sources/distributed-fs/openafs/src/util/work_queue.h

Purpose: Public API header for the OpenAFS work queue package.

Important APIs and constants: Defines package error constants `AFS_WQ_ERROR`, `AFS_WQ_ERROR_RECOVERABLE`, and `AFS_WQ_ERROR_RESCHEDULE`. Declares all public queue, node, dependency, scheduling, execution, and wait functions implemented in `work_queue.c`.

Control flow and state: Header-only declaration layer. The public types are incomplete or option/callback types from `work_queue_types.h`; implementation internals stay hidden unless `work_queue_impl_types.h` is included by the implementation.

Dependencies and integration: Includes `work_queue_types.h`. Intended for volume/package code or other subsystems needing asynchronous dependency-aware work scheduling.

Risks and test signals: Error constants are marked as a future error-table TODO, so callers depend on raw negative values. API docs imply `afs_wq_del()` exists, but implementation returns `ENOTSUP`. Tests should compile against this header and exercise public API semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue_impl.h -->
# sources/distributed-fs/openafs/src/util/work_queue_impl.h

Purpose: Implementation-private umbrella header for the work queue package.

Important content: Includes the public `work_queue.h` and private `work_queue_impl_types.h`. It intentionally exposes no additional functions.

Control flow and state: Header-only include aggregator. Access to private types is guarded by `work_queue_impl_types.h`, which requires `__AFS_WORK_QUEUE_IMPL`.

Dependencies and integration: Included by `work_queue.c` after defining `__AFS_WORK_QUEUE_IMPL`. Not intended for external consumers.

Risks and test signals: Misuse outside implementation should be caught by the private types header. Compile-time enforcement is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue_impl_types.h -->
# sources/distributed-fs/openafs/src/util/work_queue_impl_types.h

Purpose: Defines private structures and enums backing the work queue implementation.

Important types: `afs_wq_work_state_t` covers init, scheduled, running, done, error, blocked, busy, and terminal states. `afs_work_queue_dep_node` links parent and child nodes. `afs_wq_node_list_id_t` identifies none, ready, blocked, and done lists. `afs_work_queue_node` stores queue linkage, dependencies, callback, rock/destructor, state, refcount, block/error counts, detach flag, retcode, mutex, and state condition. `afs_work_queue_node_list` wraps an rx queue with lock/CV/shutdown. `afs_work_queue` holds the lists, queue rock, options, drain/shutdown flags, counters, and CVs.

Control flow and state: This header defines the memory layout used by all private state transitions in `work_queue.c`; no executable control flow.

Dependencies and integration: Requires `__AFS_WORK_QUEUE_IMPL`, includes `work_queue_types.h`, and uses `<rx/rx_queue.h>`, pthread mutexes, and condition variables.

Risks and test signals: Layout changes affect all implementation logic and any accidental private consumers. The header has a typo in a comment (`signalled when th queue`) but no functional issue. Compile-time guard prevents normal external inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue_impl_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue_types.h -->
# sources/distributed-fs/openafs/src/util/work_queue_types.h

Purpose: Defines public opaque work queue types, option structs, and callback signatures.

Important types: Forward declares `struct afs_work_queue_node` and `struct afs_work_queue`. `struct afs_work_queue_opts` configures pending low/high thresholds. `struct afs_work_queue_add_opts` configures add-time donation, blocking, and force behavior. `afs_wq_callback_func_t` is invoked as `callback(queue, node, queue_rock, node_rock, worker_rock)`. `afs_wq_callback_dtor_t` destroys node rock.

Control flow and state: Header-only type contract. The semantics of thresholds and add options are enforced in `work_queue.c`.

Dependencies and integration: Included by `work_queue.h` and private implementation headers. Public consumers need only this header and `work_queue.h` to create queues and nodes without seeing internals.

Risks and test signals: The callback can receive the node and mutate dependencies while running, so caller discipline is important. `donate` transfers a node reference to the queue when set; misuse can leak or prematurely free nodes. Tests should cover add options and callback return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/work_queue_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/Makefile.in -->
# sources/distributed-fs/openafs/src/venus/Makefile.in

Purpose: Autoconf Makefile template for building and installing OpenAFS venus/client command programs.

Important targets and variables: Defines `PROGRAMS` including `afsio`, `cacheout`, `cmdebug`, `fs`, `fstrace`, `gcpags`, `livesys`, `twiddle`, `up`, and `whatfid`. Library groups include `AFSIO_LIBS`, `FSLIBS`, `CMLIBS`, and default `LIBS`. Link targets use `LT_LDRULE_static` with fsint, vlserver, rxkad, cmd, util, opr, roken, pthread, hcrypto, and Kerberos libraries as needed.

Control flow and state: The build flow includes configured `Makefile.config` and `Makefile.pthread`, builds all programs, compiles special generated `afscbint.ss.o`, installs selected binaries into bindir/sbindir/afssrvbindir, and places legacy destination-tree copies under `${DEST}`. `clean` removes build artifacts; `test` descends into a `test` subdirectory.

Dependencies and integration: Integrates venus command sources with generated component version files and many OpenAFS libraries. It is a central bridge between util library outputs and user-facing client tools like `fs`, `cmdebug`, and `fstrace`.

Risks and test signals: Some programs are built but intentionally not installed (`cacheout`, `gcpags`, `twiddle`, `whatfid`). Link library ordering is important for static builds. Install paths duplicate `fs` into both server and user bindirs. Test signal is successful `make`, `make install`/`dest`, and `make test` in the venus subtree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/Makefile.in -->
