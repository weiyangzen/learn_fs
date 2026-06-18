# Research: subset-b-007731

Grouped research for OpenAFS `src/WINNT/afssvrcfg` server configuration UI sources. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.cpp

Purpose: Implements the Windows OpenAFS server configuration program entry point, wizard/property-sheet startup, global configuration state initialization, admin-library handle management, common wizard behavior, and `CFG_DATA` string accessors.

Important APIs/types/functions: `WinMain` loads locale resources, initializes AFS client admin libraries, opens `afs_server_config_log.txt`, starts Winsock, discovers local host names, calls `GetCurrentConfig`, then launches either `RunWizard` or `RunCfgTool`. `WizStep_Common_DlgProc` centralizes help, title bolding, graphic redraw, and cancel handling. `QueryCancelWiz` hides the wizard after confirmation. `GetLibHandles` and `GetHandles` open/upgrade `afsclient` cell/token handles plus `cfg_HostOpen` handles for the local client and target server. Accessors such as `GetCellNameA`, `GetAdminPWA`, and `GetClientNetbiosNameA` convert `g_CfgData` fields for C admin APIs.

Control flow: Startup reads current client/server state before any UI so later pages can show already-configured, disabled, or required choices. Command-line text containing `wizard` selects the wizard; otherwise the configuration manager property sheet is attempted, with fallback prompts to run the wizard when client/server info is invalid. `GetLibHandles` first keeps a cached null client cell/host handle, then chooses a standard authenticated, standard unauthenticated, or null server cell handle depending on client validity, target cell, first-server status, auth-server availability, and admin credentials.

State and persistence: Defines process globals `g_pWiz`, `g_pSheet`, `g_CfgData`, `g_hToken`, `g_hCell`, `g_hClient`, `g_hServer`, `g_LogFile`, and a cached `hClientCell`. Durable writes are indirect: the log file under `AFSDIR_SERVER_LOGS_DIRPATH` and later cfg/admin calls. ANSI accessor functions return static buffers, so results are overwritten on subsequent calls.

Dependencies and integration points: Integrates Win32, Winsock, `TaLocale`, `WINNT/afsapplib`, OpenAFS cfg/client admin APIs, `lanahelper` for NetBIOS names, wizard/property-sheet helpers, resource IDs, current-config discovery, partition utilities, logging, validation, and graphics.

Risks: Global mutable handles and static conversion buffers are not thread-safe, yet configuration and salvage use worker threads. `CloseLibHandles(FALSE)` leaves client handles cached, so errors after partial opens may keep old client state. Password fields live in `g_CfgData` and static ANSI buffers. `_strlwr(pszCmdLineA)` mutates the command-line buffer. String copies rely on fixed-size buffers and legacy `lstrncpy` behavior.

Test signals: Exercise wizard and property-sheet modes, invalid client/server fallbacks, first-server and existing-cell handle selection, authenticated and unauthenticated token paths, failed DNS/hostname lookup, failed admin-library init, cancel confirmation, repeated handle upgrades, and log-file open failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.h

Purpose: Central application header for the AFS server configuration UI. It declares wizard step IDs, configuration-state flags, size limits, the `CFG_DATA` state structure, global handles, logging objects, and string accessor APIs.

Important APIs/types/functions: `StateID` enumerates the twelve wizard pages. `CONFIG_STATE` combines mutually exclusive states (`CS_NULL`, `CS_DONT_CONFIGURE`, `CS_CONFIGURE`, `CS_ALREADY_CONFIGURED`, `CS_UNCONFIGURE`) with the `CS_DISABLED` flag. `CFG_DATA` stores all choices and discovered state: server roles, root volume IDs/existence/replication flags, partition selection, system-control machine, cell/admin credentials, local and client host/cell information, reuse/login flags, and salvage thread/log state. The header declares `WizStep_Common_DlgProc`, `QueryCancelWiz`, `GetLibHandles`, `GetHandles`, and TCHAR/ANSI accessors.

Control flow: No runtime implementation, but it defines the shared contract every page follows: pages mutate `g_CfgData` state bits and text fields, and the final configuration page consumes them to assemble executable steps.

State and persistence: `CFG_DATA` is process-local and centralizes transient wizard/config-manager state. Some fields mirror durable AFS state discovered or written by cfg/vos/bos APIs, but the struct itself is not persisted. Admin and server passwords are kept in memory.

Dependencies and integration points: Includes OpenAFS cfg/util admin headers, `WINNT/afsapplib`, TCHAR/CRT debug support, hourglass/toolbox/logging/conversion/validation helpers, and `cfg_utils.h` after `CONFIG_STATE` is defined.

Risks: All modules share one global mutable state object with no ownership boundaries. Fixed-size credential and name buffers can truncate inputs. The state constants are integer flags, so equality checks can accidentally ignore or mishandle `CS_DISABLED` when combined with another state.

Test signals: Compile all pages against this contract; verify each page updates the expected `CFG_DATA` fields; test disabled-state combinations; validate boundary-length cell, machine, partition, admin, and password values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/backup_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/backup_server_page.cpp

Purpose: Implements the wizard page that lets the user configure or skip the Backup Server component.

Important APIs/functions: `BackupPageDlgProc` handles page initialization, Next/Back navigation, and radio-button changes. `OnInitDialog` sets wizard buttons and decides whether the backup option is selectable. `CantBackup` replaces the options with an explanatory message. `CalcOptionButtonSeparationHeight` exposes `nOptionButtonSeparationHeight` for the system-control page layout.

Control flow: The page moves forward to the partition page and back to the database page. On init, an already-configured backup server or a machine not configured/configuring as a database server hides the choice. Otherwise, it restores the `CS_DONT_CONFIGURE` or `CS_CONFIGURE` choice from `g_CfgData.configBak`.

State and persistence: Mutates only `g_CfgData.configBak` and its disabled bit. No durable writes occur; the final configuration page later starts backup-related database servers based on this flag.

Dependencies and integration points: Uses common wizard handling, `ConfiguredOrConfiguring`, `EnableStep`, resource strings, and UI helpers from the application library/toolbox. The global option-spacing value is consumed by `sys_control_page.cpp`.

Risks: The page returns `FALSE` when the common dialog proc returns true, following the local pattern but making message consumption subtle. If database state changes on prior pages, backup can be disabled and the previous selected state remains under the `CS_DISABLED` bit.

Test signals: Test already-configured backup, no database server, database configured/configuring, toggling both radio buttons, forward/back navigation, and repeated visits after database selection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/backup_server_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.cpp

Purpose: Provides shared helpers for interpreting configuration-state flags, redrawing the wizard graphic, resolving the current application title resource, logging admin-library errors, and showing standard error/warning UI.

Important APIs/functions: `IsStepEnabled`, `EnableStep`, `ShouldConfig`, `DontConfig`, `ShouldUnconfig`, `ConfiguredOrConfiguring`, `Configured`, and `ToggleConfig` wrap raw `CONFIG_STATE` tests. `RedrawGraphic` invalidates the wizard left pane. `GetAppTitleID` chooses wizard vs config-manager title. `GetAdminLibErrorCodeMessage`, `LogError`, `ShowError`, and `ShowWarning` connect OpenAFS error translation, the global log, and UI messages.

Control flow: Page code uses the state predicates to decide availability and later the config page uses `Should*` to build steps. Error display logs the raw/translated status, shows an `ErrorDialog`, and updates `IDC_STATUS_MSG` when a dialog handle is supplied.

State and persistence: Mutates only the disabled bit passed by reference. Persists diagnostic information via `g_LogFile`.

Dependencies and integration points: Relies on `g_pWiz`, `g_CfgData`, `g_LogFile`, `util_AdminErrorCodeTranslate`, localized resource strings, and app-library `ErrorDialog`/`MessageBox` helpers.

Risks: Predicate functions use equality rather than masking disabled state, so a disabled step combined with `CS_CONFIGURE` will not be considered configurable by `ShouldConfig`. `ShowError` blindly writes `IDC_STATUS_MSG`, which may not exist on every caller dialog. `GetAdminLibErrorCodeMessage` returns an admin-library-owned string whose lifetime depends on the utility API.

Test signals: Unit-check every state combination with and without `CS_DISABLED`; verify warnings and errors on wizard/config-manager dialogs; test error translation success/failure and absent status controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.h

Purpose: Declares the shared configuration-state and UI/error helper functions implemented by `cfg_utils.cpp`.

Important APIs/functions: Exposes state predicates/mutators, `RedrawGraphic`, `GetAppTitleID`, admin-error translation, logging, and standard error/warning dialogs.

Control flow: No runtime logic; the header is included after `CONFIG_STATE` is defined in `afscfg.h`, making include order part of the contract.

State and persistence: No local state. Functions declared here operate on passed state references and process globals.

Dependencies and integration points: Depends on `CONFIG_STATE`, `afs_status_t`, Win32 `HWND`, and resource-driven UI conventions in the server configuration app.

Risks: Header guard name `_WIZ_UTILS_H_` does not match the filename and could collide with older wizard utility code. Callers can still bypass helpers and compare raw flags inconsistently.

Test signals: Compile all wizard/config pages through `afscfg.h`; verify no direct include before `CONFIG_STATE` exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.cpp

Purpose: Implements RAII-style wrappers for converting between TCHAR strings and ANSI `char *` strings used by legacy OpenAFS admin APIs.

Important APIs/functions: `S2A::S2A` calls `StringToAnsi`; `S2A::~S2A` frees only in UNICODE builds. `A2S::A2S` calls `AnsiToString`; `A2S::~A2S` similarly frees only when conversion allocation is expected.

Control flow: Instances are typically temporary objects cast implicitly to `char *`, `const char *`, `LPTSTR`, or `LPCTSTR` at call sites.

State and persistence: Per-object pointer ownership only. No durable state.

Dependencies and integration points: Uses app-library conversion and allocation helpers from `WINNT/afsapplib`. Used throughout cfg, partition, salvage, and logging UI paths when bridging Win32 TCHAR controls to AFS C APIs.

Risks: Implicit pointer casts make lifetime easy to misuse if a callee stores the converted pointer beyond the temporary expression. Destructors only free in UNICODE builds, relying on app-library behavior in ANSI builds. Null input handling is delegated to the app-library conversion routines.

Test signals: Compile/test ANSI and UNICODE builds, temporary use inside function calls, null/empty strings, and long fixed-buffer inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.h

Purpose: Declares `S2A` and `A2S`, small conversion helper classes that make TCHAR/ANSI bridging concise.

Important APIs/types: `S2A` stores a converted `char *` and exposes casts to mutable/const ANSI pointers. `A2S` stores a converted `LPTSTR` and exposes TCHAR pointer casts.

Control flow: No active logic beyond constructors/destructors implemented in `char_conv.cpp`; callers instantiate objects at the point of API calls.

State and persistence: Object-local converted pointer only, no persistence.

Dependencies and integration points: Requires Win32/TCHAR types and app-library allocation semantics. Used by code that talks to OpenAFS admin APIs and Win32 UI helpers.

Risks: Mutable pointer casts allow callees to write into conversion buffers of unclear size. Temporary lifetime hazards are hidden by implicit operators.

Test signals: Static review for stored `S2A`/`A2S` pointers, build both character modes, and test conversions of non-ASCII cell/admin names if Unicode builds are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config.h

Purpose: Defines the execution-state enum used by the configuration progress UI.

Important APIs/types: `STEP_STATE` values are `SS_STEP_TO_BE_DONE`, `SS_STEP_IN_PROGRESS`, `SS_STEP_FINISHED`, and `SS_STEP_FAILED`.

Control flow: No runtime logic. The enum values are consumed by `config_server_page.cpp` and `graphics.cpp` to track and render progress.

State and persistence: None.

Dependencies and integration points: Included by graphics and final configuration code.

Risks: Minimal; adding enum values requires updating `PaintStepGraphic`.

Test signals: Compile-time coverage and visual verification for each rendered step state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config_server_page.cpp

Purpose: Implements the final wizard/config-manager page that converts selected `CFG_DATA` state into an ordered sequence of OpenAFS server configuration or unconfiguration operations and runs them on a background thread with progress UI.

Important APIs/functions: `Configure` shows the modal config dialog for the config manager. `ConfigServerPageDlgProc` handles Configure/Back/Cancel/View Log. Step assembly is handled by `GetStepsToPerform`, `AddSteps`, `SetupStepGUI`, and `SetupConfigSteps`. `ConfigServer` runs each `CONFIG_STEP`. Operation functions include `ConfigPartition`, `DefineCellForServer`, `DefineCellForClient`, `StartBosServer`, `StartAuthServer`, `CreatePrincipalAndKey`, `StartDbServers`, `CreateAdminPrincipal`, `StartFsVlAndSalvager`, `ConfigSCS`, `ConfigSCC`, root volume creation/mount/ACL helpers, `Replicate`, `EnableAuthChecking`, `UpgradeLibHandles`, `UpdateCellServDB`, unconfiguration helpers, `RestartAllDbServers`, and `PostConfig`.

Control flow: Initialization resets per-run globals, shows the cell title, detects nothing-to-do cases, builds a step list based on first-server mode, invalid client/server info, unconfiguration choices, partition/database/backup/file/root/replication/system-control choices, and post-config requirements. `OnConfig` optionally warns about changing the client cell, then spawns `ConfigServer`. The worker disables wizard buttons, shows progress, marks displayed steps in progress/finished/failed, calls each step function, checks cancellation between steps, closes vos handles, shows success/cancel/failure state, exposes View Log on failure, and unmaps a temporary AFS drive mapping at the end.

State and persistence: Uses many static per-run variables for progress, cancellation, vos/bos/cell-servdb handles, root volume IDs, temporary drive mapping, and flags indicating whether root volumes were created. Durable changes are made via cfg/vos/bos/client APIs: server/client cell membership, bos/auth/db/backup/file/update services, partition-table entries, CellServDB propagation, root volumes, ACLs, mount points, replication sites/releases, auth checking, service shutdowns, and host invalidation. The log file records every major operation.

Dependencies and integration points: Integrates OpenAFS cfg, vos, bos, client, pioctl, registry, volser, SMB IOC, and dirpath APIs; Win32 threading/events/critical sections/progress controls/network-drive mapping; `get_pw_dlg` for AFS principal password retry; `get_cur_config` for root-volume checks; app-library conversion and UI helpers; `graphics.cpp` step painting.

Risks: Worker thread directly updates UI controls from a non-UI thread. Global/static state is not protected except for a small CellServDB callback counter. Cancellation is cooperative and checked only between selected operations. Some handles/events/critical sections are cleaned on success paths but can leak or be left inconsistent on early failure. Passwords and tokens remain in process globals. `DefineCellForServer/Client` appends an embedded NUL to `g_CfgData.szHostname` using `MAX_PARTITION_NAME_LEN`, which is suspicious and mutates a hostname field used elsewhere. `FreeCellServDB` calls `CHECK_RESULT` without setting `m_nResult`. Root volume creation has a known TODO when `root.afs` exists but `root.cell` does not. Drive mapping scans Z-to-D and prompts repeatedly. CellServDB update errors may be logged but `m_szCellServDbUpdateErrMsg` is not clearly surfaced.

Test signals: Integration-test first-server setup, joining an existing cell, invalid client info repair, invalid server info repair, partition-only changes, db+backup combined startup, backup-only startup, unconfiguring each service, last-DB-server shutdown, root volume creation with/without freelance client mode, ACL/mount creation, replication of one or both root volumes, CellServDB callback timeout/failure, user cancellation, failed credential/password retry, and log viewing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config_server_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.cpp

Purpose: Implements the config-manager modal dialog for adding AFS partition-table entries from an available drive list.

Important APIs/functions: `CreatePartition` opens `IDD_CREATE_PARTITION` and returns whether a partition was added. `DlgProc` handles help, create/close, drive selection, name edits, activation refresh, notifications, and resizing. `OnCreate` validates the partition name, constructs `?:` device and `/vicepX` partition strings, checks duplicates with `DoesPartitionExist`, and calls `cfg_HostPartitionTableAddEntry`.

Control flow: Init wires resize behavior and drive-list setup. Selecting a non-AFS drive auto-fills a one-letter partition suffix when the user has not typed a name. Create is enabled only when a drive and partition name exist. After successful creation, the dialog remains open with the name field cleared and `bCreated` set.

State and persistence: Uses static dialog state for selected item, auto-name flag, current buffers, and `bCreated`. Durable state is the host partition table entry written through the cfg library; the file server must later restart/export it.

Dependencies and integration points: Uses FastList drive-list helpers from `volume_utils`, `partition_utils` cached table checks, validation helpers, resource strings, and `g_hServer`/`g_LogFile`.

Risks: `GetWindowText` size arguments use character counts inconsistently with buffer byte sizes. Duplicate checking compares a constructed `/vicep` name through `A2S`, while auto-fill checks `viceX`, so naming conventions must stay aligned. The dialog does not refresh the cached partition table after adding, so repeated duplicate checks may depend on external refresh.

Test signals: Test empty/no-drive disabled state, auto-name behavior, duplicate partition names, invalid names, successful add, activation-time drive refresh, resize behavior, and cfg API failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.h

Purpose: Declares the modal partition-creation entry point.

Important APIs/functions: `CreatePartition(HWND hParent)` returns true when the dialog successfully added at least one partition.

Control flow: No implementation logic; consumers call it from the partitions property page and refresh their lists on true.

State and persistence: None in the header. Implementation writes host partition table entries.

Dependencies and integration points: Requires Win32 `HWND`; included by `partitions_page.cpp`.

Risks: The boolean return only indicates at least one successful add, not which partition was added or whether the cached partition table was refreshed.

Test signals: Verify callers refresh partition displays after true and handle false without assuming failure vs cancel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/db_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/db_server_page.cpp

Purpose: Implements the wizard page for configuring or skipping this host as a database server and collecting a System Control Machine hostname for CellServDB propagation.

Important APIs/functions: `DBServerPageDlgProc`, `OnInitDialog`, `ConfigMsg`, `EnableSCM`, `ShowPageInfo`, and `SavePageInfo`.

Control flow: First-server mode forces database configuration and hides choices. Otherwise, the page restores the database selection, enables the SCM edit field only when configuring DB service, saves the SCM field on Next/Back, and navigates between file-server and backup-server pages.

State and persistence: Mutates `g_CfgData.configDB` and `g_CfgData.szSysControlMachine`. No durable writes occur until the final config step starts database services and possibly updates CellServDB through that SCM.

Dependencies and integration points: Uses common wizard handling, UI helpers, resource strings, and `CFG_DATA` shared state. The final config page consumes the DB flag to choose db/bak and CellServDB restart steps.

Risks: No validation is performed on the SCM hostname here. First-server mode returns early without showing existing page info. Disabling the SCM field does not clear stale `szSysControlMachine`.

Test signals: Test first-server forced mode, already-configured mode, configure/don't configure toggles, SCM enable/disable and persistence, and navigation preserving edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/db_server_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/file_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/file_server_page.cpp

Purpose: Implements the wizard page for choosing whether this host should be a file server.

Important APIs/functions: `FileServerPageDlgProc`, `OnInitDialog`, and `ConfigMsg`.

Control flow: First-server mode forces file-server configuration. Already-configured file servers show a message instead of options. Otherwise radio buttons set `g_CfgData.configFS` and navigation moves between admin info and database pages.

State and persistence: Mutates `g_CfgData.configFS` only. Final configuration later starts or stops file-server-related bos processes based on this state.

Dependencies and integration points: Uses common wizard handler, resource strings, and global wizard/config state. Partition and root-volume pages depend on file-server state to enable their options.

Risks: Stale downstream choices may remain selected when file-server selection changes; later pages mask some of this through disabled flags. No validation beyond first-server forcing.

Test signals: Test first-server forced mode, already-configured message, radio toggles, downstream partition enablement, and forward/back navigation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/file_server_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.cpp

Purpose: Discovers the machine's current AFS client/server configuration before showing the wizard or config manager and populates `g_CfgData` with existing role, partition, root-volume, replication, and cell state.

Important APIs/functions: `GetCurrentConfig` drives a `PROGRESSDISPLAY` around `GetCurrentConfigState`. Checks include `IsClientConfigured`, `IsConfigInfoValid`, `StartBosServer`, `DoesAPartitionExist`, `IsFSConfigured`, `IsDBConfigured`, `IsBakConfigured`, `AreWeLastDBServer`, `DoRootVolumesExist`, `AreRootVolumesReplicated`, `IsSCSConfigured`, and `IsSCCConfigured`. `CheckConfigState` maps boolean checks to `CS_ALREADY_CONFIGURED` or `CS_NULL`.

Control flow: The scanner verifies the client is installed/configured, reads host config status and cell name, pre-fills `szCellServDbHostname` when client/server cells differ, opens cfg handles, reads partitions, and if server config is valid starts bosserver if necessary so service state can be queried. Root volume existence and replication are read from VLDB entries and stored for later wizard decisions.

State and persistence: Populates many `g_CfgData` fields, including valid client/server flags, client cell/version, server cell, partition name/device, service config states, last-DB-server flag, root volume IDs, existence flags, and replication flags. It may persistently start bosserver as a side effect. Progress/cancel state is static process-local.

Dependencies and integration points: Uses OpenAFS cfg, vos, VLDB constants, partition utilities, `PROGRESSDISPLAY`, app-library animation, logging, and global cfg handles. Root-volume helper functions are exported for the final config page to refresh unknown status.

Risks: Service discovery can mutate the system by starting bosserver. `NextStep` uses a static `nCurStep` that is not reset in `GetCurrentConfig`, so repeated runs may over-advance progress. `AreRootVolumesReplicated` assumes VLDB entries were populated by prior `DoRootVolumesExist`; missing volumes can leave default entries. Allocated strings from cfg enumeration/query are not consistently deallocated. Cancellation relies on shared booleans without synchronization.

Test signals: Test installed/uninstalled client, invalid client, invalid server, valid server with stopped bosserver, no partitions, multiple partitions, fs/db/bak/scs/scc configured combinations, last DB server detection, missing root volumes, one root volume missing, replicated/unreplicated sites, client/server cell mismatch, and cancel during scan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.h

Purpose: Declares current-configuration discovery entry points and root-volume helper checks.

Important APIs/functions: `GetCurrentConfig(HWND, BOOL&)`, `DoRootVolumesExist(BOOL&)`, and `AreRootVolumesReplicated(BOOL&)`.

Control flow: No header logic. The final configuration page uses the root-volume helpers when startup could not determine status.

State and persistence: Functions declared here mutate `g_CfgData` in implementation and may query/start server components.

Dependencies and integration points: Requires `afs_status_t`, Win32 types, and the global configuration environment from `afscfg.h`.

Risks: Function names imply pure queries, but implementation has side effects and depends on initialized global handles.

Test signals: Verify callers only invoke root-volume checks after `g_hCell`/vos context is available and handle nonzero AFS statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.cpp

Purpose: Provides a small password prompt used when setting the AFS server principal requires the current AFS principal password.

Important APIs/functions: `GetAfsPrincipalPassword` displays `IDD_GET_PW` and returns a pointer to `g_CfgData.szServerPW` on OK. `GetPwDlgProc`, `CheckEnableButtons`, and `SaveDlgInfo` implement the dialog behavior.

Control flow: The final config page calls this from `CreatePrincipalAndKey` when cfg reports invalid/missing AFS password/key. The dialog enables OK only when the password field is non-empty and saves the value into global config data.

State and persistence: Mutates `g_CfgData.szServerPW`; no durable writes directly. The password is then passed to cfg APIs and remains in process memory.

Dependencies and integration points: Uses app-library help, modal dialog helpers, resource IDs, and fixed-size credential limits from `afscfg.h`.

Risks: `ShowPageInfo` is defined but not called, so existing password state is not prefilled. Returning a pointer to global password storage exposes mutable shared state. Password length is truncated by `lstrncpy` and not cleared after use.

Test signals: Test empty password disabling, OK/cancel return values, retry loop integration from `CreatePrincipalAndKey`, max-length password input, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.h

Purpose: Declares the AFS principal password prompt.

Important APIs/functions: `GetAfsPrincipalPassword(HWND hParent, TCHAR *&pszServerPW)` returns true and points the output reference at the stored server password on success.

Control flow: No implementation logic; intended for password retry paths in final configuration.

State and persistence: Implementation writes `g_CfgData.szServerPW`.

Dependencies and integration points: Requires Win32/TCHAR types and is included by `config_server_page.cpp`.

Risks: API exposes pointer lifetime tied to global config state instead of returning a copied secure string.

Test signals: Verify callers handle false by cancelling the operation and do not retain the pointer after global state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.cpp

Purpose: Draws wizard progress graphics: per-step state icons in the final configuration page and the custom left-pane wizard progress bar/arrow/text.

Important APIs/functions: `PaintStepGraphic` paints a blue/green dot, checkmark, or red X based on `STEP_STATE`. `PaintPageGraphic` renders the left-pane current-step label, progress bar, arrow, and current page description. Static helpers erase rectangles and draw each icon.

Control flow: `config_server_page.cpp` subclasses static controls to call `PaintStepGraphic` during `WM_PAINT`. `afscfg.cpp` registers `PaintPageGraphic` as the wizard graphic callback, so it runs whenever the wizard left pane repaints.

State and persistence: Uses static GDI pens/fonts in `PaintPageGraphic` for process lifetime. No persistent state.

Dependencies and integration points: Depends on Win32 GDI, `STEP_STATE`, `g_pWiz`, `g_nNumStates`, `g_StateDesc`, resource strings, and app-library font creation.

Risks: Static GDI objects are never destroyed. Drawing assumes `g_pWiz` and state indexes are valid. Color constants are raw BGR `COLORREF` values and comments may be confusing. Manual pixel drawing is brittle under high DPI/themes.

Test signals: Visual-test all step states, every wizard page index, resize/repaint behavior, high-DPI display, and repeated wizard open/close for GDI object growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.h

Purpose: Declares drawing hooks for wizard and configuration progress UI.

Important APIs/functions: `PaintStepGraphic(HWND, STEP_STATE)` and `PaintPageGraphic(LPWIZARD, HDC, LPRECT, HPALETTE)`.

Control flow: No implementation logic; functions are passed to subclass/callback mechanisms.

State and persistence: None in the header.

Dependencies and integration points: Includes `config.h` and requires wizard/app-library Win32 types.

Risks: Callers must provide valid paint contexts and a synchronized wizard state.

Test signals: Compile integration with wizard callback signatures and static-control subclass calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/help.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/help.cpp

Purpose: Registers WinHelp context mappings for all wizard pages, config-manager pages, and modal dialogs in the AFS server configuration UI.

Important APIs/functions: `RegisterWizardHelp` registers overview and control-level help for intro, info, file/db/backup/partition/root/replication/system-control/config pages and password prompt. `RegisterConfigToolHelp` registers help for partition creation, partitions/services pages, admin-info, password, salvage, and salvage-results dialogs. Static `IDH_*` values and `DWORD` arrays map resource control IDs to help topic IDs.

Control flow: `afscfg.cpp` calls the appropriate registration function before showing the wizard or property sheet. Dialog procedures then delegate `WM_HELP`/`IDHELP` handling to `AfsAppLib_HandleHelp`.

State and persistence: No durable state in this file; registrations populate app-library process-global help tables.

Dependencies and integration points: Depends on resource IDs and `WINNT/afsapplib` help registration. It must stay synchronized with dialog templates and localized help content.

Risks: Help IDs are hand-maintained static integers; mismatches are easy and not compile-checked. `IDD_CONFIG_SERVER_PAGE` is registered for wizard help, while the config-manager modal uses `IDD_CONFIG_SERVER`, so coverage depends on which dialog invokes app-library help. WinHelp is legacy.

Test signals: Press Help/F1 on every dialog/control, verify overview pages, verify config-manager vs wizard registrations, and check for stale control IDs after resource changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/help.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/hourglass.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/hourglass.h

Purpose: Defines a tiny RAII cursor helper that switches to a wait cursor while an object is in scope.

Important APIs/types: `HOURGLASS` constructor stores the current cursor and calls `SetCursor(LoadCursor(NULL, idCursor))`; destructor restores the previous cursor. `PHOURGLASS` is an alias pointer typedef.

Control flow: Stack allocation around slow UI operations temporarily changes the cursor.

State and persistence: Object-local previous cursor handle only. No persistence.

Dependencies and integration points: Uses Win32 cursor APIs. Included from `afscfg.h` and used by pages such as partition setup.

Risks: Cursor changes are thread/window-message sensitive; restoring a cursor saved before nested cursor changes can produce unexpected UI state. No error handling for `LoadCursor`.

Test signals: Test nested hourglass objects, exceptions/early returns, and use from UI thread only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/hourglass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info2_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info2_page.cpp

Purpose: Implements the second wizard information page, collecting admin credentials/UID for a new first server or admin credentials plus CellServDB host for joining an existing cell.

Important APIs/functions: `InfoPage2DlgProc`, `OnInitDialog`, `CheckEnableButtons`, `SavePageInfo`, `ShowPageInfo`, and `UseNextUid`. It uses `FIRST_SERVER_STEP` and `NOT_FIRST_SERVER_STEP` to disable the irrelevant wizard state dynamically.

Control flow: The page enables Next only when required fields are populated and password verification matches when visible. First-server mode collects admin name, password, password verification, and either next UID or explicit UID. Existing-cell mode collects admin name/password and a host name to fetch CellServDB. Next proceeds to file-server selection; Back returns to the first info page.

State and persistence: Writes `g_CfgData.szAdminName`, `szAdminPW`, `bUseNextUid`, `szAdminUID`, and `szCellServDbHostname`. No durable writes until final config creates/logs in with the admin principal.

Dependencies and integration points: Uses wizard state-disable notifications, spin control helpers, resource IDs, and global config state. Final config uses these credentials for token acquisition, admin principal creation, and CellServDB enumeration.

Risks: No explicit validation of hostname, UID range beyond spinner range, or admin name syntax here. Passwords are kept in global memory. `lstrncpy` may not guarantee null termination at maximum length.

Test signals: Test first-server and existing-cell page selection, password mismatch, empty fields, UID toggle/spinner boundaries, navigation persistence, and overlong admin/password/hostname input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info2_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info_page.cpp

Purpose: Implements the first wizard information page for choosing first-server vs existing-cell setup, entering the cell name, and setting/verifying the server principal password for a first server.

Important APIs/functions: `InfoPageDlgProc`, `OnInitDialog`, `CheckEnableButtons`, `SavePageInfo`, `ShowPageInfo`, and `IsFirstServer`.

Control flow: The page enables Next when a cell name exists and, for first-server mode, both server password fields are non-empty and match. First-server selection enables server-principal/password controls; existing-cell selection disables them. Next advances to the first-server admin page state, with the next page deciding which of its two templates is enabled.

State and persistence: Writes `g_CfgData.szCellName`, `szServerPW`, and `bFirstServer`. The server password is later used to create/set the AFS server principal key.

Dependencies and integration points: Uses common wizard handling, UI helpers, resource strings, and `CFG_DATA` limits. Later pages and final config depend heavily on `bFirstServer`.

Risks: Cell-name validation here only checks length/non-empty; syntax validation is not applied. Password truncation can make a verified UI password differ from stored value if over limit. The principal label/control is enabled but no principal value is saved in this file.

Test signals: Test first-server and existing-cell toggles, password mismatch, max-length cell/password input, empty cell, back/next persistence, and downstream page disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/intro_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/intro_page.cpp

Purpose: Implements the wizard introduction page.

Important APIs/functions: `IntroPageDlgProc` delegates common handling, initializes buttons, and moves to the first information page on Next. `OnInitDialog` enables only the Next button.

Control flow: This is a simple entry page with no validation or data capture.

State and persistence: No `g_CfgData` mutations and no durable writes.

Dependencies and integration points: Uses `WizStep_Common_DlgProc`, `g_pWiz`, and resource/template wiring.

Risks: Minimal. It relies on common wizard handling for cancel/help/graphic setup.

Test signals: Verify initial wizard state, Next navigation to `sidSTEP_TWO`, cancel behavior, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/intro_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.cpp

Purpose: Implements the `LOGFILE` class used by the configuration program to write timestamped diagnostics and translated AFS error details.

Important APIs/functions: Constructor/destructor manage `FILE *`. `Open` chooses overwrite/append mode, stores path, writes initial timestamp/open message. `Close` writes closing message. `Write` formats varargs entries and optionally timestamps each new line. `WriteError` formats caller text and translates an admin error code via `util_AdminErrorCodeTranslate`. `WriteMultistring` logs NUL-separated strings. `WriteBoolResult` logs Yes/No.

Control flow: Most operations early-return false when no file is open. `Write` maintains a static `bTimestampNextLine` so multiline entries are timestamped only at line starts.

State and persistence: Maintains the open file pointer, path, timestamp mode, and writes durable log text to disk. `Write`'s static timestamp flag is shared across all `LOGFILE` instances.

Dependencies and integration points: Uses C stdio/time helpers, Win32 types, OpenAFS utility error translation, `TaLocale_GetLanguage`, and is held globally as `g_LogFile`.

Risks: `strcpy(m_szPath, pszLogFilePath)` can overflow `MAX_PATH`. `Write` indexes `pszEntry[strlen(pszEntry)-1]`, which is invalid for an empty format string. The static timestamp flag is not per instance or thread-safe. `WriteMultistring` increments by `strlen(p)` instead of `strlen(p)+1`, causing the next loop to land on the NUL terminator and stop after the first string. Logging from worker/UI threads is unsynchronized.

Test signals: Test open/append/overwrite modes, long paths, empty writes, multiline timestamping, multiple instances, translated/untranslated errors, multistring with multiple hosts, and concurrent writes from config/salvage threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.h

Purpose: Declares `LOGFILE`, the small logging wrapper used across the server configuration application.

Important APIs/types: `LOGFILE_TIMESTAMP_MODE`, `LOGFILE_OPEN_MODE`, and methods `Open`, `Close`, `GetPath`, `Write`, `WriteError`, `WriteMultistring`, `WriteTimeStamp`, and `WriteBoolResult`.

Control flow: No implementation logic in the header; callers open once and then write diagnostics through the global `g_LogFile`.

State and persistence: Instances own a `FILE *`, path buffer, and timestamp mode; writes persist to the configured log path.

Dependencies and integration points: Includes Windows and stdio headers. Used by nearly every configuration, discovery, partition, and salvage path.

Risks: No copy-control declarations; accidental copying would duplicate a raw `FILE *`. Variadic methods provide no compile-time format checking.

Test signals: Compile with warnings for copy/use, verify global lifecycle in `WinMain`, and test destructor close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_page.cpp

Purpose: Implements the wizard page for choosing whether to create an initial AFS partition and selecting a drive/partition suffix.

Important APIs/functions: `PartitionPageDlgProc`, `WizardDlgProc`, `OnInitDialog`, `OnListSelection`, `OnPartitionName`, `SavePartitionInfo`, `ShowPartitionInfo`, `CheckEnableButtons`, `CantMakePartition`, and `MustMakePartition`.

Control flow: The page refreshes drive data when the wizard reactivates. It disables partition creation if a partition already exists or the host is not/will not be a file server. First-server mode forces partition creation. Selecting a non-AFS drive auto-fills a lower-case suffix while the user has not manually typed a name. Next validates the name and advances to root-volume choices.

State and persistence: Writes `g_CfgData.configPartition`, `szPartitionName`, and `chDeviceName`; no durable partition is created until the final config page runs `ConfigPartition`.

Dependencies and integration points: Uses drive-list helpers from `volume_utils`, partition utilities, validation, common wizard handling, FastList notifications, and `g_pWiz` subclass hooks.

Risks: Wizard subclass hook removal depends on receiving `WM_DESTROY_SHEET`; repeated visits may add duplicate hooks if not balanced. `GetWindowText` buffer sizes are close to the max and may truncate without clear feedback. Disabled state can hide stale selected device/name.

Test signals: Test no file-server dependency, already-created partition, first-server forced partition, drive refresh on activation, auto-name vs manual-name behavior, invalid names, empty drive/name button disabling, and forward/back persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.cpp

Purpose: Maintains a cached copy of the server partition table and provides simple lookup helpers.

Important APIs/functions: `ReadPartitionTable` calls `cfg_HostPartitionTableEnumerate` into static `pTable`/`cPartitions`. `GetPartitionTable`, `GetNumPartitions`, `IsAnAfsPartition`, `DoesPartitionExist`, and `FreePartitionTable` expose and clear the cache.

Control flow: Readers must call `ReadPartitionTable` before lookup. `ReadPartitionTable` frees the previous table first, then replaces the cache. `FreePartitionTable` deallocates with `cfg_PartitionListDeallocate`.

State and persistence: Static process cache only. Durable partition table state lives in the cfg library/server registry and is read/written elsewhere.

Dependencies and integration points: Requires `g_hServer`, OpenAFS cfg admin APIs, TCHAR conversion helpers, and is used by current-config discovery, wizard partition selection, partition creation, and partition listing.

Risks: Global cache is not thread-safe. `DoesPartitionExist` compares ANSI partition names converted to TCHAR against caller strings, so callers must agree on `/vicepX` vs suffix naming. On failed enumerate the cache is empty even if prior data existed.

Test signals: Test enumerate success/failure, cache replacement, free idempotence, case-insensitive drive lookup, partition-name lookup with full `/vicep` names, and concurrent refresh/list usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.h

Purpose: Declares partition-table cache and lookup helpers.

Important APIs/functions: `ReadPartitionTable`, `GetPartitionTable`, `GetNumPartitions`, `IsAnAfsPartition`, `DoesPartitionExist`, and `FreePartitionTable`.

Control flow: No implementation logic; callers are responsible for refreshing the cache before use.

State and persistence: Implementation maintains a static cache and reads server partition-table state.

Dependencies and integration points: Requires OpenAFS `cfg_partitionEntry_t`, `afs_status_t`, and Win32/TCHAR types via `afscfg.h`.

Risks: The API returns a raw pointer to static cached storage that becomes invalid after `ReadPartitionTable` or `FreePartitionTable`.

Test signals: Verify callers do not retain the returned pointer across refresh/free and handle zero-entry tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partitions_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partitions_page.cpp

Purpose: Implements the config-manager Partitions tab for listing configured/exported AFS partitions, adding registry partition entries, removing unexported entries, and launching salvage.

Important APIs/functions: `PartitionsPageDlgProc`, `UpdatePartitionList`, `OnCreatePartitions`, `OnRemove`, `OnSalvage`, `ShowPartitions`, `GetPartitionTableFromRegistry`, `GetPartitionTableFromVos`, `DiskSpaceToString`, and `CheckEnableSalvage`.

Control flow: Init sets up FastList columns/images, reads registry partition entries through cfg, optionally reads exported partition/space data through vos when file server is configured, then merges both views into the list. Create opens `CreatePartition` and refreshes on success. Remove refuses exported partitions, confirms deletion, calls `cfg_HostPartitionTableRemoveEntry`, and removes the item from UI. Salvage validates file-server state, runs the salvage dialog, shows results, then refreshes the list.

State and persistence: Uses static selected item, list handles, localized Yes/No strings, and remembered file-server config state. Durable changes include cfg partition-table removal/addition and salvage side effects on server data. VOS partition data is read-only.

Dependencies and integration points: Integrates FastList/image-list helpers, app-library icons, `partition_utils`, `create_partition_dlg`, `salvage_results_dlg`, OpenAFS vos/client/cfg APIs, and global handles `g_hServer`/`g_hCell`.

Risks: The merged display assumes registry entries are authoritative and vos entries are a subset. Removal updates UI but not necessarily the cached partition table. VOS enumeration uses a fixed `MAX_PARTITIONS` of 26. `DiskSpaceToString` returns a static buffer reused for both total/free columns; correctness depends on FastList copying text immediately.

Test signals: Test no partitions, registry-only partition, exported partition with size/free data, VOS failures, remove exported refusal, remove unexported success/failure, create refresh, salvage disabled when no partitions, and configFS changes while page is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partitions_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/replicatition_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/replicatition_page.cpp

Purpose: Implements the wizard replication page for choosing whether to replicate `root.afs` and `root.cell`.

Important APIs/functions: `ReplicationPageDlgProc`, `OnInitDialog`, and `ShowStatusMsg`.

Control flow: First-server mode forces replication. Already-replicated root volumes show a message. If replication status is unknown, the page asks whether to replicate if necessary and defaults to configure. If root volumes are not/will not be configured, replication is disabled. Otherwise radio buttons set `g_CfgData.configRep`.

State and persistence: Mutates `g_CfgData.configRep` and disabled state only. Actual read-only site creation and volume releases happen in the final config page.

Dependencies and integration points: Uses root-volume state discovered by `get_cur_config.cpp`, `ConfiguredOrConfiguring`, `EnableStep`, common wizard handling, and resource strings.

Risks: Filename is misspelled `replicatition_page.cpp`, which can confuse search/build maintenance. Unknown replication status can schedule a later check and possible no-op, so UI choice is conditional. Disabled state may retain stale configure selection under the flag.

Test signals: Test first-server forced replication, already replicated, unknown status, no root volumes, radio toggles, and final config behavior when only one root volume lacks replication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/replicatition_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/resource.h

Purpose: Central numeric resource ID header for the server configuration UI.

Important APIs/definitions: Defines string IDs (`IDS_*`) for wizard text, configuration step messages, validation/error messages, service/partition labels, salvage text, and warnings. Defines icon/bitmap/dialog IDs (`IDI_*`, `IDB_*`, `IDD_*`) and control IDs (`IDC_*`, `IDNEXT`, `IDBACK`) used by all dialog procedures and help mappings.

Control flow: No runtime logic. The IDs bind C++ dialog code to localized `.rc` resources and help context tables.

State and persistence: None.

Dependencies and integration points: Included by nearly every `afssvrcfg` source file. Must stay synchronized with `lang/*/afscfg.rc`, help registration in `help.cpp`, and dialog procedures.

Risks: Duplicate control IDs exist intentionally or accidentally (`IDC_FS_STATUS_MSG` and `IDC_SCS_PROMPT`, `IDC_SCS_FRAME` and `IDC_HOSTNAME_FRAME` share values), so code must only use them in the correct dialog template. Numeric gaps and frozen string catalog comments make adding messages delicate. Resource mismatch causes runtime UI/help failures rather than compile errors.

Test signals: Resource compile, open every dialog, verify every referenced ID exists in each template, check localized string coverage, and validate help mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/root_afs_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/root_afs_page.cpp

Purpose: Implements the wizard page for choosing whether to create `root.afs` and `root.cell` root volumes.

Important APIs/functions: `RootAfsPageDlgProc`, `OnInitDialog`, and `ShowStatusMsg`.

Control flow: First-server mode forces root volume creation. Already-created root volumes show a status message. Unknown existence defaults to creating if necessary. If no partition exists/will exist, the step is disabled. If `root.afs` exists but `root.cell` does not, creation is disabled due to a known unsupported case. Otherwise radio buttons set `g_CfgData.configRootVolumes`.

State and persistence: Mutates `g_CfgData.configRootVolumes` and its disabled bit only. Durable volume creation, ACL, mount-point, and client-start operations occur later in the final configuration page.

Dependencies and integration points: Depends on root-volume and partition state from current-config discovery and partition page, common wizard helpers, and resource strings.

Risks: The partial `root.afs` exists/`root.cell` missing case is handled by silently disabling creation with a TODO rather than a specific explanatory string. Unknown existence can lead to final config doing extra checks and no-ops.

Test signals: Test first-server forced creation, already-configured roots, unknown existence, missing partition, partial root-volume state, radio choices, and downstream replication enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/root_afs_page.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_dlg.cpp

Purpose: Implements the salvage options dialog and starts an asynchronous bos salvage operation for the server, selected partition, or selected volume.

Important APIs/functions: `ShowSalvageDlg` captures the optional partition and creates `g_CfgData.hSalvageThread` after OK. `SalvageDlgProc`, `OnInitDialog`, `OnAdvanced`, `UpdateControls`, `OnSalvage`, and worker `Salvage` manage UI and execution.

Control flow: The dialog defaults to partition salvage when a partition is selected, otherwise only server salvage is allowed. Advanced options are initially collapsed. OK validates volume name and optional parallel process count, prompts for admin login if reusable admin info is unavailable, refreshes handles, and starts a worker thread. The worker opens the bos server, calls `bos_Salvage` with selected partition/volume/temp/log/process options and fixed salvage flags, closes the bos server, and records whether admin info can be reused.

State and persistence: Uses static buffers for selected partition, volume, temp directory, process count, and output pointers consumed by the worker. Writes `g_CfgData.szSalvageLogFileName`, `hSalvageThread`, and `bReuseAdminInfo`. Durable effects are server salvage activity and optional salvage log generation by bosserver.

Dependencies and integration points: Integrates OpenAFS bos admin APIs, `admin_info_dlg` for login, `GetHandles`, app-library help/modal UI, and the salvage-results dialog that waits on `g_CfgData.hSalvageThread`.

Risks: Static option buffers are shared with the worker after the modal dialog closes. UI controls for advanced flags are shown but their checkbox values are not passed; fixed flags are used instead. Worker calls `ShowError` from a background thread. Thread handle ownership is transferred to the results dialog; if results are not shown, it can leak. User-specified log file is saved later from fetched log text, not passed to `bos_Salvage`.

Test signals: Test server/partition/volume modes, no selected partition, invalid/empty volume, process count bounds, admin login failure, handle refresh failure, bos open/salvage failure, advanced collapse/expand, and handoff to results dialog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.cpp

Purpose: Displays live and final salvage log output while waiting for the salvage worker thread to finish, and optionally saves the final log to disk.

Important APIs/functions: `ShowSalvageResults` opens the modal dialog. `OnInitDialog` opens a bos server handle, disables system close, starts animation, and spawns `ShowResults`. `ShowResults` waits on `g_CfgData.hSalvageThread`, periodically calls `bos_LogGet`, expands buffers on `ADMMOREDATA`, converts LF to CRLF, trims to edit-control capacity, updates the edit control, saves the final log, closes the salvage thread handle, and enables Close. Helpers include `AddCarriageReturnsToLog`, `GetMaxPartOfLogWeCanShow`, `AllocMemory`, and `SaveLogToDisk`.

Control flow: The dialog cannot be closed until `bSalvageComplete` is true. The polling thread updates the log every five seconds or immediately when the salvage thread exits, then marks complete/failure and enables the Close button. `OnClose` closes the bos server and ends the dialog.

State and persistence: Static dialog globals hold bos handle/status/result, logo handle, and completion flag. It reads `g_CfgData.hSalvageThread` and `szSalvageLogFileName`. Durable persistence occurs only if the user supplied a log path, in which case fetched log text is written to that file.

Dependencies and integration points: Uses OpenAFS bos admin APIs, Win32 threads/waits, app-library animation, resize helpers, conversion wrappers, global config/log state, and the salvage dialog's thread handle.

Risks: Worker thread updates dialog controls directly. `AllocMemory` uses `delete` instead of `delete[]` for arrays, and cleanup also uses `delete` for arrays. `pszLogBuf[nLogSize] = 0` assumes the allocated buffer is larger than the returned size. `bos_ServerClose` only runs on user close; init failure can leave partial UI state. Close handle ownership depends on this dialog always running after salvage starts.

Test signals: Test short and large salvage logs, `ADMMOREDATA` resizing, log over edit-control limit, save-to-disk success/failure, bos open/log get failure, user pressing Cancel before/after completion, and memory diagnostics for array deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.h

Purpose: Declares the salvage-results dialog entry point.

Important APIs/functions: `ShowSalvageResults(HWND hParent)` returns true when the results dialog closes with OK.

Control flow: No implementation logic. Callers invoke it after `ShowSalvageDlg` starts the salvage thread.

State and persistence: Implementation observes `g_CfgData.hSalvageThread` and may save the fetched salvage log to `g_CfgData.szSalvageLogFileName`.

Dependencies and integration points: Requires Win32 `HWND`; included by `partitions_page.cpp`.

Risks: The API assumes a salvage thread is already present in global state; there is no parameter enforcing that precondition.

Test signals: Verify caller sequence and behavior when the salvage thread handle is null or already signaled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/salvage_results_dlg.h -->
