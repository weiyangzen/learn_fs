# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.c

## Purpose

`cm_volstat.c` implements the Windows AFS cache-manager Volume Status Event Notification API. It dynamically loads an optional external volume-status handler DLL configured in the Windows registry, passes a bidirectional function table to that DLL, forwards service/network/volume/DFS-mapping events to it, and exposes callbacks that let the DLL map SMB/redirector paths back to AFS cell and volume IDs or DFS-link targets.

The file also bridges volume/network events to the native redirector (`RDR_*`) through an internal event queue and a delivery thread when redirector volume-status notifications are enabled.

## Important APIs, Types, and Functions

Global state:

- `hVolStatus` is the loaded handler DLL module handle. A non-NULL value means the external handler is active.
- `dll_funcs` stores callbacks supplied by the external DLL.
- `cm_funcs` stores cache-manager callbacks passed to the DLL.
- `volstat_NetbiosName` is read from registry and used to build UNC-style DFS mapping source paths.
- `RDR_Notifications` enables redirector notification forwarding.
- `rdr_evtH`/`rdr_evtT`, `rdr_q_event`, and `rdr_evt_lock` implement the redirector event queue.

Lifecycle and notification functions:

- `cm_VolStatus_SetRDRNotifications` toggles redirector notifications.
- `cm_VolStatus_Active` reports whether a handler DLL is loaded.
- `cm_VolStatus_Initialization` reads registry configuration, loads the handler DLL, resolves `VolStatus_Initialization`, initializes function tables, validates handler version, and starts redirector notification delivery if configured.
- `cm_VolStatus_Finalize` closes the redirector event handle and unloads the handler DLL.
- `cm_VolStatus_Service_Started`/`Service_Stopped` notify the DLL about AFS service lifecycle; service start also notifies network start if SMB networking is already active.
- `cm_VolStatus_Network_Started`/`Network_Stopped` notify both redirector queue and DLL of NetBIOS availability.
- `cm_VolStatus_Network_Addr_Change` reports IP address changes.
- `cm_VolStatus_Change_Notification` reports volume online/offline-like state changes to redirector and DLL.
- `cm_VolStatus_DeliverNotifications` is the long-running redirector queue consumer that calls `RDR_NetworkAddrChange`, `RDR_VolumeStatus`, or `RDR_NetworkStatus`.

Path and DFS functions:

- `cm_VolStatus_Notify_DFS_Mapping` informs version-2 DLL handlers about a DFS mapping for a scache, converting client paths to UTF-8 and normalizing slashes for UNC-style paths.
- `cm_VolStatus_Invalidate_DFS_Mapping` invalidates a previously reported DFS mapping by fid components.
- `cm_VolStatus_Path_To_ID` resolves a share/path into an scache via `cm_NameI`, fetches status/callback, returns cell and volume IDs, and optionally returns cached volume status.
- `cm_VolStatus_Path_To_DFSlink` resolves a share/path, verifies the target scache is a DFS link, and returns its mount-point string with size-query semantics.

## Control Flow

Initialization reads `AFSREG_CLT_SVC_PARAM_SUBKEY` under `HKEY_LOCAL_MACHINE`. If `VolStatusHandler` is configured, it optionally reads `NetbiosName`, loads the DLL path with `LoadLibrary`, resolves the decorated initialization export, fills `cm_funcs` with cache-manager path callbacks, sets `dll_funcs.version`, and calls into the DLL. Any missing export, non-zero initialization code, or version mismatch unloads the DLL and disables external notifications. It then separately reads `RDRVolStatNotify`; if the redirector is initialized and notifications are enabled, it initializes a mutex, starts `cm_VolStatus_DeliverNotifications`, and creates a manual-reset event named `rdr_q_event`.

Service/network/volume notification functions are no-op success paths when no DLL is loaded. When redirector forwarding is enabled, they allocate an `rdr_volstat_evt_t`, fill its event type/data, append it to the queue under `rdr_evt_lock`, and signal `rdr_q_event`. They then call the corresponding function pointer in `dll_funcs` if `hVolStatus` is active.

The path-to-ID and path-to-DFS-link callbacks convert incoming filesystem strings to client strings, initialize a root-user request, resolve the path relative to `cm_RootSCachep(cm_rootUserp, &req)` using case-fold and follow flags, obtain current status under the scache write lock with `cm_SyncOp`, and extract the requested information. Both free converted strings and release scaches before returning. `Path_To_DFSlink` supports a size query when `pBuffer == NULL`, checks buffer capacity when a buffer is supplied, and returns `CM_ERROR_TOOBIG` on insufficient capacity.

`cm_VolStatus_DeliverNotifications` waits forever on `rdr_q_event`, drains queued events from tail to head under `rdr_evt_lock`, releases the mutex while making redirector calls, frees each event, and reacquires the mutex to continue draining.

## State and Persistence Behavior

Persistent configuration comes from the Windows registry values `VolStatusHandler`, `NetbiosName`, and `RDRVolStatNotify`. Runtime state is process-local: the loaded module handle, function tables, NetBIOS name buffer, redirector notification flag, event queue, event handle, and mutex.

Path mapping state is not stored by this file. DFS mapping notifications are forwarded to an external DLL; invalidation is also delegated. Redirector events are transient heap allocations that are freed by the delivery thread.

## Dependencies and Integration Points

Key dependencies include:

- Windows APIs: registry (`RegOpenKeyEx`, `RegQueryValueEx`, `RegCloseKey`), dynamic loading (`LoadLibrary`, `GetProcAddress`, `FreeLibrary`), events (`CloseHandle`, `GetLastError`), WinSock/NetBIOS headers, and `HMODULE`.
- OpenAFS Windows cache-manager headers: `afsd.h`, `smb.h`, `afsreg.h`, string conversion helpers, request/scache/volume APIs, and logging.
- External handler ABI from `cm_volstat.h`: `dll_VolStatus_Funcs_t` and `cm_VolStatus_Funcs_t`.
- Redirector hooks declared as externs: `RDR_NetworkAddrChange`, `RDR_VolumeStatus`, `RDR_NetworkStatus`.
- Path lookup and DFS-link integration with `cm_NameI`, `cm_RootSCachep`, `cm_SyncOp`, `cm_GetVolumeByFID`, `cm_GetVolumeStatus`, and scache mount-point strings.

## Risks and Edge Cases

- Redirector event allocations are not checked for `malloc` failure before dereference.
- `cm_VolStatus_DeliverNotifications` runs forever and `Finalize` only closes the event handle; shutdown ordering must ensure the thread cannot use a closed handle or freed synchronization object.
- The event is created as manual-reset and initially signaled. The code drains the queue but does not reset the event in this file; behavior depends on the thread/event wrapper semantics and may spin if the event remains signaled.
- External DLL ABI relies on decorated export name `@VolStatus_Initialization@8` and exact version matching.
- Registry value sizes and string termination depend on registry data correctness. The fixed 64-byte NetBIOS buffer and 1024-byte DFS source buffer are potential truncation points.
- `cm_VolStatus_Notify_DFS_Mapping` uses `strncat(src, ..., sizeof(src))`, which is not the usual remaining-capacity pattern; while the fixed buffer limits writes, truncation behavior should be reviewed carefully.
- `Path_To_DFSlink` has error paths after status sync that jump to `done` without releasing the scache write lock and scache reference in the visible code. The `fileType != DFSLINK` and `TOOBIG` branches are especially important to audit or test for lock/reference leaks.
- Path resolution uses root user credentials and case-fold/follow behavior, so handler queries can see root-user access semantics rather than the original application user.

## Test Signals

- Initialization matrix: no registry key, handler path missing, DLL missing export, DLL returns failure, version mismatch, successful version-1 and version-2 handler.
- Service/network notifications with and without loaded DLL, and with `_WIN64` versus 32-bit signatures.
- Redirector queue tests for network up/down, address change, volume online/offline transitions, concurrent enqueue/drain, service shutdown, and memory cleanup.
- Path callbacks for invalid parameters, conversion failure, missing paths, successful file/dir paths, volume status known/unknown, DFS-link size query, exact-size buffer, too-small buffer, and non-DFS-link target.
- DFS mapping tests for slash normalization, trailing/leading slash joins, UTF-8 conversion, version-1 handler no-op, and invalidation by fid.
