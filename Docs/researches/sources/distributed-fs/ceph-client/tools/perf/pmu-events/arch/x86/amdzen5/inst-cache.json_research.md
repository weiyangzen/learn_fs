# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/inst-cache.json

Purpose: Defines 12 Zen 5 instruction-cache, op-cache, and fetch IBS PMU events for frontend cache diagnostics.

Important APIs/types/functions: The table uses `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`. It includes instruction cache fills from L2/system, fetch IBS tagging/filtering/validity events, `ic_tag_hit_miss.*`, and `op_cache_hit_miss.*`.

Control flow: Perf exposes these aliases to users. `recommended.json` depends on `op_cache_hit_miss.op_cache_miss`, `op_cache_hit_miss.all_op_cache_accesses`, `ic_tag_hit_miss.instruction_cache_miss`, and `ic_tag_hit_miss.all_instruction_cache_accesses` for frontend miss ratios.

State and persistence: No runtime state exists. The durable interface is the event naming for cache-hit/miss ratios and fetch IBS status counters.

Dependencies and integration: Integrates with core CPU PMU, AMD IBS fetch sampling concepts, and recommended frontend metrics. It complements branch-prediction ITLB events and decode frontend-supply events.

Risks: Op-cache and instruction-cache counters are related but not interchangeable; `ic_fetch_miss_ratio` explicitly notes that an instruction cache miss is not counted when there is an op-cache hit. Renaming Zen 5-specific `instruction_cache_*` or `op_cache_*` names breaks recommended formulas.

Test signals: Validate `perf list ic_ op_cache`, run icache-thrashing and op-cache-friendly loops, and verify recommended `op_cache_fetch_miss_ratio` and `ic_fetch_miss_ratio` produce finite values.
