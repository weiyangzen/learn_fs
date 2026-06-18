# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/frontend.json

## Purpose
Broadwell-DE frontend event catalog. The 28 events describe branch address clears, decoded-stream-buffer to MITE switches, instruction cache hits/misses/stalls, instruction delivery queue activity, microcode sequencer delivery, and frontend under-delivery cycles.

## Important APIs, Types, and Functions
Each event uses the perf PMU event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields include `CounterMask` on 15 entries, `EdgeDetect` on 2, `Invert` on 1, and `PublicDescription` on 23. Event families are `BACLEARS`, `DSB2MITE_SWITCHES`, `ICACHE`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`.

## Control Flow
Perf uses these aliases directly for event counting and indirectly for top-down frontend metrics. The metrics file combines IDQ, DSB, MITE, ICACHE, BACLEARS, and DSB-to-MITE switch events into `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_icache_misses`, `tma_lcp`, `tma_dsb_switches`, `tma_ms_switches`, and instruction fetch coverage metrics.

## State and Persistence
The file itself is static. Runtime state is counter-programming state, including edge detection, inversion, and counter masks for cycle-qualified aliases. Persistent meaning depends on the Broadwell-DE frontend pipeline model: DSB, MITE, IDQ, and microcode sequencer names are used as stable integration points by metric formulas.

## Dependencies and Integration
The catalog integrates with pipeline branch and machine-clear events to explain frontend latency after resteers. It also integrates with `metricgroups.json` groups such as `Frontend`, `FetchBW`, `FetchLat`, `DSB`, `DSBmiss`, `IcMiss`, and top-down frontend groups.

## Risks
Risks include misinterpreting cycles-with-condition events as event counts, grouping too many frontend aliases with limited counters, and under-delivery metrics being affected by SMT and backend backpressure. DSB and MITE attribution is model-specific and should not be generalized to other x86 generations.

## Test Signals
Run JSON validation, confirm aliases appear in `perf list`, and test with workloads that stress I-cache misses, large instruction footprints, branch resteers, and microcode-heavy instructions. Derived metrics should be checked through `perf stat -M Frontend,FetchBW,FetchLat`.
