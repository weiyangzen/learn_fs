# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.cpp

## Purpose
`propcache.cpp` tracks currently open property and command dialogs so the UI can focus an existing dialog instead of opening duplicates and can find server windows for refresh.

## Important APIs, Types, And Functions
Public functions are `PropCache_Add`, `PropCache_Search`, `PropCache_Delete(PropCache, PVOID)`, and `PropCache_Delete(HWND)`. The private `PropCacheEntry` stores `fInUse`, `pcType`, `pv`, and `hDialog`. `ANYVALUE` searches/deletes by type regardless of payload.

## Control Flow
Adding first searches for an existing entry of the same type/payload. If none exists, it reuses a free slot or grows the static array by 16, records the dialog, and registers non-server dialogs with AfsAppLib as modeless dialogs. Search optionally starts after a supplied window, skips unused entries, drops entries whose window handle is no longer valid, and returns the first match. Delete marks matching entries unused.

## State And Persistence
State is process-local in a grow-only static array. No persistent settings are stored.

## Dependencies And Integration Points
The cache is used by options, fileset delete/clone, server-window refresh, and many property dialogs elsewhere in afssvrmgr. It depends on Win32 `IsWindow` and AfsAppLib modeless dialog registration.

## Risks And Edge Cases
There is no synchronization, so all callers are expected to run on the UI thread. Entries are not compacted and stale entries are removed only on search or explicit delete. Duplicate protection is by exact pointer value, so object identity stability is required. Server windows are not registered as modeless dialogs by design.

## Test Signals
Test duplicate dialog focusing, `ANYVALUE` search/delete, stale window cleanup, sequential search using `hwndStart`, modeless registration for non-server dialogs, and delete-on-destroy paths.
