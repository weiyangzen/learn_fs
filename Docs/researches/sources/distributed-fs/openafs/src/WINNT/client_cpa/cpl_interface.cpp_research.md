# sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.cpp

Purpose: implements the exported Windows Control Panel `CPlApplet` entry point for the OpenAFS client applet. It dynamically chooses applet metadata and icon based on the current OS family and whether the OpenAFS client registry installation key exists.

Important APIs/functions: `IsWindowsNT()` caches `GetVersionEx` platform detection; `IsClientInstalled()` probes `AFSREG_CLT_SW_VERSION_SUBKEY` and `AFSREG_CLT_SW_VERSION_DIR_VALUE`; `CPlApplet()` handles `CPL_INIT`, `CPL_GETCOUNT`, `CPL_INQUIRE`, `CPL_NEWINQUIRE`, `CPL_DBLCLK`, and `CPL_EXIT`.

Control flow: initialization loads the resource satellite through `TaLocale_LoadCorrespondingModule` and initializes COM as apartment-threaded. Inquiry messages fill `CPLINFO` or `NEWCPLINFO` with localized strings and icons. Double-click launches `afs_config.exe`, passing `/c` when Windows NT lacks an installed client, which routes users to client configuration rather than normal client control.

State/persistence: module handles and detection booleans are static process state. Persistent data is read only from HKLM OpenAFS registry keys.

Dependencies/integration: depends on Win32 Control Panel, ShellExecute, COM initialization, `TaLocale`, and OpenAFS registry constants. It integrates with `afs_config.exe` rather than embedding configuration UI.

Risks: `GetVersionEx` and cached registry detection can become stale for long-lived Control Panel sessions. `ShellExecuteEx` return value is ignored. The applet assumes `afs_config.exe` is discoverable in the shell search path.

Test signals: verify CPL load/unload calls balance COM/resource unloading, registry-present and registry-absent labels/icons, Windows 9x versus NT behavior, and double-click command parameters.
