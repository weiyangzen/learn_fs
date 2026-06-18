# sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.h

## Purpose
Declares `mClockScheduler`, an `OpScheduler` implementation using dmclock for normal work and a separate strict queue for immediate/high-priority work.

## APIs and Control Flow
The class implements `enqueue`, `enqueue_front`, `dequeue`, `empty`, `dump`, `print`, and `get_type`. `mclock_queue_t` is a dmclock pull priority queue keyed by `{SchedulerClass, client_profile_id_t}`. `SubQueue` is a descending-priority map of lists. Constructors initialize `MclockConfig`, dmclock aging/check intervals, at-limit behavior, and anticipation timeout.

## State, Dependencies, and Integration
State is runtime-only: `ClientRegistry`, `MclockConfig`, dmclock queue, cutoff priority, and high-priority subqueues. It integrates with OSD scheduler polymorphism, config, perf counters, and scrub cost calculation via `get_cost_per_io()`.

## Risks and Test Signals
`num_shards` must be positive. The high-priority invariant requires no empty subqueue lists. Current scheduler id ignores client profile. Tests should cover construction, `empty()`, `print()`, `get_type()`, default/custom timer construction, and cost-per-IO access.
