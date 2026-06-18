# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/floating-point.json

## Purpose

This file defines 32 Bonnell floating-point, x87, SIMD, and assist events. It covers floating-point assists, SIMD assists, retired SIMD instructions by scalar/vector form, saturated arithmetic, SIMD uop execution and type breakdowns, and x87 computational operations.

## Important APIs, Types, And Data

The schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `PEBS`, and `BriefDescription`. Event families include `FP_ASSIST`, `SIMD_ASSIST`, `SIMD_COMP_INST_RETIRED`, `SIMD_INSTR_RETIRED`, `SIMD_INST_RETIRED`, `SIMD_SAT_INSTR_RETIRED`, `SIMD_SAT_UOP_EXEC`, `SIMD_UOPS_EXEC`, `SIMD_UOP_TYPE_EXEC`, and `X87_COMP_OPS_EXE`. `PEBS` marks precise-capable retired or at-retirement events such as `SIMD_UOPS_EXEC.AR` and selected x87 events.

## Control Flow

Build-time conversion lowercases names and emits event strings from the event code and umask. When `PEBS` is present, `jevents.py` augments descriptions with precise-event text unless already present. Runtime perf uses the generated aliases to program Bonnell core counters and can request precise sampling when the hardware and event support it.

## State And Persistence Behavior

The file stores static metadata. Floating-point assist and SIMD execution counts are runtime hardware state. `PEBS` is persistent metadata used by tools and users to distinguish precise sampling candidates, but actual precise-buffer state is controlled by perf and the kernel.

## Dependencies And Integration Points

Integration points include Bonnell model mapping, `jevents.py` PEBS handling, generated event tables, perf event parsing, and test fixtures that compare event strings and descriptions. These events support analysis of FP exception assists, SIMD mix, saturation, and x87 usage.

## Risks And Edge Cases

Precise-event metadata must be correct; marking a non-precise event as PEBS can produce failed or misleading sampling, while omitting PEBS hides useful attribution. SIMD type masks are dense and easy to swap. Some events count instructions while others count uops or assists, so descriptions need to remain explicit.

## Test Signals

Run JSON validation and PMU event generation. Generated descriptions for PEBS entries should include precise-event wording. Workload tests can use scalar FP, packed SIMD, saturated arithmetic, and x87-heavy loops to validate directionality of aliases.
