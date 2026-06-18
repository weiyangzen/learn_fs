# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/prefs.h

## Purpose
`prefs.h` declares registry-backed preference and subset helper functions.

## Important APIs, Types, And Functions
It exposes `ErasePreferences`, `RestorePreferences`, `StorePreferences`, `OpenSubsetsKey`, and `OpenSubsetsSubKey`. `ErasePreferences` defaults to deleting all preferences when no cell/server is supplied. `OpenSubsetsKey` notes the `fCreate` convention: `0` open, `1` create, `2` delete.

## Control Flow
No logic exists in the header. Callers pass `LPIDENT` plus a preference struct buffer to store or restore object settings.

## State And Persistence
The API represents HKCU persistence for Server Manager preferences and subset definitions, but declares no storage.

## Dependencies And Integration Points
Consumers include server/service/aggregate/fileset preference loaders and subset management dialogs. It depends on Win32 `HKEY`, TCHAR strings, and `LPIDENT`.

## Risks And Test Signals
Risks are mostly API clarity around raw blobs and `fCreate == 2`. Compile coverage and registry round-trip tests validate the contract.
