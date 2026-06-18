# Research: subset-b-006721

Grouped research for Skylake Server x86 perf PMU event data under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/frontend.json

## Purpose

`frontend.json` is a Skylake Server PMU event manifest for front-end pipeline behavior. It defines 49 core PMU aliases covering branch resteers, length-changing-prefix decode stalls, DSB-to-MITE transitions, retired-instruction front-end miss attribution, instruction-cache/tag stalls, IDQ delivery source, microcode sequencer delivery, and front-end uop delivery starvation.

The file is consumed as data by `tools/perf/pmu-events/jevents.py`; it is not executable code. During the perf build, `jevents.py` walks model JSON files, assigns the topic from the filename (`frontend`), converts every JSON object into a `JsonEvent`, and emits generated C table entries in `pmu-events.c`. At runtime those entries become perf aliases visible through `perf list` and usable in `perf stat -e <event>`.

## Important Schema, APIs, and Event Families

The important contract is the perf PMU JSON schema:

- `EventName` is the exported perf alias, lower-cased by `JsonEvent`.
- `EventCode` and `UMask` become the low-level `event=` and `umask=` fields.
- `Counter`, `CounterMask`, `Invert`, and `EdgeDetect` constrain scheduling and event semantics.
- `SampleAfterValue` becomes the default sampling `period=`.
- `BriefDescription` and `PublicDescription` become short and long descriptions.
- `PEBS`, `MSRIndex`, and `MSRValue` mark precise events and special MSR encodings.

Key families are:

- `BACLEARS.ANY`, for branch-address-calculator/front-end resteers.
- `DECODE.LCP`, an alias of `ILD_STALL.LCP`, for length-changing-prefix stalls.
- `DSB2MITE_SWITCHES.*`, with `COUNT` and `PENALTY_CYCLES` on event `0xAB`.
- `FRONTEND_RETIRED.*`, 19 PEBS events on event `0xC6` using MSR `0x3F7` and `frontend=` values to classify DSB, iTLB, L1I, L2, STLB, latency, and bubble-slot exposure.
- `ICACHE_16B.*`, `ICACHE_64B.*`, and `ICACHE_TAG.STALLS`, for instruction fetch data/tag hits, misses, and stalls.
- `IDQ.*` and `IDQ_UOPS_NOT_DELIVERED.*`, for uop source cycles, MITE/DSB/MS delivery, and insufficient front-end delivery.

## Control Flow and Integration

`jevents.py` processes this file through `preprocess_one_file()` and `process_one_file()`. `read_json_events()` loads the JSON array with `object_hook=JsonEvent`, so each dictionary is converted immediately. The converter builds an event string from `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, `SampleAfterValue`, and any recognized MSR mapping. For `MSRIndex` `0x3F7`, the generated field is `frontend=<MSRValue>`.

The resulting events are appended to `_pending_events` for the SkylakeX model directory. When the directory table is flushed, perf emits aliases with topic `frontend`. `builtin-list.c` can print them, and `util/pmu.c` later matches the generated table against the runtime CPU selected through `arch/x86/mapfile.csv`, where SkylakeX is mapped from `GenuineIntel-6-55-[01234]` to the `skylakex` directory.

## State and Persistence Behavior

The source file itself is static repository data. Persistent derived state is the generated `pmu-events.c` built into perf, plus installed perf alias data. Runtime profiling state is handled by perf and the kernel PMU; this JSON file stores no counters or mutable state.

Default periods are part of the persisted alias contract. Most front-end cycle events use large periods such as `2000003`, while retired front-end PEBS events use `100007`. Changing these values does not change event meaning, but it changes default sampling behavior.

## Dependencies

This manifest depends on:

- Intel Skylake Server PMU event encodings, including event codes, umasks, cmasks, and MSR selectors.
- `jevents.py` support for recognized fields and the `0x3F7 -> frontend=` MSR mapping.
- perf generated table types declared under `tools/perf/pmu-events/pmu-events.h`.
- x86 model mapping in `tools/perf/pmu-events/arch/x86/mapfile.csv`.

## Risks and Edge Cases

The highest-risk area is the `FRONTEND_RETIRED.*` family because many aliases share `EventCode` `0xC6`, `UMask` `0x1`, and `MSRIndex` `0x3F7`; the `MSRValue` is what differentiates them. A wrong MSR value would still produce syntactically valid aliases but measure a different front-end condition.

The IDQ families rely heavily on `CounterMask` and sometimes `Invert`; schema-preserving validation is not enough to prove semantic correctness. The `DECODE.LCP` alias overlaps conceptually with `pipeline.json`'s `ILD_STALL.LCP`, so duplicate-looking aliases need to remain intentional.

Text descriptions include hardware-specific caveats and spelling quirks. `JsonEvent.fixdesc()` strips final punctuation and escapes text, so description-only diffs can affect generated C string tables and `perf list` output without changing measurement behavior.

## Test Signals

Useful validation signals are:

- `jq empty frontend.json` to verify JSON syntax.
- Build perf with jevents enabled and confirm generated `pmu-events.c` includes topic `frontend`.
- `perf list frontend` or raw `perf list` on a matching SkylakeX system to confirm aliases appear.
- `perf stat -e idq_uops_not_delivered.core,frontend_retired.latency_ge_16 <workload>` on supported hardware.
- Existing perf PMU tests in `tools/perf/tests/pmu-events.c`, which verify generated table and alias behavior for representative JSON input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/memory.json

## Purpose

`memory.json` is the Skylake Server PMU manifest for memory, offcore, transaction, and memory-ordering events. It defines 115 aliases. The file covers L3-miss stall cycles, HLE/RTM transactional outcomes, machine clears from memory ordering, precise load-latency thresholds, offcore request and response classifications, and TSX memory abort details.

As with the other PMU manifests, this file is build-time data for `jevents.py`. Its topic is derived from the filename as `memory`, and its events become generated perf aliases for the SkylakeX CPU table.

## Important Schema, APIs, and Event Families

The core schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, descriptions, and optional special fields:

- `PEBS` marks precise-capable events. The load-latency aliases use `PEBS: "2"` and `Data_LA: "1"`, which causes `jevents.py` to append precise/address-support notes to descriptions.
- `MSRIndex` and `MSRValue` are central here. `0x3F6` maps to `ldlat=` for load-latency thresholds. `0x1A6` and `0x1A7` map to `offcore_rsp=` for offcore response filters.
- `Errata` is present for `MACHINE_CLEARS.MEMORY_ORDERING` with `SKL089`; `jevents.py` appends a spec-update note to descriptions.

Important event groups:

- `CYCLE_ACTIVITY.CYCLES_L3_MISS` and `CYCLE_ACTIVITY.STALLS_L3_MISS` on event `0xA3`, distinguishing outstanding L3 miss cycles from exposed execution stalls.
- `HLE_RETIRED.*` and `RTM_RETIRED.*` on events `0xC8` and `0xC9`, tracking transaction starts, commits, and abort classes.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_{4,8,16,32,64,128,256,512}`, all using event `0xCD`, PEBS, data linear address support, MSR `0x3F6`, and threshold-specific `MSRValue`.
- `OFFCORE_REQUESTS*`, for demand data read L3 misses and outstanding request occupancy.
- `OFFCORE_RESPONSE.*`, a large matrix of request types and L3-miss response classes sharing `EventCode` `0xB7, 0xBB`, MSR selectors `0x1a6,0x1a7`, and distinct `MSRValue` filters.
- `TX_EXEC.*` and `TX_MEM.*`, for TSX execution and memory abort causes.

## Control Flow and Integration

`jevents.py` loads each object as a `JsonEvent`. For offcore response objects, it takes the first event code from the comma-separated `EventCode` field when constructing the base `event=` string, while the `MSRIndex`/`MSRValue` pair supplies the offcore response filter. The generated alias therefore depends on both the event selector and the model-specific offcore MSR bits.

At build time, this file contributes entries to the SkylakeX model event table. At runtime, perf exposes these names as event aliases for matching CPUs. The offcore and load-latency events rely on kernel support for programming the relevant MSRs and precise sampling modes.

## State and Persistence Behavior

The JSON file stores static event definitions only. The persistent output is generated C data in perf. Runtime state includes programmed PMU counters, PEBS records, offcore response MSR state, and sampled data addresses, all managed by perf and the kernel.

`SampleAfterValue` choices vary significantly. Load-latency thresholds use smaller periods for rarer events, for example `101` for `LOAD_LATENCY_GT_512` and `1009` for `LOAD_LATENCY_GT_128`, while broad events generally use larger periods. Those defaults affect sampling density and overhead.

## Dependencies

Dependencies include:

- Intel Skylake Server event encodings and offcore response filter bit layouts.
- `jevents.py` MSR mappings for `0x3F6`, `0x1A6`, and `0x1A7`.
- Kernel PMU support for PEBS, data address capture, TSX/HLE/RTM events, and offcore response MSRs.
- Perf alias generation and CPU model dispatch through the x86 mapfile.

## Risks and Edge Cases

The offcore response matrix is the most fragile part of the file. Many aliases share identical `EventCode`, `UMask`, `Counter`, and MSR index fields, with only `MSRValue` differentiating demand reads, RFOs, prefetches, local DRAM, remote DRAM, remote HITM, and snoop outcomes. A single bit error can silently redirect an alias to a different memory-source category.

Comma-separated `EventCode` and `MSRIndex` values rely on `jevents.py` behavior that uses the first value for conversion while preserving the intended offcore filter path. Any parser change must be checked against this pattern.

PEBS load-latency aliases report latency from dispatch to completion, not pure memory latency, according to the descriptions. Documentation and metric consumers should avoid treating these as direct DRAM-only latency counters.

TSX/HLE events may be unavailable, disabled, or affected by microcode and platform policy even when the alias exists. Perf alias availability does not guarantee a useful nonzero count on every SkylakeX deployment.

## Test Signals

Useful checks are:

- `jq empty memory.json` and a generated perf build to catch syntax and schema conversion failures.
- Inspection of generated event strings for `ldlat=` and `offcore_rsp=` fields.
- `perf list memory` and `perf list | grep -i offcore_response` on SkylakeX-class hardware.
- Targeted `perf stat` runs using `mem_trans_retired.load_latency_gt_64` and a representative `offcore_response.*` alias.
- Hardware-aware comparison of local/remote DRAM and HITM counters under NUMA or sharing workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/metricgroups.json

## Purpose

`metricgroups.json` is a dictionary of metric-group descriptions for Skylake Server. It does not define counter events. Instead, it maps 138 group names to human-readable descriptions used by perf's metric listing and metric-group display paths.

Most entries are short descriptions imported from Intel's Top-down Microarchitecture Analysis metrics spreadsheet. The file includes broad groups such as `Frontend`, `Backend`, `MemoryBound`, `Pipeline`, `Power`, and `Summary`, legacy/grouping labels such as `Bv*`, and generated top-down hierarchy groups such as `TopdownL1` through `TopdownL6` and `tma_*_group`.

## Important Schema, APIs, and Groups

Unlike event files, this file is a JSON object rather than an array. Keys are metric group names and values are descriptions. `jevents.py` treats files ending in `metricgroups.json` specially in `preprocess_one_file()`: it loads the object, appends NUL terminators, interns both key and description into the shared big C string, and stores them in `_metricgroups`.

Important names include:

- Top-level analysis buckets: `Frontend`, `Backend`, `BadSpec`, `Retire`, `MemoryBound`, `Pipeline`, `HPC`, `Power`, and `Summary`.
- Memory-oriented groups: `Mem`, `MemOffcore`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Memory_BW`, and `Memory_Lat`.
- Front-end and code groups: `DSB`, `DSBmiss`, `FetchBW`, `FetchLat`, `IcMiss`, `LSD`, `MicroSeq`, and `CodeGen`.
- Top-down hierarchy aliases: `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`.
- Category-specific TMA groups: `tma_frontend_bound_group`, `tma_memory_bound_group`, `tma_branch_mispredicts_group`, `tma_ports_utilization_group`, `tma_machine_clears_group`, and related `tma_issue*` groups.

## Control Flow and Integration

`metricgroups.json` is only consumed during the preprocessing pass. It is explicitly skipped by `process_one_file()` so it does not create PMU event entries. The collected `_metricgroups` mapping is emitted into generated perf data that supports listing metric group descriptions.

The integration point is perf metric discovery and printing. `builtin-list.c` has dedicated logic for metric groups, and `perf stat -M <metric-or-group>` relies on metric metadata generated from the PMU event tree. The group descriptions help users interpret available metric bundles but do not define formulas themselves.

## State and Persistence Behavior

The source file is static metadata. Generated descriptions are persisted in the built perf binary through interned C strings. There is no runtime mutable state in this file. Changing a description affects `perf list metricgroups` style output, while changing a key can affect group lookup and user command compatibility.

## Dependencies

Dependencies include:

- `jevents.py` special handling for `metricgroups.json`.
- Metric definitions in adjacent or generated metrics files that reference these group names.
- `metricgroup.c`, `builtin-list.c`, and `builtin-stat.c` behavior for showing and selecting metric groups.
- Naming compatibility with Intel top-down metric naming conventions.

## Risks and Edge Cases

The key names are effectively user-facing API. Renaming `MemoryBound`, `TopdownL1`, or a `tma_*_group` can break scripts using `perf stat -M` or filtering `perf list metricgroups`.

Several groups are near-duplicates or compatibility variants, such as `MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, and `MemoryLat` and `Memory_Lat`. These are likely intentional compatibility aliases; cleanup that normalizes names could remove useful entry points.

Because all values are descriptions, JSON syntax validation is necessary but insufficient. A typo in a key may not fail the build, but the group would no longer describe or match the intended metrics.

## Test Signals

Useful checks are:

- `jq 'keys | length' metricgroups.json`, currently 138.
- Build perf and confirm `jevents.py` accepts the object form.
- `perf list metricgroups` to verify group names and descriptions are visible.
- `perf stat -M TopdownL1` and representative `tma_*` group invocations on supported systems.
- Grep metric JSON/generated metric output for references to key names after any rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/other.json

## Purpose

`other.json` is a small Skylake Server PMU event manifest for events that do not fit the main topic files. It defines 6 aliases: four core power license/throttle events, one hardware interrupt counter, and one memory-disambiguation history reset event.

The filename gives these aliases the perf topic `other`. They are converted by `jevents.py` into generated C event entries for the SkylakeX CPU event table.

## Important Schema, APIs, and Event Families

The schema is the standard PMU event array schema. Each object includes `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and descriptions where available.

The main families are:

- `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE`, all on event `0x28` with different umasks. These classify cycles by power-delivery/turbo license level, including non-AVX/SSE/low-current AVX, AVX2-class, and AVX-512-class operation.
- `CORE_POWER.THROTTLE`, also on event `0x28`, umask `0x40`, for cycles throttled due to pending power-level requests.
- `HW_INTERRUPTS.RECEIVED`, event `0xCB`, umask `0x1`, for hardware interrupts received by the processor.
- `MEMORY_DISAMBIGUATION.HISTORY_RESET`, event `0x09`, umask `0x1`, with a terse self-description.

## Control Flow and Integration

`jevents.py` processes this as a normal event JSON file. The generated topic is `other`, the default PMU is `default_core`, and each alias is included in the SkylakeX generated event table. Users access these through `perf list other` or by naming the lower-case alias in perf event selectors.

The four `CORE_POWER.*` entries share the same event selector and are differentiated by umask, so they integrate as related aliases over one architectural event family.

## State and Persistence Behavior

The file is static metadata. The generated perf binary persists alias definitions and descriptions. Runtime counter state is owned by the PMU and perf. Default sampling periods are `200003` for core power events, `203` for hardware interrupts, and `2000003` for memory-disambiguation history resets.

## Dependencies

Dependencies include:

- Skylake Server core PMU support for event `0x28`, `0xCB`, and `0x09`.
- `jevents.py` standard event-field conversion.
- Perf alias display and runtime event parsing.

## Risks and Edge Cases

The `CORE_POWER.*` events describe license levels where turbo may be clipped; they should not be interpreted as direct package power or frequency readings. Platform firmware, AVX offset behavior, and workload instruction mix can affect interpretation.

`MEMORY_DISAMBIGUATION.HISTORY_RESET` lacks a meaningful public description, so users may have less context from `perf list` than with other aliases. Documentation-only improvements here would be low risk if event encoding remains unchanged.

The interrupt event uses a very small default sample period (`203`), which may have higher sampling overhead if used in record mode on interrupt-heavy workloads.

## Test Signals

Useful checks are:

- `jq empty other.json`.
- Build perf and verify topic `other` includes all 6 aliases.
- `perf stat -e core_power.lvl0_turbo_license,core_power.throttle <workload>` on SkylakeX hardware.
- `perf stat -e hw_interrupts.received sleep 1` to check interrupt alias programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/pipeline.json

## Purpose

`pipeline.json` is the Skylake Server PMU manifest for core pipeline, branch, clock, retirement, execution, dispatch, resource-stall, machine-clear, and uop events. It defines 102 aliases under the `pipeline` topic.

The file gives perf symbolic names for low-level pipeline analysis counters, including top-down support events used to distinguish retiring, bad speculation, front-end/back-end stalls, port utilization, branch behavior, LSD activity, and recovery cycles.

## Important Schema, APIs, and Event Families

The schema is the standard PMU event-array schema. Besides `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, and sampling period, this file uses:

- `CounterMask` for thresholded cycle events and utilization bands.
- `Invert` and `EdgeDetect` for specialized counting semantics.
- `AnyThread` for aliases that count across sibling SMT threads, such as `CPU_CLK_UNHALTED.THREAD_ANY`.
- `PEBS` for precise retired branch and instruction events.
- `Errata`, especially `SKL091` and `SKL044`, on retired branch and instruction aliases.

Important families are:

- `BR_INST_RETIRED.*`, `BR_MISP_EXEC.*`, and `BR_MISP_RETIRED.*` for branch volume and misprediction categories.
- `CPU_CLK_THREAD_UNHALTED.*` and `CPU_CLK_UNHALTED.*` for reference and thread cycles.
- `CYCLE_ACTIVITY.*` for L1D, L2, and memory-related cycles and stalls.
- `EXE_ACTIVITY.*`, `UOPS_DISPATCHED_PORT.PORT_{0..7}`, and `UOPS_EXECUTED.*` for execution port and uop utilization.
- `INST_RETIRED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*` for retirement, issue, and stall-cycle views.
- `INT_MISC.*`, `MACHINE_CLEARS.*`, and `OTHER_ASSISTS.ANY` for recovery, clears, and assists.
- `LD_BLOCKS.*`, `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`, and `LOAD_HIT_PRE.SW_PF` for load/store pipeline hazards.
- `LSD.*`, `RS_EVENTS.*`, `ROB_MISC_EVENTS.*`, and `RESOURCE_STALLS.*` for loop stream detector, reservation station, reorder buffer, and resource pressure signals.

## Control Flow and Integration

`jevents.py` loads the 102 JSON objects into `JsonEvent` instances, derives topic `pipeline`, converts event fields into perf event selector strings, and emits them into the SkylakeX generated C table. The runtime integration is standard perf alias lookup for the CPU model. Aliases with `AnyThread` become event strings containing `any=1`; aliases with `CounterMask` become `cmask=` constraints; PEBS aliases receive precise-event description notes.

This file overlaps analytically with `frontend.json` and `memory.json` but uses a broader pipeline topic. For example, `ILD_STALL.LCP` complements `DECODE.LCP`, `CYCLE_ACTIVITY.*` appears in both pipeline and memory contexts with different miss levels, and machine-clear events are split between generic clears here and memory-ordering clears in `memory.json`.

## State and Persistence Behavior

The file is static source data. Generated alias entries are persisted in perf's compiled PMU tables. Runtime state is PMU counter programming and perf sampling output. Default sample periods are part of the generated alias definitions, with many high-volume events using periods such as `2000003` and precise retired events often using `100003` or related values.

## Dependencies

Dependencies include:

- Skylake Server PMU encodings for core pipeline events.
- `jevents.py` support for `AnyThread`, `CounterMask`, `EdgeDetect`, `Invert`, `PEBS`, and errata description annotations.
- perf event parsing and PMU alias matching.
- Kernel/hardware support for precise retired events and any-thread counting.

## Risks and Edge Cases

Many aliases share event codes and are differentiated only by umask, cmask, invert, or edge settings. Examples include `UOPS_EXECUTED.*` on `0xB1`, `UOPS_DISPATCHED_PORT.*` on `0xA1`, `BR_INST_RETIRED.*` on `0xC4`, `BR_MISP_RETIRED.*` on `0xC5`, and `CYCLE_ACTIVITY.*` on `0xA3`. Small field changes can produce valid but semantically wrong aliases.

Errata annotations are user-visible and meaningful. Removing `SKL091` or `SKL044` from retired instruction/branch events would hide known caveats. Conversely, changing only errata text affects descriptions, not counter programming.

Some aliases have overlapping or compatibility names, such as `BR_INST_RETIRED.COND` and `BR_INST_RETIRED.CONDITIONAL`, or `CPU_CLK_UNHALTED.THREAD` and `CPU_CLK_UNHALTED.THREAD_P`. These should be treated as compatibility surface rather than obvious duplication.

Any-thread aliases can behave differently under SMT and may not be comparable to per-thread aliases in scripts unless the selector semantics are understood.

## Test Signals

Useful checks are:

- `jq empty pipeline.json`.
- Generated perf build and `perf list pipeline` inspection.
- `perf stat -e cycles,instructions,uops_retired.retire_slots,br_misp_retired.all_branches <workload>` on SkylakeX hardware.
- Targeted tests for `any=1`, `cmask=`, `edge=`, and `inv=` generated event strings.
- Existing PMU event table tests in `tools/perf/tests/pmu-events.c`, plus hardware smoke tests for PEBS branch/instruction aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/pipeline.json -->
