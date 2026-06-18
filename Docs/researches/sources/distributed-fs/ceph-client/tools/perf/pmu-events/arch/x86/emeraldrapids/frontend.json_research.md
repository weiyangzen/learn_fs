<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/frontend.json

## Purpose
Defines Emerald Rapids raw PMU events for instruction fetch, decode, frontend delivery, decoded-stream-buffer behavior, microcode-sequencer delivery, unknown branches, instruction cache/tag stalls, and frontend-retired latency attribution. These events support perf users and topdown metrics that diagnose frontend bandwidth and latency bottlenecks.

## Important APIs, Types, And Functions
- Top-level type: JSON array of 43 event records.
- Common fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`.
- Optional event programming fields: `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`.
- Major event families:
  - `BACLEARS.ANY`, `DECODE.LCP`, and `DECODE.MS_BUSY` for branch resteers and decode penalties.
  - `DSB2MITE_SWITCHES.PENALTY_CYCLES` for decoded-stream-buffer to legacy decode transitions.
  - `FRONTEND_RETIRED.*` PEBS/PDIST-style events using `EventCode` `0xc6`, `MSRIndex` `0x3F7`, and specific `MSRValue` filters for DSB, ITLB, L1I, L2, STLB, latency thresholds, microcode flows, and unknown branches.
  - `ICACHE_DATA.*` and `ICACHE_TAG.*` for instruction-cache data/tag stalls.
  - `IDQ.*`, `IDQ_BUBBLES.*`, and `IDQ_UOPS_NOT_DELIVERED.*` for uop delivery source and frontend underdelivery cycles.

## Control Flow
Perf ingests the records as event definitions for the Emerald Rapids model. Simple events program an event select and umask into a general-purpose counter. Filtered retired frontend events additionally program the listed MSR index/value pair to select the precise distribution condition. For IDQ and bubble events, optional `CounterMask`, `Invert`, and `EdgeDetect` fields change the hardware condition from raw occurrences to cycles, optimal-delivery cycles, or transition counts. Derived TMA metrics then combine these counts to apportion frontend-bound slots into latency, bandwidth, DSB, MITE, ITLB, icache, branch-resteer, and microcode causes.

## State And Persistence
The file is static PMU metadata. Runtime state includes the selected frontend events, optional MSR filters programmed by perf, and counter values captured during a measurement. There is no persistence beyond source control and generated perf tables. Some events are precise distribution events and rely on hardware filtering state, so measurements can be affected by PEBS/PDIST availability and counter placement.

## Dependencies And Integration Points
- Consumed by the perf pmu-events generation path for x86 Emerald Rapids.
- Feeds metrics in `emr-metrics.json` such as `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_icache_misses`, `tma_itlb_misses`, `tma_branch_resteers`, `tma_unknown_branches`, `percent_uops_delivered_from_decoded_icache`, and `percent_uops_delivered_from_legacy_decode_pipeline`.
- Depends on Intel frontend PMU semantics, decoded stream buffer, MITE legacy decode path, IDQ delivery accounting, PEBS/PDIST retired instruction attribution, and MSR filter `0x3F7`.
- Integrates with `perf stat`, `perf record`, `perf list`, and topdown analysis workflows for code layout, branch prediction, instruction-cache locality, and decode bottlenecks.

## Risks And Edge Cases
- `FRONTEND_RETIRED.*` records share the same event select and umask but differ by `MSRValue`; losing the MSR fields would silently collapse distinct events into the same measurement.
- Alias pairs exist between `IDQ_BUBBLES.*` and `IDQ_UOPS_NOT_DELIVERED.*`; duplicate encodings are intentional compatibility surface.
- Counter masks and invert flags are semantically important. Dropping `CounterMask` on `IDQ_BUBBLES.CYCLES_FE_WAS_OK` or latency-threshold events changes a cycle condition into a raw-event condition.
- Some frontend events are limited to counters `0,1,2,3`, while retired attribution events allow a broader counter set. Metric groups can fail to schedule if this is ignored.
- Descriptions for latency thresholds encode assumptions such as "not interrupted by a back-end stall"; users should avoid interpreting them as total wall-clock frontend stall cycles.

## Test Signals
- JSON syntax validation should pass and optional MSR/filter fields should be preserved by pmu-events generation.
- `perf list` should show frontend event names with public descriptions for DSB, MITE, IDQ, icache, and frontend-retired families.
- `perf stat -e IDQ_UOPS_NOT_DELIVERED.CORE,IDQ.DSB_UOPS,IDQ.MITE_UOPS,ICACHE_DATA.STALLS` should parse on supported hardware.
- A code-layout or icache-stress benchmark should increase icache/frontend latency events, while microcoded instruction workloads should move `IDQ.MS_UOPS` or related microcode events.
- Topdown frontend metrics in `emr-metrics.json` should resolve every referenced event after any edit to this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/frontend.json -->
