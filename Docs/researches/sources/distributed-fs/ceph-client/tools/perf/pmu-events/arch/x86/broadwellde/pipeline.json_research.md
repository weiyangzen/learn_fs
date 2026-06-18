# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/pipeline.json

## Purpose
Broadwell-DE pipeline, branch, retirement, execution-port, resource-stall, and cycle-activity event catalog. It defines 137 events used to analyze branch behavior, bad speculation, uop issue/execute/retire flow, stalls, port pressure, machine clears, load blocking, loop stream detector behavior, and core clocking.

## Important APIs, Types, and Functions
Entries use the standard perf PMU event fields. All 137 have `EventName`, `Counter`, `SampleAfterValue`, and `BriefDescription`; 133 include `EventCode`, 132 include `UMask`, 94 include `PublicDescription`, 32 include `CounterMask`, 13 include `AnyThread`, 13 include `PEBS`, 6 include `Invert`, 4 include `Errata`, and 2 include `EdgeDetect`. Major event families include `BR_INST_EXEC`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CPU_CLK_THREAD_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `RS_EVENTS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_EXECUTED_PORT`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

## Control Flow
Perf expands aliases from this file into event programming requests. The derived metrics file consumes these events throughout the top-down hierarchy: branch and machine-clear events feed bad speculation and resteer metrics; uop issued/retired/executed events feed slot, retiring, and execution efficiency metrics; port events feed port utilization; cycle activity and resource stalls feed backend and memory/core-bound metrics.

## State and Persistence
The file is static PMU metadata. Runtime state includes counter allocation, any-thread counting for physical-core views, PEBS sampling for selected retired branch or instruction events, edge detection for transition events, and inversion/counter-mask qualifiers for cycle conditions. Persistent semantics must track Broadwell-DE pipeline naming and event encodings.

## Dependencies and Integration
This file is central to `bdwde-metrics.json` and integrates with frontend, cache, memory, floating-point, and other event files. Counter pressure is significant because many formulas combine events from this file with cache and frontend operands; `counter.json` and metric constraints determine whether metrics can be measured together or require multiplexing.

## Risks
Risks include grouped measurements exceeding the 4 generic core counters, SMT and any-thread aliases being mixed incorrectly, PEBS events being treated as ordinary precise-free counters, and cycle-qualified aliases being misread as raw occurrence counts. Port utilization metrics are sensitive to event family choice, and bad speculation metrics can be distorted by machine clears, recovery cycles, and multiplexing.

## Test Signals
Run JSON validation, check `perf list` for all major families, and use synthetic workloads for predictable branch mispredicts, port pressure, divider activity, memory stalls, and retirement throughput. Metric smoke tests should include `TopdownL1`, `BadSpec`, `PortsUtil`, `Pipeline`, `Branches`, `Retire`, and backend/core-bound groups, with special attention to SMT and counter multiplexing.
