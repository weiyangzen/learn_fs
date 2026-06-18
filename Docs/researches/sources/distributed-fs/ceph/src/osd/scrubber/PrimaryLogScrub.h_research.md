# sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.h

## Purpose
Declares `PrimaryLogScrub`, the `PgScrubber` derivative used by `PrimaryLogPG` for backend callbacks that require primary-log-specific APIs.

## APIs and Control Flow
Overrides `_scrub_finish()`, `_scrub_clear_state()`, `get_store_errors()`, `stats_of_handled_objects()`, `add_to_stats()`, and `submit_digest_fixes()`. It stores a typed `PrimaryLogPG* const m_pl_pg` and an `object_stat_collection_t m_scrub_cstat`.

## State, Dependencies, and Integration
The class is an adapter between generic scrub FSM/backend code and PrimaryLogPG object/stat/digest operations. It includes scrub message headers and OSD dependencies because the base scrubber routes primary and replica scrub protocol events.

## Risks and Test Signals
The base class asserts for backend stat/digest hooks, so replicated primary-log PGs must instantiate this subclass. Tests should verify construction, virtual dispatch from `ScrubBackend`, stat reset, and forwarding to `Scrub::Store`.
