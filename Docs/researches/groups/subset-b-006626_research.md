# subset-b-006626 grouped research

This grouped report covers Arrow Lake and Bonnell x86 perf PMU event JSON files from the Ceph client copy of Linux `tools/perf`. Each section is source-tree aligned and intended for reconciliation into the corresponding `Docs/researches/<source>_research.md` file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/pipeline.json

## Purpose

This JSON file is the Arrow Lake pipeline-event catalog for Linux `perf`. It contains 306 core PMU event records covering arithmetic divider activity, assists, backend stalls, branch retirement and misprediction, unhalted clocks, cycle activity, execution activity, retirement, integer/vector uops, load blocks, loop stream detector behavior, machine clears, memory stalls, top-down slots, dispatch, issue, execution, and retirement pipeline categories. The x86 mapfile binds the `arrowlake` model directory to `GenuineIntel-6-C[56]`, so these records are selected for Arrow Lake family/model matches during perf PMU table generation.

## Important APIs, Types, And Data

The file is data, not executable code. Its effective API is the perf PMU event JSON schema consumed by `tools/perf/pmu-events/jevents.py`. Important fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `Unit`, `BriefDescription`, `PublicDescription`, `MSRIndex`, `MSRValue`, `Deprecated`, and `Errata`. `Unit` values split hybrid Arrow Lake events across `cpu_core`, `cpu_atom`, and `cpu_lowpower`; `jevents.py` converts those to PMU names used in generated event tables.

Major event families include `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `INST_RETIRED`, `LD_BLOCKS`, `MACHINE_CLEARS`, `TOPDOWN_*`, `UOPS_*`, `INT_MISC`, `INT_UOPS_EXECUTED`, and `INT_VEC_RETIRED`. Several logical names intentionally repeat with different event encodings or units, such as branch-retired, branch-mispredicted, top-down, clock, and divider events.

## Control Flow

At build time, `jevents.py` loads this array with `json.load(..., object_hook=JsonEvent)`. Each record is normalized into a `JsonEvent`: `EventName` is lowercased, `EventCode` becomes `event=...`, nonzero `UMask` becomes `umask=...`, `CounterMask` becomes `cmask=...`, `EdgeDetect` becomes `edge=...`, `Invert` becomes `inv=...`, and `SampleAfterValue` becomes `period=...`. `Unit` is translated into a PMU table key, then sorted generated `compact_pmu_event` entries are emitted into `pmu-events.c`.

At runtime, perf does not parse this JSON directly. Perf commands such as `perf list`, `perf stat -e`, and metric expansion read the compiled PMU event tables and match aliases against detected Arrow Lake core, atom, or low-power PMUs.

## State And Persistence Behavior

The JSON file persists architectural event metadata in source control. Runtime counter state is not stored here; perf opens hardware PMU file descriptors based on the generated event string. Deprecation and errata fields are persistent metadata that affect displayed descriptions and event quality warnings but do not create mutable program state.

## Dependencies And Integration Points

This file integrates with `arch/x86/mapfile.csv`, `jevents.py`, `pmu-events.h`, generated `pmu-events.c`, `tools/perf/util/pmu.c`, `builtin-list.c`, Python perf event listing, and PMU event tests. It also depends on Arrow Lake hardware event definitions matching Intel documentation and on hybrid PMU naming being compatible with the kernel-exposed PMU names.

## Risks And Edge Cases

Duplicate event names are valid only when separated by PMU or disambiguating fields; duplicates under the same generated PMU table can trigger `jevents.py` duplicate assertions. Hybrid unit mistakes can put a core-only event on atom PMUs or the reverse. Incorrect `CounterMask`, `EdgeDetect`, `Invert`, MSR fields, or periods silently changes perf measurement semantics. Deprecated entries such as `BR_INST_RETIRED.IND_CALL`, `LOAD_HIT_PREFETCH.HW_PF`, `MACHINE_CLEARS.SLOW`, and `TOPDOWN_FE_BOUND.ITLB` remain compatibility surfaces. Errata-tagged branch events, including ARL010 and ARL011 cases, need careful user-facing descriptions because the event can be architecturally present but not always trustworthy.

## Test Signals

Useful validation includes `jq empty` on the JSON, running `jevents.py` generation for x86 Arrow Lake, building `tools/perf`, `perf test pmu-events`, checking `perf list` for representative lowercased aliases, and validating generated event strings for branch, top-down, clock, and uop events on Arrow Lake-like PMU names. Regression tests should cover duplicate-name handling across `cpu_core`, `cpu_atom`, and `cpu_lowpower`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-cache.json

## Purpose

This file defines Arrow Lake uncore cache events for the HAC CBO PMU. It contains two TOR allocation counters: `UNC_HAC_CBO_TOR_ALLOCATION.ALL` and `UNC_HAC_CBO_TOR_ALLOCATION.DRD`. They expose cache-coherent queue allocation activity, including all TOR entries and data-read allocations.

## Important APIs, Types, And Data

The records use the perf JSON event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `Unit` is `HAC_CBO`, which `jevents.py` maps to an uncore PMU name by lowercasing and prefixing with `uncore_`. `PerPkg` marks these as package-level uncore counters rather than per-CPU thread counters.

## Control Flow

`jevents.py` reads both JSON entries, lowercases the event names, converts `EventCode` and nonzero `UMask` into perf event strings, and places them in the Arrow Lake generated PMU table for the `uncore_hac_cbo` PMU. Runtime perf commands match the generated alias against kernel uncore PMU devices.

## State And Persistence Behavior

The file stores static hardware-event metadata only. Counter values are produced by the uncore PMU at measurement time. Because these counters are per package, aggregation behavior depends on perf's PMU discovery and package selection rather than any mutable state in this JSON.

## Dependencies And Integration Points

Integration points include the Arrow Lake x86 mapfile row, `jevents.py` unit-to-PMU conversion, uncore PMU discovery in perf, generated `pmu-events.c`, and user-facing `perf list` output. The event semantics depend on the kernel exposing a compatible HAC CBO uncore PMU.

## Risks And Edge Cases

The small file has little internal complexity, but PMU naming is sensitive: a mismatch between `HAC_CBO` and the kernel uncore PMU name would make aliases undiscoverable. `PerPkg` mistakes can cause confusing aggregation. The descriptions distinguish all TOR entries from coherent data reads; swapping masks would make cache traffic analysis misleading.

## Test Signals

Validate with `jq empty`, x86 PMU event generation, `perf test pmu-events`, and `perf list` on a system or fixture exposing `uncore_hac_cbo`. Generated event strings should contain `event=0x35,umask=0x8` for `.all` and `event=0x35,umask=0x1` for `.drd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-interconnect.json

## Purpose

This file defines five Arrow Lake uncore interconnect events for the HAC ARB PMU. The events count coherent data-read request tracking and CMI transaction totals, reads, and writes.

## Important APIs, Types, And Data

Each entry uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `Unit` is `HAC_ARB`, mapping to an uncore PMU table. Event names include `UNC_HAC_ARB_REQ_TRK_REQUEST.DRD`, `UNC_HAC_ARB_TRANSACTIONS.ALL`, `.READS`, `.WRITES`, and `UNC_HAC_ARB_TRK_REQUESTS.ALL`.

## Control Flow

During generation, `jevents.py` canonicalizes the event and umask fields into perf config strings and emits aliases under the generated Arrow Lake uncore PMU event table. Runtime control then moves through perf alias lookup, PMU wildcard matching, and hardware counter programming for matching HAC ARB devices.

## State And Persistence Behavior

The JSON is a persistent event-definition table. Per-package counter readings and accumulation happen in perf and the kernel PMU driver. The file has no local state transitions and no persistence beyond generated C tables.

## Dependencies And Integration Points

The file depends on Arrow Lake model selection in `arch/x86/mapfile.csv`, `jevents.py` schema conversion, generated PMU event tables, perf uncore alias matching, and kernel uncore PMU naming. It integrates with `perf list` and `perf stat` workflows that inspect socket/package interconnect traffic.

## Risks And Edge Cases

Read/write/all masks must remain mutually meaningful; otherwise users can derive impossible traffic ratios. PMU unit spelling is the primary discoverability risk. Since these are uncore package events, tests must account for systems with multiple packages or absent HAC ARB PMUs.

## Test Signals

Run JSON validation and PMU event generation. Check generated aliases for `unc_hac_arb_transactions.all`, `.reads`, `.writes`, and request-tracker aliases. On hardware or a PMU fixture, `perf list` should place them under the uncore HAC ARB PMU and not under core PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-memory.json

## Purpose

This file defines 18 Arrow Lake uncore memory-controller events. It covers free-running read/write CAS and total request counters for memory controllers 0 and 1, plus integrated memory-controller DRAM ACT, CAS, refresh, precharge, and thermal state events.

## Important APIs, Types, And Data

The schema uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and `Experimental`. Units include `imc_free_running_0`, `imc_free_running_1`, and `iMC`, which map to uncore PMU names. Free-running entries use `EventCode` `0xff` with masks such as `0x10`, `0x20`, and `0x30`; command events use specific event codes such as ACT, CAS, PRE, REF, and thermal counters.

## Control Flow

`jevents.py` reads each record, canonicalizes the event code and nonzero umask, maps the unit to an uncore PMU, and emits compact event-table records. Runtime perf aliases then bind to memory-controller PMU devices and program either fixed/free-running style counters or programmable iMC events according to the generated config string.

## State And Persistence Behavior

The JSON stores metadata. Memory-controller counter state exists in hardware and perf file descriptors. `PerPkg` means package-level aggregation is expected. `Experimental` on `UNC_M_DRAM_THERMAL_HOT` and `UNC_M_DRAM_THERMAL_WARM` persists into generated metadata and should signal lower confidence or unstable semantics to tools that expose it.

## Dependencies And Integration Points

Dependencies include Arrow Lake model mapping, `jevents.py`, perf PMU table generation, memory-controller PMU discovery, and user-visible perf list/stat output. The records also integrate with bandwidth and DRAM-behavior analysis workflows that combine read CAS, write CAS, total requests, ACT/PRE/REF, and thermal state counts.

## Risks And Edge Cases

The same `EventCode`/`UMask` values appear under different controller units; unit mapping must not collapse controller 0 and controller 1 unless perf intentionally wildcard-matches them. Free-running counters can have different availability and programming rules than normal counters. Experimental thermal events may be missing, renamed, or semantically unstable. Incorrect `PerPkg` handling can double-count or undercount memory traffic on multi-socket systems.

## Test Signals

Validate JSON syntax, run x86 `jevents.py` generation, and inspect generated PMU entries for all three units. On compatible hardware, `perf list` should show controller-specific free-running aliases and iMC command aliases. Functional checks should compare read/write CAS counts under memory load and verify experimental thermal aliases do not break generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-other.json

## Purpose

This one-entry file defines `UNC_CLOCK.SOCKET`, the Arrow Lake uncore socket clock fixed counter. It provides a 48-bit UCLK cycle reference for uncore measurements.

## Important APIs, Types, And Data

The entry uses `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `EventCode` is `0xff`, `Unit` is `CNCU`, and `PerPkg` marks package-level scope. There is no `UMask`, so `jevents.py` emits only the event selector.

## Control Flow

Generation follows the standard PMU JSON path: `jevents.py` builds a `JsonEvent`, maps `CNCU` to an uncore PMU name, and emits the alias into generated tables. Runtime perf uses the compiled alias to open the corresponding uncore clock counter.

## State And Persistence Behavior

The source file persists the alias and description. Hardware maintains the 48-bit uncore clock count. The JSON does not persist samples or derived rates.

## Dependencies And Integration Points

This event integrates with Arrow Lake uncore PMU discovery and can serve as a denominator or sanity signal for other uncore package events. It depends on kernel PMU support for the CNCU uncore device and on generated table lookup in perf.

## Risks And Edge Cases

Fixed clock counters often have different programming semantics from programmable counters. A width assumption mismatch around the 48-bit count can affect long-running measurements. Unit-name drift would make the alias hard to find.

## Test Signals

Use JSON validation, event generation, and `perf list` alias checks. On hardware, count monotonicity under idle and load is the main functional signal; the event should be package scoped and should not appear as a core PMU event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/virtual-memory.json

## Purpose

This file defines 65 Arrow Lake virtual-memory and TLB-related core PMU events. It covers DTLB load and store misses, ITLB misses, page-walk completions by page size, walk pending/active cycles, page-walker memory-source loads, load-head DTLB retirement signals, load blocks, and TLB flushes.

## Important APIs, Types, And Data

Records use the same perf event JSON schema as the pipeline file: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `Unit`, `BriefDescription`, and `PublicDescription`. Units include `cpu_core`, `cpu_atom`, and `cpu_lowpower`, reflecting Arrow Lake hybrid PMU coverage. Repeated logical names such as `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_STORE_MISSES.STLB_HIT`, and `ITLB_MISSES.WALK_PENDING` encode per-unit or per-generation variants.

## Control Flow

At generation time, `jevents.py` lowercases event names, converts event selectors and masks into perf config strings, preserves periods from `SampleAfterValue`, and emits separate generated tables by PMU unit. At runtime, perf resolves aliases against the detected core, atom, or low-power PMU and programs the selected TLB/page-walk counter.

## State And Persistence Behavior

The JSON persists event metadata and descriptions, not TLB state. Hardware and kernel PMU file descriptors produce per-run counts. Sample periods persist into generated aliases as default period hints. Repeated names rely on generated table PMU separation to avoid duplicate conflicts.

## Dependencies And Integration Points

This file integrates with Arrow Lake x86 model selection, `jevents.py`, generated PMU tables, `perf list`, `perf stat`, and workflows that diagnose translation overhead, huge-page behavior, instruction fetch misses, page walks, and TLB shootdowns. It depends on kernel PMU names matching `cpu_core`, `cpu_atom`, and `cpu_lowpower` mappings.

## Risks And Edge Cases

Hybrid event differences are the highest risk: same event names can have different event codes, masks, or descriptions across PMU units. Page-size-specific events are easy to misinterpret when huge pages are disabled or mixed. Counter masks on walk-pending events change counts from occurrences to cycles above a threshold. Missing or wrong public descriptions can obscure whether the event counts starts, completions, active cycles, or memory-source loads.

## Test Signals

Validate JSON syntax, generate PMU tables, and check representative aliases for DTLB load/store miss walks, ITLB walks, page-walker loads, and TLB flushes. Runtime signals include synthetic pointer-chasing workloads, huge-page versus 4K-page comparisons, instruction-cache/TLB stress tests, and duplicate-name checks across Arrow Lake PMU units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/cache.json

## Purpose

This file is the Bonnell cache-event catalog for perf. It contains 93 events covering L1D references and evictions, L2 address/data bus activity, L2 instruction fetch states, L2 load/store requests by MESI state, line fills and evictions, locks, request rejection, no-request cycles, and retired load cache-miss signals.

## Important APIs, Types, And Data

The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Unlike Arrow Lake records, these Bonnell core events generally omit `Unit`; absent unit maps through `jevents.py` to the default core PMU table. Event families include `L1D_CACHE`, `L2_DATA_RQSTS`, `L2_IFETCH`, `L2_LD`, `L2_LD_IFETCH`, `L2_LINES_IN`, `L2_LINES_OUT`, `L2_LOCK`, `L2_REJECT_BUSQ`, `L2_RQSTS`, `L2_ST`, and `MEM_LOAD_RETIRED`.

## Control Flow

The build-time flow reads the JSON array, creates `JsonEvent` objects, converts selectors and masks to generated perf event strings, and emits Bonnell entries selected by the `GenuineIntel-6-(1C|26|27|35|36)` mapfile row. Runtime perf resolves aliases from the generated table for Bonnell-family systems.

## State And Persistence Behavior

The source persists static event definitions for old Intel Atom/Bonnell systems. Runtime cache state and counters live in hardware. `SampleAfterValue` persists as default sampling periods in generated aliases, but perf users can override sampling and counting behavior.

## Dependencies And Integration Points

Dependencies include the x86 mapfile Bonnell row, `jevents.py`, generated PMU event tables, perf alias lookup, and tests that compare generated event fields. The cache events integrate with `perf list`, `perf stat`, and performance analysis of cache hierarchy behavior on Bonnell-class CPUs.

## Risks And Edge Cases

Many L2 families differ only by MESI mask or request type, so mask transposition is a realistic risk. Some event names encode `.SELF` or MESI state distinctions that users may mistake for system-wide counts. Absent `Unit` means accidental introduction of unit fields or duplicate names can alter table placement. Older hardware availability makes runtime validation harder.

## Test Signals

Use JSON validation and generated-table tests. Representative generated aliases should include L1D references, L2 MESI request variants, L2 line-in/out variants, lock events, and `MEM_LOAD_RETIRED` cache-miss entries. On Bonnell hardware, cache-stress microbenchmarks should move L1/L2 reference and miss counters in expected directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/counter.json

## Purpose

This metadata file declares Bonnell counter topology rather than a normal event alias. It states that the `core` unit has `CountersNumGeneric` set to 2 and `CountersNumFixed` set to 3.

## Important APIs, Types, And Data

The single object uses `Unit`, `CountersNumGeneric`, and `CountersNumFixed`. It intentionally lacks `EventName`, `EventCode`, and descriptions, so it is not an event users select by alias. The values describe the hardware counter resources available to perf and generated PMU metadata consumers.

## Control Flow

When `jevents.py` reads this file, the object has no `EventName`, so it does not become a normal pending event. Its fields are still part of the PMU event metadata corpus and can inform generated tables or tooling paths that inspect counter resources.

## State And Persistence Behavior

The file persistently documents Bonnell core counter counts. It does not track allocation state. Runtime allocation and scheduling of two generic counters and three fixed counters is managed by perf and the kernel PMU driver.

## Dependencies And Integration Points

The metadata integrates with the Bonnell model directory and perf PMU event generation. It is relevant to event scheduling, group feasibility, and user expectations when too many events are requested for simultaneous counting.

## Risks And Edge Cases

Because the object is structurally different from event records, schema consumers must tolerate records without `EventName`. Treating this as a malformed event would break generation. Incorrect counter counts can mislead scheduling diagnostics and event-group expectations.

## Test Signals

Validation should confirm the JSON parses and `jevents.py` generation does not emit an empty bogus alias. Perf event scheduling tests on Bonnell-like fixtures should respect two programmable and three fixed counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/floating-point.json

## Purpose

This file defines 32 Bonnell floating-point, x87, SIMD, and assist events. It covers floating-point assists, SIMD assists, retired SIMD instructions by scalar/vector form, saturated arithmetic, SIMD uop execution and type breakdowns, and x87 computational operations.

## Important APIs, Types, And Data

The schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `PEBS`, and `BriefDescription`. Event families include `FP_ASSIST`, `SIMD_ASSIST`, `SIMD_COMP_INST_RETIRED`, `SIMD_INSTR_RETIRED`, `SIMD_INST_RETIRED`, `SIMD_SAT_INSTR_RETIRED`, `SIMD_SAT_UOP_EXEC`, `SIMD_UOPS_EXEC`, `SIMD_UOP_TYPE_EXEC`, and `X87_COMP_OPS_EXE`. `PEBS` marks precise-capable retired or at-retirement events such as `SIMD_UOPS_EXEC.AR` and selected x87 events.

## Control Flow

Build-time conversion lowercases names and emits event strings from the event code and umask. When `PEBS` is present, `jevents.py` augments descriptions with precise-event text unless already present. Runtime perf uses the generated aliases to program Bonnell core counters and can request precise sampling when the hardware and event support it.

## State And Persistence Behavior

The file stores static metadata. Floating-point assist and SIMD execution counts are runtime hardware state. `PEBS` is persistent metadata used by tools and users to distinguish precise sampling candidates, but actual precise-buffer state is controlled by perf and the kernel.

## Dependencies And Integration Points

Integration points include Bonnell model mapping, `jevents.py` PEBS handling, generated event tables, perf event parsing, and test fixtures that compare event strings and descriptions. These events support analysis of FP exception assists, SIMD mix, saturation, and x87 usage.

## Risks And Edge Cases

Precise-event metadata must be correct; marking a non-precise event as PEBS can produce failed or misleading sampling, while omitting PEBS hides useful attribution. SIMD type masks are dense and easy to swap. Some events count instructions while others count uops or assists, so descriptions need to remain explicit.

## Test Signals

Run JSON validation and PMU event generation. Generated descriptions for PEBS entries should include precise-event wording. Workload tests can use scalar FP, packed SIMD, saturated arithmetic, and x87-heavy loops to validate directionality of aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/frontend.json

## Purpose

This file defines 11 Bonnell frontend events. It covers branch address clears, instruction-cache access/hit/miss events, instruction-fetch memory stalls, decode stalls, decoded macro-instruction categories, and micro-sequencer uop cycles.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, and `BriefDescription`. Event families include `BACLEARS`, `CYCLES_ICACHE_MEM_STALLED`, `DECODE_STALL`, `ICACHE`, `MACRO_INSTS`, and `UOPS.MS_CYCLES`. `CounterMask` appears where cycle qualification matters.

## Control Flow

`jevents.py` converts each record to generated aliases selected for Bonnell models. Nonzero `CounterMask` becomes `cmask=...`; masks and sampling periods become perf config terms. Runtime perf users select aliases from the generated PMU table to diagnose frontend bottlenecks.

## State And Persistence Behavior

The JSON persists frontend event metadata. Hardware frontend state, stalls, and instruction-cache behavior are counted only during perf sessions. Sampling periods persist into generated aliases as defaults.

## Dependencies And Integration Points

The file integrates with the Bonnell x86 mapfile row, generated PMU event tables, perf list/stat display, and frontend bottleneck analysis. It also relies on `jevents.py` correctly translating `CounterMask` and event masks.

## Risks And Edge Cases

Decode stall categories can overlap or be workload-sensitive. `CounterMask` changes event interpretation from raw occurrence to qualified cycles. Instruction-cache hit/miss/access events must remain mask-consistent to avoid impossible ratios. The micro-sequencer event includes assists and inserted flows, so it should not be described as normal decode throughput.

## Test Signals

Validate JSON syntax and generated aliases. Use instruction-cache stress, branch-heavy code, and decode-pressure microbenchmarks to check counter direction. Generated event strings should preserve `cmask` where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/memory.json

## Purpose

This file defines 19 Bonnell memory-access events. It focuses on misaligned memory references, split loads/stores/read-modify-write operations, nonzero segment-base bubbles, and hardware/software prefetch request types.

## Important APIs, Types, And Data

The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Event families are `MISALIGN_MEM_REF` and `PREFETCH`. Several misalignment events have `.AR` at-retirement variants, while prefetch entries distinguish hardware, software, L1, L2, NTA, and load-prefetch forms.

## Control Flow

The build path converts the JSON into generated Bonnell perf aliases. Event code `0x5` with different masks represents the misalignment family, while event code `0x7` masks represent prefetch categories. Runtime perf programs the selected alias on Bonnell PMUs.

## State And Persistence Behavior

The JSON persists event definitions. Runtime memory alignment behavior and prefetch activity are counted by hardware. `.AR` variants persist as separate aliases to distinguish retirement-qualified observations from earlier pipeline observations.

## Dependencies And Integration Points

Dependencies include `jevents.py`, Bonnell model selection, generated event tables, perf alias matching, and user workflows that diagnose split accesses, segment-base overhead, and prefetch behavior.

## Risks And Edge Cases

Misalignment events distinguish splits from bubbles and load/store/RMW forms; mask mistakes can make optimization conclusions wrong. The description typo on one store split entry should not affect generation but may be visible in `perf list`. Prefetch events can be speculative and may not correlate directly with useful demand-load behavior.

## Test Signals

Validate JSON and generated event strings. Microbenchmarks with aligned versus intentionally split accesses should change `MISALIGN_MEM_REF` aliases. Prefetch-heavy loops and software prefetch instructions should exercise `PREFETCH` aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/other.json

## Purpose

This file defines 55 miscellaneous Bonnell events, mostly external bus, snoop, interrupt masking, SpeedStep, thermal, and segment-register-load counters. It covers bus transaction classes, bus-ready/data-ready/lock/HIT/HITM signals, outstanding requests, snoop responses, interrupt masking cycles, hardware interrupt receipt, EIST transitions, and thermal trips.

## Important APIs, Types, And Data

The records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Families include `BUS_*`, `EXT_SNOOP`, `CYCLES_INT_MASKED`, `EIST_TRANS`, `HW_INT_RCV`, `SEGMENT_REG_LOADS`, `SNOOP_STALL_DRV`, and `THERMAL_TRIP`. Several bus events have `.THIS_AGENT`, `.ALL_AGENTS`, `.SELF`, or transaction-type suffixes.

## Control Flow

Generation converts each record into a generated Bonnell perf alias. Masks distinguish bus transaction classes and agent scope. At runtime, perf opens the corresponding core PMU event and counts bus or miscellaneous processor signals.

## State And Persistence Behavior

The JSON is static metadata. Runtime bus, snoop, interrupt, thermal, and power-transition counts are hardware state. Default sampling periods persist as generated event fields.

## Dependencies And Integration Points

This file integrates with Bonnell model mapping, `jevents.py`, generated PMU tables, and perf list/stat. It is relevant for platform-level diagnosis on older Atom systems where external bus and snoop events are important.

## Risks And Edge Cases

Agent scope suffixes are easy to misread: `.ALL_AGENTS`, `.THIS_AGENT`, and `.SELF` do not mean the same thing. Bus transaction masks are dense and similar, increasing maintenance risk. Some events depend heavily on platform topology and may be unavailable or low-value under virtualization. Thermal and EIST events are system-management signals rather than instruction-level performance counters.

## Test Signals

Validate JSON and generated aliases. Generation tests should confirm representative bus transaction, snoop, EIST, interrupt, and thermal aliases. Runtime validation can use I/O-heavy, memory-sharing, interrupt-heavy, and power-state-transition workloads on Bonnell hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/pipeline.json

## Purpose

This file defines 45 Bonnell pipeline events. It covers branch decode and retirement, branch prediction and misprediction types, unhalted clocks, divider and multiplier activity, dispatch blocking, retired instructions and uops, machine clears, reissue conditions, resource stalls, and store forwarding.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `PEBS`, and `BriefDescription`. Families include `BOGUS_BR`, `BR_INST_DECODED`, `BR_INST_RETIRED`, `BR_INST_TYPE_RETIRED`, `BR_MISSP_TYPE_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLES_DIV_BUSY`, `DISPATCH_BLOCKED`, `DIV`, `INST_RETIRED`, `MACHINE_CLEARS`, `MUL`, `REISSUE`, `RESOURCE_STALLS`, `STORE_FORWARDS`, and `UOPS_RETIRED`. `BR_INST_RETIRED.MISPRED` and `INST_RETIRED.ANY_P` are PEBS-capable.

## Control Flow

`jevents.py` converts the JSON records into generated aliases selected for Bonnell family/model rows. PEBS metadata updates descriptions for precise-capable events. Runtime perf resolves branch, clock, execution, and stall aliases from the generated table and programs the underlying PMU.

## State And Persistence Behavior

The file persists event definitions and default periods. Hardware pipeline state is sampled or counted only during perf runs. Precise-event capability is metadata; actual PEBS buffer behavior is managed outside the JSON by perf and the kernel.

## Dependencies And Integration Points

Integration points include x86 mapfile selection, `jevents.py`, generated PMU tables, perf list/stat/record, and test fixtures for generated event descriptors. These events support pipeline bottleneck and branch behavior analysis on Bonnell CPUs.

## Risks And Edge Cases

Branch event suffixes distinguish predicted/not-taken/taken/mispredicted/type-specific forms; mask mistakes can invalidate derived rates. Some events count cycles, some instructions, and some uops, so combining them requires unit awareness. PEBS markings must match hardware support. Old Bonnell behavior may be hard to validate on modern systems.

## Test Signals

Validate JSON, generated event strings, and PEBS description handling. Branch-heavy, divider-heavy, multiplier-heavy, store-forwarding, and stall microbenchmarks should move representative aliases. `perf test pmu-events` should catch malformed generated entries or duplicate aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/virtual-memory.json

## Purpose

This file defines 15 Bonnell virtual-memory events. It covers data TLB misses for loads and stores, L0 DTLB misses, ITLB hits/misses/flushes, retired load DTLB misses, and page-walk cycles or walk counts for data side, instruction side, or combined paths.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `PEBS`, and `BriefDescription`. Families include `DATA_TLB_MISSES`, `ITLB`, `MEM_LOAD_RETIRED`, and `PAGE_WALKS`. `ITLB.MISSES` and `MEM_LOAD_RETIRED.DTLB_MISS` include PEBS metadata.

## Control Flow

The build path converts each event into generated Bonnell perf aliases. Event and mask fields become perf config strings, sampling periods become generated default periods, and PEBS-capable entries gain precise-event description text. Runtime perf uses the generated aliases to program TLB and page-walk counters.

## State And Persistence Behavior

The JSON stores static event metadata. TLB contents, misses, and page walks are runtime hardware state. PEBS capability and default sampling periods persist through generated tables but do not allocate buffers or samples by themselves.

## Dependencies And Integration Points

This file depends on Bonnell x86 model mapping, `jevents.py`, generated PMU tables, perf alias lookup, and PMU tests. It integrates with memory-translation diagnosis, page-size analysis, and instruction-fetch miss investigation on Bonnell systems.

## Risks And Edge Cases

`PAGE_WALKS` contains both cycle-duration and number-of-walk events with overlapping event codes and masks, so descriptions are essential. Load/store DTLB aliases can be confused with retired load-only PEBS events. ITLB hit/miss/flush counts may not compose cleanly into ratios if flushes or speculation intervene.

## Test Signals

Validate JSON and generated aliases. Runtime tests can use pointer-chasing, store-heavy TLB stress, instruction-footprint stress, and page-size changes. Generated entries should preserve PEBS metadata for `ITLB.MISSES` and `MEM_LOAD_RETIRED.DTLB_MISS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/virtual-memory.json -->
