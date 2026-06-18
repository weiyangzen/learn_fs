<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.cpp

## Purpose
Bridges asynchronous AFSClass notifications to UI subscribers and immediate preference/alert maintenance.

## Important APIs, Types, And Functions
`CreateNotificationDispatch`, `PostNotification`, `DispatchNotification`, `DispatchNotification_OnPump`, `NotifyMe`, `DontNotifyMe`, and `DontNotifyMeEver`. Internals include a critical section, callback handler, subscription array, and FIFO queue.

## Control Flow
AFSClass notifications first run alternate-thread handling to attach/detach preferences, adjust monitor state, and queue alert checks. The notification is copied into a protected queue. The main pump drains notifications, updates actions, filters subscribers by `NOTIFYWHEN` and object relationships, and posts `WM_NOTIFY_FROM_DISPATCH` to target windows.

## State And Persistence
Module statics store subscriptions and queued notifications. Preference structures are attached to object user params on create and deleted on destroy. `g.sub` may be updated from monitor-state changes.

## Dependencies And Integration Points
Uses AFSClass notifications, object identity APIs, preference loaders, subset monitoring, display updates, alert/scout functions, and action tracking.

## Risks And Edge Cases
Subscriptions are tombstoned, not compacted. Posted `NOTIFYSTRUCT` ownership is transferred to receivers. Some display updates occur in alternate-thread handling. Queue allocation failure is not handled. Filtering complexity can miss propagation.

## Test Signals
Create/destroy preference attach, queue ordering, each subscription filter, unsubscribe/destroy, action/alert side effects, and dead-target handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/dispatch.cpp -->
