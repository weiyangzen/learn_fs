# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/memory.json

## Purpose

`amdzen4/memory.json` defines 29 Zen 4 memory-side core PMU events centered on load/store dispatch, DTLB and ITLB/page-walk behavior, misaligned loads, store-to-load forwarding, store commit cancellation, and TLB flushes.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important families include:

- `ls_dispatch.*`: load, store, and load-store dispatch counts.
- `ls_bad_status2.stli_other`, `ls_stlf`, and `ls_st_commit_cancel2`: status, store-to-load forwarding, and store cancellation hazards.
- `ls_l1_d_tlb_miss.*`: DTLB misses/reloads split by 4K, coalesced, 2M, and 1G pages, and by L2 TLB hit/miss; includes aggregate `all` and `all_l2_miss`.
- `bp_l1_tlb_fetch_hit.*`, `bp_l1_tlb_miss_l2_tlb_hit`, and `bp_l1_tlb_miss_l2_tlb_miss.*`: instruction-side TLB fetch hits/misses and page-size splits.
- `ls_misal_loads.*`: cacheline and 4KB/page-crossing misaligned loads.
- `ls_tlb_flush.all`: all TLB flushes.

## Control flow and integration

The file feeds generated core PMU aliases. `amdzen4/recommended.json` references `bp_l1_tlb_miss_l2_tlb_hit`, `bp_l1_tlb_miss_l2_tlb_miss.all`, `ls_l1_d_tlb_miss.all`, `ls_l1_d_tlb_miss.all_l2_miss`, and `ls_tlb_flush.all` for TLB metrics.

## State and persistence

There is no mutable state. The persistent behavior is the page-size and L2-hit/miss split encoded by unit masks and alias suffixes.

## Dependencies

Dependencies include AMD Zen 4 load/store and TLB PMU definitions, perf's core PMU schema, and recommended TLB formulas.

## Risks

TLB aliases are split across instruction-side `bp_*` names and data-side `ls_*` names, so metric authors can easily reference the wrong side. Aggregate aliases such as `.all` and `.all_l2_miss` are formula dependencies and should be preserved. Page-size-specific counts may not be meaningful on workloads that do not use those page sizes.

## Test signals

Validate JSON and generated aliases. Metric tests should resolve all TLB formulas. Hardware checks can use page-walk-heavy workloads, huge pages, TLB shootdowns, and misaligned memory access kernels to verify expected counter movement.
