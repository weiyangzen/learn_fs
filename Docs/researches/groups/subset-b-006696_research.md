# Research: subset-b-006696

Grouped research for Intel Knights Landing perf PMU event-map files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/cache.json

## Purpose

`cache.json` is a Knights Landing x86 perf PMU event definition file for cache, L2, memory-uop, and offcore-response cache-hit analysis. It is data consumed by the Linux `perf` PMU event-table tooling, not executable code. Its records let users name KNL events such as `MEM_UOPS_RETIRED.L2_MISS_LOADS` or `OFFCORE_RESPONSE.ANY_READ.L2_HIT_FAR_TILE` instead of hand-programming event codes, umasks, and offcore response MSRs.

The file contains 213 event records. Most of the file is a generated-looking matrix of `OFFCORE_RESPONSE` aliases: 200 entries combine request classes with response classes for KNL tile-local, near-tile, far-tile, miss, outstanding, and any-response cases. The remaining records cover core/L2 queue rejection, icache fill stalls, L2 prefetch allocation, L2 request reference/miss counts, L2 request rejection, and retired memory uops by load/store and L1/L2/TLB/HITM categories.

## Important APIs, Types, and Schema

The effective API is the perf JSON event schema. Important fields are:

- `EventName`: canonical perf event alias, grouped by dotted family names such as `OFFCORE_RESPONSE`, `MEM_UOPS_RETIRED`, and `L2_REQUESTS`.
- `EventCode`: programmable raw event selector, commonly `0xB7` for offcore response and `0xD0` for retired memory uops.
- `UMask`: unit mask when the event needs one; many offcore rows share `0x1`.
- `Counter`: KNL programmable counter constraint. Every entry in this file uses `0,1`.
- `MSRIndex` and `MSRValue`: extra selector state for offcore-response events. Values target `0x1a6`, `0x1a7`, or both, with some partial-write and outstanding forms constrained to one MSR/counter path.
- `PEBS` and `Data_LA`: present on selected precise retired-memory-uop events, marking precise-event and data linear-address capability.
- `SampleAfterValue`, `BriefDescription`, and occasional `PublicDescription`: sampling defaults and user-facing metadata.

There are no functions or classes in this source. Downstream parsers treat the top-level JSON array as an ordered list of event descriptors.

## Control Flow and Data Flow

At build or install time, perf's PMU event tooling parses this JSON with the other KNL files, validates required fields, and converts records into event tables. At runtime, a perf command that names one of these aliases looks up the `EventName`, configures the core PMU with `EventCode`/`UMask`, applies `Counter` constraints, and writes `MSRIndex`/`MSRValue` for offcore-response filters when present.

The offcore rows encode a two-axis flow: request type first, response type second. Request classes include any code/data/read/request/RFO, bus locks, demand code/data/RFO, full or partial streaming stores, partial reads/writes, L1/L2 hardware prefetches, software prefetches, and UC code reads. Response classes include any response, tile-local cache states (`E`, `F`, `M`, `S`), near/far tile hits, L2 miss, and outstanding weighted-cycle forms.

## State and Persistence Behavior

This file is static source data. It persists PMU programming constants in the repository and has no runtime mutable state. Runtime state is external: perf may program core counters and offcore MSRs based on these records, but the JSON itself is not modified.

The ordering of the array is part of the practical maintenance surface because generated C tables and diagnostics often preserve input order. Consumers should not depend on unique prefixes alone; full `EventName` values are the stable keys.

## Dependencies and Integration Points

The file integrates with:

- Linux perf's `pmu-events` parser/generator under `tools/perf/pmu-events`.
- KNL architecture selection logic that loads `arch/x86/knightslanding` event tables for matching CPU IDs.
- The sibling `counter.json`, which declares that the KNL core PMU has two generic counters plus fixed counters; the `Counter: "0,1"` constraints in this file rely on that model.
- Offcore response MSRs `0x1a6` and `0x1a7`, which must be programmed consistently with the selected event and available counter.

## Risks and Edge Cases

The main correctness risk is selector drift: an incorrect `MSRValue` can produce a valid perf event that measures the wrong request/response combination. The offcore matrix is repetitive, so copy/paste mistakes are plausible and hard to spot by syntax alone.

Several rows have hardware-specific counter/MSR restrictions. For example, outstanding-response and partial-write style events may only be valid through a particular offcore MSR or counter path even though the visible `Counter` field still says `0,1`. Tooling that ignores `MSRIndex` or mishandles comma-separated MSR indices will silently misprogram these aliases.

Descriptions mention speculative-path inclusion and weighted-cycle semantics for some events. Users can misinterpret these as exact retired-request counts when they are not. PEBS/data-address metadata must also stay paired with only the precise events that support it.

## Test Signals

Useful validation signals are: `jq empty cache.json` succeeds; every record has an `EventName`, `EventCode` or fixed/raw equivalent, and `BriefDescription`; `EventName` values are unique; all offcore records with request/response filters carry the expected `MSRIndex` and `MSRValue`; `perf list` on a KNL-capable table shows these aliases; and raw `perf stat -e` smoke tests can open representative events from L2, memory-uop, and offcore families without parser errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/counter.json

## Purpose

`counter.json` declares the counter capacity for Knights Landing PMU units. Unlike the other files in this directory, it is not an event list. It tells perf's event-table tooling how many fixed and generic counters exist for each KNL monitoring unit so event constraints and uncore unit descriptions can be interpreted correctly.

The file contains seven unit records: `core`, `CHA`, `EDC_ECLK`, `EDC_UCLK`, `iMC_DCLK`, `iMC_UCLK`, and `M2PCIe`.

## Important APIs, Types, and Schema

The schema is a top-level JSON array of PMU unit descriptors. Each descriptor has:

- `Unit`: the PMU unit name used by perf event-map tooling and KNL uncore integration.
- `CountersNumFixed`: number of fixed counters for that unit.
- `CountersNumGeneric`: number of programmable generic counters for that unit.

The `core` row declares `CountersNumFixed: "3"` and `CountersNumGeneric: "2"`, matching the two generic core counters referenced by the sibling event files through `Counter: "0,1"` and the fixed-counter events in `pipeline.json`. The uncore rows declare zero fixed counters and four generic counters for CHA, EDC, iMC, and M2PCIe units.

## Control Flow and Data Flow

Perf's PMU event generation reads this file alongside event JSON files. The generator associates event descriptors with the counter capacity of their unit. During runtime scheduling, perf uses the generated constraints to decide whether a requested set of events can fit on the available fixed and programmable counters.

There is no executable control flow inside the file. The data-flow dependency is from these unit capacity rows into event validation, event scheduling, and user diagnostics when perf reports unavailable or conflicting events.

## State and Persistence Behavior

This is static hardware metadata. It persists KNL PMU topology in source form and has no mutable runtime state. The only notable persistence issue is type consistency: most numeric values are encoded as strings, while `iMC_UCLK.CountersNumGeneric` is encoded as the JSON number `4`. Consumers need to tolerate both forms or the file should be normalized to one representation.

## Dependencies and Integration Points

`counter.json` is integrated with all KNL event files in this directory. Core events in `cache.json`, `floating-point.json`, `frontend.json`, `memory.json`, and `pipeline.json` constrain themselves to programmable counters `0,1` or fixed counters. Uncore event files outside this work item may rely on the CHA, EDC, iMC, and M2PCIe unit capacities.

The unit names must match names expected by perf's PMU event-map generator and runtime PMU discovery. Renaming a unit is therefore a compatibility change, not a documentation-only edit.

## Risks and Edge Cases

The mixed string/number representation for `CountersNumGeneric` is a concrete schema risk. Strict parsers expecting all counter counts as strings may reject the `iMC_UCLK` row, while strict numeric parsers may reject the other rows. Existing perf tooling is generally permissive, but research and validation scripts should account for this irregularity.

Wrong counter counts cause higher-level failures that are not obvious from this file alone: valid events may be rejected as unschedulable, or invalid event groups may be accepted and later fail at open time. Since this file carries no descriptions, incorrect unit names or counts can be hard to diagnose from user-facing `perf list` output.

## Test Signals

Validation should include JSON parsing, schema checks for exactly `Unit`, `CountersNumFixed`, and `CountersNumGeneric`, and a normalization check that all counter counts can be parsed as non-negative integers. Integration tests should confirm generated KNL tables expose two generic core counters, three fixed core counters, and four generic counters for each declared uncore unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/floating-point.json

## Purpose

`floating-point.json` defines Knights Landing perf aliases for floating-point and SIMD-related core events. It contains three records: FP assist machine clears and two retired SIMD micro-op classifications.

These aliases help users measure expensive floating-point assists and the mix of packed versus scalar SIMD work across SSE, AVX, AVX2, and AVX-512 instructions on KNL.

## Important APIs, Types, and Schema

The file follows the perf event JSON schema:

- `MACHINE_CLEARS.FP_ASSIST` uses `EventCode: "0xC3"` and `UMask: "0x4"` to count floating operations retired that required microcode assists.
- `UOPS_RETIRED.PACKED_SIMD` uses `EventCode: "0xC2"` and `UMask: "0x40"` to count packed SIMD uops, excluding loads and packed byte/word multiplies.
- `UOPS_RETIRED.SCALAR_SIMD` uses `EventCode: "0xC2"` and `UMask: "0x20"` to count scalar SIMD uops, excluding loads, division, and sqrt.

All three records constrain measurement to core programmable counters `0,1` and include `SampleAfterValue` defaults. The two SIMD rows include `PublicDescription` text clarifying that the events are micro-op-level counts rather than instruction-level counts.

## Control Flow and Data Flow

When a user requests one of these event names, perf maps the alias to its raw event code and umask, then schedules it on one of the two generic core counters. No extra MSR programming is required.

The analytical data flow is straightforward: raw retired uop and machine-clear counts feed performance ratios or investigations. Packed and scalar SIMD events can be combined with instruction-retired, cycles, or memory events from sibling files to estimate vectorization quality and FP-assist overhead.

## State and Persistence Behavior

The file is static event metadata. It has no persistent runtime state beyond the event constants stored in the repository. The descriptions persist important interpretation rules: SIMD vector width is not reflected in the count, masks do not reduce the count, and most but not all instructions map to a single uop.

## Dependencies and Integration Points

This file depends on the perf PMU event-table parser and KNL core PMU selection. It integrates with `counter.json` through the two generic core counters and with `pipeline.json` through shared event families (`MACHINE_CLEARS` and `UOPS_RETIRED`). Users commonly combine these events with fixed counters from `pipeline.json`, such as retired instructions and unhalted cycles.

## Risks and Edge Cases

The SIMD events are easy to overinterpret. They count micro-ops, not instructions, elements, or FLOPs. A 128-bit, 256-bit, and 512-bit packed operation each increments the counter the same way, and masked-off lanes still count. That makes these events unsuitable as direct FLOP counters without architecture-specific scaling and instruction mix knowledge.

`MACHINE_CLEARS.FP_ASSIST` measures pipeline disruption due to assists, not a taxonomy of which operation caused the assist. Workloads with denormals, exceptions, or unsupported fast paths may need additional context to explain the count.

## Test Signals

Checks should ensure the file parses as a three-element JSON array, all `EventName` values are unique, all records have `EventCode`, `UMask`, `Counter`, and descriptions, and `perf list` exposes the three aliases under the KNL event map. Runtime smoke tests can attempt `perf stat -e MACHINE_CLEARS.FP_ASSIST,UOPS_RETIRED.PACKED_SIMD,UOPS_RETIRED.SCALAR_SIMD` on KNL-compatible systems or generated-table tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/frontend.json

## Purpose

`frontend.json` defines Knights Landing perf aliases for front-end branch resteers, instruction-cache activity, and micro-sequencer decode entry. It contains seven core event records focused on instruction fetch and front-end redirection behavior.

The file supports analysis of instruction-cache hit/miss behavior, branch handling overhead before retirement, and flows decoded from MSROM.

## Important APIs, Types, and Schema

The event records are:

- `BACLEARS.ALL`, `BACLEARS.COND`, and `BACLEARS.RETURN`, all using `EventCode: "0xE6"` with different umasks for front-end resteers caused by branch handling.
- `ICACHE.ACCESSES`, `ICACHE.HIT`, and `ICACHE.MISSES`, all using `EventCode: "0x80"` with umasks for all fetches, cache hits, and misses that produce memory requests.
- `MS_DECODED.MS_ENTRY`, using `EventCode: "0xE7"` and `UMask: "0x1"` for micro-sequencer flow starts.

Every row uses `Counter: "0,1"` and has a `SampleAfterValue` default. This file uses only the compact schema fields `BriefDescription`, `Counter`, `EventCode`, `EventName`, `SampleAfterValue`, and `UMask`; there are no PEBS, data address, or offcore MSR fields.

## Control Flow and Data Flow

Perf reads this JSON into the KNL event alias table. At runtime, a named front-end event configures a generic core PMU counter with its event code and umask. Counts can then be compared against cycles, instructions, branch-retired, and branch-mispredicted events from `pipeline.json`.

The intended analysis flow is usually ratio-based: icache misses versus accesses, BACLEARS categories versus retired branches, or micro-sequencer entries versus total retired uops. The file itself only provides raw event selectors.

## State and Persistence Behavior

The file is immutable source metadata with no runtime state. It persists KNL-specific front-end selector values. Any runtime PMU state is created by perf when opening events and is discarded when the perf session ends.

## Dependencies and Integration Points

The file integrates with the KNL core PMU and the sibling `counter.json` capacity declaration. It also complements `pipeline.json`: `BACLEARS` are pre-retirement/front-end signals, while `BR_INST_RETIRED` and `BR_MISP_RETIRED` in `pipeline.json` provide retired branch denominators.

Instruction-cache events are front-end fetch metrics rather than offcore memory-source breakdowns. For miss-source investigation, users would combine them with offcore events from `cache.json` and `memory.json`.

## Risks and Edge Cases

`ICACHE.MISSES` counts an instruction fetch miss once, not once per outstanding cycle, so it should not be used as a direct stall-cycle metric. `BACLEARS` describe front-end resteers, not necessarily retired mispredictions, and may not line up one-for-one with branch-retired events.

All rows are constrained to only two programmable counters, so event groups that request many KNL core events can fail scheduling. The file also lacks `PublicDescription`, so user-facing interpretation depends heavily on the short `BriefDescription` text.

## Test Signals

Tests should parse the JSON array, confirm the seven expected `EventName` values, verify unique names and valid hex umasks, and confirm all rows are constrained to `0,1`. Integration smoke tests should check that `perf list` shows the `BACLEARS`, `ICACHE`, and `MS_DECODED` aliases and that representative events can be opened on KNL-compatible PMU tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/memory.json

## Purpose

`memory.json` defines Knights Landing perf aliases for memory-ordering machine clears and offcore-response memory-source breakdowns. It contains 101 records: one `MACHINE_CLEARS.MEMORY_ORDERING` event and 100 `OFFCORE_RESPONSE` events focused on DDR, MCDRAM, near/far locality, and non-DRAM responses.

The file lets users ask memory-source questions such as whether demand data reads, RFOs, prefetches, partial reads/writes, or code reads are served by local/far DDR, local/far MCDRAM, or non-DRAM address space.

## Important APIs, Types, and Schema

The file follows the perf event JSON schema with fields `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and, for offcore rows, `MSRIndex` and `MSRValue`.

Important event families are:

- `MACHINE_CLEARS.MEMORY_ORDERING`, `EventCode: "0xC3"`, `UMask: "0x2"`, for machine clears caused by memory-ordering hazards.
- `OFFCORE_RESPONSE.<request>.<source>`, almost all using `EventCode: "0xB7"` and `UMask: "0x1"`.

Offcore request classes include any code/data/read/request/RFO, bus locks, demand code/data/RFO, partial reads/writes, L1 data prefetches, L2 code/RFO prefetches, software prefetches, and UC code reads. Response/source classes include `DDR`, `DDR_NEAR`, `DDR_FAR`, `MCDRAM`, `MCDRAM_NEAR`, `MCDRAM_FAR`, and `NON_DRAM`.

Most offcore rows allow `MSRIndex: "0x1a6,0x1a7"`. Partial writes use `MSRIndex: "0x1a7"` because the descriptions say they should be programmed on PMC1. All rows list `Counter: "0,1"`, so the MSR field is the more specific hardware-programming constraint.

## Control Flow and Data Flow

Perf parses the event table, maps a requested alias to core event `0xB7/0x1`, and writes the listed offcore response filter into the selected offcore MSR. The MSR value combines request bits with response/source bits, so the named event controls both what traffic type is counted and where the response came from.

In use, these events are generally compared across source variants. For example, the DDR and MCDRAM variants of `DEMAND_DATA_RD` expose placement/locality differences, while `DDR_NEAR` versus `DDR_FAR` can reveal NUMA/tile-distance effects.

## State and Persistence Behavior

The JSON is static source metadata. Runtime state exists only when perf opens events and programs PMU registers/MSRs. Because offcore MSR filters are shared hardware resources, concurrent offcore events may be constrained by available counters and MSR slots even when each event descriptor looks independently valid.

## Dependencies and Integration Points

The file depends on perf's KNL event-map parser and the core offcore-response event implementation. It integrates closely with `cache.json`: both files use `OFFCORE_RESPONSE`, but `cache.json` focuses on L2/tile cache-response classes while `memory.json` focuses on DDR, MCDRAM, and non-DRAM source classes.

It also integrates with `counter.json` for core counter capacity and with system topology/runtime memory configuration. The semantic value of DDR versus MCDRAM near/far events depends on KNL memory mode and placement.

## Risks and Edge Cases

The largest risk is misprogramming or misinterpreting offcore MSR selectors. The file contains many similar rows whose only differences are `EventName`, `MSRValue`, and brief source text. A single wrong bit in `MSRValue` changes the measured memory source.

Partial-read descriptions note UC/WC outstanding semantics, while partial-write descriptions specify PMC1/`0x1a7`. Consumers that only honor `Counter: "0,1"` may schedule events in invalid combinations. `NON_DRAM` rows include MMIO transactions, so they should not be read as ordinary memory bandwidth.

`MACHINE_CLEARS.MEMORY_ORDERING` belongs to the machine-clear family rather than the offcore matrix, so scripts assuming every memory file row has `MSRIndex` will fail.

## Test Signals

Validation should parse the JSON, confirm 101 records, verify one `MACHINE_CLEARS` row and 100 `OFFCORE_RESPONSE` rows, check unique `EventName` values, and ensure every offcore row has `MSRIndex` and `MSRValue`. Cross-checks should verify expected near/far/source families and that partial-write events use `0x1a7`. Runtime or generated-table tests should expose representative DDR, MCDRAM, and non-DRAM aliases through `perf list` and open a small event set without parser errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/pipeline.json

## Purpose

`pipeline.json` defines Knights Landing perf aliases for core pipeline, retirement, branch, cycle, allocation-stall, recycle-queue, reservation-station, machine-clear, divider, and uop-retirement events. It contains 45 records that provide the common denominators and bottleneck counters used with the cache, memory, front-end, and floating-point event files.

## Important APIs, Types, and Schema

The file follows the perf event JSON schema. Its event families are:

- `BR_INST_RETIRED`: nine precise retired-branch classes, including all branches, calls, far branches, indirect calls, conditional jumps, non-return indirects, relative calls, returns, and taken conditional jumps.
- `BR_MISP_RETIRED`: the corresponding nine precise mispredicted retired-branch classes.
- `CPU_CLK_UNHALTED`: programmable and fixed-counter cycle events, including fixed counter 1 for core cycles and fixed counter 2 for reference cycles.
- `INST_RETIRED`: fixed and programmable retired-instruction events, including fixed counter 0 and precise programmable variants.
- `MACHINE_CLEARS`: all machine clears and self-modifying-code clears.
- `NO_ALLOC_CYCLES`: allocation pipeline no-uop cycles for all causes, mispredict wait, not-delivered/IQ-empty, RAT stall, and ROB full.
- `RECYCLEQ`: retired load/store recycle queue causes, including store-forwarding blocks, split loads/stores, locks, and store-address buffer full.
- `RS_FULL_STALL`: reservation station full stalls, including MEC-specific stalls.
- `UOPS_RETIRED`: all retired uops and micro-sequencer uops.
- `CYCLES_DIV_BUSY.ALL`: cycles when the divider is busy.

Several records include `PEBS: "1"` and two recycle-queue load/split events include `Data_LA: "1"`, marking precise sampling and data linear-address support. Fixed events use `Counter: "Fixed counter 0"`, `Fixed counter 1`, or `Fixed counter 2` rather than generic `0,1`.

## Control Flow and Data Flow

Perf maps each `EventName` to either a fixed counter or a programmable core event selector. Fixed events omit `EventCode` and rely on their fixed counter and umask identity; programmable events use `EventCode`, optional `UMask`, and `Counter: "0,1"`.

The practical analysis flow is compositional. Cycle and instruction events provide denominators; branch events feed prediction rates; allocation and reservation-station stall events identify front-end/back-end allocation pressure; recycle-queue events explain memory-ordering and forwarding hazards; and uop-retired events distinguish complex micro-sequencer flows from normal retirement.

## State and Persistence Behavior

The file is static metadata and does not mutate state. At runtime, perf may program fixed counters, generic counters, and precise sampling modes according to these descriptors. PEBS and data-address flags affect sampling capability but do not create persistence in the JSON itself.

## Dependencies and Integration Points

`pipeline.json` depends on perf's KNL event-map integration and on `counter.json` for the presence of three fixed core counters and two programmable core counters. It is a central integration file for performance analysis because sibling files often need its denominators: `frontend.json` branch/front-end counts pair with branch and cycle events; `floating-point.json` SIMD uop counts pair with `UOPS_RETIRED` and `INST_RETIRED`; `cache.json` and `memory.json` counts pair with cycles and instructions for rate calculations.

## Risks and Edge Cases

The biggest semantic risk is confusing fixed-counter aliases with programmable aliases. `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC` use fixed counters, while similarly named `_P` or `REF` variants use programmable events. Event grouping and availability differ between those forms.

Precise branch and recycle-queue events can carry PEBS/data-address expectations. If tooling drops `PEBS` or `Data_LA`, sampling behavior may differ from the alias metadata. `CYCLES_DIV_BUSY.ALL` counts divider busy cycles whether or not another divide uop is stalled waiting, so it is not a direct stall metric. `NO_ALLOC_CYCLES` categories can overlap in interpretation and should be analyzed with care.

Some rows omit `UMask` or `EventCode` because they are fixed or base programmable events. Schema checks must allow these legitimate omissions instead of treating them as malformed.

## Test Signals

Validation should parse the JSON, confirm 45 unique event names, verify the expected family counts, and ensure the three fixed-counter aliases reference fixed counters 0, 1, and 2. Additional checks should confirm PEBS/data-address fields remain on the precise events that need them. Integration tests should verify `perf list` exposes branch, cycle, instruction, recycle-queue, and no-allocation aliases and that representative fixed plus programmable events can be opened together within KNL counter constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/pipeline.json -->
