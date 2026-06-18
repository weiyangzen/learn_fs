# sources/distributed-fs/ceph/src/osd/Session.h

## Purpose
`Session.h` declares the per-connection OSD `Session` object and its `Backoff` records. It centralizes client capabilities, connection state, watch state, map-wait queues, projected epoch tracking, heartbeat metadata, and per-client PG/object backoff tracking.

## Important APIs, Types, And Functions
`Backoff` is a refcounted object with states `STATE_NEW`, `STATE_ACKED`, and `STATE_DELETING`, PG/session references, an id, PG id, and `[begin,end)` object range. Its state helpers and `operator<<` support debug logging. `Session` stores `entity_name`, `OSDCap`, `ConnectionRef`, socket address, `WatchConState`, dispatch lock, `waiting_on_map`, `projected_epoch`, backoff maps, heartbeat peer/stamps, and helpers `ack_backoff()`, `have_backoff()`, `check_backoff()`, `add_backoff()`, `rm_backoff()`, and `clear_backoffs()`.

## Control Flow
Backoff lookup uses the PG id map and `lower_bound()` on range starts to find either an exact-object backoff or the preceding range that still covers the object. Request dispatch can call `check_backoff()` to suppress operations covered by active backoff state. PG code adds/removes backoffs, while session reset calls `clear_backoffs()` to sever session ownership. The comment block documents required lock ordering: `Backoff::lock`, then `PG::backoff_lock`, then `Session::backoff_lock`.

## State And Persistence Behavior
Session state is volatile and tied to messenger connection/session lifetime. Backoff ids are generated from `backoff_seq`. `backoff_count` is an atomic fast path for avoiding map locking when no backoffs exist. Watch state is held through `WatchConState` and reset with the session.

## Dependencies And Integration Points
The header integrates `OSDCap`, `OpRequest`, `Watch`, `OSDMap`, `PeeringState`, intrusive PG refs, messenger connections, and heartbeat stamps. PG code is a close collaborator for creating and releasing backoffs, while watch code uses `Session::wstate` to track connection-owned watches.

## Risks And Test Signals
Important risks are map/range lookup edge cases, lock ordering, inconsistent bidirectional ownership, and assumptions around `backoff_count` versus `backoffs.empty()`. Tests should include overlapping ranges, single-object backoffs, disconnect while requests are queued, backoff ack deletion, and session/watch reset interactions.
