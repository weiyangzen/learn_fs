# sources/distributed-fs/ceph/src/osd/Watch.cc

## Purpose
`Watch.cc` implements OSD object watch and notify lifecycles. Watches bind clients to object contexts so clients can receive object notifications; notifies aggregate watcher acknowledgements, timeouts, and completion replies back to the notifier.

## Important APIs, Types, And Functions
`Notify` manages one notify operation: client connection/gid, payload, timeout, cookie, notify id, version, watcher set, reply collection, timer callback, and completion/discard flags. Important methods are `makeNotifyRef()`, `init()`, `start_watcher()`, `complete_watcher()`, `complete_watcher_remove()`, `discard()`, `register_cb()`, `unregister_cb()`, `do_timeout()`, and `maybe_complete_notify()`. `Watch` manages a watcher connection and object context with methods `connect()`, `disconnect()`, `got_ping()`, `remove()`, `discard()`, `start_notify()`, `cancel_notify()`, `notify_ack()`, and timeout callback creation. `WatchConState` tracks watches attached to a session.

## Control Flow
A notify is created, watchers are registered before `init()`, and `init()` arms a timeout then completes immediately if there are no watchers. Each watch stores the notify, sends `MWatchNotify` if connected, and later passes ack data to `Notify::complete_watcher()`. `Notify::maybe_complete_notify()` sends `CEPH_WATCH_EVENT_NOTIFY_COMPLETE` when all watchers respond or timeout fires, encoding replies and missed watcher ids. Watch timeout callbacks drop `watch_lock`, take the PG lock, and invoke `PrimaryLogPG::handle_watch_timeout()` if still valid. Session reset calls `WatchConState::reset()`, which disconnects affected watches under PG lock.

## State And Persistence Behavior
Watch and notify state is in-memory, associated with object contexts, sessions, messenger connections, and OSD watch timers. Persistent watch metadata is managed through object operations elsewhere; this file maintains runtime liveness, timeout, and notification state. `discard_state()` clears object context refs, session watch links, callbacks, and connection refs.

## Dependencies And Integration Points
The implementation depends on `PrimaryLogPG`, `OSDService`, `Session`, messenger `Connection`, `MWatchNotify`, OSD watch timer/lock, and PG locking. It integrates with `PrimaryLogPG` for timeout handling and with `Session::wstate` for connection reset cleanup.

## Risks And Test Signals
High-risk areas are callback lifetime, lock transitions between `watch_lock`, notify lock, and PG lock, duplicate disconnect/remove paths, ping timeout semantics, and notify completion after discard. Tests should cover connected and disconnected watches, pinging and non-pinging clients, notify ack aggregation, notify timeout with missed watchers, session reset, object removal with disconnect events, and peering discard.
