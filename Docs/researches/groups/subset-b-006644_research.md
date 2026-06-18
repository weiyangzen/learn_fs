# subset-b-006644 Research

Grouped source research for Cascade Lake X perf PMU metric-group metadata and core event tables. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/metricgroups.json

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/metricgroups.json` is the Cascade Lake X metric-group description catalog for Linux perf's generated PMU metadata. It maps metric group names to short user-facing descriptions used by `perf list metricgroups`, metric browsing, and top-down microarchitecture analysis presentation. The source was read as a complete 140-line JSON object with 138 entries.

## Important APIs, Types, and Data Fields

This file is data, not executable code. Its public contract is a JSON object whose keys are metric-group names and whose values are descriptions. Important keys include high-level groups such as `Backend`, `Frontend`, `BadSpec`, `MemoryBound`, `Pipeline`, `Retire`, `Summary`, `Power`, `Snoop`, and `Server`; top-down level names `TopdownL1` through `TopdownL6`; legacy/generated aliases `tma_L1_group` through `tma_L6_group`; category groups such as `tma_backend_bound_group`, `tma_frontend_bound_group`, `tma_memory_bound_group`, `tma_bad_speculation_group`, and `tma_retiring_group`; and issue labels such as `tma_issueTLB`, `tma_issueRFO`, `tma_issueFB`, and `tma_issueSyncxn`.

Most values use the shared description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; the top-down levels and `tma_*_group` keys have more specific generated descriptions. The schema is intentionally minimal: there are no event encodings, no metric formulas, and no membership arrays in this file.

## Control Flow and Data Flow

There is no runtime control flow in the JSON. During the perf build, `tools/perf/pmu-events/jevents.py` recognizes files ending in `metricgroups.json`, loads the object, places group names and descriptions into the generated big string table, and emits a sorted `metricgroups` lookup table plus `describe_metricgroup(const char *group)`. Runtime consumers then call through perf's metric-group code to retrieve the description for a group name referenced by metric metadata.

The data flow is therefore: static JSON object -> `jevents.py` generated `pmu-events.c` string offsets -> `describe_metricgroup()` -> `perf list`/metric display. This file does not decide which events belong to a group; metric JSON or generated Intel metric code references these group names through `MetricGroup`.

## State and Persistence Behavior

The file persists static labels and descriptions only. It owns no runtime counters, sampled values, or metric membership state. Once built, its contents are embedded into perf's generated PMU event library and persist as compiled lookup metadata until perf is rebuilt.

## Dependencies and Integration Points

The main dependency is name consistency with Cascade Lake X metrics, especially `clx-metrics.json` and generated Intel top-down metric definitions. The directory is selected for CPUIDs matching `GenuineIntel-6-55-[56789ABCDEF]` in `tools/perf/pmu-events/arch/x86/mapfile.csv`, while lower 6-55 steppings map to `skylakex`; that selection controls when these group descriptions are paired with Cascade Lake X metric tables.

Integration points include `tools/perf/pmu-events/jevents.py` for build-time conversion, `tools/perf/pmu-events/pmu-events.h` for `describe_metricgroup()`, `tools/perf/util/metricgroup.c` for metric-group lookup and expansion, `tools/perf/builtin-list.c` for listing groups and descriptions, and `tools/perf/tests/shell/stat_all_metricgroups.sh` for exercising all listed groups through `perf stat -M`.

## Risks and Edge Cases

The group names are free-form strings, so typos create orphan descriptions or leave referenced metric groups undescribed. Some conceptual aliases coexist, for example `TopdownL1` and `tma_L1_group`, and removing either form can break scripts or metric definitions that still use the older spelling. Description text is not validated against metric membership, so stale descriptions can survive if metrics move groups. Because this file is architecture/model-specific, accidentally sharing it with the wrong CPUID model can expose Cascade Lake X top-down group names on a CPU whose metric formulas or event support differ.

## Test Signals

Useful checks are `jq type`/object parse success, perf build success with generated `pmu-events.c`, `perf list --raw-dump metricgroups` showing representative entries such as `TopdownL1`, `Pipeline`, and `tma_memory_bound_group`, and `perf list metricgroups` returning descriptions rather than blank entries. Consistency tests should compare metric-group names referenced by Cascade Lake X metrics against keys in this file and flag missing or unused descriptions. The shell test `tools/perf/tests/shell/stat_all_metricgroups.sh` is a runtime signal that listed groups can be expanded by `perf stat -M` on the selected system.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/other.json

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/other.json` defines Cascade Lake X core PMU events that do not fit the cache, frontend, memory, pipeline, virtual-memory, or uncore topic files. The file is dominated by offcore response (`OCR.*`) events for demand reads, prefetch reads, RFOs, PMM local hits, and supplier/snoop response classes, plus a small set of core power-license and hardware-interrupt events. The source was read as a complete 1,257-line JSON array with 126 event objects.

## Important APIs, Types, and Data Fields

This file uses perf's standard PMU event JSON schema. Every event has `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Five non-OCR rows also carry `PublicDescription`. The 121 `OCR.*` rows additionally use `MSRIndex` and `MSRValue`, which cause `jevents.py` to generate offcore-response MSR programming fields for the event alias.

Event families are:

- `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, `CORE_POWER.LVL2_TURBO_LICENSE`, and `CORE_POWER.THROTTLE`, all using event code `0x28` with distinct umasks for AVX/turbo license and throttle-cycle accounting.
- `HW_INTERRUPTS.RECEIVED`, using event code `0xCB` and umask `0x1`.
- `OCR.*`, using event codes `0xB7, 0xBB`, umask `0x1`, counters `0,1,2,3`, MSR indices `0x1a6,0x1a7`, and different `MSRValue` encodings.

The OCR rows cover request classes including `ALL_DATA_RD`, `ALL_PF_DATA_RD`, `ALL_PF_RFO`, `ALL_READS`, `ALL_RFO`, `OTHER`, `PF_L1D_AND_SW`, `PF_L2_DATA_RD`, `PF_L2_RFO`, `PF_L3_DATA_RD`, and `PF_L3_RFO`. For those classes, response filters include `ANY_RESPONSE`, `PMM_HIT_LOCAL_PMM` variants (`ANY_SNOOP`, `SNOOP_NONE`, `SNOOP_NOT_NEEDED`), and `SUPPLIER_NONE` variants (`ANY_SNOOP`, `HITM_OTHER_CORE`, `HIT_OTHER_CORE_FWD`, `HIT_OTHER_CORE_NO_FWD`, `NO_SNOOP_NEEDED`, `SNOOP_MISS`, `SNOOP_NONE`).

## Control Flow and Data Flow

There is no executable control flow in the file. Build-time flow is handled by `tools/perf/pmu-events/jevents.py`: each object is parsed into generated PMU event metadata, `EventCode` contributes the base `event=` selector, `UMask` contributes `umask=`, `SampleAfterValue` contributes the default `period=`, and `MSRIndex`/`MSRValue` are converted into the appropriate offcore-response MSR field. The code path takes the first event code before the comma when building the alias, while the MSR index/value data supplies the extra offcore filter.

At runtime, a user can select symbolic names such as `OCR.ALL_READS.ANY_RESPONSE` or `CORE_POWER.LVL2_TURBO_LICENSE` with `perf stat` or `perf record`. Perf resolves the alias from the generated Cascade Lake X table, asks the kernel x86 PMU driver to program the programmable counter and any required MSR filter, and reports counts or samples. The OCR rows are designed for memory-origin and snoop-response analysis; the power rows expose cycles spent in each turbo license level or throttled while a power-level request is pending.

## State and Persistence Behavior

The JSON is static metadata. It does not store live offcore transactions, interrupt counts, power state, or throttle state. `SampleAfterValue` values persist as default sampling periods in generated metadata, but actual counter values are owned by hardware and perf event file descriptors during a profiling run. Offcore response configuration is transiently programmed into model-specific registers by the kernel for active events and is not persisted by this file.

## Dependencies and Integration Points

The file depends on Cascade Lake X core PMU semantics, including the availability of programmable counters `0,1,2,3`, the `CORE_POWER`, `HW_INTERRUPTS`, and offcore response events, and MSR filter encodings for `0x1a6`/`0x1a7`. It integrates with `jevents.py` for JSON conversion, `pmu-events.h`/generated `pmu-events.c` for event lookup, the x86 mapfile entry `GenuineIntel-6-55-[56789ABCDEF],v1.25,cascadelakex,core`, and perf runtime commands that consume event aliases.

The file also integrates analytically with Cascade Lake X memory and PMM metrics: the `PMM_HIT_LOCAL_PMM` rows distinguish persistent-memory local hits, while `SUPPLIER_NONE` and snoop variants help explain offcore read responses, cache-to-cache transfers, and requests that did not require snooping.

## Risks and Edge Cases

The biggest correctness risk is the pairing of event selector, offcore MSR index, and `MSRValue`. A wrong `MSRValue` can produce a valid event that counts the wrong response class. The comma-separated `EventCode` values are parsed by the generator with the first code as the alias event selector, so any expectation that both selectors are programmed from the string itself must be verified against the x86 PMU driver path. OCR events compete for limited programmable counters and offcore response MSR resources, so some combinations may fail to schedule together.

Several descriptions are mechanically generated and repetitive, sometimes duplicating the event name in prose; this can make documentation less clear without changing encoding. Power-license events count cycles in license categories, not necessarily direct wall-clock residency or frequency, and turbo throttling interpretation depends on package power/thermal policy. Hardware interrupt counts can be affected by interrupt routing, affinity, virtualization, and privilege restrictions.

## Test Signals

Static test signals include JSON parse success, every row having `EventName`/`EventCode`/`UMask`/`Counter`/`SampleAfterValue`, all OCR rows having both `MSRIndex` and `MSRValue`, and generated `pmu-events.c` build success. Runtime smoke tests should verify `perf list` shows representative names from each family and `perf stat -e CORE_POWER.LVL0_TURBO_LICENSE,HW_INTERRUPTS.RECEIVED sleep 0.1` is accepted on matching hardware.

For OCR rows, useful tests are `perf stat` runs for a small subset such as `OCR.ALL_READS.ANY_RESPONSE`, `OCR.ALL_RFO.ANY_RESPONSE`, and one PMM-local row on a Cascade Lake X system. Workload signals should show all-read counters moving under memory-heavy loads, RFO counters moving under write-heavy workloads, and PMM-local counters only becoming meaningful on systems with configured persistent memory. Scheduling tests should intentionally combine multiple OCR events to catch offcore MSR constraint failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/pipeline.json

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/pipeline.json` defines Cascade Lake X core PMU events for execution pipeline analysis. It covers branch instruction retirement and misprediction, core/reference cycle accounting, cycle activity stalls, execution-port utilization, instruction and uop retirement, machine clears, allocation/resource stalls, loop stream detector activity, load blocking, assists, reservation-station emptiness, and divider activity. The source was read as a complete 953-line JSON array with 102 event objects.

## Important APIs, Types, and Data Fields

This file uses perf's standard PMU event object schema. All rows include `EventName`, `Counter`, `SampleAfterValue`, and `BriefDescription`; most rows include `EventCode` and `UMask`; many include `PublicDescription`. Optional fields exercise important perf parser paths: `CounterMask` appears on threshold/cycle-counting events, `Invert` appears on "no uops" or "less than threshold" forms, `EdgeDetect` appears on transition/end events, `AnyThread` appears on core-wide logical-thread variants, `PEBS` marks precise retired branch events, and `Errata` marks branch-retired rows affected by `SKL091`.

Major event families include `ARITH`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_THREAD_UNHALTED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `ILD_STALL`, `INST_DECODED`, `INST_RETIRED`, `INT_MISC`, `LD_BLOCKS`, `LD_BLOCKS_PARTIAL`, `LOAD_HIT_PRE`, `LSD`, `MACHINE_CLEARS`, `OTHER_ASSISTS`, `PARTIAL_RAT_STALLS`, `RESOURCE_STALLS`, `ROB_MISC_EVENTS`, `RS_EVENTS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Fixed-counter rows include `CPU_CLK_UNHALTED.REF_TSC` on fixed counter 2 and `CPU_CLK_UNHALTED.THREAD`/`THREAD_ANY` on fixed counter 1. Programmable rows generally use counters `0,1,2,3`. Port rows `UOPS_DISPATCHED_PORT.PORT_0` through `PORT_7` use event code `0xA1` with one umask per execution port. Threshold rows such as `UOPS_EXECUTED.CORE_CYCLES_GE_1` through `GE_4`, per-thread `CYCLES_GE_*`, `STALL_CYCLES`, and `UOPS_RETIRED.TOTAL_CYCLES` rely on `CounterMask` and sometimes `Invert` to change the hardware condition being counted.

## Control Flow and Data Flow

There is no executable control flow in the JSON itself. Build-time flow runs through `jevents.py`, which lowers each object into a generated event string such as `event=...,umask=...,period=...` plus optional `cmask=`, `inv=`, `edge=`, and `any=` fields. PEBS settings become precision metadata in descriptions and runtime event capability. Errata strings are appended to generated descriptions as specification-update notes.

At runtime, users select these names through `perf stat`, `perf record`, metric formulas, or top-down analysis. Perf resolves the symbolic event name in the Cascade Lake X table, configures the kernel PMU event with the encoded selector and modifiers, and uses the counts to diagnose pipeline bottlenecks. Data flow differs by family: branch rows count retired or speculative branch behavior; cycle rows count unhalted or reference cycles; `CYCLE_ACTIVITY` rows attribute stalls while cache/memory misses are outstanding; port/uop rows measure execution width, issue, and retirement pressure; machine-clear and assist rows expose pipeline flush or microcode-assist causes.

## State and Persistence Behavior

The file persists static event encodings, descriptions, sampling defaults, precision hints, errata annotations, and counter constraints. It does not store live branch, cycle, stall, or uop counts. Runtime state is held by CPU PMU counters and perf event contexts; fixed counters and programmable counters are allocated only while a perf event is active. Any generated metadata persists in perf's compiled PMU tables until the tool is rebuilt.

## Dependencies and Integration Points

The table depends on Cascade Lake X PMU behavior for Intel server cores derived from Skylake/Cascade Lake, including fixed counters, PEBS for precise branch-retired variants, Hyper-Threading semantics for `AnyThread`, and correct interpretation of `CounterMask`, `Invert`, and `EdgeDetect`. It is selected through the x86 mapfile entry for `GenuineIntel-6-55-[56789ABCDEF]`.

Integration points include `tools/perf/pmu-events/jevents.py` for event-string generation, generated `pmu-events.c` and `pmu-events.h` for lookup, `perf list` for display, `perf stat` for direct counts and top-down metric formulas, `perf record` for sampling PEBS-capable rows, and `tools/perf/tests/pmu-events.c` plus shell tests for generated-table validation. The file also supplies raw ingredients for metric groups described by `metricgroups.json`, especially `Pipeline`, `Branches`, `BadSpec`, `PortsUtil`, `Retire`, `Frontend`, and top-down `tma_*` groups.

## Risks and Edge Cases

Counter semantics are easy to misread. `CounterMask` and `Invert` rows often count cycles satisfying a threshold condition rather than raw event occurrences, so using them as numerator/denominator terms without unit awareness can produce invalid metrics. `AnyThread` variants count activity from either logical thread on a physical core and are not interchangeable with per-thread events. Fixed-counter events can schedule differently from programmable events and may interact with kernel/NMI watchdog constraints.

Branch-retired rows marked with errata `SKL091` should be treated carefully in tests and documentation. PEBS rows require precise-event support and may fail or degrade if the kernel, privilege level, or hardware constraints do not allow precise sampling. Execution-port and uop events are low-level microarchitectural signals; port binding, fused uops, macro-fusion, and SMT sharing can make direct source-code attribution misleading. Some rows have aliases or near-duplicates, such as `BR_INST_RETIRED.COND` and `BR_INST_RETIRED.CONDITIONAL`, so metric formulas should choose one spelling consistently.

## Test Signals

Static checks should validate JSON parsing, generated perf build success, and field coverage for optional modifiers (`CounterMask`, `Invert`, `EdgeDetect`, `AnyThread`, `PEBS`, `Errata`). `perf list` should show representative families such as `BR_INST_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, `UOPS_DISPATCHED_PORT.PORT_0`, and `UOPS_RETIRED.RETIRE_SLOTS`.

Runtime smoke tests on matching hardware should verify `perf stat` accepts a mix of fixed-counter and programmable rows. CPU-bound loops should move `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `UOPS_RETIRED.RETIRE_SLOTS`; unpredictable branches should increase `BR_MISP_RETIRED.*`; memory-latency workloads should affect `CYCLE_ACTIVITY.STALLS_MEM_ANY`; arithmetic kernels should move port/uop and `ARITH.DIVIDER_ACTIVE` counters when applicable. Sampling tests should cover at least one PEBS branch-retired event and report permission or precision failures separately from JSON/generation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/pipeline.json -->
