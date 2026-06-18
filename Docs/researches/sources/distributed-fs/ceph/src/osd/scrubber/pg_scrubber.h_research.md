# sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.h

## Purpose
Declares `PgScrubber`, the core PG scrub implementation layer behind `ScrubPgIF`, `ScrubMachineListener`, and `ScrubBeListener`, plus map collection status, scrub flags, and scrub perf-counter mappings.

## APIs and Control Flow
`MapsCollectionStatus` tracks local and replica map readiness. `scrub_flags_t` carries priority, auto-repair, after-repair, and deep-on-error flags. `PgScrubber` exposes PG-facing scheduling/operator/message APIs, FSM-facing effects for range selection, map collection, cleanup, and finish, and backend-facing hooks for stats/digest fixes. `PrimaryLogScrub` overrides the hooks that require `PrimaryLogPG`.

## State, Dependencies, and Integration
State includes PG/OSD references, FSM, scrub job, active flags, active target, local resource wrapper, store, backend, map builders, range bounds, error counts, digest-pending count, session counter, preemption state, replica request fields, and config cachers. It depends on `PG`, `ScrubStore`, `ScrubBackend`, scrub FSM interfaces, scrub reservations, and `osd_scrub_sched`.

## Risks and Test Signals
Several base methods assert if not overridden by the PrimaryLog subclass. Many methods assume PG lock, active session, or primary role. Token/epoch fields are central to stale-event safety, while preemption is mutex-protected because writes can race scrub progress. Tests should cover interface dispatch, maps-status transitions, queued/active semantics, preemption reset/adjustment, callback cancellation, and all reported schedule states.
