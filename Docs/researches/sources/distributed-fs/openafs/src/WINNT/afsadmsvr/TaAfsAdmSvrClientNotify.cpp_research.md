<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.cpp

Purpose: implements client-side notification registration for the AFS admin server client library. It tracks windows interested in object property changes and action lifecycle changes, then posts Windows messages when server-side cache updates or action state changes are observed.

Important APIs/types/functions: `LISTENER` binds `idCell`, `idObject`, and `HWND`. `AddObjectNotification()` lazily creates a `HASHLIST` and an object-id key, then stores a listener. `ClearObjectNotifications()` removes all registrations for a window. `TestForNotifications()` builds an `ASIDLIST` for watched objects and calls `RefreshCachedProperties()`. `NotifyObjectListeners()` posts `WM_ASC_NOTIFY_OBJECT`. `SetActionNotification()` manages a growable `HWND` array, and `NotifyActionListeners()` posts copied `ASACTION` records through `WM_ASC_NOTIFY_ACTION`.

Control flow: object notification starts with UI registration, then periodic or explicit refresh checks call `TestForNotifications()`. Cache refresh side effects eventually call `NotifyObjectListeners()`, which filters by object and cell before posting to live windows. Action notifications are more direct: server action callbacks are copied into heap `ASACTION` objects and posted to every valid listener slot.

State and persistence: all state is process-local static memory under `asc_Enter()`/`asc_Leave()`: a listener hash list, an object-id hash key, and a sparse action-listener array. Nothing persists across process lifetime.

Dependencies/integration: depends on `TaAfsAdmSvrClientInternal.h`, AfsAppLib allocation/`REALLOC`, `HASHLIST`, RPC/admin-client cache functions, `ASIDLIST`, and Windows `PostMessage`/`IsWindow`.

Risks and test signals: `ClearObjectNotifications()` removes while enumerating the hash list, so iterator validity is important. `TestForNotifications()` creates an `ASIDLIST` without visibly freeing it in this file, relying on client-library ownership conventions. Action posts transfer heap-allocated `ASACTION` ownership to recipients; tests should verify recipients free it. Useful tests register multiple windows per object, destroy a listener window before notification, clear registrations, and verify action start/finish messages carry independent copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.cpp -->
