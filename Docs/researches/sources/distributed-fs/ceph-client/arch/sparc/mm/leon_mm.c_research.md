# sources/distributed-fs/ceph-client/arch/sparc/mm/leon_mm.c

Purpose: LEON SPARC32 SRMMU support, including software page-table probing and cache/TLB operation implementations.

Important APIs/functions: `leon_swprobe(vaddr, paddr)` walks SRMMU tables by physical bypass loads. Cache/TLB functions include `leon_flush_icache_all`, `leon_flush_dcache_all`, `leon_flush_cache_all`, `leon_flush_tlb_all`, and per-mm/page/range wrappers. `leon3_getCacheRegs` reads LEON3 cache registers. `leon_flush_needed` decides whether context-switch cache flushing is required. `init_leon` installs `leon_ops`.

Control flow: `leon_swprobe` reads the context table pointer, validates physical pages with `_pfn_valid`, reads the current context, walks PGD/PMD/PED/PTE levels using LEON bypass loads, handles large PTEs at higher levels, computes physical address based on the found level, and returns the PTE. Flush functions issue LEON ASI cache/TLB flush instructions. `leon_flush_needed` reads cache set/size fields and disables context-switch flush when direct-mapped set size is no larger than page size. `init_leon` names the SRMMU, sets cache/TLB ops, sets poke hook, and records flush policy.

State and persistence: globals `leon_flush_during_switch` and `srmmu_swprobe_trace`; installed `sparc32_cachetlb_ops` and `poke_srmmu` persist after init. Cache/TLB hardware state is mutated by flush calls.

Dependencies/integration: includes LEON ASI/TLB headers and `mm_32.h`; integrates with SRMMU page tables, context register access, and common SPARC32 cache/TLB ops dispatch.

Risks: software probing must reject invalid physical table pointers to avoid bypass-load faults. Large-page physical address reconstruction depends on level-specific masks. Flush-needed heuristic only recognizes LEON3 cache fields and defaults to flushing when uncertain.

Test signals: LEON boot, page-fault/probe paths, context switch cache coherency with flush enabled/disabled, executable page icache coherency, DMA dcache flushes, TLB flush all/mm/page/range behavior, and cache register decoding logs.
