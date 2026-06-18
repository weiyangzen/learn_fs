# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/memory.json

## Purpose

`amdzen3/memory.json` defines 72 Zen 3 load/store, data-cache, DTLB, table-walker, lock, prefetch, fill-source, and memory-related core PMU events. It is the main Zen 3 source for L1 data-cache and load-store subsystem aliases.

## Important records and schema

Entries contain `EventName`, `EventCode`, optional `UMask`, `BriefDescription`, and in some cases `PublicDescription`.

Important families include:

- `ls_dispatch.*`: load, store, and load-store dispatch counts.
- `ls_dc_accesses`: all L1 data-cache accesses.
- `ls_mab_alloc.*` and `ls_alloc_mab_count`: miss address buffer allocation categories and outstanding miss counts.
- `ls_locks.*`: speculative/non-speculative lock and bus-lock events.
- `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_sw_pf_dc_fills.*`, and `ls_hw_pf_dc_fills.*`: demand, any, software-prefetch, and hardware-prefetch L1 data-cache fill sources split across local L2, same CCX, local/remote memory or IO, and external cache sources.
- `ls_l1_d_tlb_miss.*`, `ls_tablewalker.*`, and `ls_tlb_flush.all_tlb_flushes`: DTLB miss/reload, page-walk, and TLB flush events.
- `ls_pref_instr_disp.*` and `ls_inef_sw_pref.*`: software prefetch dispatch and ineffective prefetch conditions.
- `ls_misal_loads.*`, `ls_stlf`, `ls_st_commit_cancel2`, `ls_bad_status2.stli_other`: load/store forwarding, misalignment, store-cancel, and status hazards.
- `ls_not_halted_cyc`, `ls_ret_cl_flush`, `ls_ret_cpuid`, `ls_smi_rx`, `ls_int_taken`, `ls_rdtsc`: cycle and system/instruction-side memory/control support events.

## Control flow and integration

The file is converted into core PMU aliases by `jevents.py`. `amdzen3/recommended.json` references many aliases here for L1 data-cache fill metrics, DTLB metrics, all data-cache accesses, TLB flushes, and supporting stall/cycle formulas.

At runtime, perf users select aliases or derived metrics; perf uses the generated event table to program the core PMU event select and unit mask.

## State and persistence

No runtime state is stored here. Persistent state is the alias taxonomy and hardware event mapping. Fill-source masks encode locality semantics that are consumed by higher-level metrics and topology analysis.

## Dependencies

Dependencies are AMD Zen 3 load/store PMU definitions, perf's PMU JSON schema, and recommended metrics that reference `ls_*` aliases. The file also complements `cache.json`: L1/L2/cache-fill metrics often combine aliases from both files.

## Risks

Fill-source events have topology semantics; mistakes can mislead NUMA/locality analysis. Aggregate masks like `ls_l1_d_tlb_miss.all` and `ls_tlb_flush.all_tlb_flushes` are referenced by recommended metrics, so renames or mask changes are high impact. Some events are speculative or count conditions rather than retired architectural operations, which should be clear in user-facing analysis.

## Test signals

Run `jq empty`, PMU event generation, and metric parser tests. Validate that `recommended.json` formulas resolve all `ls_*` names. Hardware tests should exercise memory bandwidth, TLB miss/page-walk, lock, prefetch, and misaligned-load workloads to confirm relative counter behavior.
