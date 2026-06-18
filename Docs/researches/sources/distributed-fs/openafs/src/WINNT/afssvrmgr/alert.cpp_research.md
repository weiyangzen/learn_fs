<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.cpp

## Purpose
Maintains alert state for servers, services, aggregates, and filesets, and runs the background Scout health-check loop.

## Important APIs, Types, And Functions
Public APIs query, describe, add/remove, initialize, and schedule alerts. Internals roll child alerts up to servers, maintain bad-credential warnings, and evaluate server health in `Alert_ScoutProc`/`Alert_Scout_CheckServer`.

## Control Flow
Alerts live in per-object preference structures. Child alert changes update server secondary alerts. Scout wakes periodically or on demand, checks credentials, refreshes server lists/status when due, evaluates aggregate capacity, fileset state/quota/ghost entries, and stopped services, then posts alert/scout notifications.

## State And Persistence
`OBJECTALERTS` stores cadence, next test/refresh ticks, count, and fixed alert array. Preferences persist alert settings; `Alert_Initialize` clears runtime fields. Static Scout thread/event live for process lifetime.

## Dependencies And Integration Points
Uses credentials, AFSClass object/status APIs, preference structs, ghost flags, `PostNotification`, and display consumers for descriptions/remedies/buttons.

## Risks And Edge Cases
Scout has no explicit shutdown. Alert arrays cap at 32. `Alert_GetAlert`/`Alert_GetIdent` use `>` instead of `>=` for bounds. `Alert_RemoveFunc` swaps with the last alert. `PulseEvent` can lose wakeups.

## Test Signals
Alert rollup/removal, bad credential insertion/removal, timeout status, Scout threshold detection, array-full behavior, notification emission, and index boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.cpp -->
