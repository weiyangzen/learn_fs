# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/floating-point.json

## Purpose
This file defines 28 Nehalem EX floating-point, MMX, SSE, and SIMD integer PMU aliases. It covers x87 floating-point assists, computational FP operations, FP/MMX transitions, 128-bit SIMD integer operation classes, and 64-bit SIMD integer operation classes.

## Important APIs, Types, And Fields
The schema is an event-object array with `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PEBS`. Families include `FP_ASSIST`, `FP_COMP_OPS_EXE`, `FP_MMX_TRANS`, `SIMD_INT_128`, and `SIMD_INT_64`. `FP_ASSIST.ALL`, `.INPUT`, and `.OUTPUT` are precise events with `PEBS: 1`; the rest are generic execution counters available on counters `0,1,2,3`.

## Control Flow
The file has no functions. Perf's build process reads the JSON, generates C event tables, and runtime perf alias lookup maps user names to event selectors. The CPU hardware performs the actual counting of FP and SIMD activity.

## State And Persistence
The file persists static event metadata and default sample periods. It does not maintain runtime state. Precise assist events are important because they can be used to sample problematic x87 operations more accurately than broad execution counters.

## Dependencies And Integration Points
It depends on Nehalem EX PMU encodings for FP/SIMD execution and on perf's PEBS handling for assist events. It integrates with the generated x86 event table, `perf list`, and command lines such as `perf stat -e FP_COMP_OPS_EXE.SSE_FP_PACKED`. The event families complement pipeline retired SSE-uop aliases, but this file focuses on execution and assist categories.

## Risks
The table mixes x87, MMX, SSE floating-point, and SIMD integer terminology; mislabeling an event can send users to the wrong optimization target. `FP_COMP_OPS_EXE` masks are easy to confuse because several aliases share the same event code with different unit masks. PEBS support on assist events must be preserved if the event is used for precise sampling.

## Test Signals
Validate JSON and generated `pmu-events.c`. Check that all five families appear in `perf list`. Generation tests should include at least one PEBS `FP_ASSIST` alias and one SIMD integer alias to cover both precise and generic forms.
