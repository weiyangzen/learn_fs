# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.cpp

## Purpose
`dispguts.cpp` implements the concrete redraw routines behind `UpdateDisplay()`. It populates the main cell identity fields and the FastList/combobox views for servers, services, aggregates, filesets, replicas, and per-server windows. This is the bridge between the AFSClass object model (`LPCELL`, `LPSERVER`, `LPAGGREGATE`, `LPFILESET`, `LPSERVICE`, `LPIDENT`) and the Win32/AfsAppLib visual controls.

## Important APIs, Types, And Functions
Externally declared functions are `Display_Cell_Internal`, `Display_Servers_Internal`, `Display_Services_Internal`, `Display_Aggregates_Internal`, `Display_Filesets_Internal`, `Display_Replicas_Internal`, and `Display_ServerWindow_Internal`. Private helpers clean incrementally replaced rows, add parent/child hierarchy nodes, choose status/type images through `Display_PickImages`, and add FastList rows through `Display_InsertItem`. The file depends heavily on column-format helpers from `svr_col.h`, `svc_col.h`, `agg_col.h`, and `set_col.h`, plus `Filesets_fIsLocked` from `set_general.h`.

## Control Flow
Each display routine receives a `DISPLAYREQUEST` prepared by `display.cpp`. It discovers the target control, ensures image lists exist, starts a FastList or combobox change transaction, optionally removes only rows affected by `lpiNotify`, enumerates the relevant AFSClass hierarchy, inserts or updates visible items, restores selection, and sets `actOnDone` flags such as `ACT_ENDCHANGE`, `ACT_UNCOVER`, and `ACT_SELPREVIEW`. Incremental requests are filtered by server or aggregate identity before expensive enumeration. Error status from a notification is rendered directly into the first column and usually prevents descending into children.

## State And Persistence
This file does not persist settings itself, but it mutates process state and cached object preferences. Successful status fetches are copied into `SERVER_PREF::ssLast`, `SERVICE_PREF::ssLast`, `AGGREGATE_PREF::asLast`, and `FILESET_PREF::fsLast`, and fileset preferences also cache `lpiRW`. Tree expansion state is read from server and aggregate preference records. Main-window identity labels are derived from `g.lpiCell` and `g.hCreds`.

## Dependencies And Integration Points
Integration points include FastList APIs (`FL_StartChange`, `FastList_AddItem`, `FastList_SetExpanded`), combobox helpers (`CB_StartChange`, `CB_AddItem`), AfsAppLib image lists and cover/uncover UI, AFSClass object enumeration/status APIs, global UI state `g` and `gr`, credential cracking, alert counts, and server-window selection. `Display_Replicas_Internal` performs a full cell/server/aggregate/fileset walk to find read-only replicas matching a read-write volume ID.

## Risks And Edge Cases
Several cleanup loops rely on identity pointer stability and careful parent identity checks; stale or reused `LPIDENT` pointers would remove wrong rows. Static image-list initialization is per control and not reference-counted here. `Display_Replicas_Internal` can be expensive because it scans the whole cell. Status failures suppress child enumeration, so partial outages can hide lower-level objects. The helper uses static UI buffers returned by column functions, which is acceptable for immediate copies but fragile if reused asynchronously.

## Test Signals
Useful tests include full and incremental refresh for each target, row replacement when a server/aggregate/fileset notification arrives, error rendering, monitored versus unmonitored servers, alert and locked icons, tree expansion persistence, combobox selection fallback, replica discovery for RW/RO volume IDs, credential-expired label formatting, and preview-pane selection updates after server-list refresh.
