# sources/distributed-fs/ceph/src/osd/PGPeeringEvent.h

## Purpose
`PGPeeringEvent.h` defines the event envelope and concrete Boost.Statechart events used by OSD placement-group peering. It packages incoming peering messages, local reservation callbacks, lease events, creation metadata, and simple control events into types that `PeeringState` can react to uniformly.

## Important APIs and Types
- `PGCreateInfo` carries the data needed to instantiate a PG: `spg_t pgid`, creation epoch, `pg_history_t`, `PastIntervals`, and whether creation came from the monitor.
- `PGPeeringEvent` wraps a statechart `event_base` intrusive pointer with `epoch_sent`, `epoch_requested`, a printable description, `requires_pg`, and optional `PGCreateInfo`.
- `PGPeeringEventRef` and `PGPeeringEventURef` provide shared and unique ownership forms used by queues and callbacks.
- Message-backed statechart events include `MInfoRec`, `MLogRec`, `MNotifyRec`, `MQuery`, `MTrim`, `MLease`, and `MLeaseAck`.
- Priority/control events include `RequestBackfillPrio`, `RequestRecoveryPrio`, `DeferRecovery`, `DeferBackfill`, and trivial macro-generated events such as `NullEvt`, `PgCreateEvt`, reservation outcomes, `RecoveryDone`, and `RenewLease`.

## Control Flow
Callers construct a concrete statechart event, then wrap it in `PGPeeringEvent`. The templated constructor stores an intrusive pointer via `evt_.intrusive_from_this()`, records the epoch metadata, builds a stable string description by calling the concrete event's `print()`, and appends `+create_info` when present. `PeeringState` later reads `get_event()` and dispatches to statechart reactions while queueing and logging can use `get_desc()`.

Each concrete event is mostly a typed data holder with a `print()` method. Message wrappers preserve sender PG/shard and message payloads. Lease wrappers carry epoch and lease state. Delay and priority events carry scheduler inputs for recovery/backfill reservation control.

## State and Persistence Behavior
These event types are transient in-memory control records. They do not write persistent state themselves. Their epoch fields are safety gates for peering: consumers can compare the event's sent/requested epoch against current OSD maps before applying state transitions. Optional `PGCreateInfo` is owned by the event envelope and transfers PG creation metadata into the peering state machine.

## Dependencies and Integration Points
- Depends on Boost.Statechart and Boost intrusive pointers.
- Uses OSD types such as `spg_t`, `pg_history_t`, `PastIntervals`, `pg_info_t`, `pg_notify_t`, `pg_query_t`, `pg_lease_t`, and shard identifiers.
- Forward-declares `MOSDPGLog`; the out-of-line `MLogRec` implementation includes the message header.
- Integrated directly by `PG::queue_peering_event()`, `PG::do_peering_event()`, and `PeeringState` custom reactions for message, reservation, lease, and recovery events.

## Risks and Edge Cases
- The templated envelope requires the concrete event to support `intrusive_from_this()` and `print(std::ostream*)`; adding a new event without those conventions will fail at compile time.
- `get_current_event()` style access is by base reference; downstream code must use statechart reaction typing rather than unsafe casts.
- Description strings are built at construction time, so later mutation of the underlying message/event is not reflected in `desc`.
- `requires_pg` must be set carefully for create and non-PG-specific events; incorrect values can make queue handling drop or mishandle legitimate creation events.

## Test Signals
Compile-time coverage is important because most contracts are type-level. Runtime tests should cover queueing events across epoch changes, PG creation events with `PGCreateInfo`, `MLogRec` dispatch into `PeeringState`, and formatting for diagnostics. Lease and reservation events should be exercised by peering/recovery scheduler tests.
