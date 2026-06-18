# Research: subset-b-006625

This grouped report covers Arrow Lake PMU event definition files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake`. The reconciliation lane can split each section into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/cache.json

## Purpose

`cache.json` is the Arrow Lake cache and cache-adjacent memory event catalog consumed by perf's PMU event generator. It contains 209 JSON event records for the `cache` topic: 71 `cpu_atom`, 86 `cpu_core`, and 52 `cpu_lowpower` records. At build time, `tools/perf/pmu-events/jevents.py` reads this file, derives the topic name `cache` from the filename, and emits generated C table entries in `pmu-events.c`. At runtime, perf exposes these aliases through `perf list`, `perf stat`, `perf record`, and metric expressions that reference raw event names.

The file is selected for Arrow Lake by `arch/x86/mapfile.csv`, whose Arrow Lake entry maps `GenuineIntel-6-C[56]` version `v1.16` to the `arrowlake` model directory with event type `core`. This means the data becomes active when perf's x86 CPUID matching selects the Arrow Lake table.

## Important APIs, types, and data shape

The file is a top-level JSON array of event objects. The schema surface used by `jevents.py` is data-driven rather than function-based:

- `EventName`: perf alias such as `L2_RQSTS.MISS`, `MEM_LOAD_RETIRED.L3_MISS`, or `OCR.DEMAND_DATA_RD.L3_HIT.SNOOP_HITM`.
- `EventCode` and `UMask`: raw PMU selector fields rendered into perf event encodings.
- `Unit`: PMU scope selector, primarily `cpu_core`, `cpu_atom`, or `cpu_lowpower`; duplicate `EventName` values can intentionally exist with unit-specific encodings.
- `Counter` and optional `CounterMask`: constrain valid programmable counters or cycle-threshold forms.
- `SampleAfterValue`: default sampling period used by perf event aliases.
- `BriefDescription` and optional `PublicDescription`: user-facing descriptions shown by perf list and documentation-style output.
- Optional `MSRIndex` and `MSRValue`: extra model-specific register programming for latency threshold filters and offcore response filters.
- Optional `Data_LA`: marks events that support data linear-address sampling/precise load attribution in perf's generated metadata.

There are no metric definitions in this file; all records are event aliases. There are also no deprecated entries in this file.

## Event coverage

The catalog covers both P-core and E-core/low-power cache behavior. Major groups include:

- `L1D`, `L1D_MISS`, and `L1D_PENDING`: core L0/L1 replacement, fill-buffer pressure, L2 resource stalls, and outstanding load miss occupancy.
- `L2_LINES_IN`, `L2_LINES_OUT`, `L2_REQUEST`, and `L2_RQSTS`: L2 fills, evictions, hit/miss/reject accounting, code reads, demand data reads, and RFOs.
- `LONGEST_LAT_CACHE`: LLC references and misses across core, atom, and low-power PMUs.
- `MEM_LOAD_RETIRED`, `MEM_INST_RETIRED`, `MEM_UOPS_RETIRED`, and `MEM_LOAD_UOPS_RETIRED`: retired load/store/SW-prefetch aliases, split accesses, STLB hit/miss classification, load hit levels, and latency thresholds.
- `MEM_BOUND_STALLS_LOAD` and `MEM_BOUND_STALLS_IFETCH`: Atom and low-power stall classification for L2/LLC/local memory sources.
- `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, and `OCR.*`: offcore request classes, outstanding cycles, and filtered response categories.
- `LLC_PREFETCHES_THROTTLED`, `L2_PREFETCHES_THROTTLED`, and `SW_PREFETCH_ACCESS`: hardware/software prefetch activity and throttling.
- `LOCK_CYCLES.CACHE_LOCK_DURATION` and `SQ_MISC.BUS_LOCK`: locking and bus-lock visibility.

The file contains 154 unique event names, so about a quarter of the rows are unit variants or aliases that share a logical name but differ by PMU type.

## Control flow and integration

The control path is the perf PMU event pipeline:

1. `Makefile.perf` builds `libpmu-events.a` and runs the `pmu-events/Build` rules.
2. `pmu-events/Build` invokes `jevents.py` over `pmu-events/arch`.
3. `jevents.py` ignores `metricgroups.json`, then reads every other `.json` file in a model leaf directory. For this file it calls `read_json_events(item.path, "cache")`.
4. The parser converts each record into generated `struct pmu_table_entry` data, stores strings in the generated big C string table, and associates entries with the PMU unit.
5. Generated mapping code uses `arch/x86/mapfile.csv` to bind Arrow Lake CPUID strings to the generated Arrow Lake event table.
6. Runtime perf code in `util/pmu.c`, `builtin-list.c`, and `metricgroup.c` walks the generated tables to create aliases and resolve user-supplied event names.

Within this JSON file, array order is not a runtime control flow primitive, but it affects generated output ordering and therefore review diffs.

## State and persistence behavior

The file itself is static source data. It has no runtime mutable state and no persistence writes. Persistence happens indirectly when the build emits `pmu-events.c` into the perf output directory and compiles it into perf. Changes to any event record persist in the built binary until perf is rebuilt.

MSR-backed events carry important hidden state implications: aliases with `MSRIndex` `0x3F6` program load-latency threshold controls, while `OCR.*` records use `MSRIndex` `0x1a6,0x1a7` with large response-filter values. Those fields must stay aligned with the architectural event encodings or perf can program the wrong filter even though the JSON parses.

## Dependencies and integration points

Primary dependencies are `jevents.py`, `pmu-events/README`, `pmu-events/Build`, and `arch/x86/mapfile.csv`. Runtime consumers include perf PMU alias enumeration and metric formulas in neighboring Arrow Lake metric files, especially `arl-metrics.json`, which can reference event aliases defined here.

The file also depends on perf's JSON schema conventions: field names are case-sensitive, values are string-encoded even when they represent numbers, and PMU unit names must match Linux PMU names exposed in sysfs. The `cpu_core`, `cpu_atom`, and `cpu_lowpower` split is central on hybrid Arrow Lake systems.

## Risks and edge cases

The highest-risk rows are the offcore and latency-threshold aliases because they require correct `MSRIndex`/`MSRValue` pairing. A typo can silently produce an alias that lists correctly but measures the wrong response class or threshold. Unit-specific duplicates are also risky: changing only the `cpu_core` version of a shared name does not update `cpu_atom` or `cpu_lowpower` semantics. Consumers must specify or resolve the right PMU unit on hybrid systems.

Several records use `Data_LA`, especially retired memory-load aliases and load-latency aliases. Removing or adding this flag changes sampling capabilities and could affect users relying on data address capture. Counter restrictions such as `Counter: "2"` on `L1D_PENDING.*` must be preserved because invalid counter placement can fail at event scheduling time.

Descriptions are user-visible and often copied into generated C strings. Malformed JSON, missing commas, duplicate-but-inconsistent aliases, or non-string numeric fields can break `jevents.py` generation or produce confusing perf output.

## Test signals

Useful validation signals are:

- `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/cache.json` for syntax.
- Running the perf PMU event generation path, for example the `pmu-events/Build` target or a normal `tools/perf` build for x86 with jevents enabled.
- `perf list cache` or `perf list --details` on an Arrow Lake-capable build to confirm aliases, descriptions, PMU units, and MSR extra config fields are emitted.
- `tools/perf/tests/pmu-events.c` and `tools/perf/tests/shell/stat_all_metricgroups.sh` as broad regression signals for generated event and metric tables.
- Targeted `perf stat -e` checks for representative aliases: `L2_RQSTS.MISS`, `MEM_LOAD_RETIRED.L3_MISS`, `MEM_UOPS_RETIRED.LOAD_LATENCY_GT_128`, and `OCR.DEMAND_DATA_RD.ANY_RESPONSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/floating-point.json

## Purpose

`floating-point.json` defines Arrow Lake floating-point, vector-integer, floating-point assist, and divide-unit PMU aliases for perf. It contains 64 event records: 22 for `cpu_atom`, 29 for `cpu_core`, and 13 for `cpu_lowpower`. The file's topic is derived as `floating point` by `jevents.py`, so generated perf output groups these aliases under the floating-point topic.

This file lets users use symbolic aliases such as `FP_ARITH_OPS_RETIRED.256B_PACKED_SINGLE`, `ARITH.FPDIV_ACTIVE`, and `FP_FLOPS_RETIRED.FP64` instead of manually specifying raw event code and umask combinations.

## Important APIs, types, and data shape

The top-level structure is a JSON array of PMU event records. Relevant fields are:

- `EventName`, `EventCode`, `UMask`, `Counter`, and optional `CounterMask`.
- `Unit`, which separates P-core (`cpu_core`), E-core (`cpu_atom`), and low-power E-core (`cpu_lowpower`) definitions.
- `SampleAfterValue`, commonly `1000003`, `100003`, or `2000003`.
- `BriefDescription` and optional `PublicDescription`.
- `Deprecated`, present on compatibility aliases that should remain listable but direct users toward newer names.

The file does not use `MSRIndex`, `MSRValue`, `EdgeDetect`, `Invert`, or `Data_LA`. Its complexity is mostly in naming compatibility and unit-specific event families.

## Event coverage

The P-core section focuses on arithmetic retirement and dispatch:

- `ARITH.FPDIV_ACTIVE` tracks busy cycles for FP divide/square-root execution.
- `ASSISTS.FP` and `ASSISTS.SSE_AVX_MIX` expose microcode floating-point assist behavior.
- `FP_ARITH_DISPATCHED.V0` through `.V3` count FP arithmetic uops dispatched on vector ports.
- `FP_ARITH_OPS_RETIRED.*` provides scalar/vector and width-specific FP operation retirement aliases.
- `FP_ARITH_INST_RETIRED.*` provides deprecated compatibility names that point to `FP_ARITH_OPS_RETIRED.*`.

The Atom and low-power sections use different event families:

- `FP_INST_RETIRED.*` covers 32-bit/64-bit scalar and 128-bit/256-bit packed single/double variants.
- `FP_FLOPS_RETIRED.*` covers aggregate, FP32, and FP64 FLOP counters, with low-power compatibility aliases `SP` and `DP`.
- `FP_VINT_UOPS_EXECUTED.*` appears on `cpu_atom` for vector integer uop execution by port or category.
- `MACHINE_CLEARS.FP_ASSIST` and `UOPS_RETIRED.FPDIV` expose assist clears and retired FP divide uops on Atom/low-power units.

There are 52 unique event names. Several logical aliases repeat across `cpu_atom`, `cpu_core`, and `cpu_lowpower`, but their event codes differ.

## Control flow and integration

During build, `jevents.py` reads this file as a regular event JSON, derives topic `floating point`, parses each object via `read_json_events`, and emits generated C table entries. Those entries become part of the Arrow Lake event table selected by the `GenuineIntel-6-C[56]` mapfile row.

At runtime, perf's PMU alias lookup exposes these names for event selection. Metric formulas in Arrow Lake metric files can depend on the aliases. Top-down metric groups such as `Flops`, `Compute`, `tma_fp_arith_group`, and `tma_divider_group` are conceptually related, but the actual group descriptions live in `metricgroups.json` and metric expressions live in metric JSON files.

## State and persistence behavior

The file is immutable source data at runtime. Its contents persist only through generated `pmu-events.c` and the compiled perf binary. It carries no MSR side effects and no address-sampling flags. The `Deprecated` field is persistent metadata used by generated tables and perf output; removing a deprecated alias is a user-facing compatibility change even when a replacement alias exists.

## Dependencies and integration points

The file depends on perf's PMU event JSON schema and on Arrow Lake unit names matching runtime PMU names. The strongest integration points are:

- `pmu-events/jevents.py`, which requires valid array-of-object event JSON for files other than `metricgroups.json`.
- `pmu-events/arch/x86/mapfile.csv`, which selects this directory for Arrow Lake CPUIDs.
- `builtin-list.c` and PMU alias display paths, where `Deprecated` and descriptions become visible.
- Metric definitions in `arl-metrics.json` or generated extra metrics that may refer to these FP aliases.

## Risks and edge cases

The main risk is compatibility drift between deprecated and replacement names. There are 11 deprecated entries: nine `FP_ARITH_INST_RETIRED.*` P-core aliases that point to `FP_ARITH_OPS_RETIRED.*`, plus low-power `FP_FLOPS_RETIRED.DP` and `.SP` aliases that map conceptually to `.FP64` and `.FP32`. Removing them can break scripts, while changing only the deprecated or only the replacement form can make counters inconsistent.

Unit-specific semantics are another risk. `ARITH.FPDIV_ACTIVE` exists across all units but uses different event codes and umasks. P-core `FP_ARITH_OPS_RETIRED.*` and Atom `FP_INST_RETIRED.*` are not interchangeable even though both describe FP work. Any metric expression that assumes one family exists on all PMUs can fail or undercount on hybrid systems.

Counter masks for active-cycle events must stay intact because they encode cycle-occupancy semantics rather than simple occurrence counts. Sampling periods should be reviewed when adding high-frequency FLOP aliases because too-low periods can create large sampling overhead.

## Test signals

Validation should include JSON syntax checks, perf event generation, and generated alias inspection. Useful runtime probes on supported hardware include `perf list floating` and `perf stat -e cpu_core/FP_ARITH_OPS_RETIRED.SCALAR_DOUBLE/` or equivalent PMU-qualified aliases. Regression checks should include deprecated names to ensure they still parse and list as deprecated, and replacement names to ensure users have a working migration target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/frontend.json

## Purpose

`frontend.json` defines Arrow Lake front-end PMU event aliases for branch resteers, decode restrictions, instruction cache stalls, microcode-sequencer delivery, decoded-stream-buffer versus MITE delivery, and retired instructions tagged with front-end causes. It contains 82 event records: 26 `cpu_atom`, 43 `cpu_core`, and 13 `cpu_lowpower`.

Perf consumes this file to let users diagnose front-end-bound behavior through symbolic event names such as `FRONTEND_RETIRED.L1I_MISS`, `IDQ.MITE_UOPS`, `BACLEARS.ANY`, and `ICACHE.MISSES`.

## Important APIs, types, and data shape

The file is a JSON array of PMU event records. Important fields include:

- `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and optional `CounterMask`.
- `Unit` for PMU selection across Arrow Lake core types.
- `BriefDescription` and optional `PublicDescription`.
- `MSRIndex` and `MSRValue` on many `FRONTEND_RETIRED.*` P-core aliases, especially latency and source-classification filters.
- `EdgeDetect` on `ICACHE_DATA.STALL_PERIODS` and `IDQ.MS_SWITCHES`.
- `Invert` on `IDQ_BUBBLES.CYCLES_FE_WAS_OK`.
- `Deprecated` on `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE`.

There are 67 unique event names. The dominant prefix is `FRONTEND_RETIRED`, with 38 records.

## Event coverage

Atom and low-power front-end records include:

- `BACLEARS.*` for BTB correction/resteer categories such as conditional, indirect, return, and unconditional branches.
- `DECODE_RESTRICTION.PREDECODE_WRONG` on Atom.
- `FRONTEND_RETIRED.*` for retired instructions associated with branch detect, branch resteer, CISC, decode, icache, ITLB miss, predecode, and other front-end causes.
- `FRONTEND_RETIRED_SOURCE.*` on Atom for icache L2/L3 and ITLB STLB source buckets.
- `ICACHE.ACCESSES`, `.HIT`, `.MISSES`, and `MS_DECODED.*`.

P-core records include:

- `BACLEARS.ANY` for unknown branches.
- `DECODE.LCP` and `DECODE.MS_BUSY`.
- `DSB2MITE_SWITCHES.PENALTY_CYCLES`.
- `FRONTEND_RETIRED.*` source and latency-threshold aliases using `MSRIndex` `0x3F7`.
- `ICACHE_DATA.*` and `ICACHE_TAG.*` stall events.
- `IDQ.*` delivery counters for DSB, MITE, and MS sources.
- `IDQ_BUBBLES.*` starvation, fetch-latency, and zero-delivery cycle aliases.

## Control flow and integration

The build flow is the standard PMU event path. `jevents.py` derives topic `frontend`, parses all event objects, interns strings, and emits generated table entries. The generated table is selected for Arrow Lake through `arch/x86/mapfile.csv`.

Runtime consumers include:

- `perf list frontend` or raw event listing paths.
- `perf stat -e` aliases for branch and instruction-delivery analysis.
- Top-down and front-end metric formulas that combine aliases such as `IDQ_UOPS_NOT_DELIVERED`, `FRONTEND_RETIRED.*`, or related generated metrics.
- `describe_metricgroup()` output for related metric groups, although group descriptions are sourced from `metricgroups.json`.

The `MSRIndex` `0x3F7` records are effectively a mini-API for front-end retirement filtering. `jevents.py` preserves those fields into generated event encodings so perf can program the extra register values when users select the alias.

## State and persistence behavior

The JSON is static source data. Build output persists the records in generated C. Runtime state only appears when perf programs PMU counters and extra registers. P-core front-end retired events with `MSRIndex` `0x3F7` are stateful from a hardware-programming perspective because each alias selects a distinct filter value, such as latency thresholds from `LATENCY_GE_2` through `LATENCY_GE_512` or source categories like `L1I_MISS`, `ITLB_MISS`, and `UNKNOWN_BRANCH`.

The deprecated `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE` alias preserves compatibility as an alias to `IDQ_BUBBLES.STARVATION_CYCLES`.

## Dependencies and integration points

Key dependencies are `jevents.py`, `pmu-events/README`, `arch/x86/mapfile.csv`, and the runtime PMU alias code in `util/pmu.c`. Hybrid PMU naming must match sysfs names for `cpu_core`, `cpu_atom`, and `cpu_lowpower`.

This file integrates strongly with top-down analysis. Front-end metric groups in `metricgroups.json` include `Frontend`, `Fed`, `FetchBW`, `FetchLat`, `IcMiss`, `Ifetch`, `DSB`, `DSBmiss`, `MicroSeq`, `tma_frontend_bound_group`, `tma_fetch_bandwidth_group`, `tma_fetch_latency_group`, `tma_icache_misses_group`, `tma_itlb_misses_group`, `tma_mite_group`, and `tma_microcode_sequencer_group`.

## Risks and edge cases

The highest-risk entries are `FRONTEND_RETIRED.*` P-core filters because many aliases share `EventCode` `0xc6` and depend on distinct `MSRValue` settings. A single wrong filter value can make a named alias measure another front-end condition. Latency threshold names must remain monotonically aligned with their threshold values.

`EdgeDetect` and `Invert` fields materially alter event semantics. For example, `ICACHE_DATA.STALL_PERIODS` counts stall periods rather than cycles, and `IDQ_BUBBLES.CYCLES_FE_WAS_OK` inverts the condition. These fields are easy to lose in bulk edits because most rows do not use them.

Hybrid-unit asymmetry is significant. Many P-core `IDQ` and `FRONTEND_RETIRED` aliases do not exist on Atom/low-power PMUs, while Atom exposes `FRONTEND_RETIRED_SOURCE.*` aliases not present on P-cores. Scripts should use PMU-qualified names or check availability.

## Test signals

Test with `jq empty`, a perf build with jevents enabled, and generated alias listing. Good representative aliases are `BACLEARS.ANY` across units, `FRONTEND_RETIRED.LATENCY_GE_64`, `IDQ.MS_SWITCHES`, `ICACHE_DATA.STALL_PERIODS`, and the deprecated `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE`. Runtime validation should confirm extra MSR filters appear in `perf list --details` and that PMU-qualified aliases resolve on hybrid hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/memory.json

## Purpose

`memory.json` defines Arrow Lake memory-ordering, load-head, offcore miss, page-split, and load-latency PMU aliases for perf. It contains 45 event records: 18 `cpu_atom`, 18 `cpu_core`, and 9 `cpu_lowpower`.

The file complements `cache.json`: `cache.json` covers broad cache hierarchy activity and many retired memory events, while `memory.json` emphasizes load-blocking causes, machine clears, long-latency memory transactions, page splits, and L3-miss/DRAM offcore filters.

## Important APIs, types, and data shape

The top-level JSON value is an array of event objects. Used fields include:

- `EventName`, `EventCode`, `UMask`, `Counter`, and `SampleAfterValue`.
- Optional `CounterMask`, especially for outstanding request cycle forms.
- `Unit`.
- `BriefDescription` and optional `PublicDescription`.
- `MSRIndex` and `MSRValue` for `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` and `OCR.*` filters.
- `Data_LA` for P-core `MEM_TRANS_RETIRED.*` latency threshold and store sampling aliases.

The file has 35 unique event names and no deprecated entries.

## Event coverage

Atom records are dominated by `LD_HEAD.*`:

- `LD_HEAD.ANY`, `.L1_MISS`, `.PGWALK`, `.ST_ADDR`, `.ST_DATA`, `.WCB_FULL`, `.L1_BOUND_AT_RET`, `.OTHER`, and `_AT_RET` variants.
- `MACHINE_CLEARS.MEMORY_ORDERING` and `.MEMORY_ORDERING_FAST`.
- `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT` and `.STORE_PAGE_SPLIT`.

P-core records include:

- `MACHINE_CLEARS.MEMORY_ORDERING`.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4` through `GT_2048` plus `MEM_TRANS_RETIRED.STORE_SAMPLE`, all with `Data_LA`.
- `OCR.DEMAND_DATA_RD.DRAM`, `OCR.DEMAND_DATA_RD.L3_MISS`, and `OCR.DEMAND_RFO.L3_MISS`.
- `OFFCORE_REQUESTS.L3_MISS_DEMAND_DATA_RD` and corresponding outstanding count/cycle aliases.

Low-power records provide retired load-head subsets, memory-ordering clears, and page-split aliases.

## Control flow and integration

At build time, `jevents.py` derives topic `memory` and emits these records into the generated Arrow Lake PMU events table. At runtime, PMU alias lookup exposes them for event selection and metric expressions. The file's Arrow Lake activation depends on the `GenuineIntel-6-C[56]` mapfile row.

The control flow for MSR-backed aliases is important: perf resolves the alias, sees the extra config fields generated from `MSRIndex`/`MSRValue`, and programs the associated filter register in addition to the event select and umask fields.

## State and persistence behavior

This is static source data with no direct persistence beyond generated build artifacts. Runtime hardware state appears when perf programs offcore response MSRs (`0x1a6,0x1a7`) or load-latency threshold MSR `0x3F6`. `Data_LA` indicates that sampling for certain P-core memory transaction aliases can carry data linear-address information, which is a meaningful behavior contract for profiling tools.

## Dependencies and integration points

Dependencies include perf's PMU event JSON parser, x86 mapfile matching, and runtime PMU alias support. Neighboring `cache.json` and `virtual-memory.json` likely provide related aliases used by memory-bound top-down metrics. Metric group labels in `metricgroups.json` relevant to this file include `Mem`, `MemoryBound`, `MemoryLat`, `Memory_BW`, `Memory_Lat`, `Load_Store_Miss`, `MachineClears`, `tma_memory_bound_group`, `tma_mem_latency_group`, `tma_dram_bound_group`, and `tma_machine_clears_group`.

## Risks and edge cases

Latency threshold aliases are the primary risk. Names such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128` must correspond exactly to the expected `MSRValue` threshold. The sequence extends to `GT_2048`, so missing one threshold may only be noticed by users doing latency distribution analysis.

Offcore response aliases share event families with `cache.json`, so duplicate-looking `OCR.*` names across files must be checked by exact event name and unit before editing. Atom `LD_HEAD` events use a different conceptual model from P-core `MEM_TRANS_RETIRED`; metrics that mix them must account for PMU type.

`Data_LA` is present on all P-core `MEM_TRANS_RETIRED.*` records in this file. Losing it would reduce profiling utility for load latency and store sampling even though counting still works.

## Test signals

Use JSON validation and perf's jevents generation as baseline tests. Runtime or generated-table checks should include `LD_HEAD.PGWALK_AT_RET`, `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_512`, `MEM_TRANS_RETIRED.STORE_SAMPLE`, and `OCR.DEMAND_DATA_RD.DRAM`. For MSR-backed aliases, inspect `perf list --details` output to ensure extra register values are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/metricgroups.json

## Purpose

`metricgroups.json` defines human-readable descriptions for Arrow Lake metric group names. Unlike the neighboring event files, it is not an array of event records. It is a JSON object with 148 key/value pairs where each key is a metric group name and each value is a short description.

Perf uses this data to describe groups listed by `perf list metricgroups` and selected by `perf stat -M <group>`. It does not define metric formulas; metric expressions live in files such as `arl-metrics.json` and generated `extra-metrics.json` files.

## Important APIs, types, and data shape

The schema is:

```json
{
  "GroupName": "Description"
}
```

`jevents.py` has special handling for filenames ending in `metricgroups.json`: it loads the object, iterates each group name, interns both the group and description into the generated big C string table, and stores them in `_metricgroups`. Later `print_metricgroups()` writes a sorted C lookup table and a generated `describe_metricgroup(const char *group)` function that performs binary search over the sorted group names.

Group names include legacy/top-level labels such as `Backend`, `Frontend`, `Mem`, `Flops`, `HPC`, `Summary`, and `TopdownL1` through `TopdownL6`, plus many `tma_*_group` labels such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`. There are also issue-oriented names such as `tma_issueBW`, `tma_issueLat`, and `tma_issueTLB`.

## Control flow and integration

The control flow differs from regular event JSON files:

1. During preprocessing, `jevents.py` detects `item.name.endswith('metricgroups.json')`.
2. It calls `json.load` and expects an object whose keys are group names.
3. For each key, it asserts the group name length is greater than one, appends C-string terminators, and stores group/description strings as metric strings.
4. It returns early, so the file is not passed through `read_json_events`.
5. At code-generation time, `print_metricgroups()` sorts the collected group names and emits the `metricgroups` offset table plus `describe_metricgroup()`.
6. Runtime perf list/stat paths use that generated function to show descriptions for metric groups.

Because generated lookup uses binary search over sorted group names, exact spelling and case are the public API.

## State and persistence behavior

The file has no runtime state. Its contents persist through generated `pmu-events.c` and the compiled perf binary. Group descriptions are static string data in the generated big C string table. Adding, renaming, or removing a key changes which metric groups can be described, but it does not by itself create or remove the underlying metrics.

## Dependencies and integration points

The file depends directly on `jevents.py` special-case parsing. It also depends on metric names and metric groups emitted by Arrow Lake metric definitions. The descriptions are useful only when group names match `MetricGroup` fields used by metrics. Build rules can also generate `extra-metricgroups.json` from `intel_metrics.py`, and `jevents.py` treats all metricgroups files similarly.

Runtime integration points include `builtin-list.c` for metric group listing and `util/metricgroup.c` for metric group expansion and top-down maximum-level handling. User-facing commands include `perf list metricgroups`, `perf list --details`, and `perf stat -M`.

## Risks and edge cases

The major risk is schema confusion. This file must remain a JSON object, not an event array. Treating it like the other Arrow Lake JSON files breaks parsing because string descriptions do not have event keys. Conversely, moving metric formulas into this file would be ignored by the metricgroup parser.

Descriptions are mostly generic, many reading "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet." That is valid but low-information. If group names are renamed without updating metric definitions, `describe_metricgroup()` may return descriptions for groups that no metrics use, or metrics may reference groups with no description.

Case and punctuation are significant. Both `TopdownL1` and `tma_L1_group` style names exist, as do similarly named `MachineClears` and `Machine_Clears`. Automated normalization could collapse distinct public group names and break user scripts.

## Test signals

Validation starts with `jq type`, which should return `"object"`, and `jq 'keys | length'`, which should return 148 for the current file. A perf build with jevents enabled should generate `describe_metricgroup()`. Runtime checks should include `perf list --raw-dump metricgroups`, `perf list metricgroups`, and representative group descriptions for `TopdownL1`, `Frontend`, `Mem`, `tma_memory_bound_group`, and `tma_ports_utilization_group`. `tools/perf/tests/shell/stat_all_metricgroups.sh` is a useful broad integration test because it iterates metric groups exposed by perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/other.json

## Purpose

`other.json` defines Arrow Lake PMU aliases that do not fit cleanly into cache, memory, front-end, pipeline, virtual-memory, or floating-point topic files. It contains 21 event records: 16 `cpu_atom`, 4 `cpu_core`, and 1 `cpu_lowpower`.

The file covers bus locks, dynamic prefetch throttler state, streaming write offcore responses, queue promotion/fullness, hardware/page-fault assists, and a low-power last-branch-record compatibility alias.

## Important APIs, types, and data shape

The file is a standard event JSON array. Fields used are:

- `EventName`, `EventCode`, `UMask`, `Counter`, and `SampleAfterValue`.
- Optional `CounterMask`, particularly for cycle-style bus-lock aliases.
- `Unit`.
- Optional `MSRIndex` and `MSRValue` for `OCR.*` streaming write aliases.
- `Deprecated` on `LBR_INSERTS.ANY`.
- `BriefDescription` and optional `PublicDescription`.

There are 20 unique event names; only `OCR.STREAMING_WR.ANY_RESPONSE` appears for both `cpu_atom` and `cpu_core`.

## Event coverage

Atom aliases include:

- `BUS_LOCK.BLOCKED_CYCLES`, `.LOCK_CYCLES`, `.NON_SPLIT_LOCKS`, and `.SPLIT_LOCKS`.
- `DYNAMIC_PREFETCH_THROTTLER.LEVEL0_SOC` through `.LEVEL4_SOC`.
- `OCR.FULL_STREAMING_WR.ANY_RESPONSE`, `OCR.PARTIAL_STREAMING_WR.ANY_RESPONSE`, and `OCR.STREAMING_WR.ANY_RESPONSE`.
- `XQ_PROMOTION.ALL`, `.CRDS`, `.DRDS`, and `.RFOS`.

P-core aliases include `ASSISTS.HARDWARE`, `ASSISTS.PAGE_FAULT`, `OCR.STREAMING_WR.ANY_RESPONSE`, and `XQ.FULL`. The only low-power alias is deprecated `LBR_INSERTS.ANY`, described as an alias to `MISC_RETIRED.LBR_INSERTS`.

## Control flow and integration

`jevents.py` derives topic `other` from the filename and processes the file through the standard event parser. Generated entries become part of the Arrow Lake PMU event table selected by `mapfile.csv`. Runtime perf consumers see these names as normal event aliases.

The offcore streaming write aliases use the same extra-register path as `OCR.*` events in `cache.json` and `memory.json`. They depend on `MSRIndex` `0x1a6,0x1a7` and distinct `MSRValue` filters to classify full, partial, or general streaming writes.

## State and persistence behavior

The JSON is static source data. Runtime state appears only through PMU programming. `OCR.*` aliases program offcore response filter MSRs. Bus-lock and dynamic prefetch throttler aliases are read-only hardware counters from perf's perspective, but their values reflect global or SoC-level behavior that may be affected by other workloads on the system.

Deprecated metadata for `LBR_INSERTS.ANY` persists into generated tables and keeps old scripts working while pointing users toward `MISC_RETIRED.LBR_INSERTS`.

## Dependencies and integration points

The file depends on the same perf PMU event generation path as other event JSON files. It integrates with lock-contention, prefetch, assist, and offcore analysis workflows. Relevant metric group descriptions in `metricgroups.json` include `LockCont`, `Prefetches`, `Offcore`, `MachineClears`, `OS`, and possibly `Power` or `SoC` for dynamic prefetch throttler events.

Because this is a catch-all topic, it may overlap conceptually with several neighboring files. New events should be placed here only when no more specific topic matches, to preserve `perf list` usability.

## Risks and edge cases

The catch-all nature of the file is the biggest maintainability risk. It can accumulate unrelated aliases, making topic filtering less predictable. Offcore streaming write aliases are MSR-sensitive and must remain aligned with the correct response-filter values. Bus-lock events can be high-impact on production systems because they often indicate severe synchronization or split-lock behavior; descriptions should stay precise.

The deprecated low-power `LBR_INSERTS.ANY` alias is a compatibility surface. Removing it can break scripts even though a replacement name exists elsewhere. The dynamic prefetch throttler levels use a sequence of related names; adding or renumbering levels should be checked against hardware documentation so level semantics do not drift.

## Test signals

Baseline tests are JSON syntax validation and perf PMU event generation. Representative alias checks include `BUS_LOCK.SPLIT_LOCKS`, `DYNAMIC_PREFETCH_THROTTLER.LEVEL4_SOC`, `OCR.STREAMING_WR.ANY_RESPONSE`, `XQ_PROMOTION.ALL`, `ASSISTS.PAGE_FAULT`, and deprecated `LBR_INSERTS.ANY`. For `OCR.*` aliases, `perf list --details` should show the extra MSR filter data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/other.json -->
