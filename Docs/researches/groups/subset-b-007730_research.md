# subset-b-007730 Research

Grouped research for the listed OpenAFS Windows redirector, registry, and server-configuration files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRInit.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRInit.cpp

## Purpose
Implements the user-mode side of the Windows AFS redirector control channel. It initializes the redirector service connection to the kernel driver, creates worker threads that block on `IOCTL_AFS_PROCESS_IRP_REQUEST`, dispatches `AFSCommRequest` records into cache-manager and redirector helper routines, and sends completion, extent, lock, status, invalidation, network, volume, and sysname notifications back through `DeviceIoControl`.

## Important APIs, Types, And Functions
Key exported entry points are `RDR_Initialize`, `RDR_ShutdownNotify`, `RDR_ShutdownFinal`, `RDR_ProcessWorkerThreads`, `RDR_RequestWorkerThread`, `RDR_ProcessRequest`, `RDR_SetFileExtents`, `RDR_SetFileStatus`, `RDR_RequestExtentRelease`, `RDR_NetworkStatus`, `RDR_VolumeStatus`, `RDR_InvalidateVolume`, `RDR_InvalidateObject`, `RDR_SysName`, `RDR_Suspend`, and `RDR_Resume`. `RDR_DeviceIoControl` wraps overlapped `DeviceIoControl` with a per-thread TLS event. `WorkerThreadInfo` carries worker handle, readiness event, and request flags, with every fifth non-direct-IO worker reserved for release-extent work. The file depends heavily on driver/user shared structures such as `AFSCommRequest`, `AFSCommResult`, `AFSRedirectorInitInfo`, `AFSSetFileExtentsCB`, `AFSReleaseFileExtentsCB`, `AFSNetworkStatusCB`, `AFSVolumeStatusCB`, `AFSInvalidateCacheCB`, and `AFSSysNameNotificationCB`.

## Control Flow
`RDR_Initialize` creates `RDR_SuspendEvent`, reads `ServerThreads` and `NetbiosName` from `HKLM\...\TransarcAFSDaemon\Parameters`, allocates TLS for overlapped I/O events, starts worker processing, then initializes pioctl and pipe subsystems. `RDR_ProcessWorkerThreads` builds redirector init parameters, opens `AFS_SYMLINK_W`, initializes the control device, starts a bounded thread pool, waits for each worker to signal readiness, and finally sends `IOCTL_AFS_INITIALIZE_REDIRECTOR_DEVICE`. Each worker allocates one reusable request buffer, posts `IOCTL_AFS_PROCESS_IRP_REQUEST`, waits for resume if suspended, and calls `RDR_ProcessRequest`.

`RDR_ProcessRequest` derives `cm_user_t` from the request auth group and dispatches by `RequestType`. It covers directory enumeration; target evaluation by ID/name; create, update, delete, rename, hardlink, symlink, open, flush, cleanup, read, and write operations; pioctl open/write/read/close; byte-range lock/unlock/unlock-all; volume info and size queries; FID hold/release; pipe open/read/write/close/transceive/query/set info; file extent request/release; and unsupported request reporting. Synchronous requests are completed back to the driver with `IOCTL_AFS_COMPLETE_IRP_REQUEST`; asynchronous extent and lock completions use `IOCTL_AFS_SET_FILE_EXTENTS` and `IOCTL_AFS_SET_BYTE_RANGE_LOCKS`. A retry path exists for async file-extent acquisition when helper code asks the dispatcher to loop.

## State And Persistence
In-process global state includes `Exit`, `ExitPending`, `glDevHandle`, `glWorkerThreadInfo`, `glThreadHandleIndex`, `dwOvEvIdx`, `RDR_SuspendEvent`, and `RDR_UNCName`. Persistent input is limited to registry configuration for worker count and redirector UNC/NetBIOS name. Most other state is external: kernel driver request queues, cache-manager objects, held FIDs, extent state, byte-range locks, auth groups, and the Windows event/TLS handles. Shutdown notification sets `ExitPending`, while final shutdown sets `Exit`, closes worker thread handles, and closes the device handle.

## Dependencies And Integration Points
This file is the central integration point between `afsd_service`, the AFS redirector driver, and user-mode cache-manager code declared in `RDRPrototypes.h`. It calls Windows APIs (`CreateFile`, `DeviceIoControl`, `CreateThread`, events, TLS, registry), OpenAFS logging and cache-manager helpers, pioctl logic from `RDRIoctl.c`, named-pipe/MSRPC logic from `RDRPipe.c`, and file/directory/extent/lock implementations in sibling redirector modules. Its IOCTL values and callback structures must stay ABI-compatible with the kernel redirector.

## Risks And Test Signals
The largest risks are ABI drift with driver structures, incomplete cleanup of worker/TLS event handles, races during shutdown while requests are blocked in the driver, and buffer-size mismatches when completing synchronous or async requests. Thread-count registry values are clamped, but extreme values still affect service capacity. Error paths often log and return `GetLastError` or `-1`, so integration tests need driver-level smoke coverage. Useful signals include successful service startup/shutdown, worker thread creation, pioctl/pipe/file I/O request completion, extent release under memory pressure, suspend/resume behavior, cache invalidation notification, and event/log entries for failed IOCTL postings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRInit.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.c -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.c

## Purpose
Implements the redirector-backed pioctl endpoint. It tracks open pioctl instances by request index, buffers write/read halves of the pioctl protocol, decodes opcodes, routes them to cache-manager ioctl handlers, translates path strings into `cm_scache_t` objects, and performs token, ACL, volume, cell, server-preference, symlink, mount-point, Unix-mode, rxstat, UUID, Unicode, verify-data, and caller-access operations.

## Important APIs, Types, And Functions
`RDR_InitIoctl` initializes `RDR_globalIoctlLock` and populates `RDR_ioctlProcsp[CM_IOCTL_MAXPROCS]` with `VIOC*` opcode handlers. `RDR_SetupIoctl`, `RDR_CleanupIoctl`, `RDR_FindIoctl`, `RDR_ReleaseIoctl`, and `RDR_DestroyIoctl` manage the linked list of `RDR_ioctl_t` objects. `RDR_IoctlWrite` appends client data into `cm_ioctl_t.inAllocp`, while `RDR_IoctlRead` lazily executes the opcode through `RDR_IoctlPrepareRead` and copies output chunks to the mapped buffer. Private helpers `RDR_ParseIoctlPath` and `RDR_ParseIoctlParent` resolve pioctl path strings, including UNC paths and share aliases. `RDR_IoctlSetToken` parses Kerberos token material and stores it in `cm_ucell_t`.

## Control Flow
Open/setup creates or reuses an `RDR_ioctl_t`, records parent/root FIDs, and holds the parent scache. Write calls allocate/reset fixed `CM_IOCTL_MAXDATA` input and output buffers at request start, then append caller bytes. The first read after writes clears `CM_IOCTLFLAG_DATAIN`, validates that an opcode is present, bounds-checks it against `CM_IOCTL_MAXPROCS`, looks up the registered handler, reserves space for the return code, runs the handler, and writes the handler return code at the front of the output buffer. Later reads stream remaining output bytes. Cleanup immediately destroys idle instances or marks busy instances with `RDR_IOCTL_FLAG_CLEANED` for deferred destruction after the refcount drops.

Path-oriented handlers either use `cm_ioctlQueryOptions_t` FIDs when present or call `RDR_ParseIoctlPath`/`RDR_ParseIoctlParent`. Those helpers convert UTF-8-prefixed, ANSI, or OEM path bytes into client strings, recognize `\\<RDR_UNCName>\...` forms, expand configured SMB shares through `smb_FindShare`, treat unrecognized shares as cell names under the AFS root, perform `cm_NameI` lookup with case-folding and optional literal/no-mount-chase behavior, and synchronize status callbacks through `cm_SyncOp`. Most remaining handlers skip the path and directly delegate to corresponding `cm_Ioctl*` functions.

## State And Persistence
Runtime state is a global doubly linked list of active pioctl instances guarded by `RDR_globalIoctlLock`, plus per-instance input/output buffers, copied byte counts, flags, parent/root FIDs, held parent scache, request metadata, and refcount. Security-sensitive input/output buffers are zeroed before free. Token-setting persists authentication material in the user/cell token cache (`cm_ucell_t` ticket, session key, kvno, expiration, username, generation, and RXKAD flag) and invalidates ACL cache for the cell. Cell, server-preference, cache-size, rxkcrypt, and other pioctls may update broader cache-manager or configuration state via delegated `cm_Ioctl*` routines.

## Dependencies And Integration Points
The module depends on `afsd.h`, cache-manager structures/functions, SMB share helpers, NLS conversion utilities, rx/auth token definitions, RPC token-event lookup, and the request flags passed by `RDRInit.cpp`. It is called by pioctl open/write/read/close dispatch in the redirector path and exposes declarations through `RDRIoctl.h`/`RDRPrototypes.h`. Its opcode table must align with OpenAFS `VIOC*` constants and `CM_IOCTL_MAXPROCS`.

## Risks And Test Signals
Important risks include fixed-size `CM_IOCTL_MAXDATA` buffering, path-conversion memory leaks because local `free_path` flags are initialized false even when allocations occur, UNC parsing comments noting possible overflow around share-name extraction, duplicated `VIOC_ISSYMLINK` assignment, token handling correctness for local-system/logon callers, and many wrappers relying on delegated cache-manager validation. Test signals should cover fragmented pioctl writes/reads, bad opcode and too-large input cases, path parsing for relative, UNC share, `all`, cell-root, UTF-8, ANSI, and OEM inputs, token set/get/delete cycles, ACL and volume operations, symlink/mount-point creation/deletion, and cleanup while an ioctl is still referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.h

## Purpose
Declares the redirector pioctl subsystem API and, when `RDR_IOCTL_PRIVATE` is defined, exposes the private instance structure, flags, function-pointer type, and all opcode handler prototypes used by `RDRIoctl.c`.

## Important APIs, Types, And Functions
The public API is `RDR_InitIoctl`, `RDR_ShutdownIoctl`, `RDR_SetupIoctl`, `RDR_CleanupIoctl`, `RDR_IoctlRead`, and `RDR_IoctlWrite`. The private `RDR_ioctl_t` stores list links, request index, parent/root FIDs, held parent scache, embedded `cm_ioctl_t`, flags, lock-protected refcount, and `cm_req_t`. `RDR_ioctlProc_t` is the common handler signature. The header declares handlers for ACLs, token management, volume/cell/server/cache controls, mount points, symlinks, rx statistics, UUID/path availability, file type, Unix owner/group/mode, verify data, and caller access.

## Control Flow
Callers create pioctl state with `RDR_SetupIoctl`, push bytes with `RDR_IoctlWrite`, retrieve the return code and response stream with `RDR_IoctlRead`, and tear state down with `RDR_CleanupIoctl`. Private helpers declared here allow `RDRIoctl.c` to transition a request from data-in to data-out and find/refcount live instances.

## State And Persistence
The header defines no state by itself, but its private structure describes the in-memory persistence of a pioctl request across multiple redirector read/write calls. `RDR_IOCTL_FLAG_CLEANED` marks instances that were closed while still referenced.

## Dependencies And Integration Points
It depends on cache-manager pointer types and `cm_ioctl_t` from surrounding includes. It is included by `RDRIoctl.c` with `RDR_IOCTL_PRIVATE` and by other redirector modules for public entry points. The handler prototypes integrate with `VIOC*` opcode registration in `RDR_InitIoctl`.

## Risks And Test Signals
The main risk is declaration drift against implementations and the opcode table. Because private declarations expose many cache-manager wrappers, signature mismatches can break C/C++ callers. Compile coverage of `RDRIoctl.c` and pioctl integration tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.c -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.c

## Purpose
Implements user-mode state for redirector named-pipe/MSRPC endpoints. It maps kernel pipe request indexes to `RDR_pipe_t` instances, initializes MSRPC connections, proxies read/write operations to the MSRPC layer, and returns basic file/pipe information expected by Windows pipe clients.

## Important APIs, Types, And Functions
The main functions are `RDR_InitPipe`, `RDR_ShutdownPipe`, `RDR_FindPipe`, `RDR_SetupPipe`, `RDR_CleanupPipe`, `RDR_Pipe_Read`, `RDR_Pipe_Write`, `RDR_Pipe_QueryInfo`, and `RDR_Pipe_SetInfo`. `RDR_SetupPipe` converts the incoming UTF-16 pipe name to UTF-8, initializes `msrpc_conn` with `MSRPC_InitConn`, records parent/root FIDs and scache, and configures message-mode client-end device state. Read/write functions call `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, `MSRPC_ReadMessage`, and `MSRPC_WriteMessage`.

## Control Flow
Initialization creates a global RW lock. Setup runs under the write lock, reuses an existing pipe by index or allocates a new one, resolves/holds the parent scache, initializes the RPC connection by pipe name, and links the instance only after successful RPC init. Cleanup unlinks the instance, releases the scache, zeroes/free input/output buffers if allocated, frees the RPC connection, and frees the structure. Read, write, query-info, and set-info requests look up the instance under the lock and return `STATUS_INVALID_PIPE_STATE` when missing. Query-info supports basic, standard, and name information; set-info supports `FilePipeInformation` read/completion mode updates.

## State And Persistence
State is an in-memory doubly linked list guarded by `RDR_globalPipeLock`. Each pipe stores request index, name, parent/root FIDs, parent scache, flags, device state, and `msrpc_conn`. No registry or disk state is written. Buffers are zeroed on cleanup, although the current implementation mostly delegates payload storage to `msrpc_conn`.

## Dependencies And Integration Points
This module depends on Windows status codes and file-information layouts, OpenAFS cache-manager FIDs/scaches, `msrpc.h`, `cm_rpc.h`, `afs/afsrpc.h`, auth structures, SMB/NLS helpers, and `RDRPipe.h`. It is reached from `RDR_ProcessRequest` cases for pipe open, read, write, close, transceive, query info, and set info.

## Risks And Test Signals
Risks include lock granularity around potentially blocking MSRPC operations, exact `FILE_INFORMATION_CLASS` layout compatibility with kernel expectations, cleanup correctness when RPC init fails, and mode flag mismatches because `devstate` is initialized but only `flags` are later modified. Test signals include named-pipe open/close, message-mode read/write/transceive, file-name query buffer overflow handling, pipe mode set/query behavior, and shutdown cleanup with multiple live pipe instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.h

## Purpose
Declares the redirector pipe API and, under `RDR_PIPE_PRIVATE`, the private pipe state structure plus local copies of Windows DDK pipe information types needed by user-mode code that cannot include DDK headers.

## Important APIs, Types, And Functions
Public declarations include pipe lifecycle (`RDR_InitPipe`, `RDR_ShutdownPipe`, `RDR_SetupPipe`, `RDR_CleanupPipe`) and I/O/info calls (`RDR_Pipe_Read`, `RDR_Pipe_Write`, `RDR_Pipe_QueryInfo`, `RDR_Pipe_SetInfo`). `RDR_pipe_t` stores list links, request index, UTF-16 name, parent/root FIDs, held parent scache, flags, device state, `msrpc_conn`, and optional input/output buffers. The header defines pipe flags, device-state bits, `RDR_PIPE_MAXDATA`, `RDR_pipeProc_t`, `FILE_INFORMATION_CLASS`, and structures such as `FILE_BASIC_INFORMATION`, `FILE_STANDARD_INFORMATION`, `FILE_NAME_INFORMATION`, and `FILE_PIPE_INFORMATION`.

## Control Flow
The declared API supports the flow where redirector dispatch opens a pipe with a request index, performs multiple reads/writes and info calls against that index, and closes it later. Private declarations let `RDRPipe.c` find an instance and format Windows-compatible responses.

## State And Persistence
The header itself persists no state, but it defines the shape of per-pipe memory retained between kernel requests. Flag constants track data direction, logon/UTF-8 state, RPC/message/blocking modes, and in-call state.

## Dependencies And Integration Points
It relies on surrounding includes for `DWORD`, `ULONG`, `WCHAR`, `cm_fid_t`, `cm_req_t`, `cm_user_t`, `cm_scache_t`, and `msrpc_conn`. It bridges redirector request dispatch to MSRPC pipe handling and Windows file-information semantics.

## Risks And Test Signals
Risks are ABI/layout drift in replicated DDK structures and inconsistencies between flag constants and implementation. Compile checks on user-mode pipe code and runtime query/set-info tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPrototypes.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPrototypes.h

## Purpose
Centralizes C-linkage prototypes for the Windows redirector user-mode implementation. It lets C and C++ redirector modules call common request, file, directory, extent, pioctl, pipe, byte-range-lock, volume, user, and FID conversion helpers without circular includes.

## Important APIs, Types, And Functions
The header forward-declares `cm_user_t`, `cm_req_t`, `cm_fid_t`, and `cm_scache_t`, includes shared `AFSUserPrototypes.h`, and declares `RDR_InitReq`, `RDR_SetInitParams`, worker/request dispatch, directory/file lifecycle helpers, async file extent functions, pioctl open/write/read/close, byte-range lock helpers, volume info helpers, FID hold/release, pipe helpers, raw read/write helpers, `RDR_UserFromCommRequest`, `RDR_UserFromAuthGroup`, `RDR_ReleaseUser`, `RDR_fid2FID`, `RDR_FID2fid`, and ioctl init/shutdown.

## Control Flow
The prototypes describe the end-to-end dispatch graph used by `RDRInit.cpp`: worker threads receive an `AFSCommRequest`, map it to a user, fan out to one of these helper families, and return `AFSCommResult` or asynchronous result callbacks. The same declarations support helper modules that need to call back into driver notification functions.

## State And Persistence
The header has no runtime state. Its signatures expose the state surfaces passed across modules: auth users, AFS file IDs, cache-manager FIDs/scaches, request contexts, result-buffer lengths, mapped I/O buffers, and flags such as WoW64, fast query, mount following, cache bypass, and FID holding.

## Dependencies And Integration Points
This is a broad integration header for `afsrdr/user` modules and includes `ntsecapi.h` for security/auth interfaces. It must remain consistent with shared driver callback structures from the common redirector headers and with implementations spread across many `.cpp`/`.c` files.

## Risks And Test Signals
The main risk is prototype drift, especially across C/C++ compilation units and shared structures whose layout also matters to the kernel driver. Full Windows redirector build coverage and request-dispatch smoke tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPrototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.c

## Purpose
Provides extended Windows registry helpers for OpenAFS installers/configuration tools. It opens canonical registry paths, reads values with optional allocation, enumerates subkeys into multistrings, recursively deletes keys, deletes named key/value entries, and duplicates entire registry key trees.

## Important APIs, Types, And Functions
Exported functions are `IsWow64`, `RegOpenKeyAlt`, `RegQueryValueAlt`, `RegEnumKeyAlt`, `RegDeleteKeyAlt`, `RegDeleteEntryAlt`, and `RegDupKeyAlt`. Private helpers `CopyKey`, `CopyValues`, and `CopySubkeys` implement recursive duplication. `IsWow64` dynamically resolves `IsWow64Process` and caches the result. `RegOpenKeyAlt` can parse a full path beginning with predefined key names such as `HKEY_LOCAL_MACHINE`, and on WoW64 adds `KEY_WOW64_64KEY` to access the 64-bit registry view.

## Control Flow
Open operations optionally create keys through `RegCreateKeyEx` or open existing keys through `RegOpenKeyEx`. Query operations either fill a caller-supplied buffer or first probe with a DWORD-sized read, allocate the required size, and read again when needed. Enumeration calls `RegQueryInfoKey` for count/name size, allocates one double-NUL-terminated multistring, and fills it with `RegEnumKeyEx`. Recursive delete first tries `RegDeleteKey`, falls back to enumerating/deleting children if needed, then retries the delete. Duplication deletes the target key, copies source values, and recursively copies subkeys.

## State And Persistence
All meaningful state is Windows registry state. The helper can create, delete, overwrite, and duplicate HKLM/HKCU/HKCR/HKU/etc. subtrees. Allocated buffers returned by query/enumeration must be freed by callers. The WoW64 detection result is cached in static variables.

## Dependencies And Integration Points
The file uses Win32 registry APIs, `windows.h`, `roken`, and constants/types from `afsreg.h`. It is used by `afssw.c`, `syscfg.c`, `vptab.c`, and the test tools to hide path parsing, allocation, recursive delete, and 64-bit registry view selection.

## Risks And Test Signals
This checkout shows a duplicated `RegDeleteKeyAlt(HKEY key,` declaration line before the real signature, which is a compile risk. Runtime risks include destructive recursive deletion, target replacement in `RegDupKeyAlt`, allocation-size assumptions for multistrings, path parsing that accepts prefix-length matches, and `FreeLibrary` being called on a module handle returned by `GetModuleHandle`. Test signals include building the library, duplicating/deleting nested test keys, reading DWORD/string/multistring values, and verifying 32-bit process behavior on 64-bit Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.h -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.h

## Purpose
Defines OpenAFS Windows registry key/value constants and declares the extended registry helper API implemented by `afsreg.c`.

## Important APIs, Types, And Functions
The header names service identifiers (`TransarcAFSServer`, `TransarcAFSDaemon`), software keys under `Software\TransarcCorporation`, client OpenAFS keys, event-log keys, TCP/IP interface keys, server Afstab keys, client service parameter/provider keys, and network-provider order values. It defines `regentry_t` with `REGENTRY_KEY` and `REGENTRY_VALUE`, plus prototypes for `RegOpenKeyAlt`, `RegQueryValueAlt`, `RegEnumKeyAlt`, `RegDeleteKeyAlt`, `RegDeleteEntryAlt`, `RegDupKeyAlt`, and `IsWow64`.

## Control Flow
Consumers combine these constants with the helper functions to open, read, write, delete, or duplicate OpenAFS-related registry state. The constants encode both canonical full paths and subkey paths so callers can start at `AFSREG_NULL_KEY` or an already-open parent.

## State And Persistence
The file itself has no runtime state, but it defines the persistent registry schema for OpenAFS server/client install metadata, service configuration, event-log source registration, client cell and CellServDB location, server vice partition table entries, TCP/IP interface inspection, and network provider ordering.

## Dependencies And Integration Points
It requires Win32 `HKEY`/`TEXT` types from `windows.h` in consumers. It is shared by registry helpers, installers/configuration tools, server partition table code, and system interface discovery.

## Risks And Test Signals
Changing any string can break installers, services, or backwards compatibility with existing registry installations. Header compile coverage and install/configuration smoke tests that verify expected key names are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.c

## Purpose
Implements convenience accessors for OpenAFS software configuration in the Windows registry: server/client install directories, client CellServDB directory, client cell name, and installed client/server version numbers.

## Important APIs, Types, And Functions
Exported functions include `afssw_GetServerInstallDir`, `afssw_GetClientInstallDir` (implemented but not declared in the companion header), `afssw_GetClientCellServDBDir`, `afssw_GetClientCellName`, `afssw_SetClientCellName`, `afssw_GetServerVersion`, and `afssw_GetClientVersion`. Private helpers are `StringDataRead`, `StringDataWrite`, and `DwordDataRead`.

## Control Flow
String reads open a configured registry key, use `RegQueryValueAlt`, validate `REG_SZ`, and return an allocated buffer. String writes create/open the target key and set a `REG_SZ` value. DWORD reads validate `REG_DWORD`. `afssw_GetClientInstallDir` falls back from the normal client software key to the legacy client-tools key. `afssw_GetClientCellServDBDir` prefers the `AFSCONF` environment variable, then the OpenAFS `CellServDBDir` registry value, then `All Users\Application Data\OpenAFS\Client` if it contains `CellServDB`, and finally the client install directory.

## State And Persistence
Reads expose persistent installer/service registry values. `afssw_SetClientCellName` writes the client service `Parameters\Cell` value. Returned string buffers are heap-allocated and owned by the caller. The CellServDB directory lookup also observes process environment and filesystem existence of a CellServDB file.

## Dependencies And Integration Points
The module depends on `afsreg.h`, `afssw.h`, `nterr_nt2unix` error mapping, Win32 registry APIs, `SHGetFolderPath`, and file existence checks through `CreateFile`. It is used by configuration tools such as `regman.c` and likely server/client setup code.

## Risks And Test Signals
Risks include undeclared `afssw_GetClientInstallDir` in `afssw.h`, string buffer/path truncation around fixed 512-byte `wdir`, mixed slash conventions while constructing default server paths, and reliance on legacy registry keys. Test signals include reading all install/version values from test registry fixtures, setting and re-reading the client cell, exercising `AFSCONF` override, and validating fallback to common appdata when `CellServDB` exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.h -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.h

## Purpose
Declares the public registry accessors for OpenAFS software configuration.

## Important APIs, Types, And Functions
The header declares `afssw_GetServerInstallDir`, `afssw_GetClientCellServDBDir`, `afssw_GetClientCellName`, `afssw_SetClientCellName`, `afssw_GetServerVersion`, and `afssw_GetClientVersion`, all under C linkage for C++ callers.

## Control Flow
Callers use these functions to read allocated strings or version triples, and to write the client cell name. Return convention is `0` on success and `-1` with `errno` set for failures.

## State And Persistence
The declarations represent access to persistent registry configuration under the keys defined in `afsreg.h`; the header itself stores no state.

## Dependencies And Integration Points
It is consumed by installer/configuration tools and pairs with `afssw.c`. Consumers must free returned strings from the getter functions.

## Risks And Test Signals
The implementation contains `afssw_GetClientInstallDir`, but this header does not declare it, so callers relying on the header cannot use that accessor without an external declaration. Compile coverage for all intended consumers is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.c

## Purpose
Retrieves IPv4 interface configuration for OpenAFS on Windows: addresses, subnet masks, MTUs, and flags. It supports modern `GetAdaptersAddresses`/`GetIpAddrTable` discovery and a fallback path for older Windows 2000-style registry layout.

## Important APIs, Types, And Functions
Public APIs are `syscfg_GetIFInfo` and fallback `syscfg_GetIFInfo_2000`. Private helpers include `GetMTUForAddress`, `IsLoopback`, `GetInterfaceList`, `GetNextInterface`, and `GetIP`. `syscfg_GetIFInfo` dynamically loads `iphlpapi` and resolves `GetAdaptersAddresses`, while still using `GetIpAddrTable` to map adapter indexes to IPv4 addresses and masks.

## Control Flow
The modern path probes `GetIpAddrTable` for size, reads the IP address table, probes `GetAdaptersAddresses` for size, reads adapter data, skips software loopback and down interfaces, performs an additional registry-based loopback check, then matches IP table entries by interface index. For each accepted entry it stores host-order address/mask, MTU as the minimum of adapter MTU and registry MTU, and flags as zero until the caller-provided capacity is reached; the return value still counts configured entries. If `GetAdaptersAddresses` is unavailable, `syscfg_GetIFInfo_2000` opens the TCP/IP services key, reads the `Tcpip\Linkage\Bind` multistring, iterates adapter names, filters loopback devices, reads static or DHCP IP/mask values, and assigns default MTU 1500.

## State And Persistence
The module only reads state: IP helper API data plus registry keys under `SYSTEM\CurrentControlSet\Services`, adapter `IpConfig`, interface `MTU`, TCP/IP `Bind`, DHCP/static address values, and network adapter enum data used to identify Microsoft loopback adapters. It fills caller-owned arrays and updates `*count` to the number of returned entries.

## Dependencies And Integration Points
It depends on WinSock/IP Helper APIs, registry helpers from `afsreg.c`, TCP/IP key constants from `afsreg.h`, and `syscfg.h`. It is a system configuration provider for network-address initialization in OpenAFS networking code and has a test utility in `test/getifinfo.c`.

## Risks And Test Signals
Risks include manual memory management around multi-pass IP helper calls, handling systems with no addresses, registry MTU fallback value `0xFFFFFFFF`, old registry schemas, fixed default MTU in the fallback path, and `GetNextInterface` pointer arithmetic over multistrings. Modern and fallback paths should be tested on hosts with multiple NICs, DHCP/static addresses, down interfaces, loopback adapters, nondefault MTUs, and caller arrays smaller than the interface count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.h -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.h

## Purpose
Declares the Windows system-configuration function that returns network interface address information.

## Important APIs, Types, And Functions
The sole public function is `syscfg_GetIFInfo(int *count, int *addrs, int *masks, int *mtus, int *flags)`. It uses C linkage for C++ callers.

## Control Flow
Callers pass array capacity in `*count`; on return, `*count` is the number of elements filled and the function result is the total configured usable interface count or `-1` on error.

## State And Persistence
The header defines no state. The API exposes caller-provided arrays for IPv4 addresses, masks, MTUs, and flags.

## Dependencies And Integration Points
It pairs with `syscfg.c` and is included by the interface-info test utility and network initialization code.

## Risks And Test Signals
The API contract relies on callers sizing all arrays consistently and interpreting addresses in host byte order. Compile tests and `getifinfo` runtime output are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/test/dupkey.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/test/dupkey.c

## Purpose
Small manual test program for `RegDupKeyAlt`. It duplicates one registry key tree to another and reports success or the Win32 error code.

## Important APIs, Types, And Functions
The only function is `main`, which validates that two key path arguments were supplied and calls `RegDupKeyAlt(argv[1], argv[2])`.

## Control Flow
Incorrect argument count prints `Usage: <program> key1 key2` and exits with status 1. Otherwise the program performs duplication and prints a success/failure message. The source and target key names are expected to be canonical paths accepted by `RegOpenKeyAlt`.

## State And Persistence
The program can modify persistent registry state by deleting/replacing the target key and copying source values/subkeys into it.

## Dependencies And Integration Points
It includes `WINNT/afsreg.h` and links against the registry helper implementation plus Win32 registry libraries. It is a developer/admin diagnostic rather than production code.

## Risks And Test Signals
Because target keys are replaced by `RegDupKeyAlt`, running it with real OpenAFS keys can be destructive. Useful test signals are success duplicating a temporary nested key and failure codes for missing source or inaccessible target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/test/dupkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/test/getifinfo.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/test/getifinfo.c

## Purpose
Manual test utility for `syscfg_GetIFInfo`. It prints detected usable IPv4 addresses and subnet masks for the local machine.

## Important APIs, Types, And Functions
The file defines fixed arrays `addrs`, `masks`, `mtus`, and `flags` with `MAXIPADDRS` capacity, plus `main` that calls `syscfg_GetIFInfo`, converts host-order addresses back to dotted decimal with `htonl` and `inet_ntoa`, and prints the results.

## Control Flow
The program initializes `rxi_numNetAddrs` to 16, calls the system-configuration API, reports failure if it returns negative, otherwise prints the number of usable addresses and iterates the filled entries.

## State And Persistence
No persistent state is changed. It reads host network configuration indirectly through `syscfg_GetIFInfo` and writes output to stdout.

## Dependencies And Integration Points
It includes WinSock2 and `WINNT/syscfg.h`, and links with the syscfg implementation and networking libraries. It provides a quick runtime signal for the registry/IP-helper code.

## Risks And Test Signals
The file uses old-style `main` without an explicit return type and has an accidental nested comment opener near the header comment, both compile-style risks depending on compiler strictness. Runtime test signal is the printed interface list compared against `ipconfig`/adapter configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/test/getifinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/test/regman.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/test/regman.c

## Purpose
Manual registry/service management utility for OpenAFS Windows configuration. It can list/add/delete vice partition table entries, get/set the server install directory, create/delete the BOS control service, and display installed client/server version information.

## Important APIs, Types, And Functions
Command handlers include `DoVptList`, `DoVptAdd`, `DoVptDel`, `DoDirGet`, `DoDirSet`, `DoBosCfg`, `DoBosDel`, and `DoVersionGet`. Setup functions register command syntaxes through the OpenAFS `cmd` package. `main` initializes the command error table, registers all syntaxes, and dispatches. It uses `vptab` APIs, `afssw` accessors, registry helpers, Windows Service Control Manager APIs, and OpenAFS path constants.

## Control Flow
VPT commands validate names/devices before reading or mutating Afstab entries. Directory commands read or write `AFSREG_SVR_SW_VERSION_DIR_VALUE`. BOS config either quotes an explicitly provided service path or constructs one from the server install dir and canonical server binary path, then calls `CreateService` for `TransarcAFSServer`. BOS delete opens and deletes the service, treating already-missing/marked-for-delete conditions as nonfatal. Version command attempts client and server version reads independently.

## State And Persistence
The utility mutates persistent registry state for server install directory and vice partition table entries, and mutates SCM service configuration when creating/deleting the BOS service. It reads installed version information and may allocate temporary strings that are freed by command handlers.

## Dependencies And Integration Points
It integrates the `afsreg`, `afssw`, and `vptab` libraries with the OpenAFS command parser and Windows SCM. It is useful as a pre-configuration-manager or diagnostic tool.

## Risks And Test Signals
Risks include destructive service deletion/creation, required administrator privileges, quoted path construction, mixed slash separators in the default BOS path, and unchecked `strcpy` into fixed-size `vptab` fields after validation. Test signals include each command against temporary registry/service fixtures, privilege-denied behavior, idempotent delete of missing service/partition, and version output when registry values are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/test/regman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.c -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.c

## Purpose
Implements the Windows vice partition table stored in the registry under the OpenAFS server service Afstab key. It validates partition/device names, enumerates entries, adds/updates entries, and removes entries.

## Important APIs, Types, And Functions
Exported functions are `vpt_PartitionNameValid`, `vpt_DeviceNameValid`, `vpt_Start`, `vpt_NextEntry`, `vpt_Finish`, `vpt_AddEntry`, and `vpt_RemoveEntry`. `PARTITION_NAME_PREFIX` is `/vicep`. Entries are `struct vptab` with `vp_name` and `vp_dev`; iteration uses `struct vpt_iter` over a registry multistring.

## Control Flow
Partition validation accepts `/vicep` plus one lowercase suffix letter or two lowercase letters whose encoded value is within 26..255. Device validation accepts only an uppercase drive letter followed by `:`. Iteration opens `AFSREG_SVR_SVC_AFSTAB_KEY`, enumerates child keys with `RegEnumKeyAlt`, and each `vpt_NextEntry` opens the partition key and reads `DeviceName`. Add opens/creates the Afstab key and partition subkey and writes `DeviceName`. Remove validates the partition name, opens Afstab, and deletes the partition key.

## State And Persistence
The persistent state is registry subkeys under `HKLM\System\CurrentControlSet\Services\TransarcAFSServer\Afstab`, one subkey per vice partition, with a `DeviceName` string value. Iteration state is a heap-allocated multistring owned by the caller until `vpt_Finish`.

## Dependencies And Integration Points
It depends on `afsreg.h` key constants and registry helper functions plus NT-to-Unix errno mapping. It is used by server configuration tools and the `regman` test utility.

## Risks And Test Signals
Risks include strict C-locale assumptions, fixed 32-byte name/device buffers, no recursive delete for partition subkeys, and limited device syntax that only accepts drive-letter devices. Test signals include validation edge cases (`/vicepa`, `/vicepz`, `/vicepaa`, upper/lower drive names), add/list/remove round trips, and errno behavior for missing or malformed registry entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.h -->
# sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.h

## Purpose
Declares the vice partition table data structures and registry-backed access functions.

## Important APIs, Types, And Functions
The header defines `VPTABSIZE_NAME` and `VPTABSIZE_DEV`, `struct vptab` with `vp_name` and `vp_dev`, `struct vpt_iter` with multistring iteration pointers, and prototypes for starting/advancing/finishing iteration, adding/removing entries, and validating partition/device names.

## Control Flow
Callers iterate with `vpt_Start`, repeated `vpt_NextEntry`, then `vpt_Finish`; mutations use `vpt_AddEntry` and `vpt_RemoveEntry` after validation.

## State And Persistence
The structures represent registry-backed persistent partition entries, while `vpt_iter` owns transient enumeration memory allocated by the implementation.

## Dependencies And Integration Points
It uses C linkage for C++ callers and pairs with `vptab.c`. It is consumed by server setup/diagnostic utilities such as `regman.c`.

## Risks And Test Signals
The fixed field sizes and validation contract are the main compatibility boundaries. Compile coverage and add/list/remove tests are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.cpp

## Purpose
Implements a modal Windows dialog that collects administrator credentials and, optionally, the system control server hostname for the OpenAFS server configuration application.

## Important APIs, Types, And Functions
`GetAdminInfo` sets the requested mode and opens `IDD_ADMIN_INFO` through `ModalDialog`. `AdminInfoDlgProc` handles help, initialization, command notifications, cancel, and OK. Static helpers are `OnInitDialog`, `CheckEnableButtons`, `SaveDlgInfo`, and `ShowPageInfo`. The dialog reads/writes global `g_CfgData` fields: `szAdminName`, `szAdminPW`, and optionally `szSysControlMachine`.

## Control Flow
On initialization, the dialog stores its `HWND`, hides hostname controls when only login data is needed, moves buttons upward, and shrinks the window. It then populates controls from `g_CfgData`. Edit changes in admin name/password/hostname/SCS controls trigger `CheckEnableButtons`, which enables OK only when admin name and password are nonempty. OK saves control text into `g_CfgData` and ends with `IDOK`; cancel ends with `IDCANCEL`.

## State And Persistence
State is UI-local `hDlg`, static `eOptions`, and a static layout offset cached across invocations. User-entered values are persisted into the process-global configuration data structure; no registry or disk write occurs here.

## Dependencies And Integration Points
The file depends on Win32 dialog messaging, Winsock includes inherited by the application, `afscfg.h`, `resource.h`, UI helper functions (`ModalDialog`, `HideAndDisable`, `MoveWnd`, `SetEnable`, `GetWndText`, `SetWndText`), help integration through `AfsAppLib_HandleHelp`, and constants for maximum field lengths.

## Risks And Test Signals
Risks include password retention in global memory, `lstrncpy` truncation without explicit visible validation, OK enablement not requiring the SCS hostname even in `GAIO_GET_SCS` mode, static offset reuse if dialog resources change, and layout issues after hiding controls. Test signals include both modes rendering correctly, OK enable/disable behavior, saved field truncation boundaries, cancel preserving prior data, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.h

## Purpose
Declares the administrator-information dialog entry point and option enum for the OpenAFS server configuration UI.

## Important APIs, Types, And Functions
`GET_ADMIN_INFO_OPTIONS` has `GAIO_LOGIN_ONLY` and `GAIO_GET_SCS`, where the latter includes the former plus system-control-server collection. `GetAdminInfo(HWND hParent, GET_ADMIN_INFO_OPTIONS eOptions)` opens the modal dialog and returns success/failure.

## Control Flow
Callers select the mode, call `GetAdminInfo`, and on `TRUE` read updated global configuration data managed by the dialog implementation.

## State And Persistence
The header itself has no state. The option controls which UI fields are shown and which global config fields are saved by `admin_info_dlg.cpp`.

## Dependencies And Integration Points
It depends on Win32 `HWND`/`BOOL` types from surrounding includes and is consumed by the server configuration application where administrator credentials are needed.

## Risks And Test Signals
The enum ordering is documented as cumulative, so future options should preserve that assumption. Compile coverage and dialog smoke tests in both modes are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.h -->
