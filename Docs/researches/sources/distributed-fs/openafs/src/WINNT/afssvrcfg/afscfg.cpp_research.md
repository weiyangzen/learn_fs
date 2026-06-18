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
