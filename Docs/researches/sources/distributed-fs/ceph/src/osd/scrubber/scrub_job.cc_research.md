# sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.cc

## Purpose

`scrub_job.cc` implements scrub scheduling primitives for a single PG. It maintains shallow and deep scrub targets, randomizes regular schedules, handles operator-forced targets, delays failed targets, chooses the next eligible target, and defines urgency-to-policy helper functions used by OSD scrub scheduling.

## Important APIs, types, and functions

- `SchedEntry::dump()` serializes a queue entry for admin/query output, including PG id, level, urgency, schedule, last issue, and whether the target is forced.
- `SchedTarget::reset()` restores defaults for the same PG/level; `up_urgency_to()` raises urgency monotonically.
- `ScrubJob` constructor initializes shallow/deep targets, the random generator, Ceph context, OSD id, and log prefix.
- `get_target()`, `is_queued()`, `clear_both_targets_queued()`, and `set_both_targets_queued()` are queue-state helpers.
- `adjust_shallow_schedule()` uses uniform randomization around the shallow interval for periodic scrubs and preserves fixed target time for higher urgencies.
- `adjust_deep_schedule()` uses a normal distribution around the deep interval, clamped to two standard deviations, for periodic deep scrubs.
- `guaranteed_offset()` computes an offset large enough to make a faked last-scrub stamp eligible.
- `operator_forced()` marks a shallow/deep target as operator requested or must repair and schedules it at `PgScrubber::scrub_must_stamp()`.
- `earliest_eligible()` and `earliest_target()` use `cmp_entries()`/`cmp_future_entries()` from `scrub_queue_entry.h`.
- `delay_on_failure()` maps delay causes to config retry delays and pushes the target's `not_before`.
- Static policy helpers such as `requires_reservation()`, `observes_noscrub_flags()`, `has_high_queue_priority()`, and `is_repair_implied()` translate urgency into behavior gates.

## Control flow

The OSD owns a `ScrubJob` per PG while the PG is registered for scrub scheduling. Configuration or PG state updates call the adjust methods to compute future shallow/deep schedule times. The OSD scrub queue asks for the earliest target, and when a target is ready `earliest_eligible()` identifies which scrub should run. Operator commands raise urgency and set immediate timestamps. If start or mid-scrub work fails, `delay_on_failure()` postpones retry and records `last_issue`.

## State and persistence behavior

State is in memory: two `SchedTarget`s, registration/blocked flags, last delay cause, blocked-since timestamp, and random generator. The job does not persist schedules itself; its state is reflected into the OSD scrub queue and admin output. Retry delays derive from runtime config keys such as `osd_scrub_retry_delay`, `osd_scrub_retry_after_noscrub`, `osd_scrub_retry_pg_state`, `osd_scrub_retry_trimming`, and `osd_scrub_retry_new_interval`.

## Dependencies and integration points

The implementation integrates with `PgScrubber` for the must-scrub timestamp, `scrub_queue_entry.h` comparators, `scrubber_common.h` delay and schedule types, `CephContext` config, Ceph debug logging, and `ceph::Formatter` output.

## Risks

Scheduling decisions are priority-sensitive. Incorrect comparator use can starve a target or run lower-priority work first. Randomization must be disabled for forced/repair urgencies or operator requests could be delayed. `earliest_target()` without `now` is documented as potentially wrong when both targets are already eligible. Delay cause mapping changes retry behavior and can make PGs appear stuck if too long. Static urgency policy helpers must stay consistent with the table documented in the header.

## Test signals

Useful tests include deterministic comparator cases for ripe and future entries, shallow/deep randomization boundaries, forced scrub immediacy, delay cause to config-key mapping, blocked/queued state descriptions, and each urgency's policy exemptions for flags, reservations, load, recovery, max concurrency, and repair limits.
