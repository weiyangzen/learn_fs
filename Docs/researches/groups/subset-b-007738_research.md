# Group Research: subset-b-007738

This grouped report covers the OpenAFS Windows client configuration utility sources under `sources/distributed-fs/openafs/src/WINNT/client_config`. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/RegistrySupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/RegistrySupport.cpp

## Purpose
`RegistrySupport.cpp` is the low-level registry adapter for the Windows AFS client configuration UI. It reads and writes global service parameters under `AFSREG_CLT_SVC_PARAM_SUBKEY`, user preferences under `AFSREG_USER_OPENAFS_SUBKEY` with machine fallback, and the machine-wide `GlobalAutoMapper` drive map.

## Important APIs, Types, and Functions
The file exports `Config_GetGlobalDriveList`, `Config_ReadGlobalNum`, `Config_ReadGlobalString`, `Config_WriteGlobalNum`, `Config_WriteGlobalString`, `Config_ReadUserNum`, `Config_ReadUserString`, `Config_WriteUserNum`, and `Config_WriteUserString`. It uses Win32 registry APIs, `DRIVEMAPLIST`, `QueryDriveMapList`, `SubmountToPath`, and `FreeDriveMapList`.

## Control Flow
Global reads open the service parameter key read-only, query a value, close the key, and return `FALSE` on missing values. Global writes create the same key and set `REG_DWORD` or `REG_SZ`. User reads try `HKCU\...\OpenAFS` first and then fall back to `HKLM\...\OpenAFS`; user writes always create/update HKCU. `Config_GetGlobalDriveList` enumerates `GlobalAutoMapper` values whose names are drive letters and whose data are submount names, then translates each submount to an AFS path using the current submount list.

## State and Persistence Behavior
Persistent state is registry state: service-global parameters, per-user options, and global drive-to-submount entries. The function initializes output drive lists to zero and only fills entries that exist in the global registry key. Registry failures are treated as absent configuration, not fatal errors.

## Dependencies and Integration Points
This module is consumed by `config.cpp`, `dlg_automap.cpp`, `tab_general.cpp`, and other tabs through declarations in `config.h`. It depends on `drivemap.cpp` for submount path resolution and on OpenAFS registry key constants from `WINNT/afsreg.h`.

## Risks and Edge Cases
String write lengths use `sizeof(TCHAR)`, but some helper code elsewhere in the folder uses byte counts inconsistently; mixed ANSI/Unicode builds are a risk. Reads do not validate registry value types. `Config_GetGlobalDriveList` indexes directly by `drive - 'A'`, so malformed registry value names outside `A:` to `Z:` could address outside the 26-entry array.

## Test Signals
Useful checks are registry round-trip tests for HKLM/HKCU values, fallback behavior from HKCU to HKLM, malformed or missing registry key behavior, and `GlobalAutoMapper` enumeration with valid and invalid drive names/submounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/RegistrySupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/afs_config.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/afs_config.h

## Purpose
`afs_config.h` is the central include and global-state contract for the AFS client configuration applet. It pulls in the Win32 UI controls, OpenAFS configuration headers, local tab headers, CellServDB support, drive-map support, resources, and configuration APIs.

## Important APIs, Types, and Functions
The primary type is `GLOBALS`, exported as `extern GLOBALS g`. It stores the main property sheet, platform/admin flags, help-file path, restart-required flag, and an embedded `Configuration` struct containing gateway, cell, sysname, cache, daemon/thread, login, diagnostic, server preference, CellServDB, and drive-map state.

## Control Flow
This header has no executable flow, but it defines the shared state that `main.cpp` initializes and every tab reads or mutates. It also declares application helpers such as `Quit`, `AfsConfigReallocFunction`, `Main_OnInitDialog`, `Main_RefreshAllTabs`, `GetCautionTitle`, and `GetErrorTitle`.

## State and Persistence Behavior
`g.Configuration` is the in-memory staging area for values read from registry, CellServDB, service state, and pioctl calls. Dialogs compare their local values against `g.Configuration` before calling `Config_Set*` functions. `g.fNeedRestart` is the cross-tab signal that a service restart should be offered after applying changes.

## Dependencies and Integration Points
The header couples all client-config modules to `TaLocale`, custom controls (`fastlist`, `spinner`, `sockaddr`, `dialog`), `cellservdb.h`, `drivemap.h`, `resource.h`, `config.h`, `help.hid`, and OpenAFS registry constants.

## Risks and Edge Cases
Because `GLOBALS` is a process-wide mutable singleton, tabs can observe stale values if one dialog updates registry or service state without updating `g.Configuration`. The broad include surface also means build-order and macro conflicts are likely. The `REALLOC` macro hides pointer/count mutation, so misuse can silently corrupt shared arrays.

## Test Signals
Compile-time coverage should ensure every tab sees the same structure layout. Runtime smoke tests should open all tabs, apply changes in different orders, and verify `g.fNeedRestart` and `g.Configuration` remain consistent after commits and cancellations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/afs_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/afsmap.c -->
# sources/distributed-fs/openafs/src/WINNT/client_config/afsmap.c

## Purpose
`afsmap.c` is intended to be a small command-line tool for listing, adding, deleting, and persisting AFS drive mappings. It parses drive letters, AFS paths, UNC paths, optional submounts, and `/persistent`, then calls drive-map helpers.

## Important APIs, Types, and Functions
The file contains `usage` and `main`. It uses `MountDOSDrive`, `DisMountDOSDrive`, `WriteActiveMap`, `DriveIsGlobalAfsDrive`, `IsValidSubmountName`, `lana_GetNetbiosName`, and registry reads for `MountRoot`.

## Control Flow
`main` validates argument count, handles `/list` and `/help`, parses a drive letter, handles `/delete`, reads mount root and NetBIOS server name, then branches between UNC-style paths and AFS mount-root paths. UNC inputs are mapped directly by extracting the submount portion after `\\netbios\`. AFS paths optionally generate or accept a submount and persist the active-map flag.

## State and Persistence Behavior
The tool changes live Windows network drive mappings through `MountDOSDrive` and `DisMountDOSDrive`, and records desired active state with `WriteActiveMap`. It consults the service-parameter registry for the configured mount root and the SMB server name from LANA helper code.

## Dependencies and Integration Points
This file is a CLI-facing integration point for the same drive-mapping backend used by the GUI. It depends on OpenAFS fs utilities, rxkad headers, Win32 registry APIs, and the LANA/NetBIOS helper stack.

## Risks and Edge Cases
The current code has multiple apparent defects: it references `program` instead of `argv[0]`, uses `stricmp` tests as though zero means false in some branches, indexes `argv[2]`/`argv[3]` without proving they exist, mixes `cm_mountRoot` names with local `mountRoot`, and passes bad arguments to `strncpy`. These make this file high risk unless it is dead or excluded from the build. Path comparisons also appear to use `argv[1]` where `argv[3]` was intended.

## Test Signals
Tests should cover `/help`, `/list`, add/delete with bad arity, invalid drives, global-drive deletion refusal, UNC path parsing, AFS path parsing with generated and explicit submounts, and persistent flag storage. Static analysis or a build of this target should be treated as a primary signal because the source has compile-time-looking errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/afsmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.c -->
# sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.c

## Purpose
`cellservdb.c` implements an editable in-memory model for OpenAFS `CellServDB`/`AFSDCELL.INI` style files. It reads file lines into a doubly linked list, parses cell and server records, formats records back into text, and supports add/remove operations used by the Hosts tab.

## Important APIs, Types, and Functions
Key exports are `CSDB_GetFileName`, `CSDB_ReadFile`, `CSDB_WriteFile`, `CSDB_FreeFile`, `CSDB_CrackLine`, `CSDB_FormatLine`, `CSDB_FindCell`, `CSDB_RemoveCell`, `CSDB_RemoveCellServers`, `CSDB_AddCell`, `CSDB_AddCellServer`, `CSDB_AddLine`, and `CSDB_RemoveLine`. It uses `CELLDBLINE`, `CELLSERVDB`, and `CELLDBLINEINFO`.

## Control Flow
`CSDB_ReadFile` resolves the path through `cm_GetCellServDB` when no filename is supplied, reads the full file, strips leading whitespace and blank lines, splits on EOLs, and appends each line into a linked list. `CSDB_CrackLine` distinguishes cell lines beginning with `>` from server-address lines, extracts optional linked cell/comment text, and converts server IP addresses with `inet_addr`. `CSDB_AddCell` creates or rewrites a cell line; server additions insert after a given line; remove helpers delete a cell header and/or following server lines until the next cell.

## State and Persistence Behavior
The `CELLSERVDB` object owns filename, dirty flag, and linked-list nodes. Writes only occur when `fChanged` is true and rewrite the whole file with CRLF endings. `CSDB_FreeFile` releases all nodes and clears the owner struct.

## Dependencies and Integration Points
The Hosts tab uses this module to display, edit, validate, and persist cell/server entries. `tab_general.cpp` also uses `CSDB_FindCell` as one fallback during cell validation. The file depends on OpenAFS `cm_config.h` for locating CellServDB and Winsock for IP parsing.

## Risks and Edge Cases
The parser drops blank/comment-only lines because it skips leading whitespace/eol and only stores parsed non-empty text, so a write may not preserve original formatting/comments. `CSDB_AddLine` uses `strcpy` into fixed `cchCELLDBLINE` buffers and assumes callers format bounded lines. One pointer bug appears in insertion: assigning `pNew->pNext->pPrev = pNew->pPrev` should likely be `pNew`, otherwise inserting in the middle can corrupt backward links.

## Test Signals
Tests should read/write a representative CellServDB with cells, linked cells, server comments, invalid IP lines, and multiline edits. Linked-list integrity after middle insert/remove, dirty-flag behavior, and preservation or intentional loss of comments should be verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.h

## Purpose
`cellservdb.h` defines the C ABI, data model, constants, and prototypes for the CellServDB editor used by the Windows configuration tool.

## Important APIs, Types, and Functions
It defines `BOOL` fallback values, `MAX_CSDB_PATH`, `cchCELLDBLINE`, linked-list node `CELLDBLINE`, owner `CELLSERVDB`, and parsed record `CELLDBLINEINFO`. Prototypes cover file discovery/read/write/free, line parse/format, cell lookup, cell/server removal, and cell/server/line insertion.

## Control Flow
The header exposes a list-oriented workflow: call `CSDB_ReadFile`, inspect or modify linked nodes through `CSDB_*` helpers, call `CSDB_WriteFile`, then call `CSDB_FreeFile`. C++ consumers include it under `extern "C"` guards.

## State and Persistence Behavior
`CELLSERVDB` carries all mutable state: `szFilename`, `fChanged`, and list head/tail. Each `CELLDBLINE` owns one fixed-size raw text line plus previous/next links. `CELLDBLINEINFO` is a parsed transient representation.

## Dependencies and Integration Points
The header is included by `afs_config.h`, `tab_hosts.cpp`, and validation paths in `tab_general.cpp`. It is intentionally C-compatible so both `.c` and `.cpp` sources can share the same parser.

## Risks and Edge Cases
The local `BOOL` typedef can conflict if included after Win32 headers in a C file. Fixed 512-byte line buffers and 2048-byte path buffers constrain long CellServDB entries. Callers must not mutate linked-list pointers directly because the implementation depends on them for file order.

## Test Signals
ABI checks should compile both C and C++ consumers. Functional tests should use the public sequence read, find, add/remove, write, free, and should validate behavior when lines exceed `cchCELLDBLINE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/config.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/config.cpp

## Purpose
`config.cpp` is the main configuration service adapter. It translates UI operations into registry writes, Windows service-state queries, OpenAFS pioctl calls, AFS credentials/tray integration, and gateway/cell handling.

## Important APIs, Types, and Functions
Important exports include `Config_GetServiceState`, gateway/cell getters and setters, `Config_ContactGateway`, `Config_FixGatewayDrives`, tray icon get/set, `Config_GetServerPrefs`, `Config_SetServerPrefs`, cache/chunk/stat/thread/daemon/sysname/root/mount/cache-path/LANA/diagnostic/login getters and setters, and `Config_GetCacheInUse`.

## Control Flow
Most getters read a registry value and fall back to an OpenAFS default. Most setters write the registry and set `g.fNeedRestart` when the change requires the service to restart. Live operations first verify `Config_GetServiceState() == SERVICE_RUNNING`, then issue pioctls such as `VIOC_GETSPREFS`, `VIOC_SETSPREFS`, `VIOCCKSERV`, `VIOC_AFS_SYSNAME`, and `VIOCGETCACHEPARMS`. Tray icon changes notify an existing `AfsCreds` window or start `AfsCreds.exe /quiet`.

## State and Persistence Behavior
Global persistent state is stored in HKLM service parameter keys through `Config_WriteGlobal*`; user display preferences use `Config_WriteUser*`. Server preferences are live cache-manager state, not plain registry state. `Config_SetSysName` updates the live cache manager if running and then persists `SysName`.

## Dependencies and Integration Points
This file bridges the GUI to Windows SCM, OpenAFS cache-manager ioctl interfaces, registry support, drive-map support, and `AfsCreds`. It is called by general, advanced, misc, binding, diagnostic, logon, and preference tabs.

## Risks and Edge Cases
Several functions assume caller-supplied buffers are `MAX_PATH`. `Config_SetServerPrefs` zeroes allocated input storage with `sizeof(cbInDataStorage)` rather than `cbInDataStorage`, leaving most bytes uninitialized. `Config_SetSysName` can read `InData.szData[j-1]` when whitespace is encountered before any character. Values written to registry are not range-validated here, relying on UI spinners.

## Test Signals
Use registry mock/fixture tests for defaults and restart flags, SCM tests for stopped/running state, pioctl stubs for server preferences/cache/sysname/probe behavior, and UI integration tests verifying restart prompts after restart-required settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/config.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/config.h

## Purpose
`config.h` declares the UI-facing configuration API and server-preference data structures. It is the shared contract between tabs/dialogs and `config.cpp`/`RegistrySupport.cpp`.

## Important APIs, Types, and Functions
It defines `SERVERPREF` with server IP/name/rank/change/list-item fields, `SERVERPREFS` with VL-vs-file-server mode and dynamic array metadata, and the sentinel rank `iRankREMOVED`. Prototypes cover service state, cell/gateway/tray/server prefs, cache parameters, daemon/thread counts, sysname/root/mount/cache path, LAN adapter, diagnostic/logon toggles, global drive list, and registry read/write helpers.

## Control Flow
The header groups APIs into high-level config operations and raw registry helpers. Tabs generally call getters during initialization, compare local UI state on apply, then call setters and update `g.Configuration`.

## State and Persistence Behavior
`SERVERPREFS` instances are heap-owned by callers and released through `Config_FreeServerPrefs`. `SERVERPREF.fChanged` controls whether `Config_SetServerPrefs` sends an entry back to the cache manager. Registry helpers distinguish global HKLM service state from user HKCU state.

## Dependencies and Integration Points
The header includes `fastlist.h` because server preferences store `HLISTITEM`, and `drivemap.h` for global drive-list operations. It is included indirectly by most client-config source files through `afs_config.h`.

## Risks and Edge Cases
The data contract mixes model data with UI handles (`hItem`), making background refresh and list rebuilds sensitive to stale handles. Optional `pStatus` defaults are C++-only, so C consumers must avoid these prototypes unless guarded.

## Test Signals
Compilation of all C++ consumers is the main structural signal. Runtime tests should verify `SERVERPREFS` lifetime, changed-entry filtering, and registry helper behavior with absent, malformed, and valid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_automap.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_automap.cpp

## Purpose
`dlg_automap.cpp` implements the Advanced tab's Global AutoMapper dialog, allowing administrators to view, add, edit, and remove machine-wide drive mappings stored under the `GlobalAutoMapper` registry key and applied as DOS drive mappings.

## Important APIs, Types, and Functions
Key routines are `AutoMap_DlgProc`, `AutoMap_OnInitDialog`, `ShowDriveList`, `UpdateRegistry`, `DefineDosDrive`, `AutoMap_OnAdd/Edit/Remove/Select`, `GetSelectedDrive`, and the nested `AutoMapEdit_*` dialog functions. It uses `DRIVEMAP`, `DRIVEMAPLIST`, `MountDOSDrive`, `DisMountDOSDrive`, `PathToSubmount`, `IsValidSubmountName`, and `AdjustAfsPath`.

## Control Flow
Initialization configures a fastlist, reads the global drive list through `Config_GetGlobalDriveList`, and renders drive/path rows. Add/edit opens `IDD_GLOBAL_DRIVES_ADDEDIT`, validates drive/path/submount inputs, resolves or creates a submount, then calls `DefineDosDrive`. Successful map/unmap operations update the registry and in-memory `GlobalDrives` array before refreshing the list.

## State and Persistence Behavior
`GlobalDrives` is a static snapshot for the dialog. Persistent state is HKLM `...\GlobalAutoMapper`, where value names are drive letters like `X:` and value data is the submount. Live state changes are made through `MountDOSDrive`/`DisMountDOSDrive`.

## Dependencies and Integration Points
The dialog is launched from `tab_advanced.cpp`. It shares validation and mapping primitives with the user drive tab and depends on OpenAFS mount-root globals initialized by `fs_utils_InitMountRoot`.

## Risks and Edge Cases
`UpdateRegistry` writes string lengths without multiplying by `sizeof(TCHAR)`, which is unsafe in Unicode builds. `ShowDriveList` ignores its `drives` parameter and always reads `GlobalDrives`. Editing first removes the old mapping, then tries to add the new one, so a failed add can leave the old mapping gone. Registry update failure after a successful map can leave live and persistent state divergent.

## Test Signals
Tests should exercise add/edit/remove with valid and invalid submounts, paths outside the mount root, drive-letter conflicts, map succeeds/registry fails, registry succeeds/map fails, and list refresh after direct registry edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_automap.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_binding.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_binding.cpp

## Purpose
`dlg_binding.cpp` implements the Advanced Binding dialog for selecting which LANA/NIC the OpenAFS SMB server binds to, or using the default adapter.

## Important APIs, Types, and Functions
Key routines are `Binding_DlgProc`, `Binding_OnInitDialog`, `Binding_OnOK`, `Binding_OnApply`, `Binding_OnCancel`, and `GetAdapterNumber`. It uses `Config_GetLanAdapter`, `Config_SetLanAdapter`, `lana_FindLanaByName`, and `lana_GetAfsNameString`.

## Control Flow
The first initialization loads the configured LAN adapter into static dialog state, enumerates LANA adapters into a combo box, selects the configured adapter if present, and displays the resulting AFS NetBIOS name. Toggling default NIC or selecting a combo entry recalculates `nLanAdapter` and updates the message. OK stores the chosen adapter in static state; Apply persists it if changed.

## State and Persistence Behavior
State is cached in file-static `fFirstTime`, `nLanAdapter`, `isGateway`, and `lanainfo`. Persistence is through the `LANadapter` global registry value via `Config_SetLanAdapter`, which marks the service for restart.

## Dependencies and Integration Points
The dialog is invoked by `tab_advanced.cpp` and participates in `AdvancedTab_OnApply`. It depends on the LANA helper library and the global configuration singleton.

## Risks and Edge Cases
`lanainfo` is allocated by helper code but freed with `delete`, which may not match the allocator. `fFirstTime` is only reset on cancel, so repeated OK/open cycles reuse cached data. If adapter enumeration fails, later combo operations may still assume `lanainfo` is valid. `WM_GETTEXT` length parameters use `sizeof(selected)` as TCHAR count, which is only correct in ANSI builds.

## Test Signals
Tests should cover no adapters, default NIC toggle, explicit adapter selection, stale configured adapter, gateway flag affecting displayed AFS name, cancel without persistence, and apply marking restart-required state through `Config_SetLanAdapter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_binding.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_diag.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_diag.cpp

## Purpose
`dlg_diag.cpp` implements the Advanced Diagnostics dialog for trace buffer size, trap-on-panic, and report-session-startups options.

## Important APIs, Types, and Functions
Key routines are `Diag_DlgProc`, `Diag_OnInitDialog`, `Diag_OnOK`, `Diag_OnApply`, `Diag_OnCancel`, and the helper `SetUpYesNoCombo`. It uses `Config_GetTraceBufferSize`, `Config_SetTraceBufferSize`, `Config_GetTrapOnPanic`, `Config_SetTrapOnPanic`, `Config_GetReportSessionStartups`, and `Config_SetReportSessionStartups`.

## Control Flow
On first initialization it reads values into `g.Configuration` and file-static dialog variables. It creates a spinner bounded between 3000 and 32000 for trace buffer size and two yes/no combo boxes. OK copies UI state to static variables; Apply compares those variables with `g.Configuration` and persists only changed values.

## State and Persistence Behavior
Static `fFirstTime` gates one-time reads; cancel resets it. Trace size and panic/session flags are persisted under global registry settings. Trace size and trap-on-panic changes mark `g.fNeedRestart` through `config.cpp`, while report-session-startups does not.

## Dependencies and Integration Points
The dialog is launched by `tab_advanced.cpp`; `Diag_OnApply` is called from `AdvancedTab_OnApply` so changes are committed with the rest of Advanced settings.

## Risks and Edge Cases
Repeated `WM_INITDIALOG` after OK may not reload from registry because `fFirstTime` remains false. Combo selection relies on index 0/1 mapping to `FALSE`/`TRUE`; changes to `CB_AddItem` semantics would break it. There is no validation beyond spinner bounds.

## Test Signals
Tests should check initial defaults, yes/no combo mapping, persistence only when changed, cancel discarding staged state, and restart prompt behavior after trace or trap changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_diag.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_logon.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_logon.cpp

## Purpose
`dlg_logon.cpp` implements the Advanced Logon dialog for login retry interval and whether failed integrated logons should be reported silently.

## Important APIs, Types, and Functions
The main routines are `Logon_DlgProc`, `Logon_OnInitDialog`, `Logon_OnOK`, `Logon_OnApply`, and `Logon_OnCancel`. It calls `Config_GetLoginRetryInterval`, `Config_SetLoginRetryInterval`, `Config_GetFailLoginsSilently`, and `Config_SetFailLoginsSilently`.

## Control Flow
On first initialization it loads registry-backed values into `g.Configuration` and static dialog state, creates a spinner with 5 to 180 bounds, localizes yes/no labels, and selects the current fail-silently flag. OK captures spinner and combo state. Apply persists changed values and updates `g.Configuration`.

## State and Persistence Behavior
Dialog state is static and reset on cancel. Both options are global registry values. `Config_SetLoginRetryInterval` and `Config_SetFailLoginsSilently` do not set the restart flag in `config.cpp`, implying they are read by logon-provider paths without requiring AFSD restart.

## Dependencies and Integration Points
The dialog is launched by `tab_advanced.cpp`; `Logon_OnApply` is called from the advanced commit path. It depends on custom spinner and combo helpers included through `afs_config.h`.

## Risks and Edge Cases
Like other advanced subdialogs, OK does not reset `fFirstTime`, so subsequent opens in the same process show staged state rather than re-reading registry. Combo indexes are assumed to map directly to boolean values. There is no explicit validation for registry values outside spinner bounds before control initialization.

## Test Signals
Tests should cover default values, min/max spinner behavior, yes/no localization, staged OK plus Advanced Apply persistence, cancel reset, and no unintended restart prompt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_logon.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_misc.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_misc.cpp

## Purpose
`dlg_misc.cpp` implements the Advanced Miscellaneous Parameters dialog for probe interval, server threads, daemon count, sysname, root volume, and mount directory.

## Important APIs, Types, and Functions
Core routines are `Misc_DlgProc`, `Misc_OnInitDialog`, `Misc_OnOK`, `Misc_OnApply`, and `Misc_OnCancel`. It uses `Config_GetProbeInt`, `Config_SetProbeInt`, `Config_GetNumThreads`, `Config_SetNumThreads`, `Config_GetNumDaemons`, `Config_SetNumDaemons`, `Config_GetSysName`, `Config_SetSysName`, `Config_GetRootVolume`, `Config_SetRootVolume`, `Config_GetMountRoot`, and `Config_SetMountRoot`.

## Control Flow
First initialization reads current values into `g.Configuration` and local globals, sets bounded spinners, and populates text fields. OK copies UI values into static globals. Apply compares staged values to `g.Configuration`, applies each changed value in sequence, and updates the global snapshot.

## State and Persistence Behavior
The dialog stores staged values in file-scope globals, with `fFirstTime` reset only on cancel. Probe interval is applied live through a pioctl when the service is running; thread/daemon/root/mount settings are registry-backed and mark restart required. Sysname is applied live and persisted when possible.

## Dependencies and Integration Points
`tab_advanced.cpp` opens this dialog and calls `Misc_OnApply` as part of the Advanced tab commit. The general tab later uses `g.fNeedRestart` to offer service restart after changes.

## Risks and Edge Cases
The file has `#if undef` blocks for old LANA UI, suggesting dead code around adapter selection. `GetDlgItemText` uses `sizeof(szSysName)` for TCHAR count, unsafe under Unicode. Partial apply can leave earlier values persisted if a later setter fails.

## Test Signals
Tests should verify spinner bounds, live probe pioctl behavior, sysname whitespace validation in `config.cpp`, restart flagging for thread/daemon/root/mount changes, and partial-failure UI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/dlg_misc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.cpp

## Purpose
`drivemap.cpp` is the core Windows drive/submount mapping engine for the configuration UI, command-line mapper, and logon-provider remapping behavior. It translates AFS paths and submounts, persists user and machine mapping preferences, detects live network-drive state, and mounts/unmounts DOS drive letters or AFS shares.

## Important APIs, Types, and Functions
Major exports include `QueryDriveMapList`, `WriteDriveMappings`, `FreeDriveMapList`, `ActivateDriveMap`, `InactivateDriveMap`, `AddSubMount`, `RemoveSubMount`, `AdjustAfsPath`, `GetDriveSubmount`, `SubmountToPath`, `PathToSubmount`, `WriteActiveMap`, `ForceMapActive`, `SetBitLogonOption`, `RWLogonOption`, `DoMapShare`, `DoMapShareChange`, `GlobalMountDrive`, `MountDOSDrive`, and `DisMountDOSDrive`.

## Control Flow
Querying maps initializes all 26 drive entries, reads HKLM submount definitions, reads HKCU drive mappings, scans live network drives through `QueryDosDevice` or WNet APIs, marks active/in-use entries, and rewrites mappings if unexpected AFS drives are discovered. Activating a drive validates that the target is under the AFS mount root, asks AFSD for or creates a submount via `VIOC_MAKESUBMOUNT`, then calls `MountDOSDrive`. Logon remapping unmounts stale AFS connections, maps all submount shares, ensures `all` exists, and remaps active or forced drives after service startup.

## State and Persistence Behavior
Persistent state spans HKLM submounts, HKCU mappings, HKCU active-map flags, HKLM logon-provider options, and HKLM global automapper entries. Live state is Windows network connections or AFSIFS DOS-device definitions. Static globals track service transition state and a one-shot username override.

## Dependencies and Integration Points
The file is called by drive tabs, automapper dialogs, `config.cpp`, `tab_general.cpp`, `afsmap.c`, and service-start/stop flows. It depends on Win32 registry, SCM, WNet, QueryDosDevice/DefineDosDevice, OpenAFS pioctl interfaces, fs-utils mount-root globals, LANA NetBIOS helper code, and optional `AFSIFS` paths.

## Risks and Edge Cases
This module contains several high-risk areas: mixed TCHAR/char length calculations, many fixed `MAX_PATH` buffers with `sprintf`/`strcpy`, complex parsing of OS-version-specific LanmanRedirector device paths, and live/persistent divergence when WNet or registry writes fail. `DoMapShareChange` ignores its `removeUnknown` parameter. `ReadRegistryString` creates missing keys while reading. Some allocation/free paths assume OpenAFS `Allocate`/`Free`, others use `malloc`.

## Test Signals
Important tests include registry fixtures for submounts/mappings/active flags, live-drive detection on NT/Win2K/XP-style device paths, AFSIFS and non-AFSIFS mount/unmount behavior, service-start remapping, global automapper entries, invalid submount names, and pioctl failure paths in `PathToSubmount`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.h

## Purpose
`drivemap.h` defines the drive mapping model and public API shared by the GUI tabs, global automapper dialog, command-line mapper, and logon remapping code.

## Important APIs, Types, and Functions
It defines drive-letter constants, `DRIVEMAP`, `SUBMOUNT`, and `DRIVEMAPLIST`. Public functions cover validation, querying/writing/freeing mappings, activating/inactivating drives, adding/removing submounts, path/submount translation, live submount detection, service-logon mapping operations, DOS drive mount/dismount, active-map flags, and logon-option bit manipulation.

## Control Flow
The typical workflow is `QueryDriveMapList`, inspect or edit `DRIVEMAPLIST`, `ActivateDriveMap`/`InactivateDriveMap` live state, then `WriteDriveMappings` or `AddSubMount`/`RemoveSubMount` for persistence. Logon-provider users call `TestAndDoMapShare`, `DoMapShare`, or `DoMapShareChange`.

## State and Persistence Behavior
The structs represent both persisted desired state and detected live state. `DRIVEMAP.fPersistent` controls Windows profile persistence; `fActive` records whether the mapping is currently connected. `SUBMOUNT.fInUse` prevents deletion of submounts currently referenced by live mappings.

## Dependencies and Integration Points
The header is included by `afs_config.h`, `config.h`, `RegistrySupport.cpp`, `dlg_automap.cpp`, `tab_drives.cpp`, `config.cpp`, and `afsmap.c`. It exports global username state and logon-option helpers for network-provider integration when `DRIVEMAP_DEF_H` is not set.

## Risks and Edge Cases
The API exposes mutable arrays and global variables directly, so callers can create inconsistent state. Several prototypes use default arguments, tying the header to C++ even though it is included by at least one `.c` source. Buffer ownership and expected lengths are implicit.

## Test Signals
Compile tests should validate C/C++ inclusion assumptions. API-level tests should check that each public mutator preserves `DRIVEMAPLIST` invariants and that caller-provided buffers receive normalized AFS paths/submounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.cpp

## Purpose
`isadmin.cpp` detects whether the process is running on Windows NT and whether the current user has OpenAFS client administration rights.

## Important APIs, Types, and Functions
The exports are `IsWindowsNT` and `IsAdmin`. `IsAdmin` checks membership in the local `AFS Client Admins` group and also treats LocalSystem as administrative.

## Control Flow
`IsWindowsNT` caches `GetVersionEx` platform detection. `IsAdmin` caches its result after first evaluation, builds `COMPUTERNAME\AFS Client Admins`, resolves the group SID, opens the process token, uses `CheckTokenMembership`, falls back to enumerating `TokenGroups`, and finally compares the token user SID against LocalSystem.

## State and Persistence Behavior
Only static process-local cache state is maintained. If the AFS Client Admins group cannot be found, the function intentionally grants admin privileges to preserve compatibility on systems without the group.

## Dependencies and Integration Points
`main.cpp` uses these functions to set `g.fIsWinNT` and `g.fIsAdmin`. The General tab uses `g.fIsAdmin` to enable/disable service start/stop and configuration controls. The code depends on Win32 security APIs and `TaLocale`-included platform headers.

## Risks and Edge Cases
Returning admin when the local group is absent is permissive. Some early returns before `fTested = TRUE` mean repeated calls can redo work after unexpected computer-name lookup failures. Token handles are not explicitly closed, which can leak handles. Allocation and lookup failures generally bias toward allowing operation after the group has been detected once.

## Test Signals
Tests should cover group missing, user in group, user not in group, LocalSystem token, failed `GetComputerName`, denied token queries, and repeated calls verifying cache behavior and handle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.h

## Purpose
`isadmin.h` declares platform/admin detection helpers used during application startup.

## Important APIs, Types, and Functions
It exposes `BOOL IsWindowsNT(void)` and `BOOL IsAdmin(void)`.

## Control Flow
Consumers call `IsWindowsNT` to select NT versus Win9x UI/service behavior and `IsAdmin` to gate service-control and configuration permissions.

## State and Persistence Behavior
The header itself has no state. The implementation caches both decisions in static variables.

## Dependencies and Integration Points
`main.cpp` includes this header directly and writes the results into `GLOBALS g`; tabs subsequently consult those flags rather than calling these functions repeatedly.

## Risks and Edge Cases
The header assumes `BOOL` is already defined by included Windows/OpenAFS headers. It does not document the permissive "missing AFS Client Admins group means admin" policy implemented in `isadmin.cpp`.

## Test Signals
Compile coverage is sufficient for the header. Behavioral tests belong to `isadmin.cpp` and should verify UI gating in `main.cpp`/`tab_general.cpp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/main.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/main.cpp

## Purpose
`main.cpp` is the Win32 entry point and property-sheet bootstrap for the AFS Client Configuration utility and Control Center variant.

## Important APIs, Types, and Functions
It defines the global `GLOBALS g`, `WinMain`, `Main_ShowMountTab`, `Main_OnInitDialog`, `Main_RefreshAllTabs`, `Quit`, `GetCautionTitle`, and `GetErrorTitle`.

## Control Flow
`WinMain` loads localized resources, starts Winsock, registers custom controls, initializes mount-root utilities, clears `g`, detects platform/admin state, parses `/c` for Control Center mode, selects the help file, creates a property sheet, and adds tabs based on mode, OS, and `ShowMountTab` registry policy. The modal property sheet owns the app lifetime.

## State and Persistence Behavior
`g` holds all process-global app state. `Main_ShowMountTab` reads `ShowMountTab` from HKCU first and HKLM second, using 64-bit registry view on WOW64. `Main_OnInitDialog` centers the property sheet and strips context-help styles. Title helpers cache localized strings.

## Dependencies and Integration Points
The entry point wires together general, drives, prefs, hosts, and advanced tabs. It depends on `isadmin`, custom UI control registration, `fs_utils_InitMountRoot`, registry constants, and the property-sheet helper library.

## Risks and Edge Cases
The command-line parser only recognizes leading slash/dash options and appears to advance only over spaces after each option, so combined or valued options are not robust. There is no `WSACleanup`. Tab inclusion depends on registry policy and OS/admin flags, so missing registry values can hide drive UI.

## Test Signals
Smoke tests should verify startup in NT, Win9x-compatible, and Control Center modes; `ShowMountTab` policy from HKCU/HKLM including WOW64; correct tab set; help-file selection; and `Main_RefreshAllTabs` delivery of `IDC_REFRESH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/misc.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/misc.cpp

## Purpose
`misc.cpp` provides a shared dynamic-array reallocation helper used by macros in `afs_config.h` and several configuration data paths.

## Important APIs, Types, and Functions
The only export is `AfsConfigReallocFunction(LPVOID *ppTarget, size_t cbElement, size_t *pcTarget, size_t cReq, size_t cInc)`.

## Control Flow
If the requested count is already within capacity, it returns true. Otherwise it rounds requested capacity up to the next increment, allocates zeroed memory with OpenAFS `Allocate`, copies existing entries, frees the old block with `Free`, updates pointer and capacity, and returns success.

## State and Persistence Behavior
It mutates caller-owned pointer and capacity variables; no persistent state is stored. Existing elements are preserved and new capacity is zero-initialized.

## Dependencies and Integration Points
The `REALLOC` macro in `afs_config.h` wraps this helper. It is used by server-preference arrays and other dynamic lists.

## Risks and Edge Cases
No overflow checks are performed for `cbElement * cNew`. A zero or invalid increment can produce failure. The helper assumes all memory was allocated with the same OpenAFS allocator pair.

## Test Signals
Unit tests should cover no-op growth, exact boundary growth, increment rounding, content preservation, zeroing of new slots, allocation failure, and large-count overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/misc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.cpp

## Purpose
`pagesize.cpp` reads configured Windows paging-file sizes and converts them into a kilobyte total, presumably for cache-size guidance.

## Important APIs, Types, and Functions
It exports `ExtractPageSize` and `GetPagingSpace`. `ExtractPageSize` pulls the trailing numeric size from a paging-file string. `GetPagingSpace` reads the `PagingFiles` `REG_MULTI_SZ` value under `SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management`.

## Control Flow
`GetPagingSpace` opens the Memory Management key, queries `PagingFiles`, iterates each null-terminated entry in the multi-string, sums `ExtractPageSize`, closes the key, and returns the sum multiplied by 1024.

## State and Persistence Behavior
No state is mutated. The function reads system registry state and returns zero if the key or value cannot be read.

## Dependencies and Integration Points
The file depends on Win32 registry APIs and `pagesize.h`. `tab_advanced.cpp` includes `pagesize.h`, though current cache bounds use fixed constants rather than calling `GetPagingSpace`.

## Risks and Edge Cases
`ExtractPageSize` assumes the final numeric run is the desired page-file maximum/minimum value. The returned unit is named `ckPageSpace` but multiplies by 1024, so callers must understand the expected units. Buffer size is fixed at 1024 TCHARs and may truncate unusually large multi-string values.

## Test Signals
Tests should cover standard `PagingFiles` entries, multiple entries, missing registry values, entries with no trailing digits, and unit expectations against cache-size UI limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.h

## Purpose
`pagesize.h` declares helpers for extracting and summing Windows paging-file sizes.

## Important APIs, Types, and Functions
It declares `ULONG ExtractPageSize(LPCTSTR psz)` and `ULONG GetPagingSpace(void)`.

## Control Flow
The intended flow is to parse individual paging-file strings with `ExtractPageSize` or call `GetPagingSpace` to read all configured paging files.

## State and Persistence Behavior
There is no state in the header or implementation; only registry reads occur in `pagesize.cpp`.

## Dependencies and Integration Points
The header is included by `tab_advanced.cpp`, making paging-space information available for cache sizing even though the current UI uses fixed min/max constants.

## Risks and Edge Cases
The header assumes Windows types such as `ULONG` and `LPCTSTR` are already in scope. It does not document units, which is important because `GetPagingSpace` multiplies parsed values by 1024.

## Test Signals
Compile inclusion from `tab_advanced.cpp` and unit coverage of `pagesize.cpp` parsing/units are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/resource.h

## Purpose
`resource.h` defines numeric resource identifiers for localized strings, dialogs, icons, and controls used by the Windows AFS client configuration UI.

## Important APIs, Types, and Functions
It defines string IDs for titles, service states, warnings, errors, column labels, and validation messages; dialog IDs such as `IDD_GENERAL_NT`, `IDD_PREFS_NT`, `IDD_HOSTS_NT`, `IDD_DRIVE_EDIT`, and advanced subdialogs; icon IDs; and control IDs such as `IDC_STATUS`, `IDC_CELL`, `IDC_LIST`, `IDC_CACHE_SIZE`, `IDC_GLOBAL_DRIVE_LIST`, and `IDC_NICSELECTION`.

## Control Flow
There is no executable control flow. The IDs are consumed by resource scripts and by code calling `GetString`, `ModalDialog`, `PropSheet_AddTab`, `GetDlgItem`, and WinHelp.

## State and Persistence Behavior
The header has no state. The stability of numeric IDs is a persistence-like contract with compiled resources and help mappings.

## Dependencies and Integration Points
Every UI source file depends on this header indirectly through `afs_config.h`. It must stay synchronized with `afs_config.rc` language files and `help.hid`.

## Risks and Edge Cases
Duplicate control IDs are intentionally reused in different dialogs, so handlers must be scoped to the active dialog. Changing numeric values can break resource binding, help contexts, or saved UI automation tests. Several IDs share the same value for aliases, such as `IDD_DRIVES`/`IDD_DRIVES_NT` and `IDC_ADVANCED`/`IDC_IMPORT`.

## Test Signals
Resource compilation is the primary signal. UI smoke tests should open each dialog and verify controls can be found by the expected IDs, with localized strings loaded for all string IDs referenced by code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.cpp

## Purpose
`tab_advanced.cpp` implements the Advanced property-sheet tab for cache size/path, chunk size, stat entries, and access to advanced subdialogs for misc, binding, logon, automap, and diagnostics.

## Important APIs, Types, and Functions
Exports are `AdvancedTab_DlgProc` and `AdvancedTab_CommitChanges`. Internal routines include `AdvancedTab_OnInitDialog`, `AdvancedTab_OnApply`, `AdvancedTab_OnRefresh`, and a local `log2`. It calls many `Config_*` getters/setters and subdialog apply functions.

## Control Flow
Initialization reads cache/path/chunk/stat settings, creates spinners, sets cache path text, and refreshes cache-in-use display. Commands open subdialogs or handle spinner power-of-two adjustment for chunk size. Apply persists changed top-level values, then calls `Misc_OnApply`, `Binding_OnApply`, `Logon_OnApply`, and `Diag_OnApply`.

## State and Persistence Behavior
The tab stores current values in `g.Configuration`; setters write registry values and usually mark `g.fNeedRestart`. Cache-in-use is live service state read by pioctl and displayed as informational text.

## Dependencies and Integration Points
It integrates with `config.cpp`, `pagesize.h`, and all advanced subdialogs. The General tab calls `AdvancedTab_CommitChanges` before service start/restart decisions.

## Risks and Edge Cases
Subdialog state is applied only when the Advanced tab applies, so users can OK a subdialog and then cancel the main sheet without persistence. The top-level sysname control is initialized but not applied here, likely legacy or mismatched resource usage. Chunk size normalization assumes powers of two and may behave unexpectedly for zero.

## Test Signals
Tests should cover spinner bounds, chunk power-of-two normalization, cache-in-use display with stopped service, subdialog staged apply behavior, and restart prompting after cache/chunk/stat/path changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.h

## Purpose
`tab_advanced.h` declares the Advanced tab dialog procedure and commit hook.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK AdvancedTab_DlgProc(HWND, UINT, WPARAM, LPARAM)` and `BOOL AdvancedTab_CommitChanges(BOOL fForce)`.

## Control Flow
The property sheet uses the dialog procedure for UI messages. Other tabs, especially General, call `AdvancedTab_CommitChanges` to force pending advanced settings to persist before service start/restart logic.

## State and Persistence Behavior
The header has no state. Implementation state lives in `g.Configuration` and subdialog statics.

## Dependencies and Integration Points
It is included by `main.cpp`, `tab_general.cpp`, and `afs_config.h`, binding the Advanced tab into the application tab set and global apply path.

## Risks and Edge Cases
The commit hook returns success if the Advanced tab window does not exist, so hidden or uncreated tabs cannot block apply. That is intentional for modes where the tab is absent, but tests should verify no settings are silently skipped in NT mode.

## Test Signals
Compile coverage and a property-sheet smoke test that invokes `AdvancedTab_CommitChanges(TRUE/FALSE)` with tab present and absent are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.cpp

## Purpose
`tab_drives.cpp` implements the user drive-mapping tab and the advanced submount editor. It lets users view, activate/deactivate, add/edit/remove AFS drive mappings and manage named submounts.

## Important APIs, Types, and Functions
Main routines are `DrivesTab_DlgProc`, `DrivesTab_OnInitDialog`, `DrivesTab_FillList`, `DrivesTab_OnCheck`, `DrivesTab_EditMapping`, `DriveEdit_*`, `Submounts_*`, and `SubEdit_*`. It relies on `QueryDriveMapList`, `ActivateDriveMap`, `InactivateDriveMap`, `WriteDriveMappings`, `WriteActiveMap`, `AddSubMount`, `RemoveSubMount`, `DoMapShareChange`, and path/submount validators.

## Control Flow
Initialization loads current mappings into `g.Configuration.NetDrives` and renders mapped drives. Checking a row maps or unmaps the live drive and updates active-map persistence. Add/edit opens a drive editor, validates mount-root paths and submount names, unmaps old active mappings, maps the new target, updates the 26-entry map array, writes HKCU mappings, and refreshes. The Advanced button opens a submount property sheet whose apply rewrites all submount registry entries from the list.

## State and Persistence Behavior
User drive mappings persist under HKCU mappings and active-map keys. Machine submount definitions persist under HKLM. Live state is Windows network mappings. `g.Configuration.NetDrives` owns the current list and is freed/refilled during refreshes.

## Dependencies and Integration Points
This tab is conditionally added by `main.cpp` based on `ShowMountTab`. It integrates tightly with `drivemap.cpp`, General service state, LANA NetBIOS naming, and optional integrated-logon remapping.

## Risks and Edge Cases
The list check state is stored as item data but depends on external checklist/list behavior. Editing an active mapping unmaps first, so failure to activate the new mapping can leave no mapping. Submount apply removes all old submounts before adding new ones, making partial registry failures risky. Some string formatting uses ANSI buffers in TCHAR contexts.

## Test Signals
Tests should cover service stopped disabling controls, add/edit/remove of active and inactive mappings, persistent versus nonpersistent mappings, submount in-use deletion prevention, submount rename, registry rewrite failure, and integrated-logon `DoMapShareChange` invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.h

## Purpose
`tab_drives.h` declares the drive-mapping tab dialog procedure.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK DrivesTab_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

## Control Flow
`main.cpp` registers this procedure as the Drives property-sheet page when the mount tab is enabled. All drive and submount workflows are handled inside `tab_drives.cpp`.

## State and Persistence Behavior
The header has no state. Implementation state is stored in `g.Configuration.NetDrives`, HKCU/HKLM mapping registry keys, and live WNet/DOS-device mappings.

## Dependencies and Integration Points
It is included by `main.cpp` and `afs_config.h`. Its presence in the central header makes the Drives tab available to other modules through the property-sheet framework.

## Risks and Edge Cases
The small header is low risk; the main risk is that consumers have no commit function analogous to other tabs, because mapping changes are applied immediately from the tab rather than on property-sheet apply.

## Test Signals
Compile coverage and UI smoke tests confirming `DrivesTab_DlgProc` receives initialization/command/help messages are sufficient for the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.cpp

## Purpose
`tab_general.cpp` implements the General tab: service status/start/stop, cell and gateway settings, integrated logon authentication, tray icon preference, validation, restart prompts, and status polling.

## Important APIs, Types, and Functions
Key routines include `GeneralTab_DlgProc`, `GeneralTab_OnInitDialog`, `GeneralTab_VerifyCell`, `GeneralTab_OnApply`, `GeneralTab_OnRefresh`, `GeneralTab_OnTimer`, `GeneralTab_OnStartStop`, `GeneralTab_AskIfStopped`, `GeneralTab_DoStartStop`, `fIsCellInCellServDB`, and `Status_DlgProc`.

## Control Flow
Initialization starts a refresh timer and loads current configuration. Apply first commits Hosts and Advanced tabs, validates gateway/cell state, writes changed cell/logon/tray/gateway values, and for Win9x gateway changes contacts the gateway and fixes drive mappings. The timer polls service state, opens/closes a modeless starting/stopping dialog, refreshes all tabs on state changes, and calls `TestAndDoMapShare` for drive remapping after service start. Start/stop commits config as needed and controls `TransarcAFSDaemon` through SCM.

## State and Persistence Behavior
The file tracks transient service UI state in a static `l` struct. Persistent state includes registry-backed cell/gateway/logon/tray settings and service state outside the process. `g.fNeedRestart` controls restart prompts after changes requiring AFSD restart.

## Dependencies and Integration Points
It integrates with `Config_*`, `HostsTab_CommitChanges`, `AdvancedTab_CommitChanges`, CellServDB/DNS cell validation, Windows SCM, drive-map logon hooks, and Control Center mode.

## Risks and Edge Cases
Cell-name conversion assumes ASCII. `fIsCellInCellServDB` has an unused `done:` label and combines registry, file, and DNS lookup with different failure semantics. Start/stop operations set warning flags and then rely on timer polling rather than synchronous service-state waits. Partial commits in Hosts/Advanced can persist before General validation fails.

## Test Signals
Tests should cover valid/invalid cells from registry, CellServDB and DNS; admin versus non-admin UI gating; start, stop, restart, and failure paths; gateway contact on non-NT mode; integrated logon flag persistence; and restart prompt behavior after advanced changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.h

## Purpose
`tab_general.h` declares the General tab dialog procedure.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK GeneralTab_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

## Control Flow
`main.cpp` registers this procedure as the first tab for normal client configuration mode. The implementation handles initialization, apply, refresh, service control, and help messages.

## State and Persistence Behavior
The header has no state. Implementation state spans `g.Configuration`, `g.fNeedRestart`, service status polling, and registry-backed settings.

## Dependencies and Integration Points
It is included by `main.cpp` and `afs_config.h`, placing the General tab in the central UI contract.

## Risks and Edge Cases
The header is low risk. Because there is no separate public commit function, other tabs do not force General changes; instead the property sheet sends `IDAPPLY` to the tab.

## Test Signals
Compile coverage and property-sheet smoke tests for `GeneralTab_DlgProc` are sufficient at the header level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.cpp

## Purpose
`tab_hosts.cpp` implements the Cells/Hosts tab for viewing and editing CellServDB cell entries and their database servers. In Control Center mode it also validates and persists the default cell.

## Important APIs, Types, and Functions
Main routines are `HostsTab_DlgProc`, `HostsTab_OnInitDialog`, `HostsTab_CommitChanges`, `HostsTab_OnApply`, `HostsTab_FillList`, `HostsTab_OnAdd/Edit/Remove`, `CellEdit_*`, `ServerEdit_*`, and `TextToAddr`.

## Control Flow
Initialization reads CellServDB once into `g.Configuration.CellServDB` and fills a fastlist with cell lines. Add/edit opens a cell property sheet; server add/edit resolves addresses or names and stores formatted CellServDB lines; cell apply replaces the cell line and following server entries in the in-memory list. Hosts apply writes the file and, in Control Center mode, validates/persists the default cell.

## State and Persistence Behavior
CellServDB edits are staged in memory until `CSDB_WriteFile` during apply. Cell edit dialogs use temporary copied `CELLDBLINE` entries in list item params and free them on destroy. Control Center default cell persists through `Config_SetCellName`.

## Dependencies and Integration Points
The General tab calls `HostsTab_CommitChanges` before applying service settings. Cell validation uses `cm_SearchCellRegistry`, `CSDB_FindCell`, and `cm_SearchCellByDNS`. Server editing uses Winsock DNS and the custom sockaddr control.

## Risks and Edge Cases
Server dialog specific-address mode overwrites the comment with the numeric address before lookup, losing user-entered comments. `CellEdit_SortFunction` stores order in `pNext` cast to an integer, reusing a linked-list field as UI metadata. `TextToAddr` rejects `inet_addr` result zero, which can reject valid `0.0.0.0`, and uses legacy `gethostby*` APIs.

## Test Signals
Tests should cover reading/writing CellServDB, add/edit/remove cells, multiple server ordering, DNS success/failure, Control Center default-cell validation through registry/file/DNS, cancellation without file writes, and comments/linked-cell preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.h

## Purpose
`tab_hosts.h` declares the Hosts tab dialog procedure and commit hook.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK HostsTab_DlgProc(HWND, UINT, WPARAM, LPARAM)` and `BOOL HostsTab_CommitChanges(BOOL fForce)`.

## Control Flow
The property sheet uses the dialog procedure. General tab apply/start logic calls `HostsTab_CommitChanges` to flush CellServDB edits before validating the configured cell or starting the service.

## State and Persistence Behavior
The header has no state. Implementation state lives in `g.Configuration.CellServDB` until committed to disk.

## Dependencies and Integration Points
It is included by `afs_config.h`, `main.cpp`, and `tab_general.cpp`. The commit hook is part of the cross-tab apply order.

## Risks and Edge Cases
If the Hosts tab window is absent, `HostsTab_CommitChanges` returns success, which is needed for modes without the tab but can hide skipped writes if tab creation fails unexpectedly.

## Test Signals
Compile coverage plus property-sheet tests with the Hosts tab present and absent should verify commit behavior and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.cpp -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.cpp

## Purpose
`tab_prefs.cpp` implements the Server Preferences tab for viewing, importing, adding, editing, ranking, and applying file-server and VL-server preferences.

## Important APIs, Types, and Functions
Key routines are `PrefsTab_DlgProc`, `PrefsTab_OnInitDialog`, `PrefsTab_CommitChanges`, `PrefsTab_OnApply`, `PrefsTab_OnRefresh`, `PrefsTab_OnFillList`, `PrefsTab_OnUpDown`, `PrefsTab_OnAdd/Edit/Import`, `PrefsTab_MergeServerPrefs`, `PrefsTab_AddItem`, refresh/name-resolution thread routines, sort/hash callbacks, and `PrefsEdit_*`.

## Control Flow
Initialization sets list columns and starts refresh. Refresh spawns a thread that retrieves server preferences through `Config_GetServerPrefs`, merges new values into `g.Configuration`, fills the list, starts a background reverse-DNS thread, and enables controls based on service state. Users can switch between FS/VL lists, adjust ranks, add/edit servers, or import text files containing server/rank pairs. Apply sends changed preferences back through `Config_SetServerPrefs`.

## State and Persistence Behavior
`g.Configuration.pFServers` and `pVLServers` hold mutable preference arrays. `SERVERPREF.fChanged` marks entries to send on apply; `g.Configuration.fChangedPrefs` gates apply. Background thread state is guarded by a critical section in static `l`.

## Dependencies and Integration Points
The tab integrates with `config.cpp` pioctl server-pref APIs, Winsock DNS, custom fastlist/spinner controls, the hashlist utility for merging, and General tab commit ordering through `PrefsTab_CommitChanges`.

## Risks and Edge Cases
Thread cancellation appears inverted: setting `*pfStopFlag = FALSE` when a thread is active does not request stop if the worker exits on true. `PrefsTab_MergeServerPrefs` copies `sizeof(SERVERPREFS)` into a `SERVERPREF` slot, which is likely a memory-corrupting bug. Threads update UI controls directly from worker threads, a Win32 threading risk. Import allocates `sizeof(TCHAR) * (cbLength + 2)` for byte length and reads bytes into a TCHAR buffer, unsafe for Unicode.

## Test Signals
Tests should cover stopped-service disabling, pioctl refresh/apply, FS/VL switching, rank changes and sorting, add/edit duplicate handling, import parsing, merge de-duplication, background reverse-DNS updates, and thread cancellation/race behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.h -->
# sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.h

## Purpose
`tab_prefs.h` declares the Server Preferences tab dialog procedure and commit hook.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK PrefsTab_DlgProc(HWND, UINT, WPARAM, LPARAM)` and `BOOL PrefsTab_CommitChanges(BOOL fForce)`.

## Control Flow
`main.cpp` registers the dialog procedure on NT systems. General or property-sheet apply paths can use the commit function to force pending preference changes to be sent to the cache manager.

## State and Persistence Behavior
The header has no state. Implementation state is in `g.Configuration.pFServers`, `g.Configuration.pVLServers`, `g.Configuration.fChangedPrefs`, and worker-thread statics.

## Dependencies and Integration Points
It is included by `main.cpp` and `afs_config.h`. It completes the cross-tab commit model along with Hosts and Advanced.

## Risks and Edge Cases
The commit hook succeeds if the tab is absent. This is appropriate for non-NT modes but means missing tab creation will skip preference application.

## Test Signals
Compile coverage and property-sheet tests should verify `PrefsTab_CommitChanges` behavior with no tab, unchanged preferences, changed preferences, and failed `Config_SetServerPrefs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.h -->
