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
