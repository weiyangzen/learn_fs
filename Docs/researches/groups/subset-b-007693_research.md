# Research: subset-b-007693

Grouped research for OpenAFS `src/WINNT/afsapplib` files. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_creds.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_creds.cpp

Purpose: Implements AFS credential acquisition, credential cracking, validation, bad/expired credential warnings, and the reusable Open Cell/New Credentials dialogs used by Windows admin UI code.

Important APIs and functions: `AfsAppLib_CrackCredentials`, `AfsAppLib_GetCredentials`, and `AfsAppLib_SetCredentials` bridge callers to either the admin-server client (`asc_*`) or dynamically loaded local AFS client admin APIs. `AfsAppLib_ShowOpenCellDialog` and `AfsAppLib_ShowCredentialsDialog` wrap modal dialogs. Dialog procedures `OpenCell_DlgProc`, `NewCreds_DlgProc`, and `BadCreds_DlgProc` dispatch help hooks, command handling, and initialization. `AfsAppLib_CheckCredentials`, `AfsAppLib_IsUserAdmin`, `AfsAppLib_CheckForExpiredCredentials`, and `OnExpiredCredentials` implement validation and warning policy.

Control flow: Credential read/set operations first prefer `AfsAppLib_GetAdminServerClientID`; without an admin server, they call `OpenClientLibrary`, convert Unicode/TCHAR inputs to ANSI buffers, call `afsclient_Token*`, then close the library. The Open Cell dialog populates the cell combo, starts `OpenCell_OnCell_ThreadProc` on cell edits, and receives `WM_REFRESHED_CREDENTIALS` with current credential status. OK handlers disable controls, show an hourglass, set tokens, and then call `AfsAppLib_CheckCredentials`.

State and persistence: Dialog state is stored in caller-supplied parameter structs via `DWLP_USER`. `AfsAppLib_SetCredentials` posts `WM_REFRESHED_CREDENTIALS` with a token handle. `AfsAppLib_CheckForExpiredCredentials` uses static `hCredsPrevious` and `fHadGoodCredentials` to detect transitions from valid to expired/destroyed. Warning suppression is persisted only through the caller-owned `pfShowWarningEver` pointer.

Dependencies and integration points: Requires Win32 dialogs/messages, `TaLocale` formatting, `al_dynlink` function pointers, `TaAfsAdmSvrClient`, `al_messages.h`, and resource IDs from `al_resource.h`. It also depends on `AfsAppLib_GetLocalCell`, `AfsAppLib_IsTimeInFuture`, `FormatString`, `ModalDialogParam`, and main-window routing.

Risks: Background credential checks can race with cell changes, partially mitigated by comparing returned cell text. Created threads are not joined and handles are not closed. Fixed-size ANSI buffers (`cchRESOURCE`) and password copies increase truncation/sensitive-data lifetime risk. `AfsAppLib_CrackCredentials` only writes `pStatus` when `!hCreds`, which may hide failure detail for invalid non-null handles. Under default non-`USE_KASERVER`, `AfsAppLib_IsUserAdmin` returns `TRUE`, so admin validation is compile-time dependent.

Test signals: Exercise admin-server and local-client paths; verify empty/default cell behavior; test invalid, expired, destroyed, and non-admin credentials; confirm warning suppression; verify `WM_REFRESHED_CREDENTIALS` and `WM_EXPIRED_CREDENTIALS`; test cancellation, help routing, and dialog hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_creds.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.cpp

Purpose: Lazily loads OpenAFS admin DLLs and resolves the client, KAS, and utility admin entry points needed by the app library when no remote admin server client is in use.

Important APIs and functions: `OpenUtilLibrary`/`CloseUtilLibrary`, `OpenKasLibrary`/`CloseKasLibrary`, and `OpenClientLibrary`/`CloseClientLibrary` maintain module handles and exported function pointer variables declared in `al_dynlink.h`. Loaded DLLs are `AfsAdminUtil.dll`, `AfsKasAdmin.dll`, and `AfsClientAdmin.dll`.

Control flow: Each `Open*Library` increments a request counter, loads the DLL only on the first request, resolves all required exports with `GetProcAddress`, and rolls back by calling the corresponding close function if any step fails. `OpenClientLibrary` additionally resolves `afsclient_Init` and calls it before reporting success. Each `Close*Library` decrements the request count and frees the library when it reaches zero.

State and persistence: Global static counters (`g_cReq*Library`), module handles, and global function pointers hold process-local library state. There is no on-disk persistence and no explicit synchronization around counters or function pointer mutation.

Dependencies and integration points: Includes AFS admin headers for function signatures and Win32 `LoadLibrary`/`FreeLibrary`. Used by credential, error translation, and misc routines to call AFS client/admin APIs through macro aliases.

Risks: The reference counters are unsigned `size_t`; calling a close routine without a matching open underflows and prevents cleanup. The code is not thread-safe, so concurrent opens/closes can race. Partial failure leaves some function pointers stale until next successful load. DLL names are unqualified, so Windows DLL search-order behavior matters.

Test signals: Test successful and missing-DLL cases, missing export cases, repeated nested opens/closes, client init failure, and concurrent access from credential/background worker paths. Confirm `pStatus` receives useful `GetLastError` or AFS status values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.h

Purpose: Declares the dynamic-loading interface for optional OpenAFS admin DLLs and exposes macro names that make function-pointer calls look like normal API calls.

Important APIs and types: Declares `OpenUtilLibrary`, `OpenKasLibrary`, `OpenClientLibrary` and close counterparts. Defines function pointer typedefs for utility error translation, KAS principal enumeration/get, token get/new/close/query, cell open/close, and local cell lookup. Declares extern variables such as `afsclient_TokenGetExistingP` and maps `afsclient_TokenGetExisting` to `(*afsclient_TokenGetExistingP)`.

Control flow: This header has no runtime logic; it creates the contract that callers must obey: call `Open*Library` before using the macro-expanded function pointers and `Close*Library` afterward.

State and persistence: State is external global process state implemented in `al_dynlink.cpp`. There is no persistence.

Dependencies and integration points: Pulls in `afs_Admin.h`, `afs_utilAdmin.h`, `afs_kasAdmin.h`, and `afs_clientAdmin.h`. It is included by credential, misc/error translation, and KAS-related code.

Risks: Macro aliases hide pointer dereferences and will crash if callers forget to open the library or ignore `Open*Library` failure. The header exposes mutable globals across compilation units, making ownership and thread-safety unclear.

Test signals: Compile tests should verify typedef compatibility with shipped DLL exports. Runtime tests should call every macro only after a successful open and confirm failure paths never dereference null pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_error.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_error.cpp

Purpose: Provides asynchronous and immediate error dialogs for the Windows app library, including fatal-error behavior.

Important APIs and functions: Overloaded `ErrorDialog` and `FatalErrorDialog` accept either string pointers or resource IDs plus varargs. `ImmediateErrorDialog` shows a modal dialog synchronously. `vErrorDialog` allocates an `ERRORPARAMS` packet and routes creation through the main window via `WM_CREATE_ERROR_DIALOG`. `Error_DlgProc` formats and displays the description/status controls.

Control flow: Asynchronous calls allocate formatted text, then either call `OnCreateErrorDialog` immediately if no main window exists or post to the main window so UI is created on the main thread. `OnCreateErrorDialog` opens `IDD_APPLIB_ERROR`, posts quit for fatal dialogs, and frees allocated strings/packets. The dialog hides the status field when `dwError == 0`; otherwise it formats the status using `%e`.

State and persistence: No durable state. Transient state is an allocated `ERRORPARAMS` object transferred by message. Fatal state is represented by `fFatal` and results in `PostQuitMessage`.

Dependencies and integration points: Uses `AfsAppLib_GetMainWindow`, `AfsAppLib_GetAppName`, `AfsAppLib_TranslateError`, `FormatString`, `ModalDialogParam`, and resource IDs from `al_resource.h`/localized resources. Integrated through `WM_CREATE_ERROR_DIALOG`.

Risks: Varargs wrappers do not call `va_end`. Posting heap pointers to the main window assumes the destination outlives the packet and handles the custom message. `(LONG)(LONG_PTR)pszError` is pointer-to-integer storage and is sensitive to platform width assumptions in older code. Fatal dialogs terminate message loop after user dismissal.

Test signals: Verify resource-ID and literal-string overloads, zero/nonzero status layout, fatal quit behavior, no-main-window behavior, main-window-posted behavior, and translation fallback for unknown errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_error.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_help.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_help.cpp

Purpose: Maintains dialog-to-help context registrations and handles `IDHELP`/`WM_HELP` for app-library dialogs.

Important APIs and functions: `AfsAppLib_RegisterHelpFile` sets the global help filename. `AfsAppLib_RegisterHelp` inserts or updates a `DIALOGHELP` entry containing dialog ID, per-control help context array, and overview context ID. `AfsAppLib_HandleHelp` handles command and F1/help messages.

Control flow: On `IDHELP`, it finds the matching dialog record and calls `WinHelp(..., HELP_CONTEXT, idhOverview)`. On `WM_HELP`, it either redirects dialog-level help to the `IDHELP` command or calls `WinHelp(..., HELP_WM_HELP, adwContext)` for a specific child control.

State and persistence: Global `g_szHelpfile`, dynamically grown `g_adh`, and `g_cdh` are process-local. No persistent storage; registrations are expected during app initialization.

Dependencies and integration points: Uses Win32 `WinHelp`, app allocation macro `REALLOC`, and is called by dialog procedures such as credential and bad-credential dialogs before normal message handling.

Risks: No synchronization protects the global registry. `if (g_szHelpfile)` is always true for the static array, so an empty filename can still be passed if registered empty. `WinHelp` is legacy/deprecated and may be unavailable on modern Windows without compatibility components.

Test signals: Register duplicate dialog IDs and confirm updates; test overview help, control help, missing registration fallback, empty help file behavior, and hook procedures that consume messages before help handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_help.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_messages.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_messages.h

Purpose: Centralizes custom `WM_USER` message IDs used by the app library for cross-thread UI requests, background task completion, credential changes, and dialog control.

Important APIs and definitions: Defines `WM_COVER_WINDOW`, `WM_CREATE_ERROR_DIALOG`, `WM_ENDTASK`, `WM_EXPIRED_CREDENTIALS`, `WM_CLOSE_DIALOG`, `WM_PERMTAB_REFRESH`, and `WM_REFRESHED_CREDENTIALS`, with comments documenting expected `WPARAM`/`LPARAM` payloads.

Control flow: This header has no execution logic. It reserves a message range starting at `WM_USER + 0x200` and allows modules such as error handling, task queue, cover dialogs, and credential code to communicate without hard-coded local constants.

State and persistence: None.

Dependencies and integration points: Included transitively via `afsapplib.h` by UI modules. It must stay consistent with message handlers in `al_error.cpp`, `al_task.cpp`, `al_creds.cpp`, cover-window code, and permission tabs.

Risks: Message IDs are library-private but still occupy the receiving window's `WM_USER` namespace, so embedding in foreign controls/windows could collide. Payload comments must remain accurate because the compiler cannot enforce `LPARAM` pointer ownership.

Test signals: Static checks for unique message IDs; integration tests for posted heap payload lifetime and handlers for each documented message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_misc.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_misc.cpp

Purpose: Provides library startup, image-list/icon helpers, spinner animation, AFS error translation, cell-list management, time/credential utility functions, reallocation, and font creation.

Important APIs and functions: `DllEntryPoint` initializes locale, error translation, common controls, and custom control classes. `AfsAppLib_CreateImageList`/`AfsAppLib_AddToImageList` build standard AFS object icon lists. `AfsAppLib_StartAnimation`/`StopAnimation` animate static icons. `AfsAppLib_TranslateErrorFunc` and `AfsAppLib_TranslateError` bridge admin-server/local utility error text. Cell APIs include `AfsAppLib_GetCellList`, `AfsAppLib_AddToCellList`, and `AfsAppLib_FreeCellList`. Utility APIs include `AfsAppLib_IsTimeInFuture`, `AfsAppLib_UnixTimeToSystemTime`, `AfsAppLib_SplitCredentials`, `AfsAppLib_GetLocalCell`, `AfsAppLib_ReallocFunction`, and `AfsAppLib_CreateFont`.

Control flow: DLL attach registers custom controls and error translation. Error translation prefers admin server, otherwise opens `AfsAdminUtil.dll`. Cell list reading enumerates registry subkeys, ensures the local cell is first, and trims null tail entries. Local cell lookup caches the first successful result in a static buffer. Animation uses a timer hook storing frame index in window data.

State and persistence: Holds process-level module handles, cached app instance, cached local cell, static animation icons, and registry-backed cell list entries. `AfsAppLib_AddToCellList` persists cells by creating registry keys.

Dependencies and integration points: Integrates with `TaLocale`, dynamic link helpers, `TaAfsAdmSvrClient`, image list common controls, custom control registration functions, registry APIs, and `SetErrorTranslationFunction`.

Risks: Static caches are not synchronized. Animation icons are never destroyed. Some registry operations use legacy `RegOpenKey`/`RegEnumKey`. `AfsAppLib_CreateFont` mutates the loaded resource string while parsing and assumes comma sections exist. Time conversion has manual FILETIME offset logic and elapsed mode subtracts fields from 1970/1/1.

Test signals: Load/unload DLL, verify every custom class registers; test 16/32 icon list sizes; animate start/stop; translate AFS/admin/unknown statuses; enumerate/persist cells; local cell fallback; Unix time conversion including elapsed; font resource parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_misc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.cpp

Purpose: Implements `PROGRESSDISPLAY`, a helper object that binds a dialog progress UI to a background worker thread.

Important APIs and functions: Constructors wrap an existing window or create a modeless dialog. Public methods get/set range, progress, operation text, finish message, status, and close the display. `Show` starts `ThreadProc`; `Finish` records status and notifies UI; `OnUpdate` refreshes the progress bar and text. Static `ProgressDisplay_HookProc` handles update and destruction messages.

Control flow: `Init` stores `this` in `DWLP_USER`, installs a subclass hook, initializes critical section/refcount, captures localized text templates, and configures progress range. `Show` increments the reference count, shows the dialog, creates a worker thread, and either pumps messages modally until finished or returns immediately if a finish message is configured. The worker invokes the user callback and calls `Finish`.

State and persistence: Per-object mutable state is protected by `m_cs`: progress range, current progress, operation text, finished flag, status, callback pointer, and refcount. No persistent storage.

Dependencies and integration points: Uses Win32 dialogs, common-control progress bar messages, `subclass.h`, `FormatString`, resource/control IDs from `al_progress.h`, and app allocation macros.

Risks: Worker thread handle is not closed. Destructor assumes `m_hWnd` is valid enough for `SetWindowLongPtr`. `SetProgress` is monotonic and cannot move progress backward. `m_cRef` deletion protocol is subtle because `Close` and `Finish` can both decrement. `Show` creates the thread before checking handle success.

Test signals: Existing-window and created-dialog paths; modal and finish-message modeless modes; worker exceptions; close-before-finish; progress range edge cases; operation text updates from worker thread; destruction cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.h

Purpose: Declares the `PROGRESSDISPLAY` class and the control IDs expected by progress dialog templates.

Important APIs and types: Exports `PROGRESSDISPLAY` with constructors, `GetProgressDisplay`, range/progress accessors, operation text accessors, `SetFinishMessage`, `Show`, `Close`, `GetStatus`, and `GetWindow`. Defines `IDC_OPERATION`, `IDC_PROGRESS`, and `IDC_PROGRESSTEXT`.

Control flow: No runtime logic; the header defines the callback signature accepted by `Show` and documents modal versus modeless behavior.

State and persistence: Declares private fields for finished/status state, critical section, refcount, dialog ownership, callback data, range/progress, and UI text buffers.

Dependencies and integration points: Includes `TaLocale.h` and `subclass.h`; requires dialog templates to provide the declared control IDs and a callback matching `DWORD CALLBACK fn(LPPROGRESSDISPLAY, LPARAM)`.

Risks: The private method declarations include qualified names inside the class (`void PROGRESSDISPLAY::OnUpdate`) which is non-standard in modern C++ compilers. The class self-deletes through private destructor/refcount behavior, making ownership easy to misuse.

Test signals: Compile with target compiler; verify dialog templates contain required IDs; test client code that stores pointers after `Close`/finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_pump.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_pump.cpp

Purpose: Provides the main message pump's modeless-dialog routing and a small per-window key/value storage facility.

Important APIs and functions: `AfsAppLib_RegisterModelessDialog`, `AfsAppLib_IsModelessDialogMessage`, `AfsAppLib_SetPumpRoutine`, and `AfsAppLib_MainPump` manage modeless dialog dispatch. `GetWindowDataField`, `GetWindowData`, and `SetWindowData` associate named `UINT_PTR` values with HWNDs. Hook procedures `Modeless_HookProc` and `WindowData_HookProc` remove entries on `WM_DESTROY`.

Control flow: Registered modeless dialogs are stored in `aModeless`; the main pump calls `IsDialogMessage` or property-sheet equivalents before ordinary translate/dispatch. Window data maps field names to numeric indexes and stores per-window arrays grown on demand. Destroy hooks clear modeless/window-data entries and free arrays.

State and persistence: Global dynamic arrays for modeless HWNDs, field names, window data, and two lazily allocated critical sections. No durable persistence.

Dependencies and integration points: Uses `subclass.h`, property sheet helpers, `REALLOC`, and app-wide message pump setup. Animation in `al_misc.cpp` uses window data for current frame.

Risks: `GetWindowData` and `SetWindowData` enter `pcsData` and call `GetWindowDataField`, which also enters the same critical section; Win32 critical sections are reentrant for the owning thread, but this subtle dependency matters. Brush/object cleanup is not relevant here, but global arrays never shrink. Using text field names has typo/collision risk.

Test signals: Register/destroy modeless dialogs, property sheet page closure, custom pump routine execution, multiple fields per window, overwriting/clearing values, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_pump.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_resource.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_resource.h

Purpose: Defines numeric resource, dialog, control, bitmap, icon, and string identifiers for the app library's Win32 resources.

Important APIs and definitions: String IDs cover credential and browse/error messages. Control IDs include open-cell, credentials, bad-credentials, browse, cover, and error controls. Dialog IDs include `IDD_APPLIB_OPENCELL`, `IDD_APPLIB_CREDENTIALS`, `IDD_APPLIB_ERROR`, `IDD_APPLIB_BADCREDS`, `IDD_APPLIB_COVER`, and browse dialogs. Icon/bitmap IDs cover AFS object icons and spinner frames.

Control flow: Header-only constants; used by resource scripts and C++ code for dialog/control lookup and localized string loading.

State and persistence: None, but numeric stability is part of the binary/resource contract.

Dependencies and integration points: Shared by implementation files, language resource `.rc` files, and Visual Studio resource tooling (`APSTUDIO_INVOKED` block).

Risks: Duplicate numeric IDs exist for `IDC_COVER_BORDER` and `IDC_BROWSE_TYPE` by design or accident; code must only use them in disjoint dialogs. Changing values can break existing resource scripts or compiled dialogs.

Test signals: Resource compiler checks, dialog smoke tests for every ID looked up by code, and icon/image-list load tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_task.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_task.cpp

Purpose: Implements a simple background task queue with bounded worker thread fan-out and `WM_ENDTASK` completion messages.

Important APIs and functions: `AfsAppLib_InitTaskQueue` installs caller-provided `TASKQUEUE_PARAMS`. `StartTask` enqueues task ID/reply HWND/user data and starts threads up to `nThreadsMax`. `Task_ThreadProc` pops work, creates/performs/frees task packets through callbacks, and posts results.

Control flow: First `StartTask` initializes the critical section. Each task increments active count, may spawn a below-normal-priority worker, then appends to a singly linked FIFO. Worker threads loop: decrement active count from prior work, pop one item, exit if none, call create/perform callbacks, then post `WM_ENDTASK` to the reply window or free the packet directly if no valid window remains.

State and persistence: Global `ptqp`, FIFO head/tail, critical section, `nThreadsRunning`, and `nRequestsActive`. No persistent storage.

Dependencies and integration points: Depends on task callback types from `afsapplib.h`, Win32 threads, and `WM_ENDTASK` from `al_messages.h`. UI receivers must free task packets after processing `WM_ENDTASK`.

Risks: Thread handles are not closed. `AfsAppLib_InitTaskQueue` can replace params while workers still use `ptqp`. No shutdown drain. Active count/thread count logic is compact and sensitive to races if init/reinit occurs concurrently. Posting a packet to a window transfers ownership by convention only.

Test signals: Single and multiple tasks, max-thread limits, reply window destroyed before completion, callback packet creation failure, task queue reinitialization, and receiver packet-free handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_task.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.cpp

Purpose: Implements a reusable wizard framework with a template dialog, switchable right-hand state panes, optional left graphic rendering, and optional full-screen/background wash window.

Important APIs and functions: Public methods configure template/control IDs, graphics, state table, graphic callback, current state, background, buttons, and default control. Internal logic includes `Refresh`, `GetRightHandWindow`, `GeneratePalette`, `FindState`, `SendStateCommand`, template/background dialog procedures, left-pane paint hook, and background paint helpers.

Control flow: `Show(TRUE)` creates the template modeless dialog and enters a message loop until the wizard closes. `SetState` sends leave/enter commands and skips disabled states unless forced. `Refresh(REFRESH_RIGHT_PANE)` creates the state's modeless child dialog, sizes it over the right-pane placeholder, hides the placeholder, and destroys the old pane. Left-pane painting selects the 256-color bitmap when display depth allows, otherwise the 16-color bitmap, centers/crops/fills, optionally double-buffers, and invokes a custom draw callback. Background windows render a blue wash bitmap and route cancellation back to the wizard/current state.

State and persistence: Object fields own HWNDs, bitmaps, palette, current state, state array pointer, background text/font/buffer, and callback pointers. No durable persistence.

Dependencies and integration points: Uses `TaLocale_LoadImage`, `GetString`, subclass hooks, Win32 GDI, dialogs, and property/window APIs. State pane dialog procs receive `IDC_WIZARD` command notifications for `wcSTATE_ENTER`, `wcSTATE_LEAVE`, and `wcIS_STATE_DISABLED`.

Risks: The wizard owns GDI objects and window lifetime; misuse can double-destroy or leave callers with invalid pane HWNDs. `SetStates` stores a raw pointer, so caller must keep the array alive. The modal loop inside `Show` can conflict with outer pumps. Palette/bitmap handling targets legacy 8-bit displays and uses many GDI objects. Disabled-state skipping briefly sends enter/leave to candidate states.

Test signals: Show/hide lifecycle, state transitions forward/back/disabled/forced, pane replacement, left graphic with 16/256 assets, custom graphic callback, background resize/paint/close, button enable/text/default control, and GDI leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.h

Purpose: Declares the exported `WIZARD` class, state descriptors, command enum, and button flag constants for the wizard framework.

Important APIs and types: `WIZARD_COMMAND` includes `wcSTATE_ENTER`, `wcSTATE_LEAVE`, and `wcIS_STATE_DISABLED`. `WIZARD_STATE` maps a numeric state to a dialog template, dialog proc, and init lparam. The class exposes configuration, state navigation, show/background, button, and state-command methods.

Control flow: Header-only declarations; runtime behavior is implemented in `al_wizard.cpp`. Dialog procs integrate through `WM_COMMAND` with `LOWORD == IDC_WIZARD` and `HIWORD` set to a `WIZARD_COMMAND`.

State and persistence: The class stores template IDs, bitmap handles, palette, raw state array pointer/count, current state, foreground/background HWNDs, background rendering state, and callback pointer. No persistence.

Dependencies and integration points: Includes Win32, property sheet, `TaLocale`, and subclass headers. Consumers must provide dialog templates containing left/right pane placeholders and navigation controls.

Risks: Raw pointers and GDI/HWND ownership are exposed through the class lifecycle. Copying a `WIZARD` object would be unsafe because no copy control is declared. Header uses `cchRESOURCE` without defining it locally, relying on included headers.

Test signals: Compile client code, verify expected resource IDs/control IDs, state dialog command handling, and object destruction with active/inactive windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.cpp

Purpose: Implements `OpenAFS_CheckList`, an owner-drawn listbox-derived control with a checkbox glyph per item and click/double-click toggling.

Important APIs and functions: `RegisterCheckListClass` clones base `LISTBOX` class metadata and registers `WC_CHECKLIST`; `IsCheckList` validates HWND class. `CheckListProc` handles mouse, enable, create/destroy, and custom `LB_GETCHECK`/`LB_SETCHECK`. Parent hook `CheckList_DialogProc` handles measure/draw/color messages. Draw helpers render checkbox frame/checkmark and text. Input helpers manage hit-test state and multi-select toggling.

Control flow: On create, the control hooks its parent and initializes an internal hit item in `GWLP_USERDATA`. Mouse down over a checkbox captures the mouse and records hit item; mouse up toggles selected items if released over the checkbox; double-click toggles current item. Item checked state is stored in listbox item data.

State and persistence: Global `procListbox` stores original class proc. Per-control hit state is `GWLP_USERDATA`; per-item check state is `LB_SETITEMDATA`. Static selection buffer in `CheckList_OnSetCheck_Selected` is reused. No persistence.

Dependencies and integration points: Requires Win32 listbox owner-draw messages, `TaLocale`, `subclass.h`, and public macros in `checklist.h`. Parent receives `LBN_CLICKED` after toggles.

Risks: Parent hook removal on one checklist destroy can affect siblings because it removes the same hook from the parent. `WM_CTLCOLORLISTBOX` creates brushes without deleting old ones when color changes. Text buffer is fixed at 256 characters. Storing original proc in `LONG` is pointer-width risky on 64-bit.

Test signals: Single and multi-select toggle behavior, disabled rendering, keyboard/listbox behavior pass-through, multiple checklist controls in one dialog, long text drawing, owner-draw measure, and 64-bit build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.h

Purpose: Declares the checklist control registration function, class name, custom messages, notification alias, and helper macros.

Important APIs and definitions: `RegisterCheckListClass`, `WC_CHECKLIST`, `LB_GETCHECK`, `LB_SETCHECK`, `LBN_CLICKED`, `LB_GetCheck`, and `LB_SetCheck`.

Control flow: Header-only macro dispatch sends custom messages to checklist HWNDs. Runtime handling is in `checklist.cpp`.

State and persistence: None in the header. Checked state is implemented as listbox item data by the source file.

Dependencies and integration points: Consumers create controls with class `OpenAFS_CheckList`, call `RegisterCheckListClass`, and use standard listbox APIs plus these macros.

Risks: Custom `WM_USER+300/301` messages assume no conflict with other subclassed listbox behavior. `LBN_CLICKED` is aliased to `BN_CLICKED`, which works numerically but may confuse readers/tools.

Test signals: Compile inclusion in C++ UI modules, class registration before dialog creation, get/set macros, and parent notification handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.cpp

Purpose: Implements a locale-aware composite Date control that expands into year/month/day edit fields, separators, and a spinner.

Important APIs and functions: `RegisterDateClass` registers class `Date`. `DateProc` handles lifecycle, focus, enable, key forwarding, and `DM_GETDATE`/`DM_SETDATE`. `Date_OnCreate` builds child edits in locale order from `LOCALE_IDATE`/`LOCALE_SDATE`. `DateDlgProc` handles edit colors and spinner updates. `DateEditProc`, `Date_Edit_OnSetFocus`, `Date_Edit_OnUpdate`, and `Date_Edit_SetText` synchronize fields with `SYSTEMTIME`.

Control flow: The placeholder Date window creates child edit/static controls in the parent dialog, subclasses edits, creates/reuses a spinner attached to the focused field, and forwards focus/clicks/arrow keys to the relevant child. Updates parse the edit text, mutate `dateNow`, and send `DN_UPDATE` to the parent through `WM_COMMAND`.

State and persistence: Global dynamic `aDate` table, guarded by `csDate`, maps Date HWNDs to child controls and current `SYSTEMTIME`. No durable persistence.

Dependencies and integration points: Uses `ctl_spinner`, `dialog.h` for `NextControlID`, `resize.h`, `subclass.h`, locale APIs, and public messages/macros in `ctl_date.h`.

Risks: `dateNow` is zero-initialized until caller sets a date, so initial spinner positions can be invalid. Day range is always 1-31 and does not validate month/year combinations. Parent color handler creates brushes without stable cleanup. `atoi/atol` use ANSI-oriented parsing under TCHAR builds.

Test signals: Locale formats M/D/Y, D/M/Y, Y/M/D; get/set date; focus changes update spinner range; arrow/page/home/end keys; disabled visual state; invalid dates such as February 31; parent receives `DN_UPDATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.h

Purpose: Declares the Date custom control registration function, messages, notifications, and get/set helper macros.

Important APIs and definitions: `RegisterDateClass`, `DM_GETDATE`, `DM_SETDATE`, `DN_CHANGE`, `DN_UPDATE`, `DA_GetDate`, and `DA_SetDate`. Also defines common helper macros `limit`, `inlimit`, `cxRECT`, and `cyRECT` if absent.

Control flow: Header-only message macros send `SYSTEMTIME*` payloads to the Date control; parent notifications are sent as `WM_COMMAND` from implementation.

State and persistence: None in the header. Runtime state is process-local in `ctl_date.cpp`.

Dependencies and integration points: Consumers must create a window of registered class `Date` and pass `SYSTEMTIME` pointers with the macros.

Risks: `DN_CHANGE` is declared but the implementation observed only sends `DN_UPDATE`, so consumers expecting change notifications may not see them. Custom messages use `WM_USER+313/314`, requiring no collision in the control.

Test signals: Compile consumers, verify macro pointer use, and test notification expectations against implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.cpp

Purpose: Implements a composite elapsed-time control with hours, minutes, seconds fields and a spinner that enforces min/max elapsed ranges.

Important APIs and functions: `RegisterElapsedClass` registers class `Elapsed`. `ElapsedProc` handles lifecycle, focus, enable, key forwarding, and `ELM_*` messages. `Elapsed_OnCreate` builds child edits/separators and initializes default range 0 to 24 hours. Range/time handlers get/set `SYSTEMTIME`. Edit helpers compute spinner ranges, update elapsed fields, enforce limits, and set formatted text.

Control flow: The placeholder control creates child edit/static controls in the parent, subclasses edits, and creates a spinner attached to the focused field. The hour spinner encodes days as `wDay * 24 + wHour`; minute/second spinners narrow their ranges when the current hour/minute is at the min or max boundary. Updates clamp values and notify the parent with `ELN_UPDATE`.

State and persistence: Global `aElapsed` table guarded by `csElapsed` stores HWNDs, range, current time, spinner handles, and callback suppression flags. No durable persistence.

Dependencies and integration points: Uses `ctl_spinner`, `dialog.h`, `resize.h`, `subclass.h`, locale time separator, and public macros in `ctl_elapsed.h`.

Risks: `fCanCallBack` is a `BOOL` but is incremented/decremented as a counter, which works only by convention. Parent color handler creates brushes without cleanup. Initial `timeNow` is zero and clamping depends on range setup. `ELN_CHANGE` is declared but implementation sends `ELN_UPDATE` on spinner/update flow.

Test signals: Default and custom min/max ranges, hour values over 24 via `wDay`, boundary minute/second clamping, focus/spinner migration, arrow/page key handling, disabled rendering, get/set time, and notification suppression during programmatic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.h

Purpose: Declares the elapsed-time custom control interface and helper macros for converting between `SYSTEMTIME` fields and seconds.

Important APIs and definitions: `RegisterElapsedClass`, constants `csec1SECOND` through `csec1WEEK`, `SET_ELAPSED_TIME`, `SET_ELAPSED_TIME_FROM_SECONDS`, `GET_SECONDS_FROM_ELAPSED_TIME`, messages `ELM_GETRANGE`, `ELM_SETRANGE`, `ELM_GETTIME`, `ELM_SETTIME`, notifications `ELN_CHANGE`/`ELN_UPDATE`, and `EL_*` macros.

Control flow: Header macros send `SYSTEMTIME*` payloads to controls. Conversion macros mutate their arguments directly and are intended for elapsed durations, not calendar times.

State and persistence: None in the header.

Dependencies and integration points: Consumers must use `SYSTEMTIME` as a duration structure, with `wDay` representing elapsed days and `wHour` the remainder. Used by the implementation and any dialogs embedding elapsed controls.

Risks: `SET_ELAPSED_TIME_FROM_SECONDS` mutates the `_s` argument, so callers passing expressions or reused variables can be surprised. Macros are multi-statement without `do { } while (0)`, making them unsafe in single-line conditional contexts.

Test signals: Conversion macro round trips, range/get/set message macros, and compile checks in conditional statements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_elapsed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.cpp

Purpose: Implements a composite IPv4 socket-address entry control made of four numeric edit fields separated by dots.

Important APIs and functions: `RegisterSockAddrClass` registers class `SockAddr`. `SockAddrProc` handles lifecycle, focus, enable, click forwarding, and `SAM_GETADDR`/`SAM_SETADDR`. `SockAddr_OnCreate` builds child fields. `SockAddrDlgProc` routes edit notifications. `SockAddrEditProc` handles dot key focus advance and kill-focus formatting. Edit helpers synchronize `SOCKADDR_IN`.

Control flow: On creation the placeholder creates four child edit controls and static separators in the parent dialog, subclasses each edit, and initializes address to zero. `EN_CHANGE` clamps octets, updates `sin_addr` byte fields, sends `SAN_CHANGE` with a mutable copy, and applies any parent-modified address. `EN_UPDATE` sends `SAN_UPDATE`.

State and persistence: Global `aSockAddr` table guarded by `csSockAddr` maps placeholder HWNDs to child HWNDs and current `SOCKADDR_IN`. No persistence.

Dependencies and integration points: Uses Winsock2 `SOCKADDR_IN`, `dialog.h`, `resize.h`, `subclass.h`, locale helpers, and public macros in `ctl_sockaddr.h`.

Risks: Uses legacy `sin_addr.s_net/s_host/s_lh/s_impno` byte fields, which are non-portable and depend on Windows layout. First octet is clamped 1-253 after entry begins, while all-zero is used as the blank sentinel. Parent color handler creates brushes without cleanup. No port/family validation is performed.

Test signals: Blank address, setting/getting addresses, first-octet min/max, other octet 0-255 limits, dot key navigation, parent modification in `SAN_CHANGE`, kill-focus formatting, disabled state, and byte-order expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.h

Purpose: Declares the socket-address custom control interface.

Important APIs and definitions: `RegisterSockAddrClass`, messages `SAM_GETADDR` and `SAM_SETADDR`, notifications `SAN_CHANGE` and `SAN_UPDATE`, plus `SA_GetAddr` and `SA_SetAddr` macros. It also conditionally defines common geometry/limit macros.

Control flow: Header macros send `SOCKADDR_IN*` payloads to the control. Notifications return through parent `WM_COMMAND` with `LPARAM` pointing to a `SOCKADDR_IN`.

State and persistence: None in the header; runtime state is held by `ctl_sockaddr.cpp`.

Dependencies and integration points: Consumers must include Winsock-compatible definitions before using `SOCKADDR_IN` payloads, and create a registered `SockAddr` class control.

Risks: Notification comment for `SAN_CHANGE` says `SOCKADDR_IN *pTime`, a copy-paste typo that can mislead maintainers. Custom messages may collide if sent to the wrong window class.

Test signals: Compile with Winsock headers, get/set macros, parent notification payload handling, and class registration before dialog creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.cpp -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.cpp

Purpose: Implements a reusable spinner/up-down scrollbar class that attaches to a buddy edit/listbox/combobox and synchronizes numeric or selected-index state.

Important APIs and functions: `RegisterSpinnerClass`, `CreateSpinner`, `fHasSpinner`, `SpinnerProc`, `SpinnerDialogProc`, `SpinnerBuddyProc`, `SpinnerSendCallback`, and handlers for all `SPM_*` messages. `Spinner_GetNewText` parses buddy content/selection; `Spinner_SetNewText` writes clamped text/selection and emits notifications.

Control flow: `CreateSpinner` allocates a `SpinnerInfo`, creates a vertical scrollbar-derived `Spinner` window next to the buddy or at a requested rect, and shows/enables it. Creation hooks the parent and buddy. Parent `WM_VSCROLL` increments/decrements position, allows `SPN_CHANGE_UP/DOWN` overrides, clamps to range, writes buddy text, and sends `SPN_UPDATE`. Buddy messages route keyboard arrows/page/home/end to the spinner, mark text dirty, reattach on move/size, and answer `SPM_*` messages.

State and persistence: Global `aSpinners` table guarded by `csSpinners` stores spinner HWND, buddy HWND, requested rect, min/max/base/signed/pos, callback flags, and optional format string. No persistence.

Dependencies and integration points: Uses Win32 scrollbar class metadata, `subclass.h`, app allocation, and public macros in `ctl_spinner.h`. Date and elapsed controls depend on it heavily.

Risks: Original scrollbar proc and class proc are stored in `LONG`, risky on 64-bit. The code enters `csSpinners` then calls `Spinner_FindSpinnerInfo`, which re-enters the same critical section. Signed numeric limits are represented in `DWORD` and cast to `signed long`. Buddy text parsing resets base to 10 for edits before detecting prefixes; custom format suppresses automatic base prefix behavior. Thread-safety is limited to table lookup/mutation, not all HWND lifetimes.

Test signals: Edit/listbox/combobox buddies; range and position get/set; signed decimal, hex, binary, octal-like input; custom format; keyboard and scrollbar changes; callback override with `SPVAL_UNCHANGED`; buddy move/resize; reattach/set-buddy; destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.h -->
## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.h

Purpose: Declares the spinner custom control API, notification codes, helper macros, and creation functions.

Important APIs and definitions: `RegisterSpinnerClass`, `CreateSpinner`, `fHasSpinner`, messages `SPM_GETRANGE` through `SPM_SETBUDDY`, notifications `SPN_CHANGE_UP`, `SPN_CHANGE_DOWN`, `SPN_CHANGE`, `SPN_UPDATE`, sentinel `SPVAL_UNCHANGED`, and helper macros `SP_GetRange`, `SP_SetRange`, `SP_GetPos`, `SP_SetPos`, `SP_GetBase`, `SP_SetBase`, `SP_GetSpinner`, `SP_SetRect`, `SP_SetFormat`, and `SP_SetBuddy`.

Control flow: All control messages are sent to the buddy control, not the spinner HWND. Notifications return through parent `WM_COMMAND` with `LOWORD` equal to the buddy control ID and `HIWORD` equal to an `SPN_*` code.

State and persistence: None in the header; runtime state is in `ctl_spinner.cpp`.

Dependencies and integration points: Used directly by dialogs and by composite controls such as Date and Elapsed. Consumers must understand that `SP_GetSpinner` returns the generated spinner HWND while most APIs target the buddy.

Risks: `SP_GetPos` returns the `SendMessage` result cast as `DWORD` through macro context, but the underlying handler returns `BOOL`, which is type-confusing even if values fit in `LRESULT`. Multi-argument macros do not enforce pointer types.

Test signals: Compile all helper macros, verify message target convention, callback payload semantics, and interoperation with all supported buddy classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.h -->
