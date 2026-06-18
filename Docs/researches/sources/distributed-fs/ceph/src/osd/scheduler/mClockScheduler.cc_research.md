# sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.cc

## Purpose
Implements the dmclock-backed OSD scheduler. It combines a strict high-priority queue for immediate/cutoff-priority work with a costed dmclock `PullPriorityQueue` for normal QoS-managed requests.

## APIs and Control Flow
`enqueue()` classifies by scheduler id and priority, routes immediate/high work to `enqueue_high()`, or scales cost, records counters, sets `qos_cost`, and calls `scheduler.add_request()`. `enqueue_front()` front-loads high work and emulates front insertion for normal work by using the high queue at priority 0. `dequeue()` always drains high-priority subqueues before dmclock; dmclock may return a future time, none, or a request. `get_scheduler_op_type()` maps peering and selected EC operations to perf-counter labels.

## State, Dependencies, and Integration
Runtime state is `high_priority`, dmclock scheduler state, `MclockConfig`, and the client registry. It depends on dmclock, Ceph perf counters, message type constants, and `OpSchedulerItem`. `put_mclock_counter()`/`get_mclock_counter()` integrate queue timing and cost accounting.

## Risks and Test Signals
Continuous high-priority traffic can starve dmclock. Non-high `enqueue_front()` bypasses dmclock semantics. `dequeue()` assumes callers avoid empty pulls. Tests should cover high-priority ordering, strict precedence, future returns, scaled cost propagation, counter classification, dump output, and cutoff behavior.
