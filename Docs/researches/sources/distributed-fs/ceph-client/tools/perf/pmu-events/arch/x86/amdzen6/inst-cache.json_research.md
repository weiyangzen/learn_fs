# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/inst-cache.json

Purpose: Defines 20 Zen 6 instruction-cache, op-cache, fetch IBS, and instruction-fill source PMU events.

Important APIs/types/functions: The schema uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. It includes `ic_cache_fill_l2`, `ic_cache_fill_sys`, `ic_fetch_ibs_events.*`, `op_cache_hit_miss.*`, and `ic_fills_from_sys.*` for local/remote/near/far/alternate-memory source attribution.

Control flow: Perf exposes the aliases as frontend cache events. Zen 6 recommended metrics use op-cache miss ratios, and instruction-fill source events can be used to locate instruction-fetch pressure in local L2, CCX, DRAM/MMIO, remote cache, far memory, or extension memory.

State and persistence: No mutable state. The persistent interface is the Zen 6 naming scheme for op-cache and instruction-fill source counters.

Dependencies and integration: Integrates with branch-prediction ITLB events, decode frontend-supply metrics, and recommended frontend metrics. Compared with Zen 5, Zen 6 adds `ic_fills_from_sys.*` and renames op-cache events to shorter `hit`, `miss`, and `all` suffixes.

Risks: Zen 6 removed the Zen 5 `ic_tag_hit_miss.*` names from this file, so any metric that expects those names must be generation-specific. Fill-source categories overlap through aggregate aliases. IBS fetch event names changed from `fetch_tagged/sample_*` to `tagged/filtered/valid`.

Test signals: Validate `perf list ic_ op_cache`, run instruction working-set tests, verify op-cache ratio metrics, and compare fill-source attribution under local-cache and memory-backed instruction fetch pressure.
