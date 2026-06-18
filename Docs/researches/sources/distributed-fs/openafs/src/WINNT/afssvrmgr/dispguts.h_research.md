# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispguts.h

## Purpose
`dispguts.h` declares the internal display worker entry points implemented in `dispguts.cpp`. It intentionally directs callers to use the public `UpdateDisplay()` interface instead of invoking these routines directly.

## Important APIs, Types, And Functions
The header exports seven functions: `Display_Cell_Internal`, `Display_Servers_Internal`, `Display_Services_Internal`, `Display_Aggregates_Internal`, `Display_Filesets_Internal`, `Display_Replicas_Internal`, and `Display_ServerWindow_Internal`. All accept `LPDISPLAYREQUEST`, tying the header to `display.h`.

## Control Flow
There is no executable control flow. At runtime `display.cpp` dispatches on `DISPLAYREQUEST::dt` and calls these functions while holding the AFSClass lock, after the request has passed queue filtering.

## State And Persistence
No state is declared. State is supplied through the request object and global application structures used by the implementations.

## Dependencies And Integration Points
The header integrates the display queue with the implementation module. It must be included in files that know `LPDISPLAYREQUEST`, normally through `display.h` and `svrmgr.h`.

## Risks And Test Signals
The risk is boundary drift: adding a display target in `display.h` requires matching declarations and implementations here. Compile coverage and exercising every `DISPLAYTARGET` dispatch path are the main test signals.
