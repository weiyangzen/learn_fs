# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/frontend.json

## Purpose

`frontend.json` is Rocket Lake's perf catalog for instruction-fetch, decode, uop-cache, MITE, microcode sequencer, and frontend starvation analysis. It contains 39 event rows spanning branch resteers, length-changing-prefix decode stalls, DSB-to-MITE transitions, frontend-retired latency sampling, instruction-cache stalls, IDQ source cycles/uops, and not-delivered uop cycles.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. Families are `BACLEARS`, `DECODE`, `DSB2MITE_SWITCHES`, `FRONTEND_RETIRED`, `ICACHE_16B`, `ICACHE_64B`, `ICACHE_DATA`, `ICACHE_TAG`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`.

Seventeen `FRONTEND_RETIRED.*` rows use MSR `0x3F7` with different `MSRValue` selectors for DSB misses, ITLB misses, L1I/L2/STLB misses, and latency thresholds from 1 through 512 cycles. `DSB2MITE_SWITCHES.COUNT` uses both `CounterMask: 1` and `EdgeDetect: 1`, while not-delivered rows use counter masks and inverted logic to distinguish no-uop and frontend-ok cycles.

## Control Flow and Data Flow

At build time, `jevents.py` serializes these rows into generated Rocket Lake PMU tables, preserving MSR selectors and edge/counter-mask qualifiers. At runtime, perf programs core counters and, for `FRONTEND_RETIRED.*`, configures the frontend-retired selector MSR. Data flows from branch prediction and fetch/decode structures into counters: branch resteers, DSB/MITE transitions, instruction-cache tag/data stalls, IDQ delivery by source, and retired instructions that experienced frontend latency.

The diagnostic flow separates fetch latency from fetch bandwidth. ICACHE and ITLB-related rows identify supply misses. DSB/MITE and IDQ rows identify where uops were delivered from. `IDQ_UOPS_NOT_DELIVERED` rows quantify delivery shortfall to the backend. `FRONTEND_RETIRED.LATENCY_GE_*` rows attribute retired instructions to frontend starvation intervals.

## State and Persistence Behavior

Static metadata is persisted in the JSON. Runtime frontend queues, uop-cache state, branch-predictor state, and sampled latency intervals are external. MSR selectors are persistent semantics for the generated alias and must be preserved. Edge-detected count rows and cycle rows represent different state transitions; treating them as the same unit would corrupt analysis.

## Dependencies and Integration Points

This file depends on Rocket Lake frontend PMU encodings, perf's generator, and kernel support for frontend-retired MSR programming. It integrates with `perf stat`, `perf record`, top-down frontend-bound metrics, compiler/code-layout analysis, branch tuning, instruction-cache footprint studies, and `builtin-list.c` display of event descriptions. It complements `pipeline.json`-style topdown catalogs and `virtual-memory` ITLB rows on other models.

## Risks and Edge Cases

MSR-qualified `FRONTEND_RETIRED.*` rows are selector-sensitive; dropping `MSRValue` makes many aliases indistinguishable. Latency threshold rows overlap conceptually, so counts at higher thresholds are not independent categories unless the metric formula treats them correctly. `DSB2MITE_SWITCHES.COUNT` counts transition events while `.PENALTY_CYCLES` counts cycles. LCP decode stalls depend on instruction encoding and may be rare in modern compiler output. Frontend starvation can be hidden by backend stalls, as descriptions note for some latency rows.

## Test Signals

Validation should parse the JSON, build the generated tables, and expose all frontend aliases through `perf list`. Large code-footprint workloads should raise I-cache and ITLB-related rows. Code shaped to miss the uop cache should change DSB/MITE source ratios. Synthetic LCP-heavy instruction streams can validate `DECODE.LCP`. Branchy code should move `BACLEARS.ANY`. Frontend-starved workloads should increase `IDQ_UOPS_NOT_DELIVERED` and selected `FRONTEND_RETIRED.LATENCY_GE_*` rows.
