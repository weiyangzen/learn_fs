# subset-b-007739 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.cpp

Purpose: implements the exported Windows Control Panel `CPlApplet` entry point for the OpenAFS client applet. It dynamically chooses applet metadata and icon based on the current OS family and whether the OpenAFS client registry installation key exists.

Important APIs/functions: `IsWindowsNT()` caches `GetVersionEx` platform detection; `IsClientInstalled()` probes `AFSREG_CLT_SW_VERSION_SUBKEY` and `AFSREG_CLT_SW_VERSION_DIR_VALUE`; `CPlApplet()` handles `CPL_INIT`, `CPL_GETCOUNT`, `CPL_INQUIRE`, `CPL_NEWINQUIRE`, `CPL_DBLCLK`, and `CPL_EXIT`.

Control flow: initialization loads the resource satellite through `TaLocale_LoadCorrespondingModule` and initializes COM as apartment-threaded. Inquiry messages fill `CPLINFO` or `NEWCPLINFO` with localized strings and icons. Double-click launches `afs_config.exe`, passing `/c` when Windows NT lacks an installed client, which routes users to client configuration rather than normal client control.

State/persistence: module handles and detection booleans are static process state. Persistent data is read only from HKLM OpenAFS registry keys.

Dependencies/integration: depends on Win32 Control Panel, ShellExecute, COM initialization, `TaLocale`, and OpenAFS registry constants. It integrates with `afs_config.exe` rather than embedding configuration UI.

Risks: `GetVersionEx` and cached registry detection can become stale for long-lived Control Panel sessions. `ShellExecuteEx` return value is ignored. The applet assumes `afs_config.exe` is discoverable in the shell search path.

Test signals: verify CPL load/unload calls balance COM/resource unloading, registry-present and registry-absent labels/icons, Windows 9x versus NT behavior, and double-click command parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.h -->
# sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.h

Purpose: declares the single exported Control Panel entry point `CPlApplet` with C linkage for the OpenAFS client applet.

Important APIs/types: wraps `LONG APIENTRY CPlApplet(HWND hwndCPl, UINT uMsg, LONG lParam1, LONG lParam2)` in `extern "C"` when compiled as C++ so the symbol name matches the Control Panel loader contract.

Control flow: no runtime flow is implemented here; it provides the ABI boundary consumed by `cpl_interface.cpp` and Windows `control.exe`.

State/persistence: none.

Dependencies/integration: assumes Windows header types and calling conventions are visible before or through the includer. It is the integration contract between the CPL module and the shell/control panel host.

Risks: because this header contains no include guard, repeated inclusion would redeclare the same prototype but not generally break C/C++ compilation. ABI correctness depends on retaining `APIENTRY` and C linkage.

Test signals: build/link checks should confirm the exported name is available to the `.cpl`; runtime smoke tests should load the applet from Control Panel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_cpa/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/client_cpa/resource.h

Purpose: defines resource identifiers used by the OpenAFS Control Panel applet.

Important identifiers: string IDs `IDS_CPL_NAME_NT`, `IDS_CPL_DESC_NT`, `IDS_CPL_NAME_95`, `IDS_CPL_DESC_95`, `IDS_CPL_NAME_CCENTER`, and `IDS_CPL_DESC_CCENTER` supply localized applet name/description variants. Icon IDs `IDI_AFSD` and `IDI_CCENTER` select the normal AFS client icon or configuration-center icon.

Control flow: no executable code. The IDs are consumed by `cpl_interface.cpp` through `GetString` and `TaLocale_LoadIcon`.

State/persistence: none.

Dependencies/integration: synchronized with applet `.rc` resources and localized satellite resources. The numeric values are part of the resource ABI for the applet binary.

Risks: mismatched IDs between this header and resource scripts can produce wrong labels or missing icons. String IDs start at zero, so lookup helpers must correctly support zero-valued resource IDs.

Test signals: resource compilation, localized resource load tests, and manual CPL inspection for each client-installed/NT branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_cpa/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/Makefile -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/Makefile

Purpose: legacy Windows makefile for building `afscreds.exe`, the OpenAFS credentials/tray utility.

Important build inputs: object list includes UI tabs, wizard, drive-map, credential, tray, window, checklist, and support modules. Libraries include Win32 UI/COM/network libraries plus `libafstokens.lib` and `libafsconf.lib` from `$(AFSCLIENTROOT)\obj\afsd`.

Control flow: default `all` links `$(TARGET)` from `$(OBJS)`; pattern rules compile `.cpp` and `.rc` files; `clean` deletes local build artifacts.

State/persistence: no runtime persistence, but build configuration hardcodes `AFSCLIENTROOT = q:\afs\client`, debug flags (`-Zi -Od -DDEBUG -D_DEBUG -DDBG`), C++ exception support (`-GX`), and `STRICT`.

Dependencies/integration: relies on Microsoft `win32.mak`, `MSTOOLS`, resource compiler variables, and OpenAFS client library outputs. Links GUI subsystem flags through `guilflags`.

Risks: hardcoded root and debug-only flags make this unsuitable for modern reproducible builds without adaptation. `wsock32.lib` and older toolchain assumptions indicate pre-Visual Studio project age.

Test signals: clean build with expected `AFSCLIENTROOT`, link resolution for token/config libraries, and resource inclusion in `afscreds.res`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.cpp

Purpose: implements the Advanced tab in `afscreds.exe`, exposing AFS service status/start/stop/autostart controls, Control Panel launch, and tray startup preference.

Important APIs/functions: `Advanced_DlgProc` dispatches dialog events; `Advanced_OnServiceTimer` queries `TransarcAFSDaemon` status/config and updates UI; `Advanced_OnChangeService` changes service start type or starts/stops the service; `Advanced_OnOpenCPL` launches `afs_config.exe`; `Advanced_OnStartup` persists tray startup configuration and shortcut state.

Control flow: initialization sets the startup checkbox and begins a service polling timer. Service operations open SCM/service handles with required access, perform `ChangeServiceConfig`, `StartService`, or `ControlService`, then restart polling and refresh tabs when transitions settle. On start, drive mappings are attempted and KFW token renewal may run.

State/persistence: reads service state and start type from SCM; writes `ShowTrayIcon` under the client service parameter registry key and updates the Startup shortcut through `Shortcut_FixStartup`.

Dependencies/integration: integrates with `Main_RepopulateTabs`, drive mapping functions (`TestAndDoMapShare`, `TestAndDoUnMapShare`), KFW renewal, `TaLocale`, and the Windows SCM.

Risks: service-handle cleanup is uneven in the stop path; error capture can be generic if SCM calls fail before `GetLastError`. Repeated `TestAndDoMapShare` calls happen in polling and status refresh. Requires administrative rights for service configuration.

Test signals: service missing/stopped/running/pending UI states, start/stop failures, auto-start registry updates, mapping renewal on service start, and behavior under non-admin users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.h

Purpose: declares the Advanced tab dialog procedure for the credentials UI.

Important APIs/types: `BOOL CALLBACK Advanced_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)` is the exported module-level handler used when `window.cpp` creates the `IDD_TAB_ADVANCED` modeless dialog.

Control flow: no implementation; routing is from `Main_CreateTabDialog` to this callback.

State/persistence: none in the header. Runtime state lives in `advtab.cpp` and shared `GLOBALS g`.

Dependencies/integration: included by `afscreds.h`, making the dialog procedure available throughout the client credentials app.

Risks: ABI depends on Win32 callback signature. Since the Advanced tab is conditionally compiled out of UAC-compatible builds in `window.cpp`, references must stay consistent.

Test signals: compilation and tab creation when the advanced tab is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/afscreds.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/afscreds.h

Purpose: central shared header for `afscreds.exe`; it collects Windows/OpenAFS includes, resource IDs, shared constants, global data structures, macros, and cross-module prototypes.

Important types: `CREDS` stores cell, user, expiration time, and reminder flag. `GLOBALS` stores the main window, dynamic credential array, retest timestamp, message-display count, wizard pointer, startup/OS flags, two OSI mutexes, and SMB share name.

Control flow: no direct flow, but it defines timing constants for reminder, renewal, service polling, and mouse-over retests. The `REALLOC` macro routes dynamic array growth through `AfsCredsReallocFunction`.

State/persistence: declares external `GLOBALS g`, which is the primary in-process state shared by main window, tabs, tray icon, token operations, and wizard code. Registry value names and shortcut options document persistent configuration surfaces.

Dependencies/integration: pulls in `TaLocale`, Win32 common controls, registry constants, OSI locks, RXKAD, wizard/dialog helpers, all local tab headers, drive mapping, and help IDs.

Risks: very broad include surface couples most modules to Windows, OpenAFS, and UI details. Global mutable state demands correct locking around `g.aCreds` and expiration checks. Macro redefinition of `REALLOC` can collide with other headers.

Test signals: full application build, thread-safety tests around `g.credsLock`, and registry setting compatibility across 32/64-bit registry views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/afscreds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.cpp

Purpose: implements the startup wizard shown when the AFS client service is configured but not running. It guides service start, optional credential acquisition, optional drive mapping, and completion.

Important APIs/functions: `ShowStartupWizard`; state dialog procedures `WizStart_DlgProc`, `WizStarting_DlgProc`, `WizCreds_DlgProc`, `WizMount_DlgProc`, `WizMounting_DlgProc`, `WizFinish_DlgProc`; helpers for enabling credential/map forms, service polling, and threaded mapping activation.

Control flow: `ShowStartupWizard` creates a `WIZARD`, sets state descriptors, shows it modally, refreshes tabs, and frees drive map state. The wizard starts the service, polls until running, optionally calls `ObtainNewCredentials`, optionally writes a drive mapping, and launches a background thread that activates inactive mappings before finishing.

State/persistence: file-static `l` holds a `DRIVEMAPLIST`, current wizard dialog, help ID, and requested submount. Persistent effects include service start, token creation, drive mapping writes, and submount creation through drive-map helpers.

Dependencies/integration: depends on OpenAFS `fs_utils` mount-root constants, `drivemap` APIs, `creds` token APIs, Windows SCM, and the application wizard framework (`al_wizard`).

Risks: background mapping thread shares file-static state without explicit locking. Service start failure leaves UI in failure state but may not expose detailed errors. The wizard auto-skips mapping choice when any mapping already exists.

Test signals: service stopped/start-pending/running transitions, credential success/failure, drive-letter selection, invalid submount validation, mapping activation failures, and repeated attempts while `g.pWizard` is already set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.h

Purpose: declares the startup wizard entry point.

Important APIs/types: `void ShowStartupWizard(void)` is called from main application startup and tray activation paths when the service needs interactive startup/configuration help.

Control flow: no implementation. It is the public boundary to the multi-page wizard in `afswiz.cpp`.

State/persistence: none in header; wizard state is in `g.pWizard` and a file-static state block in the implementation.

Dependencies/integration: included through `afscreds.h`; consumers do not need to know wizard state IDs or dialog procedures.

Risks: single function hides substantial side effects including service start and drive mapping writes, so callers must only invoke it from UI-safe contexts.

Test signals: build references from `main.cpp` and `window.cpp`, and UI smoke test for startup wizard display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/creds.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/creds.cpp

Purpose: provides token-library loading, AFS service status helpers, current token enumeration, token destruction, token acquisition, and default-cell lookup for `afscreds.exe`.

Important APIs/functions: `Creds_OpenLibraries` dynamically loads `afsauthent.dll` and `libafsconf.dll`; `IsServiceRunning`, `IsServicePersistent`, `IsServiceConfigured`; `GetCurrentCredentials`; `DestroyCurrentCredentials`; `ObtainNewCredentials`; `GetDefaultCell`; `GetGatewayName`.

Control flow: token operations lazily load libraries and initialize RX/KA paths. `GetCurrentCredentials` clears `g.aCreds`, lists tokens via `ktc_ListTokens`, resolves each token via `ktc_GetToken`, converts cell/user/expiration into `CREDS`, restores reminder flags, and updates the tray icon. `ObtainNewCredentials` prefers KFW when available, otherwise parses login names and calls KA authentication.

State/persistence: mutates `g.aCreds`, `g.cCreds`, and `g.tickLastRetest` under `g.credsLock`. Reads service and cell registry keys. Reminder persistence is delegated to `LoadRemind`.

Dependencies/integration: integrates dynamic OpenAFS token/config DLLs, KFW, Windows SCM, registry constants, tray icon refresh, and dialog error reporting.

Risks: dynamic function pointer set must be complete or all token operations fail. Passwords are copied into fixed-size stack buffers and not scrubbed. `GetCurrentCredentials` updates UI/tray after releasing the lock but still depends on shared state. Service status branches differ between NT and gateway-mode non-NT.

Test signals: missing DLLs, stopped service, multiple-cell token enumeration, expired tokens, KFW and non-KFW authentication, root-cell registry override, and token destruction error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/creds.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/creds.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/creds.h

Purpose: declares credential and service helper APIs used by the credentials UI, wizard, tray, and network-change code.

Important APIs: service helpers (`IsServiceRunning`, `IsServicePersistent`, `IsServiceConfigured`), token lifecycle (`GetCurrentCredentials`, `DestroyCurrentCredentials`, `ObtainNewCredentials`), cell/gateway lookup (`GetDefaultCell`, `GetGatewayName`), and dynamic library lifecycle (`Creds_OpenLibraries`, `Creds_CloseLibraries`).

Control flow: no implementation. It defines the public credential-management surface for `creds.cpp`.

State/persistence: callers should assume these functions may read registry/service state and mutate global credential state.

Dependencies/integration: C linkage guard allows inclusion from C or C++ modules; signatures use Win32 string types.

Risks: API side effects are not visible from prototypes. `ObtainNewCredentials` accepts raw password text and a `Silent` flag, so callers must manage UI/error policy and sensitive data lifetime.

Test signals: link coverage for both C and C++ users, and callers correctly handling nonzero OpenAFS/Kerberos error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/creds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.cpp

Purpose: implements credentials tab UI and the obtain-credentials modal dialog.

Important APIs/functions: `Creds_DlgProc`, `Creds_OnUpdate`, `Creds_OnCheckRemind`, `Creds_OnClickObtain`, `Creds_OnClickDestroy`, `ShowObtainCreds`, `NewCreds_DlgProc`, `NewCreds_OnInitDialog`, `NewCreds_OnEnable`, `NewCreds_OnOK`, and `NewCreds_OnCancel`.

Control flow: the tab receives a cell name in `DWLP_USER`, displays service/credential status, enables obtain/destroy/reminder controls, and updates reminder persistence. Obtain runs a new thread that opens a modal credential dialog. The dialog defaults the cell from the tab or root cell, pre-fills the known username, enables OK when credentials are plausible, calls `ObtainNewCredentials`, and refreshes tabs on success.

State/persistence: reads and writes `g.aCreds[i].fRemind` under `g.credsLock`, persists reminders through `SaveRemind`, uses `g.fShowingMessage` to suppress overlapping credential prompts, and mutates token state via credential APIs.

Dependencies/integration: depends on `creds.cpp`, `window.cpp` tab refresh, `TaLocale` formatting, OSI locking, and Win32 dialog controls.

Risks: `ShowObtainCreds` uses `strdup` on an `LPTSTR`, which is unsafe for Unicode builds. Dialog ownership/threading is unusual because modal dialogs are launched on a created thread. UI reads `g.aCreds[i]` after releasing the lock for checkbox state.

Test signals: no-credential tab, per-cell credential tab, reminder toggle persistence, obtain success/failure, destroy token, expired-prompt dialog, Unicode build behavior, and concurrent prompt suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.h

Purpose: declares credentials tab and obtain-credentials dialog entry points.

Important APIs: `ShowObtainCreds(BOOL fExpiring, LPTSTR pszCell)` launches the token acquisition UI, and `Creds_DlgProc` handles credentials tab dialog messages.

Control flow: no implementation; consumers call `ShowObtainCreds` from reminder, network-change, and user-click flows.

State/persistence: none directly, but both declared functions can interact with global credential state and reminder persistence.

Dependencies/integration: included by `afscreds.h`; relies on Win32 dialog types.

Risks: exported interface exposes mutable string pointer semantics without documenting ownership. `ShowObtainCreds` may spawn a thread and display modal UI.

Test signals: compile/link references from `window.cpp`, `ipaddrchg.c`, and `credstab.cpp` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.c -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.c

Purpose: monitors IP address changes and prompts for AFS tokens when network connectivity appears and valid tokens are missing or expired.

Important APIs/functions: `ObtainTokensFromUserIfNeeded`, `GetNumOfIpAddrs`, `IpAddrChangeMonitor`, `IpAddrChangeMonitorInit`, plus local service/token/time helpers. Optional `USE_FSPROBE` code sketches fileserver probing but is not active by default.

Control flow: `IpAddrChangeMonitorInit` spawns a monitor thread. The thread blocks on `NotifyAddrChange`, compares valid IP address counts before/after, waits briefly, then calls `ObtainTokensFromUserIfNeeded`. That helper checks the AFS service, asks the UI to start it if needed, resolves root-cell config, checks current token expiry, probes KDC reachability, attempts KFW renewal, and posts `WM_OBTAIN_TOKENS` if user input is still needed.

State/persistence: no persistent writes. Uses process messages (`WM_START_SERVICE`, `WM_OBTAIN_TOKENS`) and current token cache. Allocates root cell with `GlobalAlloc` and transfers ownership to the window message receiver on prompt.

Dependencies/integration: depends on IP Helper API, KFW, OpenAFS token/config APIs, Windows SCM, `creds.cpp`, and `window.cpp` custom messages.

Risks: monitor thread runs indefinitely with no shutdown path. The root-cell pointer is cast through `long`, unsafe on 64-bit. Token probing may attempt fake authentication in non-KFW mode. Comments note missing mutex protection around prompt decisions.

Test signals: address add/remove events, service stopped path, root cell unavailable, KDC unreachable, expired token renewal, message ownership/freeing, and 64-bit pointer correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.h

Purpose: exposes network-change/token-prompt integration points to C++ credentials modules.

Important APIs/types: defines custom messages `WM_OBTAIN_TOKENS` and `WM_START_SERVICE`; declares `ObtainTokensFromUserIfNeeded(HWND hWnd)` and `IpAddrChangeMonitorInit(HWND hWnd)` with C linkage for C++ callers.

Control flow: callers initialize the monitor or invoke token checks; message handling is implemented by `window.cpp`.

State/persistence: none in the header. Message payload ownership is part of the implicit contract: `WM_OBTAIN_TOKENS` carries allocated cell text to be freed by the receiver.

Dependencies/integration: requires Win32 `HWND`/`DWORD` types and shared `WM_USER` message range coordination.

Risks: message IDs can collide with other app-defined messages if not centrally managed. Pointer payloads must be width-safe and ownership-safe.

Test signals: build integration from `main.cpp` and `window.cpp`, and runtime validation that posted messages produce service start/token UI actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/main.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/main.cpp

Purpose: process entry and application initialization for `afscreds.exe`.

Important APIs/functions: `WinMain`, `InitApp`, `ExitApp`, `PumpMessage`, `Quit`, and `IsServerInstalled`. Command-line switches control auto token init, map renewal, network monitor, show/quiet/exit/install/uninstall, share mapping, unmapping, and map testing.

Control flow: startup initializes shortcuts, locale resources, tracing, and mount root; parses command-line flags; handles install/uninstall shortcut and registry writes; enforces single instance by class-name scan; loads tray startup preference; initializes Winsock/common controls/OSI locks/KFW; optionally starts the AFS service; creates the main modeless dialog; shows setup wizard or token prompts as needed; optionally starts the IP change monitor; then runs the message loop.

State/persistence: initializes global `g`, including startup flag, OS flag, mutexes, main window, and SMB share. Reads/writes `ShowTrayIcon` under HKCU/HKLM OpenAFS keys and manipulates the Startup shortcut.

Dependencies/integration: ties together shortcut, locale, tracing, mount-root, service control, KFW, drive-map, credentials UI, startup wizard, and network-change monitor.

Risks: single-instance detection scans top-level windows by class name and can race. Some command-line paths return before full initialization/cleanup. Service start requires privileges and logs mostly to debugger. Registry precedence logic is important for policy/user overrides.

Test signals: each command-line switch, install/uninstall behavior with existing instance, first-start with service stopped/configured/unconfigured, auto-init token prompt, drive-map renewal, and message loop shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/misc.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/misc.cpp

Purpose: miscellaneous utilities for dynamic allocation, reminder persistence, time conversion, and tab child lookup.

Important APIs/functions: `AfsCredsReallocFunction`, `LoadRemind`, `SaveRemind`, `TimeToSystemTime`, `GetTabParam`, and `GetTabChild`.

Control flow: the realloc helper grows arrays in increments, zeroes new storage, copies old data, and frees old storage. Reminder helpers read/write per-cell DWORD values under `HKCU\...\Reminders`. Tab helpers query common-control item lParams and find the active dialog child under a tab control.

State/persistence: writes `g.aCreds[i].fRemind` to registry and defaults reminders to enabled when no registry value exists. Uses OpenAFS allocation wrappers.

Dependencies/integration: used by credential enumeration, tab repopulation, and dialog update code. Depends on `TaLocale`/dialog allocation helpers through `afscreds.h` and registry view helper `IsWow64`.

Risks: array growth can overflow `cbElement * cNew` on pathological sizes. Reminder value names are raw cell names, so unusual cell-name characters could affect registry behavior. `GetTabChild` assumes dialog class `#32770`.

Test signals: realloc growth/copy/zero behavior, registry reminder default/read/write, time conversion around local timezone/DST, and tab-child lookup after tab changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/misc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.cpp

Purpose: implements the Drive/Mount tab for viewing, adding, editing, removing, activating, and deactivating AFS drive mappings.

Important APIs/functions: `Mount_DlgProc`, `Mount_OnUpdate`, `Mount_OnSelect`, `Mount_OnCheck`, `Mount_OnRemove`, `Mount_AdjustMapping`, `Mount_DriveFromItem`, `Mapping_DlgProc`, `Mapping_OnInitDialog`, `Mapping_OnOK`, and `Mapping_OnEnable`.

Control flow: initialization configures list tabs and populates mappings from `QueryDriveMapList`. Clicking a checked list item activates or inactivates the selected mapping and persists active state. Add/edit opens the mapping dialog, validates drive/path/submount, inactivates old active mappings if needed, activates the new mapping, writes `DRIVEMAPLIST`, and refreshes the list.

State/persistence: file-static `l.iDriveSelectLast` preserves selection. Persistent mapping data is read/written through drive-map APIs; active map state is written by `WriteActiveMap`.

Dependencies/integration: relies on OpenAFS fs utility path constants, drive-map functions, service status, localized messages, and custom checklist/listbox helpers.

Risks: `Mount_DriveFromItem` parses the displayed string rather than storing drive index in item data. Some removal error paths return before freeing `DRIVEMAPLIST`. Mapping validation only checks `/afs` or `\afs` prefix and submount name.

Test signals: no mappings, add/edit/remove, active checkbox toggles, service stopped disabling, unavailable drive letters, invalid paths/submounts, persistent mapping restart behavior, and failed map/unmap status display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.h

Purpose: declares the mount tab dialog procedure.

Important APIs: `BOOL CALLBACK Mount_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)` handles the tab and mapping dialog interactions implemented in `mounttab.cpp`.

Control flow: no implementation; `window.cpp` uses it when creating `IDD_TAB_MOUNT`.

State/persistence: none in the header. The implementation reads/writes drive-map persistence.

Dependencies/integration: included by `afscreds.h` and indirectly by the main window code.

Risks: minimal; correctness depends on preserving the Win32 callback signature.

Test signals: build and runtime creation of the mount tab when `ShowMountTab` registry policy enables it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/resource.h

Purpose: defines string, icon, dialog, bitmap, menu, command, and control resource identifiers for `afscreds.exe`.

Important identifiers: service/status strings (`IDS_SERVICE_*`), error text (`IDS_ERROR_*`), mapping and wizard strings, tray menu commands (`M_TERMINATE`, `M_ACTIVATE`, `M_REMIND`, `M_TERMINATE_NOW`), dialogs (`IDD_MAIN`, tab dialogs, wizard pages, mapping/auth dialogs), icons (`IDI_CREDS_*`), and controls (`IDC_*`).

Control flow: no executable code; IDs drive message dispatch and resource lookup across almost every credentials module.

State/persistence: none.

Dependencies/integration: must match `.rc` files and localized resources. IDs are consumed by `TaLocale`, dialog templates, menu resources, and Windows message handlers.

Risks: duplicate values exist intentionally for different resource classes but can confuse maintenance. Renumbering without updating resources breaks UI dispatch. Some controls share IDs across dialogs, requiring context-aware handlers.

Test signals: resource compilation, all dialogs load, menu commands dispatch correctly, and localized strings/icons resolve for startup/service/token/mapping scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/settings.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/settings.cpp

Purpose: generic registry-backed storage helpers for versioned binary settings and recursive key deletion.

Important APIs/functions: `RestoreSettings`, `StoreSettings`, `EraseSettings`, `GetBinaryRegValue`, `GetRegValueSize`, `SetBinaryRegValue`, and `RegDeltreeKey`.

Control flow: `StoreSettings` prepends a `WORD` version to a structure and writes it as `REG_BINARY`. `RestoreSettings` reads the stored blob, checks that major versions match and stored minor version is at least expected, then copies the expected structure bytes. `RegDeltreeKey` recursively deletes child keys before deleting the requested key.

State/persistence: directly reads/writes/deletes registry values beneath caller-provided roots and subkeys. Uses 64-bit registry view flags when `IsWow64()` indicates they are needed.

Dependencies/integration: uses OpenAFS allocation helpers, Win32 registry APIs, and version macros from `settings.h`.

Risks: `GetBinaryRegValue` calls `RegCloseKey(hk)` instead of `hkFinal`, which can close the caller's root handle and leak the opened subkey. It also does not verify `REG_BINARY`. Recursive delete can fail on permissions or open handles.

Test signals: store/restore across version combinations, invalid/truncated blobs, registry view selection, erase missing value, recursive delete trees, and handle-leak/regression tests around `GetBinaryRegValue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/settings.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/settings.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/settings.h

Purpose: declares registry settings helpers and versioning macros.

Important APIs/macros: root aliases `HKCR`, `HKCU`, `HKLM`; byte/version helpers `HIBYTE`, `LOBYTE`, `MAKEVERSION`; exported functions for erasing, restoring, storing, sizing, reading, writing binary registry values, and recursively deleting keys.

Control flow: no implementation. The header documents the version compatibility rules used by `RestoreSettings`.

State/persistence: all declared functions operate on registry state supplied by callers.

Dependencies/integration: uses Win32 `HKEY`, `LPCTSTR`, `PVOID`, `WORD`, and `BOOL`. `EXPORTED` can be overridden by consumers, suggesting reuse outside this executable.

Risks: macros redefine common names if not already present. Documentation says newer minor versions can be read by older programs when compatible, so structure fields must only be appended for minor version changes.

Test signals: compile with existing Windows macros, version macro values, and consumers preserving append-only minor-version semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/settings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.cpp

Purpose: initializes COM shortcut support, creates `.lnk` files, and maintains the AFS Credentials Startup shortcut.

Important APIs/functions: `Shortcut_Init`, `Shortcut_Exit`, `Shortcut_Create`, and `Shortcut_FixStartup`.

Control flow: initialization calls apartment-threaded `CoInitializeEx`. Shortcut creation instantiates `CLSID_ShellLink`, sets target path, description, optional arguments, and saves through `IPersistFile`. Startup repair locates the common or user Startup folder from Explorer shell-folder registry keys or falls back to the Windows Start Menu path; it then creates or deletes `AFS Credentials.lnk`.

State/persistence: creates/deletes a Startup folder shortcut and reads optional `AfscredsShortcutParams` from HKCU then HKLM OpenAFS keys, defaulting to `-A -M -N -Q`.

Dependencies/integration: uses COM shell interfaces, `shlobj`, registry helpers/constants, current module path, and `afscreds.h` shortcut constants.

Risks: missing braces around `if (pszArgs) rc = psl->SetArguments(pszArgs); if (SUCCEEDED(rc))` make save occur regardless of `pszArgs` only because of indentation-sensitive intent. Shell folder registry paths are legacy. Deleting the shortcut reports failure if the file is already absent.

Test signals: COM initialization balance, shortcut creation with args, Unicode/non-Unicode save path, HKCU/HKLM parameter precedence, missing startup folder fallback, and autostart disable idempotency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.h

Purpose: declares shortcut lifecycle and creation helpers for `afscreds.exe`.

Important APIs: `Shortcut_Init`, `Shortcut_Exit`, `Shortcut_Create`, and `Shortcut_FixStartup`. `Shortcut_Create` has default `NULL` description and argument parameters for C++ callers.

Control flow: no implementation. Main startup/shutdown calls COM lifecycle wrappers, while settings and install paths call `Shortcut_FixStartup`.

State/persistence: declared functions may create or delete filesystem `.lnk` files and read registry settings.

Dependencies/integration: requires C++ default arguments and Win32 string types; used from `main.cpp` and `advtab.cpp`.

Risks: header is C++-oriented despite the broader project using C linkage in places. Callers must ensure COM lifecycle is initialized before shell-link operations if bypassing `Shortcut_FixStartup`.

Test signals: compile references and startup shortcut behavior from install/uninstall and Advanced tab toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.cpp

Purpose: manages the notification-area icon representing AFS credential status.

Important APIs/functions: `ChangeTrayIcon(int nim)` wraps `Shell_NotifyIcon` operations for add, modify, and delete. It chooses `IDI_CREDS_YES` or `IDI_CREDS_NO` based on whether credentials exist and whether any are near expiration.

Control flow: first `NIM_MODIFY` becomes `NIM_ADD`; modify after delete is ignored. For add/modify/delete while the main window is valid, it fills `NOTIFYICONDATA`, calls `Main_FindExpiredCreds`, locks `g.credsLock` while checking `g.cCreds`, sets tooltip text, and calls `Shell_NotifyIcon`.

State/persistence: file-static flags track whether the icon was added or deleted. Reads global credential state; no persistent writes.

Dependencies/integration: depends on `window.cpp` for `WM_TRAYICON` and expiration detection, `TaLocale` for icons/tooltip, and Shell API.

Risks: `Main_FindExpiredCreds` may trigger token-renewal logic from an icon update, making this more than a pure paint/status function. Static icon handles are never destroyed. Delete behavior depends on `g.hMain` validity.

Test signals: initial add, repeated modify, delete on quit, tooltip localization, icon state for valid/expired/no tokens, and Explorer taskbar restart scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.h

Purpose: declares the tray icon update function.

Important APIs: `void ChangeTrayIcon(int nim)` accepts Shell API `NIM_ADD`, `NIM_MODIFY`, or `NIM_DELETE` operations.

Control flow: no implementation. It is called from startup, credential refresh, and shutdown paths.

State/persistence: none in the header; implementation reads global credential state and keeps in-process add/delete flags.

Dependencies/integration: uses Shell notification constants and `WM_TRAYICON` callback integration from `window.h`.

Risks: callers may assume it is a cheap UI update, but implementation can run expiration checks.

Test signals: compile references and shell notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/window.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/window.cpp

Purpose: implements the main hidden/modeless window, tray menu handling, tab management, reminder timer, service-start messages, and termination dialog for `afscreds.exe`.

Important APIs/functions: `Main_DlgProc`, `Main_Show`, `Main_OnInitDialog`, `Main_OnCheckMenuRemind`, `Main_OnRemindTimer`, `Main_OnMouseOver`, `Main_OnSelectTab`, `Main_OnCheckTerminate`, `Main_CreateTabDialog`, `Main_RepopulateTabs`, `Main_EnableRemindTimer`, `Main_FindExpiredCreds`, and termination dialog handlers.

Control flow: the dialog reacts to command/menu/tray/timer/custom messages. Tab repopulation refreshes credentials, builds cell/mount/advanced tab lParams, recreates tab controls, and creates the active child dialog. The reminder timer refreshes tabs, detects expiring credentials, probes reachability, and launches credential acquisition if needed. Tray clicks show the window, wizard, or menu. `WM_START_SERVICE` starts AFSD and renews tokens.

State/persistence: reads version/user and startup policy registry values, updates `g.hMain`, `g.aCreds`, `g.fShowingMessage`, and startup registry/shortcut state in termination flows. Uses mutexes for credential and expiration state.

Dependencies/integration: central hub for `creds`, `credstab`, `advtab`, `mounttab`, `afswiz`, `trayicon`, `shortcut`, `ipaddrchg`, KFW, SCM, and localized resources.

Risks: tab lParams mix pointers and sentinel integer values cast to `LPTSTR`, which is pointer-width fragile. `WM_OBTAIN_TOKENS` casts `LPARAM` to `char *`. Expiration checks perform network/KFW work on UI timer paths. Some service stop code opens the service with `SERVICE_START` access while stopping.

Test signals: tray left/right/mousemove, tab refresh with zero/multiple cells, reminder toggle and expiration prompts, service start custom message, startup policy termination, modal termination options, and 64-bit pointer-sentinel behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/window.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/window.h -->
# sources/distributed-fs/openafs/src/WINNT/client_creds/window.h

Purpose: declares main window APIs and the tray callback message.

Important APIs/constants: `WM_TRAYICON` is defined as `WM_USER+100`; exported functions include `Main_DlgProc`, `Main_RepopulateTabs`, `Main_EnableRemindTimer`, `Main_Show`, and `Main_FindExpiredCreds`.

Control flow: no implementation. Consumers use these helpers to refresh UI, show/hide the main window, manage the reminder timer, and query expiration status.

State/persistence: none in the header. Implementations mutate global window/credential/startup state.

Dependencies/integration: included by `afscreds.h`, `trayicon.cpp`, `main.cpp`, and tab modules. Message value must not collide with other app-defined messages.

Risks: `Main_FindExpiredCreds` sounds like a query but can attempt renewals, so callers should expect side effects.

Test signals: message dispatch to tray handler and successful tab/timer function calls from other modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_creds/window.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.cpp

Purpose: implements the ACL property page shown by the Explorer shell extension for a single AFS directory/file selection.

Important APIs/functions: `CPropACL::PropPageProc`, `FillACLList`, `ShowRights`, `MakeRightsString`, `EnablePermChanges`, `OnSelChange`, `OnRemove`, `IsNameInUse`, and `OnPermChange`.

Control flow: on initialization it stores the page object in window user data, sets resources, disables editing for multi-selection, or calls `GetRights` to load normal and negative ACL arrays. Button handlers add entries via `CAddAclEntryDlg`, copy ACLs via `CCopyAclDlg`, remove selected entries, clean ACLs, or update rights checkboxes. On apply it calls `SaveACL` with the edited arrays.

State/persistence: keeps pending ACL edits in `m_Normal` and `m_Negative` arrays as name/right pairs until property sheet apply. Persistent effects occur through `SaveACL`, `CopyACL`, and `CleanACL`.

Dependencies/integration: integrates MFC property sheets, localized resources, `gui2fs` filesystem operations, ACL helper dialogs, and `CSetACLInterface` for duplicate-name validation.

Risks: list index mapping assumes normal entries precede negative entries and arrays are exact name/right pairs. Multi-select apply still references `filenames.GetAt(0)` if the sheet sends apply, though controls are disabled. Permission changes do not appear to mark the page changed for add/remove in every path.

Test signals: load rights, add duplicate names, add normal/negative entries, multi-select disabled state, checkbox-to-rights ordering, remove multiple selections, apply/save failure behavior, and copy/clean ACL flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.h

Purpose: declares the ACL property page class for the Explorer extension.

Important types/APIs: `CPropACL` derives from `PropertyPage` and `CSetACLInterface`; it overrides `PropPageProc` and `IsNameInUse`. Private helpers manage ACL display, permission checkbox state, selection, removal, and permission string construction.

Control flow: no implementation. The class is instantiated with selected filenames and invoked through property sheet callbacks.

State/persistence: `m_Normal` and `m_Negative` hold pending ACL entries until apply.

Dependencies/integration: depends on `PropBase.h`, resource IDs, and `add_acl_entry_dlg.h` for the duplicate-name interface.

Risks: class stores ACLs as flat `CStringArray` pairs rather than a typed structure, making index mistakes easy.

Test signals: class construction from filename array, property page callback routing, and add-entry duplicate checks through the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.cpp

Purpose: provides the base implementation shared by shell extension property pages.

Important APIs/functions: `PropertyPage::PropertyPage` copies the selected filename array; `~PropertyPage` is empty; `SetHwnd` stores the dialog window handle; base `PropPageProc` returns `FALSE`.

Control flow: derived property pages call or override these minimal behaviors. The base callback is a no-op fallback.

State/persistence: stores selected filenames and window handle in object state. No persistent writes.

Dependencies/integration: uses MFC `CStringArray` and Win32 `HWND`; derived by file, ACL, and volume property page classes.

Risks: member fields such as `m_hInst`, `m_bIsSymlink`, `m_bIsMountpoint`, and `m_bIsDir` are declared in the header but not initialized here, so creators must set them before use.

Test signals: construction copies filenames rather than aliasing, derived pages receive/set HWND, and uninitialized flags are explicitly populated by property sheet creation code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.h

Purpose: declares the common base class for OpenAFS Explorer property pages.

Important types/APIs: `PropertyPage` stores `m_hwnd`, `m_hInst`, selected `filenames`, and booleans describing symlink, mountpoint, and directory state. It provides virtual `SetHwnd` and `PropPageProc`.

Control flow: property page subclasses override `PropPageProc` for message handling.

State/persistence: holds per-property-page runtime state only.

Dependencies/integration: includes resource IDs and relies on MFC/Win32 types. Used by `CPropFile`, `CPropACL`, and `CPropVolume`.

Risks: no constructor initialization for several public fields. Public mutable fields make lifecycle contracts implicit and easy to violate.

Test signals: object initialization by shell extension factory, flag propagation for mountpoint/symlink/directory pages, and callback dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.cpp

Purpose: implements the Explorer property page for AFS file metadata, symlink/mountpoint details, cache flushing, and Unix mode bits.

Important APIs/functions: `CPropFile::PropPageProc`, `ShowUnixMode`, `EnableUnixMode`, and `MakeUnixModeString`.

Control flow: initialization handles empty selection, multi-selection, or single item. For a single item it chooses type text from mountpoint/symlink/directory/file flags, shows remove/edit controls as appropriate, loads mode bits, file ID, owner, group, mountpoint/symlink target info, and cell name. Apply serializes checkbox state and calls `SetUnixModeBits`. Button handlers flush files, remove symlink/mountpoint after confirmation, edit mountpoint/symlink using dedicated dialogs, or mark the property sheet changed for mode-bit edits.

State/persistence: pending Unix mode changes live in checkbox state until apply. Persistent effects occur through `SetUnixModeBits`, `Flush`, `RemoveSymlink`, `RemoveMount`, and make/edit dialogs.

Dependencies/integration: relies on `gui2fs` operations, message helpers, mountpoint/symlink dialogs, MFC property sheet notifications, and `TaLocale`.

Risks: the `IDC_EDIT` case falls through to permission-control cases after launching an edit dialog, which may mark the page changed unintentionally. `m_volName` is passed to mountpoint edit but not set in this file. Multi-select still records cell from first item only.

Test signals: file/dir/mountpoint/symlink UI variants, apply mode changes, flush, remove with cancel/confirm, edit flows, multi-select behavior, and fall-through regression around `IDC_EDIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.h

Purpose: declares the file property page class for the Explorer extension.

Important APIs/types: `CPropFile` derives from `PropertyPage`, overrides `PropPageProc`, and provides helpers for enabling, displaying, and constructing Unix permission strings. It stores `m_cellName` and `m_volName`.

Control flow: implementation handles property sheet initialization, command handling, and apply notifications.

State/persistence: class members cache cell/volume context; UI state stores pending mode changes until apply.

Dependencies/integration: depends on `PropBase.h`, resource IDs, and MFC `CString`.

Risks: `m_volName` is not initialized in this header or its constructor, so creators or future code must set it before mountpoint editing depends on it.

Test signals: construction with filename arrays, flag-driven UI, and mode string round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.cpp

Purpose: implements the Explorer property page for AFS volume and server/quota information.

Important APIs/functions: `CPropVolume::PropPageProc` handles initialization, apply, and flush button commands.

Control flow: on init it decides whether to follow a mountpoint, displays selected path, cell, fileserver, volume info, quota and partition metrics, and "where is" server list. It uses `StrFormatByteSize64` for human-readable quota/partition sizes. The flush button calls `FlushVolume`.

State/persistence: no pending editable state; page is mostly read-only. Persistent/remote effect is cache flush through `FlushVolume`.

Dependencies/integration: relies on `gui2fs` functions (`GetCellName`, `GetServer`, `GetVolumeInfo`, `GetServers`, `FlushVolume`), MFC, `shlwapi`, and resource IDs.

Risks: partition percentage divides by `m_nPartSize` without guarding zero. If `GetVolumeInfo` fails, partially initialized `volInfo` fields must be safe. Multi-selection uses only first filename.

Test signals: normal volume info, quota unlimited, zero partition size, mountpoint follow/non-follow behavior, multiple servers list formatting, `GetVolumeInfo` failure message, and flush-volume command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.h

Purpose: declares the AFS volume property page class.

Important APIs/types: `CPropVolume` derives from `PropertyPage` and overrides `PropPageProc`.

Control flow: no implementation; all behavior is in `PropVolume.cpp`.

State/persistence: no additional fields beyond base property page state.

Dependencies/integration: depends on resource IDs and `PropBase.h`.

Risks: minimal class surface, but behavior depends heavily on base fields being initialized by the creator.

Test signals: construction and property sheet callback routing for selected AFS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.cpp

Purpose: implements the modal dialog for adding a normal or negative AFS ACL entry.

Important APIs/functions: constructor initializes localized dialog template and clears the ACL interface pointer; `OnInitDialog` sets normal-entry default and disables OK; `MakePermString` builds rights letters; `OnOK` validates duplicate names through `CSetACLInterface`; radio/name/help handlers update state.

Control flow: user chooses normal/negative entry, types a name, selects permission checkboxes, and presses OK. The dialog collects name/rights, checks for duplicates in the target ACL list, and returns values to the caller.

State/persistence: maintains `m_bNormal`, `m_Rights`, `m_strName`, and `m_pAclSetDlg` in memory. No persistent writes; caller updates ACL arrays and eventually saves.

Dependencies/integration: used by `CPropACL` and `set_afs_acl` style dialogs, uses localized resources, MFC DDX, and help/message helpers.

Risks: `m_pAclSetDlg` must be set before OK; otherwise `OnOK` dereferences null. `OnChangeName` enables OK when name is non-empty but never disables it again if the name is cleared.

Test signals: normal/negative selection, each permission bit, empty-name enable/disable, duplicate-name rejection, missing interface defensive behavior, and help launch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.h

Purpose: declares the ACL add-entry dialog and duplicate-name callback interface.

Important types/APIs: `CSetACLInterface` defines pure virtual `IsNameInUse`; `CAddAclEntryDlg` exposes `SetAclDlg`, `GetName`, `GetRights`, and `IsNormal`, plus MFC controls for name, entry type, and permission checkboxes.

Control flow: dialog users instantiate, set the ACL interface, run `DoModal`, and then read returned entry fields.

State/persistence: holds pending entry name/rights/type only.

Dependencies/integration: uses MFC `CDialog`, `CButton`, `CEdit`, `CString`, resource IDs, and message maps.

Risks: header has no include guard around all MFC dependencies beyond its own guard, and the interface pointer requirement is implicit.

Test signals: compile inclusion from ACL property/dialog modules and duplicate-name callback use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_acl_entry_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.cpp

Purpose: implements a modal add/edit dialog for AFS submount entries.

Important APIs/functions: `CAddSubmtDlg` constructor, `OnInitDialog`, `CheckEnableOk`, edit-change handlers, `OnOK`, `SetSubmtInfo`, `GetSubmtInfo`, and `OnHelp`.

Control flow: the dialog initializes localized resources, optionally switches to edit mode by disabling share-name editing, enables OK only when both share and path are non-empty, records save intent on OK, and returns a new `CSubmountInfo` with `SIS_ADDED` or `SIS_CHANGED`.

State/persistence: local MFC fields `m_strShareName`, `m_strPathName`, `m_bAdd`, and `m_bSave`; no direct persistence. Caller owns returned `CSubmountInfo` and performs actual submount update.

Dependencies/integration: depends on `CSubmountInfo`, help IDs, messages, MFC DDX, and localized dialog templates.

Risks: `GetSubmtInfo` allocates with `new`, so callers must delete. Validation only checks non-empty fields here; path/share semantic validation must happen elsewhere.

Test signals: add mode, edit mode title/disabled share, OK enable behavior, cancel returning null, returned status, and help ID selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.h

Purpose: declares the add/edit submount dialog.

Important APIs/types: `CAddSubmtDlg` exposes `SetAddMode`, `SetSubmtInfo`, and `GetSubmtInfo`; tracks share and path strings through DDX.

Control flow: callers configure add/edit mode and optional existing info, run the dialog, then retrieve a new `CSubmountInfo` if saved.

State/persistence: pending share/path and save/add flags; no direct registry or filesystem writes.

Dependencies/integration: forward-declares `CSubmountInfo`, uses MFC controls and resource IDs.

Risks: no include guard in this header. Ownership of `GetSubmtInfo` result is manual and must be documented by callers.

Test signals: inclusion in submount management UI and object ownership handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.cpp

Purpose: MFC DLL application and COM self-registration implementation for the OpenAFS Explorer shell extension.

Important APIs/functions: `CAfsShlExt` constructor, `InitInstance`, `DllGetClassObject`, `DllCanUnloadNow`, `WideCharToLocal`, `DoRegCLSID`, `DllRegisterServer`, `DoValueDelete`, and `DllUnregisterServer`.

Control flow: app construction starts Winsock. Initialization loads localized resources, registers OLE factories, and sets help path. COM exports delegate to MFC. Registration writes CLSID `InprocServer32` entries, threading model, shell icon overlay identifiers, approved shell-extension entries, context menu handlers, info-tip handler, and property sheet handlers for files/drives/directories. Unregistration removes corresponding keys/values.

State/persistence: persistent effects are registry writes under HKCR and HKLM. `DllCanUnloadNow` intentionally returns `S_FALSE`, keeping the extension loaded to avoid reload issues.

Dependencies/integration: depends on MFC OLE factories, Explorer shell extension registry contracts, OpenAFS resource/help modules, WinSock, `afsreg`, and architecture-specific interface IIDs.

Risks: `DoRegCLSID` closes the passed root key handle even when it is a predefined key. `DoValueDelete` opens a subkey but deletes values against the root key, likely wrong. Registration duplicates some work and requires elevation for HKLM/HKCR. Permanent `S_FALSE` can keep stale code loaded.

Test signals: regsvr32 register/unregister on 32/64-bit, registry keys/values correctness, Explorer context/property/overlay loading, localized resource loading, and unload behavior after Explorer restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.h

Purpose: declares the MFC application object for the OpenAFS shell extension DLL.

Important types/APIs: `CAfsShlExt : public CWinApp` with constructor and `InitInstance` override; declares global `theApp`.

Control flow: MFC calls `InitInstance` during DLL initialization; COM class factories are registered in the implementation.

State/persistence: the app object holds normal MFC application state; no direct persistence in header.

Dependencies/integration: requires `stdafx.h` before inclusion, includes `resource.h`, and uses MFC message-map macros.

Risks: standard MFC extension pattern but tied to precompiled header ordering. Header exposes minimal shell-extension functionality; COM classes are elsewhere.

Test signals: DLL load with MFC state, resource availability, and global app initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.cpp

Purpose: implements the Explorer extension authentication dialog showing current AFS tokens and launching get/discard token dialogs.

Important APIs/functions: `CAuthDlg` constructor, `OnInitDialog`, `OnGetTokens`, `OnDiscardTokens`, `FillTokenList`, `GetSelectedCellName`, and `OnHelp`.

Control flow: initialization configures hidden tab stops so each list item can include an invisible cell-name field, then fills the list from `GetTokenInfo`. Get/discard buttons create `CKlogDlg` or `CUnlogDlg`, seed them with the selected cell, and refresh the token list on success.

State/persistence: no local persistence; token state is changed by klog/unlog dialogs and `gui2fs` token operations.

Dependencies/integration: depends on `gui2fs`, `klog_dlg`, `unlog_dlg`, MFC listbox controls, localized resources, and help IDs.

Risks: hidden cell parsing depends on tab-delimited `GetTokenInfo` string format. If no token is selected, an empty cell is passed to dialogs, which must handle default behavior.

Test signals: empty token list, multiple token entries, selected-cell parsing, get-token success/failure, discard-token success/failure, and help display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.h

Purpose: declares the authentication/token management dialog class.

Important APIs/types: `CAuthDlg : public CDialog` with `FillTokenList`, `GetSelectedCellName`, and MFC handlers for initialization, get tokens, discard tokens, and help. It owns `m_TokenList`.

Control flow: callers run the modal dialog; handlers delegate token changes to sub-dialogs.

State/persistence: in-memory listbox state only.

Dependencies/integration: uses MFC and resource ID `IDD_AUTHENTICATION`.

Risks: no include guard. Token-list item format is implicit between implementation and `gui2fs`.

Test signals: modal construction, list refresh, and selected-cell propagation to klog/unlog dialogs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.cpp

Purpose: implements a simple dialog for choosing whether to clear normal ACL entries, negative ACL entries, or both.

Important APIs/functions: constructor initializes localized template and booleans; `DoDataExchange` binds `IDC_NEGATIVE` and `IDC_NORMAL`; `GetSettings` returns selected flags.

Control flow: MFC dialog lifecycle handles checkbox state through DDX. Caller retrieves settings after modal completion.

State/persistence: only local booleans `m_bNormal` and `m_bNegative`; no direct ACL writes.

Dependencies/integration: used by ACL cleanup flows, depends on `TaLocale` through dialog resource lookup and MFC DDX.

Risks: no validation prevents OK with neither checkbox selected unless handled in the dialog resource or caller.

Test signals: checkbox default state, selected settings returned, cancel handling by caller, and localized dialog loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.h

Purpose: declares the clear-ACL options dialog.

Important APIs/types: `CClearAclDlg : public CDialog`, `GetSettings(BOOL& bNormal, BOOL& bNegative)`, resource ID `IDD_CLEAR_ACL`, and checkbox booleans.

Control flow: callers run modal dialog then inspect selected settings.

State/persistence: local checkbox state only.

Dependencies/integration: uses MFC and resource IDs.

Risks: no include guard; validation policy is not explicit.

Test signals: inclusion from ACL-management UI and expected checkbox settings after user interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.cpp

Purpose: implements the dialog for copying ACLs from one directory to another, optionally clearing target ACLs first.

Important APIs/functions: constructor, `OnInitDialog`, `OnChangeToDir`, `OnBrowse`, `OnOK`, and `OnHelp`.

Control flow: initialization displays the source directory. The target edit box enables OK when non-empty. Browse uses `CFileDialog` to choose an existing file and then strips to its containing directory. OK records the clear flag and target path, validates the target with `PathIsDirectory`, and closes on success.

State/persistence: local `m_strFromDir`, `m_strToDir`, and `m_bClear`; actual ACL copy is performed by the caller.

Dependencies/integration: used by `CPropACL`, depends on MFC, `shlwapi`, `_access`/I/O headers, message helpers, and help IDs.

Risks: `PathIsDirectory` returns BOOL, but the code compares to `-1`, so nonexistent paths may not be rejected as intended. Browse cannot select a directory directly, only a file whose directory is then used.

Test signals: empty target disables OK, invalid target rejection, browse path trimming for root and nested paths, clear checkbox propagation, and help display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.h

Purpose: declares the ACL copy dialog class.

Important APIs/types: `CCopyAclDlg : public CDialog`; public getters `GetToDir`, `GetClear`, and setter `SetFromDir`; MFC controls for OK, source, target, and clear checkbox.

Control flow: caller sets source, runs dialog, then reads target/clear options.

State/persistence: local dialog fields only.

Dependencies/integration: MFC and resource ID `IDD_COPY_ACL`.

Risks: no include guard; target validation details are hidden in implementation.

Test signals: construction from ACL property page and option propagation to `CopyACL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.cpp

Purpose: implements a simple dialog listing AFS servers reported as down.

Important APIs/functions: constructor, `DoDataExchange`, `OnInitDialog`, and `SetServerNames`.

Control flow: caller supplies a `CStringArray` of server names. Initialization populates the listbox with each name.

State/persistence: stores server names in `m_ServerNames` and listbox UI state only; no external writes.

Dependencies/integration: MFC dialog/listbox, localized dialog template, and callers that detect down servers.

Risks: no refresh after initialization if `SetServerNames` is called while visible. It displays raw strings with no status metadata or retry path.

Test signals: empty list, multiple servers, string copying semantics, and dialog localization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.h

Purpose: declares the down-servers display dialog.

Important APIs/types: `CDownServersDlg : public CDialog`, `SetServerNames(const CStringArray&)`, resource ID `IDD_DOWN_SERVERS`, and `CListBox m_ServerList`.

Control flow: callers populate names before modal display; initialization fills the listbox.

State/persistence: in-memory copy of server names only.

Dependencies/integration: uses MFC and resource IDs.

Risks: no include guard and no metadata beyond display strings.

Test signals: server list passed by callers appears in the dialog in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.h -->
