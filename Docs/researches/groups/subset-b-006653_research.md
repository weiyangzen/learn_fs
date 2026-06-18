# subset-b-006653 Research

Grouped research for `subset-b-006653`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/cache.json

## Purpose
Describes Elkhart Lake core PMU cache-related events for perf's `jevents.py` generator. The file contains 120 JSON event entries grouped around L2/LLC requests, load/store retired cache outcomes, memory-bound stall attribution, and a large set of offcore-response (`OCR.*`) encodings.

## Important APIs, Types, And Functions
This is data consumed by `tools/perf/pmu-events/jevents.py`, not executable code. Important schema fields are `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, `Data_LA`, `MSRIndex`, `MSRValue`, and `Deprecated`. `EventCode` and `UMask` become perf event selectors; `MSRIndex`/`MSRValue` refine offcore-response filters; `PEBS` and `Data_LA` tell perf that precise sampling and data linear-address capture are available for selected events.

## Control Flow
During the perf build, `jevents.py` discovers this `.json` under the `elkhartlake` directory referenced by `arch/x86/mapfile.csv` for `GenuineIntel-6-9[6C]`. It parses each object into generated C PMU table entries. At runtime perf matches the CPU family/model, loads the Elkhart Lake table, and exposes names such as `L2_REQUEST.MISS`, `LONGEST_LAT_CACHE.MISS`, `MEM_LOAD_UOPS_RETIRED.L3_MISS`, and `OCR.*` aliases to `perf stat` and `perf record`.

## State And Persistence
The JSON itself is static repository data. Persistent generated state is the compiled `pmu-events.c` table embedded in perf. Runtime state is limited to programmed PMU counters, offcore MSR filter values, and sampled PEBS records.

## Dependencies And Integration Points
Depends on the x86 PMU JSON schema, `jevents.py` field conversion, perf metric parsing, and the `mapfile.csv` Elkhart Lake mapping. Metrics in `ehl-metrics.json` depend on `LONGEST_LAT_CACHE.MISS`, and many `OCR.*` entries depend on Intel offcore-response MSR support being modeled correctly by `MSRIndex` and `MSRValue`.

## Risks And Edge Cases
There are 87 `OCR.*` entries with MSR filters, so copy/paste or hex-value mistakes can silently point an alias at the wrong offcore response. Eight entries are deprecated and must remain discoverable without encouraging new use. Fourteen entries carry `PEBS`; fourteen carry `Data_LA`, so precise-event metadata must stay aligned with hardware support. Blank `UMask` fields for some aggregate events rely on `jevents.py` defaulting behavior.

## Test Signals
Run `jq empty` on the file, build perf with jevents enabled, and run `perf list` on an Elkhart Lake model or generated table test to confirm cache aliases appear. Exercise `perf stat -e L2_REQUEST.MISS,LONGEST_LAT_CACHE.MISS` and an `OCR.*` alias where hardware is available. Metric smoke tests should verify `L3_Cache_Fill_BW` can resolve `LONGEST_LAT_CACHE.MISS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/counter.json

## Purpose
Declares the Elkhart Lake PMU counter inventory for perf's event table metadata. It contains one `core` unit entry with three fixed counters and four generic programmable counters.

## Important APIs, Types, And Functions
The schema fields are `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. `Unit: core` ties the counts to the CPU core PMU, while the counter counts inform perf and generated PMU metadata about scheduling capacity for simultaneous events.

## Control Flow
`jevents.py` processes this JSON alongside the other Elkhart Lake PMU files when generating architecture event tables. The table is selected through `arch/x86/mapfile.csv` for the Elkhart Lake CPUID pattern. Runtime perf uses the resulting metadata when presenting PMU capabilities and when planning event groups against available counters.

## State And Persistence
No mutable state is stored here. The values persist in the generated perf PMU table and describe hardware resources that remain fixed for the model.

## Dependencies And Integration Points
Integrates with the x86 PMU event generator and perf's event scheduling model. It must match the actual Elkhart Lake core PMU layout and stay consistent with event files that specify `Counter` constraints such as `0,1,2,3`.

## Risks And Edge Cases
Incorrect generic or fixed counter counts can cause perf to accept impossible event groups or reject valid ones. Because this file has only one object, JSON validity and exact field spelling are the main ingestion risks.

## Test Signals
Validate with `jq empty`, build the generated pmu-events table, and compare `perf list`/PMU capability output on Elkhart Lake hardware. Event group tests with more than four generic core events should reveal whether scheduling constraints are represented correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/ehl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/ehl-metrics.json

## Purpose
Defines eleven Elkhart Lake derived perf metrics. They turn raw events and built-in counters into user-facing formulas for IPC, CPI, clocks, branch density, branch misprediction cost, instruction count, L3 fill bandwidth, CPU utilization, average frequency, turbo utilization, and kernel utilization.

## Important APIs, Types, And Functions
Each object uses `MetricName`, `MetricExpr`, and `BriefDescription`. Expressions reference aliases from other PMU JSON files and perf built-ins: `INST_RETIRED.ANY`, `cycles`, `BR_MISP_RETIRED.ALL_BRANCHES`, `BR_INST_RETIRED.ALL_BRANCHES`, `LONGEST_LAT_CACHE.MISS`, `CPU_CLK_UNHALTED.REF_TSC`, `msr@tsc@`, and the kernel-filtered `cycles:k`.

## Control Flow
During build, `jevents.py` detects `MetricExpr`, parses it through `metric.ParsePerfJson(...).Simplify()`, and emits metric table entries separate from raw event entries. At runtime, perf resolves metric dependencies into the needed event list, programs those events, and evaluates formulas such as `INST_RETIRED.ANY / cycles` for `IPC` and `(cycles / CPU_CLK_UNHALTED.REF_TSC) * msr@tsc@ / 1000000000` for `Average_Frequency`.

## State And Persistence
The file is static; generated metric expressions persist in the compiled perf binary. Runtime state consists of the raw counter readings used to evaluate the formulas.

## Dependencies And Integration Points
Depends on event names from Elkhart Lake `pipeline.json` and `cache.json`, plus perf's synthetic `cycles`, `cycles:k`, and `msr@tsc@` support. The `L3_Cache_Fill_BW` metric specifically depends on `LONGEST_LAT_CACHE.MISS`; branch metrics depend on retired branch and mispredict events.

## Risks And Edge Cases
Formula names must exactly match generated event aliases. Ratios can divide by zero for very short runs or workloads with no branches/mispredicts. `CPU_Utilization`, `Average_Frequency`, and `Turbo_Utilization` depend on reference TSC semantics and may be misleading under virtualization, CPU hotplug, or constrained counter access.

## Test Signals
Run `tools/perf/pmu-events/metric_test.py` or the perf metric parse tests after generation. On hardware, `perf stat -M IPC,CPI,Average_Frequency,Kernel_Utilization` should resolve all dependencies and produce finite values for a non-trivial workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/ehl-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/floating-point.json

## Purpose
Provides three Elkhart Lake floating-point PMU aliases: divider busy cycles, floating-point microcode assists, and retired floating-point divide uops.

## Important APIs, Types, And Functions
The entries use the standard raw-event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. `MACHINE_CLEARS.FP_ASSIST` also carries `PEBS: 1`, marking it as a precise-capable event in generated perf descriptions.

## Control Flow
The build-time generator reads this file from the Elkhart Lake directory, lowercases names for generated aliases, and emits event strings such as `event=0xcd,umask=0x2`. Runtime perf users can request `CYCLES_DIV_BUSY.FPDIV`, `MACHINE_CLEARS.FP_ASSIST`, or `UOPS_RETIRED.FPDIV`; perf then programs the core PMU counter with the encoded event selector.

## State And Persistence
There is no source-level mutable state. The generated aliases persist in perf's PMU table; runtime state is the programmed counter and optional PEBS sampling stream for the assist event.

## Dependencies And Integration Points
Depends on perf's generic PMU JSON parser and the Elkhart Lake `core` PMU mapping. It complements broader pipeline events because FP assists can manifest as machine clears and divide busy cycles can explain backend stalls.

## Risks And Edge Cases
The file is small, so each encoding has high impact. Mislabeling `PEBS` for `MACHINE_CLEARS.FP_ASSIST` would affect precise sampling guidance. Workloads without x87/SSE divide or FP assists naturally report zero, which is not a collection failure.

## Test Signals
Validate JSON syntax and generated aliases. Hardware smoke tests can run divide-heavy floating-point loops with `perf stat -e CYCLES_DIV_BUSY.FPDIV,UOPS_RETIRED.FPDIV`; precise-sampling tests should confirm perf accepts the FP assist event when requested with precise modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/frontend.json

## Purpose
Defines nine Elkhart Lake frontend PMU events covering branch-address clears, decode restriction from wrong predecode length prediction, and instruction-cache access/hit/miss behavior.

## Important APIs, Types, And Functions
The file uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. The `BACLEARS.*` group shares event code `0xe6` with different masks for all, conditional, indirect, return, and unconditional branch clears. `ICACHE.*` entries share event code `0x80` for access, hit, and miss outcomes.

## Control Flow
`jevents.py` converts these objects into generated aliases selected by the Elkhart Lake mapfile row. At runtime perf exposes names such as `BACLEARS.ANY`, `DECODE_RESTRICTION.PREDECODE_WRONG`, and `ICACHE.MISS`; collecting them programs the core PMU with the corresponding event and umask.

## State And Persistence
The data is static and persists in generated perf tables. Runtime state is limited to counter values gathered during a perf session.

## Dependencies And Integration Points
Integrates with perf's frontend/topdown reporting. The branch-clear aliases can be correlated with branch retired and branch mispredict events in `pipeline.json`; instruction-cache aliases can be correlated with cache and virtual-memory miss events when diagnosing fetch-side stalls.

## Risks And Edge Cases
All entries are core generic-counter events with no PEBS metadata. Event names must remain stable because scripts and topdown workflows may refer to them directly. The related `BACLEARS.*` masks are easy to transpose, and aggregate `BACLEARS.ANY` must not be confused with the sum of mutually overlapping subevents without checking hardware semantics.

## Test Signals
Run JSON validation and perf build generation. On hardware, `perf stat -e BACLEARS.ANY,ICACHE.ACCESSES,ICACHE.MISS` over branch-heavy and instruction-cache-sensitive workloads should show aliases are available and count plausible non-negative values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/memory.json

## Purpose
Describes 60 Elkhart Lake memory-access PMU aliases. Most entries are offcore-response (`OCR.*`) encodings for code reads, demand data reads, RFOs, hardware prefetches, software prefetches, streaming stores, and writebacks by source or miss class; the remainder cover memory-ordering machine clears and 4K split load/store references.

## Important APIs, Types, And Functions
Important fields are `EventName`, `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, and `Deprecated`. Fifty-seven entries carry offcore MSR filters. `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT` and `MISALIGN_MEM_REF.STORE_PAGE_SPLIT` use event `0x13`; `MACHINE_CLEARS.MEMORY_ORDERING` uses event `0xc3`.

## Control Flow
The file is parsed by `jevents.py` into raw event table entries for the Elkhart Lake core PMU. For `OCR.*` objects, generated event aliases include both the base event selector and the offcore MSR value, so perf programs the PMU event and associated filter register together. Runtime users request aliases such as `OCR.DEMAND_DATA_RD.L3_MISS_LOCAL` or `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT`.

## State And Persistence
The repository data is immutable at runtime. Generated aliases persist in perf; runtime state includes PMU counter programming and offcore-response filter MSR programming during the perf session.

## Dependencies And Integration Points
Depends on x86 offcore-response support in perf's PMU layer and the Elkhart Lake mapfile entry. It integrates with cache research and metrics because memory-source events explain LLC misses, local DRAM hits, and split-page penalties.

## Risks And Edge Cases
The 57 MSR-filtered events are sensitive to `MSRIndex`/`MSRValue` correctness. Four deprecated entries are retained for compatibility and should not be removed casually. Two entries have PEBS metadata. Offcore filters may have constraints on simultaneous use; grouping multiple `OCR.*` events can fail or multiplex depending on hardware resources.

## Test Signals
Validate syntax, build the generated perf tables, and check `perf list` includes representative `OCR.*`, `MISALIGN_MEM_REF.*`, and `MACHINE_CLEARS.MEMORY_ORDERING` aliases. Hardware tests should include an offcore event group and a split-page microbenchmark if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/other.json

## Purpose
Collects 22 Elkhart Lake PMU events that do not fit the main cache, memory, frontend, pipeline, floating-point, or virtual-memory topic files. The file covers bus-lock behavior, deprecated C0 memory stall aliases, hardware interrupts, and additional offcore-response categories.

## Important APIs, Types, And Functions
Uses standard event fields plus `Deprecated`, `EdgeDetect`, `MSRIndex`, and `MSRValue`. `BUS_LOCK.*` entries share event `0x63`; `HW_INTERRUPTS.*` entries use event `0xcb`; `OCR.*` entries use offcore-response MSR filters. Two hardware interrupt entries use edge detection.

## Control Flow
At build time, `jevents.py` emits these objects into the Elkhart Lake generated event table. Runtime perf exposes compatibility aliases such as deprecated `BUS_LOCK.CYCLES_OTHER_BLOCK` and preferred aliases such as `BUS_LOCK.BLOCK_CYCLES`, `BUS_LOCK.LOCK_CYCLES`, `BUS_LOCK.SELF_LOCKS`, and `HW_INTERRUPTS.RECEIVED`.

## State And Persistence
No source-level mutable state. Generated aliases persist in perf's compiled tables. Runtime state includes PMU counters and, for `OCR.*`, offcore filter MSR values.

## Dependencies And Integration Points
Integrates with lock-contention analysis, interrupt-rate analysis, and memory-bound stall diagnosis. The deprecated `C0_STALLS.*` aliases point users toward `MEM_BOUND_STALLS.*` events in `cache.json`, so cross-file naming consistency matters.

## Risks And Edge Cases
Six entries are deprecated, so tooling should preserve them for compatibility while descriptions guide users to replacements. `BUS_LOCK.ALL` and `BUS_LOCK.SELF_LOCKS` have blank `UMask` fields; parser defaults must encode them correctly. Edge-detected interrupt counts can differ from level/cycle-style events and should not be mixed without understanding semantics.

## Test Signals
Validate JSON and generated output. Run `perf list BUS_LOCK` and `perf list HW_INTERRUPTS` on a matching table. Lock-heavy and interrupt-heavy workloads should produce plausible counts; deprecated aliases should still resolve without breaking scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/pipeline.json

## Purpose
Defines 60 Elkhart Lake core pipeline events for retired branches, branch mispredicts, clock/reference cycles, topdown slots, machine clears, uop retirement/issue behavior, load blocks, and divide busy cycles.

## Important APIs, Types, And Functions
The file uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, and `Deprecated`. Major groups include `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `TOPDOWN_*`, `MACHINE_CLEARS.*`, `UOPS_RETIRED.*`, `UOPS_ISSUED.*`, `LD_BLOCKS.*`, `CYCLES_DIV_BUSY.*`, and `BTCLEAR.*`.

## Control Flow
`jevents.py` parses the entries and emits raw-event aliases selected for `GenuineIntel-6-9[6C]` systems. The metrics file depends on this table for `INST_RETIRED.ANY`, `BR_INST_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.REF_TSC`, and `cycles`-adjacent clock analysis. Runtime perf programs the named events directly or as dependencies of metrics.

## State And Persistence
The file is static repository data; generated aliases persist in perf. Runtime state is PMU counter values and, for precise-capable entries, PEBS sample records.

## Dependencies And Integration Points
Integrates with perf topdown analysis and Elkhart Lake metrics. Twenty-six entries carry `PEBS`, so precise sampling workflows depend on these annotations. Branch aliases integrate with frontend `BACLEARS.*`; machine-clear aliases integrate with memory ordering and FP assist events.

## Risks And Edge Cases
Topdown events use slot accounting and can be misinterpreted if treated as normal retired-event counts. Three entries are deprecated. PEBS flags must match hardware or perf may advertise unsupported precise sampling. Metric formulas will fail if foundational aliases such as `INST_RETIRED.ANY` or `BR_MISP_RETIRED.ALL_BRANCHES` are renamed.

## Test Signals
Run JSON validation and perf pmu-events generation. Metric tests for `IPC`, `CPI`, `IpBranch`, and `IpMispredict` cover key dependency names. On hardware, `perf stat -e INST_RETIRED.ANY,CPU_CLK_UNHALTED.REF_TSC,BR_MISP_RETIRED.ALL_BRANCHES` and a topdown event group should resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/virtual-memory.json

## Purpose
Provides 31 Elkhart Lake virtual-memory and TLB PMU aliases. It covers DTLB load/store misses, ITLB misses, page-walk completion by page size, STLB hits, PDE-cache misses, EPT walks/violations, and TLB-related retired memory uops.

## Important APIs, Types, And Functions
Uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, and `Data_LA`. Groups include `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `EPT.*`, `MEM_UOPS_RETIRED.STLB_MISS_*`, `ITLB.ITLB_FLUSH`, and `LD_BLOCKS.STORE_FORWARD`.

## Control Flow
The Elkhart Lake mapfile row causes `jevents.py` to include this file in the generated core PMU event table. Runtime perf users can select aliases for page-walk and TLB behavior. For entries marked `PEBS` and `Data_LA`, perf descriptions advertise precise sampling and address availability where supported.

## State And Persistence
No mutable source state exists. Generated aliases persist in perf; runtime state is counter programming and possible PEBS records with data linear addresses for selected load/store TLB miss events.

## Dependencies And Integration Points
Integrates with memory and cache analysis: TLB misses can explain apparent backend stalls or memory latency. EPT entries are relevant for virtualization workloads. The parser's `Data_LA` handling appends address-support text to generated descriptions.

## Risks And Edge Cases
Four entries carry `PEBS`, and three carry `Data_LA`; incorrect precision metadata affects sampling guidance. Page-size-specific umasks can be easily confused. Virtualization and kernel settings may restrict EPT visibility or counter availability.

## Test Signals
Validate JSON, build generated tables, and check `perf list DTLB_LOAD_MISSES` plus `perf list ITLB_MISSES`. Hardware tests should include a TLB-stressing workload, and precise sampling smoke tests should verify address-bearing events are accepted with appropriate modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/cache.json

## Purpose
Defines 125 Emerald Rapids core cache PMU aliases. Coverage includes core snoop responses, L1D pending and hardware-prefetch misses, L2 request/line/transaction behavior, LLC and L3 hit/miss retired-load classifications, memory instruction retirement, offcore requests and outstanding cycles, software prefetches, store queue behavior, and offcore-response filters.

## Important APIs, Types, And Functions
The schema uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, `Data_LA`, and `Deprecated`. Thirty-eight entries are `OCR.*` offcore-response aliases with MSR filters. Twenty-four entries carry `Data_LA`. Six entries use `CounterMask`, and one uses edge detection.

## Control Flow
`jevents.py` reads the file when generating x86 PMU tables, and `arch/x86/mapfile.csv` selects the `emeraldrapids` directory for `GenuineIntel-6-CF`. At runtime perf exposes names such as `CORE_SNOOP_RESPONSE.*`, `L2_RQSTS.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, `OFFCORE_REQUESTS.*`, and `OCR.*`; perf programs event selectors and, for OCR aliases, the required offcore MSR filters.

## State And Persistence
The JSON is static repository data. Generated perf tables persist in the binary. Runtime state is PMU counter configuration, offcore MSR filter state, and optional sampled address records for events whose generated descriptions indicate data-address support.

## Dependencies And Integration Points
Depends on the Emerald Rapids mapfile entry, the x86 PMU JSON parser, and perf support for offcore response filters. It complements Emerald Rapids uncore files in the same directory, while this file itself describes only core PMU cache aliases. `counter.json` advertises the core PMU has eight generic counters, which affects feasible grouping of these events.

## Risks And Edge Cases
Emerald Rapids has broader PMU capacity and server uncore context, so confusing core events with uncore events can lead to wrong PMU selection. OCR MSR values are high-risk data because a bad bitmask silently changes the measured memory source. Two entries are deprecated. Counter masks and edge detection change counting semantics and require accurate conversion by `jevents.py`.

## Test Signals
Validate with `jq empty`, build perf with jevents, and inspect `perf list` for representative `L2_RQSTS`, `MEM_LOAD_RETIRED`, `OFFCORE_REQUESTS`, and `OCR` aliases. On Emerald Rapids hardware, run event groups that combine cache aliases with offcore aliases and confirm perf either schedules them or reports clear constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/counter.json

## Purpose
Declares PMU counter inventory for Emerald Rapids core and uncore units. It contains 16 unit entries, including the core PMU and server uncore blocks such as PCU, IRP, M2PCIe, IIO, iMC, M2M, M3UPI, UPI, CHA, CXL, HBM, UBOX, and MDF-related units.

## Important APIs, Types, And Functions
Each object uses `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit declares four fixed counters and eight generic counters. Most uncore units declare zero fixed counters and four generic counters; `IRP` and `UBOX` declare two generic counters; `CXLCM` declares eight.

## Control Flow
`jevents.py` ingests this file with the rest of the Emerald Rapids directory. Generated metadata is selected by the `GenuineIntel-6-CF` mapfile row. Runtime perf uses unit-specific counter counts when exposing PMU capabilities and constraining event groups across core and uncore PMUs.

## State And Persistence
The file contains static hardware metadata. The generated perf table persists after build; runtime state is limited to perf's scheduling decisions and active PMU counter allocations.

## Dependencies And Integration Points
Integrates with both core files such as `cache.json` and Emerald Rapids uncore event files in the same directory. Unit names must match the `Unit` fields used by uncore JSON event descriptions and perf's PMU name mapping.

## Risks And Edge Cases
Wrong counts can make perf overcommit or underuse PMU counters. Unit-name drift is especially risky for uncore blocks because the file spans many PMU instances. Server platforms may expose only a subset depending on SKU, BIOS settings, or kernel PMU support, so metadata must describe architectural capacity without assuming every runtime PMU is present.

## Test Signals
Validate syntax and generated tables. On Emerald Rapids hardware, compare `perf list` uncore PMUs and event scheduling against the declared counts. Group tests should cover the eight-counter core PMU, two-counter `IRP`/`UBOX`, and four-counter memory/interconnect units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/counter.json -->
