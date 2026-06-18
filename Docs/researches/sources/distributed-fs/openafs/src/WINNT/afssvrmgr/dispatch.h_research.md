<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.h

## Purpose
Defines notification subscription categories, app-specific events, payloads, and dispatch APIs.

## Important APIs, Types, And Functions
`NOTIFYWHEN`, `NOTIFYSTRUCT`, custom events `evtAlertsChanged`, `evtScoutBegin`, `evtScoutEnd`, and prototypes for dispatch creation, posting, subscription, unsubscription, and pump draining.

## Control Flow
No implementation flow; consumers register windows and receive `WM_NOTIFY_FROM_DISPATCH`.

## State And Persistence
No state declared; implementation owns queue/subscriber state.

## Dependencies And Integration Points
Includes `messages.h` and uses AFSClass notification types. Used by tabs, display, action, and alert code.

## Risks And Edge Cases
Custom event values must not collide beyond `evtUser`. Pointer fields inside copied params must outlive posted handling.

## Test Signals
Compile all consumers and verify message ownership/lifetime in handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.h -->
