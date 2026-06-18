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
