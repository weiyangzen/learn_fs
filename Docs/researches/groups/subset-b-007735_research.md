# subset-b-007735 Research

Grouped research for the requested OpenAFS Windows Server Manager and Account Manager files. Each section is source-tree aligned and wrapped for reconciliation into the final per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.cpp

Purpose: implements the AFS Server Manager "Salvage Volumes" workflow. It owns the salvage selection dialog, an advanced-options expander, async population of server/aggregate/fileset combo boxes, dispatch of the salvage task, and a separate results dialog for displaying salvager output.

Important APIs/functions: `Server_Salvage` is the public entry point and uses `PropCache_Search/Add/Delete` to keep one dialog per target identity. `Server_Salvage_DlgProc` handles help, `WM_INITDIALOG`, `WM_ENDTASK`, and commands. `Server_Salvage_OnOK` builds `SVR_SALVAGE_PARAMS` and starts `taskSVR_SALVAGE`. `Server_Salvage_Results_DlgProc`, `Server_Salvage_Results_OnInitDialog`, and `Server_Salvage_OnEndTask_Salvage` render the result title and log text.

Control flow: initialization disables selection controls, starts `taskSVR_ENUM_TO_COMBOBOX`, then chains aggregate enumeration and fileset enumeration through `WM_ENDTASK`. The all-aggregates/all-filesets checkboxes gate which combo boxes are enabled. On OK, the chosen target is resolved from fileset to aggregate to server, and the task scheduler posts completion to the hidden results dialog.

State and persistence: dialog state lives in controls and `DWLP_USER`; no registry writes occur here. The result dialog is shown only after successful completion. The code registers the original dialog with `AfsAppLib_RegisterModelessDialog`, but the result dialog is the actual task reply window.

Dependencies/integration: depends on `svrmgr.h`, `svr_salvage.h`, `propcache.h`, AfsAppLib dialog helpers, `StartTask`, Fast/Combo helper APIs, and the task implementation in `task.cpp` that calls `AfsClass_Salvage`.

Risks: `Server_Salvage_OnEndTask_EnumAggregates` assumes `lpi` is non-null when comparing `lpi->GetServer()`, though the public entry point expects a valid identity. `WM_COMMAND` intentionally or accidentally falls through from `IDOK` to `IDCANCEL`, destroying the dialog after dispatch. The `WM_CTLCOLOREDIT` handler creates a brush per message without caching or deleting it. Tests should exercise chained enumeration, all-scope checkbox behavior, parameter mapping for advanced options, failures from `taskSVR_SALVAGE`, and missing/unreadable salvage logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.h

Purpose: declares the public interface and parameter packet for server/aggregate/fileset salvage operations in AFS Server Manager.

Important API/types: `SVR_SALVAGE_PARAMS` carries `LPIDENT lpiSalvage`, optional temp directory and log file buffers, concurrency count, and boolean salvager flags: force, readonly, inode logging, root inode logging, directory rebuild, and block-read mode. `Server_Salvage(LPIDENT lpi)` opens the modeless salvage UI for the selected identity.

Control flow contract: callers invoke `Server_Salvage` from command/menu handlers with a server, aggregate, or fileset identity. The UI fills this struct and passes it as `lpUser` to `taskSVR_SALVAGE`; `Task_Svr_Salvage` owns deletion after calling `AfsClass_Salvage`.

State and persistence: the struct is transient task input only. It stores fixed-size paths and flags but no persistent settings.

Dependencies/integration: depends on common AFS Manager types from `svrmgr.h`, especially `LPIDENT`, `MAX_PATH`, and task dispatch. Included by `svr_salvage.cpp` and `task.cpp`.

Risks/test signals: all path buffers must be populated with bounded `GetDlgItemText`; empty strings are interpreted later as `NULL`. Tests should verify that each UI option maps to the corresponding struct field and that ownership is never shared after dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.cpp

Purpose: implements the AFS Server Manager server-security property sheet, covering server administrator lists and BOS encryption keys. It also implements create-key input parsing, random-key retrieval, and key display formatting.

Important APIs/functions: `Server_Key_SetDefaultView` initializes `gr.viewKey`. `Server_Security` opens or focuses a modeless two-tab property sheet. `Server_Lists_*` functions load, display, add, remove, and save the admin list. `Server_Keys_*` functions load, display, create, and delete server keys. `FormatServerKey` encodes an `ENCRYPTIONKEY` as backslash-prefixed octal triplets, and `ScanServerKey` reverses that format. `CreateKey_*` manages the modal key creation dialog.

Control flow: `Server_Security` allocates one `SVR_SECURITY_PARAMS` shared by both tabs and ref-counted across sheet lifetime. The list tab starts `taskSVR_ADMLIST_OPEN`; the key tab starts `taskSVR_KEYLIST_OPEN`. User edits mutate loaded `AfsClass` list structures in memory and dispatch save/create/delete tasks. Key create chooses the next version by scanning in-use keys and either sends a string password or raw parsed key data.

State and persistence: the shared params retain `LPADMINLIST` and `LPKEYLIST` until both tabs are destroyed. Key list column layout is persisted through `gr.viewKey` on destroy. Admin-list save increments `cRef` before dispatch so task-side notification/free behavior remains safe.

Dependencies/integration: uses property sheets, `PropCache`, `display.h`, `AfsAppLib_ShowBrowseDialog`, `AfsClass_AdminList_*`, `AfsClass_KeyList_*`, `AfsClass_AddKey/DeleteKey/GetRandomKey`, and the task queue.

Risks: `Server_Keys_OnEndTask_ListOpen` calls `Server_Lists_OnSelect` instead of `Server_Keys_OnSelect`, so the remove button for keys may not refresh correctly. `CreateKey_DlgProc` stores params in a static variable, making concurrent modal instances unsafe even if UI normally prevents them. `ScanServerKey` accepts any three digits after a backslash and truncates to byte, so invalid octal-like values are not rejected. Tests should cover duplicate admin entries, removal of multiple admins, key format round trips, random-key failure disabling, key-version selection, and property-sheet ref-count teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.h

Purpose: declares server-security data structures and entry points for the AFS Server Manager security UI.

Important API/types: `SERVERKEYCOLUMN` defines version, data, and checksum columns. `SERVERKEYCOLUMNS` provides resource IDs and default widths, including right justification for checksum. `KEY_CREATE_PARAMS` carries the target server, version, optional string, and raw `ENCRYPTIONKEY`; `KEY_DELETE_PARAMS` carries target server and version. Public functions are `Server_Key_SetDefaultView` and `Server_Security`.

Control flow contract: `Server_Security` owns UI creation and passes key structs to `taskSVR_KEY_CREATE` or `taskSVR_KEY_DELETE`. `Server_Key_SetDefaultView` is called during global preference default initialization in `svrmgr.cpp`.

State and persistence: this header defines only transient task structs and column defaults. Persistent state is stored in `GLOBALS_RESTORED.viewKey`.

Dependencies/integration: depends on `LPIDENT`, `ENCRYPTIONKEY`, `VIEWINFO`, `cchRESOURCE`, and resource IDs. Included by startup, security implementation, and task code.

Risks/test signals: `SERVERKEYCOLUMNS` is a non-`extern` static definition in a header, which intentionally creates a private copy per translation unit; adding mutable fields would be risky. Tests should verify view defaults stay in sync with resource columns and task packet fields are initialized before dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.cpp

Purpose: implements the confirmation dialog for synchronizing VLDB entries with a selected server or aggregate.

Important APIs/functions: `Server_SyncVLDB` opens/focuses the modeless dialog using `PropCache`. `Server_SyncVLDB_DlgProc` handles initialization, ghost-status task completion, OK/cancel, and cleanup. `Server_SyncVLDB_OnInitDialog` formats warning text for server or aggregate scope. `Server_SyncVLDB_OnOK` creates `SVR_SYNCVLDB_PARAMS` with `fForce = TRUE` and dispatches `taskSVR_SYNCVLDB`.

Control flow: server-scoped sync shows immediately. Aggregate-scoped sync first starts `taskAGG_FIND_GHOST`; if the aggregate lacks a server entry, the dialog shows an error and closes, because syncing an unexported/offline aggregate would be unsafe. Otherwise it shows the confirmation UI.

State and persistence: state is transient in `DWLP_USER` and the task packet. There are no preference writes. `PropCache` ensures a single sync dialog per identity.

Dependencies/integration: depends on `svrmgr.h`, `svr_syncvldb.h`, `propcache.h`, string resources, `StartTask`, and `Task_Svr_SyncVLDB` in `task.cpp`, which calls `AfsClass_SyncVLDB`.

Risks/test signals: OK destroys the dialog immediately after dispatch and uses no reply window, so task failures surface through global error dialogs rather than inline UI. Aggregate ghost detection relies on `GHOST_HAS_SERVER_ENTRY`; tests should cover server path, valid aggregate path, ghost aggregate rejection, forced flag mapping, and task failure error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.h

Purpose: declares the task parameters and public UI entry point for VLDB synchronization.

Important API/types: `SVR_SYNCVLDB_PARAMS` contains `LPIDENT lpi`, which may identify a server or aggregate, and `BOOL fForce`, which controls forced synchronization. `Server_SyncVLDB(LPIDENT lpi)` opens the confirmation dialog.

Control flow contract: UI code creates this struct on OK and passes it to `taskSVR_SYNCVLDB`; `Task_Svr_SyncVLDB` deletes it after calling `AfsClass_SyncVLDB`.

State and persistence: transient task input only, no stored preferences.

Dependencies/integration: requires common Manager identity types from `svrmgr.h`; included by the dialog implementation and task implementation.

Risks/test signals: callers must pass a server or aggregate identity that remains valid across async dispatch. Tests should assert `fForce` defaults expected by the UI and task-side ownership is single-use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.cpp

Purpose: implements the "Uninstall File" dialog for removing a named file from a selected AFS server.

Important APIs/functions: `Server_Uninstall` is the public entry point and enforces a single global uninstall dialog via `PropCache_Search(pcSVR_UNINSTALL, NULL)`. `Server_Uninstall_DlgProc` manages help, task completions, commands, and cleanup. `Server_Uninstall_OnInitDialog` starts `taskSVR_ENUM_TO_COMBOBOX`. `Server_Uninstall_EnableOK` validates that a server and file name are present. `Server_Uninstall_OnOK` builds `SVR_UNINSTALL_PARAMS` and starts `taskSVR_UNINSTALL`.

Control flow: opening allocates a params struct with optional initial server and empty filename. The dialog disables server selection and OK while server enumeration runs. Once enumeration completes, the dialog enables server selection and reevaluates OK. OK dispatches without a reply window and closes the dialog.

State and persistence: selected server and file path are transient. `DWLP_USER` owns the init params until `WM_DESTROY`, where it is deleted. No registry/preferences are written.

Dependencies/integration: uses AfsAppLib help/dialog helpers, `StartTask`, `SVR_ENUM_TO_COMBOBOX_PACKET`, `PropCache`, and `Task_Svr_Uninstall`, which calls `AfsClass_UninstallFile`.

Risks/test signals: the dialog is global rather than per-server, so a second request focuses the existing instance even if a different server was intended. The init enum packet is not zeroed, though both fields are set. Failures happen after dialog close via task-side `ErrorDialog`. Tests should cover initial-server selection, empty filename disabling, server enum failures, and error text containing the base filename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.h

Purpose: declares the uninstall-file task packet and public dialog entry point.

Important API/types: `SVR_UNINSTALL_PARAMS` carries the target `LPIDENT lpiServer` and remote filename/path in `szUninstall[MAX_PATH]`. `Server_Uninstall(LPIDENT lpiServer = NULL)` starts the UI, optionally preselecting a server.

Control flow contract: the dialog and task code allocate this struct for different lifetimes: one instance is dialog state during initialization, and another is task input on OK. `Task_Svr_Uninstall` owns deletion for task input.

State and persistence: transient only; no persistent preferences or cached file lists.

Dependencies/integration: depends on Manager identity and path constants; included by UI and task code.

Risks/test signals: remote filenames longer than `MAX_PATH - 1` are truncated by UI reads. Tests should check default argument callers and that an empty `szUninstall` is never dispatched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.cpp

Purpose: implements standalone server windows and the shared tab-container behavior also used by the main preview pane. It coordinates opening/closing server windows, tab creation, server selection, keyboard routing, and persistence of per-server window positions.

Important APIs/functions: public functions include `Server_Open`, `Server_Close`, `Server_CloseAll`, `Server_PrepareTabControl`, `Server_GetCurrentTab`, `Server_SelectServer`, `Server_ForceRedraw`, `Server_DisplayTab`, `Server_SaveRect`, and keyboard helpers. `Server_DlgProc` is the standalone server window procedure. `Server_SubclassTabControlProc` resizes the active child tab. `CHILDTABINFO` maps filesets, aggregates, and services to titles/images.

Control flow: opening first ensures the server is monitored if `gr.fOpenMonitors` allows it, then creates `IDD_SERVER`, selects the server, restores a previous rectangle if present, and shows the window. Closing saves position and optionally toggles monitoring off under active subset preferences. Tab display destroys the previous child dialog and creates the requested child dialog under the tab control, then posts `WM_SERVER_CHANGED` to refresh data.

State and persistence: per-server `SERVER_PREF.rLast` and `fOpen` are updated asynchronously through `taskSVR_SETWINDOWPOS`; `gr.rServerLast` stores the last standalone server geometry. `PropCache` maps server identities to HWNDs.

Dependencies/integration: depends on tab dialogs from `set_tab.h`, `agg_tab.h`, `svc_tab.h`, display helpers, context-command routing, `StartTask`, and `StorePreferences` through `task.cpp`.

Risks: `procTabControl` is static global, so subclassing multiple tab controls can conflict if windows overlap lifetimes. Keyboard code assumes focus belongs to expected tab children. `Server_Open` dereferences `prWindow` without null checks. Tests should cover preview and standalone tab switching, window-position persistence, monitor toggling with subsets, accelerator commands, and multiple server windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.h

Purpose: declares the server-window and preview-pane interface used throughout AFS Server Manager.

Important API/types: `SERVERWINDOW_PREVIEWPANE` aliases `g.hMain` so shared server-tab code can treat the main preview pane as a server window. `SVR_SETWINDOWPOS_PARAMS` carries an identity, window rectangle, and open/closed flag for asynchronous preference updates. Public functions cover open/close, tab preparation/display, server selection lookup, redraw/uncover, and keyboard commands.

Control flow contract: callers use `Server_Open` after retrieving a saved rectangle through `taskSVR_GETWINDOWPOS`; close paths call `Server_SaveRect` indirectly. Child dialogs use `Server_GetServerForChild` and `Server_GetWindowForChild` to resolve context.

State and persistence: this header exposes the packet used to persist `SERVER_PREF.rLast` and `fOpen`.

Dependencies/integration: depends on `CHILDTAB`, `LPIDENT`, `RECT`, and global `g` from `svrmgr.h`; used by main window, command handlers, and task code.

Risks/test signals: the preview-pane macro hides a dependency on global state. Tests should verify child-to-server resolution works for both preview and standalone windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.cpp

Purpose: contains the Windows entry point and application lifecycle for AFS Server Manager.

Important APIs/functions: `WinMain` converts the ANSI command line and delegates to `InitApplication`, then runs `AfsAppLib_MainPump` and `ExitApplication`. `InitApplication` loads locale resources, enforces a single main window, initializes the AfsAppLib task queue, restores or defaults global UI settings, initializes `AfsClass`, creates notification dispatch, registers dialog classes, parses command-line options, creates the main dialog, and optionally prompts for a cell. `Quit` persists settings and decides whether to hide while actions remain active. `PumpMessage` applies accelerators and filters memory-manager messages. `StartThread` wraps `CreateThread`.

Control flow: startup builds `GLOBALS g` and `GLOBALS_RESTORED gr` before any dialogs. Defaults initialize all view definitions and behavior flags. Once `Main_DialogProc` exists, cell selection can proceed through `OpenCellDialog` or command-line opening.

State and persistence: `RestoreSettings`/`StoreSettings` serialize `gr` under `HKCU\Software\OpenAFS\AFS Server Manager`. `Quit` stores main-window placement and server-list view before leaving. `g` holds handles, selected cell identity, current subset, and credentials.

Dependencies/integration: depends on Windows, Winsock/Roken/OpenAFS config headers, AfsAppLib, AfsClass, resource modules, command-line parsing, notifications, credentials, propcache, and every default-view initializer.

Risks: `StartThread` never closes the thread handle after `CreateThread`, causing handle leaks on repeated use. Startup references `opLOOKUPERRORCODE`, which is not declared in the shown `cmdline.h` subset and must come from included headers or conditional code. Tests should cover first-run defaults, settings version migration, duplicate-instance activation, AfsClass initialization failures, command-line paths, and quit behavior with active actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.h

Purpose: central umbrella header for AFS Server Manager, defining common constants, persistent preference structs, globals, includes, and core lifecycle helpers.

Important API/types: defines registry locations, size constants, pending fileset suffixes, `CHILDTAB`, `DISPLAYINFO`, `SERVER_PREF`, `SERVICE_PREF`, `AGGREGATE_PREF`, `FILESET_PREF`, `ICONVIEW`, `GLOBALS`, and `GLOBALS_RESTORED`. Declares global `g` and `gr`, plus `Quit`, `PumpMessage`, and `StartThread`.

Control flow contract: most source files include this header to share app state, resource IDs, task interfaces, help helpers, and preference structures. Preference version macros (`wVerSERVER_PREF`, etc.) are used by save/restore helpers to validate persisted binary blobs.

State and persistence: the structs here are the durable state model: global window/view preferences in `GLOBALS_RESTORED`, and per-object alert/view/status preferences on server/service/aggregate/fileset identities. Registry keys are under `HKCU`.

Dependencies/integration: includes `windows.h`, `AfsAppLib.h`, `AfsClass.h`, resource/help headers, and major manager modules. It later includes `task.h` and `helpfunc.h`, making it a broad dependency root.

Risks/test signals: binary persistence structs are versioned but layout changes can break old settings if versions are not bumped. Header breadth increases coupling and rebuild scope. Tests should check default initialization, restore fallback when versions mismatch, and object preference save/load compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.cpp

Purpose: central asynchronous task implementation for AFS Server Manager. It adapts GUI task packets to `AfsClass_*` operations, refreshes object state, populates controls, saves preferences, and reports results/errors back through `TASKPACKETDATA` and optional reply windows.

Important APIs/functions: `CreateTaskPacket`, `PerformTask`, and `FreeTaskPacket` are registered with `AfsAppLib_InitTaskQueue`. `PerformTask` is a large switch over `TASK`. Key functions for this subset include `Task_OpenCell`, `Task_OpenedCell`, `Task_ClosedCell`, `Task_Refresh`, `Task_Svr_Enum_To_ComboBox`, `Task_Svr_GetWindowPos`, `Task_Svr_SetWindowPos`, `Task_Svr_SyncVLDB`, `Task_Svr_Salvage`, `Task_Svr_Uninstall`, `Task_Svr_AdmList_*`, `Task_Svr_Key*`, `Task_Agg_Enum_To_ComboBox`, `Task_Agg_Find_Ghost`, and `Task_Set_Enum_To_ComboBox`.

Control flow: UI code calls `StartTask` with a task id, reply HWND, and owned `lpUser` packet. The task executes in the app task queue, sets `ptp->rc/status`, optionally fills `TASKPACKETDATA`, often deletes `lpUser`, and returns to the scheduler, which posts `WM_ENDTASK` to the reply window. No-reply tasks show errors directly where appropriate.

State and persistence: modifies global cell/subset state, object monitor state, per-server window positions, server/service/aggregate/fileset preferences, and key/admin/host list references. `Task_OpenedCell` refreshes the new cell and starts alert scouting. `Task_Svr_SetWindowPos` writes `SERVER_PREF` via `StorePreferences`.

Dependencies/integration: pulls in nearly every Server Manager module plus `AfsClass`, alert scout, display update helpers, credentials, subset management, property packets, and optional debug export support.

Risks: ownership conventions are task-specific; some packets are deleted, some intentionally remain caller-owned, and bugs can become use-after-free or leaks. Many tasks show UI errors from worker context when no reply window is present. `Task_Svr_Key_Create` overwrites add-key failure context by loading the key list and using the same status path. Tests should cover packet ownership, reply/no-reply error handling, cell open/close refresh, preference persistence, security list ref-counting, salvage/sync/uninstall calls, and ghost/VLDB refresh logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.h

Purpose: declares the AFS Server Manager async task protocol.

Important API/types: packet structs wrap UI-control population and cell-opening requests: `MENUTASK`, server/aggregate/fileset enum packets, `SET_LOOKUP_PACKET`, `OPENCELL_PACKET`, and `SUBSET_TO_LIST_PACKET`. The `TASK` enum lists every task id and expected `lpUser` type. `TASKPACKETDATA` is the shared return payload containing identities, text, status structs, preferences, admin/host/key lists, ghost flags, and other task results. `TASKDATA(ptp)` casts `pReturn`.

Control flow contract: `CreateTaskPacket`, `PerformTask`, and `FreeTaskPacket` are installed in the AfsAppLib task queue. Callers must pass the exact packet type documented in the enum comments and inspect `TASKDATA` only after completion.

State and persistence: no direct persistence, but many packet types trigger persistent changes in `task.cpp`.

Dependencies/integration: depends on all common manager types pulled through `svrmgr.h`, plus many forward-visible packet types from included feature headers.

Risks/test signals: enum comments are the main type-safety guard; C++ cannot enforce the `lpUser` variant. Adding fields to `TASKPACKETDATA` requires updating `FreeTaskPacket` for owned allocations. Tests should verify each new task has a switch case and correct cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.cpp

Purpose: implements the main AFS Server Manager window, including server list, optional preview pane, action-window toggling, notification handling, refresh animation, keyboard traversal, and context-menu routing.

Important APIs/functions: `Main_DialogProc` is the main dialog procedure. `Main_OnNotifyFromDispatch` translates AfsClass notifications into display/task actions. `Main_OnOpenServers_ThreadProc` reopens persisted server windows. `Main_Redraw_ThreadProc` refreshes cell/server data. `Main_OnPreviewPane`, `Main_OnServerView`, `Main_SetServerViewMenus`, `Main_CreateTabControl`, `Main_DeleteTabControl`, `Main_DisplayTab`, and `Main_RearrangeChildren` manage the UI layout. `Main_StartWorking`, `Main_StopWorking`, and `Main_AnimateIcon` manage the busy indicator.

Control flow: on init the main dialog stores `g.hMain`, restores geometry, subclasses the server list, creates preview UI if enabled, subscribes for cell notifications, starts a redraw thread, and starts a dispatch timer. Commands update preview layout, server view, columns, actions, credentials, or delegate to `StartContextCommand`. Server-list selection updates the preview pseudo-window; double-click either opens properties or a standalone server window based on preferences.

State and persistence: uses and mutates `gr.rMain`, `gr.rMainPreview`, `gr.diHorz/diVert`, `gr.fPreview`, `gr.fVert`, `gr.fActions`, `gr.tabLast`, icon views, and credentials in `g.hCreds`. Preferences are ultimately stored by `Quit`.

Dependencies/integration: integrates display, command, notification dispatch, server window, property dialogs, credentials, column customization, action window, and AfsClass refresh.

Risks: background threads call UI helpers and AfsClass with shared globals; thread/UI boundaries depend on legacy assumptions. `LOWORD/HIWORD` on screen coordinates can mishandle negative multi-monitor coordinates. `procServers` is global subclass state. Tests should cover preview layout toggles, persisted view restoration, notification-driven redraw, expired credentials checks, double-click behavior, column dialog routing, and active-action quit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.h

Purpose: declares the main-window API for AFS Server Manager.

Important API/functions: `Main_DialogProc`, preview and server-view commands, menu refresh helpers, tab-child lookup, redraw thread entry, `GetTabDialog`, busy animation start/stop, icon animation, and server-view menu update.

Control flow contract: `svrmgr.cpp` passes `Main_DialogProc` to `ModelessDialog`; other modules call these helpers to update global UI state and invoke refreshes. `Main_Redraw_ThreadProc` is intended for `StartThread`.

State and persistence: the functions operate on global `g` and `gr`; the header itself declares no state. `WORKING_FPS` defines animation target cadence used by animation helpers/libraries.

Dependencies/integration: depends on Windows types and global definitions from `svrmgr.h`; used by startup, actions, server windows, and command handlers.

Risks/test signals: functions expose broad global UI mutation. Tests should verify calls are made on expected UI/thread contexts and menu states track `gr` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/TaAfsUsrMgr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/TaAfsUsrMgr.h

Purpose: central umbrella header for AFS Account Manager, analogous to Server Manager's `svrmgr.h`.

Important API/types: defines common size constants, registry paths under `HKCU\Software\OpenAFS\AFS Account Manager`, help filename, `ICONVIEW`, `GLOBALS`, and `GLOBALS_RESTORED`. `GLOBALS` stores app/window handles, admin-server client id, active cell ASID, credentials, and search patterns. `GLOBALS_RESTORED` stores main/action window placement, views for users/groups/machines/actions, icon modes, warning/show flags, refresh rate, last tab, create defaults, and user search parameters. Declares global `g`, `gr`, `Quit`, `PumpMessage`, and `StartThread`.

Control flow contract: almost every Account Manager source includes this header to get shared state, task prototypes, display/general helpers, property dialogs, and error data.

State and persistence: defines the binary settings state persisted by the Account Manager. Version `wVerGLOBALS_RESTORED` guards restore compatibility.

Dependencies/integration: includes `TaLocale`, `TaAfsAdmSvrClient`, `AfsAppLib`, resource/help headers, user/group property headers, `task.h`, `display.h`, `general.h`, and `errdata.h`.

Risks/test signals: broad inclusion couples unrelated modules and makes global state easy to mutate. Struct layout changes require version bumps and default initialization. Tests should cover settings restore defaults, command-line opening, active cell/client id initialization, and view persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/TaAfsUsrMgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.cpp

Purpose: implements the Account Manager action/progress window that lists active admin-server operations and elapsed time.

Important APIs/functions: `Actions_SetDefaultView` initializes action list columns. `Actions_OpenWindow`, `Actions_CloseWindow`, and `Actions_WindowToTop` manage the modeless action window. `Actions_DlgProc` handles column notifications, geometry, timer refreshes, `taskGET_ACTIONS`, and close. `Actions_OnNotify` consumes async action notifications. `Actions_OnEndTask_GetActions` initializes the stored action list. `Actions_Refresh` rebuilds the FastList display. `GetActionDescription` maps `ASACTION` variants to localized descriptions using cached object properties.

Control flow: opening the window restores `gr.viewAct` and `gr.rActions`, starts a one-second timer, and requests current actions. Notifications add/remove entries from `l.pActionList`; finished refresh actions trigger `Display_PopulateList`. Refresh converts stored start ticks to elapsed `SYSTEMTIME` text and updates summary text.

State and persistence: static `l` stores HWND and `LPASACTIONLIST`. `gr.fShowActions`, `gr.rActions`, and `gr.viewAct` persist user choice/placement/view. Active durations are normalized from seconds-active to start tick via `FixActionTime`.

Dependencies/integration: uses Afs admin-server client APIs (`asc_ActionList*`, `asc_ObjectPropertiesGet_Fast`), FastList/display helpers, main menu state, task queue, and localized resources.

Risks: `GetTickCount` wraparound and mutation of `csecActive` from seconds to tick origin make field semantics context-dependent. The action list is static global and not protected against concurrent notification/timer access. Tests should cover action add/remove notifications, elapsed formatting, refresh completion side effects, window topmost behavior, and cleanup of transferred action lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.h

Purpose: declares the Account Manager action-window interface.

Important API/functions: `Actions_SetDefaultView` initializes a `VIEWINFO`; `Actions_OpenWindow`, `Actions_CloseWindow`, and `Actions_WindowToTop` manage the modeless progress window; `Actions_OnNotify` is the external notification hook for admin-server actions.

Control flow contract: startup/default initialization calls `Actions_SetDefaultView`; menus call open/close; the notification plumbing passes action start/finish data to `Actions_OnNotify`.

State and persistence: functions operate on static state in `action.cpp` and global `gr.viewAct`, `gr.rActions`, `gr.fShowActions`.

Dependencies/integration: depends on `LPVIEWINFO`, `WPARAM`, and `LPARAM` from the umbrella header.

Risks/test signals: callers must transfer ownership of `LPASACTION` notifications because `Actions_OnNotify` deletes them. Tests should verify ownership and menu state after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.cpp

Purpose: implements a reusable modal browse dialog for selecting AFS Account Manager users and/or groups, with pattern search, optional exclusion list filtering, and name-to-ASID translation.

Important APIs/functions: `ShowBrowseDialog` chooses the dialog template and returns selected objects. `Browse_DlgProc` handles delayed search timers, commands, async task completions, and list notifications. `Browse_OnInitDialog` configures title/prompt/cell/type controls and initial list population. `Browse_UpdateDialog` starts `taskUSER_ENUM` or `taskGROUP_ENUM`. `Browse_OnEndTask_EnumObjects` populates the FastList. `Browse_OnOK` starts `taskLIST_TRANSLATE`; `Browse_OnEndTask_Translate` transfers the selected ASID list back to the caller.

Control flow: typing in the pattern field starts a 650ms debounce timer before requery. While querying, the list shows a non-selectable "querying" row and `fQuerying` suppresses selection feedback. OK disables controls and translates typed names, allowing manual entry independent of visible list selection.

State and persistence: state is held in caller-owned `BROWSE_PARAMS`, including `fQuerying`, selected objects, and display name. No registry writes occur.

Dependencies/integration: uses `TaAfsUsrMgr.h`, `usr_col.h`, admin-server client APIs (`asc_CellNameGet_Fast`, `asc_ObjectPropertiesGet_Fast`, ASID list helpers), FastList, task queue, and localized resources.

Risks: `Browse_OnEndTask_EnumObjects` loops over `TASKDATA(ptp)->pAsidList` after only an outer success guard; if the task succeeds with a null list, it can dereference null. `fQuerying` is a boolean in the header but incremented/decremented as a counter. Multiple outstanding enum tasks can complete out of order and overwrite newer results. Tests should cover debounce ordering, skip-list filtering, multi-select formatting, manual translation failure, and ownership transfer of `pObjectsSelected`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.h

Purpose: declares the reusable Account Manager browse dialog parameter block and entry point.

Important API/types: `BROWSE_PARAMS` includes parent/help/title/prompt/check resources, type mask (`TYPE_USER`/`TYPE_GROUP`), optional objects-to-skip, output selected ASID list, multiple-selection flag, display name buffer, and internal query flag. `ShowBrowseDialog` returns `TRUE` only when a non-empty selected list is available.

Control flow contract: callers allocate and initialize `BROWSE_PARAMS`, call the modal dialog, then own `pObjectsSelected` on success. `fQuerying` is marked internal and reset by the implementation.

State and persistence: no persistent state; output is returned in the same struct.

Dependencies/integration: depends on `HWND`, resource ids, `ASOBJTYPE`, `LPASIDLIST`, `cchNAME`, and task/list helpers included elsewhere.

Risks/test signals: header declares `fQuerying` as `BOOL` despite counter-like use. Callers must free `pObjectsSelected`. Tests should check both one-type and two-type template selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.cpp

Purpose: implements the Account Manager cell properties sheet, currently focused on general cell id allocation limits.

Important APIs/functions: `Cell_ShowProperties` opens/focuses the modeless property sheet and selects a requested tab. `CellProp_General_DlgProc` handles sheet lifetime, help, notifications, apply, and dirty marking. `CellProp_General_OnInitDialog` registers object listening and formats the cell name. `CellProp_General_UpdateDialog` reads cell properties and updates spinners. `CellProp_General_OnApply` dispatches `taskCELL_CHANGE`.

Control flow: if a sheet for `g.idCell` is already open, `WindowList_Search` focuses it and optionally changes tab. Otherwise a property sheet is created with the general tab. The tab starts an `OBJECT_LISTEN` task for the cell and reacts to `WM_ASC_NOTIFY_OBJECT` by reloading current values.

State and persistence: no direct settings persistence. The persisted cell limits live in the AFS admin server/cell and are changed asynchronously through `CELL_CHANGE_PARAMS`. Window de-duplication is held in `WindowList`.

Dependencies/integration: uses admin-server client fast property reads, object-listen task, property sheet helpers, spinner helpers, `winlist.h`, and localized resources.

Risks: `asc_ObjectPropertiesGet_Fast` return value is ignored in update; stale/uninitialized `Properties` could populate spinners on failure. Spinner ranges use negative max constants for signed id semantics and should be validated carefully. Tests should cover open/focus behavior, listener registration/unregistration, property refresh notification, apply packet fields, and failed property reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.h

Purpose: declares the Account Manager cell property tab selector and entry point.

Important API/types: `CELLPROPTAB` provides `cptANY`, `cptPROBLEMS`, and `cptGENERAL`; `nCELLPROPTAB_MAX` documents the maximum tab count used for tab-index adjustment. `Cell_ShowProperties` opens or focuses the cell properties sheet, optionally selecting a target tab.

Control flow contract: callers pass `cptANY` for default selection or a specific tab. The implementation maps tab ids around optional/missing tabs.

State and persistence: none in the header; property changes are task-driven.

Dependencies/integration: depends on property sheet UI resources and global account-manager state in implementation.

Risks/test signals: tab index adjustment is fragile if tabs are added/removed without updating `nCELLPROPTAB_MAX`. Tests should cover all enum values against actual sheet composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.cpp

Purpose: parses AFS Account Manager command-line switches, connects to an admin server, optionally sets credentials, and optionally opens a cell without showing the normal cell dialog.

Important APIs/functions: `ParseCommandLine` recognizes `/cell`, `/remote`, `/user`, and `/password` with values. It validates duplicate/unknown/missing values, enforces user/password pairing, opens a remote or local admin server with `AfsAppLib_OpenAdminServer`, stores `g.idClient`, applies credentials through `AfsAppLib_SetCredentials`, and starts `taskOPENCELL` when `/cell` is supplied. `CommandLineHelp` formats syntax errors through `vMessage`.

Control flow: parsing walks the raw command line manually, supporting `-` or `/`, `:` or whitespace before values, and quoted values. Errors return `opCLOSEAPP`. Successful `/cell` dispatch returns `opNOCELLDIALOG`; otherwise normal startup continues.

State and persistence: static `aSWITCHES` is reset for presence each parse but retains value buffers overwritten as switches are found. Global `g.idClient` is set after admin-server connection, and credentials may update the admin-server session.

Dependencies/integration: uses `TaAfsUsrMgr.h`, `cmdline.h`, `AfsAppLib`, admin error constants, message resources, and Account Manager `taskOPENCELL`.

Risks: values are copied into fixed `cchRESOURCE` buffers without explicit bounds during parsing, so very long arguments can overflow. Static switch values are not cleared when absent, though presence flags control use. Passwords are stored in process memory as plain text. Tests should cover quoting, duplicate switches, missing values, remote/local failures, credential pairing, and long argument rejection/fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.h

Purpose: declares the Account Manager startup command-line result enum and parser entry point.

Important API/types: `CMDLINEOP` has `opCLOSEAPP`, `opNORMAL`, and `opNOCELLDIALOG`. `ParseCommandLine(LPTSTR pszCmdLine)` returns one of these to guide startup.

Control flow contract: application initialization calls `ParseCommandLine`; `opCLOSEAPP` aborts startup, `opNOCELLDIALOG` means an open-cell task has already been started, and `opNORMAL` proceeds to interactive cell selection.

State and persistence: no state in the header.

Dependencies/integration: depends on Windows/TCHAR types from the umbrella include chain.

Risks/test signals: parser side effects are not visible in the type signature: it opens admin-server connections, sets credentials, and may start tasks. Tests should verify startup handles each enum result correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.cpp

Purpose: implements the Account Manager "Columns" dialog for choosing visible columns and column order for users, groups, and machines lists.

Important APIs/functions: `ShowColumnsDialog` clones current `gr.viewUsr`, `gr.viewGrp`, and `gr.viewMch` into static working entries and opens a modal property sheet. `Columns_DlgProc` routes selection and apply commands. `Columns_OnSelect` rebuilds available/shown lists from the selected `VIEWINFO`. `Columns_OnInsert`, `Columns_OnDelete`, `Columns_OnMoveUp`, and `Columns_OnMoveDown` mutate the working `VIEWINFO`. `Columns_OnApply` commits changed views to the active display via `Display_RefreshView` or copies them into `gr`.

Control flow: when no default view is supplied, active tab selection decides the initial category. The first shown column is protected from deletion and movement above index 0, preserving the primary name column. Apply only commits categories marked `fChanged`.

State and persistence: static `COLUMNS` holds modal working copies and change flags. Persistent state lives in `gr.viewUsr`, `gr.viewGrp`, and `gr.viewMch`; active tab commits are pushed through display refresh. Final registry storage happens through broader app settings persistence.

Dependencies/integration: uses `TaAfsUsrMgr.h`, `columns.h`, `display.h`, property sheets, combo/list helpers, and `VIEWINFO`.

Risks: `Columns_OnInsert` computes `iShown` but does not use it, so inserted columns are appended rather than inserted after the current selection. `Columns_OnMoveDown` writes `aColumns[ii+1]` without independently checking `ii < nColsShown - 1`; the button-state guard usually prevents this, but direct calls would overrun. Tests should cover add/delete/reorder edge cases, protected first column behavior, active versus inactive tab apply, and persistence after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.cpp -->
