# subset-b-006731 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/memory.json

## Purpose

`memory.json` is a Snow Ridge X86 PMU event catalog consumed by the Linux `perf` PMU events build/runtime tooling. It contributes memory-oriented symbolic event aliases for the `snowridgex` CPU model, especially machine clears, misaligned memory page splits, and offcore response (`OCR.*`) events for DRAM, local DRAM, and L3-miss classifications.

The file is data, not executable code. Its behavior comes from the shared perf PMU event JSON schema and the perf tooling that parses architecture/model event tables into generated C tables or runtime event descriptions.

## Important APIs, Types, and Data Shape

The top-level value is a JSON array of 60 event objects. Each object follows the perf PMU event schema with fields such as:

- `EventName`: public perf alias, for example `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT` or `OCR.READS_TO_CORE.L3_MISS`.
- `EventCode` and `UMask`: raw architectural event selector data for programmable counters.
- `Counter`: allowed counter set, usually `0,1,2,3`.
- `BriefDescription` and sometimes `PublicDescription`: text surfaced by perf event listing/help paths.
- `SampleAfterValue`: default sampling period metadata.
- `PEBS`: present on the two misaligned page-split events, marking precise-event support.
- `MSRIndex` and `MSRValue`: offcore-response selector programming for `OCR.*` events, using MSRs `0x1a6` and/or `0x1a7`.
- `Deprecated`: present on four `OCR.DEMAND_DATA_RD.*` compatibility aliases.

The dominant event family is `OCR.*` with shared `EventCode` `0XB7` and `UMask` `0x1`. These entries differ primarily by `MSRValue`, which selects request type and response class.

## Event Coverage

The file defines:

- Machine clear and misaligned memory events: `MACHINE_CLEARS.MEMORY_ORDERING`, `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT`, and `MISALIGN_MEM_REF.STORE_PAGE_SPLIT`.
- Offcore code-read events for all code reads, demand code reads, and L2 hardware prefetch code reads.
- Demand data, RFO, L2 hardware prefetch data/RFO, writeback, streaming-write, uncached read/write, miscellaneous, prefetch, and aggregate read-to-core events.
- Response categories expressed as `DRAM`, `LOCAL_DRAM`, `L3_MISS`, and `L3_MISS_LOCAL`.

The `LOCAL_DRAM` aliases use the same `MSRValue` as the corresponding `DRAM` aliases, and the `L3_MISS_LOCAL` aliases use the same `MSRValue` as the matching `L3_MISS` aliases. That appears intentional compatibility naming for this platform's available response filters, but it is a point to preserve carefully because a consumer will treat the aliases as distinct event names with identical raw encoding.

## Control Flow and Integration

There is no in-file control flow. Integration flow is external:

1. The perf PMU event table generator or runtime parser discovers this file through the architecture/model path `tools/perf/pmu-events/arch/x86/snowridgex/`.
2. Each JSON object is converted into an event alias for the Snow Ridge model.
3. Users can reference `EventName` values with perf commands such as `perf list`, `perf stat -e`, or `perf record -e`.
4. For `OCR.*` events, perf must program the offcore response MSR(s) listed by `MSRIndex` before counting with event code `0XB7`.

The file depends on shared perf handling for optional fields. If `Deprecated` is honored, the old demand-data aliases remain visible as deprecated aliases while the `OCR.DEMAND_DATA_AND_L1PF_RD.*` names are the preferred replacements.

## State and Persistence Behavior

The file is static repository data. It does not persist runtime state itself. Its persistent effect is the generated or parsed PMU event metadata distributed with perf. The raw fields are effectively ABI-like for users because event names, deprecation markers, descriptions, and encodings can be scripted in monitoring and profiling workflows.

## Dependencies and Coupling

The main dependencies are:

- The Linux perf PMU event JSON schema and parser.
- X86 PMU programmable counter support for counters `0,1,2,3`.
- Offcore response MSR programming support for `MSRIndex` values `0x1a6,0x1a7`.
- Snow Ridge-specific event encoding semantics from the processor PMU specification.

The file is also coupled to nearby Snow Ridge event category files. For example, `other.json` defines `OCR.*.ANY_RESPONSE` and `*.OUTSTANDING` variants, while this file defines DRAM and L3-miss response variants.

## Risks

- `EventCode` uses uppercase `0XB7` for OCR events. JSON parsers treat this as a string, but validators that expect lowercase `0x` text should normalize rather than reject it.
- Several aliases have identical encodings, especially `DRAM` versus `LOCAL_DRAM` and `L3_MISS` versus `L3_MISS_LOCAL`. Deduplication logic must not accidentally drop public aliases.
- The four deprecated `OCR.DEMAND_DATA_RD.*` entries map to the newer demand-data-and-L1-prefetch names. Removing them may break existing perf command lines.
- OCR entries depend on MSR side programming. If `MSRIndex` or `MSRValue` is malformed, the event may still parse but count the wrong offcore response class.
- Descriptive wording such as `modified writeBacks` and repeated `not supplied by the L3 cache` phrases is user-facing through perf help, so copy edits can have compatibility and documentation impact.

## Test Signals

Useful validation signals include:

- `jq` parse and schema checks over the file; this file contains 60 event objects.
- Perf PMU event table generation tests that include the `snowridgex` model.
- `perf list` checks for representative aliases: `MACHINE_CLEARS.MEMORY_ORDERING`, `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT`, `OCR.READS_TO_CORE.DRAM`, and deprecated `OCR.DEMAND_DATA_RD.DRAM`.
- Tests that preserve duplicate-encoding aliases as separate names.
- Tests that OCR events carry both `MSRIndex` and `MSRValue` into generated event tables.
- PEBS metadata checks for the two `MISALIGN_MEM_REF.*_PAGE_SPLIT` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/other.json

## Purpose

`other.json` is a Snow Ridge X86 perf PMU event catalog for events that do not fit cleanly into the memory or pipeline group files. It defines bus-lock, interrupt, deprecated memory-bound stall aliases, and several offcore response (`OCR.*`) miscellaneous response/latency events for the `snowridgex` model.

The file is declarative event metadata. Runtime behavior is provided by the shared Linux `perf` PMU event parser, generated event tables, and X86 PMU programming logic.

## Important APIs, Types, and Data Shape

The file is a JSON array of 22 event objects using the perf PMU event schema. Important fields are:

- `EventName`: symbolic alias exposed to users, such as `BUS_LOCK.SELF_LOCKS`, `HW_INTERRUPTS.MASKED`, or `OCR.UC_RD.OUTSTANDING`.
- `EventCode` and `UMask`: raw programmable event encoding where applicable.
- `Counter`: all entries target general-purpose counters `0,1,2,3`.
- `EdgeDetect`: used by bus-lock count events that count accepted/self bus locks as edges.
- `Deprecated`: present on compatibility aliases for old bus-lock and C0-stall names.
- `MSRIndex` and `MSRValue`: used by OCR events that require offcore response MSR programming.
- `PublicDescription`, `BriefDescription`, and `SampleAfterValue`: user-facing and sampling metadata.

There are no `PEBS` entries in this file.

## Event Coverage

The file defines four main categories:

- `BUS_LOCK.*`: current aliases `BLOCK_CYCLES`, `LOCK_CYCLES`, and `SELF_LOCKS`, plus deprecated aliases `ALL`, `CYCLES_OTHER_BLOCK`, and `CYCLES_SELF_BLOCK`.
- `C0_STALLS.*`: three deprecated load-stall aliases that refer users to `MEM_BOUND_STALLS.LOAD_DRAM_HIT`, `LOAD_L2_HIT`, and `LOAD_LLC_HIT`.
- `HW_INTERRUPTS.*`: masked cycles, pending-and-masked cycles, and received interrupt count events.
- `OCR.*`: `ANY_RESPONSE` and `OUTSTANDING` variants for code reads, streaming writes, miscellaneous requests, prefetches, and uncached reads/writes.

The `OCR.*.OUTSTANDING` events use only `MSRIndex` `0x1a6` and encode latency-style counting with high-bit `MSRValue` values such as `0x8000000000000044` and `0x8000100000000000`.

## Control Flow and Integration

There is no executable control flow in the file. The effective flow is:

1. Perf discovers the file under `arch/x86/snowridgex`.
2. The event-table tooling parses each object and joins it with the Snow Ridge model event set.
3. User-facing tools expose the names through `perf list` and resolve them in `perf stat` or `perf record`.
4. For `BUS_LOCK.*`, perf programs event `0x63` with the appropriate umask and edge-detect flag where present.
5. For `HW_INTERRUPTS.*`, perf programs event `0xcb` with umasks `0x1`, `0x2`, or `0x4`.
6. For OCR entries, perf programs event `0XB7`, umask `0x1`, and the requested offcore response MSR value.

Deprecated entries remain part of resolution flow so old names can continue to resolve while pointing users toward newer aliases.

## State and Persistence Behavior

The file itself has no mutable state. Its content becomes persistent perf metadata after installation or build. The `Deprecated` flags, event names, and descriptions are persistent compatibility signals: changing them affects scripts, dashboards, and profiling documentation that rely on stable event aliases.

## Dependencies and Coupling

Dependencies include:

- The perf PMU event JSON schema.
- Snow Ridge PMU support for event codes `0x63`, `0xcb`, and `0XB7`.
- Offcore response MSRs `0x1a6` and `0x1a7` for OCR events.
- Shared perf handling for `EdgeDetect` and `Deprecated`.

The file is coupled to `pipeline.json` through deprecated `C0_STALLS.*` references to `MEM_BOUND_STALLS.*` names that are not defined in this file, and to `memory.json` through shared OCR request categories.

## Risks

- Deprecated aliases are still valid public names. Removing or renaming them can break existing perf command lines.
- `BUS_LOCK.ALL` has `Deprecated` and `EdgeDetect` but no `UMask`; parsers must tolerate event-specific defaults as represented in upstream event tables.
- OCR entries use uppercase `0XB7`, matching nearby Snow Ridge files but potentially surprising strict text validators.
- Long interrupt descriptions are surfaced to users; truncation or escaping issues in generated tables would reduce usability.
- The `OUTSTANDING` OCR entries use only `MSRIndex` `0x1a6`, unlike many `ANY_RESPONSE` entries that use both `0x1a6,0x1a7`. Validation should preserve this distinction.

## Test Signals

Useful validation signals include:

- `jq` parse and length checks; this file contains 22 event objects.
- Perf table generation for the Snow Ridge model.
- `perf list` checks for `BUS_LOCK.SELF_LOCKS`, `BUS_LOCK.ALL`, `HW_INTERRUPTS.PENDING_AND_MASKED`, `OCR.ALL_CODE_RD.OUTSTANDING`, and `OCR.UC_RD.OUTSTANDING`.
- Checks that six deprecated aliases remain marked deprecated.
- Checks that `EdgeDetect` is retained for `BUS_LOCK.ALL` and `BUS_LOCK.SELF_LOCKS`.
- OCR encoding tests that preserve `MSRIndex` differences between `ANY_RESPONSE` and `OUTSTANDING` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/pipeline.json

## Purpose

`pipeline.json` is the Snow Ridge X86 perf PMU event catalog for pipeline, retirement, branch, topdown, clock, load-block, machine-clear, and uop events. It supplies the symbolic event aliases used by Linux `perf` for high-level pipeline analysis on the `snowridgex` CPU model.

This is static metadata rather than executable code. The important behavior is how perf's PMU event parser maps these event descriptions into user-visible aliases and raw PMU encodings.

## Important APIs, Types, and Data Shape

The top-level JSON array contains 60 event objects. Key schema fields include:

- `EventName`: the user-facing perf alias, for example `BR_INST_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.CORE`, or `TOPDOWN_FE_BOUND.ITLB`.
- `EventCode` and `UMask`: programmable counter encodings for most non-fixed events.
- `Counter`: either general counters `0,1,2,3` or fixed counter labels for fixed events.
- `PEBS`: marks precise-event support; 26 entries include `PEBS: "1"`.
- `Deprecated`: marks compatibility aliases, present on three entries.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: user-facing descriptions and default sampling periods.

Fixed-counter aliases include `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.REF_TSC`, and `INST_RETIRED.ANY`. Programmable alternatives include `CPU_CLK_UNHALTED.CORE_P`, `CPU_CLK_UNHALTED.REF`, `CPU_CLK_UNHALTED.REF_TSC_P`, and `INST_RETIRED.ANY_P`.

## Event Coverage

The file covers these major groups:

- Branch retirement and misprediction: `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, and `BTCLEAR.ANY`.
- Clock and instruction retirement: `CPU_CLK_UNHALTED.*` and `INST_RETIRED.*`.
- Divider and load-block behavior: `CYCLES_DIV_BUSY.*` and `LD_BLOCKS.*`.
- Machine clears: `MACHINE_CLEARS.ANY`, `DISAMBIGUATION`, `PAGE_FAULT`, and `SMC`.
- Topdown slots: `TOPDOWN_BAD_SPECULATION.*`, `TOPDOWN_BE_BOUND.*`, `TOPDOWN_FE_BOUND.*`, and `TOPDOWN_RETIRING.ALL`.
- Uop issue/retirement: `UOPS_ISSUED.ANY` and `UOPS_RETIRED.*`.

Deprecated entries are `CYCLES_DIV_BUSY.ANY`, `TOPDOWN_BAD_SPECULATION.MONUKE`, and `TOPDOWN_BE_BOUND.STORE_BUFFER`.

## Control Flow and Integration

There is no direct control flow. The integration path is:

1. Perf discovers the file in the Snow Ridge event directory.
2. The PMU event parser or generator loads each object into the model-specific event table.
3. `perf list` displays aliases and descriptions.
4. `perf stat`, `perf record`, and related commands resolve aliases to fixed counters or programmable event selectors.
5. Topdown analysis tooling can consume the `TOPDOWN_*` events to classify issue slots into retiring, bad speculation, frontend-bound, and backend-bound categories.

Events sharing `EventCode` are differentiated by `UMask` and sometimes by fixed-counter designation. For example, many branch-retired events use `0xc4`, branch-mispredict events use `0xc5`, and topdown categories use `0x71`, `0x73`, or `0x74`.

## State and Persistence Behavior

The file stores static PMU metadata. It has no runtime state, locks, or persistence of its own. Once included in perf, its event names and encodings become persistent user-facing interfaces. The fixed-counter aliases are especially sensitive because users may choose them to avoid consuming programmable counters.

## Dependencies and Coupling

Dependencies include:

- Linux perf's PMU event JSON schema and table generator/parser.
- Snow Ridge CPU support for fixed counters 0, 1, and 2 and programmable counters `0,1,2,3`.
- PEBS handling for precise-capable retired-branch, retired-instruction, load-block, topdown-retiring, and uop-retired events.
- Topdown metric consumers that interpret slot-counting events.

The file is related to `memory.json` through machine-clear coverage: `pipeline.json` contains broad machine-clear and disambiguation/page-fault/SMC events, while `memory.json` adds `MACHINE_CLEARS.MEMORY_ORDERING`.

## Risks

- Fixed-counter entries do not include `EventCode`, relying on `Counter` and `EventName` conventions. Validators must not require `EventCode` on fixed events.
- Several programmable and fixed aliases describe similar clock or instruction counts. Incorrect alias selection can consume a different counter class.
- `PEBS` metadata is widespread and user-visible; losing it would degrade precise sampling workflows.
- Topdown events count issue slots, not raw cycles or instructions. Consumers must not compare them directly to non-slot events without the proper topdown model.
- Deprecated aliases should remain resolvable for compatibility but should not be used as preferred names.
- `SampleAfterValue` varies by category; changing it can alter default sampling behavior.

## Test Signals

Useful validation signals include:

- `jq` parse and length checks; this file contains 60 event objects.
- Perf table generation for `snowridgex`.
- `perf list` checks for representative fixed, programmable, PEBS, topdown, and deprecated names: `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.CORE_P`, `INST_RETIRED.ANY`, `BR_MISP_RETIRED.ALL_BRANCHES`, `TOPDOWN_FE_BOUND.ITLB`, and `TOPDOWN_BAD_SPECULATION.MONUKE`.
- Checks that 26 entries retain `PEBS: "1"`.
- Checks that fixed counter entries are accepted without `EventCode`.
- Tests that topdown event umasks remain distinct and are not collapsed by shared `EventCode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/pipeline.json -->
