# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.cpp

Purpose: implements the Account Manager action/progress window that lists active admin-server operations and elapsed time.

Important APIs/functions: `Actions_SetDefaultView` initializes action list columns. `Actions_OpenWindow`, `Actions_CloseWindow`, and `Actions_WindowToTop` manage the modeless action window. `Actions_DlgProc` handles column notifications, geometry, timer refreshes, `taskGET_ACTIONS`, and close. `Actions_OnNotify` consumes async action notifications. `Actions_OnEndTask_GetActions` initializes the stored action list. `Actions_Refresh` rebuilds the FastList display. `GetActionDescription` maps `ASACTION` variants to localized descriptions using cached object properties.

Control flow: opening the window restores `gr.viewAct` and `gr.rActions`, starts a one-second timer, and requests current actions. Notifications add/remove entries from `l.pActionList`; finished refresh actions trigger `Display_PopulateList`. Refresh converts stored start ticks to elapsed `SYSTEMTIME` text and updates summary text.

State and persistence: static `l` stores HWND and `LPASACTIONLIST`. `gr.fShowActions`, `gr.rActions`, and `gr.viewAct` persist user choice/placement/view. Active durations are normalized from seconds-active to start tick via `FixActionTime`.

Dependencies/integration: uses Afs admin-server client APIs (`asc_ActionList*`, `asc_ObjectPropertiesGet_Fast`), FastList/display helpers, main menu state, task queue, and localized resources.

Risks: `GetTickCount` wraparound and mutation of `csecActive` from seconds to tick origin make field semantics context-dependent. The action list is static global and not protected against concurrent notification/timer access. Tests should cover action add/remove notifications, elapsed formatting, refresh completion side effects, window topmost behavior, and cleanup of transferred action lists.
