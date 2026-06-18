<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.h

## Purpose
Declares the context command dispatcher.

## Important APIs, Types, And Functions
`StartContextCommand(HWND, LPIDENT lpiRepresentedByWindow, LPIDENT lpiChosenByClick, int cmd)`.

## Control Flow
No runtime flow in the header.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Requires HWND and `LPIDENT`; used by list subclasses and menu handlers.

## Risks And Edge Cases
Correct routing depends on callers passing represented and clicked identities consistently.

## Test Signals
UI command-routing tests for all callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.h -->
