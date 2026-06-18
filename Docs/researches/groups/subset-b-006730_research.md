# subset-b-006730 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-memory.json -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-power.json

## Purpose

`uncore-power.json` is the Skylake-X package power-control-unit PMU catalog for perf. It contains 25 package-scoped `PCU` events that expose package clock ticks, frequency transition cycles, thermal and power limit cycles, prochot and VR-hot conditions, FIVR phase shedding, memory phase shedding, package C-state residency, core C-state occupancy, and core transition/demotion activity. The file gives perf static aliases for power and residency signals outside the core PMUs.

## Important APIs, Types, and Data Fields

The JSON array uses perf event object fields including `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `Unit`, `PerPkg`, and optional `Experimental`. All rows target `Unit: "PCU"`, are package scoped with `PerPkg: "1"`, and use counters `0,1,2,3`. `UNC_P_CLOCKTICKS` is the baseline PCU clock-cycle event. `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6` share `EventCode: "0x80"` with different `UMask` values to classify core C-state occupancy. Other named rows cover frequency maximum/minimum limit cycles, package C0/C2E/C3/C6 residency, prochot, VR hot, phase shedding, and transition cycles.

## Control Flow and Data Flow

The file has no executable control flow. Perf's event-table generation reads these records, associates the `PCU` unit with the platform uncore PMU, and exposes aliases for runtime selection. During profiling, perf programs PCU counters and returns package-level cycle or occupancy counts. Analysis generally compares limit, transition, residency, and hot-condition cycles to `UNC_P_CLOCKTICKS` or to workload phases to understand power-management behavior.

## State and Persistence Behavior

The only persistent state is the static alias metadata. Runtime package power state, C-state occupancy, thermal limits, and transition counts are hardware state sampled by perf and are not persisted in this JSON. `PerPkg` means values describe the whole package. Counter records are mostly raw count/cycle definitions and do not define `MetricExpr` formulas in this file, so any percentage conversion is left to users or higher-level tooling.

## Dependencies and Integration Points

This file depends on Skylake-X PCU uncore PMU support in the Linux kernel and perf's pmu-events generator. It integrates with `uncore-memory.json` when memory traffic and memory phase shedding or throttling need to be correlated, and with core event files when CPU stalls must be connected to package-level power limits. It is consumed by `perf list`, `perf stat`, power/thermal diagnostics, frequency transition analysis, and package C-state residency studies.

## Risks and Edge Cases

The data is package-scoped, so results include all package activity and can be misleading on shared systems. Many events are cycle-like residency or limit signals rather than event occurrences; consumers need a denominator such as `UNC_P_CLOCKTICKS` for ratios. Some event descriptions are terse and repeat the event name, so external Intel PMU documentation may be needed for exact semantics. The `UNC_P_CLOCKTICKS` row has no explicit `EventCode`/`UMask` fields in the JSON, which is intentional for this catalog but can expose assumptions in parsers that require those fields for every event.

## Test Signals

Static tests should verify JSON parsing and generated perf tables, including acceptance of `UNC_P_CLOCKTICKS` without an explicit event code. Runtime smoke tests on Skylake-X should check that `perf list` exposes `UNC_P_*` PCU aliases and that `UNC_P_CLOCKTICKS` advances. Idle and sleep-friendly workloads should affect package C-state residency; CPU load should increase C0 occupancy; frequency scaling, thermal stress, or power-limit scenarios should move frequency-limit, prochot, VR-hot, and transition-cycle rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/virtual-memory.json

## Purpose

`virtual-memory.json` is the Skylake-X core PMU catalog for TLB, page-walk, EPT-walk, and TLB flush events in perf. It contains 28 events covering data-load DTLB misses, store DTLB misses, instruction TLB misses, second-level TLB hits, page-walk completion by page size, page-walk active and pending cycles, EPT walk pending cycles, ITLB flushes, and DTLB/STLB flush attempts.

## Important APIs, Types, and Data Fields

The file is a JSON array using the core event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, and optional `Counter`, `CounterMask`, and `SampleAfterValue`. Unlike uncore files, these records do not set a `Unit`; they are core PMU events. Major families are `DTLB_LOAD_MISSES.*` with `EventCode: "0x08"`, `DTLB_STORE_MISSES.*` with `EventCode: "0x49"`, `ITLB_MISSES.*` with `EventCode: "0x85"`, `EPT.WALK_PENDING` with `EventCode: "0x4f"`, `ITLB.ITLB_FLUSH` with `EventCode: "0xAE"`, and `TLB_FLUSH.*` with `EventCode: "0xBD"`.

The page-walk completion masks distinguish all page sizes from 4K, 2M/4M, and 1G completions. `STLB_HIT` rows count L1 TLB misses that were satisfied by the second-level TLB. `WALK_ACTIVE` and `WALK_PENDING` rows use the same event and mask within each family but describe related cycle/accounting views of page miss handler activity.

## Control Flow and Data Flow

There is no code-level control flow. Perf parses the records into generated event tables, exposes aliases, and programs core PMU counters when users request them. Data flow starts at per-core hardware counters, then perf aggregates per CPU, per thread, or system-wide according to the chosen command. The events form a diagnostic pipeline: first identify DTLB/ITLB miss-caused page walks, then separate STLB hits from full walks, then split completed walks by page size, and finally correlate active/pending cycles with workload stalls.

## State and Persistence Behavior

Persistent state is limited to the static event metadata. Runtime page-table behavior, TLB contents, EPT walk state, and flush activity live in hardware and kernel execution, not in this file. Counts are core-scoped and depend on perf's sampling or counting mode. The descriptions explicitly note that EPT page-walk duration is excluded from the Skylake `WALK_ACTIVE`/`WALK_PENDING` DTLB and ITLB rows, while `EPT.WALK_PENDING` covers EPT walks separately.

## Dependencies and Integration Points

This file depends on Skylake-X core PMU support and perf's pmu-events schema. It integrates with cache, frontend, backend, and uncore memory files by explaining whether observed stalls or memory traffic are related to address translation. It is relevant to huge-page tuning, virtualization overhead analysis, page-table locality studies, TLB shootdown diagnostics, and instruction-fetch bottleneck analysis.

## Risks and Edge Cases

Rows with the same event code and mask but different names can be misinterpreted if tooling treats aliases as independent signals rather than alternate semantic views. Page-walk completion counts by page size require workloads that actually use those page sizes; otherwise the counters may stay at zero. EPT walk accounting is separated from ordinary page-walk duration on Skylake-X, so virtualization analysis must include `EPT.WALK_PENDING`. TLB flush events count attempts or flushes, not necessarily resulting misses. Core aggregation can hide per-core skew in NUMA, virtualization, or mixed workload cases.

## Test Signals

Static validation should parse the JSON and generate perf event tables. Runtime tests should confirm `perf list` exposes `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_PENDING`, and `TLB_FLUSH.*` aliases on Skylake-X. Pointer-chasing or large working-set tests should increase DTLB walk events; code-footprint stress should affect ITLB rows; huge-page workloads should move 2M/4M or 1G completion rows; virtualized workloads should exercise EPT walk pending; TLB shootdown or mapping churn tests should affect flush rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/cache.json

## Purpose

`cache.json` is the Snow Ridge X core cache and memory-access PMU catalog for perf. It contains 120 events covering L1/L2/LLC access behavior, memory-bound stalls, retired load uops by hit level, retired memory uops, and a large set of offcore response (`OCR.*`) aliases for data, code, RFO, prefetch, streaming store, and writeback request classes. It lets perf users diagnose cache hierarchy behavior and offcore response sources on Snow Ridge X systems.

## Important APIs, Types, and Data Fields

The file uses perf core event fields including `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `SampleAfterValue`, optional `PEBS`, optional `Data_LA`, optional `Deprecated`, and offcore-specific `MSRIndex` and `MSRValue`. Non-OCR cache rows include `CORE_REJECT_L2Q.ANY`, `DL1.DIRTY_EVICTION`, `L2_REJECT_XQ.ANY`, `L2_REQUEST.ALL/HIT/MISS/REJECTS`, `LONGEST_LAT_CACHE.REFERENCE/MISS`, `MEM_BOUND_STALLS.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_UOPS_RETIRED.*`, and `TOPDOWN_FE_BOUND.ALL`.

The dominant family is `OCR.*`: 87 records use `EventCode: "0XB7"` and `UMask: "0x1"` with `MSRIndex` values such as `0x1a6` and `0x1a7` plus long `MSRValue` filters. These describe offcore responses for demand data reads, demand code reads, RFOs, L2 hardware prefetches, all code reads, reads-to-core, L1/L2/core writebacks, streaming writes, and snoop outcomes such as `SNOOP_HITM`, `SNOOP_MISS`, and `SNOOP_NOT_NEEDED`. Fourteen rows carry PEBS support, and eight deprecated `OCR.DEMAND_DATA_RD.*` aliases point users to `OCR.DEMAND_DATA_AND_L1PF_RD.*`.

## Control Flow and Data Flow

The JSON has no internal control flow. Perf's generator converts these records into event aliases. At runtime, simple cache rows program core PMU event select and umask fields, while OCR rows additionally program offcore response filter MSRs from `MSRIndex` and `MSRValue`. Counts flow from per-core PMU counters into perf output. The expected diagnostic flow is to use broad L2/LLC/load-retirement events to identify cache pressure, then use `MEM_BOUND_STALLS.*` and OCR response filters to separate L2, L3, DRAM/MMIO, snoop, prefetch, RFO, and writeback behavior.

## State and Persistence Behavior

The persistent state is the static event and filter metadata. Runtime offcore filter programming, PEBS records, and counts are session state owned by perf and the kernel. `Deprecated` rows are still present as aliases but should be treated as compatibility shims. `PEBS` and `Data_LA` mark events that can participate in precise sampling or data-linear-address capture when the hardware and perf mode support it; they do not store sampled data in the JSON.

## Dependencies and Integration Points

This file depends on Snow Ridge X core PMU support, offcore response MSR programming support, and perf's pmu-events parser preserving `MSRIndex`, `MSRValue`, `PEBS`, `Data_LA`, and `Deprecated` fields. It integrates with `snowridgex/counter.json` for available generic/fixed core counters, `frontend.json` for instruction-fetch and branch-clear causes, `floating-point.json` for FP divider/assist pressure, and uncore memory files when core cache misses need to be correlated with memory-controller traffic.

## Risks and Edge Cases

OCR aliases are filter-heavy and easy to break if `MSRValue` is truncated, normalized incorrectly, or paired with the wrong `MSRIndex`. Some OCR rows use two MSRs while outstanding-latency rows use one, so parsers must preserve comma-separated fields. Deprecated demand-data aliases can double-count conceptually with their replacement names if users select both. PEBS availability is model- and mode-dependent. The file mixes access counts, stall cycles, uop retirement counts, topdown slots, and offcore response counts; downstream metrics need explicit unit handling. Shared-core or system-wide aggregation can obscure which workload generated offcore responses.

## Test Signals

Static tests should parse the JSON, preserve OCR MSR fields, and generate perf tables without dropping deprecated or PEBS metadata. Runtime smoke tests should verify `perf list` exposes `L2_REQUEST.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, and representative `OCR.*` aliases. Cache-resident workloads should increase L2 hit and load-hit rows; large streaming reads should move LLC miss and OCR DRAM-like response filters; prefetch-heavy workloads should affect hardware prefetch OCR families; cache-line sharing tests should move snoop outcome filters; selecting deprecated aliases should either work or produce the expected perf deprecation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/counter.json

## Purpose

`counter.json` is the Snow Ridge X PMU counter-capacity catalog for perf. Unlike event files, it does not define programmable events. It defines how many fixed and generic counters are available for each PMU unit: `core`, `CHA`, `IIO`, `IRP`, `iMC`, `M2M`, `M2PCIe`, `PCU`, and `UBOX`. This metadata helps perf understand platform counter resources when scheduling events across core and uncore units.

## Important APIs, Types, and Data Fields

The file is a JSON array of unit-capacity objects with three fields: `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit declares 3 fixed and 4 generic counters. Uncore units are mostly generic-only: `CHA`, `IIO`, `M2M`, `M2PCIe`, and `PCU` each declare 4 generic counters; `IRP` and `UBOX` declare 2 generic counters; `iMC` declares 1 fixed and 4 generic counters. `UBOX` uses a numeric `CountersNumFixed` value of `1` while most other counts are strings, so consumers must tolerate both JSON number and string forms.

## Control Flow and Data Flow

There is no executable control flow. Perf's pmu-events tooling reads these capacity records alongside event catalogs and uses them as static constraints for the Snow Ridge X platform. The data flow is from checked-in JSON to generated tables, then into perf event scheduling decisions and user-facing metadata about PMU units. Event files reference the same unit names, and this file supplies the resource context for those units.

## State and Persistence Behavior

The persistent state is the static list of PMU units and counter counts. Runtime counter allocation, multiplexing, and enabled/running time accounting happen in perf and the kernel; none of that state is persisted here. The file describes hardware capacity, not current availability, so actual sessions can still be constrained by privilege, kernel support, occupied counters, or event incompatibilities.

## Dependencies and Integration Points

This file depends on perf support for counter metadata records in the pmu-events tree. It integrates with Snow Ridge X event files that use `core`, `CHA`, `IIO`, `IRP`, `iMC`, `M2M`, `M2PCIe`, `PCU`, or `UBOX` units. It is especially relevant to grouped perf stat runs, uncore monitoring, and scheduling multiple events where the number of generic counters determines whether multiplexing is needed.

## Risks and Edge Cases

The mixed numeric/string representation of counter counts can reveal fragile parsers. Counter counts are unit-level capacities, not guarantees that every event can run on every counter. If unit names drift from event files, perf may fail to associate events with capacity metadata. The file has no `EventName` rows, so tools that blindly expect event schemas for every JSON file in the directory can mis-handle it.

## Test Signals

Static validation should parse the file and confirm all nine expected units are present with non-negative fixed and generic counts. Generation tests should verify the file is accepted even without `EventName` or `EventCode`. Runtime or integration tests should schedule more events than available generic counters on a Snow Ridge X unit and confirm perf either schedules, multiplexes, or reports constraints consistently with these capacities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/floating-point.json

## Purpose

`floating-point.json` is the Snow Ridge X core PMU catalog for a small set of floating-point execution and assist events. It contains three events: FP divider busy cycles, floating-point operations retired with microcode assists, and retired floating-point divide uops. These aliases help perf users identify workloads limited by FP division throughput or by expensive FP assists.

## Important APIs, Types, and Data Fields

The file is a JSON array of core event records with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. All three rows use counters `0,1,2,3`. `CYCLES_DIV_BUSY.FPDIV` uses `EventCode: "0xcd"` and `UMask: "0x2"` to count cycles when the floating-point divider is busy. `MACHINE_CLEARS.FP_ASSIST` uses `EventCode: "0xc3"` and `UMask: "0x4"` to count retired FP operations requiring microcode assist. `UOPS_RETIRED.FPDIV` uses `EventCode: "0xc2"` and `UMask: "0x8"` to count retired FP divide uops, including x87 and SSE and x87 sqrt.

## Control Flow and Data Flow

The file has no internal control flow. Perf parses the records into event aliases and programs core PMU counters when users select them. Data flows from core hardware counters into perf counts or samples. The analysis flow is to compare divider busy cycles with retired FP divide uops to infer divider pressure or latency, and to track FP assist events when unusual inputs, denormals, exceptions, or instruction forms cause microcode intervention.

## State and Persistence Behavior

Only the static metadata is persisted. Runtime divider occupancy, retired uops, and machine clear or assist behavior are hardware execution state. Counts are per core or per task depending on perf mode and aggregation. No metric expressions are defined, so higher-level ratios such as busy cycles per divide uop must be computed externally.

## Dependencies and Integration Points

This file depends on Snow Ridge X core PMU support and perf's generated event tables. It integrates with `counter.json` for core counter availability, cache/backend events when FP workloads are also memory-bound, and frontend events when assists or clears interact with pipeline refetch/redecode behavior. It is useful for math kernels, vectorized code, numerical libraries, and workloads sensitive to denormal or exceptional FP behavior.

## Risks and Edge Cases

These events do not cover all FP operations; they focus on division, square root through the divide-uop row, and assists. A workload can be FP-heavy without moving these counters if it mainly uses adds, multiplies, or vector fused operations. Assist counts can be rare and input-sensitive, so tests need inputs that trigger the hardware condition. Aggregating across cores can hide a single hot thread's divider pressure. Counter pressure can cause multiplexing if these events are combined with many other core events.

## Test Signals

Static tests should parse the JSON and generate aliases for all three event names. Runtime smoke tests should run a tight floating-point divide or sqrt workload and observe `CYCLES_DIV_BUSY.FPDIV` and `UOPS_RETIRED.FPDIV` increase. Inputs known to trigger FP assists should move `MACHINE_CLEARS.FP_ASSIST`; ordinary multiply/add loops should provide a low baseline for these specific counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/frontend.json

## Purpose

`frontend.json` is the Snow Ridge X core PMU catalog for frontend instruction-fetch and branch-address-clear behavior. It contains nine events for branch address clears (`BACLEARS.*`), instruction cache accesses/hits/misses, and decode restrictions from wrong predecode length prediction. These aliases help perf users diagnose frontend bubbles caused by branch target correction, instruction cache misses, and decode throughput restrictions.

## Important APIs, Types, and Data Fields

The JSON array uses core event fields `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. The `BACLEARS` family uses `EventCode: "0xe6"` with masks for all, conditional, indirect, return, and unconditional branch clears. `ICACHE.ACCESSES`, `.HIT`, and `.MISSES` use `EventCode: "0x80"` with masks `0x3`, `0x1`, and `0x2`. `DECODE_RESTRICTION.PREDECODE_WRONG` uses `EventCode: "0xe9"` and `UMask: "0x1"` for decode throughput reductions due to wrong instruction length prediction.

## Control Flow and Data Flow

There is no executable control flow. Perf turns the JSON records into aliases, then programs core PMU counters when selected. Counts flow from core frontend hardware to perf output. A typical diagnostic flow starts with `ICACHE.ACCESSES/HIT/MISSES` to understand instruction-cache locality, then checks `BACLEARS.*` to separate branch-redirection cleanup by branch type, and uses `DECODE_RESTRICTION.PREDECODE_WRONG` when frontend throughput is limited by instruction-length prediction rather than cache misses.

## State and Persistence Behavior

The only persisted state is the static event metadata. Runtime branch prediction, instruction cache contents, and decode restriction state are not stored here. Counts are core-scoped and reflect the workload and aggregation mode chosen by perf. No derived metrics are defined, so hit rates or clear rates are computed by downstream tooling from raw counts.

## Dependencies and Integration Points

This file depends on Snow Ridge X core PMU support and perf's pmu-events generator. It integrates with cache events, particularly instruction-cache and memory-bound instruction fetch signals, and with topdown analysis where frontend-bound slots need a concrete cause. It also complements branch prediction and pipeline-clear events in other perf categories.

## Risks and Edge Cases

`ICACHE.ACCESSES` uses a combined mask rather than a separately measured sum, so consumers should not assume accesses always equal hits plus misses under all counting conditions. Branch address clears are not the same as all branch mispredictions; they represent specific frontend correction behavior. Decode restriction events may be very workload-specific and can be hard to trigger in simple smoke tests. Aggregated counts can hide per-core instruction-cache or branch behavior in mixed workloads.

## Test Signals

Static tests should parse the JSON and expose all nine aliases in generated perf tables. Runtime smoke tests should show `ICACHE.ACCESSES` increasing during instruction execution, with larger code-footprint workloads increasing `ICACHE.MISSES`. Branch-heavy tests with indirect, return, conditional, and unconditional branches should move the relevant `BACLEARS.*` rows when the hardware triggers clears. Crafted instruction streams or binaries with difficult length prediction are the best signal for `DECODE_RESTRICTION.PREDECODE_WRONG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/frontend.json -->
