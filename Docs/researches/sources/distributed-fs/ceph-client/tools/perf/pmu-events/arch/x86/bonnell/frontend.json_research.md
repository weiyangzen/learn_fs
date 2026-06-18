# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/frontend.json

## Purpose

This file defines 11 Bonnell frontend events. It covers branch address clears, instruction-cache access/hit/miss events, instruction-fetch memory stalls, decode stalls, decoded macro-instruction categories, and micro-sequencer uop cycles.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, and `BriefDescription`. Event families include `BACLEARS`, `CYCLES_ICACHE_MEM_STALLED`, `DECODE_STALL`, `ICACHE`, `MACRO_INSTS`, and `UOPS.MS_CYCLES`. `CounterMask` appears where cycle qualification matters.

## Control Flow

`jevents.py` converts each record to generated aliases selected for Bonnell models. Nonzero `CounterMask` becomes `cmask=...`; masks and sampling periods become perf config terms. Runtime perf users select aliases from the generated PMU table to diagnose frontend bottlenecks.

## State And Persistence Behavior

The JSON persists frontend event metadata. Hardware frontend state, stalls, and instruction-cache behavior are counted only during perf sessions. Sampling periods persist into generated aliases as defaults.

## Dependencies And Integration Points

The file integrates with the Bonnell x86 mapfile row, generated PMU event tables, perf list/stat display, and frontend bottleneck analysis. It also relies on `jevents.py` correctly translating `CounterMask` and event masks.

## Risks And Edge Cases

Decode stall categories can overlap or be workload-sensitive. `CounterMask` changes event interpretation from raw occurrence to qualified cycles. Instruction-cache hit/miss/access events must remain mask-consistent to avoid impossible ratios. The micro-sequencer event includes assists and inserted flows, so it should not be described as normal decode throughput.

## Test Signals

Validate JSON syntax and generated aliases. Use instruction-cache stress, branch-heavy code, and decode-pressure microbenchmarks to check counter direction. Generated event strings should preserve `cmask` where present.
