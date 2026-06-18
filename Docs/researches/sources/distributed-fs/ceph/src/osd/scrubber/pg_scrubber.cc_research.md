# sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.cc

## Purpose
Implements the PG scrubber core: scheduling target handling, FSM event forwarding, chunk range selection, primary/replica scrub-map construction, map comparison, persistent error storage, repair/stat updates, preemption/blocking, and query/debug output.

## APIs and Control Flow
`start_scrub_session()` verifies active primary, clean state, snaptrim state, no-scrub flags, and local resources, then freezes `m_active_target`, sets scrub flags, removes queued siblings, and queues a scrub work item. `select_range()` chooses `[m_start,m_end)` using shallow/deep chunk config, avoids splitting clone/head groups, and checks range availability. `get_replicas_maps()` sends `MOSDRepScrub`; replicas handle `replica_scrub_op()`, build maps, clean metadata, and reply with `MOSDRepScrubMap`. `maps_compare_n_cleanup()` compares maps, persists errors, repairs snap mapper metadata, advances the range, and requeues waiting writes. `scrub_finish()` handles auto repair caps, follow-up deep scrub, result stats, failed repair, recovery events, cleanup, and future schedule updates.

## State, Dependencies, and Integration
Persistent effects include PG state bits, scrub timestamps/error counters, OMAP error store writes, object digest fixes through subclass hooks, snap mapper fixes, PG info sharing, and recovery events. Runtime state includes `m_active`, `m_queued_or_active`, active target, map builders, backend, store, callbacks, preemption data, chunk bounds, maps status, and cached config. Dependencies include `ScrubMachine`, `ScrubBackend`, `ScrubStore`, `OSDService`, `PGBackend`, `SnapMapper`, scrub messages, and `ScrubJob`.

## Risks and Test Signals
Stale epoch/token checks protect against interval changes and obsolete replica work. Queue state is split between OSD queue copies and PG targets. Unexpected replica backend errors abort. Snap mapper repairs wait synchronously for apply. Tests should cover scheduling failures/requeues, operator commands, interval cleanup, range clone boundaries, write preemption/blocking, map collection, auto-repair limits, digest update completion, and query states.
