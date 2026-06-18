<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/frontend.json

## Purpose
Granite Rapids x86 perf PMU event table for front-end pipeline observation. The file is data, not executable code: perf's PMU event tooling parses the 46 JSON objects to expose named hardware events such as branch resteers, decode stalls, DSB/MITE/MS delivery, instruction-cache stalls, and precise front-end retirement latency events.

## APIs, Types, and Functions
The effective API is the perf `pmu-events` JSON schema. Each object maps an `EventName` to encodings and metadata consumed by the perf event alias generator: `EventCode`, `UMask`, optional `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and for some precise retired events `RetirementLatencyMin/Mean/Max`. There are no C functions or local types in the file, but downstream generated C tables treat these fields as declarative event descriptors.

The event families are:
- `BACLEARS.ANY`, `DECODE.LCP`, `DECODE.MS_BUSY`, and `DSB2MITE_SWITCHES.PENALTY_CYCLES` for branch-discovery, length-changing-prefix, microcode, and DSB-to-MITE penalties.
- `FRONTEND_RETIRED.*` precise-distribution events for DSB miss, iTLB/STLB/L1I/L2 misses, unknown branches, MS flows, software prefetch lateness, ANT and mispredicted ANT branches, and latency thresholds from 1 to 512 cycles. These use `EventCode` `0xc6`, `UMask` `0x3`, and PEBS/PDist-related MSR programming through `MSRIndex` `0x3F7`.
- `ICACHE_DATA.*` and `ICACHE_TAG.*` stalls for fetch misses and instruction TLB/tag-side stalls.
- `IDQ.*`, `IDQ_BUBBLES.*`, and `IDQ_UOPS_NOT_DELIVERED.*` events for DSB, MITE, microcode sequencer uop delivery, front-end bubbles, and no-uop-delivery cycles.

## Control Flow, State, and Persistence
At build or runtime table-generation time, perf reads this JSON array, validates field names, and folds each entry into architecture-specific PMU alias tables for `arch/x86/graniterapids`. At perf execution time, a user-facing event alias such as `frontend_retired.l1i_miss` resolves to the encoded event select, umask, counter constraints, and optional MSR filter values from the entry. The file itself keeps no mutable state; persistence is the version-controlled JSON plus generated perf tables when the kernel/perf source is built.

The control relationship is mostly dependency-oriented: metrics in `gnr-metrics.json` refer directly to many names in this file, including `FRONTEND_RETIRED.L1I_MISS`, `FRONTEND_RETIRED.L2_MISS`, `FRONTEND_RETIRED.ITLB_MISS`, `FRONTEND_RETIRED.STLB_MISS`, `FRONTEND_RETIRED.ANY_DSB_MISS`, `FRONTEND_RETIRED.MS_FLOWS`, `FRONTEND_RETIRED.UNKNOWN_BRANCH`, `ICACHE_DATA.STALLS`, `ICACHE_DATA.STALL_PERIODS`, `ICACHE_TAG.STALLS`, `DECODE.LCP`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, and `IDQ.MS_UOPS`.

## Dependencies and Integration
This table integrates with perf's PMU event parser, generated event alias tables, `perf list`, `perf stat`, `perf record`, and the Granite Rapids metric formulas. It depends on the kernel perf PMU JSON schema and on Intel Granite Rapids architectural event definitions. It is paired with sibling event files for branch, cache, floating point, memory, uncore, and topdown sources, because metrics in `gnr-metrics.json` combine this front-end data with core, offcore, branch, and uncore events.

Counter constraints are part of the integration contract. General events often allow counters `0,1,2,3`; several `FRONTEND_RETIRED.*` aliases allow `0..7` but declare PDist counter availability in descriptions. MSR-backed selectors require perf to program `MSRIndex`/`MSRValue` consistently, and ratio formulas that use the `:R` retirement-latency companion depend on the event being recognized as a retired latency-capable source.

## Risks
Risks are primarily data-contract risks. A wrong `EventCode`, `UMask`, `MSRValue`, or counter mask silently produces misleading measurements. Precise events using `MSRIndex` `0x3F7` are especially sensitive because multiple aliases share the same architectural event but differ by MSR selector. Several metrics divide by these events or multiply by `:R`, so missing PEBS/retirement-latency support can break top-down formulas or produce zeros. The file also contains human-facing descriptions; typo-level issues are less operationally severe but can confuse `perf list` output.

## Test Signals
Useful validation signals are `jq` parse success, perf PMU event-table generation without schema warnings, `perf list` showing the expected Granite Rapids front-end aliases, and `perf stat -e` acceptance for representative aliases from each family. Metric-level signals include successful evaluation of `tma_icache_misses`, `tma_itlb_misses`, `tma_dsb_switches`, `tma_lcp`, DSB/MITE/MS delivery percentages, and front-end information metrics such as DSB miss, unknown branch, and icache miss latency ratios. Hardware validation should include workloads with known instruction-cache pressure, branch misprediction/resteer behavior, microcode-heavy instructions, and DSB-vs-MITE shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/frontend.json -->
