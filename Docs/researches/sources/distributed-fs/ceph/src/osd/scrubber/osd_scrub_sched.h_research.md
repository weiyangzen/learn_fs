# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.h

## Purpose
Declares OSD scrub scheduling interfaces: `ScrubSchedListener` for OSDService callbacks and `ScrubQueue` for storing queued PG scrub targets.

## APIs and Control Flow
`ScrubSchedListener` supplies node id, locked PG lookup, remote scrub reserver access, and snap-trim queue totals. `ScrubQueue` exposes enqueue/dequeue/remove, `pop_ready_entry()`, `get_pgs()`, dump/iteration, and blocked-PG accounting. `EntryPred` and `EligibilityPred` keep queue policy caller-defined. `time_now()` is virtual for tests.

## State, Dependencies, and Integration
State is `jobs_lock`, `not_before_queue_t<SchedEntry>`, service reference, context pointer, and `blocked_scrubs_cnt`. It integrates with `OsdScrub`, `PgScrubber`/`ScrubJob`, `AsyncReserver`, and admin dumps.

## Risks and Test Signals
The source diagram highlights split ownership between OSD queue copies and PG-owned jobs. Lock ordering is critical: no PG locks under `jobs_lock`. Tests should use mock listeners and overridden time to validate selection, locking boundaries, blocked counts, and queue state transitions.
