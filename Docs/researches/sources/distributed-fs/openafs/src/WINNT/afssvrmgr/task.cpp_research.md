# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.cpp

Purpose: central asynchronous task implementation for AFS Server Manager. It adapts GUI task packets to `AfsClass_*` operations, refreshes object state, populates controls, saves preferences, and reports results/errors back through `TASKPACKETDATA` and optional reply windows.

Important APIs/functions: `CreateTaskPacket`, `PerformTask`, and `FreeTaskPacket` are registered with `AfsAppLib_InitTaskQueue`. `PerformTask` is a large switch over `TASK`. Key functions for this subset include `Task_OpenCell`, `Task_OpenedCell`, `Task_ClosedCell`, `Task_Refresh`, `Task_Svr_Enum_To_ComboBox`, `Task_Svr_GetWindowPos`, `Task_Svr_SetWindowPos`, `Task_Svr_SyncVLDB`, `Task_Svr_Salvage`, `Task_Svr_Uninstall`, `Task_Svr_AdmList_*`, `Task_Svr_Key*`, `Task_Agg_Enum_To_ComboBox`, `Task_Agg_Find_Ghost`, and `Task_Set_Enum_To_ComboBox`.

Control flow: UI code calls `StartTask` with a task id, reply HWND, and owned `lpUser` packet. The task executes in the app task queue, sets `ptp->rc/status`, optionally fills `TASKPACKETDATA`, often deletes `lpUser`, and returns to the scheduler, which posts `WM_ENDTASK` to the reply window. No-reply tasks show errors directly where appropriate.

State and persistence: modifies global cell/subset state, object monitor state, per-server window positions, server/service/aggregate/fileset preferences, and key/admin/host list references. `Task_OpenedCell` refreshes the new cell and starts alert scouting. `Task_Svr_SetWindowPos` writes `SERVER_PREF` via `StorePreferences`.

Dependencies/integration: pulls in nearly every Server Manager module plus `AfsClass`, alert scout, display update helpers, credentials, subset management, property packets, and optional debug export support.

Risks: ownership conventions are task-specific; some packets are deleted, some intentionally remain caller-owned, and bugs can become use-after-free or leaks. Many tasks show UI errors from worker context when no reply window is present. `Task_Svr_Key_Create` overwrites add-key failure context by loading the key list and using the same status path. Tests should cover packet ownership, reply/no-reply error handling, cell open/close refresh, preference persistence, security list ref-counting, salvage/sync/uninstall calls, and ghost/VLDB refresh logic.
