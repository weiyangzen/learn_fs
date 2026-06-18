# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l2-cache.json

Purpose: Defines 54 Zen 6 L2 cache PMU events for request classes, WCB requests, cache hit/miss status, prefetch outcomes, fill response sources, and system bandwidth utilization.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `l2_request_g1.*`, `l2_request_g2.*`, `l2_wcb_req.*`, `l2_cache_req_stat.*`, prefetch hit/miss families, `l2_fill_rsp_src.*`, and `l2_sys_bw.*`.

Control flow: Perf exposes the aliases and derived metrics can combine them for L2 access/miss/hit rates. `l2_sys_bw.*` adds Zen 6 source categories for local/remote DRAM fills, non-temporal writes, local/remote SCM/CXL fills, victims, and all bandwidth utilization.

State and persistence: No runtime state. The durable contract is event naming and mask encoding, including generation-specific aggregate names such as `dc_all`, `no_pf_all`, and `alt_mem`.

Dependencies and integration: Integrates with load-store fill events, instruction-cache fill events, and recommended L2 metrics. Source categories align with Zen 6 memory hierarchy and CXL/extension-memory descriptions.

Risks: Several Zen 5 names changed (`all_dc` to `dc_all`, `all_no_prefetch` to `no_pf_all`, `alternate_memories` to `alt_mem`), so formula reuse can fail. Prefetch and request-status aggregates overlap. New `l2_sys_bw` events require validation against hardware support and may not behave like ordinary cache-hit counters.

Test signals: Validate `perf list l2_`, run demand and prefetch-heavy memory tests, verify recommended L2 formulas for Zen 6 name compatibility, and test `l2_sys_bw.*` on local/remote memory and non-temporal write workloads.
