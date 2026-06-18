# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.cpp

Purpose: Implements the server host/admin list editor, with add/remove UI and save task dispatch.

Important APIs/functions: `Server_Hosts` opens/focuses a cached property sheet per server. `Server_Hosts_DlgProc` handles list lifecycle. `Server_Hosts_OnInitDialog` initializes FastList image lists and starts `taskSVR_HOSTLIST_OPEN`. `Server_Hosts_OnEndTask_ListOpen` stores and displays `LPHOSTLIST`. `Server_Hosts_OnApply` increments host-list refcount and starts `taskSVR_HOSTLIST_SAVE`. Add/remove helpers mutate the in-memory list. `Server_AddHost_DlgProc` captures a host name.

Control flow: The host list is loaded asynchronously. Until loaded, list/add/remove are disabled. Add opens a modal dialog, avoids duplicate visible entries, calls `AfsClass_HostList_AddEntry` if new, and selects the item. Remove deletes all selected entries from both list model and UI. Apply saves only if list is enabled.

State and persistence: `SVR_HOSTS_PARAMS` owns `LPHOSTLIST`; free uses `AfsClass_HostList_Free`. Saving persists remote server host list through task. The host list has reference counting; apply increments before handing to task.

Dependencies/integration: Uses AFS class host-list APIs, prop cache, FastList, image lists, and task dispatch.

Risks: `memset(pAdd, 0x00, sizeof(pAdd))` clears only pointer size, not `SVR_ADDHOST_PARAMS`; subsequent fields are set enough for current use except tail bytes remain uninitialized. Failed `taskSVR_HOSTLIST_OPEN` may leave `lpList` null with no visible error in this file. Add dialog validates only nonempty host string.

Test signals: Load failure, duplicate add case-insensitive, add new host, remove multiple selected hosts, apply refcount behavior, cached sheet focus, and memory analysis for the `sizeof(pAdd)` initialization bug.
