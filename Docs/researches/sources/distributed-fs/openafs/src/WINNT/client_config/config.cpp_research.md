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
