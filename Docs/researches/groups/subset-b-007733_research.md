# Research Group subset-b-007733

This grouped report covers the OpenAFS Windows Server Manager display, preferences, help, problem reporting, and fileset operation files assigned to `subset-b-007733`. Each source-tree-aligned section is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.cpp

## Purpose
`dispguts.cpp` implements the concrete redraw routines behind `UpdateDisplay()`. It populates the main cell identity fields and the FastList/combobox views for servers, services, aggregates, filesets, replicas, and per-server windows. This is the bridge between the AFSClass object model (`LPCELL`, `LPSERVER`, `LPAGGREGATE`, `LPFILESET`, `LPSERVICE`, `LPIDENT`) and the Win32/AfsAppLib visual controls.

## Important APIs, Types, And Functions
Externally declared functions are `Display_Cell_Internal`, `Display_Servers_Internal`, `Display_Services_Internal`, `Display_Aggregates_Internal`, `Display_Filesets_Internal`, `Display_Replicas_Internal`, and `Display_ServerWindow_Internal`. Private helpers clean incrementally replaced rows, add parent/child hierarchy nodes, choose status/type images through `Display_PickImages`, and add FastList rows through `Display_InsertItem`. The file depends heavily on column-format helpers from `svr_col.h`, `svc_col.h`, `agg_col.h`, and `set_col.h`, plus `Filesets_fIsLocked` from `set_general.h`.

## Control Flow
Each display routine receives a `DISPLAYREQUEST` prepared by `display.cpp`. It discovers the target control, ensures image lists exist, starts a FastList or combobox change transaction, optionally removes only rows affected by `lpiNotify`, enumerates the relevant AFSClass hierarchy, inserts or updates visible items, restores selection, and sets `actOnDone` flags such as `ACT_ENDCHANGE`, `ACT_UNCOVER`, and `ACT_SELPREVIEW`. Incremental requests are filtered by server or aggregate identity before expensive enumeration. Error status from a notification is rendered directly into the first column and usually prevents descending into children.

## State And Persistence
This file does not persist settings itself, but it mutates process state and cached object preferences. Successful status fetches are copied into `SERVER_PREF::ssLast`, `SERVICE_PREF::ssLast`, `AGGREGATE_PREF::asLast`, and `FILESET_PREF::fsLast`, and fileset preferences also cache `lpiRW`. Tree expansion state is read from server and aggregate preference records. Main-window identity labels are derived from `g.lpiCell` and `g.hCreds`.

## Dependencies And Integration Points
Integration points include FastList APIs (`FL_StartChange`, `FastList_AddItem`, `FastList_SetExpanded`), combobox helpers (`CB_StartChange`, `CB_AddItem`), AfsAppLib image lists and cover/uncover UI, AFSClass object enumeration/status APIs, global UI state `g` and `gr`, credential cracking, alert counts, and server-window selection. `Display_Replicas_Internal` performs a full cell/server/aggregate/fileset walk to find read-only replicas matching a read-write volume ID.

## Risks And Edge Cases
Several cleanup loops rely on identity pointer stability and careful parent identity checks; stale or reused `LPIDENT` pointers would remove wrong rows. Static image-list initialization is per control and not reference-counted here. `Display_Replicas_Internal` can be expensive because it scans the whole cell. Status failures suppress child enumeration, so partial outages can hide lower-level objects. The helper uses static UI buffers returned by column functions, which is acceptable for immediate copies but fragile if reused asynchronously.

## Test Signals
Useful tests include full and incremental refresh for each target, row replacement when a server/aggregate/fileset notification arrives, error rendering, monitored versus unmonitored servers, alert and locked icons, tree expansion persistence, combobox selection fallback, replica discovery for RW/RO volume IDs, credential-expired label formatting, and preview-pane selection updates after server-list refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.h

## Purpose
`dispguts.h` declares the internal display worker entry points implemented in `dispguts.cpp`. It intentionally directs callers to use the public `UpdateDisplay()` interface instead of invoking these routines directly.

## Important APIs, Types, And Functions
The header exports seven functions: `Display_Cell_Internal`, `Display_Servers_Internal`, `Display_Services_Internal`, `Display_Aggregates_Internal`, `Display_Filesets_Internal`, `Display_Replicas_Internal`, and `Display_ServerWindow_Internal`. All accept `LPDISPLAYREQUEST`, tying the header to `display.h`.

## Control Flow
There is no executable control flow. At runtime `display.cpp` dispatches on `DISPLAYREQUEST::dt` and calls these functions while holding the AFSClass lock, after the request has passed queue filtering.

## State And Persistence
No state is declared. State is supplied through the request object and global application structures used by the implementations.

## Dependencies And Integration Points
The header integrates the display queue with the implementation module. It must be included in files that know `LPDISPLAYREQUEST`, normally through `display.h` and `svrmgr.h`.

## Risks And Test Signals
The risk is boundary drift: adding a display target in `display.h` requires matching declarations and implementations here. Compile coverage and exercising every `DISPLAYTARGET` dispatch path are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.cpp

## Purpose
`display.cpp` is the asynchronous display scheduler for the Server Manager UI. It accepts display refresh requests, coalesces redundant work, runs up to four update threads, dispatches to the `dispguts.cpp` internals, and completes FastList/combobox transactions once all pending refreshes for a window finish.

## Important APIs, Types, And Functions
Public routines include `GetItemText`, `UpdateDisplay`, `UpdateDisplay_Cell`, `UpdateDisplay_Servers`, `UpdateDisplay_Services`, `UpdateDisplay_Aggregates`, `UpdateDisplay_Filesets`, `UpdateDisplay_Replicas`, `UpdateDisplay_ServerWindow`, `UpdateDisplay_SetIconView`, `Display_GetServerIconView`, and `HandleColumnNotify`. Important private state includes `aDisplayQueue`, `cDisplayQueueActive`, `cUpdateThreadsActive`, critical sections, active request snapshots per target, and `aWindowActOnDone` for deferred end-change actions.

## Control Flow
`UpdateDisplay()` validates and copies a `DISPLAYREQUEST`, initializes queue state lazily, applies `DisplayQueueFilter()` against queued and active work, increments a per-window outstanding count, and either runs synchronously for `fWait` or starts `DisplayQueue_ThreadProc`. The thread pulls queued requests, records the active request, enters AFSClass, dispatches to the appropriate internal display routine, decrements the per-window count, and either performs final UI actions or records them for a later request on the same control. Wrapper functions construct standard request packets for common targets.

## State And Persistence
Display state is process-local. Queue storage grows in chunks of 128 entries and never shrinks. Per-window counters are maintained through `InterlockedIncrementByWindow` and `InterlockedDecrementByWindow`. Completion actions and desired selection are stored in `aWindowActOnDone` until the last outstanding operation for a list finishes. Column sort/width changes are persisted indirectly by `FL_StoreView` into the supplied `VIEWINFO`, which is later saved with global settings.

## Dependencies And Integration Points
The module depends on Win32 threads and critical sections, FastList callbacks, AFSClass locking, `Main_StartWorking`/`Main_StopWorking`, server-window helpers, property cache lookup, global view state `gr`, and the internal display functions declared by `dispguts.h`. `GetItemText` integrates every list view with server/service/aggregate/fileset/replica column formatters.

## Risks And Edge Cases
The queue is global and lazily initialized without an outer initialization lock, so first-use concurrency is sensitive. `DisplayQueueFilter()` deliberately drops requests when broader refreshes cover them; bugs here cause stale UI. `UpdateDisplay(..., TRUE)` executes immediately on the caller and the header warns not to block the main thread. `aWindowActOnDone` entries are reused but not compacted. UI updates from worker threads are legacy Win32-style and rely on controls tolerating these calls.

## Test Signals
Test signals include duplicate request coalescing, broad-refresh versus narrow-refresh ordering, active-request filtering, synchronous refresh behavior, maximum update-thread fan-out, correct `FL_EndChange`/`CB_EndChange` after multiple outstanding requests, selection preservation, preview-pane update, column resize/click persistence, and icon-view switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.h

## Purpose
`display.h` defines the public contract for all list, tree, combobox, cell label, and server-window refreshes in the Server Manager UI.

## Important APIs, Types, And Functions
`DISPLAYTARGET` enumerates refresh targets: cell, servers, services, aggregates, filesets, replicas, and server window. `DISPLAYREQUEST` carries target windows, identity filters, status codes, parent identities, selection, view settings, worker-populated list handles, completion action flags, and whether the target is a FastList. Action flags are `ACT_ENDCHANGE`, `ACT_UNCOVER`, and `ACT_SELPREVIEW`. Prototypes expose display wrappers, `GetItemText`, `HandleColumnNotify`, and `Display_GetServerIconView`.

## Control Flow
Callers either fill a `DISPLAYREQUEST` and call `UpdateDisplay()` or use one of the `UpdateDisplay_*` wrappers. The request is copied by the scheduler, so stack-allocated packets are valid even for asynchronous updates.

## State And Persistence
The header declares no storage. It describes state passed into `display.cpp` and mutable `VIEWINFO` records owned by global settings or dialog-local view structures.

## Dependencies And Integration Points
Consumers need Win32 HWND types, `LPIDENT`, `LPVIEWINFO`, FastList notification types, and the broader `svrmgr.h` environment. The API is used throughout tabs, property dialogs, and fileset operation dialogs whenever an AFS object list must be rebuilt.

## Risks And Test Signals
The main risk is semantic coupling around nullable fields: `lpiNotify == NULL` means full refresh, while non-null means targeted replacement; `hList` may be caller-provided or worker-discovered. Compile tests plus functional refresh tests for every wrapper are the most useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/exportcl.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/exportcl.h

## Purpose
`exportcl.h` defines debug-only textual keys for exporting or describing OpenAFS cell objects. The keys cover cells, servers, services, partitions, volumes, principals, replica policy, and group membership.

## Important APIs, Types, And Functions
There are no functions or types. Under `#ifdef DEBUG`, it defines `TEXT(...)` constants such as `eckCELL`, `eckSERVER`, `eckSERVICE`, `eckAGGREGATE`, `eckFILESET`, `eckADDRESS`, service status keys, partition capacity keys, volume quota/time keys, replication policy keys, principal lifetime/key keys, and group/member/owner keys.

## Control Flow
No executable control flow exists. The header is a shared constant table for debug/export code outside this file set.

## State And Persistence
No runtime state is stored here. The constants imply a serialized field vocabulary for debug exports, but actual persistence is handled by consumers.

## Dependencies And Integration Points
The file depends on Windows/TCHAR `TEXT()` macros and only emits definitions for debug builds. It integrates with any debug-only cell export code that needs stable property names.

## Risks And Test Signals
Risks are low but include schema drift between these keys and export/import consumers. Test signals are debug-build compile coverage and export output checks for server, service, aggregate, fileset, principal, and group records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/exportcl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.cpp

## Purpose
`general.cpp` provides a small synchronization utility that associates a `LONG` counter with an `HWND` and exposes interlocked increment/decrement operations for that counter. The display scheduler uses it to know when all outstanding updates for a window have completed.

## Important APIs, Types, And Functions
Public functions are `InterlockedIncrementByWindow` and `InterlockedDecrementByWindow`. The private helper `FindLongByWindow` lazily initializes `pcsWindowList`, searches `aWindowList`, and allocates entries in chunks of 16 using `REALLOC`.

## Control Flow
On each increment or decrement, the code finds or creates the row for the supplied window while holding a critical section, then calls the Win32 `InterlockedIncrement` or `InterlockedDecrement` primitive on the associated counter outside the table lock.

## State And Persistence
State is process-local: a grow-only static array of `{ HWND hWnd; LONG dw; }` records and one critical section. Entries are never removed when windows are destroyed.

## Dependencies And Integration Points
The main integration point is `display.cpp`, which increments before scheduling a display operation and decrements when the operation completes. It depends on Win32 handles, critical sections, and interlocked APIs.

## Risks And Edge Cases
The table leaks stale HWND entries for the process lifetime, which is acceptable for a small legacy GUI but can grow with many transient windows. Reuse of destroyed HWND values could associate a new window with an old nonzero counter if lifetimes overlap badly. Lazy critical-section initialization is not itself protected against simultaneous first callers.

## Test Signals
Test repeated increments/decrements for one window, many windows forcing `REALLOC`, concurrent access from display worker threads, zero return after balanced operations, and behavior after window destruction/recreation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.h

## Purpose
`general.h` declares the per-window interlocked counter helpers used by the UI refresh machinery.

## Important APIs, Types, And Functions
It exposes `LONG InterlockedIncrementByWindow(HWND hWnd)` and `LONG InterlockedDecrementByWindow(HWND hWnd)`.

## Control Flow
No logic is present in the header. Callers increment before starting work associated with a window and decrement when that work finishes.

## State And Persistence
No storage is declared. The implementation keeps process-local counters in `general.cpp`.

## Dependencies And Integration Points
The API depends on Win32 `HWND` and `LONG` types. Its main consumer is `display.cpp`.

## Risks And Test Signals
Risks are tied to lifecycle semantics: callers must balance increments and decrements or completion handlers will run too early or too late. Compile coverage and display-queue completion tests cover the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.cpp

## Purpose
`helpfunc.cpp` implements Server Manager help features: command help lookup, numeric error translation, About dialog behavior, and registration of context-sensitive help maps for dialogs across the application.

## Important APIs, Types, And Functions
Public functions are `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`. Internal structures map Unix command families (`vos`, `bos`, `kas`, `fs`) to string and help IDs. `lstrstr` performs case-insensitive substring search, `Help_FindCommand_Search` strips leading command-family tokens, `Help_FindError_OnTranslate` formats system/OpenAFS error text, and `Main_ConfigureHelp` registers dozens of dialog/control help maps through AfsAppLib.

## Control Flow
The Find Command dialog fills a combobox from `aCOMMANDS`, accepts free text, narrows by utility family if the user typed one, searches localized command strings, and opens WinHelp at the selected context ID. The Find Error dialog starts in a compact state, parses decimal or hex input with `strtoul`, formats an error description, strips the trailing numeric code, and expands the window with the translated text. The About dialog subclasses its OK button and uses timer/syscommand hooks plus `NextSearch()` to reveal hidden animated text.

## State And Persistence
The module has static command/help tables, compressed search values for the About animation, and static layout state for the error dialog shrink/expand path. No persistent settings are written. Help registration mutates AfsAppLib's process-global help table.

## Dependencies And Integration Points
Dependencies include Win32 dialogs, WinHelp, AfsAppLib help registration, localization resource IDs, control IDs from `resource.h`, and string/error formatting helpers. The help maps cover fileset create/delete/move/dump/restore, server operations, service operations, subsets, credentials, options, and problem tabs.

## Risks And Edge Cases
The command search relies on localized command strings and a first-match substring search, so ambiguous keywords may open an unexpected topic. `Help_FindCommand_Search` edits the input buffer by inserting NULs. The About dialog uses hard-coded child IDs (`0x051E`, `0x051F`) and nonstandard messages. The error dialog creates a brush in `WM_CTLCOLORSTATIC` without visible ownership management elsewhere.

## Test Signals
Test command lookup by full command, partial command, and family-qualified search; unknown and empty input paths; decimal and hex error translation; shrink/expand layout; WinHelp context opening; About dialog lifecycle; and context help coverage for every dialog ID registered in `Main_ConfigureHelp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.h

## Purpose
`helpfunc.h` declares the Server Manager help and About entry points.

## Important APIs, Types, And Functions
It exposes `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`.

## Control Flow
No header logic exists. Menu handlers call the first three functions to open modal dialogs; application startup calls `Main_ConfigureHelp` to bind dialog/control IDs to help topics.

## State And Persistence
No state is declared here. Implementation state is static in `helpfunc.cpp` and AfsAppLib's help registry.

## Dependencies And Integration Points
The header is consumed by menu and startup code in the Win32 GUI. It depends on the broader application headers for Win32 and TCHAR definitions.

## Risks And Test Signals
Risks are limited to declaration/implementation drift. Compile coverage plus menu invocation of each help function validates the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/messages.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/messages.h

## Purpose
`messages.h` centralizes custom window messages and timer IDs used by the Server Manager UI and worker dispatch paths.

## Important APIs, Types, And Functions
The file defines timer IDs `ID_DISPATCH_TIMER` and `ID_ACTION_TIMER`, plus `WM_USER`-based messages including `WM_NOTIFY_FROM_DISPATCH`, `WM_SERVER_CHANGED`, `WM_REFRESH_UPDATE`, `WM_OPEN_SERVERS`, `WM_COLUMNS_CHANGED`, `WM_OPEN_SERVER`, `WM_SHOW_CREATEREP_DIALOG`, `WM_SHOW_YOURSELF`, `WM_OPEN_ACTIONS`, and `WM_REFRESH_SETSECTION`. Comments document expected `wParam`/`lParam` payloads.

## Control Flow
No executable flow exists. Dialog procedures and main-window handlers switch on these values to receive AFSClass notifications, redraw server tabs, update refresh progress, reopen servers, react to column changes, and request cross-thread dialog creation.

## State And Persistence
No state is declared. The message values form an in-process ABI between UI components and worker/task code.

## Dependencies And Integration Points
The header depends on Win32 `WM_USER` conventions and is included by modules that post or handle these messages. It integrates the dispatch notification layer, refresh dialog, server windows, fileset drag/drop replica workflow, and action window.

## Risks And Test Signals
Risks include message ID collisions, wrong payload casting, and posting messages to windows after destruction. Test signals are compile coverage and functional tests for each message source/handler pair, especially cross-thread `WM_SHOW_CREATEREP_DIALOG` and notification cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.cpp

## Purpose
`options.cpp` implements the modal Options property sheet, specifically the General tab for global Server Manager preferences.

## Important APIs, Types, And Functions
The public entry point is `ShowOptionsDialog`. Internal functions are `Options_General_DlgProc`, `Options_General_OnInitDialog`, and `Options_General_OnApply`. The tab edits `gr.fServerLongNames`, `gr.fDoubleClickOpens`, `gr.fOpenMonitors`, `gr.fCloseUnmonitors`, and `gr.fWarnBadCreds`.

## Control Flow
`ShowOptionsDialog` creates a property sheet and adds the General tab. The dialog registers itself in `PropCache`, initializes checkboxes from `gr`, marks the sheet dirty on control changes, and on apply copies UI state back into `gr`. If long-server-name behavior changed, it calls `AfsClass_RequestLongServerNames` and refreshes the server list. If bad-credential warnings are enabled, it immediately checks credentials and posts the Credentials command when needed.

## State And Persistence
Global restored settings in `gr` are updated and persisted via `StoreSettings(REGSTR_SETTINGS_BASE, REGSTR_SETTINGS_PATH, REGVAL_SETTINGS, &gr, sizeof(gr), wVerGLOBALS_RESTORED)`. The property cache tracks the sheet while open.

## Dependencies And Integration Points
Dependencies include AfsAppLib property sheets/help, the property cache, credentials checking, global registry settings, `UpdateDisplay_Servers`, and the main window command path for `M_CREDENTIALS`.

## Risks And Edge Cases
The local `szCell` in `ShowOptionsDialog` is populated but unused. Applying settings can trigger asynchronous refresh and credential UI while the property sheet remains active. `fDoubleClickOpens` is encoded as numeric values rather than an enum, so radio-button mapping must stay consistent with consumers.

## Test Signals
Test each checkbox/radio path, dirty-state/apply behavior, registry persistence, server-list refresh after long-name toggling, warning-enabled credential prompt, help handling, and property-cache cleanup on sheet destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.h

## Purpose
`options.h` declares the entry point for opening Server Manager options.

## Important APIs, Types, And Functions
It exposes `void ShowOptionsDialog(void)`.

## Control Flow
No logic exists in the header. Menu handlers call `ShowOptionsDialog` to show the modal property sheet.

## State And Persistence
No state is declared. The implementation edits and persists global `gr` settings.

## Dependencies And Integration Points
The header integrates the menu command layer with the options dialog implementation.

## Risks And Test Signals
Risks are limited to declaration drift. Compile coverage and invoking the Options menu validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.cpp

## Purpose
`prefs.cpp` builds and manages Windows registry paths for per-object preferences and server subset definitions. It provides generic store/restore/erase helpers for server, service, aggregate, and fileset preference blobs.

## Important APIs, Types, And Functions
Public functions are `RestorePreferences`, `StorePreferences`, `ErasePreferences`, `OpenSubsetsKey`, and `OpenSubsetsSubKey`. The private `GetPreferencesInfo` constructs a registry subpath and selects the expected version (`wVerSERVER_PREF`, `wVerSERVICE_PREF`, `wVerAGGREGATE_PREF`, or `wVerFILESET_PREF`) based on the `LPIDENT` type. Keyword constants include `Settings`, `Preferences`, `Services`, `Aggregates`, `Filesets`, and `Server Subsets`.

## Control Flow
Store/restore first derive a path under the current cell and server and then call `StoreSettings` or `RestoreSettings` using `SETTINGS_KW` and the version tag. `ErasePreferences` deletes all preferences, a cell subtree, or server-prefixed keys under a cell. Subset helpers open, create, or delete keys under the current or supplied cell's `Server Subsets` branch.

## State And Persistence
Persistent state is under HKCU OpenAFS Server Manager settings. Paths are cell-specific, server-specific, and then optionally nested by object kind/name. Subsets are also HKCU-scoped and can be destroyed/recreated when `fCreate` is set.

## Dependencies And Integration Points
Dependencies include `LPIDENT` name accessors, registry helpers (`RegOpenKey`, `RegDeltreeKey`, `RegCreateKey`, `RegDeleteKey`), global `g.lpiCell`, and versioned settings helpers. Server, service, aggregate, fileset, and subset modules consume these APIs.

## Risks And Edge Cases
Path construction uses fixed `MAX_PATH` buffers and repeated `lstrcat`; unusually long cell/server/object names could overflow depending on helper behavior. `ErasePreferences` wildcard deletion matches server-name prefixes and restarts enumeration after deletion, which is intentional but broad. `OpenSubsetsSubKey` uses `fCreate == 2` as a delete-only convention, a non-obvious API contract.

## Test Signals
Test preference store/restore for each object type, version mismatch fallback, deleting all/cell/server preferences, subset create/open/delete, current-cell fallback, long-name handling, and registry permission failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.h

## Purpose
`prefs.h` declares registry-backed preference and subset helper functions.

## Important APIs, Types, And Functions
It exposes `ErasePreferences`, `RestorePreferences`, `StorePreferences`, `OpenSubsetsKey`, and `OpenSubsetsSubKey`. `ErasePreferences` defaults to deleting all preferences when no cell/server is supplied. `OpenSubsetsKey` notes the `fCreate` convention: `0` open, `1` create, `2` delete.

## Control Flow
No logic exists in the header. Callers pass `LPIDENT` plus a preference struct buffer to store or restore object settings.

## State And Persistence
The API represents HKCU persistence for Server Manager preferences and subset definitions, but declares no storage.

## Dependencies And Integration Points
Consumers include server/service/aggregate/fileset preference loaders and subset management dialogs. It depends on Win32 `HKEY`, TCHAR strings, and `LPIDENT`.

## Risks And Test Signals
Risks are mostly API clarity around raw blobs and `fCreate == 2`. Compile coverage and registry round-trip tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.cpp

## Purpose
`problems.cpp` implements the Problems tab shown on property sheets when an AFS object has alerts. It summarizes alert count, displays alert descriptions/remedies, provides a remedy button, and updates itself when the underlying object changes.

## Important APIs, Types, And Functions
The dialog entry point is `Problems_DlgProc`. Internal handlers are `Problems_OnInitDialog`, `Problems_OnRefresh`, `Problems_OnRedraw`, `Problems_OnRemedy`, and `ParseFilesetName`. Remedy actions call `StartTask(taskREFRESH)`, `Filesets_ShowProperties`, `Aggregates_ShowProperties`, `Services_ShowServiceLog`, or `NewCredsDialog` depending on alert type.

## Control Flow
On initialization the dialog stores the target `LPIDENT`, subscribes through `NotifyMe`, formats a title based on object type, and refreshes. Refresh reads `Alert_GetCount`; zero alerts hide scrolling/remedy controls and show a no-problems string, one alert redraws without the scrollbar, and multiple alerts configure a scrollbar. Redraw reads the selected alert's description, remedy text, and button label. The remedy button maps selected alert type to the appropriate corrective UI or task.

## State And Persistence
State is dialog-local (`DWLP_USER`, scrollbar position, visible controls) plus the alert subsystem's state. No settings are persisted. Notification subscriptions are removed with `DontNotifyMeEver` on destroy.

## Dependencies And Integration Points
Dependencies include the alert subsystem, AFSClass notification dispatch (`WM_NOTIFY_FROM_DISPATCH`), service log viewing, fileset and aggregate properties, credentials dialogs, and resource strings. The macro in `problems.h` decides whether this tab is added to property sheets.

## Risks And Edge Cases
`WM_CTLCOLORSTATIC` returns a newly created brush without visible cleanup, which can leak GDI objects. `ParseFilesetName` appears to compute `pszBase[pszEnding - szFileset]`, subtracting pointers from different buffers; that is suspicious and could corrupt memory if the function is used. Remedy handling assumes alert target identities remain valid. Alerts with no button intentionally hide remediation.

## Test Signals
Test zero/one/multiple alert display, scrollbar navigation, notification-driven refresh, each remedy action, property-tab addition only when alerts exist, object-title formatting for all identity types, GDI leak checks, and direct tests for `ParseFilesetName` with `.readonly`, `.backup`, and ordinary names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.h

## Purpose
`problems.h` declares the Problems dialog procedure and provides a helper macro for conditionally adding the Problems tab to property sheets.

## Important APIs, Types, And Functions
`PropSheet_AddProblemsTab(_psh,_idd,_lpi,_nAlerts)` returns true without adding a tab when alert count is zero; otherwise it calls `PropSheet_AddTab` with `Problems_DlgProc`. The header declares `BOOL CALLBACK Problems_DlgProc(...)`.

## Control Flow
The macro is used during property sheet construction to avoid showing an empty Problems tab. The dialog procedure handles runtime refresh and remedy behavior.

## State And Persistence
No storage is declared. The macro passes `LPIDENT` as tab lParam so the dialog can access alert state.

## Dependencies And Integration Points
It depends on property-sheet helpers, resource ID `IDS_PROBLEMS`, and Win32 dialog signatures. It integrates property pages with the alert display module.

## Risks And Test Signals
Macro arguments may be evaluated more than once only for `_nAlerts` in the condition and `_lpi` in the add path, so callers should avoid side effects. Test property sheets with zero and nonzero alerts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/problems.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.cpp

## Purpose
`propcache.cpp` tracks currently open property and command dialogs so the UI can focus an existing dialog instead of opening duplicates and can find server windows for refresh.

## Important APIs, Types, And Functions
Public functions are `PropCache_Add`, `PropCache_Search`, `PropCache_Delete(PropCache, PVOID)`, and `PropCache_Delete(HWND)`. The private `PropCacheEntry` stores `fInUse`, `pcType`, `pv`, and `hDialog`. `ANYVALUE` searches/deletes by type regardless of payload.

## Control Flow
Adding first searches for an existing entry of the same type/payload. If none exists, it reuses a free slot or grows the static array by 16, records the dialog, and registers non-server dialogs with AfsAppLib as modeless dialogs. Search optionally starts after a supplied window, skips unused entries, drops entries whose window handle is no longer valid, and returns the first match. Delete marks matching entries unused.

## State And Persistence
State is process-local in a grow-only static array. No persistent settings are stored.

## Dependencies And Integration Points
The cache is used by options, fileset delete/clone, server-window refresh, and many property dialogs elsewhere in afssvrmgr. It depends on Win32 `IsWindow` and AfsAppLib modeless dialog registration.

## Risks And Edge Cases
There is no synchronization, so all callers are expected to run on the UI thread. Entries are not compacted and stale entries are removed only on search or explicit delete. Duplicate protection is by exact pointer value, so object identity stability is required. Server windows are not registered as modeless dialogs by design.

## Test Signals
Test duplicate dialog focusing, `ANYVALUE` search/delete, stale window cleanup, sequential search using `hwndStart`, modeless registration for non-server dialogs, and delete-on-destroy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.h

## Purpose
`propcache.h` defines dialog cache categories and declares the property-cache API.

## Important APIs, Types, And Functions
The `PropCache` enum covers server windows, server property/list/create/sync/install/security/salvage/hosts dialogs, service property/create dialogs, aggregate properties, fileset replication/properties/release/clone/delete dialogs, error dialogs, and general dialogs. `ANYVALUE` is `(PVOID)-1`. The API exposes add, search, and delete overloads.

## Control Flow
No logic is present. Dialogs call `PropCache_Add` on creation, use `PropCache_Search` before creating a new instance, and call `PropCache_Delete` on destroy.

## State And Persistence
The header declares no storage; the implementation maintains process-local state.

## Dependencies And Integration Points
It depends on Win32 `HWND` and pointer payloads. It is a cross-cutting GUI integration point for duplicate-dialog prevention and server-window refresh routing.

## Risks And Test Signals
Risks are enum/category mismatches and misuse of `ANYVALUE`. Compile coverage and duplicate-dialog tests for representative cache types validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/resource.h

## Purpose
`resource.h` is the Visual C++ resource identifier catalog for the Server Manager application. It assigns stable numeric IDs to localized strings, controls, dialogs, menus, icons, accelerators, animations, and commands.

## Important APIs, Types, And Functions
There are no functions. String IDs cover tab titles, column labels, status text, action names, alert descriptions/remedies/buttons, error messages, command-help labels, option text, and fileset/server/service operation messages. Control IDs cover main window controls, property page controls, fileset create/delete/move/dump/restore widgets, help dialogs, credentials/options, host/address/security/salvage controls, and shared buttons. Dialog/resource IDs include `IDD_MAIN`, service/aggregate/fileset tabs, operation dialogs, help dialogs, options, clone/dump/restore dialogs, and menus. Command IDs include view, refresh, properties, server/service/fileset actions, help, options, export, subset, icon-view, and keyboard accelerators.

## Control Flow
No executable flow exists. Dialog templates, menus, accelerators, C++ switch statements, help maps, and string formatters all use these IDs to bind UI resources to logic.

## State And Persistence
No runtime state is stored. The numeric assignments are effectively persistent ABI within compiled resources and code.

## Dependencies And Integration Points
Every afssvrmgr UI module depends on this header. The files in this work item reference IDs for display labels, help maps, options controls, fileset operation dialogs, problem controls, and commands such as `M_COLUMNS`.

## Risks And Edge Cases
The file intentionally contains reused numeric IDs for controls in different dialogs, which is normal but can confuse cross-dialog handlers. Resource ID collisions within the same dialog or command range would break message routing. Hand-edited changes can desynchronize `.rc` templates, help maps, and code.

## Test Signals
Test compile/resource compilation, opening each dialog, menu command routing, accelerator routing, help context registration, localization string formatting, and UI automation that exercises IDs referenced by display, options, help, problems, and fileset operation modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.cpp

## Purpose
`set_clone.cpp` implements fileset clone commands: cloning one selected fileset or cloning multiple filesets in a cell/server/aggregate scope with optional prefix filtering.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Clone`. Single-fileset UI is handled by `Filesets_Clone_DlgProc` and `Filesets_Clone_OnInitDialog`. Bulk clone UI is handled by `Filesets_Clonesys_DlgProc`, `Filesets_Clonesys_OnInitDialog`, `Filesets_Clonesys_OnOK`, `Filesets_Clonesys_OnSelect`, `Filesets_Clonesys_OnSelectServer`, and end-task handlers for server/aggregate enumeration.

## Control Flow
`Filesets_Clone` allocates `SET_CLONESYS_PARAMS`, defaults the target identity to the supplied object or current cell, and chooses a simple confirmation dialog for a fileset or a scope-selection dialog otherwise. Single clone confirmation starts `taskSET_CLONE` with the fileset identity. Bulk clone gathers scope controls, optional prefix/exclusion prefix, and starts `taskSET_CLONESYS`, transferring ownership of the parameter block to the task.

## State And Persistence
Dialog state lives in `SET_CLONESYS_PARAMS`: target identity, prefix flags, prefix text, and enumeration-complete flags. No settings are persisted. The property cache tracks clone dialogs while open.

## Dependencies And Integration Points
Dependencies include `PropCache`, task IDs `taskSET_CLONE`, `taskSET_CLONESYS`, `taskSVR_ENUM_TO_COMBOBOX`, and `taskAGG_ENUM_TO_COMBOBOX`, combobox helpers, current cell `g.lpiCell`, and resource controls for clone scope selection.

## Risks And Edge Cases
The same `pcSET_CLONE` cache key is used for both single and bulk clone dialogs with `NULL` payload, so only one clone dialog of either kind can be active. Prefix exclusion is encoded by a leading `!`, which is simple but ambiguous if a literal prefix begins with that character. OK can be disabled while asynchronous enumeration is incomplete; failed enumeration handling is minimal.

## Test Signals
Test single-fileset clone confirmation, bulk clone for cell/server/aggregate, server combobox enumeration, aggregate combobox refresh when server changes, prefix include/exclude parsing, OK enablement during enumeration, cancel cleanup, and task parameter ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.h

## Purpose
`set_clone.h` declares the fileset clone UI entry point and the parameter block used by single and bulk clone workflows.

## Important APIs, Types, And Functions
`SET_CLONESYS_PARAMS` stores `LPIDENT lpi`, prefix include/exclude flags, a `MAX_PATH` prefix buffer, and server/aggregate enumeration flags. The public function is `Filesets_Clone(LPIDENT lpi)`.

## Control Flow
Callers pass a fileset, aggregate, server, or cell identity. The implementation decides whether to show single or bulk clone UI and then starts the relevant task.

## State And Persistence
The struct is runtime task/dialog state. It is not persisted.

## Dependencies And Integration Points
The header depends on `LPIDENT`, `BOOL`, and `TCHAR`. Task handlers consume this struct for `taskSET_CLONESYS`.

## Risks And Test Signals
Risks include ownership transfer of the struct to asynchronous tasks and prefix buffer truncation. Compile coverage and clone task tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_clone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.cpp

## Purpose
`set_col.cpp` defines default fileset and replica views and formats column text for FastList callbacks.

## Important APIs, Types, And Functions
Public functions are `Filesets_SetDefaultView`, `Filesets_GetAlertCount`, `Filesets_GetColumnText`, `Replicas_SetDefaultView`, and `Replicas_GetColumnText`. Formatting covers fileset name, aggregate/server location, type, create/update/access/backup times, quota used/free/total/percent, status, numeric ID, file count, and replica server/aggregate/update date.

## Control Flow
Default-view functions copy resource IDs and widths from static column tables and set visible columns/sort. `Filesets_GetColumnText` rotates through static buffers, reads cached `FILESETSTATUS` from `FILESET_PREF`, formats the requested column, and uses alert descriptions before raw state flags for status. `Replicas_GetColumnText` similarly formats location and update date from cached fileset status.

## State And Persistence
The module uses static rotating text buffers sized by column count. It reads but does not write per-fileset preference cache state populated by display refreshes. `VIEWINFO` state is caller-owned and later persisted elsewhere.

## Dependencies And Integration Points
Dependencies include resource strings, alert helpers, `FormatTime`, `FormatString`, `LPIDENT` name accessors, fileset status flags/types, and global constants such as `ck1MB`. `display.cpp` calls these functions through `GetItemText`.

## Risks And Edge Cases
Static buffers are not thread-safe and returned pointers must be consumed immediately. `setcolQUOTA_FREE` subtracts used from quota without guarding underflow. Percent defaults to 100 when quota is zero. Type/status text depends on cached status; before a refresh columns may be blank or say no alerts.

## Test Signals
Test default column order/widths, all fileset types, quota formatting including zero and over-quota cases, alert versus state status precedence, date formatting failures, server-name inclusion, replica columns, and concurrent list rendering assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.h

## Purpose
`set_col.h` declares fileset and replica column metadata and formatter APIs.

## Important APIs, Types, And Functions
`FILESETCOLUMN` enumerates fileset columns, and `FILESETCOLUMNS` maps each to a resource string and width. `REPLICACOLUMN` and `REPLICACOLUMNS` do the same for replica views. Macros `nFILESETCOLUMNS` and `nREPLICACOLUMNS` expose counts. Functions declare default-view setup and text retrieval for filesets and replicas.

## Control Flow
No executable logic exists. Display code uses these enums as indexes in `VIEWINFO::aColumns` and callback dispatch.

## State And Persistence
The static column tables live in each translation unit that includes the header. View selections are stored in `VIEWINFO` instances elsewhere.

## Dependencies And Integration Points
The header depends on resource IDs, `LPVIEWINFO`, `LPFILESET`, `LPIDENT`, and column justification flags. It integrates display callbacks with fileset and replica tabs/dialogs.

## Risks And Test Signals
Because the static tables are in a header, every including source gets its own copy. Enum order must match table order and resource strings. Test default views and column chooser behavior after adding or reordering columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.cpp

## Purpose
`set_create.cpp` implements the Create Fileset dialog. It collects a fileset name, target aggregate, quota, quota units, and optional clone creation flag, then starts the asynchronous fileset creation task.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Create`. Internal handlers include `Filesets_Create_DlgProc`, `Filesets_Create_OnInitDialog`, `Filesets_Create_OnSelectServer`, `Filesets_Create_StartDisplay_Aggregates`, `Filesets_Create_OnEndTask_EnumAggregates`, `Filesets_Create_EnableOK`, and `Filesets_Create_OnEndTask_FindQuotaLimits`. A subclass procedure handles the columns context menu for the aggregate list.

## Control Flow
`Filesets_Create` allocates `SET_CREATE_PARAMS`, sets defaults (`ckQUOTA_DEFAULT`, no clone), displays `IDD_SET_CREATE`, validates the aggregate and name, and starts `taskSET_CREATE`. The dialog asynchronously enumerates servers to a combobox, enumerates aggregates to a FastList, and finds quota limits for the selected aggregate. Selection and column changes refresh the aggregate list. Quota unit changes recalculate spinner limits. OK is enabled only when a target aggregate and nonempty fileset name exist.

## State And Persistence
Runtime state is in `SET_CREATE_PARAMS` plus global view state `gr.viewAggCreate` and `gr.cbQuotaUnits`. The aggregate list view layout is restored/stored through `FL_RestoreView` and `FL_StoreView`; global settings persistence happens elsewhere. The task owns the params after a successful OK.

## Dependencies And Integration Points
Dependencies include `set_general.h` quota constants, columns UI, server-window helpers, display text callbacks, task packets `SVR_ENUM_TO_COMBOBOX_PACKET` and `AGG_ENUM_TO_LISTVIEW_PACKET`, and task IDs `taskSET_CREATE`, `taskAGG_FIND_QUOTA_LIMITS`, `taskSVR_ENUM_TO_COMBOBOX`, and `taskAGG_ENUM_TO_LISTVIEW`.

## Risks And Edge Cases
Name validation is limited to nonempty text in this UI; deeper validation must occur in the task layer. Quota conversions can lose precision when switching to MB units. The list subclass procedure uses a static original WNDPROC, so multiple simultaneous create dialogs would share it. Server/aggregate enumeration failure handling is minimal.

## Test Signals
Test initial parent aggregate selection, empty-name OK disable, quota spinner range and unit conversion, aggregate selection updates quota limits, server change clears invalid aggregate target, column chooser persistence, cancel cleanup, and task parameter correctness on OK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.h

## Purpose
`set_create.h` declares the Create Fileset dialog entry point and the task parameter structure for fileset creation.

## Important APIs, Types, And Functions
`SET_CREATE_PARAMS` contains the target aggregate identity, new fileset name, quota in KB units, and whether to create a clone. `Filesets_Create(LPIDENT lpiParent = NULL)` opens the dialog.

## Control Flow
The dialog fills the struct and transfers it to `taskSET_CREATE` on success. On cancel or validation failure, the implementation deletes it.

## State And Persistence
The struct is transient dialog/task state. No persistent settings are declared here.

## Dependencies And Integration Points
Consumers need `LPIDENT`, `TCHAR`, quota units, and task-layer agreement on `SET_CREATE_PARAMS`.

## Risks And Test Signals
Risks include ownership transfer and quota unit assumptions. Compile coverage and task tests for create-fileset parameter handling are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.cpp

## Purpose
`set_createrep.cpp` implements the Create Replica dialog, allowing a read-write fileset to be replicated onto a selected aggregate.

## Important APIs, Types, And Functions
The public entry point is `Filesets_CreateReplica`. Internal handlers include `Filesets_CreateReplica_DlgProc`, `Filesets_CreateReplica_OnInitDialog`, `Filesets_CreateReplica_OnSelectServer`, `Filesets_CreateReplica_StartDisplay_Aggregates`, `Filesets_CreateReplica_OnEndTask_EnumAggregates`, and `Filesets_CreateReplica_EnableOK`. A subclass procedure supports the aggregate-list columns menu.

## Control Flow
The entry point allocates `SET_CREATEREP_PARAMS`, shows `IDD_SET_CREATEREP`, validates that the target is an aggregate, and starts `taskSET_CREATEREP`. Initialization formats the source server/aggregate/fileset into the dialog title text, restores the aggregate view, disables OK/list/server controls, and asynchronously enumerates servers. When a server is selected, aggregate enumeration starts; selecting an aggregate enables OK.

## State And Persistence
Runtime state is the source and target identity pair. `gr.viewAggMove` is reused for the aggregate list layout and stored on destroy. No registry persistence is performed directly.

## Dependencies And Integration Points
Dependencies include columns UI, display text callbacks, server combobox enumeration, aggregate list enumeration, global aggregate view state, and task IDs `taskSVR_ENUM_TO_COMBOBOX`, `taskAGG_ENUM_TO_LISTVIEW`, and `taskSET_CREATEREP`. It is used by fileset drag/drop and "replicate here" workflows.

## Risks And Edge Cases
The dialog assumes the caller supplies a valid source fileset; it validates only target aggregate on OK. Static list subclass state limits simultaneous dialogs. Failed enumeration has little user-visible handling. Reusing `gr.viewAggMove` couples create-replica and move dialog column choices.

## Test Signals
Test default target selection, server-change target clearing, aggregate selection OK enablement, formatted source text, column menu behavior, cancel cleanup, and task parameter identity correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.h

## Purpose
`set_createrep.h` declares Create Replica UI and its parameter block.

## Important APIs, Types, And Functions
`SET_CREATEREP_PARAMS` contains `lpiSource` and `lpiTarget`. `Filesets_CreateReplica(LPIDENT lpiSource, LPIDENT lpiTarget = NULL)` opens the confirmation/selection dialog.

## Control Flow
The implementation fills or updates `lpiTarget`, then transfers the struct to `taskSET_CREATEREP` on OK.

## State And Persistence
The struct is transient dialog/task state and has no persistence.

## Dependencies And Integration Points
The API depends on `LPIDENT` and is called by fileset menu/drag/drop workflows.

## Risks And Test Signals
Risks include ownership transfer and validating that source/target identities remain live. Compile coverage and create-replica task tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.cpp

## Purpose
`set_delete.cpp` implements fileset deletion confirmation. It handles normal read-write volumes, read-only replicas, clones, and ghost state where VLDB and server entries may differ.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Delete`. Internal handlers are `Filesets_Delete_DlgProc`, `Filesets_Delete_OnInitDialog`, `Filesets_Delete_OnEndTask_FindGhost`, `Filesets_Delete_OnCheckBoxes`, and `Filesets_Delete_ShrinkWindow`. Parameters are stored in `SET_DELETE_PARAMS`.

## Control Flow
Before opening a dialog, `Filesets_Delete` checks `PropCache` for an existing delete dialog for that fileset. The modeless dialog starts hidden, formats object text, disables OK, and starts `taskSET_FIND_GHOST`. When status returns, it rejects replicated read-write filesets, sets default VLDB/server deletion checkboxes from ghost bits, specializes the dialog for replicas or clones by hiding checkboxes, enables only valid choices, shows the dialog, and eventually starts `taskSET_DELETE` if the user selected at least one deletion surface.

## State And Persistence
Dialog/task state includes target identity, selected VLDB/server deletion flags, ghost flags, and current help dialog ID. The property cache prevents duplicate modeless delete dialogs. No settings are persisted.

## Dependencies And Integration Points
Dependencies include `PropCache`, AfsAppLib help, `taskSET_FIND_GHOST`, `taskSET_DELETE`, fileset status types, ghost flag constants, error dialogs, and resource strings for normal/replica/clone descriptions.

## Risks And Edge Cases
The dialog is modeless and transfers ownership of `SET_DELETE_PARAMS` to the task on OK, so lifetime bugs are possible if later messages arrive. Destroying the window after starting the task leaves task-layer ownership. Replicated read-write filesets are blocked based on the ghost/status task result. Shrink logic assumes specific control positions.

## Test Signals
Test duplicate dialog focus, ghost combinations, read-write with replicas rejection, replica and clone specialized layouts, VLDB/server checkbox enablement, OK disable when nothing selected, cancel cleanup, task parameter values, and hidden-until-status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.h

## Purpose
`set_delete.h` declares fileset deletion UI and the task parameter structure.

## Important APIs, Types, And Functions
`SET_DELETE_PARAMS` stores target fileset identity, booleans for VLDB and server deletion, ghost flags, and the help dialog ID. `Filesets_Delete(LPIDENT lpiFileset)` opens or focuses the delete dialog.

## Control Flow
The implementation fills the struct after a ghost-status task and passes it to `taskSET_DELETE` on confirmation.

## State And Persistence
The struct is runtime dialog/task state. No persistence is declared.

## Dependencies And Integration Points
It depends on `LPIDENT`, Win32 booleans, and ghost/task semantics defined elsewhere.

## Risks And Test Signals
Risks include task ownership and consistency between `wGhost`, `fVLDB`, and `fServer`. Compile and delete-task parameter tests cover the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_delete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.cpp

## Purpose
`set_dump.cpp` implements the Dump Fileset dialog, collecting a local dump filename and optional incremental timestamp before starting the dump task.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Dump`. Internal handlers are `Filesets_Dump_DlgProc`, `Filesets_Dump_OnInitDialog`, `Filesets_Dump_OnSelect`, `Filesets_Dump_EnableOK`, `Filesets_Dump_OnOK`, and `Filesets_Dump_OnBrowse`.

## Control Flow
`Filesets_Dump` allocates `SET_DUMP_PARAMS`, shows `IDD_SET_DUMP`, and starts `taskSET_DUMP` on OK. Initialization formats source identity text, creates a default dump filename from the fileset name, initializes date/time controls to local time, selects full dump by default, and enables OK only when a filename exists. Radio changes toggle date/time controls. Browse builds a filter from localized strings and uses `GetSaveFileName` with overwrite and path checks.

## State And Persistence
Runtime state includes target identity, filename, `fDumpByDate`, and `stDump`. No settings are persisted. The selected filename is copied into the task parameter block on OK.

## Dependencies And Integration Points
Dependencies include Win32 common dialogs, date/time helper controls (`DA_*`, `TI_*`), resource strings, and task ID `taskSET_DUMP`. It integrates with fileset menus and action-progress handling through the task subsystem.

## Risks And Edge Cases
The dialog validates only that the filename field is nonempty; path validity is mostly delegated to `GetSaveFileName` when browse is used and to the dump task otherwise. The filter parsing depends on the final character of the localized string being the separator. Date/time is local time, while backend interpretation must agree on timezone semantics.

## Test Signals
Test default filename generation, browse filter and default extension, manual filename validation, full versus time-limited dump selection, date/time round-trip, cancel cleanup, and task parameter values for full and incremental dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.h

## Purpose
`set_dump.h` declares the Dump Fileset dialog and its task parameters.

## Important APIs, Types, And Functions
`SET_DUMP_PARAMS` stores target fileset identity, dump filename, whether the dump is limited by date, and the selected `SYSTEMTIME`. `Filesets_Dump(LPIDENT lpi)` opens the dialog.

## Control Flow
The implementation fills the struct and transfers it to `taskSET_DUMP` on OK.

## State And Persistence
The struct is transient runtime state and has no persistence.

## Dependencies And Integration Points
It depends on `LPIDENT`, `TCHAR`, `MAX_PATH`, and Win32 `SYSTEMTIME`. The task layer consumes this struct.

## Risks And Test Signals
Risks include filename truncation and local-time interpretation. Compile coverage and dump task parameter tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.cpp

## Purpose
`set_general.cpp` contains common fileset helpers for preferences, selection, focus lookup, and lock-state checks.

## Important APIs, Types, And Functions
Public functions are `Filesets_LoadPreferences`, `Filesets_SavePreferences`, `Filesets_GetSelected`, `Filesets_GetFocused`, and `Filesets_fIsLocked`.

## Control Flow
Preference loading allocates `FILESET_PREF`, attempts registry restore, and falls back to default warning and alert settings. It always calls `Alert_Initialize`. Saving retrieves the preference pointer from the identity user param and stores it if present. Selection/focus helpers read `IDC_SET_LIST` FastList state, optionally hit-testing a point. Lock checks test `fsLOCKED` in a `FILESETSTATUS`.

## State And Persistence
Fileset preferences are registry-backed through `RestorePreferences` and `StorePreferences`. Runtime user-param state stores warning settings, alert options, last status, and read-write identity as populated by other modules.

## Dependencies And Integration Points
Dependencies include preference helpers, alert initialization/defaults, FastList wrappers, resource control `IDC_SET_LIST`, and fileset status flags. Display and property modules use these helpers.

## Risks And Edge Cases
`Filesets_LoadPreferences` assumes allocation succeeds. `Filesets_SavePreferences` silently returns false if no user param exists. `Filesets_GetFocusedItem` is declared in the header but not implemented in this file, suggesting either dead API or implementation elsewhere; this should be checked by link coverage.

## Test Signals
Test preference fallback, registry round-trip, alert initialization after restore, selected/focused identity retrieval, point hit testing, lock-state detection, and link coverage for all header declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.h

## Purpose
`set_general.h` declares common fileset helper APIs and quota/list constants.

## Important APIs, Types, And Functions
Constants include `ckQUOTA_DEFAULT`, `ckQUOTA_MINIMUM`, `ckQUOTA_MAXIMUM`, and `LVIS_ALL`. Functions declare fileset preference load/save, selected/focused identity lookup, focused tree item lookup, and lock-state detection.

## Control Flow
No logic exists in the header. Callers use these helpers from fileset tabs, display code, and fileset operation dialogs.

## State And Persistence
The declared preference helpers persist fileset preferences through the registry-backed preference layer. Other helpers are runtime UI state accessors.

## Dependencies And Integration Points
It depends on fileset identities/status, Win32 list/tree types, quota constants such as `ck1TB`, and `FILESET_PREF` definitions from broader `svrmgr.h`.

## Risks And Test Signals
`Filesets_GetFocusedItem` is declared but not visible in the paired implementation read here, so link or dead-code checks are important. Quota max is near signed 32-bit KB limits and must match task/server expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.cpp

## Purpose
`set_move.cpp` implements the Move Fileset dialog, choosing a destination aggregate for an existing fileset and starting the move task.

## Important APIs, Types, And Functions
The public entry point is `Filesets_ShowMoveTo`. Internal handlers include `Filesets_MoveTo_DlgProc`, `Filesets_MoveTo_OnInitDialog`, `Filesets_MoveTo_OnEndTask_InitDialog`, `Filesets_MoveTo_OnSelectServer`, `Filesets_MoveTo_StartDisplay_Aggregates`, `Filesets_MoveTo_OnEndTask_EnumAggregates`, and `Filesets_MoveTo_EnableOK`. A list subclass procedure supports the columns context menu.

## Control Flow
The entry point allocates `SET_MOVE_PARAMS`, shows `IDD_SET_MOVETO`, validates a target aggregate, and starts `taskSET_MOVE`. Initialization restores `gr.viewAggMove`, disables controls, and starts `taskSET_MOVETO_INIT` to fetch source status. The end-task handler formats a read-write/read-only description or shows an error, then enumerates servers. Server selection clears invalid targets and starts aggregate enumeration. Aggregate selection enables OK.

## State And Persistence
Runtime state is the source/target identity pair and the selected server stored in `DWLP_USER`. Aggregate list layout is stored in `gr.viewAggMove` through FastList view helpers. No direct registry writes occur.

## Dependencies And Integration Points
Dependencies include columns UI, display text callbacks, server/aggregate enumeration tasks, source-status task `taskSET_MOVETO_INIT`, move task `taskSET_MOVE`, resource strings, and global aggregate view state. Drag/drop code calls this entry point for move-here actions.

## Risks And Edge Cases
`Filesets_MoveTo_StartDisplay_Aggregates` sets `lpp->lpiServer = NULL`, so despite storing selected server in `DWLP_USER`, aggregate enumeration may not be server-filtered here unless the task infers it from dialog state. That is worth regression testing. Static subclass state limits simultaneous dialogs. Source-status failure cancels the dialog.

## Test Signals
Test read-write/read-only source descriptions, server selection filtering, target clearing when server changes, aggregate selection OK enablement, column chooser persistence, source-status error path, drag/drop default target, and task parameter identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.h

## Purpose
`set_move.h` declares the Move Fileset dialog and its parameter structure.

## Important APIs, Types, And Functions
`SET_MOVE_PARAMS` contains `lpiSource` and `lpiTarget`. `Filesets_ShowMoveTo(LPIDENT lpiSource, LPIDENT lpiTarget)` opens the dialog.

## Control Flow
The implementation updates `lpiTarget` from UI selection and transfers the struct to `taskSET_MOVE` on OK.

## State And Persistence
The struct is transient dialog/task state and is not persisted.

## Dependencies And Integration Points
The header depends on `LPIDENT` and is used by fileset menu and drag/drop paths.

## Risks And Test Signals
Risks include ownership transfer and stale identities between dialog open and task execution. Compile coverage and move task parameter tests validate the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.h -->
