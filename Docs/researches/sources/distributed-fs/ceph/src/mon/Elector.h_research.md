<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.h -->
# sources/distributed-fs/ceph/src/mon/Elector.h

## Purpose
`Elector.h` declares the monitor election integration class. `Elector` owns the election algorithm and connectivity tracker, implements both `ElectionOwner` and `RankProvider`, and exposes monitor-facing hooks for dispatching election/ping messages and reacting to monmap or strategy changes.

## Important APIs, types, and functions
`Elector` contains `ElectionLogic logic`, `ConnectionTracker peer_tracker`, ping timestamp maps, live/dead/pending ping sets, timer state, peer feature metadata, monitor pointer, and disallowed leader set. Internal message handlers cover propose, ack, victory, NAK, ping, and connection report assimilation. Owner-interface methods expose epoch persistence, store validation, election triggers, peer proposals, deferral, victory messaging, quorum membership, stretch-mode checks, and connectivity score persistence.

Public monitor APIs include constructor/destructor, `shutdown()`, `get_epoch()`, `declare_standalone_victory()`, `begin_peer_ping()`, `dispatch()`, `call_election()`, `stop_participating()`, `start_participating()`, peer tracker inspection, netsplit query, peer-state reset/rank notifications, strategy update, disallowed leader update, pending ping processing, and connection score dumping.

## Control flow
The header defines a layered flow: external monitor code calls `call_election()` or `dispatch()`, private handlers validate and translate messages, `ElectionLogic` makes the decision, and owner callbacks send messages or update monitor state. Connectivity pings run as self-rescheduling timer callbacks and feed the tracker used by connectivity elections.

## State and persistence behavior
Persistent state is not written in the header, but the declared owner methods persist election epochs and connectivity scores in the implementation. Runtime state includes timer callback `expire_event`, peer feature metadata collected during self-election, ping maps/sets, disallowed leaders, and pending pings waiting for quorum feature negotiation.

## Dependencies and integration points
The class depends on `Monitor`, `MonOpRequest`, `mon_types`, `ElectionLogic`, `ConnectionTracker`, and `Formatter`. It is the bridge between monitor networking/timers/store and the pure election decision engine.

## Risks and edge cases
`Elector` inherits `RankProvider` privately via `class Elector : public ElectionOwner, RankProvider`; only internal conversion to the tracker is intended. The public `Elector *elector` self-pointer is unusual and may exist for legacy call sites. `set_disallowed_leaders()` only records changes; callers must trigger elections if the current leader becomes disallowed. `start_participating()` only flips the flag in the declaration's implementation and does not itself call an election despite the comment.

## Test signals
Compile tests should ensure `Elector` still satisfies both owner interfaces after interface changes. Runtime tests should validate monitor lifecycle hooks, disallowed leader change behavior, start/stop participation semantics, pending ping draining, and exposed dump/netsplit methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.h -->
