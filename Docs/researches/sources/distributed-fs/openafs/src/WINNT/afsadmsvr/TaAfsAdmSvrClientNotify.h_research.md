<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.h

Purpose: declares the client-library notification helpers implemented by `TaAfsAdmSvrClientNotify.cpp`.

Important APIs/types/functions: exposes `AddObjectNotification()`, `ClearObjectNotifications()`, `TestForNotifications()`, `NotifyObjectListeners()`, `SetActionNotification()`, and `NotifyActionListeners()`. `TestForNotifications()` has a default `idObject = 0`, allowing a caller to refresh all registered objects in a cell.

Control flow: callers include this header to register UI `HWND`s, clear registrations during window teardown, trigger cache-refresh checks, and dispatch action callbacks. The header deliberately keeps storage details private.

State and persistence: no state is declared here. State is private to the implementation file and protected by the client critical section.

Dependencies/integration: requires the surrounding admin client types (`ASID`, `LPASACTION`) and Windows `HWND`; it is normally included through the client internal header graph.

Risks and test signals: because the API exposes raw `HWND` handles and posted message ownership, tests should cover listener teardown and posted action memory lifetime. Header-level compile tests should verify default parameters remain compatible with C++ callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.h -->
