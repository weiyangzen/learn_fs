# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pipeline.json

## Purpose

This file defines 101 POWER10 raw PMU events for front-end, dispatch, issue, execution, load-store, branch, completion, synchronization, and L2 translation invalidation behavior. It is the main raw-event backing store for the CPI stall breakdowns in `metrics.json`.

## APIs, types, and schema

Each entry has `EventCode`, `EventName`, and `BriefDescription`. Event names include `PM_EXEC_STALL_*`, `PM_DISP_STALL_*`, `PM_CMPL_STALL_*`, `PM_LSU_*_FIN`, `PM_VSU*_ISSUE`, `PM_FLUSH*`, `PM_NTC_*`, `PM_BR_FIN`, `PM_FXU_ISSUE`, `PM_1PLUS_PPC_DISP`, and L2 TLB invalidation delay events. There are no functions or classes; the public contract is the raw PMU event namespace.

## Control flow and integration

`jevents.py` converts these event definitions into generated perf event tables. Runtime consumers either open these events directly or evaluate metrics that divide these counters by `PM_RUN_INST_CMPL` or other baseline counters. The control model is declarative: categories such as dispatch stalls, execution stalls, and completion stalls are represented as independent counters that metrics combine into CPI contributions.

## State and persistence

The file does not store mutable state. The event names and codes persist into the built perf binary. Because many `metrics.json` formulas refer to this file's names, renaming or deleting a pipeline event can break metric generation or produce unresolved runtime metrics.

## Dependencies

Dependencies include POWER10 PMU encodings, perf's PMU event generator, and related files that provide denominator counters such as `PM_RUN_INST_CMPL` and `PM_CYC`. Integration points include `metrics.json`, `pmc.json`, `pmu-events/metric.py`, and runtime PMU scheduling in `util/pmu.c`.

## Risks

This file has broad blast radius because it backs the central CPI model. Stall events with overlapping descriptions can be misinterpreted as exclusive when hardware may count them differently. Lack of `PublicDescription` limits user-facing detail. Event-code mistakes can corrupt multiple derived metrics. The source also contains specialized names such as `PM_EXEC_STALL_UNKNOWN`, `PM_DISP_STALL_HELD_HALT_CYC`, and L2 TLBIE/SLBIE delay events that need hardware-specific verification.

## Test signals

Test with JSON parsing, event-code uniqueness, generated `pmu-events.c` build, and `perf list` visibility for representative pipeline events. Metric parser tests should ensure all `PM_DISP_STALL_*`, `PM_EXEC_STALL_*`, and `PM_CMPL_STALL_*` references in `metrics.json` resolve. Hardware smoke tests should compare high-level CPI metrics against direct raw event counts.
