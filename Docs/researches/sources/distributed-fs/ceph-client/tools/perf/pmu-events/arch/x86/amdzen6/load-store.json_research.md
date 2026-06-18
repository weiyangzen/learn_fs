# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/load-store.json

Purpose: Defines 88 Zen 6 load-store PMU events covering memory dispatch, locks, CLFLUSH/CPUID, interrupts, store/load conflicts, MAB allocation, demand/any/prefetch fill sources, DTLB misses, misaligned loads, WCB closes, cycles, and TLB flushes.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and mostly `BriefDescription`; like Zen 5, one object exposes the misspelled `BriefDescript6ion` key. Families include `ls_locks.*`, `ls_dispatch.*`, `ls_mab_alloc.*`, `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_l1_d_tlb_miss.*`, `ls_pref_instr_disp.*`, `ls_sw_pf_dc_fills.*`, `ls_hw_pf_dc_fills.*`, `ls_alloc_mab_count`, `ls_not_halted_cyc`, and `ls_not_halted_p0_cyc.p0_freq_cyc`.

Control flow: Perf exposes these aliases. Zen 6 pipeline metrics depend on `ls_not_halted_cyc`; recommended metrics depend on dispatch, fill-source, DTLB miss, and TLB flush aliases.

State and persistence: No runtime state. The durable interface is Zen 6's memory hierarchy taxonomy, including renamed short suffixes such as `ls_mab_alloc.ls`, `hwpf`, and `alt_mem`.

Dependencies and integration: Integrates with pipeline dispatch-slot formulas, L1 data-cache recommended metrics, TLB metrics, and memory locality analysis. It complements L2 and L3 source events.

Risks: The misspelled description key can break strict schema consumers. Fill-source categories overlap through aggregate aliases. Zen 5-to-Zen 6 renames (`ld_dispatch` to `pure_ld`, `hardware_prefetcher_allocations` to `hwpf`, `alternate_memories` to `alt_mem`) require generation-specific formulas.

Test signals: Validate JSON parsing and `perf list ls_`, run load/store dispatch tests, DTLB page-size tests, prefetch tests, memory locality tests, and `perf stat -M PipelineL1,PipelineL2` to confirm `ls_not_halted_cyc` integration.
