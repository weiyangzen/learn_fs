# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.cpp

Purpose: implements standalone server windows and the shared tab-container behavior also used by the main preview pane. It coordinates opening/closing server windows, tab creation, server selection, keyboard routing, and persistence of per-server window positions.

Important APIs/functions: public functions include `Server_Open`, `Server_Close`, `Server_CloseAll`, `Server_PrepareTabControl`, `Server_GetCurrentTab`, `Server_SelectServer`, `Server_ForceRedraw`, `Server_DisplayTab`, `Server_SaveRect`, and keyboard helpers. `Server_DlgProc` is the standalone server window procedure. `Server_SubclassTabControlProc` resizes the active child tab. `CHILDTABINFO` maps filesets, aggregates, and services to titles/images.

Control flow: opening first ensures the server is monitored if `gr.fOpenMonitors` allows it, then creates `IDD_SERVER`, selects the server, restores a previous rectangle if present, and shows the window. Closing saves position and optionally toggles monitoring off under active subset preferences. Tab display destroys the previous child dialog and creates the requested child dialog under the tab control, then posts `WM_SERVER_CHANGED` to refresh data.

State and persistence: per-server `SERVER_PREF.rLast` and `fOpen` are updated asynchronously through `taskSVR_SETWINDOWPOS`; `gr.rServerLast` stores the last standalone server geometry. `PropCache` maps server identities to HWNDs.

Dependencies/integration: depends on tab dialogs from `set_tab.h`, `agg_tab.h`, `svc_tab.h`, display helpers, context-command routing, `StartTask`, and `StorePreferences` through `task.cpp`.

Risks: `procTabControl` is static global, so subclassing multiple tab controls can conflict if windows overlap lifetimes. Keyboard code assumes focus belongs to expected tab children. `Server_Open` dereferences `prWindow` without null checks. Tests should cover preview and standalone tab switching, window-position persistence, monitor toggling with subsets, accelerator commands, and multiple server windows.
