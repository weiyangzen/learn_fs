<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.h

## Purpose
Declares the column customization dialog entry point.

## Important APIs, Types, And Functions
`ShowColumnsDialog(HWND hParent, LPVIEWINFO lpvi = NULL)`.

## Control Flow
No runtime flow.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Requires `HWND` and `LPVIEWINFO`; invoked by command handling.

## Risks And Edge Cases
Null default selects the server-list view based on current preview/orientation state.

## Test Signals
Open dialog from server, aggregate, service, and fileset menus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.h -->
