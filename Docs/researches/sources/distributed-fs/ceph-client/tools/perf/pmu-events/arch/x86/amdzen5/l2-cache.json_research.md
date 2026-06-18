# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/l2-cache.json

Purpose: Defines 44 Zen 5 L2 cache PMU events for request classes, WCB close requests, hit/miss status, prefetch outcomes, and fill response source attribution.

Important APIs/types/functions: The event schema is `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `l2_request_g1.*`, `l2_request_g2.*`, `l2_wcb_req.wcb_close`, `l2_cache_req_stat.*`, `l2_pf_hit_l2.*`, `l2_pf_miss_l2_hit_l3.*`, `l2_pf_miss_l2_l3.*`, and `l2_fill_rsp_src.*`.

Control flow: Perf exposes these as named core PMU aliases. `recommended.json` builds L2 accesses, misses, and hits per instruction from `l2_request_g1.*`, `l2_cache_req_stat.*`, and L2 prefetch families.

State and persistence: The file has no mutable state. It stores stable L2 event encodings and aggregate aliases such as `all_no_prefetch`, `all_dc`, and `all`.

Dependencies and integration: Integrates with load-store fill events, instruction-cache fill metrics, and recommended L2 cache metrics. Source attribution spans local CCX, near/far cache, DRAM/MMIO near/far, alternate memory, and all sources.

Risks: Some masks represent aggregate groups and overlap narrower masks. Recommended formulas rely on Zen 5 names like `all_no_prefetch`, `all_dc`, and `alternate_memories`; Zen 6 renames some of these, so metrics are not textually portable. Prefetch families split L1 data and L2 hardware prefetchers, which can be misinterpreted as demand misses.

Test signals: Validate event aliases, run L1 instruction/data miss workloads, hardware-prefetch-sensitive streams, and recommended L2 metrics; ensure every L2 event referenced from `recommended.json` resolves.
