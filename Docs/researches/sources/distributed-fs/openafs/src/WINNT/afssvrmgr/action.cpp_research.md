<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.cpp

## Purpose
Tracks long-running server-manager operations and presents action/progress UI.

## Important APIs, Types, And Functions
`ActionNotification_MainThread` maps AFSClass events to begin/update/end handlers. Public APIs manage the action window, default view, topmost state, active-operation query, and confirmation display. Internals include `ACTIONTYPE`, `ACTION`, `Action_Begin`, `Action_Find`, `Action_End`, `Action_GetDescription`, and dialog procs for refresh/move/dump/restore/open-cell progress.

## Control Flow
Dispatch sends notifications on the UI thread. Simple operations add/remove action records; refresh receives percent/section messages; move/dump/restore/open-cell create modeless animation dialogs. The action window uses a timer to refresh elapsed times in a FastList.

## State And Persistence
Static `l` owns the dynamic action array, active count, and confirmation flag. Global `gr` persists action window geometry/view. No operation state is durable.

## Dependencies And Integration Points
Depends on AFSClass notifications, global `g/gr`, FastList/view helpers, modeless dialogs, animation controls, and resource strings. Called by `dispatch.cpp`.

## Risks And Edge Cases
Begin/end matching depends on exact notify params. `GetTickCount` wrap can affect elapsed time. Dialogs are closed asynchronously via posted `IDCANCEL`. Refresh actions intentionally do not count toward quit-blocking active operations.

## Test Signals
Begin/end pairs for every event, mismatched ends, simultaneous actions, confirmation messages, refresh skip, progress-dialog closure races, and hidden-main quit gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.cpp -->
