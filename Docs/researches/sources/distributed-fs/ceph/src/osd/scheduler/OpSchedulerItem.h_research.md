# sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.h

## Purpose
Defines the move-only `OpSchedulerItem` wrapper and the `OpQueueable` hierarchy used by OSD op queues. It gives schedulers a uniform view of PG ordering, queue sharding, op cost, priority, owner, map epoch, scheduler class, and eventual `run()` dispatch.

## APIs and Control Flow
`OpQueueable` is the polymorphic contract. `PGOpQueueable` binds queue and ordering tokens to a `spg_t`. Concrete queueables include client ops, peering events, snap trim, scrub FSM events, recovery work, deletes, recovery contexts, and recovery protocol messages. Schedulers inspect class/priority/cost, then OSD dispatch calls the concrete `run()` implementation in `OpSchedulerItem.cc`. EC read classification intentionally routes recovery reads away from immediate class when priority indicates recovery/backfill.

## State, Dependencies, and Integration
State is transient scheduling metadata plus ownership of the underlying queueable. `qos_cost` is set only when mClock queues the item through dmclock proper. Dependencies include `OpRequest`, `PG`, `PGPeeringEvent`, `MOSDOp`, `SchedulerClass`, and thread-pool handles. Integration points include `mClockScheduler`, OSDService queue helpers, PG peering/recovery, snap trimming, and scrub event delivery.

## Risks and Test Signals
The base `peering_requires_pg()` aborts unless overridden. Scheduler-class mistakes can starve client or recovery work, especially for EC subops. Tests should cover class selection, formatting, move ownership, scrub-token/event propagation, reserved pushes, and visibility of `qos_cost` only on dmclock-queued items.
