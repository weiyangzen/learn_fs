# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/pipeline.json

## Purpose

`pipeline.json` defines 101 Skylake PMU events for branch behavior, clock cycles, cycle activity, execution port utilization, load-blocking, machine clears, resource stalls, reservation-station state, uop dispatch/issue/execute/retire, and retired instruction classes. It is the main low-level pipeline behavior event catalog for Skylake.

Major clusters include branch retired/mispredict events, `CPU_CLK_UNHALTED.*`, `CYCLE_ACTIVITY.*`, `EXE_ACTIVITY.*`, `INST_RETIRED.*`, `INT_MISC.*`, `LD_BLOCKS.*`, `LSD.*`, `MACHINE_CLEARS.*`, `UOPS_DISPATCHED_PORT.PORT_0` through `.PORT_7`, `UOPS_EXECUTED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`.

## Important schema/API surface

Important fields are standard perf event descriptor fields:

- `EventName`: public aliases such as `BR_INST_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `CYCLE_ACTIVITY.STALLS_TOTAL`, `EXE_ACTIVITY.1_PORTS_UTIL`, `INST_RETIRED.ANY`, `RESOURCE_STALLS.SB`, and `UOPS_RETIRED.RETIRE_SLOTS`.
- `EventCode`/`UMask`: raw PMU selector and unit mask.
- `Counter`, `CounterMask`, `AnyThread`, `EdgeDetect`, and `Invert`: counter constraints and qualifier bits, especially for cycles, stalls, and thresholded uop counts.
- `PEBS`: precise sampling support for selected retired branch and instruction events, including PEBS variants named explicitly such as `BR_INST_RETIRED.ALL_BRANCHES_PEBS` and `BR_MISP_RETIRED.ALL_BRANCHES_PEBS`.
- `BriefDescription`, `PublicDescription`, `SampleAfterValue`: visible perf documentation and default sampling periods.

## Control flow and integration

Perf exposes these descriptors as Skylake aliases and uses them for direct event selection and metric formulas. Many top-down metrics rely on this file's events: clocks, instructions, uops retired, bad speculation, port utilization, and stall counters are foundational to throughput and pipeline-breakdown calculations.

Events are programmed through generic PMU counters without the offcore or frontend MSR-filter complexity seen in the cache/memory/frontend files. The control-flow complexity is instead in counter scheduling: port events, uop-cycle thresholds, and stall events may compete for the same limited generic counters.

## State and persistence behavior

The JSON has no mutable state. Runtime state is PMU counter values, optional PEBS samples for precise events, and perf's multiplexing/scheduling state. Because this file includes core throughput events, measurements can be sensitive to SMT, frequency scaling, NMI watchdog reservations, and multiplexing.

## Dependencies

The file depends on Skylake PMU encodings, perf's event parser, CPU model mapping, PEBS support for precise retired events, and kernel scheduling of constrained events. Top-down metrics in adjacent files depend on these aliases retaining stable names and semantics.

## Risks and maintenance notes

Semantic overlap is a key risk. For example, `CPU_CLK_THREAD_UNHALTED.*` and `CPU_CLK_UNHALTED.*` variants differ in thread/core/reference semantics; choosing the wrong alias changes normalization. `INST_RETIRED.ANY`, `.ANY_P`, `TOTAL_CYCLES_PS`, and `PREC_DIST` are similarly specialized.

Some branch events have PEBS-specific variants and non-PEBS variants. Tooling should not collapse names just because descriptions are similar. Uop and port utilization events are often used in ratios; wrong counter masks, any-thread flags, or event aliases can distort top-down calculations.

Counter pressure is likely in real profiles because this file exposes many desirable events but Skylake has only four generic counters. Users and tests should expect multiplexing unless event sets are carefully chosen or fixed counters are used for cycles/instructions where available.

## Test signals

Static validation should check JSON syntax, required fields for all 101 entries, unique event names, and valid counter lists. Runtime smoke tests should include `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, `UOPS_RETIRED.RETIRE_SLOTS`, one `UOPS_DISPATCHED_PORT.PORT_*`, one branch retired event, and one `CYCLE_ACTIVITY.*` event. Metric integration tests should verify top-down formulas still resolve their pipeline aliases after any rename or encoding update.
