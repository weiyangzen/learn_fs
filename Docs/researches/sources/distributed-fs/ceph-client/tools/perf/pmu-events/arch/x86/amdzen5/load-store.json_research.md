# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/load-store.json

Purpose: Defines 87 Zen 5 load-store PMU events for memory dispatch, locks, store-forwarding, MAB allocation, data fill sources, DTLB misses, prefetch activity, write-combining, cycles, and TLB flushes.

Important APIs/types/functions: Objects use `EventName`, `EventCode`, `UMask`, and mostly `BriefDescription`; one object uses the misspelled key `BriefDescript6ion`, which is part of the file's current schema surface. Families include `ls_dispatch.*`, `ls_dmnd_fills_from_sys.*`, `ls_any_fills_from_sys.*`, `ls_l1_d_tlb_miss.*`, `ls_pref_instr_disp.*`, `ls_sw_pf_dc_fills.*`, `ls_hw_pf_dc_fills.*`, `ls_alloc_mab_count`, `ls_not_halted_cyc`, and `ls_tlb_flush.all`.

Control flow: Perf exposes the aliases as core PMU events. Pipeline metrics depend on `ls_not_halted_cyc` to compute dispatch slots, and recommended metrics depend on dispatch, fill-source, DTLB, and TLB flush names.

State and persistence: No mutable state. The persistent contract is a detailed memory hierarchy naming scheme that separates demand versus any fills, software versus hardware prefetch fills, local/remote/near/far/alternate-memory sources, and page-size-specific DTLB miss masks.

Dependencies and integration: Integrates with L1 data-cache recommended metrics, pipeline dispatch-slot metrics, TLB metrics, and memory-locality analysis. It complements L2 response-source events and data-fabric bandwidth counters.

Risks: The misspelled `BriefDescript6ion` can be missed by strict description tooling. Fill-source masks overlap (`local_all`, `remote_cache`, `dram_io_all`, `far_all`, `all`), so totals require care. `ls_not_halted_cyc` drives many ratios; incorrect availability or multiplexing can distort topdown-style metrics.

Test signals: Validate JSON parsing despite the misspelled key, `perf list ls_`, memory locality workloads, TLB/page-size tests, software prefetch tests, and pipeline/recommended metrics that reference load-store events.
