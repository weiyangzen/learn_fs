# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.cc

## Purpose
Implements `ScrubQueue`, the OSD-local `not_before_queue_t` wrapper for queued PG scrub targets.

## APIs and Control Flow
`enqueue_scrub_job()` queues both shallow and deep targets. `enqueue_target()` queues one target. `remove_from_osd_queue()` removes all entries for a PG; `dequeue_target()` removes a specific level. `pop_ready_entry()` advances queue time and dequeues the first entry satisfying the supplied eligibility predicate. `dump_scrubs()`, `for_each_job()`, and `get_pgs()` provide admin/debug traversal. Blocked-PG methods maintain an atomic counter.

## State, Dependencies, and Integration
`jobs_lock` protects `to_scrub`. The queue stores copied `SchedEntry` values from PG-owned `ScrubJob` targets. It depends on `not_before_queue_t`, `SchedEntry`, `SchedTarget`, `ScrubJob`, and `ScrubSchedListener`. `OsdScrub` owns it and supplies policy.

## Risks and Test Signals
Callers must not acquire PG locks while holding `jobs_lock`. Queue copies can diverge if PG target queued flags are not maintained. Tests should cover ready ordering, predicate filtering, remove-by-PG and remove-by-level, dump eligibility, and blocked counter underflow assertions.
