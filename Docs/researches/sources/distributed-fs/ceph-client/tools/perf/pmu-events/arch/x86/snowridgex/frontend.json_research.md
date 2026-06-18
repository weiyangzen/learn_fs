# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/frontend.json

## Purpose

`frontend.json` is the Snow Ridge X core PMU catalog for frontend instruction-fetch and branch-address-clear behavior. It contains nine events for branch address clears (`BACLEARS.*`), instruction cache accesses/hits/misses, and decode restrictions from wrong predecode length prediction. These aliases help perf users diagnose frontend bubbles caused by branch target correction, instruction cache misses, and decode throughput restrictions.

## Important APIs, Types, and Data Fields

The JSON array uses core event fields `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. The `BACLEARS` family uses `EventCode: "0xe6"` with masks for all, conditional, indirect, return, and unconditional branch clears. `ICACHE.ACCESSES`, `.HIT`, and `.MISSES` use `EventCode: "0x80"` with masks `0x3`, `0x1`, and `0x2`. `DECODE_RESTRICTION.PREDECODE_WRONG` uses `EventCode: "0xe9"` and `UMask: "0x1"` for decode throughput reductions due to wrong instruction length prediction.

## Control Flow and Data Flow

There is no executable control flow. Perf turns the JSON records into aliases, then programs core PMU counters when selected. Counts flow from core frontend hardware to perf output. A typical diagnostic flow starts with `ICACHE.ACCESSES/HIT/MISSES` to understand instruction-cache locality, then checks `BACLEARS.*` to separate branch-redirection cleanup by branch type, and uses `DECODE_RESTRICTION.PREDECODE_WRONG` when frontend throughput is limited by instruction-length prediction rather than cache misses.

## State and Persistence Behavior

The only persisted state is the static event metadata. Runtime branch prediction, instruction cache contents, and decode restriction state are not stored here. Counts are core-scoped and reflect the workload and aggregation mode chosen by perf. No derived metrics are defined, so hit rates or clear rates are computed by downstream tooling from raw counts.

## Dependencies and Integration Points

This file depends on Snow Ridge X core PMU support and perf's pmu-events generator. It integrates with cache events, particularly instruction-cache and memory-bound instruction fetch signals, and with topdown analysis where frontend-bound slots need a concrete cause. It also complements branch prediction and pipeline-clear events in other perf categories.

## Risks and Edge Cases

`ICACHE.ACCESSES` uses a combined mask rather than a separately measured sum, so consumers should not assume accesses always equal hits plus misses under all counting conditions. Branch address clears are not the same as all branch mispredictions; they represent specific frontend correction behavior. Decode restriction events may be very workload-specific and can be hard to trigger in simple smoke tests. Aggregated counts can hide per-core instruction-cache or branch behavior in mixed workloads.

## Test Signals

Static tests should parse the JSON and expose all nine aliases in generated perf tables. Runtime smoke tests should show `ICACHE.ACCESSES` increasing during instruction execution, with larger code-footprint workloads increasing `ICACHE.MISSES`. Branch-heavy tests with indirect, return, conditional, and unconditional branches should move the relevant `BACLEARS.*` rows when the hardware triggers clears. Crafted instruction streams or binaries with difficult length prediction are the best signal for `DECODE_RESTRICTION.PREDECODE_WRONG`.
