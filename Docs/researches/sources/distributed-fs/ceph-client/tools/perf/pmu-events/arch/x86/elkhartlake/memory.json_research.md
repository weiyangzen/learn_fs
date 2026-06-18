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
