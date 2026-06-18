# sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.h

## Purpose

`scrub_job.h` declares the per-PG scrub scheduling model. It defines scheduling configuration, target state, and the `ScrubJob` object that tracks shallow/deep scrub deadlines, queue state, urgency, retry issues, and behavior-policy helpers.

## Important APIs, types, and functions

- `must_scrub_t` marks mandatory versus ordinary proposed schedules.
- `sched_params_t` carries a proposed time and mandatory flag.
- `sched_conf_t` groups shallow/deep intervals, randomization ratios, and invalid-stamp behavior.
- `SchedTarget` wraps a `SchedEntry` with a scrubber-local `queued` flag and helpers for reset, urgency raising, level/urgency inspection, and queued element projection.
- `ScrubJob` contains `pgid`, OSD id, `shallow_target`, `deep_target`, registration and blocking flags, `last_issue`, blocked timestamp, `CephContext`, RNG, and log prefix.
- Core methods choose eligible targets, adjust schedules, delay retries, apply operator requests, compute guaranteed fake offsets, expose scheduling state, and manage queued flags.
- Static methods translate `urgency_t` into behavior requirements and exemptions.
- `fmt` formatters serialize `sched_params_t`, `SchedTarget`, `ScrubJob`, and `sched_conf_t`.

## Control flow

`ScrubJob` is constructed with shallow and deep targets for the same PG. Configuration-driven code updates the targets through `adjust_shallow_schedule()` and `adjust_deep_schedule()`. The OSD queue uses `SchedTarget::queued_element()` and comparators to order work, then `ScrubJob` methods report the earliest eligible or earliest future target. Runtime events such as operator commands, failed reservations, blocked state, or completed repairs mutate urgency and `not_before`.

## State and persistence behavior

All scheduling state is in memory and mirrored indirectly by the OSD's scrub queue. `registered` means the OSD manages the job. `queued` flags are duplicated at the target level because the queue owns `SchedEntry` copies while the scrubber tracks whether those copies are enqueued. `blocked` and `blocked_since` support health/query reporting for long object locks. The RNG is per job, which can influence reproducibility in tests unless seeded/mocked externally.

## Dependencies and integration points

The header depends on `scrubber_common.h` for scrub levels, urgency, delay causes, and schedule types; `scrub_queue_entry.h` for queue entries/comparators; Ceph time/format utilities; and `PgScrubber` implementation for behavior referenced in `scrub_job.cc`.

## Risks

The shallow/deep targets must remain consistent with queue contents. If queue flags are not cleared when dequeued or set when enqueued, admin state and scheduling decisions become misleading. Static urgency policy methods encode operational semantics documented in the long table; future urgency additions require updating all helpers and formatters. The header notes that the no-argument `earliest_target()` can be wrong when both targets are eligible.

## Test signals

Tests should exercise `SchedTarget` reset/urgency monotonicity, shallow/deep target selection with both eligible and both future targets, state descriptions for unregistered/queued/scrubbing jobs, blocked flag reporting, and exhaustive urgency policy helper expectations.
