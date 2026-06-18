# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pmc.json

## Purpose
`pmc.json` defines 23 POWER8 raw PMU events related to performance monitor counter control and threshold behavior. It covers PMC overflow aliases, PMC rewind/save events, run PURR/SPURR accounting, a suspended counter marker, and threshold met/not-met or threshold-exceeded encodings.

These are lower-level control/status events rather than workload-domain counters. They are useful for diagnosing counter overflow, threshold configuration, sampling control, and run-timebase accounting.

## Important schema and data surface
- Schema: array of objects with `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`.
- Count: 23 raw event rows.
- Counter events: `PM_PMC1_OVERFLOW` through `PM_PMC6_OVERFLOW`, plus PMC2/PMC4 rewind and saved events.
- Run accounting events: `PM_RUN_PURR` and `PM_RUN_SPURR`.
- Counter-off marker: `PM_SUSPENDED` with code `0x0`.
- Threshold events: `PM_THRESH_EXC_32`, `PM_THRESH_EXC_64`, `PM_THRESH_EXC_128`, `PM_THRESH_EXC_256`, `PM_THRESH_EXC_512`, `PM_THRESH_EXC_1024`, `PM_THRESH_EXC_2048`, `PM_THRESH_EXC_4096`, `PM_THRESH_MET`, and `PM_THRESH_NOT_MET`.

## Control flow and integration
At build time, `jevents.py` ingests `pmc.json` with the rest of the POWER8 directory and emits perf aliases for these hardware events. At runtime, perf users can select the aliases directly. The file is not a major dependency for `metrics.json`; its role is more diagnostic and control-oriented than high-level metric computation.

## State and persistence behavior
This is static metadata only. The actual overflow, rewind, saved, suspended, and threshold states are hardware/runtime PMU behavior. The JSON persists names, codes, and descriptions that perf exposes to users.

## Dependencies
- Depends on POWER8 PMU support for PMC overflow, rewind, saved-value, PURR/SPURR, and threshold encodings.
- Depends on perf PMU-events generation and the powerpc mapfile selecting the `power8` directory for matching PVRs.
- Integrates with perf event selection and listing; it has little direct coupling to derived metrics compared with `pipeline.json` and `other.json`.

## Risks and edge cases
- `PM_SUSPENDED` uses event code `0x0`; validation should allow this even though many event-code checks assume nonzero hex.
- Threshold descriptions are inconsistent in detail, and `PM_THRESH_EXC_64` has a `BriefDescription` that appears unrelated (`IFU non-branch finished`) while the public description states threshold exceeded by 64. That should be treated as a documentation risk.
- Overflow and rewind events may be platform- or configuration-sensitive; availability in `perf list` does not guarantee useful counts in arbitrary sessions.
- Counter-control aliases are easy to misuse as workload metrics; documentation should keep them clearly separated from architectural performance ratios.

## Test signals
- JSON/schema validation for all 23 rows, allowing `EventCode` `0x0`.
- Full-directory uniqueness validation for `EventName`.
- Generator/build validation through the perf PMU-events path.
- Runtime smoke tests can list/select representative events: `pm_pmc1_overflow`, `pm_run_purr`, `pm_run_spurr`, `pm_thresh_met`, and `pm_suspended`.
- Manual review of threshold descriptions is warranted, especially `PM_THRESH_EXC_64`.
