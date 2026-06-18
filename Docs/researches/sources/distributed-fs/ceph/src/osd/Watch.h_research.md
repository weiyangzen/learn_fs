# sources/distributed-fs/ceph/src/osd/Watch.h

## Purpose
`Watch.h` declares runtime structures for RADOS object watch/notify behavior in the OSD. It separates `Notify` aggregation, individual `Watch` connection/object state, and `WatchConState` session-level watch tracking.

## Important APIs, Types, And Functions
`WatcherState` defines pending/notified markers used by watch metadata paths. `Notify` stores the notifying client, payload, timeout, cookie, notify id, object version, watcher refs, reply buffers, and timer callback. `Watch` stores weak self-ref, connection, callback, OSD service, PG ref, object context, in-progress notifies, timeout/cookie/address/entity fields, ping state, and discarded flag. Public APIs create refs, connect/disconnect, remove/discard, start/cancel notify, process notify ack, and access object/PG/cookie/entity data. `WatchConState` adds/removes watches and resets all watches for a connection.

## Control Flow
`Notify` is initialized after all watchers are added; it then waits for watcher completion or timeout. `Watch` connects to a session and registers with `Session::wstate`, resends in-progress notifies on reconnect, and uses timeout callbacks for missed pings or disconnected older clients. Removing or discarding a watch drains in-progress notifies and clears runtime state.

## State And Persistence Behavior
The declarations define volatile runtime state. Watcher persistence in object metadata is handled by PG object operations and object contexts, not by this header. `Notify` keeps reply aggregation until completion; `Watch` keeps notify membership by notify id until ack, cancel, remove, or discard.

## Dependencies And Integration Points
The file depends on messenger connections, `Context`, `PrimaryLogPG`, `ObjectContext`, `OSDService`, and `MWatchNotify` forward declarations. It is consumed by `PrimaryLogPG` for watch operation effects and by `Session` for connection reset tracking.

## Risks And Test Signals
Risks include dangling weak/self references, missing callback cancellation, inconsistent connection/session state, and accidental use without PG lock where required. Tests should target object watch connect/unwatch, notify lifecycle, delayed timeout generation during scrub/recovery, reconnect resend behavior, and session reset interactions.
