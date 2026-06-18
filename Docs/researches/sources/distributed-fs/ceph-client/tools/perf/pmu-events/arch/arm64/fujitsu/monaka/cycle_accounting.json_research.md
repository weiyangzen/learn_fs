<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/cycle_accounting.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/cycle_accounting.json

## Purpose
Monaka cycle-accounting event table for commit bandwidth, no-commit reasons, load completion waits, ROB empty cycles, WFE/WFI, retention, and MOVPRFX-only commit cycles. It is intended to explain where cycles are spent when instructions do not retire or retire at limited width.

## APIs, Types, and Functions
The records are direct Monaka event definitions with `EventName`, `EventCode`, and `BriefDescription`. Important aliases include `LD_COMP_WAIT`, `LD_COMP_WAIT_L1_MISS`, `LD_COMP_WAIT_L2_MISS`, `EU_COMP_WAIT`, `FL_COMP_WAIT`, `BR_COMP_WAIT`, `ROB_EMPTY`, `_0INST_COMMIT` through `_5INST_COMMIT`, `UOP_ONLY_COMMIT`, and `RETENTION_CYCLE`.

## Control Flow, State, and Persistence
The JSON is read during perf event-table generation and persisted as static aliases in the generated binary. At runtime, perf binds these events to the Monaka core PMU through the mapfile CPUID. No state is stored by the file itself; active counter state is owned by the kernel PMU and perf sessions.

## Dependencies and Integration
Depends on Monaka hardware event-code definitions and the perf PMU JSON schema. It integrates with `gcycle.json` for frequency/retention interpretation, `stall.json` for topdown stall classes, and cache/TLB files for diagnosing the root cause of load completion waits.

## Risks and Test Signals
Risks include overlapping no-commit categories, event-code drift from vendor documentation, and ratios exceeding intuitive totals if users sum non-exclusive counters. Test signals are build-time generation success, `perf stat` availability, idle/retention tests increasing `RETENTION_CYCLE`, memory-latency tests increasing `LD_COMP_WAIT*`, and instruction streams showing plausible commit-width distributions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/cycle_accounting.json -->
