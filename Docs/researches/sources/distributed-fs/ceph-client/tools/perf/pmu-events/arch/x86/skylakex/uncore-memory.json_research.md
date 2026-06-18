# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-memory.json

## Purpose

`uncore-memory.json` is the Skylake-X uncore memory PMU catalog used by Linux perf's PMU event generator. It contains 411 package-scoped `iMC` events for integrated memory-controller behavior: DRAM CAS read/write traffic, activate and precharge behavior, read/write pending queue pressure, major-mode transitions, bypass commands, refresh, ECC, rank/bank-level CAS activity, and memory-side power/throttle states. The file is static metadata, not executable code, but it defines the event aliases that users see through `perf list` and program through `perf stat` or related perf flows on Skylake-X systems.

## Important APIs, Types, and Data Fields

The file is a JSON array of event records following the perf PMU event schema. Common fields are `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `Unit`, `PerPkg`, and optional `Experimental`, `MetricName`, `MetricExpr`, and `ScaleUnit`. Every record uses `Unit: "iMC"`, `PerPkg: "1"`, and programmable counters `0,1,2,3`, so the aliases target integrated memory-controller PMU instances at package scope.

Important event families include `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE` derived from memory-controller CAS counts; `UNC_M_CAS_COUNT.*` for all, read, write, regular, underfill, WMM/RMM, and isochronous CAS traffic; `UNC_M_ACT_COUNT.*` and `UNC_M_PRE_COUNT.*` for row activation and precharge causes; `UNC_M_RPQ_*` and `UNC_M_WPQ_*` for read/write pending queue inserts, occupancy, non-empty cycles, full cycles, and CAM hits; `UNC_M_RD_CAS_RANK{0..7}.*` and `UNC_M_WR_CAS_RANK{0..7}.*` for per-rank bank and bank-group traffic; and `UNC_M_POWER_*` for CKE, throttle, self-refresh, channel power-down, DLLOFF, PCU throttling, and critical throttle cycles. Two rows define derived perf metrics: `power_channel_ppd = (UNC_M_POWER_CHANNEL_PPD / UNC_M_CLOCKTICKS) * 100` and `power_self_refresh = (UNC_M_POWER_SELF_REFRESH / UNC_M_CLOCKTICKS) * 100`.

## Control Flow and Data Flow

There is no local control flow in the JSON itself. The control flow is external: perf's pmu-events tooling parses the array, validates known schema keys, builds generated event tables, and later maps user-selected aliases to `EventCode`/`UMask` encodings for the appropriate uncore PMU. At runtime, perf opens the matching iMC PMU instances, programs one of counters `0,1,2,3`, and aggregates package-level counts according to the selected event and topology.

The event data supports several analysis flows. CAS and `LLC_MISSES.MEM_*` rows feed memory bandwidth calculations, usually with the `64Bytes` scale on the derived LLC miss read/write aliases. Activate, precharge, rank, bank, and bank-group rows describe DRAM row-buffer and address-distribution behavior. Queue occupancy and full-cycle rows expose memory-controller backpressure. Power rows use `UNC_M_CLOCKTICKS` as a denominator for residency-like metrics and should be interpreted as cycles or percentages rather than transactions.

## State and Persistence Behavior

The persistent state is the checked-in event catalog. Runtime counter values, perf session output, and aggregation state are not stored here. `PerPkg` is an important semantic marker because these events observe all traffic reaching a package's memory controllers, not a single process or thread. `Experimental: "1"` appears heavily, especially on rank/bank, refresh, precharge, and power-management rows; those aliases persist in the catalog but carry a weaker stability signal than baseline CAS, queue insert, and clocktick rows.

Occupancy and cycle events represent time-integrated hardware state, while CAS, activate, precharge, insert, and ECC rows represent counted transactions or incidents. The two metric rows persist formulas that depend on `UNC_M_CLOCKTICKS`; if event names change, the formulas must be updated in lockstep.

## Dependencies and Integration Points

This file depends on the perf pmu-events parser, Skylake-X uncore PMU support in perf and the kernel, and platform firmware exposing the expected iMC PMU topology. It integrates with neighboring Skylake-X files such as `uncore-power.json` for package power-controller state and `virtual-memory.json` for core-side TLB behavior. Higher-level users include `perf list`, `perf stat`, memory bandwidth diagnostics, NUMA and memory placement investigations, memory-controller queue pressure studies, and power/thermal analyses that need to connect memory traffic to throttling or low-power residency.

## Risks and Edge Cases

The primary risk is scope confusion: iMC uncore events are package-level and include traffic from all cores and agents on the package, so they cannot be attributed to one task without isolation. The file mixes raw events, derived aliases, cycle counts, occupancy counts, and percentage metrics; downstream reporting must not sum unlike units. Many rows are experimental, and rank/bank encodings may be unavailable or topology-dependent on some systems. The rank families are large and repetitive, making copy/paste mistakes in `EventCode`, `UMask`, or descriptions difficult to spot manually. Formula rows depend on `UNC_M_CLOCKTICKS`; missing clocktick support breaks the derived percentages. `ScaleUnit: "64Bytes"` on the LLC miss aliases is a conversion hint, not proof that every memory-controller row has the same unit.

## Test Signals

Static validation should parse the JSON, verify the event count and required keys, and run the perf pmu-events generation step. On Skylake-X hardware, `perf list` should expose the iMC aliases, especially `UNC_M_CAS_COUNT.RD`, `UNC_M_CAS_COUNT.WR`, `UNC_M_CLOCKTICKS`, and the two `LLC_MISSES.MEM_*` aliases. Streaming read and write workloads should move CAS read/write and LLC miss memory events; random access should affect activation, precharge, and queue-pressure rows; idle or low-power scenarios should move clockticks and memory power residency while leaving transaction counts low. Metric smoke tests should confirm `power_channel_ppd` and `power_self_refresh` resolve their denominator event.
