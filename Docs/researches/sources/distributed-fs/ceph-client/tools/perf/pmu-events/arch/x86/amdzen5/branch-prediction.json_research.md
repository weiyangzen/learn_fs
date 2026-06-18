# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/branch-prediction.json

## Purpose

`amdzen5/branch-prediction.json` defines 16 Zen 5 branch-prediction and instruction-side TLB PMU events. It is an early Zen 5 category-specific file that combines predictor events, redirect counts, and instruction fetch TLB hit/miss breakdowns.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important event families include:

- `bp_l1_tlb_miss_l2_tlb_hit`: L1 ITLB miss with L2 ITLB hit.
- `bp_l1_tlb_miss_l2_tlb_miss.*`: L1 and L2 ITLB misses split by 4K, 2M, 1G, coalesced 4K, and all.
- `bp_l1_tlb_fetch_hit.*`: instruction fetch TLB hits split by page size/coalesced categories.
- `bp_l2_btb_correct`, `bp_dyn_ind_pred`, and `bp_de_redirect`: branch prediction and decode redirect primitives.
- `bp_redirects.*`: redirect counts from static, dynamic, and other sources.

## Control flow and integration

The file is parsed by perf's PMU event generator into Zen 5 core PMU aliases. Although this work item only includes the branch-prediction file, adjacent Zen 5 files such as `recommended.json`, `pipeline.json`, `inst-cache.json`, and `load-store.json` are likely to reference some of these aliases for branch and TLB metrics.

## State and persistence

There is no mutable state. The persistent contract is the branch-prediction and instruction-side TLB alias set. Because Zen 5 uses a more split folder taxonomy than Zen 3/4, the file path and names are part of the model organization contract.

## Dependencies

Dependencies are AMD Zen 5 branch-prediction PMU definitions, perf's JSON event schema, and any Zen 5 recommended/pipeline metrics that refer to these aliases.

## Risks

Instruction-side TLB aliases overlap conceptually with memory/load-store TLB counters but are in a branch-prediction file, so future metric authors must choose the correct side. The branch redirect categories may not be mutually exclusive unless hardware documentation says so. Since Zen 5 support is newer and split across renamed category files, cross-file formula references are a higher-risk area.

## Test signals

Validate JSON and generated PMU aliases. Run full Zen 5 PMU event generation and metric parsing across adjacent Zen 5 files. On Zen 5 hardware, use branch-heavy and instruction-TLB-heavy workloads to confirm predictor redirect and ITLB page-size counters move as expected.
