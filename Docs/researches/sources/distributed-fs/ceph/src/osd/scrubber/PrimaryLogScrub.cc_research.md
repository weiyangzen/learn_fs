# sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.cc

## Purpose
Specializes `PgScrubber` for `PrimaryLogPG`, adding replicated-primary-log stat reconciliation, digest repair submission, store-error listing, and active object-stat accounting.

## APIs and Control Flow
`get_store_errors()` reads object or snapset errors from `Scrub::Store`. `submit_digest_fixes()` creates PrimaryLogPG op contexts, updates or clears data/omap digests, submits MODIFY log entries, and queues a digest-update event after all success callbacks run. `_scrub_finish()` compares collected scrub stats to PG stats, fixes invalid or mismatched stats, logs real stat mismatches, and clears object contexts after repair. `stats_of_handled_objects()` accounts for objects already before the current scrub range.

## State, Dependencies, and Integration
`m_scrub_cstat` is transient per-session stat accumulation. Persistent effects include PG log digest updates, `recovery_state.update_stats()`, `publish_stats_to_osd()`, and PG info sharing. Dependencies include `PrimaryLogPG`, object contexts, OSD cluster log, `Scrub::Store`, and scrub backend digest-fix types.

## Risks and Test Signals
Missing object contexts and mismatched object-info names reduce pending digest updates and log errors. `num_digest_updates_pending` is assigned per chunk, assuming no old chunk callbacks remain. Tests should cover digest set/clear, callback completion, stat mismatch branches, invalid stats repair, repair fixed-count behavior, and error-list selection.
