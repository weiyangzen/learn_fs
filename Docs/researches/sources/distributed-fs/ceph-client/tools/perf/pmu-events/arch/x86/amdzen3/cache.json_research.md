# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/cache.json

## Purpose

`amdzen3/cache.json` defines 67 AMD Zen 3 cache, instruction-fetch, TLB, op-cache, and L3 PMU event records for perf. It provides raw event names, event select values, unit masks, short descriptions, and `Unit: L3PMC` markers for uncore L3 events so perf can expose these counters on Zen 3 systems.

## Important records and schema

Each entry is a JSON object with `EventName`, `EventCode`, optional `UMask`, optional `BriefDescription`, and optional `Unit`. Core PMU events omit `Unit`; L3 events use `Unit: L3PMC`, which `jevents.py` maps to the AMD L3 PMU name.

Important event families include:

- `l2_request_g1` and `l2_request_g2`: common and rare L2 request classes, including data reads, stores, instruction reads, prefetches, sized/non-cacheable reads, self-modifying-code invalidations, and bus-lock traffic.
- `l2_cache_req_stat`: L2 access status masks for instruction/data hits and misses; aggregate aliases such as `ic_dc_miss_in_l2` and `ic_dc_hit_in_l2` feed recommended metrics.
- `l2_pf_*`, `l2_latency`, `l2_fill_pending`, and `l2_wcb_req`: L2 prefetch hit/miss paths, fill latency/busy cycles, and write-combining-buffer requests.
- `ic_*` and `op_cache_hit_miss`: instruction-cache fills, fetch-window misses, stalls, invalidations, instruction-cache tag hit/miss, op-cache hit/miss, and op-cache/instruction-cache mode switches.
- `bp_l1_tlb_miss_l2_tlb_*`: instruction-side TLB miss events split by L2 TLB hit/miss and page size.
- `l3_request_g1`, `l3_lookup_state`, `l3_comb_clstr_state`, `xi_sys_fill_latency`, and `xi_ccx_sdp_req1`: L3 accesses, misses, and miss latency support.

One aggregate event, `l2_request_g1.all_no_prefetch`, intentionally has no description and uses `UMask: 0xf9` to combine non-prefetch L2 request masks.

## Control flow and integration

There is no runtime control flow in this file. Build-time control flow is:

1. perf's PMU event build scans model folders listed in `arch/x86/mapfile.csv`.
2. `jevents.py` parses this JSON array.
3. Records with `Unit: L3PMC` are routed to AMD L3 PMU tables; records without `Unit` become core PMU event aliases.
4. Generated tables are compiled into `pmu-events.c` and surfaced through perf event lookup.

`recommended.json` depends on many names from this file, especially `l2_request_g1.*`, `l2_pf_*`, `l2_cache_req_stat.*`, `l3_lookup_state.*`, `xi_sys_fill_latency`, `xi_ccx_sdp_req1`, `ic_tag_hit_miss.*`, and `op_cache_hit_miss.*`.

## State and persistence

The file is static source data. Its persistent contract is the event name/code/mask mapping. Changing a name breaks metric expressions and user-visible perf aliases; changing an event code or mask changes the hardware counter programmed by perf.

## Dependencies

Dependencies are the perf PMU JSON schema, AMD Zen 3 performance-monitoring event definitions, and perf's AMD PMU unit mapping. The file also depends indirectly on metric parser support for aliases referenced in `recommended.json`.

## Risks

The main risks are silent hardware miscounting from wrong event codes or masks, broken derived metrics if an alias is renamed, and bad PMU routing if L3 records lose `Unit: L3PMC`. Aggregate masks with sparse descriptions should be preserved carefully because they are consumed by formulas even when not directly user-facing.

## Test signals

Useful checks are `jq empty` for JSON validity, perf's PMU event generation target, metric tests for formulas referencing these events, `perf list` on Zen 3 for alias visibility, and hardware sanity checks such as comparing L2 access/hit/miss relationships and L3 latency formulas under controlled workloads.
