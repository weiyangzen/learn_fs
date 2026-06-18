# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/floating-point.json

## Purpose

This file defines two POWER8 raw PMU events, `PM_FXU_BUSY` and `PM_FXU_IDLE`. Despite the filename, the visible events describe fixed-point unit activity rather than floating-point/vector execution.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. The schema matches other POWER8 raw event files. The two public event names expose whether both FXU units are busy or idle.

## Control flow and integration

During perf build, `jevents.py` converts these entries into generated event tables. Runtime users select the raw events directly with perf. These counters can also be used by derived metrics or external scripts to reason about integer execution-unit pressure.

## State and persistence

There is no mutable state. The event-code mapping and descriptions persist into generated perf metadata. The mismatch between filename and fixed-point event names is also persistent source organization behavior that maintainers need to know.

## Dependencies

Dependencies are POWER8 PMU encodings, FXU hardware semantics, and perf's raw event generation. Integration points are generated PMU tables, `perf list`, and direct `perf stat` event selection.

## Risks

The file name can mislead maintainers looking for floating-point or VSU counters. With only two events, accidental deletion or misclassification would remove the entire category. Event descriptions are short and do not explain SMT, sampling, or attribution details.

## Test signals

Validate JSON, event-code uniqueness, perf PMU generation, and direct event-open behavior for `PM_FXU_BUSY` and `PM_FXU_IDLE` on POWER8. If a broader POWER8 metric references FXU activity, include it in integration checks.
