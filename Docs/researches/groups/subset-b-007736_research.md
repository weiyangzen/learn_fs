# sources/distributed-fs/openafs/src/WINNT/afsusrmgr subset-b-007736 research

This grouped report covers the requested OpenAFS Windows Account Manager source files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.h

Purpose: declares the column-selection dialog entry point used by the main command layer when the user chooses the Columns command. It is intentionally tiny and only exposes `ShowColumnsDialog(HWND hParent, LPVIEWINFO lpvi = NULL)`.

Important APIs/types/functions: the function accepts an optional `LPVIEWINFO`; passing `NULL` lets the implementation infer the active view, while passing a view structure lets callers edit a specific FastList layout. It depends on `HWND` and `LPVIEWINFO` coming from the broader `TaAfsUsrMgr.h` include graph.

Control flow: this header has no logic. Runtime flow is initiated from `command.cpp` via `OnContextCommand(M_COLUMNS)`, which calls `ShowColumnsDialog(g.hMain)`.

State and persistence behavior: column state is represented by `VIEWINFO` arrays for available/shown columns, sort order, and widths. Persistence happens elsewhere through `gr.viewUsr`, `gr.viewGrp`, `gr.viewMch`, `RestoreSettings`, and `StoreSettings`.

Dependencies and integration points: integrates with FastList view-management code (`FL_StoreView`, `FL_RestoreView`) and with `resource.h` column dialog control IDs. The dialog affects display behavior in `display.cpp`.

Risks: because the default argument hides whether the active view or an explicit view is edited, regressions can misapply column changes to the wrong tab. The header also requires C++ compilation because of its default parameter.

Test signals: exercise Columns from each tab, change column order/width/visibility, switch tabs, restart the app, and verify persisted `VIEWINFO` settings remain tab-specific.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.cpp

Purpose: central command dispatcher for menus, context menus, accelerator commands, and keyboard-navigation behavior in the Account Manager UI.

Important APIs/types/functions: `OnRightClick`, `ShowContextMenu`, and `OnContextCommand` route user gestures. Command handlers include `Command_OnView`, `Command_OnShowActions`, `Command_OnRefresh`, `Command_OnUnlock`, `Command_OnProperties`, `Command_OnMembership`, `Command_OnChangePassword`, `Command_OnRename`, `Command_OnCreateUser`, `Command_OnCreateGroup`, `Command_OnCreateMachine`, and `Command_OnDelete`. Keyboard handlers emulate dialog behavior for tab, control-tab, return, context-menu, escape, and properties keys.

Control flow: right-clicks first collect the selected `ASIDLIST` from `Display_GetSelectedList`; header clicks open the column menu, while item/list clicks open user/group/machine menus. `OnContextCommand` switches on `resource.h` command IDs and forwards work to dialogs, async tasks, help, or display refresh logic. Selection-sensitive operations inspect `asc_ObjectTypeGet_Fast` and dispatch only homogeneous selections to user/group/machine property, membership, rename, delete, or password workflows.

State and persistence behavior: modifies restored UI state through `gr.fShowActions`, per-tab view structures, and icon-view settings. Mutating commands generally allocate task parameter objects or pass ASID lists to `StartTask`, leaving state refresh to task completion and display layers.

Dependencies and integration points: depends on `display.cpp` for selection and view changes, `creds.cpp` for cell/credential dialogs, user/group/machine modules for object dialogs, `action.cpp` for the operations window, `cell_prop.cpp` and `options.cpp` for application dialogs, and WinHelp/AfsAppLib for help flows.

Risks: ownership of `LPASIDLIST` is path-sensitive; handlers pass lists to dialogs/tasks or free them when unused. Mixed selections intentionally no-op after freeing the list, which can appear unresponsive. `Command_OnKey_Return` posts a double-click notification to the focused control's parent and assumes the focus window is a valid notification source.

Test signals: cover every menu and context-menu ID for no selection, single selection, multi-selection, mixed user/group/machine selection, and keyboard accelerators. Verify that disabled context-menu items (`M_CPW`, `M_RENAME`) match multi-selection constraints and that list/header right-clicks open the correct menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.h

Purpose: public command-layer interface for the Account Manager UI.

Important APIs/types/functions: defines `POPUPMENU` with `pmUSER`, `pmGROUP`, and `pmMACHINE`, plus `OnRightClick(POPUPMENU pm, HWND hList, POINT *pptScreen = NULL)` and `OnContextCommand(WORD wCmd)`.

Control flow: callers pass the active logical list type to `OnRightClick`; the implementation chooses the proper menu and either uses explicit screen coordinates or synthesizes coordinates for keyboard context-menu use. `OnContextCommand` receives `resource.h` command IDs from menus, buttons, and accelerators.

State and persistence behavior: no direct state in the header; implementation updates global restored settings and launches tasks/dialogs.

Dependencies and integration points: used by tab dialog procedures (`grp_tab.cpp`, `mch_tab.cpp`, and the analogous user tab) to route toolbar/button/menu IDs without duplicating command logic.

Risks: adding a new tab/object class requires extending `POPUPMENU` and the implementation switch. The default `POINT *` argument ties this header to C++.

Test signals: invoke `OnRightClick` from mouse and keyboard paths for all three popup types and confirm `OnContextCommand` routes all advertised `M_*` command IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.cpp

Purpose: owns cell-opening and credential-management dialogs and status display.

Important APIs/types/functions: `OpenCell_Hook_*` implements a hook procedure for the AfsAppLib open-cell dialog. Public operations are `OpenCellDialog`, `NewCredsDialog`, `CheckForExpiredCredentials`, `CheckCredentials`, and `ShowCurrentCredentials`. Helpers `GetBadCredsDlgParams` and `GetCredentialsDlgParams` build AfsAppLib parameter blocks.

Control flow: on OK in the open-cell dialog, controls are disabled, user/cell/password text is read, credentials are acquired with `AfsAppLib_SetCredentials`, then validated with `AfsAppLib_CheckCredentials`. If validation succeeds, `g.hCreds` is set and an async `taskOPENCELL` starts; the hook only closes the dialog after `WM_ENDTASK` reports success. Failures re-enable controls and show an error.

State and persistence behavior: updates `g.hCreds` and fills default credential dialog fields from `g.idCell` or the local cell. Bad-credential warning behavior points at `gr.fWarnBadCreds`, so user preference persists with restored settings.

Dependencies and integration points: depends on AfsAppLib credential/cell dialogs, admin server task queue, `ErrorDialog`, localized strings, and global `g`/`gr`. It is called from startup, menu commands, and periodic credential checks.

Risks: passwords are held in stack `TCHAR` buffers and not explicitly wiped. `g.hCreds` is assigned before `taskOPENCELL` succeeds, so failed open attempts rely on later handling to avoid misleading state. UI disabling/enabling must match every failure path.

Test signals: test good credentials, bad passwords, insufficient credentials with warnings enabled/disabled, task open failure after credentials succeed, expired credentials, no current cell, and status display for none/expired/valid credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.h

Purpose: declares the credential and cell-opening operations shared by startup, commands, and status refresh code.

Important APIs/types/functions: `OpenCellDialog` opens/selects a cell and returns dialog status; `NewCredsDialog` obtains replacement credentials; `CheckForExpiredCredentials` prompts on expiration; `CheckCredentials(BOOL fComplain)` validates current credentials; `ShowCurrentCredentials` updates the main window credential label.

Control flow: consumers call these functions around cell lifecycle events and before admin operations that require valid tokens.

State and persistence behavior: functions work against global current credentials (`g.hCreds`) and bad-credential warning preference (`gr.fWarnBadCreds`).

Dependencies and integration points: depends on AfsAppLib credential dialogs and on main-window controls such as `IDC_CREDS`.

Risks: the declaration says `OpenCellDialog` returns `int` while implementation returns `BOOL`; call sites compare to `IDOK`, so type/semantic drift is a maintenance hazard.

Test signals: compile with warnings for prototype/implementation mismatch and exercise startup/open-cell flows using the returned value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.cpp

Purpose: maintains list display population, active-tab selection helpers, FastList view refresh, lazy item text, column sorting, and work animation.

Important APIs/types/functions: `Display_StartWorking`/`StopWorking` reference-count the animation. `Display_Populate*List` reads tab filter text and starts `taskUPD_USERS`, `taskUPD_GROUPS`, or `taskUPD_MACHINES`. `Display_OnEndTask_Upd*` reconciles returned `ASIDLIST`s into FastList controls. `Display_RefreshView`, `Display_RefreshView_Fast`, `Display_SelectAll`, `Display_GetSelectedList`, `Display_GetSelectedCount`, `Display_GetActiveTab`, `Display_HandleColumnNotify`, `Display_GetItemText`, and `Display_GetImageIcons` form the display API.

Control flow: population starts only when `g.idCell` exists and the relevant list control is live. Completion handlers ignore stale async results by comparing `TASKDATA(ptp)->szPattern` to the current global pattern. They build a `HASHLIST` of returned ASIDs, remove no-longer-present FastList items, add new ones, and update title text. FastList lazy text callbacks call user/group/machine column functions based on the `VIEWINFO` cookie.

State and persistence behavior: uses global filter strings (`g.szPatternUsers`, `g.szPatternGroups`, `g.szPatternMachines`) and restored view/icon state (`gr.viewUsr`, `gr.viewGrp`, `gr.viewMch`, `gr.ivUsr`, `gr.ivGrp`, `gr.ivMch`). Column resize/click events store sort/column state through `FL_StoreView`.

Dependencies and integration points: depends on FastList, AfsAppLib image lists/animation, task packets, `usr_col`, `grp_col`, `mch_col`, `Main_SetMenus`, and OpenAFS admin cache APIs. It is the bridge between async task results and visible objects.

Risks: `l_cReqAnimation` must stay balanced across all task paths; extra stops hide active work, missing stops leave animation running. Several functions discover the active list by probing for group, then user, then machine list controls; dialog-layout changes could break this. `Display_GetImageIcons` has alert logic stubbed as always false.

Test signals: start overlapping refreshes, change search filters before completion, switch tabs during refresh, resize/click columns, select all, sort numeric and alphabetic columns, and verify no stale results replace current lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.h

Purpose: declares tab and FastList display services for account manager modules.

Important APIs/types/functions: defines `TABTYPE` (`ttUSERS`, `ttGROUPS`, `ttMACHINES`) and declares population, async completion, view refresh, selection, active-tab, column notification, lazy text, and icon-selection functions.

Control flow: tab dialogs and command handlers use these declarations to populate current lists and retrieve selected ASIDs for commands. FastList callbacks call `Display_GetItemText`, and notification handlers call `Display_HandleColumnNotify`.

State and persistence behavior: API operates on global windows and restored `VIEWINFO`/`ICONVIEW` records rather than caller-owned display state.

Dependencies and integration points: uses `LPTASKPACKET`, `LPVIEWINFO`, `LPASIDLIST`, `LPFLN_GETITEMTEXT_PARAMS`, `ICONVIEW`, and `ASID` from the larger OpenAFS Windows support headers.

Risks: all selection helpers assume the current tab child contains exactly one recognized list control. Adding tabs or changing resource IDs requires updating implementation heuristics.

Test signals: compile all callers after any signature changes and verify user/group/machine tabs all support populate, selection, column notification, and lazy text callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.cpp

Purpose: aggregates per-object operation failures and presents a single final error dialog.

Important APIs/types/functions: implements `ED_Create`, `ED_Free`, `ED_RegisterStatus`, `ED_GetFinalStatus`, and `ED_ShowErrorDialog`. The visible snippet shows freeing, registering failed ASIDs and status, and choosing single vs multiple error messages.

Control flow: callers create an `ERRORDATA` with message IDs, register each operation result, and finally show the aggregated dialog. `ED_RegisterStatus` ignores successes, increments failure count on failures, stores the last status, and appends the failed object ASID to an internal list.

State and persistence behavior: state is in the heap `ERRORDATA` object and its `LPASIDLIST`; there is no persisted state. `ED_GetFinalStatus` returns the aggregate status for caller decisions.

Dependencies and integration points: uses `asc_AsidListCreate/AddEntry/Free`, `CreateNameList`, localized error strings, and `ErrorDialog`. It is intended for batch operations such as multi-delete/change tasks.

Risks: only the last failure status is retained, so mixed failure causes can be collapsed. Dialog text depends on being able to resolve ASID names after an operation, which can fail after deletes or cache invalidation.

Test signals: register zero failures, one failure, and multiple failures; verify status return, name-list formatting, and object list cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.h

Purpose: declares the operation-error aggregation structure and API.

Important APIs/types/functions: `ERRORDATA` stores `cFailures`, `pAsidList`, `status`, and resource IDs for single and multiple error text. Public functions create, free, register per-object status, fetch final status, and show the dialog.

Control flow: batch task code can accumulate results independently of UI presentation, then show one summary.

State and persistence behavior: heap-owned transient state; no registry or global persistence.

Dependencies and integration points: depends on `LPASIDLIST`, `ASID`, and `ULONG` status conventions used by the OpenAFS admin client.

Risks: callers must call `ED_Free` exactly once and must not retain `pAsidList` entries after freeing. Message IDs must match format expectations used by `ED_ShowErrorDialog`.

Test signals: validate allocation/free with no registered failures and with failed ASIDs; check leak tooling around early returns in batch operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.cpp

Purpose: shared formatting, parsing, sort, list-name, and utility functions for account manager dialogs and FastList controls.

Important APIs/types/functions: `fIsValidDate`, `FormatElapsedSeconds`, `CreateNameList`, `GetLocalSystemTime`, `FormatServerKey`, `ScanServerKey`, `General_ListSortFunction`, `AppendUID`, `GetEditText`, and overloaded `fIsMachineAccount`.

Control flow: `FormatElapsedSeconds` appends localized weeks/days/hours/minutes/seconds parts. `CreateNameList` resolves each ASID name, optionally appends UID from object properties, and joins using the locale list separator. `General_ListSortFunction` uses static cached sort context initialized by FastList sentinel calls, dispatches to `User_GetColumn` or `Group_GetColumn`, and compares by column type. Server-key routines encode/decode `ENCRYPTIONKEYLENGTH` bytes using backslash triples.

State and persistence behavior: uses a static cached locale separator and static sort context within the sort callback. No disk persistence, but it reads global `g.idClient`, `g.idCell`, and restored `gr.view*` sort definitions.

Dependencies and integration points: depends on localized resource strings, `usr_col`/`grp_col`, FastList sort API, OpenAFS object property cache, and Windows time conversion APIs.

Risks: `ScanServerKey` relies on `_istdigit`/`isdigit` style digit checks and fixed triple parsing; malformed input can fail late. `General_ListSortFunction` returns numeric differences directly, which can overflow for large values. Static cached sort context is not reentrant.

Test signals: sort all column types, create name lists with missing objects and locale-specific separators, round-trip server keys including all-zero hidden keys, and classify machine-account names composed only of dots/digits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.h

Purpose: shared utility declarations and column-sort type definitions.

Important APIs/types/functions: defines `COLUMNTYPE` (`ctALPHABETIC`, `ctNUMERIC`, `ctDATE`, `ctELAPSED`) and `GetColumnFunction`. Declares date validation, elapsed formatting, ASID name-list creation, local time conversion, server-key formatting/scanning, FastList sort callback, UID appending, edit-text allocation, and machine-account detection.

Control flow: consumed by column modules, delete dialogs, property dialogs, and FastList sorting.

State and persistence behavior: header itself has none; declared functions often read global cell/client and restored view state.

Dependencies and integration points: ties generic display/sort code to OpenAFS `ASID`, Windows `SYSTEMTIME`, and FastList `HLISTITEM` types.

Risks: function signatures expose caller-owned buffers without sizes for several formatting functions, so callers must pass resource-sized buffers.

Test signals: build with all callers after utility signature changes and run UI paths that sort, format names, and parse encryption keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.cpp

Purpose: defines default group-list column layout and values for lazy FastList display and sorting.

Important APIs/types/functions: `Group_SetDefaultView` initializes `VIEWINFO` with all group columns and default shown columns; `Group_GetColumn` maps `GROUPCOLUMN` values to text or `COLUMNTYPE`.

Control flow: default view starts in small-icon mode, exposes name, UID, and member count, and uses status icon view. `Group_GetColumn` retrieves `ASOBJPROP` through `asc_ObjectPropertiesGet_Fast`, then formats name, member count, UID, owner, or creator with numeric IDs when names are unavailable.

State and persistence behavior: no persistence itself; writes defaults into `gr.viewGrp` and `gr.ivGrp` during first-run initialization. Runtime column ordering is later persisted by settings storage.

Dependencies and integration points: used by `display.cpp`, `general.cpp` sorting, and startup defaults. Depends on `GROUPCOLUMNS` from `grp_col.h`, localized string IDs, and OpenAFS cached group properties.

Risks: formatting uses caller-provided buffers and `wsprintf`. Owner/creator output is alphabetic even when it falls back to numeric ID, which may surprise sort behavior.

Test signals: display and sort every group column with full properties, missing names, and large member/UID values; verify default first-run column choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.h

Purpose: declares group-list columns and their metadata.

Important APIs/types/functions: defines `GROUPCOLUMN` values `grpcolNAME`, `grpcolCMEMBERS`, `grpcolUID`, `grpcolOWNER`, and `grpcolCREATOR`. Static `GROUPCOLUMNS` maps columns to string resource IDs and default widths, with numeric columns right-justified. Declares `Group_SetDefaultView` and `Group_GetColumn`.

Control flow: `Group_SetDefaultView` consumes `GROUPCOLUMNS` to seed a `VIEWINFO`; FastList lazy text and sorting call `Group_GetColumn`.

State and persistence behavior: no direct state, but static metadata in a header means each including translation unit gets a copy.

Dependencies and integration points: includes `display.h` for `ICONVIEW`/`VIEWINFO` and relies on resource IDs in `resource.h`.

Risks: header-level non-const static table can diverge per translation unit if modified at runtime, although current code treats it as read-only. Column enum order must stay aligned with the table and persisted `VIEWINFO` column indexes.

Test signals: verify all `GROUPCOLUMN` enum values have table entries and resource strings; test compatibility of persisted column indexes after changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.cpp

Purpose: implements the new-group dialog, advanced defaults, input parsing, and task parameter creation.

Important APIs/types/functions: `Group_SetDefaultCreateParams`, `Group_ShowCreate`, `Group_Create_DlgProc`, `Group_Create_OnInitDialog`, `Group_Create_OnNames`, `Group_Create_OnID`, `Group_Create_OnAdvanced`, `Group_Create_OnOK`, and `Group_Create_OnEndTask_ObjectGet`.

Control flow: dialog initialization formats title with current cell, creates a negative-ID spinner, selects auto-ID, and starts `taskOBJECT_GET` to fetch cell max group ID. Name changes enable OK and disable manual ID when multiple names are detected. Advanced opens group properties in modal new-group mode. OK builds `GROUP_CREATE_PARAMS`, copies access permissions/members/owned groups, tokenizes names using localized separators plus whitespace, and starts `taskGROUP_CREATE`.

State and persistence behavior: defaults are stored in `gr.CreateGroup` after OK. The temporary `CREATEGROUPDLG` owns advanced member/owner ASID lists and frees them after dialog close.

Dependencies and integration points: depends on group property UI (`grp_prop.cpp`), spinner helpers, `FormatMultiString`, `StartTask`, OpenAFS cell properties, and resource IDs for the dialog.

Risks: name tokenization uses a fixed `cchNAME` buffer after copying the remaining string before truncating, so unusually long input is risky. Multiple-name creation forces auto IDs. Advanced property pointers are nulled before modal editing to avoid sharing stale lists.

Test signals: create one group with auto/manual ID, create multiple groups, use advanced permissions/members, cancel after advanced edits, and verify cell max group ID display updates from `taskOBJECT_GET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.h

Purpose: declares group creation defaults and dialog launcher.

Important APIs/types/functions: `Group_SetDefaultCreateParams(LPGROUPPROPINFO lpp)` and `Group_ShowCreate(HWND hParent)`.

Control flow: startup calls the default initializer for first-run restored settings; command handling calls `Group_ShowCreate` from `M_GROUP_CREATE`.

State and persistence behavior: default initializer prepares a `GROUPPROPINFO` that later lives in `gr.CreateGroup`.

Dependencies and integration points: depends on `GROUPPROPINFO` from `grp_prop.h` via the broader include graph.

Risks: changing `GROUPPROPINFO` requires updating default initialization or new groups may inherit undefined permissions.

Test signals: fresh settings should produce predictable access controls, owner/creator blanks, and no preselected members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.cpp

Purpose: implements group delete confirmation and task dispatch.

Important APIs/types/functions: `Group_ShowDelete`, `Group_Delete_DlgProc`, `Group_Delete_OnInitDialog`, `Group_Delete_OnDestroy`, and `Group_Delete_OnOK`.

Control flow: selected group `ASIDLIST` is passed as dialog user data. Initialization formats a single-group title from the object name or a multi-group title from `CreateNameList`. OK copies the ASID list and starts `taskGROUP_DELETE`; destroy frees the original list.

State and persistence behavior: transient dialog state only. Actual deletion and subsequent cache/list updates occur in background task/action layers.

Dependencies and integration points: called by `Command_OnDelete` for homogeneous group selections. Uses OpenAFS object-name cache, localized strings, and `StartTask`.

Risks: if `asc_ObjectNameGet_Fast` fails for a single group, title formatting may use uninitialized/empty text. Ownership is split between the original list freed on destroy and the copied list owned by the task.

Test signals: delete one group, multiple groups, groups with missing cache names, OK/cancel, and verify no list double-free after task dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.h

Purpose: exposes the group delete dialog entry point.

Important APIs/types/functions: declares `Group_ShowDelete(LPASIDLIST pGroupList)`.

Control flow: command handling passes ownership of selected group ASIDs to the delete dialog, which confirms and starts the delete task.

State and persistence behavior: no persistent state; passed ASID list is transient and freed by the dialog.

Dependencies and integration points: integrates with `command.cpp` selection dispatch and `taskGROUP_DELETE`.

Risks: callers must pass only groups; mixed-selection validation is performed before this API.

Test signals: ensure direct callers do not pass users or machines and that cancellation frees the list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_delete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.cpp

Purpose: implements group property sheets for existing groups and for advanced new-group settings, including general permissions, owner, members, and owned groups.

Important APIs/types/functions: public APIs are `Group_ShowProperties` overloads and `Group_FreeProperties`. Internal dialogs include `GroupProp_General_DlgProc` and `GroupProp_Member_DlgProc`; key handlers update dialogs, browse for owners/members, apply changes, fetch members/owned groups, and populate FastLists.

Control flow: `Group_ShowProperties` prevents duplicate property windows using `WindowList_Search`, creates a property sheet, and adds General and Member tabs. General init starts `taskOBJECT_LISTEN`; updates aggregate selected group properties, marking mixed values. Apply stores selected access controls and normalized owner name in `GROUPPROPINFO`. Freeing properties after sheet close launches `taskGROUP_CHANGE` for each group with mixed fields preserved from current properties. Member tab copies original ASID lists as cancel backups, fetches member/owned lists asynchronously when needed, uses browse dialogs to add objects, removes selected objects, and on apply starts `taskGROUP_MEMBERS_SET` and/or `taskGROUP_OWNED_SET`.

State and persistence behavior: `GROUPPROPINFO` carries selected group list, apply flags, mixed-value flags, owner/creator text, and cached member/owned lists. Dialog window data stores backup ASID lists so cancel can restore prior values. WindowList tracks modeless sheets by group ID or multi-group key.

Dependencies and integration points: depends on `winlist`, `browse`, `usr_col` display-name helpers, `StartTask`, PropSheet helpers, AfsAppLib context help, OpenAFS object properties, and resource IDs. Creation dialogs reuse this code for advanced defaults by passing `pGroupList == NULL`.

Risks: apply-on-destroy in `Group_FreeProperties` means property changes are launched when the sheet closes, so ownership and flags must be exact. Multi-group membership semantics use `lParam` to mean present in all groups vs mixed, and mistakes can add/remove membership too broadly. Async member fetch completion ignores later user edits if list pointers are already populated.

Test signals: single-group properties, multi-group mixed permissions, owner browse, duplicate-window prevention, member add/remove, owned-group add/remove, apply/cancel behavior, object-change notifications, and new-group advanced settings with no backing group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.h

Purpose: defines group property-sheet tabs, data model, and public property APIs.

Important APIs/types/functions: `GROUPPROPTAB` includes `gptANY`, `gptPROBLEMS`, `gptGENERAL`, and `gptMEMBERS`; `nGROUPPROPTAB_MAX` is 3. `GROUPPROPINFO` contains selected groups, modal/deletion flags, owner window handle, general permission values and mixed flags, owner/creator strings, and member/owned-group ASID lists. Public functions are `Group_ShowProperties` overloads and `Group_FreeProperties`.

Control flow: callers either pass an `LPASIDLIST` for existing groups or a prepared `GROUPPROPINFO` for advanced creation. Target tab selects initial property-sheet tab.

State and persistence behavior: the structure is the mutable state for property dialogs and is reused as part of `gr.CreateGroup` defaults.

Dependencies and integration points: depends on OpenAFS account access enums, ASID lists, and dialog/window types from the shared application headers.

Risks: fields with `_Mixed` flags must be interpreted together with values; forgetting to preserve mixed fields can overwrite multi-selection properties. Ownership flags (`fDeleteMeOnClose`, `fShowModal`) control lifetime and must be set by every caller.

Test signals: validate initialization for existing single, existing multi, and new-group advanced cases; check no stale ASID lists survive after `Group_FreeProperties`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.cpp

Purpose: implements the group rename and optional owner-change dialog.

Important APIs/types/functions: `Group_ShowRename`, `Group_Rename_DlgProc`, `Group_Rename_OnInitDialog`, `Group_Rename_OnDestroy`, `Group_Rename_OnNewName`, `Group_Rename_OnChangeOwner`, `Group_Rename_OnOK`, and `Group_Rename_UpdateDialog`.

Control flow: initialization registers object-listen notifications for the target group, fills current group/owner fields, and disables OK until a new name is entered. Owner-change opens a browse dialog restricted to one user or group. OK allocates a group-change/rename task parameter, reads new name and possibly owner, and starts background mutation. Destroy unregisters object listening.

State and persistence behavior: target `ASID` is stored in dialog user data. No persistent settings are changed, but background tasks mutate the OpenAFS protection database and refresh cached object state.

Dependencies and integration points: invoked only for a single selected group by `command.cpp`. Uses `browse`, object listeners, OpenAFS cached properties, and localized help/resources.

Risks: rename is disabled in context menu for multi-select, but direct callers must enforce single group. Owner text may include appended UID and must be stripped before use. Object notifications during the dialog can change displayed current values.

Test signals: rename a group, change owner to user/group, cancel browse, handle group deletion/change while dialog is open, and verify owner UID suffix is not submitted as part of the owner name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.h

Purpose: declares the group rename dialog entry point.

Important APIs/types/functions: `Group_ShowRename(HWND hParent, ASID idGroup)`.

Control flow: command handling calls this for single selected group rename.

State and persistence behavior: no persistent state in the API; the implementation listens for object updates and starts mutation tasks.

Dependencies and integration points: uses OpenAFS `ASID` identity and a Win32 parent window.

Risks: the API does not encode object type, so callers must pass a group ASID.

Test signals: compile direct callers and assert only `TYPE_GROUP` selections reach this function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_rename.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.cpp

Purpose: dialog procedure for the Groups tab, including list setup, search debounce, context menu routing, and button enablement.

Important APIs/types/functions: `Groups_DlgProc`, `Groups_EnableButtons`, local timer constants `ID_SEARCH_TIMER` and `msecSEARCH_TIMER`, and a small static state record tracking last typed tick.

Control flow: init applies image lists/view settings, configures list callbacks, restores the group search pattern, and populates. Pattern edits start a debounce timer before calling `Display_PopulateGroupList`. Context-menu messages call `OnRightClick(pmGROUP, ...)`. Button/menu commands delegate to `OnContextCommand`. FastList item selection refreshes main menus and buttons; double-click posts Properties.

State and persistence behavior: writes the current group pattern into `g.szPatternGroups` through display population and uses restored group view/icon state in `gr.viewGrp`/`gr.ivGrp`.

Dependencies and integration points: depends on FastList, display helpers, command routing, main menu state, resource IDs, and AfsAppLib image lists.

Risks: debounce/timer behavior can issue refreshes after the tab is destroyed if timers are not killed on destroy paths. Button enablement is based only on selected count, while command dispatch later validates object type.

Test signals: type search filters quickly, switch tabs during debounce, use right-click and keyboard context menu, double-click group, select/deselect rows, and verify properties/membership buttons track selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.h

Purpose: declares the Groups tab dialog procedure.

Important APIs/types/functions: `BOOL CALLBACK Groups_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

Control flow: main tab construction uses this dialog proc for group-tab messages.

State and persistence behavior: implementation interacts with global search/view state but the header carries none.

Dependencies and integration points: Win32 dialog callback signature; integrated by main window/tab creation code.

Risks: signature must remain compatible with `DLGPROC`.

Test signals: tab creation should instantiate the Groups tab and route init, command, timer, notify, and context-menu messages to this proc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.cpp

Purpose: implements command lookup help, error-code translation, about dialog behavior, and context-help registration.

Important APIs/types/functions: public functions are `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`. Helpers include `lstrstr`, `Help_FindCommand_Search`, `NextSearch`, dialog procedures, error shrink/expand logic, and many static dialog-control-to-help-ID arrays.

Control flow: command help populates a combo from `aCOMMANDS`, skips leading utility words like `pts` or `kas`, does case-insensitive substring matching, and opens WinHelp at the matched context. Error help parses numeric input with `strtoul`, translates via `AfsAppLib_TranslateError`, strips duplicated numeric suffixes, and expands the dialog to show results. About dialog subclasses the OK button and uses timer/system-command messages plus `aSEARCHVALUES` for hidden text behavior. `Main_ConfigureHelp` registers the help file and per-dialog context maps.

State and persistence behavior: static arrays hold command mappings, packed search values, and help maps. No user settings are persisted.

Dependencies and integration points: depends on WinHelp, AfsAppLib help registration, localization resources, dialog resource IDs, and help context IDs from help headers/resources.

Risks: help mappings must stay synchronized with dialogs and `resource.h`; stale control IDs silently break F1/context help. `NextSearch` packed data logic is opaque and uses static command state. Parsing error input accepts C numeric bases but does not validate trailing garbage.

Test signals: search PTS/KAS command aliases, unknown/empty command input, translate decimal and hex error codes, context-help every registered dialog, and exercise about dialog close/subclass cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.h

Purpose: declares user-visible help operations and application help registration.

Important APIs/types/functions: `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`.

Control flow: menu commands call the first three functions; startup calls `Main_ConfigureHelp` before dialogs rely on context help.

State and persistence behavior: no persistent state in the header.

Dependencies and integration points: integrates the command menu in `command.cpp`, startup in `main.cpp`, and AfsAppLib help handling throughout dialog procs.

Risks: failing to call `Main_ConfigureHelp` early leaves `AfsAppLib_HandleHelp` without registered context maps.

Test signals: verify Help menu commands and F1/context help work immediately after startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/main.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/main.cpp

Purpose: application entry point, global state owner, startup/shutdown coordinator, message pump adapter, and thread helper.

Important APIs/types/functions: defines global `GLOBALS g` and `GLOBALS_RESTORED gr`. Implements `WinMain`, `InitApplication`, `ExitApplication`, `Quit`, `PumpMessage`, and `StartThread`.

Control flow: `WinMain` converts ANSI command line to `TCHAR`, initializes, runs `AfsAppLib_MainPump`, exits, frees the command line, and returns `g.rc`. Initialization loads locale resources, prevents duplicate instances via `FindWindow`, configures AfsAppLib and the task queue, registers help, restores or initializes persisted UI/default state, registers a custom dialog class, parses command line, creates the main modeless dialog, and optionally opens the cell dialog. Exit closes current cell and admin server. Quit saves main-window placement and restored settings, then posts quit.

State and persistence behavior: `gr` is restored from and stored to registry settings (`REGSTR_SETTINGS_*`, `REGVAL_SETTINGS`) with `wVerGLOBALS_RESTORED`. First-run defaults initialize create parameters, action/user/group/machine views, icon modes, refresh interval, and user search settings.

Dependencies and integration points: ties together locale loading, AfsAppLib task queue, command-line parsing, main window dialog proc, help, credentials, admin server lifecycle, user/group/machine defaults, action window defaults, and Windows thread/message APIs.

Risks: returning `FALSE` after creating `g.hMain` or acquiring credentials depends on `ExitApplication` handling partial initialization. Duplicate-instance detection relies on class/title consistency. `StartThread` does not close the created thread handle, which can leak handles if used often.

Test signals: fresh start, restored settings start, duplicate launch, `/close` or no-cell command-line paths, failed main dialog creation, cell-open cancel, normal quit with settings persistence, and task queue/thread creation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.cpp

Purpose: defines default machine-list column layout and displayed values. Machine accounts are represented as PTS user objects with machine-specific filtering.

Important APIs/types/functions: `Machine_SetDefaultView` and `Machine_GetColumn`.

Control flow: default view uses small icons, shows name and UID, and sets status icon mode. `Machine_GetColumn` retrieves `ASOBJPROP`, then formats name, group quota, UID, owner, or creator from `UserProperties.PTSINFO` when available.

State and persistence behavior: writes first-run defaults into `gr.viewMch` and `gr.ivMch`; persisted user changes are stored elsewhere.

Dependencies and integration points: consumed by `display.cpp` lazy text and startup defaults. Depends on `MACHINECOLUMNS`, OpenAFS cached user/PTS properties, and resource IDs.

Risks: if `fHavePtsInfo` is false, most machine columns remain blank while still reporting numeric/alphabetic type. The file comment says user-view columns, a stale comment that can mislead maintenance.

Test signals: display machines with full/missing PTS info, sort each machine column, and verify default shown columns and icon mode after first-run initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.h

Purpose: declares machine-list column enum, metadata table, and column accessors.

Important APIs/types/functions: `MACHINECOLUMN` values are `mchcolNAME`, `mchcolCGROUPMAX`, `mchcolUID`, `mchcolOWNER`, and `mchcolCREATOR`. `MACHINECOLUMNS` maps each to localized column IDs and widths, with numeric columns right-justified. Declares `Machine_SetDefaultView` and `Machine_GetColumn`.

Control flow: startup uses metadata for default `VIEWINFO`; display/sort code uses `Machine_GetColumn`.

State and persistence behavior: static header metadata only; runtime view persistence is stored in `gr.viewMch`.

Dependencies and integration points: includes `display.h`; depends on `resource.h` IDs and the machine tab/display modules.

Risks: enum order must remain compatible with persisted column indexes. Header-level static table creates one copy per translation unit.

Test signals: resource/string coverage for every machine column and compatibility after adding/reordering columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.cpp

Purpose: implements machine-account creation dialog using user creation task infrastructure with KAS disabled and PTS enabled.

Important APIs/types/functions: `Machine_SetDefaultCreateParams`, `Machine_ShowCreate`, `Machine_Create_DlgProc`, `Machine_Create_OnInitDialog`, `Machine_Create_OnNames`, `Machine_Create_OnID`, `Machine_Create_OnAdvanced`, `Machine_Create_OnOK`, and `Machine_Create_OnEndTask_ObjectGet`.

Control flow: initialization formats title with current cell, creates a positive UID spinner, selects auto-ID, and fetches cell max user ID with `taskOBJECT_GET`. Name changes enable OK and disable manual ID for multiple names. Advanced opens user properties in machine mode. OK builds `USER_CREATE_PARAMS` with blank password, PTS-only creation, machine defaults, membership/owned group lists, and tokenized machine names, then starts `taskUSER_CREATE`.

State and persistence behavior: default machine creation properties are initialized on first run and saved back to `gr.CreateMachine` after OK. Temporary advanced ASID lists are freed after dialog close.

Dependencies and integration points: reuses `usr_prop` and user-create task structures, spinner helpers, localized separators, `FormatMultiString`, and OpenAFS cell max UID properties.

Risks: machine-account validity is not visibly enforced here; names are merely tokenized. KAS fields are forced false/zero, so future machine-auth changes need explicit updates. Multiple names force auto IDs.

Test signals: create one machine with auto/manual UID, multiple machines, advanced membership/quota changes, cancel advanced edits, and verify task parameters set `fCreateKAS = FALSE` and `fCreatePTS = TRUE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.h

Purpose: declares machine creation defaults and dialog launcher.

Important APIs/types/functions: `Machine_SetDefaultCreateParams(LPUSERPROPINFO lpp)` and `Machine_ShowCreate(HWND hParent)`.

Control flow: startup initializes default machine creation state; command dispatch opens the new-machine dialog.

State and persistence behavior: default initializer fills `gr.CreateMachine` with machine-specific user property defaults.

Dependencies and integration points: depends on `USERPROPINFO` from user property modules.

Risks: machine defaults share a user-property structure, so user-only fields must remain deliberately disabled/zero for machine accounts.

Test signals: fresh settings should produce PTS-only machine defaults, no KAS creation, and expected quota/permission values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.cpp

Purpose: implements machine-account delete confirmation and task dispatch.

Important APIs/types/functions: `Machine_ShowDelete`, `Machine_Delete_DlgProc`, `Machine_Delete_OnInitDialog`, `Machine_Delete_OnDestroy`, and `Machine_Delete_OnOK`.

Control flow: selected machine ASIDs are stored in dialog user data. Initialization builds a single or multi-delete title. OK creates `USER_DELETE_PARAMS`, sets `fDeleteKAS = FALSE` and `fDeletePTS = TRUE`, copies selected machines into `pUserList`, and starts `taskUSER_DELETE`. Destroy frees the original ASID list.

State and persistence behavior: transient dialog state only; actual persisted data changes occur in the OpenAFS protection database via background task.

Dependencies and integration points: called by `Command_OnDelete` when selected user objects satisfy `fIsMachineAccount`. Uses user delete infrastructure rather than a separate machine task.

Risks: machine deletion deliberately does not touch KAS, so any machine credentials outside PTS are left intact. Like group delete, title formatting relies on object-name cache.

Test signals: delete one and multiple machines, ensure normal users do not reach this path, verify KAS deletion flag remains false, and validate cancel frees selected ASID list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.h

Purpose: declares the machine-account delete dialog entry point.

Important APIs/types/functions: `Machine_ShowDelete(LPASIDLIST pMachineList)`.

Control flow: command dispatch passes homogeneous machine selections to this function.

State and persistence behavior: no persistent state; selected ASID list is dialog-owned after the call.

Dependencies and integration points: integrates with command selection classification and user-delete task infrastructure.

Risks: API cannot enforce that ASIDs are machine accounts; callers must pre-filter.

Test signals: call path should only be reachable for names accepted by `fIsMachineAccount`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.cpp

Purpose: dialog procedure for the Machines tab, mirroring the Groups tab for machine-account search, display, and command routing.

Important APIs/types/functions: `Machines_DlgProc`, `Machines_EnableButtons`, local search timer constants, and static debounce state.

Control flow: initialization configures FastList image lists/view, lazy text callback, saved machine pattern, and initial population. Pattern edits debounce via timer before `Display_PopulateMachineList`. Context menus call `OnRightClick(pmMACHINE, ...)`; commands route through `OnContextCommand`; selection/double-click update menus/buttons or open properties.

State and persistence behavior: interacts with `g.szPatternMachines`, `gr.viewMch`, and `gr.ivMch`.

Dependencies and integration points: depends on display helpers, command routing, FastList, main menu state, and machine column metadata.

Risks: duplicated structure with `grp_tab.cpp` can drift. Properties/membership buttons are enabled purely by selection count; deeper command handlers decide whether selected machine ASIDs map to supported user property flows.

Test signals: quick filter typing, refresh debounce, right-click menu, double-click properties, selection enablement, and tab switch/destruction during pending timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.h

Purpose: declares the Machines tab dialog procedure.

Important APIs/types/functions: `BOOL CALLBACK Machines_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

Control flow: main tab creation uses this procedure to handle machine-tab messages.

State and persistence behavior: header contains no state; implementation reads/writes global machine tab view/search state.

Dependencies and integration points: Win32 `DLGPROC` callback signature and main window tab infrastructure.

Risks: must remain ABI-compatible with dialog procedure expectations.

Test signals: create Machines tab and verify init, timer, command, notify, and context-menu messages reach this callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/messages.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/messages.h

Purpose: defines private main-window messages used by the application.

Important APIs/types/functions: `WM_SHOW_YOURSELF` is `WM_USER + 0x100` and asks `g.hMain` to show itself after a cell is selected/opened; `WM_SHOW_ACTIONS` is `WM_USER + 0x101` and asks the main window to open the Operations In Progress window.

Control flow: startup/secondary-instance code and task/action code post or send these messages to the main window. `WM_SHOW_YOURSELF` carries a boolean force flag in `lp`.

State and persistence behavior: no direct state; messages trigger changes in visible window/action-window state.

Dependencies and integration points: included by `main.cpp` and main-window/action handling code. Numeric values must not collide with other app-private messages.

Risks: message payload convention is documented in comments but not type-checked. Future `WM_USER` ranges must avoid these IDs.

Test signals: duplicate launch should send/show the existing window; action tasks should open the actions window through `WM_SHOW_ACTIONS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.cpp

Purpose: implements the Options property sheet for regexp style, bad-credential warnings, and automatic refresh interval.

Important APIs/types/functions: `ShowOptionsDialog`, `Options_DlgProc`, `Options_OnInitDialog`, and `Options_OnApply`. Constants define refresh spinner bounds: min 1, default 60, max 10080 minutes, despite a stale comment saying min is 15 minutes.

Control flow: showing options creates a modal PropSheet with one `IDD_OPTIONS` tab. Init checks radio/checkboxes from `gr`, creates the refresh-rate spinner, and enables it only if refresh is checked. Apply copies selections back to `gr`; if refresh rate changed while a cell is open, it starts `taskSET_REFRESH`.

State and persistence behavior: updates restored settings `gr.fWindowsRegexp`, `gr.fWarnBadCreds`, and `gr.cminRefreshRate`. Persistence to registry occurs on `Quit`.

Dependencies and integration points: command menu calls `ShowOptionsDialog`; credential warning code reads `gr.fWarnBadCreds`; search code likely reads regexp mode; refresh scheduling uses `taskSET_REFRESH`.

Risks: apply does not immediately persist settings unless the app quits cleanly. Refresh-rate comment disagrees with the actual minimum. Toggling refresh only enables/disables the spinner; task scheduling changes happen on Apply.

Test signals: switch regexp modes, warning checkbox, disable refresh, set min/default/max refresh, apply with and without open cell, and verify `taskSET_REFRESH` only starts on actual interval changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.h

Purpose: declares the options dialog launcher.

Important APIs/types/functions: `ShowOptionsDialog(HWND hParent)`.

Control flow: `OnContextCommand(M_OPTIONS)` calls this function with the main window as parent.

State and persistence behavior: implementation edits `gr` restored settings and relies on application quit for registry persistence.

Dependencies and integration points: connected to command menu, help registration for `IDD_OPTIONS`, credential warnings, search behavior, and refresh scheduling.

Risks: single entry point hides which settings are changed; future options need synchronized UI, restored struct, and persistence versioning.

Test signals: compile command handler and verify Options menu opens modal dialog with the expected parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/resource.h -->
## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/resource.h

Purpose: generated-style resource ID registry for strings, icons, bitmaps, accelerators, menus, dialogs, controls, and command IDs used by the Account Manager.

Important APIs/types/functions: defines `IDS_*` strings for titles, column names, actions, help messages, errors, account permissions, delete/create/property text, and machine/user/group labels. Defines `IDI_*`, `IDB_*`, `ACCEL_MAIN`, `MENU_*`, `IDD_*`, `IDC_*`, and `M_*` command IDs. Private control IDs cover main tab/list controls, property dialogs, create/delete dialogs, browse dialogs, credentials, options, and search.

Control flow: most modules switch on `M_*` command IDs from menus/buttons/accelerators; dialog procs address controls with `IDC_*`; help registration maps `IDD_*` and `IDC_*` IDs to help contexts.

State and persistence behavior: no runtime state, but numeric IDs are persistent build-time contracts across `.rc`, help maps, menus, accelerators, and code.

Dependencies and integration points: included broadly by application headers and generated resource compilation. It is central to `command.cpp`, `helpfunc.cpp`, tab dialogs, property dialogs, and options.

Risks: duplicate numeric IDs are normal in dialog-local control spaces but risky if reused in the same dialog or command context. Changing resource IDs without updating help maps and command switches breaks UI behavior silently. `_APS_NEXT_*` values must stay coherent for resource editor use.

Test signals: full resource compile, menu command routing for every `M_*`, context help for every registered dialog, dialog smoke tests checking each referenced control exists, and accelerator tests for keyboard command IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/resource.h -->
