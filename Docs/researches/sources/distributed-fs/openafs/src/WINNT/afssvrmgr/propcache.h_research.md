# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/propcache.h

## Purpose
`propcache.h` defines dialog cache categories and declares the property-cache API.

## Important APIs, Types, And Functions
The `PropCache` enum covers server windows, server property/list/create/sync/install/security/salvage/hosts dialogs, service property/create dialogs, aggregate properties, fileset replication/properties/release/clone/delete dialogs, error dialogs, and general dialogs. `ANYVALUE` is `(PVOID)-1`. The API exposes add, search, and delete overloads.

## Control Flow
No logic is present. Dialogs call `PropCache_Add` on creation, use `PropCache_Search` before creating a new instance, and call `PropCache_Delete` on destroy.

## State And Persistence
The header declares no storage; the implementation maintains process-local state.

## Dependencies And Integration Points
It depends on Win32 `HWND` and pointer payloads. It is a cross-cutting GUI integration point for duplicate-dialog prevention and server-window refresh routing.

## Risks And Test Signals
Risks are enum/category mismatches and misuse of `ANYVALUE`. Compile coverage and duplicate-dialog tests for representative cache types validate the contract.
