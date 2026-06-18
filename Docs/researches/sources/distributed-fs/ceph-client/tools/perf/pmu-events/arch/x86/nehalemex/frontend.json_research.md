# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/frontend.json

## Purpose
This small file defines three Nehalem EX frontend/decode aliases: `MACRO_INSTS.DECODED`, `MACRO_INSTS.FUSIONS_DECODED`, and `TWO_UOP_INSTS_DECODED`. They expose decoded instruction volume, macro-fusion activity, and two-uop decoded instruction counts.

## Important APIs, Types, And Fields
Each object uses the standard event fields `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`. All three aliases are usable on counters `0,1,2,3` and use the default sample value `2000000`. No `PEBS`, `MSRIndex`, edge, invert, or counter-mask fields are present.

## Control Flow
There is no executable control flow. `jevents.py` converts the three declarative aliases into generated C entries. At runtime, perf resolves the names and programs the PMU event selector, while the processor counts decode/frontend activity.

## State And Persistence
The file stores static alias metadata only. It does not persist workload state. Because the table is small and simple, the main persisted behavior is alias naming and event encoding.

## Dependencies And Integration Points
The file depends on Nehalem EX frontend PMU event encodings. It integrates with the x86 model event table, `perf list`, and `perf stat`/`perf record` alias parsing. These counters complement broader pipeline events in `pipeline.json`, especially decode and uop-delivery diagnostics.

## Risks
The risk profile is mostly schema and encoding correctness. With only three aliases, any wrong event code or mask has visible user impact. Because no special fields are present, parser regressions are unlikely to be isolated here; this file is better as a simple baseline event-table fixture.

## Test Signals
Run JSON validation and generated table tests. Use `perf list` or generated output inspection to confirm all three aliases are emitted with counters `0,1,2,3`. These entries are useful as plain-event smoke tests because they avoid PEBS and MSR side paths.
