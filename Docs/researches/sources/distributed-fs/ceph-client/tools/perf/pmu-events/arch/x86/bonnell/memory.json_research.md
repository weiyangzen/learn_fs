# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/memory.json

## Purpose

This file defines 19 Bonnell memory-access events. It focuses on misaligned memory references, split loads/stores/read-modify-write operations, nonzero segment-base bubbles, and hardware/software prefetch request types.

## Important APIs, Types, And Data

The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Event families are `MISALIGN_MEM_REF` and `PREFETCH`. Several misalignment events have `.AR` at-retirement variants, while prefetch entries distinguish hardware, software, L1, L2, NTA, and load-prefetch forms.

## Control Flow

The build path converts the JSON into generated Bonnell perf aliases. Event code `0x5` with different masks represents the misalignment family, while event code `0x7` masks represent prefetch categories. Runtime perf programs the selected alias on Bonnell PMUs.

## State And Persistence Behavior

The JSON persists event definitions. Runtime memory alignment behavior and prefetch activity are counted by hardware. `.AR` variants persist as separate aliases to distinguish retirement-qualified observations from earlier pipeline observations.

## Dependencies And Integration Points

Dependencies include `jevents.py`, Bonnell model selection, generated event tables, perf alias matching, and user workflows that diagnose split accesses, segment-base overhead, and prefetch behavior.

## Risks And Edge Cases

Misalignment events distinguish splits from bubbles and load/store/RMW forms; mask mistakes can make optimization conclusions wrong. The description typo on one store split entry should not affect generation but may be visible in `perf list`. Prefetch events can be speculative and may not correlate directly with useful demand-load behavior.

## Test Signals

Validate JSON and generated event strings. Microbenchmarks with aligned versus intentionally split accesses should change `MISALIGN_MEM_REF` aliases. Prefetch-heavy loops and software prefetch instructions should exercise `PREFETCH` aliases.
