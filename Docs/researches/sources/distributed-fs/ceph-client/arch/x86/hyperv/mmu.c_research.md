## `sources/distributed-fs/ceph-client/arch/x86/hyperv/mmu.c`

Purpose: replaces remote TLB shootdowns with Hyper-V hypercalls when the hypervisor recommends enlightened remote TLB flushes.

Important APIs and functions: `hyperv_setup_mmu_ops()` installs `hyperv_flush_tlb_multi()` into `pv_ops.mmu.flush_tlb_multi`. `fill_gva_list()` encodes page ranges into Hyper-V GVA list entries. `hyperv_flush_tlb_others_ex()` handles extended VP-set hypercalls.

Control flow: flush builds an address-space identifier from CR3 without PCID bits or requests all address spaces, converts CPU masks to VP masks or extended VP sets, skips lazy CPUs unless freed page tables require flushing, chooses address-space vs address-list hypercalls based on `TLB_FLUSH_ALL` and GVA capacity, and falls back to `native_flush_tlb_multi()` on unsupported status or missing hypercall page.

State and persistence: no persistent private state beyond the installed paravirt op. It uses per-CPU hypercall input pages while interrupts are disabled.

Dependencies and integration points: Hyper-V hints, x86 TLB state, per-CPU `cpu_tlbstate_shared.is_lazy`, CR3/address-space semantics, tracepoints, VP-set helpers, and native TLB fallback.

Risks: incorrect lazy CPU skipping can leave stale translations. GVA encoding packs page counts in low address bits and must respect maximum rep count. Extended hypercall variable headers must compute `max_gvas` correctly.

Test signals: memory-management stress under Hyper-V, high CPU-count guests, lazy TLB workloads, page table free paths, tracepoints, and fallback behavior when hypercalls fail.
