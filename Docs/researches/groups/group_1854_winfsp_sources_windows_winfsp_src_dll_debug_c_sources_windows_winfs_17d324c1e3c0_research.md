# Group Research: group_1854_winfsp_sources_windows_winfsp_src_dll_debug_c_sources_windows_winfs_17d324c1e3c0

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/winfsp`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/debug.c -->
# File Research: sources/windows/winfsp/src/dll/debug.c

Small debug-only support file for WinFsp DLL internals.

Key responsibilities:
- Defines `DebugRandom()` only when `NDEBUG` is not set.
- Implements a thread-safe pseudo-random generator with a static `SRWLOCK`.
- Uses the UCRT-style linear congruential update `Seed = Seed * 214013 + 2531011`.
- Returns a 15-bit value from the high portion of the seed.

Dependencies:
- Includes `dll/library.h`.
- Uses Windows SRW lock primitives.

Filesystem relevance:
- Supports internal debug/test behavior through the library debug macros, not production filesystem semantics.

Notable risks:
- Deterministic fixed seed is intentional for debug repeatability, but it is not suitable for security or randomness-sensitive logic.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/debuglog.c -->
# File Research: sources/windows/winfsp/src/dll/debuglog.c

Human-readable trace logging for WinFsp request/response traffic and filesystem metadata.

Key responsibilities:
- Maintains a global debug log handle set by `FspDebugLogSetHandle`.
- Emits formatted debug text to the configured file handle or `OutputDebugStringA`.
- Provides helpers for logging security descriptors, SIDs, `FILETIME`, file info, volume info, wide-char buffers, user contexts, and reparse data.
- Logs every major `FSP_FSCTL_TRANSACT_REQ` kind in `FspDebugLogRequest`.
- Logs every major `FSP_FSCTL_TRANSACT_RSP` kind in `FspDebugLogResponse`.
- Decodes create dispositions, create/open flags, access tokens, file names, EA/security payloads, query directory markers, FSCTL reparse operations, volume labels, and stream/security operations.

Important behavior:
- Skips response logging for `STATUS_PENDING`.
- Uses `FspDiagIdent()` and the current thread ID in trace prefixes.
- Converts security descriptors to SDDL when present.
- Handles mount-point, symlink, Microsoft, and GUID reparse payload shapes.
- Uses fixed-size stack buffers with truncation-oriented formatting.

Dependencies:
- Includes `dll/library.h`, `sddl.h`, and `stdarg.h`.
- Depends on WinFsp transaction structures and Windows APIs such as `ConvertSecurityDescriptorToStringSecurityDescriptorA`, `ConvertSidToStringSidA`, `FileTimeToSystemTime`, `WriteFile`, and `OutputDebugStringA`.

Notable risks:
- Formatting is intentionally diagnostic and uses Windows `wvsprintf/wsprintf` style APIs with fixed buffers.
- Logs can expose paths, security descriptors, access tokens, and user context pointers; this should remain a debug facility.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/debuglog.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/dirbuf.c -->
# File Research: sources/windows/winfsp/src/dll/dirbuf.c

Sorted directory enumeration buffer used by user-mode filesystems to cache and replay directory entries.

Key responsibilities:
- Defines an internal `FSP_FILE_SYSTEM_DIRECTORY_BUFFER` with an SRW lock, capacity marks, and a single byte buffer.
- Stores directory records from the low end of the buffer and an index array from the high end.
- Grows allocation from a low bound of 256 bytes up to a high bound of 1 MiB using different growth factors.
- Orders `"."` and `".."` before normal names.
- Sorts entries by filename using an internal non-recursive quicksort.
- Supports binary search by marker for resume-style directory reads.
- Exposes acquire, fill, release/sort, read, delete, and peek functions.

Important behavior:
- `FspFileSystemAcquireDirectoryBufferEx` lazily creates the buffer under a static create lock and returns it already exclusively locked when reset/created.
- `FspFileSystemFillDirectoryBuffer` appends an `FSP_FSCTL_DIR_INFO` and records its offset in the index.
- `FspFileSystemReleaseDirectoryBuffer` removes invalidated index entries and sorts the remaining index.
- `FspFileSystemReadDirectoryBuffer` acquires shared access, seeks past an optional marker, copies entries to the caller buffer, then appends the terminating zero-sized entry.
- `FspFileSystemDeleteDirectoryBuffer` frees the data buffer and header.

Dependencies:
- Includes `dll/library.h`.
- Uses `FspFileSystemAddDirInfo`, `invariant_wcsncmp`, `MemAlloc`, `MemRealloc`, `MemFree`, interlocked pointer helpers, SRW locks, and WinFsp `FSP_FSCTL_DIR_INFO`.

Notable risks:
- The caller contract requires acquire/fill/release discipline; fill and peek assume the exclusive lock is already held.
- Sorting relies on an index count derived from capacity/high mark, so buffer mark integrity is critical.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/dirbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/eventlog.c -->
# File Research: sources/windows/winfsp/src/dll/eventlog.c

Windows Event Log integration for the WinFsp DLL.

Key responsibilities:
- Lazily registers an event source with `RegisterEventSourceW`.
- Provides `FspEventLog` and `FspEventLogV` formatted logging APIs.
- Maps information, warning, and error event types to WinFsp message IDs.
- Registers and unregisters the Event Log source under `HKLM\SYSTEM\CurrentControlSet\Services\EventLog\Application\<LIBRARY_NAME>`.
- Writes `EventMessageFile` and `TypesSupported` registry values.

Important behavior:
- Falls back from the library event source name to `FspDiagIdent()` if initial registration fails.
- `FspEventLogFinalize` deregisters only on explicit dynamic unload.
- Message strings include diagnostic identity and formatted message text.
- Registry registration resolves the DLL/module path with `MyEventLogRegisterPath`.

Dependencies:
- Includes `dll/library.h`, `stdarg.h`, and `eventlog/eventlog.h`.
- Uses Windows Event Log, registry, and module-path APIs.

Notable risks:
- Event source registration/unregistration requires appropriate registry privileges.
- Uses `wvsprintfW` into a 1024-wide-character buffer, matching the file’s own safety comment.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/eventlog.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/eventlog/eventlog.h -->
# File Research: sources/windows/winfsp/src/dll/eventlog/eventlog.h

Generated-style Event Log message identifier header.

Key contents:
- Documents the standard 32-bit Windows message ID layout: severity, customer bit, reserved bit, facility, and code.
- Defines three WinFsp event IDs:
  - `FSP_EVENTLOG_INFORMATION` as `0x60000001L`
  - `FSP_EVENTLOG_WARNING` as `0xA0000001L`
  - `FSP_EVENTLOG_ERROR` as `0xE0000001L`
- All messages have the text shape `%1: %2`.

Dependencies:
- Consumed by `eventlog.c` when selecting event IDs for `ReportEventW`.

Filesystem relevance:
- Provides diagnostic message constants for service/DLL event reporting; no runtime filesystem logic is implemented here.

Notable risks:
- Must remain synchronized with the corresponding message resource compiled into the DLL/sys event message file.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/eventlog/eventlog.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fs.c -->
# File Research: sources/windows/winfsp/src/dll/fs.c

Core `FSP_FILE_SYSTEM` object lifecycle, mount management, dispatcher threading, and notification wrappers.

Key responsibilities:
- Allocates a TLS key for per-dispatcher operation context.
- Preflights device and mount-point availability.
- Creates and deletes WinFsp file system objects.
- Opens the driver volume through `FspFsctlCreateVolume`.
- Installs the default operation dispatch table for all transaction kinds.
- Sets and removes mount points through `FspMountSet`/`FspMountRemove`.
- Starts, stops, and supervises dispatcher threads.
- Sends synchronous and asynchronous responses back to the driver.
- Wraps notification begin/end/send APIs.

Important behavior:
- Default dispatcher thread count is based on process affinity and clamped to 4-16, with a hard minimum of 2.
- The dispatcher creates additional dispatcher threads recursively until the requested count is reached.
- Each dispatcher owns request and response buffers and places them in TLS as `FSP_FILE_SYSTEM_OPERATION_CONTEXT`.
- Requests are received and responses are sent through `FspFsctlTransact`.
- Each valid transaction is guarded by `EnterOperation`/`LeaveOperation`, dispatched via `FileSystem->Operations[Kind]`, optionally logged, aligned, and returned.
- `STATUS_PENDING` clears the immediate response so async completion can later use `FspFileSystemSendResponse`.
- `FspFileSystemStopDispatcher` marks an internal stopping bit, stops the driver transaction path, waits for the dispatcher, and then issues the final stop.

Dependencies:
- Includes `dll/library.h`.
- Depends on `fsop.c` operation entry points, `fsctl.c` driver calls, mount helpers, memory helpers, debug logging, TLS, SRW locks, and Windows threading APIs.

Notable risks:
- Dispatcher shutdown and async response paths depend on correct stop ordering.
- Some state bits are manipulated through packed/interlocked access to adjacent structure fields, so layout compatibility matters.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fsctl.c -->
# File Research: sources/windows/winfsp/src/dll/fsctl.c

Driver and Service Control Manager interface layer for WinFsp filesystem devices.

Key responsibilities:
- Creates WinFsp volumes by constructing a `GLOBALROOT` device path with encoded volume parameters.
- Starts the WinFsp driver service before opening volumes.
- Retrieves volume names and volume lists through driver control codes.
- Sends transaction, stop, notify, mountdev, mountmgr, unload, and list IOCTL/FSCTL requests.
- Detects installed driver version and switches between older `FSP_FSCTL_TRANSACT*` and newer `FSP_IOCTL_TRANSACT*` control codes.
- Starts and stops driver services with side-by-side installation awareness.
- Enumerates WinFsp filesystem driver services.
- Registers and unregisters the filesystem driver service.
- Updates service security so Everyone can start but not stop the service.

Important behavior:
- `FspFsctlCreateVolume` encodes raw `FSP_FSCTL_VOLUME_PARAMS` bytes into Unicode private-use characters appended to the device path.
- Non-SxS mode tries the normal driver service first, then selects the best available SxS service if needed.
- SxS mode starts only the suffixed driver name.
- Container detection short-circuits service start/stop as successful.
- `FspFsctlStopService` temporarily enables/checks `SeLoadDriverPrivilege` before sending unload.
- `FspFsctlRegister` derives the `.sys` driver path from the module path and creates or updates a demand-start filesystem driver service.

Dependencies:
- Includes `dll/library.h` and `aclapi.h`.
- Uses Windows SCM APIs, registry/token/privilege APIs, service security APIs, `DeviceIoControl`, `CreateFileW`, and WinFsp SxS helpers.

Notable risks:
- Service registration, stop, unload, and security changes require administrative/privileged context.
- Device-path construction has strict `MAX_PATH` and encoded-parameter size checks.
- The service security policy is deliberately unusual: broad start permission and broad stop denial.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fsop.c -->
# File Research: sources/windows/winfsp/src/dll/fsop.c

Main filesystem operation adapter from WinFsp kernel transactions to user-supplied `FSP_FILE_SYSTEM_INTERFACE` callbacks.

Key responsibilities:
- Implements operation guard entry/leave behavior with fine or coarse SRW locking.
- Performs access checks for create, open, overwrite, target-directory open, and rename replacement cases.
- Implements Windows create dispositions: create, open, open-if, overwrite, overwrite-if, supersede, and open-target-directory.
- Creates and returns security descriptors for newly created/opened objects when requested.
- Marshals callbacks for overwrite, cleanup, close, read, write, flush, file info, set info, EA, volume info, directory query, FSCTL reparse operations, device control, security, and stream information.
- Handles named stream/reparse not-found and collision follow-up checks.
- Packs directory, stream, EA, and notify entries into WinFsp response buffers.
- Resolves reparse points and symlink chains for user-mode filesystems.
- Checks whether reparse data can be replaced safely.

Important behavior:
- File contexts can be mapped as `UserContext`, `UserContext2`, or full context depending on volume parameters.
- Fine-grained operation guarding takes exclusive locks for mutating namespace/volume operations and shared locks for selected lookup/query operations.
- Create/open paths combine WinFsp access-check helpers with filesystem callbacks and set NT create information such as `FILE_CREATED`, `FILE_OPENED`, `FILE_OVERWRITTEN`, or `FILE_SUPERSEDED`.
- `CreateEx`/`OverwriteEx` are preferred when present, with older callback forms used as fallback.
- `SetInformation` supports basic info, allocation size, EOF, disposition/disposition-ex, rename/rename-ex.
- Directory query can optimize exact-name pattern requests through `GetDirInfoByName`.
- Reparse resolution follows symlinks, handles `.` and `..`, caps attempts at 32, and returns either synthetic symlink reparse data or underlying non-symlink reparse data.
- `FspFileSystemStopServiceIfNecessary` stops the service loop on abnormal dispatcher stop.

Dependencies:
- Includes `dll/library.h`.
- Depends heavily on access/security helpers, WinFsp FSCTL transaction structures, path helpers, reparse structures, and the callback table in `FSP_FILE_SYSTEM_INTERFACE`.

Notable risks:
- This file encodes subtle Windows filesystem semantics; regressions here can affect create/open security, delete-on-close, rename replacement, reparse handling, and async I/O behavior.
- Several paths construct temporary/fake requests for access checks, so size and buffer layout correctness is important.
- Buffer packing uses 16-bit size fields and fixed maximum response sizes.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fsop.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse.c -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse.c

Core WinFsp FUSE compatibility layer setup, option parsing, mount-channel handling, notifications, TLS context, and errno mapping.

Key responsibilities:
- Defines `struct fuse_chan` carrying a Windows mount point.
- Defines supported FUSE/WinFsp core mount options and parser actions.
- Lazily allocates a TLS key for `struct fuse_context`.
- Implements `fsp_fuse_mount` and `fsp_fuse_unmount`.
- Converts SDDL, token users, user/group names, and UID maps into Windows security/SID/UID state.
- Parses core options such as debug logging, umasks, uid/gid, reparse/link behavior, volume name, UNC/volume prefix, filesystem name, file security, cache timeouts, thread count, and POSIX unlink/rename support.
- Creates and initializes a `struct fuse` with WinFsp volume parameters in `fsp_fuse_new`.
- Preflights the WinFsp disk or network device and mount point.
- Implements destroy, exit, exited, notify, context allocation, and errno-to-NTSTATUS mapping.

Important behavior:
- Mount-point parsing accepts `*`, drive letters, `\\?\X:`, `\\.\X:`, absolute Windows paths, and optionally environment-converted paths.
- Debug mode redirects WinFsp debug logging to stderr or a configured append file.
- If uid/gid is `-1`, it queries the process token; Azure AD users get a default uidmap compatible with the comment’s Cygwin expectation.
- FUSE defaults set case-sensitive search, case-preserved names, persistent ACLs, reparse-point support, device control support, and `UmFileContextIsUserContext2`.
- `fsp_fuse_notify` maps POSIX-ish notification actions to Windows `FILE_NOTIFY_CHANGE_*` filters and `FILE_ACTION_*` actions, uppercasing names for case-insensitive filesystems.
- Per-thread FUSE contexts are allocated on demand and released by `fsp_fuse_finalize_thread`.

Dependencies:
- Includes `dll/fuse/library.h` and `sddl.h`.
- Uses WinFsp core APIs (`FspFileSystemPreflight`, `FspFileSystemNotify`, `FspDebugLogSetHandle`), POSIX mapping helpers, Windows token/SID/security APIs, FUSE option parsing helpers, and `errno.i`.

Notable risks:
- Option parsing mixes FUSE conventions with Windows-specific options, so compatibility behavior depends on exact string matching.
- TLS context cleanup is incomplete for dynamic DLL unload, as noted by the file comment.
- UID/SID mapping is limited to eight explicit uidmap entries.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse.pc.in -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse.pc.in

Pkg-config template for the WinFsp FUSE-compatible API.

Key contents:
- Sets `prefix` relative to the pc file directory.
- Sets `incdir` to `${prefix}/inc/fuse`.
- Sets `implib` to `${prefix}/bin/winfsp-${arch}.dll`.
- Advertises package name `fuse`, description `WinFsp FUSE compatible API`, version `2.8`, and URL `https://winfsp.dev`.
- Emits `Libs` as the WinFsp DLL path and `Cflags` as the FUSE include directory.

Filesystem relevance:
- Build/distribution metadata that lets FUSE-compatible consumers discover headers and link target for WinFsp.

Notable risks:
- Depends on the packaging environment providing `arch` and placing headers/DLLs at the expected relative locations.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_compat.c -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse_compat.c

Export shim for traditional `fuse_*` symbols.

Key responsibilities:
- Documents that normal C/C++ users should consume `fsp_fuse_*` symbols via headers/macros.
- Defines `FSP_FUSE_API` empty and `FSP_FUSE_SYM` as a `__declspec(dllexport)` wrapper.
- Includes `fuse_common.h`, `fuse.h`, and `fuse_opt.h` to instantiate exported `fuse_*` forwarding symbols.
- Uses the default `fsp_fuse_env`.

Dependencies:
- Includes `dll/library.h` and public FUSE compatibility headers.

Filesystem relevance:
- Supports FFI consumers that look up conventional FUSE symbol names directly, such as Python or JVM FUSE bindings.

Notable risks:
- This is intentionally a compatibility/export layer; new native users should avoid depending on these direct symbols when the `fsp_fuse_*` API is available.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_compat.c -->