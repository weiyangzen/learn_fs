# subset-b-007734 grouped research

This grouped report covers the OpenAFS Windows Server Manager files requested for subset `subset-b-007734`. Each file section is bounded with the required reconciliation markers and preserves the original source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.cpp

Purpose: Implements the fileset properties sheet, primarily the General tab for a selected fileset. It shows identity, timestamps, state, quota usage, lock/unlock controls, and fileset-full warning settings.

Important APIs/functions: `Filesets_ShowProperties` opens or focuses a cached modeless property sheet and can jump directly to the threshold/problems tab. `Filesets_General_DlgProc` is the Win32 dialog procedure. `Filesets_General_OnInitDialog` fills static identity fields and disables controls while data loads. `Filesets_General_OnEndTask_InitDialog` consumes `taskSET_PROP_INIT` results and refreshes all status controls. `Filesets_General_OnApply` packages warning settings in `SET_PROP_APPLY_PARAMS` for `taskSET_PROP_APPLY`. `Filesets_General_OnWarnings` enables/disables threshold controls based on radio/checkbox state.

Control flow: The property sheet is cached via `PropCache` under `pcSET_PROP`. On `WM_INITDIALOG`, it starts `taskSET_PROP_INIT` and registers `NotifyMe(WHEN_OBJECT_CHANGES, lpi, ...)`. On `WM_ENDTASK`, failed status refresh displays unknown values and an error dialog; successful refresh enables controls, formats timestamps, calculates alert/status text, shows quota via `Filesets_DisplayQuota` for read-write filesets, and replaces quota UI with a static explanation for replicas/clones. Command handling applies warning changes, opens the quota dialog, or starts lock/unlock tasks.

State and persistence: This file does not persist settings directly; it collects UI state and dispatches task packets. It reads server/fileset preferences from the task data (`lpsp`, `lpfp`) and relies on the task layer to save changes. It stores only dialog-local `LPIDENT` in `DWLP_USER` and uses `PropCache` for open-window identity.

Dependencies/integration: Depends on `svrmgr.h` task infrastructure, `set_quota.h` for quota display/editing, `svr_general.h` for default warning values, `propcache.h`, and `problems.h`. It integrates with alerts (`Alert_GetCount`), property sheets, AFS identity helpers, and notification dispatch.

Risks: UI depends on valid `TASKDATA(ptp)` members for both fileset status and preference pointers. The code replaces `IDC_SET_USAGEBAR` with a static child for non-RW filesets, so repeated init paths need the control lifetime to match dialog assumptions. Warning percentages use spinner values and `WORD`; bounds are enforced by spinner creation, not by apply-time validation.

Test signals: Exercise property sheet reuse, jump-to-threshold behavior, failed `taskSET_PROP_INIT`, read-write vs replica/clone filesets, lock/unlock/start quota commands, warning off/default/custom states, and object-change notifications while the dialog is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.h

Purpose: Declares the fileset property dialog entry point and the apply packet used when changing fileset warning preferences.

Important APIs/types: `SET_PROP_APPLY_PARAMS` carries `LPIDENT lpi`, whether fileset-full warnings are enabled, whether to use the server default threshold, and the custom warning percentage. `Filesets_ShowProperties(LPIDENT, size_t, BOOL)` opens the fileset property sheet and optionally starts on the threshold-related tab.

Control flow/state: The header is consumed by UI code and task code. The packet is allocated by the dialog and passed to `taskSET_PROP_APPLY`.

Dependencies/integration: Requires `LPIDENT`, `BOOL`, and `WORD` types from the broader server manager headers. Integrated with property sheets, alert counts, and task application logic.

Risks/test signals: Verify that task handlers and UI code agree on boolean semantics: warnings disabled, server default (`perWarnSetFull == -1` in loaded prefs), and custom percentage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.cpp

Purpose: Implements fileset quota editing and quota display. It can either apply a supplied quota immediately or ask the user via a modal quota dialog.

Important APIs/functions: `Filesets_SetQuota` dispatches `taskSET_SETQUOTA_APPLY`; `Filesets_PickQuota` returns a chosen quota or zero on cancel; `Filesets_SetQuota_DlgProc` handles quota dialog messages; `Filesets_SetQuota_OnEndTask_InitDialog` initializes/updates the spinner based on `ckMin`, `ckMax`, and current quota; `Filesets_DisplayQuota` formats usage text and progress bar percentage.

Control flow: If caller passes `ckQuota == 0`, the modal dialog loads current fileset state through `taskSET_SETQUOTA_INIT`. Unit changes update `gr.cbQuotaUnits`, preserve current value, and restart init to rebuild spinner ranges. Applying closes the dialog and returns quota in KB to `Filesets_SetQuota`, which starts the async apply task.

State and persistence: Uses global `gr.cbQuotaUnits` as a UI preference for KB vs MB. The quota value in the packet is always normalized to KB before applying. No direct persistence beyond the task layer changing the fileset quota.

Dependencies/integration: Depends on `agg_prop.h` to open aggregate properties, `Alert_GetCount`, spinner helpers, combobox helpers, and `LPFILESETSTATUS` from AFS class/task data.

Risks: The dialog procedure stores packet state in a static variable, so concurrent quota dialogs would interfere; the UI likely assumes modal single-instance use. Integer conversion to `int` for spinner min/current/max may truncate very large quotas. MB unit conversion uses integer division, which can round displayed values down.

Test signals: Test cancel path, supplied quota bypass, failed init task, KB/MB switching, very high quota ranges, zero/overfull quota display, and aggregate-properties button routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.h

Purpose: Declares quota edit/display APIs and the task packet used to apply a new fileset quota.

Important APIs/types: `SET_SETQUOTA_APPLY_PARAMS` contains the target fileset identity and quota in KB. `Filesets_SetQuota` applies or prompts, `Filesets_PickQuota` opens the picker, and `Filesets_DisplayQuota` renders quota usage into a dialog.

Control flow/state: UI callers can pass zero to prompt the user or a nonzero quota for immediate async application.

Dependencies/integration: Requires `LPIDENT`, `size_t`, `HWND`, and `LPFILESETSTATUS` from the server manager framework.

Risks/test signals: Ensure callers understand that zero means "ask" rather than "set unlimited quota"; if the lower task layer supports zero quota semantics, this API cannot express it directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.cpp

Purpose: Implements the confirmation dialog for releasing a read-write fileset to its replication sites.

Important APIs/functions: `Filesets_Release` opens/focuses a cached modeless release dialog. `Filesets_Release_DlgProc` handles lifecycle and OK/cancel. `Filesets_Release_OnInitDialog` formats the target server/aggregate/fileset description and defaults to normal release. `Filesets_Release_OnOK` sends `SET_RELEASE_PARAMS` to `taskSET_RELEASE`.

Control flow: Uses `PropCache` keyed by `pcSET_RELEASE` and target `LPIDENT` to prevent duplicate release dialogs for the same fileset. OK reads force-vs-normal radio state, starts the release task, and destroys the dialog; cancellation just destroys it.

State and persistence: Dialog-local only. The task packet stores `lpiRW` and `fForce`; release persistence is remote AFS volume state handled by `taskSET_RELEASE`.

Dependencies/integration: Depends on `svrmgr.h`, `set_release.h`, and `propcache.h`. Usually invoked from replication or fileset context menus.

Risks: The dialog assumes caller passes a suitable read-write fileset identity. It does not validate fileset type locally. Errors are not handled in this file after dispatch.

Test signals: Open duplicate release dialogs, normal vs force release, cancel path, and invocation on non-RW identities through higher-level command gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.h

Purpose: Declares the release dialog entry point and task packet for fileset release.

Important APIs/types: `SET_RELEASE_PARAMS` contains the read-write fileset identity and force flag. `Filesets_Release(LPIDENT)` starts the UI.

Control flow/state: The UI allocates `SET_RELEASE_PARAMS` and hands ownership to `taskSET_RELEASE`.

Dependencies/integration: Uses server manager identity types and the task layer.

Risks/test signals: Check task code treats `lpiRW` as read-write and handles forced releases consistently with the UI radio selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.cpp

Purpose: Implements fileset rename workflow, including an async preflight that resolves the read-write fileset for a possibly replica/clone request.

Important APIs/functions: `Filesets_ShowRename` allocates `SET_RENAME_INIT_PARAMS` and starts `taskSET_RENAME_INIT`. `Filesets_OnEndTask_ShowRename` handles lookup result, opens the modal rename dialog, and starts `taskSET_RENAME_APPLY` on success. `Filesets_Rename_DlgProc`, `Filesets_Rename_OnInitDialog`, and `Filesets_Rename_EnableOK` implement the modal UI.

Control flow: The preflight obtains `lpiRW`; failures show refresh or not-replicated errors. The dialog displays server/aggregate/current fileset name, initializes the new-name edit control to the current name, focuses it, and enables OK only when the new name is nonempty and differs case-insensitively.

State and persistence: The apply packet stores `lpiFileset` and `szNewName`. Persistent rename effects occur in `taskSET_RENAME_APPLY`.

Dependencies/integration: Relies on `svrmgr.h` tasks, identity name getters, resource strings, and help context.

Risks: `Filesets_Rename_DlgProc` uses a static packet pointer, acceptable for modal single-use but unsafe if reentered. It validates only nonempty/different names, leaving syntax/conflict validation to the task/server.

Test signals: Rename from RW and replica selections, failed lookup, unchanged-name disablement, empty-name disablement, and task error reporting by downstream handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.h

Purpose: Defines the init/apply packets and exported entry points for fileset rename.

Important APIs/types: `SET_RENAME_INIT_PARAMS` carries requested identity and resolved RW identity. `SET_RENAME_APPLY_PARAMS` carries the RW fileset and destination name. `Filesets_ShowRename` starts the workflow; `Filesets_OnEndTask_ShowRename` is the task completion hook.

Control flow/state: The init task mutates `lpiRW`; the completion handler owns the transition into modal UI and apply task.

Dependencies/integration: Consumed by command/task dispatch code that routes `taskSET_RENAME_INIT` completions.

Risks/test signals: Validate packet ownership and deletion across success, cancel, and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.cpp

Purpose: Implements the fileset replication properties sheet, focused on listing, adding, deleting, and releasing replica sites for a read-write fileset.

Important APIs/functions: `Filesets_ShowReplication` starts `taskSET_REPPROP_INIT`; `Filesets_OnEndTask_ShowReplication` opens/focuses the replication properties sheet; `Filesets_RepSites_DlgProc` manages the replica-site list tab; `Filesets_RepSites_OnInitDialog` sets identity fields and populates via `UpdateDisplay_Replicas`; `Filesets_RepSites_OnDelete` calls `Filesets_Delete` for selected replica.

Control flow: The init task resolves a RW fileset and status. Existing sheets are found with `PropCache_Search(pcSET_REP, lpiRW)`. The list registers `FastList` text callbacks and column notifications, stores/restores `gr.viewRep`, subscribes to `WHEN_SETS_CHANGE`, and refreshes the list on dispatch notifications. Commands route to create replica, delete selected site, and release RW fileset.

State and persistence: Dialog state consists of `SET_REPPROP_PARAMS` with requested/RW identities and a copied `FILESETSTATUS`. Column layout persists through `gr.viewRep` and `FL_StoreView`/`FL_RestoreView`. Actual replication changes are performed by delegated tasks invoked through other modules.

Dependencies/integration: Uses `set_createrep.h`, `set_delete.h`, `set_release.h`, `display.h`, `columns.h`, `propcache.h`, and the command/display infrastructure. It subclasses the replica FastList to support column menu commands.

Risks: The `lpiTarget` parameter to `Filesets_ShowReplication` is accepted but not used in this file. Subclass procedure pointer is static and shared across instances. The list refresh depends on notification ordering and valid `prp` lifetime.

Test signals: Open from RW/replica identity, failed init, duplicate property sheet focus, add/delete/release commands, column resize persistence, `WHEN_SETS_CHANGE` refresh, and context menu header behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.h

Purpose: Declares replication-property workflow entry points and the init packet populated by the async resolver.

Important APIs/types: `SET_REPPROP_INIT_PARAMS` stores requested identity, resolved RW identity, and `FILESETSTATUS`. `Filesets_ShowReplication` starts the workflow; `Filesets_OnEndTask_ShowReplication` handles init completion.

Control flow/state: The task layer fills `lpiRW` and `fs`; UI opens a cached properties sheet once the RW fileset is known.

Dependencies/integration: Integrates with task dispatch and fileset display/replica management modules.

Risks/test signals: Verify callers do not rely on the unused `lpiTarget` parameter without downstream support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.cpp

Purpose: Implements the fileset restore dialog. It lets users choose a dump file, target fileset name, target server/aggregate, and incremental mode before starting restore.

Important APIs/functions: `Filesets_Restore` opens the modal dialog and dispatches `taskSET_RESTORE` if required fields are present. `Filesets_Restore_DlgProc` coordinates async lookup and server/aggregate enumeration. `Filesets_Restore_OnSetName` starts `taskSET_LOOKUP`. `Filesets_Restore_OnEndTask_LookupFileset` decides create-vs-overwrite UI state. `Filesets_Restore_OnBrowse` uses `GetOpenFileName` for dump selection.

Control flow: Initialization subclasses the aggregate list, restores `gr.viewAggRestore` from related aggregate views when first used, sets defaults from an optional parent identity, runs lookup once, and starts `taskSVR_ENUM_TO_COMBOBOX`. Server selection triggers `taskAGG_ENUM_TO_LISTVIEW`. Fileset name edits start async lookup, which can change `psrp->lpi` from aggregate target to existing fileset target and disable server/aggregate choice for overwrite.

State and persistence: `SET_RESTORE_PARAMS` stores chosen target identity, fileset name, filename, and incremental flag. Column layout persists in `gr.viewAggRestore` on destroy. Actual restore changes occur in `taskSET_RESTORE`.

Dependencies/integration: Uses server and aggregate enumeration packets, `set_general.h` for lookup packet, `svr_window.h`, `display.h`, `columns.h`, and `FastList` helpers.

Risks: `Filesets_Restore_OnEndTask_EnumAggregates` is empty, so aggregate enumeration failure feedback depends on lower display behavior. Multiple rapid name changes can queue overlapping lookup tasks; late completion could update `psrp->lpi` for stale text if the task layer does not coalesce. OK enablement relies on `psrp->lpi` not being a server.

Test signals: Restore into existing fileset, restore creating new fileset, parent server/aggregate/fileset defaults, failed lookup, server switch, empty filename/name, browse filter, incremental checkbox, and column persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.h

Purpose: Declares the restore task packet and UI entry point.

Important APIs/types: `SET_RESTORE_PARAMS` contains target identity, fileset name, dump filename, and incremental flag. `Filesets_Restore(LPIDENT)` opens the restore workflow with an optional parent identity.

Control flow/state: The packet is owned by the modal dialog until OK; on OK it is passed to `taskSET_RESTORE`.

Dependencies/integration: Requires `LPIDENT`, path constants, and task handling from the server manager.

Risks/test signals: Ensure the task interprets `lpi` correctly as either aggregate target for create or fileset target for overwrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.cpp

Purpose: Implements the Filesets tab in the server manager UI, including list/tree display, context menus, selection-sensitive buttons, notification refresh, and drag/drop move/replica workflows.

Important APIs/functions: `Filesets_DlgProc` is the tab dialog procedure. `Filesets_OnSelect` and `Filesets_OnEndTask_Select` enable buttons after `taskSET_SELECT` returns fileset type/status. `Filesets_OnNotifyFromDispatch` refreshes display on fileset/status/alert/destroy events. `Filesets_Subclass_OnCommand` routes list commands to view changes, move/replica drop commands, or generic `StartContextCommand`. Drag helpers manage FastList drag images and target highlighting. `Filesets_ShowPopupMenu` and `Filesets_OnEndTask_Menu` build context menus based on focused identity and task-returned fileset status.

Control flow: On init, the tab is resized into the parent tab area, restores `gr.viewSet`, registers `GetItemText`, subclasses the list, applies view style, and initializes selection state. `WM_SERVER_CHANGED` updates header text based on selected server/cell/subset and monitors all object changes. Context menus delegate menu-state computation to `taskSET_MENU`; drag right-drop delegates to `taskSET_DRAGMENU`.

State and persistence: Stores list view layout in `gr.viewSet`, icon view in `gr.ivSet`, and server/aggregate expand state in per-object preferences through `Server_SavePreferences` and `Aggregates_SavePreferences`. Drag state is a file-static struct with drag source, target, image list, and target item.

Dependencies/integration: Integrates with server, service, aggregate, fileset display, move, create-replica, command dispatch, and column-management modules. It depends heavily on `FastList`, `UpdateDisplay_Filesets`, `Filesets_GetSelected/Focused`, and notification dispatch.

Risks: Drag state is global to the module and assumes one active fileset list. Context-menu enablement depends on async status; stale tasks may affect UI if selection changes before completion. `IdentifyPoint` trusts a FastList item from any target window, so only callers constrain target windows by identity type. Menu logic disables operations for clones/non-RW filesets but task handlers still need validation.

Test signals: Tree/list/report view switching, selection changes for RW/replica/clone, double-click behavior on expandable vs leaf items, server/cell/subset header text, expand persistence, context menus on header/items/empty area, drag move and drag replica targets, and dispatch refresh events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.h

Purpose: Declares the Filesets tab dialog procedure and popup-menu helper.

Important APIs/types: `Filesets_DlgProc` plugs into the server manager tab UI. `Filesets_ShowParticularPopupMenu` lets other UI components show a fileset-specific or empty-area menu at a screen point.

Control flow/state: The popup helper allocates a menu task and starts async menu state calculation.

Dependencies/integration: Used by server/aggregate/fileset list components that need fileset context menus.

Risks/test signals: Verify callers pass a parent HWND whose parent is the expected tab/window so `StartTask(taskSET_MENU, GetParent(hParent), ...)` returns to a live handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.cpp

Purpose: Implements server subset filtering for a cell, including in-memory monitor decisions, subset edit UI, load/save dialogs, and registry persistence.

Important APIs/functions: `Subsets_fMonitorServer` evaluates whether a server is included based on inclusive (`pszMonitored`) or exclusive (`pszUnmonitored`) multistrings. `Subsets_SetMonitor` mutates a subset for one server. `ShowSubsetsDialog` opens the modal property sheet. `Subsets_OnApply` copies dialog state into global `g.sub` and starts `taskAPPLY_SUBSET`. `Subsets_SaveIfDirty` prompts save/discard/cancel for modified subsets. `Subsets_EnumSubsets`, `Subsets_SaveSubset`, and `Subsets_LoadSubset` use registry keys. `Subsets_CopySubset`/`Subsets_FreeSubset` manage allocation. The open/save dialog supports list, delete, and rename.

Control flow: The edit sheet receives a copy of `g.sub`. Checkbox list changes create a subset if needed, rebuild monitored/unmonitored multistrings from UI, update display name, and mark the sheet dirty. Load replaces the current subset with registry-loaded content; save prompts for a name and writes the current server list. Apply swaps `g.sub` to a copy of dialog state and triggers refresh. The open/save dialog enumerates subset registry subkeys and supports overwrite confirmation and rename by load-save-delete.

State and persistence: `SUBSET` contains `szSubset`, `fModified`, and either an inclusive or exclusive allocated multistring. Registry persistence uses `REGVAL_INCLUSIVE` as a DWORD and stores each server name as a value set to `"X"` under a subset subkey. `OpenSubsetsKey/OpenSubsetsSubKey` are external helpers. `g.sub` is the active filter.

Dependencies/integration: Uses prop sheet cache (`pcGENERAL`), global cell/server identities, task `taskSUBSET_TO_LIST`, `taskAPPLY_SUBSET`, resource dialogs, listbox/listview helpers, and registry APIs.

Risks: `Subsets_SaveSubset` does not clear old registry values before writing new entries unless `OpenSubsetsSubKey` with create mode replaces/cleans externally; stale values could persist. Inclusive/exclusive semantics are compact but easy to misinterpret: a single checked server uses `pszMonitored`, otherwise unchecked servers use `pszUnmonitored`. `Subsets_OnApply` passes the original `sub` to `taskAPPLY_SUBSET` after copying it into `g.sub`, so task ownership/lifetime must be checked elsewhere. Rename overwrite prompt formats `lpp->szSubset` instead of the proposed text in one branch, which may display the wrong name.

Test signals: No subset, single-server subset, all/none toggles, inclusive vs exclusive save/load round-trip, dirty save/discard/cancel, subset delete, rename into existing name, case-insensitive long/short server matching, and refresh after apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.h

Purpose: Defines the `SUBSET` model and exports subset filtering, UI, persistence, copy, and cleanup functions.

Important APIs/types: `SUBSET` holds subset name, dirty flag, and allocated monitored/unmonitored multistrings. Exports include `Subsets_fMonitorServer`, `Subsets_SetMonitor`, `ShowSubsetsDialog`, save/load/enumerate helpers, and memory management.

Control flow/state: A subset can represent "only these servers" via `pszMonitored`, "all except these servers" via `pszUnmonitored`, or no filter via null pointers.

Dependencies/integration: Consumed by display/dispatch code to decide monitored servers and by UI code to edit/save subsets.

Risks/test signals: All code that copies or frees subsets must preserve multistring double-null termination and use `Subsets_FreeSubset` rather than raw delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.cpp

Purpose: Provides default service list column configuration and text formatting for service rows.

Important APIs/functions: `Services_SetDefaultView` initializes `VIEWINFO` with all available columns and default shown columns. `Services_GetAlertCount` delegates to `Alert_GetCount`. `Services_GetColumnText` returns formatted text for name, type, params, notifier, state, dates, and last error.

Control flow: Column text is pulled from `SERVICE_PREF::ssLast` stored in the service identity user param. Name can include server prefix when requested. Params/notifier sanitize CR/LF/tab to spaces. Date columns use `FormatTime`; start/stop combined column labels date based on current running/stopped state.

State and persistence: Uses a rotating static buffer array sized by `nSERVICECOLUMNS`; callers must consume text before enough subsequent calls overwrite it. View preferences are written into caller-provided `VIEWINFO`.

Dependencies/integration: Depends on `svc_col.h`, alert system, service status/preference structures, and localization strings.

Risks: Static buffers are not thread-safe and limit nested use. If `GetUserParam()` is missing, most columns return empty text. `svccolLASTERROR` always formats an error number if status exists, even if zero.

Test signals: Service rows with no loaded prefs, each service type/state, multiline params/notifier, invalid dates, show-server-name mode, and repeated column callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.h

Purpose: Defines service list columns and declares formatting/default-view helpers.

Important APIs/types: `SERVICECOLUMN` enumerates ten service columns. `SERVICECOLUMNS` maps resource IDs to default widths. `nSERVICECOLUMNS` computes column count. Exports include `Services_SetDefaultView`, `Services_GetAlertCount`, and `Services_GetColumnText`.

Control flow/state: The enum order must match `SERVICECOLUMNS` and text buffers in `svc_col.cpp`.

Dependencies/integration: Used by FastList display code and column chooser logic.

Risks/test signals: Adding/reordering columns requires updating enum, table, and text switch together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.cpp

Purpose: Implements the Add Service property sheet for creating BOS-managed services on a selected server.

Important APIs/functions: `Services_Create` opens/focuses a singleton create sheet. `Services_Create_DlgProc` handles input changes and apply. `Services_Create_OnInitDialog` enumerates servers and fills common service names. `Services_Create_OnType` toggles fields for simple/cron services and populates recurrence days. `Services_Create_OnApply` collects fields into `SVC_CREATE_PARAMS` for `taskSVC_CREATE`. `Services_Create_EnableOK` validates required fields.

Control flow: The sheet is cached under `pcSVC_CREATE`. Server enumeration is async through `taskSVR_ENUM_TO_COMBOBOX`. Name changes call `Services_GuessLogName` and may auto-fill log filename. Type radio buttons enable run-now for simple services and recurrence day/time for cron services.

State and persistence: No direct persistence; it creates task packets for service creation. It reads no existing service state. The guessed log name is UI convenience.

Dependencies/integration: Depends on `svc_general.h` for log guesses, prop sheet cache, combobox helpers, time input helpers, and task dispatch.

Risks: `Services_Create_EnableOK` checks whether server combo is enabled, so OK may stay disabled if enum task failure leaves it disabled. Fields use `cchNAME` for command/params/log/notifier, which may truncate paths/commands longer than name length. Type handler references `IDC_SVC_TYPE_FS` in logic but the command switch only listens to simple/cron, so FS toggling must be covered by dialog resource behavior or may not update controls.

Test signals: Server enumeration success/failure, required name/command validation, log-name auto-fill, simple/cron/FS service types, cron day/time collection, and duplicate create sheet focus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.h

Purpose: Declares service creation task data and UI entry point.

Important APIs/types: `SVC_CREATE_PARAMS` stores target server, service name, command, params, notifier, log file, service type, run-now flag, and cron schedule. `Services_Create(LPIDENT)` opens the creation UI.

Control flow/state: The create dialog fills the packet and passes it to `taskSVC_CREATE`.

Dependencies/integration: Uses `AFSSERVICETYPE`, `SYSTEMTIME`, and `LPIDENT` from the broader OpenAFS Windows manager framework.

Risks/test signals: Verify field buffer sizes match BOS service creation API expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.cpp

Purpose: Implements confirmation dialog for deleting a service.

Important APIs/functions: `Services_Delete` opens a modal delete confirmation and starts `taskSVC_DELETE` on OK. `Services_Delete_DlgProc` stores the target identity in a static pointer and handles OK/cancel. `Services_Delete_OnInitDialog` formats the target server/service into explanatory text.

Control flow: The dialog is purely synchronous. The selected service identity is passed directly to the delete task after confirmation.

State and persistence: No local persisted state; deletion is remote service state handled by the task layer.

Dependencies/integration: Depends on `svrmgr.h`, `svc_delete.h`, resource strings, and task dispatch. Higher-level menus disable deletion for BOS.

Risks: Uses a static dialog pointer, safe only under modal single-instance assumptions. No local validation prevents deleting BOS or invalid identities; callers must gate.

Test signals: Confirm/cancel paths, delete for normal service, attempted BOS delete via direct call, and error handling in task completion elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.h

Purpose: Declares service deletion UI entry point.

Important APIs/types: `Services_Delete(LPIDENT)` prompts for confirmation and dispatches deletion.

Control flow/state: The target identity is passed to `taskSVC_DELETE` on OK.

Dependencies/integration: Called from service tab/property/context commands.

Risks/test signals: Ensure command gating excludes BOS and null identities before calling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.cpp

Purpose: Provides service preference loading/saving and default log-name inference.

Important APIs/functions: `Services_GuessLogName` maps known service names to log filenames. `Services_LoadPreferences` restores `SERVICE_PREF`, initializes defaults if absent, initializes alerts, and stores guessed log file on first creation. `Services_SavePreferences` writes current service preferences.

Control flow: On load, `RestorePreferences` fills the struct; if missing, defaults are set (`fWarnSvcStop`, alert defaults, guessed log path) and immediately stored. `Alert_Initialize` runs for restored and new prefs.

State and persistence: Persists `SERVICE_PREF` by identity via `StorePreferences`. The `szLogFile` preference is used by log viewing.

Dependencies/integration: Depends on global preference helpers, alert helpers, and service identities.

Risks: Log-name mapping is hard-coded and case-insensitive but limited to known services. Immediate store on first load writes guessed defaults even before user action.

Test signals: First-load defaults, restored prefs, unknown/upclient/upserver services with empty log, and save failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.h

Purpose: Declares service preference and log-name helper APIs.

Important APIs/types: `Services_LoadPreferences`, `Services_SavePreferences`, and `Services_GuessLogName`.

Control flow/state: Preference pointers are stored as user params on service identities by the broader identity framework.

Dependencies/integration: Used by service display, property, and log viewer code.

Risks/test signals: Header exposes only string-name `Services_GuessLogName`; the identity overload is private to the `.cpp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.cpp

Purpose: Implements service property sheets. The General tab shows status, type, params, notifier, start/stop dates, warning preference, start/stop/restart controls, and log viewer. The BOS-only tab configures restart schedules.

Important APIs/functions: `Services_ShowProperties` builds cached property sheets with problems/general/BOS tabs. `PropSheet_AddBOSTab` conditionally adds BOS tab. `Services_General_DlgProc` handles refresh, apply, and service control commands. `Services_General_OnEndTask_InitDialog` renders `taskSVC_PROP_INIT` data. `Services_BOS_DlgProc` and related helpers get/set restart times via `taskSVC_GETRESTARTTIMES` and `taskSVC_SETRESTARTTIMES`.

Control flow: General tab registers object-change notifications and refreshes on `evtRefreshStatusEnd` for the target service. Init disables controls until async status returns; success enables controls, formats status and dates, sanitizes params/notifier, and checks stop-warning prefs based on service and cell/server preference data. Start command restarts BOS but starts non-BOS; stop command invokes `Services_Stop`; view log invokes `Services_ShowServiceLog`. BOS tab populates recurrence controls, loads schedule asynchronously, and applies schedule packets.

State and persistence: General apply sends `SVC_PROP_APPLY_PACKET` with warning preference. BOS apply sends `SVC_RESTARTTIMES_PARAMS`. Actual preference and BOS restart-time persistence is in tasks/service APIs.

Dependencies/integration: Uses `svc_general.h`, `svc_startstop.h`, `svc_viewlog.h`, `propcache.h`, `problems.h`, time controls, alert/problem tabs, and notification dispatch.

Risks: The general tab creates a brush on each `WM_CTLCOLOR*`-like path in related code patterns; here main risks are stale async refreshes and disabling buttons during starting/stopping. BOS detection is by literal service name `"BOS"`. `Services_BOS_OnApply` does not use the dialog as task target, so failures may be reported elsewhere or not directly in this tab.

Test signals: Property sheet caching, failed status refresh, running/starting/stopping/stopped services, BOS vs non-BOS controls, warn-stop apply failure, view-log path, BOS schedule load/apply, and notification-triggered refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.h

Purpose: Declares service property task packets and UI entry point.

Important APIs/types: `SVC_PROP_APPLY_PACKET` carries target service and warn-stop setting. `SVC_RESTARTTIMES_PARAMS` carries BOS general/new-binary restart flags and schedules. `Services_ShowProperties` opens the property sheet.

Control flow/state: Packets are allocated by tabs and consumed by task handlers.

Dependencies/integration: Used by service command routing and task implementation.

Risks/test signals: Ensure `SYSTEMTIME.wDayOfWeek == (WORD)-1` daily convention is honored by BOS restart task code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.cpp

Purpose: Provides service running check and start/restart/stop workflows with permanent/temporary mode selection.

Important APIs/functions: `Services_fRunning` queries live status through `LPSERVICE::GetStatus`. `Services_Restart` directly starts `taskSVC_RESTART`. `Services_Start` and `Services_Stop` show a modal start/stop dialog, then dispatch `taskSVC_START` or `taskSVC_STOP` with temporary flag. Dialog helpers format text and capture the selected mode.

Control flow: Start/stop use a local `SERVICE_STARTSTOP_PARAMS` stack struct for modal UI, then allocate the public task packet only after OK. The dialog title and radio labels are selected based on `fStart`.

State and persistence: Temporary/permanent affects remote BOS service state via task packets. No local preferences.

Dependencies/integration: Depends on service status APIs, task dispatch, resource strings, and help IDs.

Risks: `Services_StartStop_DlgProc` keeps a static pointer that is not explicitly cleared on destroy, though the modal lifetime limits exposure. Restart bypasses confirmation and temporary mode entirely.

Test signals: Start/stop cancel, temporary vs permanent selection, service status query failure, BOS restart from property tab, and help routing for start vs stop dialog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.h

Purpose: Declares public service control packets and helper functions.

Important APIs/types: `SVC_START_PARAMS` and `SVC_STOP_PARAMS` carry service identity and temporary flag. Functions include `Services_fRunning`, `Services_Start`, `Services_Restart`, and `Services_Stop`.

Control flow/state: Start/stop allocate these packets after confirmation and hand them to tasks.

Dependencies/integration: Used by service property and context command handlers.

Risks/test signals: Ensure restart task does not need the temporary flag that start/stop expose.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.cpp

Purpose: Implements the Services tab list UI, including selection-sensitive buttons, display refresh, context menus, and command routing.

Important APIs/functions: `Services_DlgProc` is the tab procedure. `Services_OnSelect` enables restart/delete based on selected service and disables delete for BOS. `Services_OnNotifyFromDispatch` refreshes list display. `Services_SubclassListProc` routes list commands to `StartContextCommand`. `Services_ShowPopupMenu` chooses service/server/header/empty menus. `Services_OnEndTask_Menu` enables/disables start/stop/restart menu commands based on service status returned by `taskSVC_MENU`.

Control flow: On init, the tab is resized, `gr.viewSvc` restored, text callback installed, list subclassed, and selection updated. `WM_SERVER_CHANGED` subscribes to service changes for the selected server and updates header text based on server/cell/subset monitoring. Context menus on selected server identities defer to server menus; service menus are built asynchronously.

State and persistence: Stores list layout in `gr.viewSvc` on destroy and reads icon view `gr.ivSvc` for empty-area menu checkmarks. No direct service persistence.

Dependencies/integration: Uses `svr_window.h`, `svr_general.h`, `display.h`, command dispatcher, FastList, notification dispatch, and service status task data.

Risks: Menu state logic appears to use `else if (state != RUNNING)` after `if (state != STOPPED)`, which disables stop only when stopped but may leave stop enabled for starting/stopping unless task statuses constrain elsewhere. Selection actions depend on `FL_GetSelectedData` identity validity.

Test signals: Service list refresh events, BOS selection, no selection, server identity in list, start/stop menu enablement for each state, header context menu, and double-click properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.h

Purpose: Declares the Services tab dialog procedure and service popup-menu helper.

Important APIs/types: `Services_DlgProc` plugs into tab UI; `Services_ShowParticularPopupMenu` starts async menu generation for selected/empty service context.

Control flow/state: The popup helper passes a `MENUTASK` to `taskSVC_MENU`.

Dependencies/integration: Used by services tab and other list contexts needing service menus.

Risks/test signals: Ensure returned `WM_ENDTASK` goes to a window that handles `taskSVC_MENU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.cpp

Purpose: Implements log viewing for a service or arbitrary server log. It discovers a remote log name, downloads the log to a temporary local file, displays the tail, and supports Save As.

Important APIs/functions: `Services_ShowServiceLog` and `Services_ShowServerLog` create modeless view-log dialogs. `Services_ShowLog_TakeNextStep` is a small state machine: local file ready, remote name known, service log discovery, or user pick. `Services_ShowLog_OnEndTask` handles `taskSVC_FINDLOG` and `taskSVC_VIEWLOG`. `Services_ShowLog_OnInitDialog` stores service log preference, reads/truncates local file, and populates the edit control. `Services_ShowLog_OnSaveAs` copies the temp file via `SHFileOperation`. `Services_ShowLog_Pick` opens the remote log-name dialog.

Control flow: The dialog begins hidden, runs discovery/download steps asynchronously, then shows itself only after local content is ready. If service log discovery fails, it prompts for a filename once; if download fails after user-chosen or repeated attempt, it shows an error. Server log viewing can prompt for server/file when no remote path is given.

State and persistence: `SVC_VIEWLOG_PACKET` stores service/server identities, remote path, local temp path, and download attempt count. The local temp file is deleted on dialog destroy. Successful service log viewing persists `szRemote` in `SERVICE_PREF::szLogFile` via `Services_SavePreferences`. Window rectangle persists in `gr.rViewLog`.

Dependencies/integration: Uses shell API, open/save dialogs, service preferences, server enumeration, task-based download/discovery, and Win32 file APIs.

Risks: Reads file bytes into `TCHAR` buffer using byte count, which is fragile for Unicode builds or non-text encodings. The trailing CR/LF trimming loop lacks parentheses around `&&`/`||`, making it evaluate `pszLog[cch-1]` when `cch == 0` if the second disjunct is reached. `WM_CTLCOLOREDIT` creates a brush per paint without caching/deleting. Only the last 20 KB are shown by design.

Test signals: Known service log, unknown service prompting, failed first download then prompt, server-level log, temp file cleanup, large log truncation and line count, Save As copy, Unicode/ANSI builds, and empty file handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.h

Purpose: Defines view-log state and declares service/server log viewer entry points.

Important APIs/types: `SVC_VIEWLOG_PACKET` contains service/server identities, remote and local file paths, and download attempt count. `Services_ShowServiceLog` and `Services_ShowServerLog` open modeless log viewers.

Control flow/state: Packet state drives discovery, download, display, and cleanup in the implementation.

Dependencies/integration: Used from service properties and server commands.

Risks/test signals: `fTriedDownload` is defined but unused by the implementation, while `nDownloadAttempts` is authoritative.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.cpp

Purpose: Implements server address display, parsing, host lookup, and the Change Addresses dialog used by server properties.

Important APIs/functions: `Server_FillAddrList` populates address listbox from `SERVERSTATUS`. `Server_ParseAddress` converts text to `SOCKADDR_IN` using `inet_addr`. `Server_Ping` resolves a server hostname with `gethostbyname`. `ChangeAddr_DlgProc` handles address edit UI. `ChangeAddr_OnEndTask_Init` loads old/new `SERVERSTATUS` from `taskSVR_PROP_INIT`. `ChangeAddr_OnRemove` zeroes selected address entries. `ChangeAddr_OnChange` opens `NewAddr_DlgProc` and updates `ssNew`.

Control flow: The dialog starts disabled with a querying list, runs server property init, copies status into old/new structures, then lets the user remove/change addresses. Change operation prevents duplicates by detecting an existing new address and converting the selected old address to zero instead.

State and persistence: `SVR_CHANGEADDR_PARAMS` stores server identity plus old/new status snapshots. The dialog mutates `ssNew`; on OK the caller starts `taskSVR_CHANGEADDR`. No registry/local persistence.

Dependencies/integration: Uses WinSock, AFS address conversion helpers, listbox helpers, server property task data, and socket-address UI control helpers `SA_SetAddr/SA_GetAddr`.

Risks: `inet_addr` error value for invalid input is not validated distinctly from broadcast-like values. `Server_Ping` uses legacy `gethostbyname`, IPv4 only, and broad catch. Address removal loops over `ssOld.nAddresses` and indexes `ssNew` by same count, assuming arrays match. Zero-address entries are hidden, so user cannot directly re-add through this dialog.

Test signals: Server with no addresses, multiple addresses, duplicate replacement, remove all, invalid address text through new address control, failed property init, and host lookup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.h

Purpose: Declares server address change packet and helper APIs.

Important APIs/types: `SVR_CHANGEADDR_PARAMS` contains target server and old/new `SERVERSTATUS`. Exports include address list fill, parse, ping, and `ChangeAddr_DlgProc`.

Control flow/state: Server properties allocate this packet, run the modal dialog, and dispatch address-change task on OK.

Dependencies/integration: Requires server status structures, WinSock address types, and dialog framework.

Risks/test signals: Confirm all users initialize both status snapshots before expecting meaningful diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.cpp

Purpose: Provides default server list view settings and server row column text.

Important APIs/functions: `Server_SetDefaultView_Horz` and `Server_SetDefaultView_Vert` initialize horizontal/vertical server `VIEWINFO`. `Server_GetAlertCount` delegates to alerts. `Server_GetColumnText` formats server name, first address, and quick status/alert description.

Control flow: Column formatting reads `SERVER_PREF::ssLast` from identity user param for address; status uses `Alert_GetQuickDescription` with fallback to no-alerts text.

State and persistence: Uses rotating static buffers sized by `nSERVERCOLUMNS`; caller-provided `VIEWINFO` receives default columns and sort.

Dependencies/integration: Used by display code and column callbacks.

Risks: Only the first address is shown. Static buffers are not thread-safe. Missing preferences produce empty address but still can show alert status.

Test signals: Server with no prefs, multiple addresses, alert/no-alert states, vertical vs horizontal defaults, and repeated callback usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.h

Purpose: Defines server list columns and declares server view/text helper APIs.

Important APIs/types: `SERVERCOLUMN` enumerates name, address, and status. `SERVERCOLUMNS` maps columns to resource IDs and widths. Exports include default view setup and `Server_GetColumnText`.

Control flow/state: Enum/table order must remain synchronized with implementation switch logic.

Dependencies/integration: Used by server display and column chooser.

Risks/test signals: Adding columns requires updating `nSERVERCOLUMNS` consumers and text formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.cpp

Purpose: Implements a singleton modeless dialog for executing a command on a selected server.

Important APIs/functions: `Server_Execute` opens/focuses the dialog. `Server_Execute_DlgProc` handles lifecycle. `Server_Execute_OnInitDialog` enumerates servers. `Server_Execute_EnableOK` validates selected server and command text. `Server_Execute_OnOK` sends `SVR_EXECUTE_PARAMS` to `taskSVR_EXECUTE`.

Control flow: The dialog is cached under `pcSVR_EXECUTE` with no identity key. Server combo is disabled until `taskSVR_ENUM_TO_COMBOBOX` completes. OK destroys the dialog after dispatching the task.

State and persistence: Dialog packet stores default server and command buffer. No persisted state.

Dependencies/integration: Uses server enumeration packet, prop cache, task dispatcher, and Win32 dialog controls.

Risks: No confirmation or command validation beyond nonempty text; security and quoting rules must be enforced by task/server layer. Singleton prevents multiple simultaneous command dialogs across servers.

Test signals: Default server selection, server enum failure, empty command validation, duplicate dialog focus, and task dispatch contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.h

Purpose: Declares remote execute packet and UI entry point.

Important APIs/types: `SVR_EXECUTE_PARAMS` carries server identity and command path/string. `Server_Execute(LPIDENT)` opens the command dialog.

Control flow/state: Dialog fills packet and dispatches `taskSVR_EXECUTE`.

Dependencies/integration: Used by server context command routing.

Risks/test signals: `szCommand` is limited to `MAX_PATH`, which may be too short for complex command lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.cpp

Purpose: Provides server preference initialization/saving and server context-menu construction.

Important APIs/functions: `Server_LoadPreferences` restores or initializes `SERVER_PREF` defaults for alert thresholds, warning flags, window state, monitor/open state, and tree expansion. `Server_SavePreferences` stores preferences. `Server_ShowPopupMenu` and `Server_ShowParticularPopupMenu` show empty/server-specific context menus with checked/disabled items based on view state, monitor state, and open property windows.

Control flow: Preferences default to monitored until dispatch later decides otherwise. Empty menu checks server view mode and icon view and disables close-all if no server property windows are cached. Server menu toggles open/close/monitor and disables sensitive operations for unmonitored servers.

State and persistence: Persists `SERVER_PREF` via `RestorePreferences`/`StorePreferences`. Reads globals `gr.fPreview`, `gr.fVert`, `gr.diHorz/diVert`, `gr.fOpenMonitors`, and display icon view.

Dependencies/integration: Uses prop cache, display helpers, alert defaults, menu helpers, and identity user params.

Risks: Monitor state is initialized optimistically and corrected elsewhere; early UI may briefly show monitored behavior. Context-menu gating is UI-only and must be mirrored by command handlers.

Test signals: First-load prefs, restored prefs, monitored/unmonitored server menus, open/close state, empty-area view checks, close-all enablement, and preference save after tree expansion/window state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.h

Purpose: Declares default warning constants and server preference/menu APIs.

Important APIs/types: Defines default aggregate-full and fileset-full warning percentages and service-stop warning default. Exports server popup helpers and preference load/save functions.

Control flow/state: Defaults are used by server/fileset property UIs when stored preferences are absent or disabled.

Dependencies/integration: Included by server property, fileset property, and tab modules.

Risks/test signals: Changing defaults affects first-run preferences and UI fallback values but may not migrate existing stored preferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.cpp

Purpose: Implements UI to query modification dates for a server file and its `.BAK`/`.OLD` variants.

Important APIs/functions: `Server_GetDates` opens/focuses singleton input dialog. `Server_GetDates_DlgProc` enumerates servers and validates filename. `Server_GetDates_OnOK` opens a results dialog. `Server_GetDates_Results_OnInitDialog` starts `taskSVR_GETDATES`. `Server_GetDates_Results_OnEndTask_InitDialog` formats up to three returned date strings into result controls.

Control flow: Server combo starts disabled during `taskSVR_ENUM_TO_COMBOBOX`. OK in the first dialog allocates a results packet and destroys the input dialog. Results dialog starts the actual getdates task, fills server/filename labels, then shows itself after task completion.

State and persistence: `SVR_GETDATES_PARAMS` stores server identity and filename. No persisted state.

Dependencies/integration: Uses prop cache, server enumeration, task data string fields (`pszText1..3`), and resource formatting.

Risks: Results dialog allocates a copy of input params for the task but the original `lppIn` lifetime depends on first dialog destruction; current flow fills labels immediately before destruction side effects matter. No error message is shown on failed getdates in this file.

Test signals: Empty filename validation, server enum failure, success with one/two/three returned dates, task failure, duplicate input dialog focus, and lifecycle around input/result dialogs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.h

Purpose: Declares get-dates task packet and dialog entry point.

Important APIs/types: `SVR_GETDATES_PARAMS` carries server identity and filename. `Server_GetDates(LPIDENT)` starts the workflow.

Control flow/state: Packet is passed from input dialog to results dialog and task.

Dependencies/integration: Used by server command menus for file maintenance.

Risks/test signals: `szFilename` uses `MAX_PATH`; remote server paths longer than that cannot be expressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.cpp

Purpose: Implements the server host/admin list editor, with add/remove UI and save task dispatch.

Important APIs/functions: `Server_Hosts` opens/focuses a cached property sheet per server. `Server_Hosts_DlgProc` handles list lifecycle. `Server_Hosts_OnInitDialog` initializes FastList image lists and starts `taskSVR_HOSTLIST_OPEN`. `Server_Hosts_OnEndTask_ListOpen` stores and displays `LPHOSTLIST`. `Server_Hosts_OnApply` increments host-list refcount and starts `taskSVR_HOSTLIST_SAVE`. Add/remove helpers mutate the in-memory list. `Server_AddHost_DlgProc` captures a host name.

Control flow: The host list is loaded asynchronously. Until loaded, list/add/remove are disabled. Add opens a modal dialog, avoids duplicate visible entries, calls `AfsClass_HostList_AddEntry` if new, and selects the item. Remove deletes all selected entries from both list model and UI. Apply saves only if list is enabled.

State and persistence: `SVR_HOSTS_PARAMS` owns `LPHOSTLIST`; free uses `AfsClass_HostList_Free`. Saving persists remote server host list through task. The host list has reference counting; apply increments before handing to task.

Dependencies/integration: Uses AFS class host-list APIs, prop cache, FastList, image lists, and task dispatch.

Risks: `memset(pAdd, 0x00, sizeof(pAdd))` clears only pointer size, not `SVR_ADDHOST_PARAMS`; subsequent fields are set enough for current use except tail bytes remain uninitialized. Failed `taskSVR_HOSTLIST_OPEN` may leave `lpList` null with no visible error in this file. Add dialog validates only nonempty host string.

Test signals: Load failure, duplicate add case-insensitive, add new host, remove multiple selected hosts, apply refcount behavior, cached sheet focus, and memory analysis for the `sizeof(pAdd)` initialization bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.h

Purpose: Declares the server host-list editor entry point.

Important APIs/types: `Server_Hosts(LPIDENT)` opens a per-server property sheet for host list management.

Control flow/state: Implementation owns private host-list and add-host packet types.

Dependencies/integration: Invoked from server command/menu handlers.

Risks/test signals: Callers should pass a server identity; the implementation does not validate identity type before using server name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.cpp

Purpose: Implements singleton dialog for installing/copying a local binary/file to a target directory on a selected server.

Important APIs/functions: `Server_Install` opens/focuses the dialog. `Server_Install_DlgProc` handles lifecycle. `Server_Install_OnInitDialog` enumerates servers and sets description. `Server_Install_EnableOK` validates selected server, source filename, and target directory. `Server_Install_OnBrowse` uses `GetOpenFileName`. `Server_Install_OnOK` dispatches `taskSVR_INSTALL`.

Control flow: Dialog is cached under `pcSVR_INSTALL`. Server combo is disabled until async enumeration completes. Browse preserves/restores current directory around file dialog. OK dispatches install task then destroys the dialog through fallthrough to cancel handling.

State and persistence: `SVR_INSTALL_PARAMS` stores target server, source path, and target directory. No local persistence.

Dependencies/integration: Uses prop cache, server enumeration, common file dialog APIs, resource filters, and task dispatch.

Risks: Target directory is free text with only nonempty validation. Source/target buffers use `MAX_PATH`; long paths are unsupported. OK closes immediately, so task failures must surface elsewhere.

Test signals: Empty-field validation, server enum failure, browse cancel/success, current-directory preservation, duplicate dialog focus, and task packet field contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.h

Purpose: Declares server install task packet and UI entry point.

Important APIs/types: `SVR_INSTALL_PARAMS` carries server identity, local source path, and remote target directory. `Server_Install(LPIDENT)` opens the install dialog.

Control flow/state: The dialog fills this packet for `taskSVR_INSTALL`.

Dependencies/integration: Used by server maintenance commands.

Risks/test signals: Validate target path semantics in the task layer; UI only checks nonempty fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.cpp

Purpose: Implements server property sheets. The General tab shows server status/capacity/addresses and supports auth/address changes. The Scout tab configures monitoring warnings and auto-refresh.

Important APIs/functions: `Server_ShowProperties` builds cached problems/general/scout property sheets. `Server_General_DlgProc` handles init, auth toggles, and address change. `Server_General_OnEndTask_InitDialog` renders `taskSVR_PROP_INIT` data. `Server_General_OnAuth` dispatches `taskSVR_SETAUTH` after warning for disable. `Server_General_OnChangeAddr` runs the address modal and starts `taskSVR_CHANGEADDR`. `Server_Scout_DlgProc` and helpers load/apply warning preferences through `taskSVR_SCOUT_INIT`/`taskSVR_SCOUT_APPLY`.

Control flow: General tab disables controls until status task returns, then enables auth/address controls and displays aggregate count, capacity, allocation, and addresses. Scout tab disables all controls until preference init returns, then initializes checkboxes and spinners for aggregate-full, fileset-full, service stop, server timeout, VLDB/server mismatch, aggregate allocation/no-server, and auto-refresh minutes.

State and persistence: General auth/address changes are remote server state via tasks. Scout apply sends `SVR_SCOUT_APPLY_PACKET`, which represents preference fields and auto-refresh period; persistence handled by task/server preference code. Spinners enforce percentage/minute bounds.

Dependencies/integration: Depends on `svr_address.h`, `svr_general.h`, `problems.h`, `propcache.h`, alert/preference structures, and task dispatch.

Risks: `WM_CTLCOLORLISTBOX` creates a new brush without ownership management. Auth disable warning is UI-only; task must still enforce authorization. Scout controls are enabled broadly after init; command handlers for all checkboxes must keep dependent controls in sync. Auto-refresh stores minutes but task code must convert to ticks consistently.

Test signals: Failed status/preference init, address list display, auth enable/disable confirmation, address change OK/cancel, each scout warning toggle and spinner, auto-refresh toggle, apply failure, and property sheet caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.h

Purpose: Declares server property task packets and UI entry point.

Important APIs/types: `SVR_SETAUTH_PARAMS` carries server identity and auth-enable flag. `SVR_SCOUT_APPLY_PACKET` carries warning toggles, warning percentages, and auto-refresh settings. `Server_ShowProperties` opens the property sheet.

Control flow/state: Packets are filled by property tabs and consumed by async tasks.

Dependencies/integration: Used by server property implementation and task dispatcher.

Risks/test signals: Confirm `WORD` percentage fields and `size_t` minute field map correctly to stored preference types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.cpp

Purpose: Implements singleton dialog for pruning `.BAK`, `.OLD`, and/or core files from a selected server.

Important APIs/functions: `Server_Prune` opens/focuses the dialog with default checkbox choices. `Server_Prune_DlgProc` handles lifecycle. `Server_Prune_OnInitDialog` sets checkboxes and starts server enumeration. `Server_Prune_EnableOK` requires a selected server and at least one prune option. `Server_Prune_OnOK` dispatches `taskSVR_PRUNE`.

Control flow: The dialog is cached under `pcSVR_PRUNE`. Server combo is disabled until `taskSVR_ENUM_TO_COMBOBOX` completes. OK dispatches the prune task and closes by fallthrough.

State and persistence: `SVR_PRUNE_PARAMS` stores target server and option booleans. No local persistence.

Dependencies/integration: Uses prop cache, server enumeration, task dispatch, and maintenance command resources.

Risks: Destructive operation is gated only by the dialog options; no additional confirmation is shown here. Task failures must be reported elsewhere. Singleton cache prevents independent prune dialogs for different servers.

Test signals: Default option combinations, no option selected disables OK, server enum failure, selected server dispatch, duplicate dialog focus, and prune-task error handling outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.h

Purpose: Declares server prune task packet and UI entry point.

Important APIs/types: `SVR_PRUNE_PARAMS` carries server identity and booleans for deleting `.BAK`, `.OLD`, and core files. `Server_Prune` opens the prune dialog with default options.

Control flow/state: The dialog fills the packet and starts `taskSVR_PRUNE`.

Dependencies/integration: Used by server maintenance menu commands.

Risks/test signals: Because defaults are true, command callers should be deliberate when invoking this destructive maintenance UI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.h -->
