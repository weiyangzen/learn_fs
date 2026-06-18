# sources/distributed-fs/ceph-client/arch/x86/mm/tlb.c

## Purpose
`tlb.c` implements x86 TLB context management, PCID/ASID allocation, local and remote shootdowns, lazy TLB handling, global-ASID broadcast invalidation, PTI user-PCID invalidation, temporary-mm switching, and debugfs tuning of single-page flush thresholds.

## Important APIs, Types, and Functions
Important entry points include `switch_mm()`, `switch_mm_irqs_off()`, `leave_mm()`, `initialize_tlbstate_and_flush()`, `flush_tlb_mm_range()`, `flush_tlb_all()`, `flush_tlb_kernel_range()`, `flush_tlb_one_kernel()`, `flush_tlb_one_user()`, `flush_tlb_local()`, `__flush_tlb_all()`, `arch_tlbbatch_flush()`, `use_temporary_mm()`, `unuse_temporary_mm()`, `nmi_uaccess_okay()`, and KVM-exported `__get_current_cr3_fast()`. Core state is per-CPU `cpu_tlbstate`/`cpu_tlbstate_shared`, `struct flush_tlb_info`, per-mm `context.tlb_gen`, dynamic ASID slots, and optional global ASIDs.

## Control Flow and State
Context switching chooses an ASID with `choose_new_asid()`, optionally assigns global ASIDs for processes active on many CPUs when `INVLPGB` is available, writes CR3 with or without `CR3_NOFLUSH`, updates per-ASID generation state, maintains `mm_cpumask()`, and applies IBPB/L1D/PCE/LDT mitigations. Flush requests increment the mm TLB generation, build per-CPU flush info, choose broadcast `INVLPGB`, remote IPI, or local direct flushing, and then update secondary MMU notifiers. Remote `flush_tlb_func()` compares local and target generations, skips lazy CPUs when safe, uses partial single-page invalidations only when generation ordering proves they are sufficient, otherwise performs full local flushes.

## State and Persistence
Persistent state includes per-CPU loaded mm/asid/LAM state, lazy flags, user-PCID flush masks, ASID generation slots, global ASID allocation bitmaps and rollover state, `last_user_mm_spec` mitigation tracking, `tlb_single_page_flush_ceiling`, and debugfs control for that ceiling. Temporary-mm use disables breakpoints while active and clears cpumasks on exit to avoid unnecessary shootdowns.

## Dependencies and Integration Points
This file depends on x86 CR3/PCID/INVPCID/INVLPGB/PTI/LAM semantics, scheduler context switching, mmu_gather and unmap batching, CPU hotplug, perf RDPMC policy, LDT switching, speculation mitigations, KVM CR3 restoration, MMU notifiers, paravirt TLB hooks, debugfs, and trace/vmstat TLB events.

## Risks and Test Signals
Risks include missed generation ordering causing stale translations, freeing page tables without flushing lazy CPUs, ASID reuse without adequate invalidation, global ASID transition races, PTI user-PCID flush mask mistakes, CR3 state mismatches during NMIs or temporary-mm use, and performance regressions from over-flushing. Test signals include context-switch stress, munmap/mprotect/mremap shootdown tests, THP flush ranges, CPU hotplug reinitialization, PTI+PCID boot, INVLPGB-capable broadcast paths, KVM CR3 checks, membarrier ordering tests, perf RDPMC availability changes, and debugfs threshold tuning.
