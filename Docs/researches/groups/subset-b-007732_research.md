<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/services_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/services_page.cpp

## Purpose
Implements the Services property page for the Windows OpenAFS server configuration tool. The page lets an administrator inspect and toggle file server, database server, backup server, system-control server, and system-control client configuration states before applying the requested changes.

## Important APIs, Types, And Functions
`ServicesPageDlgProc` is the exported dialog procedure. `ShowInitialConfig`, `ShowServiceStates`, `CheckEnableBak`, and `CheckEnableSc` keep the UI synchronized with `g_CfgData`. `PrepareToConfig(CONFIG_STATE&, BOOL, BOOL, UINT)` maps checkbox transitions into `CS_CONFIGURE` or `CS_UNCONFIGURE`; the no-argument `PrepareToConfig` gathers credentials, updates `g_CfgData`, and calls `Configure`. The file uses helper APIs such as `Configured`, `ShouldConfig`, `ShouldUnconfig`, `GetAdminInfo`, `GetHandles`, and `GetCurrentConfig`.

## Control Flow
Initialization snapshots current service configuration into static booleans, initializes status/action text, and bolds service labels. Command handling toggles requested state, updates dependent controls, and marks the property sheet changed when requested state diverges from running state. Applying first computes local config deltas, handles the last-database-server safety path, collects missing system-control and admin information, then commits local states into `g_CfgData` only immediately before running the configuration engine.

## State And Persistence
State is mostly dialog-static: `b*Running`, `b*On`, `bDbParial`, `szScMachine`, and `hDlg`. Persistent effects happen indirectly through `Configure`, which consumes the updated `g_CfgData` and changes installed/configured server roles. Successful config enables `g_CfgData.bReuseAdminInfo`; failed config clears the admin password.

## Dependencies And Integration Points
Depends on `afscfg.h`, resource identifiers, admin-info dialogs, current-config discovery, and the external `Configure` routine from `config_server_page.cpp`. It integrates with the Win32 property-sheet change protocol and with the larger configuration wizard state object `g_CfgData`.

## Risks And Edge Cases
System-control server and client are mutually exclusive, backup requires database service, and system-control requires either file or database service. The last DB server path forcibly unconfigures other roles and exits after configuration. A visible typo, `bDbParial`, appears to represent partial DB configuration but is never set in this file. `EnableScMachine` sets the edit text before `szScMachine` is copied from `g_CfgData` in the SCC-running branch, which may briefly display stale or empty text.

## Test Signals
Exercise initial display for all role combinations, backup disabled when DB is off, SCS/SCC mutual exclusion, SCC requiring a machine name, last-DB confirmation cancellation, admin credential reuse/failure, and property-sheet dirty-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/services_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/sys_control_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/sys_control_page.cpp

## Purpose
Implements the wizard step that chooses whether the machine becomes a system-control server, a system-control client, or is not configured for system control.

## Important APIs, Types, And Functions
`SysControlPageDlgProc` is the dialog procedure. `OnInitDialog` configures wizard buttons, evaluates whether the step can run, and adapts the layout for first-server installs. `CantConfig`, `EnableSysControlMachine`, `ShowSysControlMachine`, and `CheckEnableNextButton` manage disabled states and the required system-control-machine edit box.

## Control Flow
The dialog delegates common wizard handling to `WizStep_Common_DlgProc`, then responds to `IDNEXT`, `IDBACK`, radio buttons, and edit changes. Initialization blocks configuration if the machine is already SCS/SCC or is not a file/database server. First-server installs hide SCC controls and reposition the remaining choices because a first server cannot be a system-control client.

## State And Persistence
Selections are written directly to `g_CfgData.configSCS`, `g_CfgData.configSCC`, and `g_CfgData.szSysControlMachine`; persistence is deferred to later wizard configuration steps. The file also uses static `hDlg` and the external layout spacing `nOptionButtonSeparationHeight`.

## Dependencies And Integration Points
Depends on the wizard controller `g_pWiz`, global configuration state, common toolbox/window helpers, and resource text. It integrates with adjacent wizard steps `sidSTEP_TEN` and `sidSTEP_TWELVE`.

## Risks And Edge Cases
The Next button is disabled only for SCC with an empty machine name. The first-server layout manually moves controls, so resource-layout changes can introduce overlap. If an existing SCS/SCC state is detected, controls are hidden rather than merely disabled, which should be covered by visual regression testing.

## Test Signals
Validate transitions among all radio choices, empty/non-empty SCC machine input, already-configured SCS/SCC cases, non-file/non-DB server disabling, and first-server layout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/sys_control_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.cpp

## Purpose
Provides small Win32 UI utility wrappers used throughout the server configuration tool.

## Important APIs, Types, And Functions
Exports enable/show/text/check helpers (`SetEnable`, `ShowWnd`, `EnableWnd`, `SetWndText`, `GetWndText`, `SetCheck`, `IsButtonChecked`, `GetButtonState`), elapsed-time control adapters (`SetElapsedTime`, `GetElapsedTime`, `SecondsToElapsedTime`), list and spinner helpers (`AddLBString`, `ClearListBox`, `SetUpDownRange`), refresh/layout helpers (`ForceUpdateWindow`, `MoveWnd`), and presentation helpers (`MakeBold`, `MsgBox`, `HideAndDisable`, `ShowAndEnable`).

## Control Flow
Most functions translate a dialog/control ID to an HWND and call the underlying Win32 or AFS app-library API. `SecondsToElapsedTime` decomposes seconds into hours/minutes/seconds and builds a static string. `MoveWnd` converts screen coordinates to client coordinates before applying offsets.

## State And Persistence
No persistent application state is stored. `SecondsToElapsedTime` and `GetResString` return static buffers, so callers must consume or copy results before later calls. `MakeBold` creates a new font and assigns it to a control; this font is not explicitly deleted here.

## Dependencies And Integration Points
Depends on Win32 controls, `afsapplib` elapsed-time helpers, resource loading via `GetString`, and the local `ENABLE_STATE` enum from `toolbox.h`.

## Risks And Edge Cases
Static string buffers are not thread-safe and are overwritten by subsequent calls. `SetEnable` has no default initialization if an invalid enum is passed. `MakeBold` can leak fonts if called repeatedly without cleanup.

## Test Signals
Use UI smoke tests for enable/disable/show/hide behavior, elapsed-time round trips, spinner range setup, bold label rendering, and movement of controls under different DPI/layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.h

## Purpose
Declares shared UI helper functions and the `ENABLE_STATE` enum for the Windows server configuration dialogs.

## Important APIs, Types, And Functions
Defines `ENABLE_STATE { ES_DISABLE, ES_ENABLE, ES_TOGGLE }`. Declares wrappers for control enablement, elapsed time controls, text access, window refresh, checkbox/listbox/up-down operations, resource-string retrieval, bold font application, message boxes, and simple layout movement.

## Control Flow
This header has no runtime control flow. It supplies overloaded declarations, default parameters, and inline convenience functions such as `GetWndTextLength` and `MakeBold(HWND, UINT)`.

## State And Persistence
No state is declared here. Callers rely on implementation-level static buffers for some returned strings.

## Dependencies And Integration Points
Requires Win32 types and constants to be in scope, plus `cchRESOURCE` from the surrounding app headers. It is included by configuration pages and utility code that manipulate dialog controls.

## Risks And Edge Cases
The header declares `ShowWnd` twice with the same signature/default shape, which is harmless in C++ but noisy. The implementation of `SetCheck` takes an `int`, while the header exposes a `BOOL` default, yet callers in the codebase pass `BST_INDETERMINATE`; this relies on the compiled implementation signature being visible or compatible.

## Test Signals
Compilation across all users is the main signal. Pay attention to three-state checkbox callers and any compiler warnings around duplicate declarations or default arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.cpp

## Purpose
Centralizes basic input validation for AFS server configuration fields.

## Important APIs, Types, And Functions
`Validation_IsValid` dispatches by `VALIDATION_TYPE`. Only `CheckAfsPartitionName` performs real validation, by prepending `/vicep` to the user-supplied partition suffix and calling `cfg_HostPartitionNameValid`. `ShowError` formats a validation error message. Cell, password, UID, and server-name validators currently return true.

## Control Flow
The public function switches on validation type, receives an error resource ID by reference, and optionally shows an error if validation fails. Partition validation allocates an ANSI buffer, calls the AFS config library, sets an error resource for invalid names, and deletes the buffer.

## State And Persistence
No persistent state. Validation failures are reported through modal UI only when requested.

## Dependencies And Integration Points
Depends on AFS configuration APIs, conversion macro/function `S2A`, local resource IDs, and app-library message formatting.

## Risks And Edge Cases
The allocation length uses `strlen("/vicpe")`, which is likely a typo but the same length as `/vicep`; it is still brittle. The code uses `delete pszName` instead of `delete [] pszName`, which is undefined behavior. If allocation fails, the function returns true, effectively accepting invalid input. Several enum values are unimplemented but reported as valid.

## Test Signals
Validate partition suffixes accepted/rejected by `cfg_HostPartitionNameValid`; include allocation/error paths under instrumentation and tests proving unimplemented validation types are intentionally permissive or replaced with real checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.h

## Purpose
Declares validation categories and the public validation entry point for configuration dialogs.

## Important APIs, Types, And Functions
`VALIDATION_TYPE` includes AFS partition, cell, password, UID, server-name, filename, and path validation categories. `Validation_IsValid(TCHAR *pszInput, VALIDATION_TYPE type, BOOL bShowErorr = TRUE)` is the exported checker.

## Control Flow
No runtime control flow. Consumers pass a mutable `TCHAR*`, the category, and whether a UI error should be shown.

## State And Persistence
No state is declared.

## Dependencies And Integration Points
Requires Win32/TCHAR types and is implemented by `validation.cpp`. It is intended as the common validation API for wizard/property-page input.

## Risks And Edge Cases
The parameter name has a typo, `bShowErorr`. `VALID_FILENAME` and `VALID_PATH` are declared but not handled by the implementation, causing the default assertion/failure path if used.

## Test Signals
Compilation and static analysis should flag implementation/header coverage gaps for every enum value. Call sites should be checked before enabling filename/path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.cpp

## Purpose
Builds and refreshes the drive-selection FastList used when choosing Windows disk partitions suitable for AFS.

## Important APIs, Types, And Functions
`SetupDriveList` initializes image lists, columns, and sorting for a FastList control. `UpdateDriveList` clears and repopulates the list. Internals include `DRIVE_INFO`, `GetDriveInfo`, `FillDriveList`, `GetDriveSizeAsString`, `DoesDriveContainData`, `DriveHasRecycleBin`, `DoesDriveContainNT`, and `DriveListSortFunc`.

## Control Flow
Setup attaches disk/disabled/warning/AFS icons and creates Drive/Name-or-error/Size columns. Refresh reads the partition table, iterates `GetLogicalDrives`, filters to fixed drives with volume information, validates file system/compression/existing-AFS/data conditions, then inserts FastList rows with warning or disabled flags. Sorting places enabled drives before disabled drives and then sorts by drive text.

## State And Persistence
State is module-static `m_hDriveList`. The code reads live filesystem and partition-table state but persists nothing. The FastList row param carries the disabled flag for sorting.

## Dependencies And Integration Points
Depends on Win32 volume APIs, FastList, image-list helpers, AFS partition utilities (`ReadPartitionTable`, `IsAnAfsPartition`), and resource strings/icons.

## Risks And Edge Cases
The "drive has data" condition is treated as a warning image but the resource ID is named `IDS_ERROR_DRIVE_HAS_DATA`. `OnlyHasFolder` only inspects the first root entry before deciding if a recycle-bin folder is the only content. `DoesDriveContainNT` is currently unused due to a commented policy. `dwFlags` is assigned with `|=` after zeroing the struct; future non-zero initialization would matter.

## Test Signals
Test fixed/removable drives, NTFS/non-NTFS, compressed volumes, existing AFS partitions, empty drives, drives with only recycle-bin artifacts, and list sorting/selection-disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.h

## Purpose
Declares the drive-list setup and refresh API for configuration pages that need to display candidate AFS partitions.

## Important APIs, Types, And Functions
`SetupDriveList(HWND hDriveList)` binds the module to a FastList control and initializes columns/images/sorting. `UpdateDriveList()` refreshes the currently bound list from system drive state.

## Control Flow
No runtime control flow in the header. Callers are expected to call setup before update.

## State And Persistence
The implementation keeps the target control in module-static state, so the API represents a single active drive list per process/module.

## Dependencies And Integration Points
Includes `toolbox.h` for Win32/helper context and is implemented by `volume_utils.cpp`.

## Risks And Edge Cases
Because `UpdateDriveList` has no HWND parameter, using multiple drive-list controls concurrently would overwrite shared state. Missing setup before update leaves the implementation operating on a null handle.

## Test Signals
Compile all users and run UI flows that create/destroy the drive-list page multiple times to catch stale control handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.cpp

## Purpose
Implements the Windows Control Panel applet entry point for OpenAFS server configuration.

## Important APIs, Types, And Functions
Exports `CPlApplet`. `LoadResString` loads localized strings. `GetInstallDir` reads the OpenAFS server install directory from the registry. The applet reports one item, fills `NEWCPLINFO`, loads an icon, and launches `afssvrcfg.exe` on double-click.

## Control Flow
`CPL_INIT` loads module handles/resources, initializes app name, and constructs the executable path from install dir plus `\usr\afs\bin\afssvrcfg.exe`. `CPL_GETCOUNT` returns one applet. `CPL_NEWINQUIRE` fills display metadata. `CPL_DBLCLK` runs the config executable with `WinExec` and reports launch failure. `CPL_EXIT` frees the locale resource module.

## State And Persistence
Static state holds module handles and app/path strings. The only external state read is the registry install directory; no registry values are written.

## Dependencies And Integration Points
Depends on Win32 Control Panel APIs, OpenAFS registry constants, `RegOpenKeyAlt`, and `TaLocale` resource loading. It integrates Control Panel with the separate `afssvrcfg.exe` application.

## Risks And Edge Cases
Fixed-size 256-byte buffers and `sprintf`/`strcpy` can truncate or overflow if install paths or localized strings exceed assumptions. `WinExec` is legacy and provides weak error reporting. If registry lookup fails, the executable path becomes only the suffix and likely fails to launch.

## Test Signals
Test applet initialization with valid/missing registry install directories, localized resource module loading, icon load failure, and double-click launch behavior on systems with long install paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.h

## Purpose
Declares the Control Panel applet entry point with C linkage.

## Important APIs, Types, And Functions
`LONG APIENTRY CPlApplet(HWND hwndCPl, UINT uMsg, LONG lParam1, LONG lParam2)` is declared inside an `extern "C"` guard for C++ consumers.

## Control Flow
No runtime control flow. The Windows Control Panel host calls `CPlApplet` with standard CPL messages.

## State And Persistence
No state is declared.

## Dependencies And Integration Points
Requires Windows API types and is implemented by `cpl_interface.cpp`.

## Risks And Edge Cases
The legacy signature uses `LONG` for parameters, matching older CPL examples; pointer-sized values on modern builds must be reviewed if this code is ported.

## Test Signals
Successful Control Panel loading and exported-symbol discovery are the primary test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcpa/resource.h

## Purpose
Defines resource identifiers for the OpenAFS server Control Panel applet.

## Important APIs, Types, And Functions
String IDs include icon-load error, title, execution error, and app name. `IDI_AFSD` identifies the applet icon.

## Control Flow
No runtime control flow.

## State And Persistence
No state is declared.

## Dependencies And Integration Points
Consumed by `cpl_interface.cpp` and corresponding resource script/localization modules.

## Risks And Edge Cases
String IDs start at zero, so resource tooling and localization files must agree exactly. Missing or mismatched resources degrade applet metadata and error messages.

## Test Signals
Resource compilation and runtime `CPL_NEWINQUIRE` string/icon loading verify this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.cpp

## Purpose
Tracks long-running server-manager operations and presents progress/action windows for the OpenAFS Windows server manager.

## Important APIs, Types, And Functions
`ActionNotification_MainThread` maps AFSClass notification events to action begin/update/end handlers. Public functions include `Action_OpenWindow`, `Action_CloseWindow`, `Action_SetDefaultView`, `Action_WindowToTop`, `Action_fAnyActive`, and `Action_ShowConfirmations`. Core internal types are `ACTIONTYPE` and `ACTION`; core helpers are `Action_Begin`, `Action_Find`, `Action_End`, `Action_GetDescription`, and `Action_Window_Refresh`.

## Control Flow
Notifications enter from dispatch on the UI thread. Simple operations create an action record on begin and remove it on end. Refresh operations create a modeless refresh dialog and receive percent/section messages. Move, dump, restore, and open-cell operations create modeless animation dialogs. The actions window periodically refreshes elapsed time with a timer and displays active actions in a FastList.

## State And Persistence
Module-static `l` owns the dynamic action array, action count, in-use count, and confirmation setting. Window geometry and views are persisted through global preferences `gr`. No durable operation state is written; the module reflects live notifications.

## Dependencies And Integration Points
Depends on AFSClass `NOTIFYEVENT`/`NOTIFYPARAMS`, server-manager globals `g`/`gr`, FastList/view helpers, modeless dialog helpers, animation controls, and resource-format strings. `dispatch.cpp` calls `ActionNotification_MainThread`.

## Risks And Edge Cases
Action matching compares identifiers, strings, and `dw1`; missing/changed notify parameters can leave stale actions. `GetTickCount` wraparound can affect elapsed display. The code posts `IDCANCEL` to progress dialogs during `Action_End`, so dialog handlers must tolerate asynchronous close. Refresh actions do not increment `cActionsInUse`, which is intentional but affects quit gating. Many descriptions dereference `lpi1`/`lpi2` based on event assumptions.

## Test Signals
Simulate begin/end pairs for every event, mismatched end parameters, simultaneous actions, hidden-main quit gating, confirmation toggles, refresh skip, and modeless dialog lifecycle under close/end races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.h

## Purpose
Declares the action/progress tracking API used by notification dispatch and main-window commands.

## Important APIs, Types, And Functions
Exports `ActionNotification_MainThread`, action window open/close/topmost controls, `Action_SetDefaultView`, `Action_fAnyActive`, and `Action_ShowConfirmations`.

## Control Flow
No runtime control flow. The declared functions are called by the notification dispatcher, menu handlers, and shutdown/menu-state logic.

## State And Persistence
No state is declared here; implementation state is in `action.cpp` and global preferences.

## Dependencies And Integration Points
Requires `NOTIFYEVENT`, `PNOTIFYPARAMS`, `LPVIEWINFO`, `BOOL`, and Win32 types from surrounding headers.

## Risks And Edge Cases
The API exposes no explicit initialization or teardown, so callers rely on module statics being zero-initialized and process lifetime cleanup.

## Test Signals
Compile-time integration and menu-state tests around `Action_fAnyActive` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.cpp

## Purpose
Defines aggregate-list default columns and converts aggregate identifiers/status/preferences into display text.

## Important APIs, Types, And Functions
`Aggregates_SetDefaultView` initializes a `VIEWINFO` for aggregate lists. `Aggregates_GetAlertCount` delegates to `Alert_GetCount`. `Aggregates_GetColumnText` formats name, ID, device, used/free/allocated/total storage, usage percent, and alert status for an aggregate `LPIDENT`.

## Control Flow
Column text retrieval pulls `AGGREGATE_PREF` from `LPIDENT::GetUserParam`, uses `asLast` and `szDevice` when available, then switches by `AGGREGATECOLUMN`. Storage values are converted from KiB-like counters to formatted bytes. Status uses `Alert_GetQuickDescription`, falling back to a no-alerts string.

## State And Persistence
Uses a ring of static buffers indexed by column count for returned strings. No persistent writes. It reads per-aggregate preference/status snapshots attached by dispatch/prefs.

## Dependencies And Integration Points
Depends on `svrmgr.h`, `agg_col.h`, `Alert_*`, `FormatString`, and `LPIDENT` name/status APIs. Used by FastList display callbacks.

## Risks And Edge Cases
Static buffers are overwritten after several calls and are not thread-safe. Missing user params produce blank status fields except where defaults are explicit. Percent calculation clamps to 0-100.

## Test Signals
Validate text for aggregate-only and server-qualified names, zero-capacity aggregates, missing preferences, alert/no-alert display, and each configured column.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.h

## Purpose
Declares aggregate-list column identifiers, default metadata, and aggregate display helper prototypes.

## Important APIs, Types, And Functions
`AGGREGATECOLUMN` enumerates name, ID, device, used, used percent, allocated, free, total, and status columns. `AGGREGATECOLUMNS` maps each to resource IDs and widths. Prototypes expose `Aggregates_SetDefaultView`, `Aggregates_GetAlertCount`, and `Aggregates_GetColumnText`.

## Control Flow
No runtime control flow in the header.

## State And Persistence
The static `AGGREGATECOLUMNS` array has internal linkage per translation unit that includes the header.

## Dependencies And Integration Points
Requires resource IDs and `LPVIEWINFO`, `LPAGGREGATE`, `LPIDENT` types from server-manager headers. Used by aggregate tabs and display code.

## Risks And Edge Cases
Defining a non-const static array in a header duplicates it in each including translation unit. Column enum order must stay synchronized with the metadata array and formatter switch.

## Test Signals
Compile/link checks and UI verification that all aggregate columns show expected labels, widths, sorting, and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.cpp

## Purpose
Provides common aggregate preference and selection helpers for the server manager.

## Important APIs, Types, And Functions
`Aggregates_LoadPreferences` allocates and restores an `AGGREGATE_PREF`, applies defaults for warning thresholds and alerts, and initializes volatile alert state. `Aggregates_SavePreferences` stores the aggregate user parameter. `Aggregates_GetFocused` and `Aggregates_GetSelected` extract `LPIDENT` values from the aggregate list.

## Control Flow
Preference load attempts `RestorePreferences`; on failure it sets default aggregate-full warning inheritance, disables allocation warnings, and sets alert defaults. Alert runtime fields are initialized after restore/default. Save only runs if `GetUserParam` is non-null.

## State And Persistence
Preferences are persisted via `RestorePreferences`/`StorePreferences` keyed by aggregate identity. Runtime alert timers/counts are reset by `Alert_Initialize` even for restored preferences.

## Dependencies And Integration Points
Depends on aggregate preference structures from `svrmgr.h`, alert defaults, server preferences, and FastList focus/selection APIs. Called by notification dispatch on aggregate creation/destruction.

## Risks And Edge Cases
Allocation failure is not handled before writing through `pap`. Persistence writes the full struct size, so structure layout/version changes can affect compatibility.

## Test Signals
Preference restore/default/save tests and UI focus/selection tests on aggregate lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.h

## Purpose
Declares aggregate preference and list-selection helper APIs.

## Important APIs, Types, And Functions
Exports `Aggregates_LoadPreferences`, `Aggregates_SavePreferences`, `Aggregates_GetFocused`, and `Aggregates_GetSelected`.

## Control Flow
No runtime control flow.

## State And Persistence
No state is declared; preference persistence is implemented in `agg_general.cpp`.

## Dependencies And Integration Points
Requires `LPIDENT`, `HWND`, and preference infrastructure types from the server-manager environment.

## Risks And Edge Cases
Callers must pass aggregate identifiers to preference functions; the prototypes do not enforce object kind.

## Test Signals
Compilation and runtime dispatch tests that create aggregate identities and attach saved preferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.cpp

## Purpose
Implements the aggregate Properties dialog, including general status information and warning-threshold controls.

## Important APIs, Types, And Functions
`Aggregates_ShowProperties` opens or focuses a cached property sheet. `Aggregates_General_DlgProc` handles the General tab. `Aggregates_General_OnInitDialog`, `_OnApply`, `_OnWarnings`, `_OnEndTask_InitDialog`, and `_OnEndTask_Apply` initialize UI, collect warning edits, and process background task completions. `AGG_PROP_APPLY_PACKET` carries apply data.

## Control Flow
Opening first searches `PropCache`; existing sheets can jump to the threshold tab. New sheets include a Problems tab and General tab. The General tab starts `taskAGG_PROP_INIT` to refresh aggregate data. Apply builds a packet from warning controls and starts `taskAGG_PROP_APPLY`. End-task handlers either populate ID/device/fileset/usage/warning controls or show errors.

## State And Persistence
State is per-dialog via `DWLP_USER` storing `LPIDENT`, property-cache entries, and task packets. Warning changes are persisted by the background apply task through aggregate preferences/server state, not directly in this file.

## Dependencies And Integration Points
Depends on property-sheet/cache helpers, task framework, alert/problem tabs, aggregate/server preference structures, spinner/progress-bar controls, and resource formatting.

## Risks And Edge Cases
Controls are disabled until init completes; failed init leaves unknown values. The warning UI supports default inheritance with `perWarnAggFull == -1`, disabled warnings with zero, and custom percentages; regressions here can change alert behavior. Concurrent property sheets are prevented by `PropCache`.

## Test Signals
Open/focus/jump behavior, init failure, storage usage formatting, warning default/custom/off combinations, apply success/failure, and property-cache destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.h

## Purpose
Declares the aggregate property dialog API and apply-packet structure.

## Important APIs, Types, And Functions
`AGG_PROP_APPLY_PACKET` stores aggregate identity and warning-control values. `Aggregates_ShowProperties` opens aggregate properties and can jump to threshold-related UI.

## Control Flow
No runtime control flow. The packet fields mirror controls in the aggregate General tab.

## State And Persistence
No state is declared in the header; packets are allocated for async task handoff.

## Dependencies And Integration Points
Requires `LPIDENT`, `HWND`, and Win32 scalar types. Used by command handlers and alert/problem flows.

## Risks And Edge Cases
The packet encodes UI control IDs in field names, coupling task consumers to dialog layout.

## Test Signals
Compile all task producers/consumers and verify apply packet interpretation matches UI controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.cpp

## Purpose
Implements the Aggregates tab in server and cell windows.

## Important APIs, Types, And Functions
`Aggregates_DlgProc` is the tab dialog procedure. `Aggregates_OnNotifyFromDispatch` refreshes the list after relevant notifications. `Aggregates_SubclassListProc` routes list `WM_COMMAND` messages to `StartContextCommand`. `Aggregates_ShowPopupMenu` and `Aggregates_ShowParticularPopupMenu` build context menus for aggregate lists and header-column menus.

## Control Flow
On init, the tab sizes itself to the parent tab area, restores the aggregate FastList view, installs text callbacks, and subclasses the list. On server changes it re-registers for aggregate notifications, updates description text based on current server/cell/subset state, and refreshes display. Double-click opens properties. Context-menu handling distinguishes headers, selected server rows, selected aggregate rows, and empty space.

## State And Persistence
View layout is stored/restored through `gr.viewAgg`. Notification registrations are held by dispatch until destroyed. The original list window procedure is stored in static `procAggregatesList`.

## Dependencies And Integration Points
Depends on resize helpers, FastList, dispatch notifications, server-window helpers, display refresh functions, menu resources, and `command.cpp`.

## Risks And Edge Cases
The subclass procedure is static/global, so multiple aggregate lists could race on `procAggregatesList`. Context-menu selection intentionally ignores right-clicked unselected items, which may surprise users but prevents commands on unintended rows. Notification cleanup on destroy is essential to avoid posting to dead HWNDs.

## Test Signals
Tab initialization/resizing, server/cell/subset description text, notification refresh, double-click properties, header column menu, empty-list menu, and destroy/recreate cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.h

## Purpose
Declares the Aggregates tab dialog procedure and context-menu helpers.

## Important APIs, Types, And Functions
Exports `Aggregates_DlgProc`, `Aggregates_ShowPopupMenu`, and `Aggregates_ShowParticularPopupMenu`.

## Control Flow
No runtime control flow in the header.

## State And Persistence
No state is declared; implementation uses static subclass state and global view preferences.

## Dependencies And Integration Points
Requires Win32 dialog/menu types and `LPIDENT`. Used by server-window tab construction and command/menu code.

## Risks And Edge Cases
Callers must pass client and screen coordinates consistently; the header does not clarify coordinate spaces beyond parameter names.

## Test Signals
Compile integration and manual context-menu coverage for aggregate tab lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.cpp

## Purpose
Maintains alert state for servers, services, aggregates, and filesets, and runs the background "Scout" health-check loop.

## Important APIs, Types, And Functions
Public APIs include `Alert_GetObjectAlerts`, `Alert_SetDefaults`, `Alert_Initialize`, `Alert_Scout_SetOutOfDate`, `Alert_Scout_ServerStatus`, alert count/query/description/remedy/button helpers, `Alert_RemoveSecondary`, `Alert_Remove`, `Alert_AddPrimary`, `Alert_StartScout`, and `Alert_Scout_QueueCheckServer`. Core internals include `Alert_BeginUpdate`, `Alert_EndUpdate`, `Alert_RemoveFunc`, `Alert_ScoutProc`, and `Alert_Scout_CheckServer`.

## Control Flow
Alerts live inside per-object preference structures. Adding/removing child alerts rolls them up as server `alertSECONDARY` entries and may insert/remove `alertBADCREDS` when no-server-entry problems require credentials checking. The Scout thread wakes periodically or on demand, enters the AFSClass lock, checks expired credentials, refreshes the server list, optionally refreshes stale servers, and evaluates aggregate, fileset, and service warning conditions.

## State And Persistence
`OBJECTALERTS` stores refresh cadence, next refresh/test ticks, count, and fixed alert array. Preference persistence stores object alert settings, while `Alert_Initialize` clears volatile counters/timers at load. Static `hScout` and `heScoutWakeup` own the background thread/event for process lifetime.

## Dependencies And Integration Points
Depends on preference structs for all object kinds, `CheckCredentials`/expired credential checks, AFSClass cell/server/aggregate/fileset/service APIs, ghost status flags, status structures, and `PostNotification(evtAlertsChanged/evtScoutBegin/evtScoutEnd)`. Display modules consume descriptions, remedies, and button labels.

## Risks And Edge Cases
The Scout thread runs forever with no explicit shutdown. Alert arrays are capped at `nAlertsMAX`; new secondary alerts are dropped when full. `Alert_GetAlert` and `Alert_GetIdent` use `iAlert > nAlerts` rather than `>=`, which can read one past valid entries. `Alert_RemoveFunc` swaps with the last alert, so order is not stable except where special insertion logic preserves bad-credentials first. `PulseEvent` can lose wakeups.

## Test Signals
Test alert add/remove/rollup, full arrays, credential warning insertion/removal, timeout status changes, Scout threshold detection for aggregate full/overallocated, fileset state/no-entry/full, service stopped, notification emission, and boundary indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.h

## Purpose
Defines alert types, alert payload structures, alert storage, timing constants, and public alert APIs.

## Important APIs, Types, And Functions
`ALERT` enumerates invalid, secondary, timeout, full, missing VLDB/server entries, stopped service, bad credentials, overallocated aggregate, and fileset state alerts. `ALERTINFO` stores the active alert plus a union-like anonymous payload. `OBJECTALERTS` holds refresh/test timing and a fixed `aAlerts[nAlertsMAX]` array. Public prototypes expose object alert retrieval, initialization/defaults, query/description/remedy/button helpers, mutation, Scout start, and queued server checks.

## Control Flow
No implementation flow in the header. The struct shapes determine how `alert.cpp` stores and interprets each alert.

## State And Persistence
`OBJECTALERTS` is embedded in persisted preference structs for servers/services/aggregates/filesets, but some fields are reset at runtime.

## Dependencies And Integration Points
Requires `LPIDENT`, `FILESETSTATE`, `SYSTEMTIME`, and Windows/AFS types. Used broadly by display, columns, properties, dispatch, and preference code.

## Risks And Edge Cases
The anonymous nested structs rely on compiler extensions or old MSVC behavior. Fixed-size alert storage can truncate problems. Structure layout changes affect stored preferences if serialized by raw struct size.

## Test Signals
Compile portability checks, preference compatibility tests, and runtime coverage for every `ALERT` variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.cpp

## Purpose
Parses server-manager command-line switches and converts them into startup operations.

## Important APIs, Types, And Functions
`ParseCommandLine` recognizes `cell`, `subset`, `server`, `reset`, `confirm`, `user`, `password`, `lookup`, and `useexisting`. `CommandLineHelp` displays syntax/error messages. Return values are `CMDLINEOP` values from `cmdline.h`.

## Control Flow
The parser resets switch presence, scans `/` or `-` switches with optional colon-separated values and quote handling, rejects unknown/duplicate/missing values, then validates switch combinations. It can enable action confirmations, erase settings/preferences for reset, set credentials, open lookup-error-code mode, reuse existing credentials and start `taskOPENCELL`, or start `taskOPENCELL` for a requested cell/subset/server.

## State And Persistence
Static `aSWITCHES` stores parsed presence and values. Reset deletes persisted settings/preferences via registry helpers. Credential switches call `AfsAppLib_SetCredentials`; `useexisting` updates `g.hCreds`. Cell-open operations allocate `OPENCELL_PACKET` and optional `SUBSET`.

## Dependencies And Integration Points
Depends on AFS app-library credential APIs, subset persistence, task framework, global credentials, action confirmations, and message/error dialogs.

## Risks And Edge Cases
Parsing is custom and fixed-buffer; long values can overflow `szValue`. Switch matching allows abbreviated prefixes if unambiguous by following delimiter rules, which may be surprising. `useexisting` silently closes the app on credential lookup failure. Allocated packets are handed to async tasks, so failure ownership is important.

## Test Signals
Test all valid switch combinations, quoted values, duplicate/unknown/missing values, required `cell` for `subset`/`server`, required user/password pairing, reset scopes, credentials failures, and `useexisting` with/without cached credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.h

## Purpose
Declares startup command-line outcomes and the command-line parser.

## Important APIs, Types, And Functions
`CMDLINEOP` values are `opCLOSEAPP`, `opNORMAL`, `opNOCELLDIALOG`, and `opLOOKUPERRORCODE`. `ParseCommandLine(LPTSTR pszCmdLine)` returns one of those operations.

## Control Flow
No runtime control flow. The application startup code uses the enum to decide whether to continue, show normal dialogs, skip the cell dialog, or show the error lookup UI.

## State And Persistence
No state is declared.

## Dependencies And Integration Points
Requires `LPTSTR`; implemented by `cmdline.cpp`.

## Risks And Edge Cases
Callers must honor every enum value; treating `opNOCELLDIALOG` like normal startup can duplicate cell-opening UI.

## Test Signals
Startup integration tests should assert each return value drives the intended application path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.cpp

## Purpose
Implements the column customization dialog for server-manager list views.

## Important APIs, Types, And Functions
`ShowColumnsDialog` opens the modal property sheet. `Columns_DlgProc` dispatches UI events. Internal handlers initialize the category combo, update available/shown lists, insert/delete/reorder columns, and apply changed `VIEWINFO` structures back to global views and visible FastList controls.

## Control Flow
Opening copies current global view settings into a static `COLUMNS` working array and chooses the default category. The dialog displays available columns not in `aColumns` and shown columns in order. Insert/delete/up/down mutate the selected working `VIEWINFO`, mark its category changed, and dirty the property sheet. Apply copies changed views back to `gr`, restores FastList state for visible affected tabs, forces redraws, and posts `WM_COLUMNS_CHANGED` when the originally requested view changed.

## State And Persistence
Static `COLUMNS` holds working copies and change flags for server, fileset, aggregate, service, replica, and aggregate-selection views. Persistent/global state is in `gr.*` view structures; individual FastList controls store/restore view state during apply.

## Dependencies And Integration Points
Depends on property sheets/cache, combo/list helper wrappers, server windows, display refresh, FastList view APIs, and global layout state. Command handling opens this dialog through `M_COLUMNS`.

## Risks And Edge Cases
The first column cannot be deleted and movement is constrained to keep it anchored. `Columns_OnInsert` computes `iShown` but appends rather than inserting at that position, so UI behavior may not match intent. Static working state means only one dialog should be active. Applying to all visible server windows relies on `PropCache_Search` iteration.

## Test Signals
Test each category, hidden categories when not selected, insert/delete/reorder constraints, apply/cancel behavior, visible tab redraw, server-list refresh, and persistence of global view settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.h

## Purpose
Declares the column customization dialog entry point.

## Important APIs, Types, And Functions
`ShowColumnsDialog(HWND hParent, LPVIEWINFO lpvi = NULL)` opens the dialog for a parent window and optional default view.

## Control Flow
No runtime control flow.

## State And Persistence
No state is declared; implementation reads and writes global view preferences.

## Dependencies And Integration Points
Requires `HWND` and `LPVIEWINFO`. Invoked from context/menu command handling.

## Risks And Edge Cases
Passing null defaults to the server-list view based on current preview/orientation state; callers should pass an explicit view when opening from a specific list.

## Test Signals
Compile integration and command-menu tests that open the dialog from server, aggregate, service, and fileset views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.cpp

## Purpose
Centralizes context/menu command dispatch for the server manager.

## Important APIs, Types, And Functions
`StartContextCommand` maps menu IDs to UI dialogs, property sheets, or background tasks. `Command_OnProperties` opens the correct property sheet for the chosen object type. `Command_OnIconView` changes icon/list/status view mode for server or child tabs.

## Control Flow
The dispatcher derives the active child tab and chosen identity from the clicked object or represented window, suppresses cell identities for most object commands, and switches on menu command IDs. It invokes column dialogs, refresh tasks, sync/salvage, fileset create/delete/move/quota/release/clone/dump/restore, server security/hosts/install/prune/execute, service create/delete/start/stop/restart/log, cell opening, credentials, options, and help/about flows.

## State And Persistence
Commands mutate global view preferences through display helpers, credentials/cell state through dialog/task flows, and server/fileset/service state through background tasks. This file itself holds no persistent state.

## Dependencies And Integration Points
Includes many feature modules and is called by tab/list subclass procedures and menus. It depends on `Server_GetDisplayedTab`, `StartTask`, global `g.lpiCell`, and many modal/modeless feature entry points.

## Risks And Edge Cases
Many cases silently no-op when `lpi` is missing or wrong type. Some commands allow null identities intentionally for create/restore/global unlock. The central switch is broad, so new menu IDs must be added carefully to avoid wrong-object operations.

## Test Signals
Command matrix tests should cover every menu ID with null, server, service, aggregate, fileset, and cell contexts, plus view-mode changes and properties routing with alert counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.h

## Purpose
Declares the server-manager context command dispatcher.

## Important APIs, Types, And Functions
`StartContextCommand(HWND hDialog, LPIDENT lpiRepresentedByWindow, LPIDENT lpiChosenByClick, int cmd)` executes the command represented by a menu/control ID in the context of a window and optional clicked object.

## Control Flow
No runtime control flow in the header. The implementation resolves context and dispatches by command ID.

## State And Persistence
No state is declared.

## Dependencies And Integration Points
Requires Win32 HWND and AFSClass `LPIDENT`. Used by list subclasses, context menus, and main/server windows.

## Risks And Edge Cases
The generic signature places responsibility on callers to pass the right represented and clicked identities; wrong context can lead to no-op or wrong command routing.

## Test Signals
Compile integration and UI command-routing tests for every list/menu caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.cpp

## Purpose
Handles cell-opening, credential acquisition, credential refresh, and monitoring-scope choices for the server manager.

## Important APIs, Types, And Functions
Open-cell helpers include `OpenCellDlg_Hook`, `OpenCellDlg_Hook_OnOK`, `OpenCell_OnCellChange`, `OpenCell_OnSubset`, `OpenCell_OnAdvanced`, and `OpenCellDlg_Hook_OnEndTask_OpenCell`. Credential helpers include `GetBadCredsDlgParams`, `GetCredentialsDlgParams`, `OpenCellDialog`, `NewCredsDialog`, `CheckForExpiredCredentials`, and `CheckCredentials`.

## Control Flow
The open-cell hook initializes monitoring choices, toggles advanced UI, populates subset choices as the cell changes, and validates credentials on OK. With KFW available it obtains Kerberos/AFS credentials then reads them through the app library; otherwise it sets credentials directly and checks them. On success it builds an `OPENCELL_PACKET` with all/one/subset monitoring and starts `taskOPENCELL`; the dialog closes only when that task succeeds.

## State And Persistence
Global credential handle `g.hCreds` is updated on success. Subsets are loaded from/saved to the subset subsystem; `OpenCellDialog` first saves dirty current subsets. Dialog state is stored in controls and `DWLP_USER` params. Warning preferences use `gr.fWarnBadCreds`.

## Dependencies And Integration Points
Depends on AFS app-library credential/open-cell dialogs, KFW (`afskfw.h`), subset storage, task framework, display globals, and time/credential warning helpers.

## Risks And Edge Cases
Passwords are held in stack buffers and passed to credential APIs. KFW and non-KFW paths differ in validation behavior. The advanced dialog resizes based on current client/group metrics and can drift with resource changes. `OpenCell_OnCellChange` references `g.sub->szSubset` when current-cell/subset assumptions hold.

## Test Signals
Test KFW and non-KFW login success/failure, bad credential warnings, expired credential checks, all/one/subset monitoring packets, dirty subset save failure, advanced toggle layout, and task failure re-enabling controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.h

## Purpose
Declares credential and open-cell operations for the server manager.

## Important APIs, Types, And Functions
Exports `OpenCellDialog`, `NewCredsDialog`, `CheckForExpiredCredentials`, and `CheckCredentials`.

## Control Flow
No runtime control flow. Callers use these entry points for startup, menu commands, and background Scout credential checks.

## State And Persistence
No state is declared; implementation updates global credential state and uses persisted warning/subset settings.

## Dependencies And Integration Points
Requires Win32/AFS boolean types. Used by command handling, alert/scout code, and startup flows.

## Risks And Edge Cases
The header declares `OpenCellDialog` as `int` while the implementation returns `BOOL`; ABI-compatible in old Win32 C++ but semantically inconsistent.

## Test Signals
Compilation should flag signature drift under stricter settings. Runtime tests should confirm callers correctly treat nonzero as success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.cpp

## Purpose
Bridges asynchronous AFSClass notifications to server-manager UI windows and immediate preference/alert maintenance.

## Important APIs, Types, And Functions
`CreateNotificationDispatch` initializes the critical section and notification callback. `PostNotification` broadcasts app-level events. `DispatchNotification` is the callback from AFSClass. `DispatchNotification_OnPump` drains queued notifications on the main thread. `NotifyMe`, `DontNotifyMe`, and `DontNotifyMeEver` manage window subscriptions.

## Control Flow
AFSClass invokes `DispatchNotification` on library threads. The alternate-thread handler immediately updates preferences on object create/destroy, syncs monitor state, and queues alert checks. The notification is then copied into a protected FIFO queue. The main thread pump drains the queue, lets `action.cpp` update progress tracking, filters subscriptions by `NOTIFYWHEN` and object relationships, and posts `WM_NOTIFY_FROM_DISPATCH` with a heap-allocated `NOTIFYSTRUCT` to interested windows.

## State And Persistence
Module-static state includes `csDispatch`, `Handler`, a reallocating dispatch subscription array, and queue head/tail pointers. Preference load/save attachment happens indirectly on create/destroy through `SetUserParam`; monitor subset state can update `g.sub`.

## Dependencies And Integration Points
Depends on AFSClass notification callbacks, object identity APIs, server/service/aggregate/fileset preference loaders, subset monitoring, display update helpers, alert/scout functions, and action notification handling.

## Risks And Edge Cases
Subscription entries are tombstoned rather than compacted. Posted `NOTIFYSTRUCT` ownership transfers to target windows, which must delete it. UI updates from `DispatchNotification_AltThread` include `UpdateDisplay_ServerWindow`, so thread-safety depends on those functions being safe or historically tolerated. Queue allocation failure is not handled. Event filtering is complex and should be reviewed for missed cell/server/child propagation.

## Test Signals
Test create/destroy preference attachment, notification queue order, cross-thread pump delivery, each `NOTIFYWHEN` filter, window unsubscribe/destroy, alert/task side effects, and allocation/target-window failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.h

## Purpose
Defines notification subscription categories, app-level notification events, payload structure, and dispatch API.

## Important APIs, Types, And Functions
`NOTIFYWHEN` enumerates cell-opened, object-changed, server, fileset, aggregate, and service change subscriptions. `NOTIFYSTRUCT` packages target HWND, event, and parameters. App-specific events are `evtAlertsChanged`, `evtScoutBegin`, and `evtScoutEnd`. Prototypes expose dispatch creation, notification posting, subscribe/unsubscribe, and main-thread pump draining.

## Control Flow
No implementation flow. Consumers register windows and later receive `WM_NOTIFY_FROM_DISPATCH` messages with `NOTIFYSTRUCT` payloads.

## State And Persistence
No state is declared in the header; implementation owns subscription and queue state.

## Dependencies And Integration Points
Includes `messages.h` for message/event definitions and requires AFSClass notification types. Used by display tabs, action tracking, alert code, and object-management code.

## Risks And Edge Cases
Custom events are defined relative to `evtUser`; additions must avoid collisions. `NOTIFYSTRUCT` includes copied `NOTIFYPARAMS`, so any pointer members must remain valid long enough for posted UI handling.

## Test Signals
Compile all notification consumers and verify message ownership/lifetime conventions in every `WM_NOTIFY_FROM_DISPATCH` handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.h -->
