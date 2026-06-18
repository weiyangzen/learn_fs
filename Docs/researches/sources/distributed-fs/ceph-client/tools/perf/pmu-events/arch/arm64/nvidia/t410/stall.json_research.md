# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/stall.json

## Purpose
This 33-entry T410 Arm64 topic file defines frontend, backend, slot, memory-bound, CPU-bound, dispatch, issue-queue, and synchronization stall events. These entries are central to T410 topdown-style metrics and bottleneck diagnosis.

## Important Data Fields
The file combines `ArchStdEvent` rows such as `STALL_FRONTEND` and `STALL_BACKEND` with T410-specific `EventCode` rows such as `STALL_SLOT_FRONTEND_WITHOUT_MISPRED`. Every row has a `PublicDescription` explaining the stall source or accounting unit.

## Control Flow And Integration
Build-time flow is standard PMU JSON ingestion through `jevents.py`; runtime flow is perf alias lookup for the T410 CPU table. The events are integration points for `metrics.json` in the same CPU directory and generic topdown views because stall-slot names often appear in `MetricExpr` formulas.

## State, Dependencies, Risks, And Tests
There is no mutable state. The main dependencies are CPU slot accounting, T410 PMU event-code correctness, and compatibility with metric formulas. Risks are high because stall events are easy to misinterpret: slot events, cycle events, frontend/backend categories, and misprediction exclusions must not be mixed casually. Tests should include JSON validity, `metric_test.py`/parse-metric coverage for formulas that reference these names, and sanity checks that topdown percentages remain bounded under known workloads.
