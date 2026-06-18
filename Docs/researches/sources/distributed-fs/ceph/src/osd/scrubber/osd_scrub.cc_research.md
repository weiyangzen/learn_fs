# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.cc

## Purpose
Implements the OSD-wide scrub service that selects eligible PG scrub targets, applies OSD-level gates, manages local scrub resources, and owns scrub performance counters.

## APIs and Control Flow
`initiate_scrub()` computes restrictions, pops a ready eligible `SchedEntry`, locks the PG, and calls `start_scrubbing()`. `restrictions_on_scrubbing()` checks local concurrency, random backoff, recovery, time window, CPU load, and queued snap trims. `is_sched_target_eligible()` applies those restrictions based on urgency observer rules. `on_config_change()` relocks queued PGs and tells them to recompute schedules. Queue/resource methods forward to `ScrubQueue` and `ScrubResources`.

## State, Dependencies, and Integration
Runtime state includes `ScrubResources`, `ScrubQueue`, CPU count cache, config reference, service listener, and four labeled perf-counter sets. Integration points are OSD tick, heartbeat load average update, admin dump commands, PG scrub-job registration, and PgScrubber perf-counter lookup.

## Risks and Test Signals
The selected target is dequeued before PG locking; PG-level code must requeue on eligible failures. Time windows use local modulo intervals. CPU load uses cached CPU count. Tests should cover each restriction, urgency observer filtering, allowed day/hour wraparound, snaptrim gating, config-change callbacks, and perf-counter lifecycle.
