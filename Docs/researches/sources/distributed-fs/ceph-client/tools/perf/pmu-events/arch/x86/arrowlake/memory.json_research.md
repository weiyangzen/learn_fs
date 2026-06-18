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
