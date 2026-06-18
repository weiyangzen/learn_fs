# sources/distributed-fs/ceph/src/osd/scrubber/scrub_queue_entry.h

## Purpose

`scrub_queue_entry.h` defines the queueable scrub scheduling entry and ordering helpers used by the OSD scrub queue and `ScrubJob`. It formalizes urgency levels, schedule fields, queue projection functions, and priority comparators.

## Important APIs, types, and functions

- `urgency_t` enumerates periodic regular scrubs and higher-priority scrubs: `must_scrub`, `after_repair`, `repairing`, `operator_requested`, and `must_repair`.
- `SchedEntry` stores `spg_t`, scrub level, urgency, `scrub_schedule_t`, and last delay cause. `dump()` is implemented in `scrub_job.cc`.
- `cmp_ripe_entries()` orders eligible entries by higher urgency, earlier scheduled-at time, higher level ordering, earlier not-before, then a tie breaker.
- `cmp_future_entries()` orders non-eligible entries by earliest not-before, higher urgency, earlier scheduled-at, then level.
- `cmp_entries()` chooses the ripe comparator when one or both entries are eligible at a supplied time and future comparator otherwise.
- `project_not_before()` and `project_removal_class()` adapt `SchedEntry` to the generic not-before queue.
- `operator<()` delegates eligible ordering to `cmp_ripe_entries()`.
- `fmt` formatters stringify urgency and schedule entries for logs.

## Control flow

When scrub targets are enqueued, the generic queue projects `not_before` for readiness and uses `operator<()`/comparators to select eligible work. `ScrubJob` also uses `cmp_entries()` to decide whether shallow or deep work should run first for a PG at a given time.

## State and persistence behavior

`SchedEntry` is a small value object copied into queues. It carries transient scheduling state but no persistence. The removal class projection groups entries by PG id so queue users can remove or replace all entries for a PG.

## Dependencies and integration points

The header depends on `scrubber_common.h` for `scrub_schedule_t`, scrub levels, and `delay_cause_t`, plus Ceph formatting/time types. It is included by `scrub_job.h` and OSD scrub scheduling code.

## Risks

Comparator semantics determine scrub fairness and operator command latency. The ordering intentionally treats higher urgency as "better" by comparing `r.urgency <=> l.urgency`; reversing this would invert priority. Future-entry ordering prioritizes earliest `not_before`, so scheduled-at time is secondary until the entry ripens. Tie handling returns `greater`, which can affect stability in ordered containers.

## Test signals

Comparator tests should cover all combinations of ripe/future shallow/deep entries, urgency precedence, scheduled-at ties, not-before ties, removal by PG id, and formatting for admin output.
