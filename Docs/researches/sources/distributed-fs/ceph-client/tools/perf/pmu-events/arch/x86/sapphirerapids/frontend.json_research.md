# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/frontend.json

## Purpose
`frontend.json` defines 43 Sapphire Rapids core PMU events for instruction fetch/decode behavior: branch clears, length-changing prefix stalls, microcode sequencer busy time, DSB-to-MITE switches, frontend-retired latency and miss classification, instruction-cache stalls, IDQ delivery, and frontend bubble aliases.

## Important APIs, types, and schema fields
The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`, plus modifier fields `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. `FRONTEND_RETIRED.*` events use event `0xc6`, umask `0x1`, counters `0-7`, and MSR `0x3F7` with different values to select DSB misses, ITLB/L1I/L2/STLB misses, unknown branches, microcode-sequencer flows, and latency thresholds.

## Control flow and integration
During perf build, these entries become generated event tables. At runtime they feed `perf list`, event parsing, and top-down frontend analysis. Some families are direct counters (`IDQ.*`, `ICACHE_*`, `DECODE.*`), while `FRONTEND_RETIRED.*` relies on extra MSR programming to select a frontend retirement classification. Alias families `IDQ_BUBBLES.*` and `IDQ_UOPS_NOT_DELIVERED.*` map to the same encodings and must remain aligned.

## State and persistence behavior
The JSON persists stable event names, encodings, and threshold definitions. Runtime state is in PMU counters and frontend classification MSRs. Latency threshold events encode policy in `MSRValue`, for example `LATENCY_GE_1` through `LATENCY_GE_512`; edits change how users classify fetch starvation length.

## Dependencies
Dependencies include Sapphire Rapids frontend PMU facilities, perf's MSR-extra event support, and metric expressions/groups that consume frontend events. Integration points include `builtin-list.c` for listing, metric parsing tests, top-down frontend-bound metrics, and sibling pipeline events such as branch mispredicts, machine clears, and topdown slots.

## Risks and edge cases
MSR-coded frontend events are easy to break by changing only the name or description while leaving an inconsistent `MSRValue`. `CounterMask`, `Invert`, and `EdgeDetect` change cycle versus period/count semantics for events such as `ICACHE_DATA.STALL_PERIODS`, `IDQ.MS_SWITCHES`, and frontend bubble cycle variants. Alias drift between `IDQ_BUBBLES` and `IDQ_UOPS_NOT_DELIVERED` would confuse existing scripts. Descriptions distinguish frontend starvation not interrupted by backend stalls, so wording matters for top-down interpretation.

## Test signals
Run JSON validation and the perf PMU event generator. `perf list frontend` should expose all families, including aliases. On hardware, instruction-cache miss loops, branch-heavy code, large-code-footprint workloads, and microcode-heavy instruction streams can validate event directionality. Unit-level tests should assert `FRONTEND_RETIRED.*` rows keep `MSRIndex` `0x3F7` and expected threshold `MSRValue` patterns.
