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
