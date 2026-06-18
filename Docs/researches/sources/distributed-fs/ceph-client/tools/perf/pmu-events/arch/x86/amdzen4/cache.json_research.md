# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/cache.json

## Purpose

`amdzen4/cache.json` defines 126 Zen 4 cache and cache-adjacent PMU events. It covers L1 data-cache fill sources, software/hardware prefetch behavior, L2 request and prefetch paths, instruction/op-cache behavior, and L3 lookup/latency counters.

## Important records and schema

Most records use `EventName`, `EventCode`, `UMask`, and `BriefDescription`. L3 records add `Unit: L3PMC` and may include `SliceId`, `EnAllSlices`, `ThreadMask`, and `EnAllCores` routing fields. One source key is misspelled as `BriefDescript6ion` on an L3 latency-related record; consumers that only read `BriefDescription` may ignore that text.

Important families include:

- `ls_mab_alloc.*`, `ls_alloc_mab_count`, and `ls_inef_sw_pref.*`: miss address buffer allocation, outstanding misses, and ineffective software prefetch conditions.
- `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_sw_pf_dc_fills.*`, and `ls_hw_pf_dc_fills.*`: demand, all, software-prefetch, and hardware-prefetch data-cache fills split across local L2, local CCX, near/far cache, near/far DRAM or IO, remote cache, and all categories.
- `ls_pref_instr_disp.*`: software prefetch instruction dispatch classes.
- `l2_request_g1.*`, `l2_cache_req_stat.*`, and `l2_pf_*`: L2 request classes, L2 hit/miss status, and L2 prefetch hit/miss by source/path. Zen 4 adds broader per-type prefetch masks than Zen 3.
- `ic_cache_fill_l2`, `ic_cache_fill_sys`, `ic_tag_hit_miss.*`, and `op_cache_hit_miss.*`: instruction-cache and op-cache access/miss aliases.
- `l3_lookup_state.*`, `l3_xi_sampled_latency.*`, and `l3_xi_sampled_latency_requests.*`: L3 coherent access/miss counts and sampled latency/request counters.

The aggregate `ls_inef_sw_pref.all` uses `UMask: 0x03` and has no description, acting as a combined ineffective software prefetch alias.

## Control flow and integration

`jevents.py` parses the array and routes L3 records to AMD L3 PMU generation through `Unit: L3PMC`. `amdzen4/recommended.json` depends heavily on this file for L1 data-cache fill metrics, L2 access/miss/hit formulas, L3 accesses/misses/latency, op-cache and instruction-cache miss ratios, and prefetch-related aliases.

At runtime, perf resolves aliases into core or L3 PMU events depending on the `Unit` field and generated table.

## State and persistence

The file is static metadata. Persistent semantics include alias names, masks, L3 routing fields, and topology categories like near/far cache or memory. Many formulas depend on exact names ending in `.all`, `.local_l2`, `.dram_io_far`, and similar suffixes.

## Dependencies

Dependencies include AMD Zen 4 cache/L3 PMU definitions, perf's AMD L3 PMU unit mapping, and recommended metrics that reference these aliases. The L3 routing fields depend on generated-table support in perf.

## Risks

The misspelled `BriefDescript6ion` key is a schema-risk signal and may lose documentation in generated outputs. L3 routing fields are easy to break when normalizing JSON because they are not used by most core events. Renaming `.all` or locality-specific aliases breaks many recommended formulas. Topology terms such as near/far memory/cache are hardware-specific and must remain aligned with AMD documentation.

## Test signals

Run JSON validation, PMU event generation, and metric parser tests for `amdzen4/recommended.json`. Check generated descriptions for records near the `BriefDescript6ion` typo. On Zen 4 hardware, validate `perf list` for core and `amd_l3` aliases, then sanity-check L2 hit/miss and L3 latency formulas under cache-fitting and memory-streaming workloads.
