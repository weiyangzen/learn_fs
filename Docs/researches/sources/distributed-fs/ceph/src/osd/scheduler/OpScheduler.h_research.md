# `sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.h`

## Purpose

`OpScheduler.h` declares the scheduler abstraction used by OSD shards to order `OpSchedulerItem` work and provides an adapter from Ceph's classed `OpQueue` implementations to that abstraction. It is the interface boundary between OSD worker queues and concrete scheduling policies such as weighted priority queue and mClock.

## Important APIs And Types

- `using client = uint64_t` is the queue owner/client key type.
- `using WorkItem = std::variant<std::monostate, OpSchedulerItem, double>` is the dequeue result type, allowing no item, a real op item, or scheduler-specific delay/cost feedback.
- `class OpScheduler` declares `enqueue()`, `enqueue_front()`, `empty()`, `dequeue()`, `dump()`, `print()`, `get_type()`, optional `get_cost_per_io()`, and a virtual destructor.
- `OpSchedulerRef` is `std::unique_ptr<OpScheduler>`.
- `make_scheduler()` is the factory implemented in `OpScheduler.cc`.
- `template <typename T> class ClassedOpQueueScheduler final` adapts an `OpQueue<OpSchedulerItem, client>`-like type.

## Control Flow And State Behavior

`ClassedOpQueueScheduler` stores a priority cutoff and the concrete queue. `enqueue()` and `enqueue_front()` read priority, cost, and owner from `OpSchedulerItem`. Items with `priority >= cutoff` enter the strict queue (`enqueue_strict` or `enqueue_strict_front`) and bypass cost accounting; lower-priority items enter the classed queue with owner, priority, and cost. `dequeue()`, `empty()`, `dump()`, `print()`, and `get_type()` delegate to the underlying queue.

`OpScheduler::get_cost_per_io()` asserts by default, indicating it is only valid for schedulers that override it, such as mClock. Calling it on WPQ-style implementations is a programming error.

## Persistence Behavior

No persistent state is stored here. Scheduler queues are in-memory runtime state. The only durable coupling is indirect: `get_type()` returns `op_queue_type_t` from `osd_types.h`, and OSD configuration/state may report that type.

## Dependencies And Integration Points

The header includes `CephContext`, `OpQueue`, `MonClient`, `OpSchedulerItem`, and `ceph_assert`. Concrete integrations include `WeightedPriorityQueue` through the adapter and `mClockScheduler` through the factory. OSDShard uses this interface to enqueue client ops, peering events, scrub events, recovery, and deletes while worker threads consume `WorkItem` results.

## Risks And Edge Cases

- The cutoff comparison is `>=`, so a priority exactly equal to `op_queue_cut_off` becomes strict/immediate.
- Strict queueing ignores cost; misconfigured priorities can starve lower classes.
- `WorkItem` includes `double`, so consumers must handle scheduler delay/control results and not assume every dequeue returns an op.
- The adapter assumes `T` implements a specific `OpQueue` surface: strict/front enqueue APIs, classed enqueue APIs, `dequeue`, `dump`, `print`, and `get_type`.
- `get_cost_per_io()` default asserts; generic code must branch by scheduler type or virtual capability before calling it.

## Test Signals

Focused tests should verify cutoff behavior, `enqueue_front()` ordering, strict vs non-strict queue selection, `dump()`/`print()` delegation, `get_type()` propagation, and safe handling of all `WorkItem` alternatives. Integration signals include OSD op latency under mixed priorities and scheduler dump output.
