<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.h

## Purpose
Declares the action/progress tracking API.

## Important APIs, Types, And Functions
Exports `ActionNotification_MainThread`, action window open/close/topmost functions, `Action_SetDefaultView`, `Action_fAnyActive`, and `Action_ShowConfirmations`.

## Control Flow
No runtime flow in the header.

## State And Persistence
No state declared; implementation uses module statics and global preferences.

## Dependencies And Integration Points
Requires notification, view, and Win32 types from server-manager headers.

## Risks And Edge Cases
No explicit init/teardown API; callers rely on zero-initialized module state.

## Test Signals
Compile integration and menu/shutdown behavior around active actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/action.h -->
