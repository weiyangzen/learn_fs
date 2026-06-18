<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-ddrc.json

## Purpose
Hip08 uncore DDR controller PMU event table. It exposes memory read/write flux, command counts, precharge/activate commands, rank changes, and read/write direction changes.

## APIs, Types, and Functions
Records use uncore schema fields `EventName`, `ConfigCode`, `BriefDescription`, and `Unit`. Aliases are `flux_wr`, `flux_rd`, `flux_wcmd`, `flux_rcmd`, `pre_cmd`, `act_cmd`, `rnk_chg`, and `rw_chg`, all associated with the DDRC unit.

## Control Flow, State, and Persistence
At perf build time, the uncore JSON is encoded into PMU metadata. Runtime perf uses the uncore PMU unit name and config code rather than core event codes; counter state belongs to the DDRC PMU instance during a measurement.

## Dependencies and Integration
Depends on Hip08 uncore PMU driver naming and config-code interpretation. It integrates with core memory-bound metrics, HHA home-agent events, and L3C events to explain bandwidth and DRAM command behavior.

## Risks and Test Signals
Risks include uncore unit naming mismatches, multi-controller aggregation mistakes, permissions or kernel support limiting uncore access, and flux units needing conversion before bandwidth comparisons. Test signals are `perf list` uncore visibility, memory bandwidth workloads increasing `flux_rd`/`flux_wr`, row-locality tests affecting precharge/activate counts, and multi-controller runs showing expected distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-ddrc.json -->
