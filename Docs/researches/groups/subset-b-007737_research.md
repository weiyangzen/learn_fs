# Research Report: subset-b-007737

This grouped report covers the OpenAFS Windows user manager, aklog, linked-list, and BOS control service files assigned to `subset-b-007737`. Each section is source-path aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.cpp

Purpose: implements the asynchronous task dispatcher for the Windows AFS User Manager. `CreateTaskPacket`, `PerformTask`, and `FreeTaskPacket` wrap all admin-server work in `TASKPACKET` objects and route `TASK` enum values to concrete handlers for cell open, cache refresh, user/group CRUD, membership/ownership changes, object lookup/listen, credential refresh, and random key retrieval.

Important APIs and control flow: most handlers call `asc_*` admin client APIs against global `g.idClient`/`g.idCell`, populate `TASKDATA(ptp)`, update `ptp->rc` and `ptp->status`, and then refresh UI state with `Display_PopulateList`, `Display_RefreshView_Fast`, `ShowCurrentCredentials`, or action notifications. Multi-object setters use `HASHLIST` and `ERRORDATA` to compute deltas, continue after per-object failures, and show aggregate error dialogs. `TranslateRegExp`, `WeedAsidList`, and `PerformRefresh` provide shared filtering and cache invalidation logic.

State, persistence, and dependencies: this file owns many `lpUser` payloads passed from dialogs and frees them after task completion; ASID lists and action lists are freed through OpenAFS admin helpers. It mutates global app state (`g.idCell`, credentials handle, selected cell text) and preference-driven refresh rate `gr.cminRefreshRate`, but durable persistence is elsewhere. Dependencies include `TaAfsUsrMgr.h`, `messages.h`, credentials/action/display/user-column helpers, Windows messaging, the AFS admin client library, and app-specific allocation/string helpers.

Risks and test signals: lifetime ownership is the main risk: incorrect `lpUser` or `TASKDATA` freeing would leak or double-free ASID lists. Multi-step creates can leave partially created users/groups if property or membership updates fail. Test through mocked/admin test cells for each `TASK` branch, partial-failure aggregate dialogs, wildcard translation modes, machine/user filtering, refresh invalidation, and credential update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.h

Purpose: declares the task protocol shared by UI dialogs and the background task executor. It defines parameter blocks for opening cells, changing/creating/deleting users and groups, setting membership and ownership lists, translating names to ASIDs, listening for object notifications, and changing cell max IDs.

Important APIs/types: the `TASK` enum is the central dispatch contract consumed by `PerformTask` in `task.cpp` and by callers through `StartTask`. `TASKPACKETDATA` is the common return structure carrying cell/object IDs, ASID/action lists, search pattern, object type/properties, membership flag, and random key bytes. `TASKDATA(_ptp)` casts `ptp->pReturn` to this return payload.

State and dependencies: the header depends on AFS admin-server types such as `ASID`, `ASIDLIST`, `ASOBJPROP`, `AFSADMSVR_CHANGEUSER_PARAMS`, and `ACCOUNTACCESS` through the umbrella application headers. It does not persist state, but it encodes ownership expectations in comments: many enum cases take heap-allocated structs, cloned strings, or ASID lists that `task.cpp` frees.

Risks and test signals: adding a task requires updating the enum, caller payload type, dispatcher, result cleanup, and possibly `FreeTaskPacket`. Tests should verify every task id has a dispatch branch and that payload/list ownership matches the comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.cpp

Purpose: supplies default user-list view settings and converts cached user object properties into displayable column values for FastList/list views.

Important APIs and control flow: `User_SetDefaultView` initializes `VIEWINFO` with all user columns, default sort by name, five visible columns, and status icon view. `User_GetColumn` calls `asc_ObjectPropertiesGet_Fast`, switches over `USERCOLUMN`, formats text/date/elapsed/numeric values from KAS and PTS fields, and sets `COLUMNTYPE` for sorting. `User_GetDisplayName` formats user name plus instance except for special `admin` and `krbtgt` entries; the ASID overload falls back to `asc_ObjectNameGet_Fast`. `User_SplitDisplayName` splits dotted names into name/instance except machine accounts.

State and dependencies: this module reads cached admin-server object properties through global `g.idClient`/`g.idCell` and uses UI formatting helpers (`GetString`, `FormatTime`, `FormatElapsedSeconds`, `FormatServerKey` indirectly via dependencies). It does not own durable state.

Risks and test signals: column formatting assumes buffers are large enough for `wsprintf` and string concatenation. Display-name parsing must preserve machine account names and hide only the intended special instances. Test signals include column sort type correctness, mixed KAS/PTS availability, expiration and lifetime formatting, and dotted principal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.h

Purpose: defines the user-list column model for the AFS User Manager.

Important APIs/types: `USERCOLUMN` enumerates name, flags, KAS booleans, dates, lifetimes, lockout counts, quota, UID, owner, and creator columns. The static `USERCOLUMNS` table maps each enum entry to resource-string IDs and default widths/justification flags. Exports are `User_SetDefaultView`, `User_GetColumn`, `User_GetDisplayName`, and `User_SplitDisplayName`.

State and dependencies: includes `display.h` for `VIEWINFO`, `ICONVIEW`, `COLUMNTYPE`, and column flags. The header itself has no persistence, but the static table in a header means every including translation unit gets a private copy.

Risks and test signals: enum/table order must stay synchronized because comments and `User_GetColumn` switch logic depend on it. Tests should catch mismatched column captions, widths, sorting types, and display-name split behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.cpp

Purpose: implements the change-password/server-key dialog for a single user.

Important APIs and control flow: `User_ShowChangePassword` opens `IDD_USER_PASSWORD`. The dialog initializes by fetching current user properties and displaying the target user name; it lets the operator choose automatic or manual key version and string-derived or raw key data. `User_Password_OnType` enables OK only when a string password is present or `ScanServerKey` accepts raw key text. `User_Password_OnRandom` starts `taskGET_RANDOM_KEY`, and `User_Password_OnEndTask_Random` formats returned key bytes into the raw-key field. `User_Password_OnOK` builds `USER_CPW_PARAMS` and starts `taskUSER_CPW`.

State and dependencies: the target `ASID` is stored in `DWLP_USER`; real mutation is delegated to `task.cpp`. Dependencies include `usr_col` for display names, server-key scan/format helpers, spinner helpers, and the task framework.

Risks and test signals: raw key validation, manual key-version bounds, and random-key task failure handling are key risk points. Tests should cover string vs data paths, automatic vs manual versions, random-key failure disabling, and task payload contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.h

Purpose: exposes the user password/key-change dialog entry point.

Important APIs/types: declares `User_ShowChangePassword(HWND hParent, ASID idUser)`, which opens a modal UI for changing a selected user's password/server key. The implementation uses `USER_CPW_PARAMS` from `task.h` for the actual admin operation.

State and dependencies: no local state or persistence. It depends on Windows `HWND` and AFS `ASID` types through the application include graph.

Risks and test signals: API misuse risk is limited to passing a non-user ASID or invalid parent window. Tests should confirm callers only enable it for single selected users and that the dialog delegates to `taskUSER_CPW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.cpp

Purpose: implements the new-user dialog and default creation settings.

Important APIs and control flow: `User_SetDefaultCreateParams` initializes `USERPROPINFO` defaults for KAS/PTS creation, tickets, quota, ACLs, password policy, and lockout. `User_ShowCreate` copies persisted defaults from `gr.CreateUser`, opens `IDD_NEWUSER`, and frees temporary membership/ownership lists. The dialog validates password presence and confirmation, supports auto/manual UID, disables manual UID for multiple names, opens the advanced property sheet for initial properties/memberships, splits names into a multi-string, and starts `taskUSER_CREATE`.

State and dependencies: `CREATEUSERDLG` holds dialog-local password, UID, and advanced property state. Defaults are saved back to `gr.CreateUser` after successful OK. Cell max user ID is fetched asynchronously via `taskOBJECT_GET` to show the next auto ID.

Risks and test signals: multi-name parsing and UID behavior are sensitive; auto/manual ID must be disabled correctly for batch creation. Password validation is UI-side only before task delegation. Test single and multiple names, separator handling, password mismatch, advanced membership preservation, and object-get failure or stale max-ID display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.h

Purpose: declares new-user creation helpers for the Windows User Manager.

Important APIs/types: `User_SetDefaultCreateParams` fills a `USERPROPINFO` structure with baseline new-user defaults, and `User_ShowCreate` opens the modal create dialog.

State and dependencies: depends on `USERPROPINFO` from `usr_prop.h`, Windows dialog handles, and global runtime settings in the implementation. The header has no state.

Risks and test signals: creation defaults are part of user-visible behavior, so tests should verify the defaults after reset/startup and that callers use `User_ShowCreate` rather than constructing task payloads inconsistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.cpp

Purpose: implements the user deletion confirmation dialog.

Important APIs and control flow: `User_ShowDelete` opens `IDD_USER_DELETE` with an ASID list. Initialization formats either a single display name or a multi-user name list and defaults both KAS and PTS deletion checkboxes to checked. `User_Delete_OnCheck` prevents OK when neither backing database is selected. `User_Delete_OnOK` copies the ASID list into `USER_DELETE_PARAMS`, records KAS/PTS delete flags, and starts `taskUSER_DELETE`.

State and dependencies: the selected user list is stored in `DWLP_USER` and freed on dialog destroy. Actual deletion and aggregate error reporting live in `task.cpp`. Dependencies include user display-name formatting, ASID-list helpers, resource strings, and task dispatch.

Risks and test signals: ownership of the passed ASID list is important because this dialog frees it. Tests should cover single vs multi-title formatting, checkbox gating, copying lists before task start, and deleting only KAS or only PTS records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.h

Purpose: exposes the user deletion confirmation entry point.

Important APIs/types: declares `User_ShowDelete(LPASIDLIST pUserList)`, which assumes ownership of the selected ASID list through the dialog lifecycle and delegates real deletion to `taskUSER_DELETE`.

State and dependencies: no persistent state. Depends on ASID-list types and Windows UI infrastructure through the application headers.

Risks and test signals: callers must pass a valid, heap-managed ASID list and should not reuse it after invoking the dialog. Tests should verify selected-list ownership and task payload creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_delete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.cpp

Purpose: implements user and machine account property sheets, including general security settings, advanced KAS/PTS properties, and group membership/ownership pages. It supports existing users, multiple selected users, and new-user/new-machine property editing.

Important APIs and control flow: `User_ShowProperties` prevents duplicate property windows with `WindowList`, builds a tabbed property sheet, and selects the requested tab. General and advanced tabs subscribe to object notifications with `taskOBJECT_LISTEN`, read current properties from the local admin cache, compute mixed states for multi-select, and write pending values back into `USERPROPINFO` on apply. `User_FreeProperties` performs final writes by building `USER_CHANGE_PARAMS` per selected user and starting `taskUSER_CHANGE`, warning before changing system accounts. Membership tab gets current groups via `taskGROUP_SEARCH`, marks common vs partial membership through ASID `lParam`, uses the browse dialog to add groups, removes selected groups, and starts `taskUSER_GROUPLIST_SET` on apply.

State and dependencies: `USERPROPINFO` is the shared cross-tab state object. Dialog window data stores backup ASID lists so cancel/destroy can restore membership state. Dependencies include `usr_cpw`, `usr_col`, `winlist`, `browse`, PropSheet helpers, FastList, date/time/elapsed controls, task dispatch, and admin-cache property APIs.

Risks and test signals: mixed tri-state handling can accidentally overwrite fields if the `_Mixed` flags are wrong. Time conversion between GMT account expiration and local UI controls is another risk. Membership backup/restore and ASID-list ownership are delicate. Test single/multi-user properties, system-account warning cancellation, apply order, notification refresh, machine-account tab set, membership add/remove for full and partial groups, and create-mode defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.h

Purpose: defines the user property-sheet public model and constants.

Important APIs/types: constants define ticket lifetime, group quota, password-expiration, and quota boundaries. `USERPROPTAB` names selectable tabs. `USERPROPINFO` is the central state structure for property editing: target user list, modal/modeless behavior, machine flag, apply flags, general password/expiration/lockout fields, advanced KAS/PTS fields, ACL access values, mixed-state flags, and membership/ownership ASID lists. Exports are `User_ShowProperties` overloads and `User_FreeProperties`.

State and dependencies: the structure bridges create dialogs, property sheets, and task payload generation. It stores pending user edits but no durable data itself.

Risks and test signals: this header is a cross-module contract; adding fields requires updating initialization, copy, apply, and free paths. Tests should cover default initialization, modal create-mode behavior, mixed-state preservation, and ASID-list ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.cpp

Purpose: implements the advanced user search dialog and default search settings.

Important APIs and control flow: `Users_SetDefaultSearchParams` resets `AFSADMSVR_SEARCH_PARAMS` to `SEARCH_NO_LIMITATIONS`. `Users_ShowAdvancedSearch` opens `IDD_SEARCH_USERS`. Initialization mirrors `gr.SearchUsers` into radio buttons and date controls. OK updates `gr.SearchUsers` for all users, account expiration before a date, or password expiration before a date; if the structure changed, it calls `Display_PopulateList`.

State and dependencies: persistent search state lives in global `gr.SearchUsers`; this module only edits it. Dependencies include date controls (`DA_SetDate`, `DA_GetDate`), resource IDs, and display population.

Risks and test signals: date values are only meaningful for the selected search type, so tests should verify switching search modes preserves expected dates and triggers refresh only when the effective structure changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.h

Purpose: declares the advanced user search helpers.

Important APIs/types: exports `Users_ShowAdvancedSearch(HWND hParent)` and `Users_SetDefaultSearchParams(LPAFSADMSVR_SEARCH_PARAMS)`.

State and dependencies: depends on AFS admin search parameters and Windows UI handles. Search persistence is external in global preferences.

Risks and test signals: callers should refresh user lists after changed search settings. Tests should verify default parameters and dialog-to-global update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.cpp

Purpose: implements the Users tab dialog in the main AFS User Manager window.

Important APIs and control flow: `Users_DlgProc` initializes tab sizing, image lists, sort and text callbacks, restores `gr.viewUsr`, loads the pattern edit from `g.szPatternUsers`, and calls `Display_PopulateUserList`. Pattern changes start a debounce timer (`msecSEARCH_TIMER`) before repopulating. The Advanced button opens `Users_ShowAdvancedSearch`; context commands are routed through `OnContextCommand`; selection notifications update menus and buttons; double-click opens properties.

State and dependencies: stores last type tick in a file-static `l`. View state is persisted externally in `gr.viewUsr` through `FL_RestoreView`/`FL_StoreView`. Dependencies include FastList, display callbacks, command routing, window menu updates, and resize helpers.

Risks and test signals: timer debounce and global pattern synchronization are likely UI regressions. Tests should cover view restoration, selection-driven button/menu enablement, double-click behavior, and refresh after search text edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.h

Purpose: exposes the Users tab dialog procedure.

Important APIs/types: declares `Users_DlgProc(HWND, UINT, WPARAM, LPARAM)`, the child dialog proc installed by `window.cpp` for the users tab.

State and dependencies: no state in the header. The implementation depends on FastList/display/command infrastructure.

Risks and test signals: the dialog proc is called by the tab framework, so signature compatibility and resource ID wiring are the main integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.cpp

Purpose: implements the main AFS User Manager dialog, tab host, and dynamic menu state.

Important APIs and control flow: `Main_DialogProc` installs `g.hMain`, handles show/activation/credential/refresh/action messages, routes completed update tasks to display handlers, and delegates commands to context command handling. `Main_OnInitDialog` restores the saved main window rectangle, creates the tab control image list and tab items, subclasses the tab control, sizes the child area, selects the last tab, and registers action listening. `Main_PrepareTabChild` destroys the old tab child and creates the new Users/Groups/Machines dialog. `Main_SetMenus` and `Main_SetViewMenus` enable, check, and radio-select operations based on current selection and tab view mode.

State and dependencies: uses global runtime/preferences (`g.hMain`, `g.idCell`, `gr.rMain`, `gr.iTabLast`, view settings, action-window flag). Dependencies include user/group/machine tab procs, command/action/credential/display helpers, Windows tab controls, resize helpers, and admin action listen APIs.

Risks and test signals: tab index and `aTABS` ordering must match `TABTYPE` expectations. Menu enablement depends on `Display_GetSelectedList` and cached object type. Tests should cover startup restoration, tab switching, resize forwarding, credentials messages, completed update tasks, and menu state for user/group/machine selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.h

Purpose: declares main-window entry points for the AFS User Manager UI.

Important APIs/types: exports `Main_DialogProc`, `Main_PrepareTabChild`, `Main_SetMenus`, and `Main_SetViewMenus`. These are used by startup code and tab/list dialogs when selection or view state changes.

State and dependencies: no state in the header; implementation uses globals in `g` and `gr`.

Risks and test signals: callers rely on these functions being safe when main window/tab controls exist. Tests should cover calling menu refresh after list selection changes and preparing explicit or current tab children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.cpp

Purpose: tracks open modeless property windows so the UI can prevent duplicate user/group/cell property sheets and focus existing windows.

Important APIs and control flow: `WindowList_Add` ignores duplicate HWNDs, reuses empty slots, grows the static array with `REALLOC`, stores window type and object ASID, and registers the modeless dialog with the app library. `WindowList_Search` returns the first live entry matching type and, unless `ASID_ANY`, object ID. `WindowList_Remove` nulls the HWND slot without compacting.

State and dependencies: file-static `aWindowList` and `cWindowList` hold process-local window registry state. It depends on `TaAfsUsrMgr.h`, modeless dialog registration, and allocation macros.

Risks and test signals: stale slots are tolerated but never compacted; leaks are small but long-lived. Search by object ID `0` is used for multi-object property windows, so tests should cover exact object lookup, `ASID_ANY`, duplicate add, remove, and reusing empty slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.h -->
# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.h

Purpose: declares the process-local modeless property-window registry.

Important APIs/types: `WINDOWLISTTYPE` differentiates user, group, and cell property windows. `ASID_ANY` is a wildcard for searches. Exports are `WindowList_Add`, `WindowList_Search`, and `WindowList_Remove`.

State and dependencies: no state in the header; implementation stores registry entries in a static array.

Risks and test signals: object ID `0` has semantic use for multi-selection windows, while `ASID_ANY` is `-1`; tests should verify callers do not confuse those cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/aklog.c -->
# sources/distributed-fs/openafs/src/WINNT/aklog/aklog.c

Purpose: implements the Windows/OpenAFS `aklog` command, acquiring Kerberos credentials for AFS service principals and installing AFS tokens for explicit cells or cells discovered by walking paths.

Important APIs and control flow: command-line parsing builds linked lists of cell/realm pairs and paths. `auth_to_cell` resolves cell configuration, avoids repeated attempts with `authedcells`, obtains Kerberos v5 tickets by trying user realm, cell realm, referral/fallback realm, and service forms `afs/<cell>` then `afs`, optionally converts through krb524 when built with Kerberos 4, builds `ktc_token`, optionally resolves/registers PTS identity in `ViceIDToUsername`, and calls `ktc_SetToken`. Linked cells are authenticated after the primary cell. `auth_to_path` resolves path components via `next_path`, detects AFS mount points with `pioctl`, extracts cells, and authenticates to each encountered cell. Helpers handle local cell config, realm discovery, dotted principal registry policy, WOW64 registry view, symlink traversal, and error redirection.

State and dependencies: global flags control debug, PRDB lookup, force replacement, Kerberos version, and krb5 context/ccache. External dependencies include Kerberos/Heimdal delay loading, AFS config, ptserver, ktc token APIs, pioctl, registry APIs, and the local linked-list utility. The command mutates token state in the AFS cache manager, not repository files.

Risks and test signals: security-sensitive risks include buffer copying with fixed arrays, service principal fallback logic, DES key derivation, duplicate-token comparison, cross-cell auto-registration, and registry-controlled dotted principals. Tests should cover no-arg local-cell auth, `-cell/-k`, `-path`, duplicate cell suppression, linked cells, missing Kerberos runtime, PRDB failures with `-noprdb`, `AFS_SMBNAME`, referral fallback, and bad path/symlink loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/aklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/aklog.h -->
# sources/distributed-fs/openafs/src/WINNT/aklog/aklog.h

Purpose: provides the public embedding interface and portability declarations for the aklog implementation.

Important APIs/types: `aklog_params` contains function pointers for filesystem, credential, output, and exit hooks, allowing an embeddable `aklog(int, char **, aklog_params *)` API in older builds. `aklog_init_params` initializes that hook table. It also defines `ARGS` for pre-ANSI compatibility and includes Kerberos/linked-list compatibility headers.

State and dependencies: includes AFS/Kerberos headers and `linked_list.h`; no runtime state is stored in the header. The current `aklog.c` in this subset implements a standalone `main` rather than visibly using the hook table.

Risks and test signals: stale public declarations can diverge from the implementation. Tests or build checks should verify whether embeddable `aklog` symbols are still provided elsewhere or should be reconciled with the standalone Windows command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/aklog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.c -->
# sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.c

Purpose: implements a minimal doubly linked list used by `aklog` for cell/path queues and duplicate string suppression.

Important APIs and control flow: `ll_init` initializes an empty list and aborts on NULL. `ll_add_node` allocates a node and inserts at head or tail. `ll_delete_node` scans for a node, relinks neighbors, frees the node, and decrements count. `ll_string_check` scans string data using `strcmp`. `ll_add_string` adds a `strdup` copy only if absent.

State and dependencies: list state is caller-owned in `linked_list`; node allocation uses C runtime `malloc/free`, and string data allocated by `ll_add_string` remains caller-owned for cleanup. Dependencies are only stdio/stdlib/string and the local header.

Risks and test signals: no list-level cleanup function exists, and node deletion does not free `data`; callers can leak strings. `ll_string_check` assumes every data pointer is a valid string. Tests should cover empty lists, head/tail insertion, delete first/last/missing node, duplicate string suppression, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.h -->
# sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.h

Purpose: declares the simple linked-list abstraction used by `aklog`.

Important APIs/types: defines `ll_node`, `linked_list`, `ll_end`, status constants, the `ll_add_data` macro, and functions for initialization, node add/delete, duplicate string checks, and unique string add.

State and dependencies: the header is standalone C and exposes struct layouts directly, so callers iterate nodes and manage stored data themselves.

Risks and test signals: direct struct access makes invariant enforcement caller-dependent. Tests should verify `nelements`, `first`, and `last` remain coherent after mixed head/tail operations and deletions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/aklog/linked_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/bosctlsvc/bosctlsvc.c -->
# sources/distributed-fs/openafs/src/WINNT/bosctlsvc/bosctlsvc.c

Purpose: implements the Windows SCM service wrapper that controls the AFS `bosserver`, including start, stop, and restart handling.

Important APIs and control flow: `main` registers `BosCtlMain` with `StartServiceCtrlDispatcher`. `BosCtlMain` initializes `SERVICE_STATUS`, creates stop/exit events, registers `BosCtlHandler`, opens firewall ports, initializes AFS server dir paths, installs a `SIGCHLD` handler, and calls `BosserverRun`. `BosserverRun` builds a `spawnprocve` argument vector for `AFSDIR_SERVER_BOSVR_FILEPATH`, marks process management as detached, starts/restarts the child, reports `SERVICE_RUNNING`, and waits for stop or child-exit events. `BosserverDoStopEvent` sends `SIGQUIT`, waits bounded time for child exit while updating SCM checkpoints, and reports timeout/failure. `BosserverDoExitEvent` distinguishes spurious SIGCHLD, restart exit codes via `BOSEXIT_DORESTART`, and terminal child exits.

State and dependencies: service status is protected by `bosCtlStatusLock`; `bosCtlEvent` handles coordinate SCM controls and signal events. Dependencies include Windows services/events, OpenAFS event logging, registry service name constants, process management, dirpath, bnode restart-code macros, and firewall configuration.

Risks and test signals: stop timeout behavior, child restart loops, SCM checkpoint reporting, and signal/event races are central risks. There is a potential uninitialized `status` path if the first event creation succeeds and the second fails before reporting resources. Tests should simulate SCM stop, bosserver clean exit, restart exit, spawn failure, event creation failure, SIGCHLD without wait status, and stop timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/bosctlsvc/bosctlsvc.c -->
