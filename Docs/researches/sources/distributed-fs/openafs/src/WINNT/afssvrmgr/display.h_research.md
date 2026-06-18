# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.h

## Purpose
`display.h` defines the public contract for all list, tree, combobox, cell label, and server-window refreshes in the Server Manager UI.

## Important APIs, Types, And Functions
`DISPLAYTARGET` enumerates refresh targets: cell, servers, services, aggregates, filesets, replicas, and server window. `DISPLAYREQUEST` carries target windows, identity filters, status codes, parent identities, selection, view settings, worker-populated list handles, completion action flags, and whether the target is a FastList. Action flags are `ACT_ENDCHANGE`, `ACT_UNCOVER`, and `ACT_SELPREVIEW`. Prototypes expose display wrappers, `GetItemText`, `HandleColumnNotify`, and `Display_GetServerIconView`.

## Control Flow
Callers either fill a `DISPLAYREQUEST` and call `UpdateDisplay()` or use one of the `UpdateDisplay_*` wrappers. The request is copied by the scheduler, so stack-allocated packets are valid even for asynchronous updates.

## State And Persistence
The header declares no storage. It describes state passed into `display.cpp` and mutable `VIEWINFO` records owned by global settings or dialog-local view structures.

## Dependencies And Integration Points
Consumers need Win32 HWND types, `LPIDENT`, `LPVIEWINFO`, FastList notification types, and the broader `svrmgr.h` environment. The API is used throughout tabs, property dialogs, and fileset operation dialogs whenever an AFS object list must be rebuilt.

## Risks And Test Signals
The main risk is semantic coupling around nullable fields: `lpiNotify == NULL` means full refresh, while non-null means targeted replacement; `hList` may be caller-provided or worker-discovered. Compile tests plus functional refresh tests for every wrapper are the most useful signals.
