# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/floating-point.json

## Purpose

`floating-point.json` is the Snow Ridge X core PMU catalog for a small set of floating-point execution and assist events. It contains three events: FP divider busy cycles, floating-point operations retired with microcode assists, and retired floating-point divide uops. These aliases help perf users identify workloads limited by FP division throughput or by expensive FP assists.

## Important APIs, Types, and Data Fields

The file is a JSON array of core event records with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. All three rows use counters `0,1,2,3`. `CYCLES_DIV_BUSY.FPDIV` uses `EventCode: "0xcd"` and `UMask: "0x2"` to count cycles when the floating-point divider is busy. `MACHINE_CLEARS.FP_ASSIST` uses `EventCode: "0xc3"` and `UMask: "0x4"` to count retired FP operations requiring microcode assist. `UOPS_RETIRED.FPDIV` uses `EventCode: "0xc2"` and `UMask: "0x8"` to count retired FP divide uops, including x87 and SSE and x87 sqrt.

## Control Flow and Data Flow

The file has no internal control flow. Perf parses the records into event aliases and programs core PMU counters when users select them. Data flows from core hardware counters into perf counts or samples. The analysis flow is to compare divider busy cycles with retired FP divide uops to infer divider pressure or latency, and to track FP assist events when unusual inputs, denormals, exceptions, or instruction forms cause microcode intervention.

## State and Persistence Behavior

Only the static metadata is persisted. Runtime divider occupancy, retired uops, and machine clear or assist behavior are hardware execution state. Counts are per core or per task depending on perf mode and aggregation. No metric expressions are defined, so higher-level ratios such as busy cycles per divide uop must be computed externally.

## Dependencies and Integration Points

This file depends on Snow Ridge X core PMU support and perf's generated event tables. It integrates with `counter.json` for core counter availability, cache/backend events when FP workloads are also memory-bound, and frontend events when assists or clears interact with pipeline refetch/redecode behavior. It is useful for math kernels, vectorized code, numerical libraries, and workloads sensitive to denormal or exceptional FP behavior.

## Risks and Edge Cases

These events do not cover all FP operations; they focus on division, square root through the divide-uop row, and assists. A workload can be FP-heavy without moving these counters if it mainly uses adds, multiplies, or vector fused operations. Assist counts can be rare and input-sensitive, so tests need inputs that trigger the hardware condition. Aggregating across cores can hide a single hot thread's divider pressure. Counter pressure can cause multiplexing if these events are combined with many other core events.

## Test Signals

Static tests should parse the JSON and generate aliases for all three event names. Runtime smoke tests should run a tight floating-point divide or sqrt workload and observe `CYCLES_DIV_BUSY.FPDIV` and `UOPS_RETIRED.FPDIV` increase. Inputs known to trigger FP assists should move `MACHINE_CLEARS.FP_ASSIST`; ordinary multiply/add loops should provide a low baseline for these specific counters.
