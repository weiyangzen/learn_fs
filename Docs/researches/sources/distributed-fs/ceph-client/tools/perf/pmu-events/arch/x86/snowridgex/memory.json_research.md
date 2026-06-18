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
