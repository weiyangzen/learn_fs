<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.h -->
# sources/distributed-fs/ceph/src/mon/ElectionLogic.h

## Purpose
`ElectionLogic.h` declares the side-effect-free monitor election state machine interface and its owner callback contract. It separates the algorithm from monitor-specific messaging, timers, storage, monmap, and quorum management.

## Important APIs, types, and functions
`ElectionOwner` is the callback interface for persisting epochs, validating local store writes, triggering elections, getting rank/quorum/disallowed leader data, sending proposals, resetting elections, deferring, announcing victory, and querying current quorum membership. `ElectionLogic` declares strategies `CLASSIC`, `DISALLOW`, and `CONNECTIVITY`, public state `participating`, `electing_me`, and `acked_me`, and public methods for standalone victory, election start/end, proposal/ack/victory reception, and epoch/winner reads.

Private helpers implement epoch initialization and bumping, proposal handlers, connectivity scoring, deferral, victory declaration, victory sanity checks, and live-state reset.

## Control flow
The header's comments define the election protocol: start enters an odd election epoch and proposes; proposal handlers may defer or trigger a new election; timer expiry either declares victory with majority acks or restarts/resets; victory claims end the election only when consistent with local strategy and epoch.

## State and persistence behavior
Only `epoch` is persisted, via `ElectionOwner`. The rest of the fields are in-memory election state and connectivity snapshots. The contract says `paxos_size()` and disallowed leader sets can change between elections but not during one.

## Dependencies and integration points
The header forward-declares `ConnectionTracker` and uses Ceph context, bufferlist, and epoch types. `Elector` implements `ElectionOwner` and wires this logic to monitor messages and store writes. The strategy enum must stay synchronized with `MonMap.h`.

## Risks and edge cases
The owner interface is large and correctness-critical; any owner implementation must preserve callback semantics such as durable epoch writes before messaging. Public `acked_me` and `electing_me` are exposed for `Elector` logging/metadata handling, so external code can observe live state but should not mutate protocol invariants. Strategy enum drift with `MonMap` would break mixed monitor behavior.

## Test signals
Interface tests can use a fake `ElectionOwner` to assert callback ordering, persisted epoch transitions, proposal payload behavior, and strategy-specific decisions without monitor networking. Build tests should catch enum/API drift with `Elector`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.h -->
