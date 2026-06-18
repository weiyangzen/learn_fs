# sources/distributed-fs/ceph/src/osd/PGPeeringEvent.cc

## Purpose
`PGPeeringEvent.cc` provides the small out-of-line definitions for peering-event support: the mempool object factory for `PGPeeringEvent` and the `MLogRec` constructor/formatter. The implementation keeps heavyweight message printing out of the header while preserving statechart event semantics.

## Important APIs and Functions
- `MEMPOOL_DEFINE_OBJECT_FACTORY(PGPeeringEvent, pg_peering_evt, osd)` registers `PGPeeringEvent` allocation with the OSD mempool helpers used by `MEMPOOL_CLASS_HELPERS()` in the class declaration.
- `MLogRec::MLogRec(pg_shard_t from, MOSDPGLog *msg)` stores the source shard and intrusive pointer to the PG log message.
- `MLogRec::print(std::ostream *out) const` prints the source shard and delegates detailed message formatting to `MOSDPGLog::inner_print()`.

## Control Flow
Construction of `MLogRec` is direct: callers pass the sender shard and raw `MOSDPGLog*`, and the boost intrusive pointer member takes ownership/reference tracking. Printing first emits `"MLogRec from <shard>"`, then calls into the message object to render the log payload.

## State and Persistence Behavior
This file has no persistent state. Its state effects are memory-management related: the mempool factory controls allocation accounting for queued peering events, and the `MLogRec` intrusive pointer keeps the message alive while the statechart event is queued or processed.

## Dependencies and Integration Points
- Includes `osd/PGPeeringEvent.h` for event declarations.
- Includes `include/mempool.h` for factory registration.
- Includes `messages/MOSDPGLog.h` for `inner_print()` and intrusive message ownership.
- Integrated with `PeeringState` reactions that consume `MLogRec` during log exchange.

## Risks and Edge Cases
- `MLogRec::print()` assumes `msg` is non-null. A null `MOSDPGLog*` would dereference during diagnostics.
- Factory registration must match the declaration's mempool helpers; mismatches would affect allocation tracking and possibly build linkage.
- Formatting depends on `MOSDPGLog::inner_print()` remaining safe for partially decoded or otherwise unusual messages.

## Test Signals
Relevant signals are compile/link tests for the mempool factory and peering-message tests that construct and print `MLogRec`. Integration coverage should observe queued `MOSDPGLog` events in `PeeringState` reactions and ensure diagnostics remain useful during peering failures.
