<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbflush.h

Purpose: defines x86 TLB flush state, CR4 shadow management, dynamic PCID/ASID context tracking, lazy TLB handling, range flush APIs, broadcast ASID helpers, and PTE/PMD flush-decision helpers.

Important APIs/types: `tlb_context`, `tlb_state`, `tlb_state_shared`, per-CPU `cpu_tlbstate`, `enter_lazy_tlb()`, `nmi_uaccess_okay()`, CR4 set/clear helpers, `initialize_tlbstate_and_flush()`, `flush_tlb_info`, `flush_tlb_local()`, `flush_tlb_multi()`, `flush_tlb_mm_range()`, `flush_tlb_kernel_range()`, `arch_tlbbatch_*()`, `pte_flags_need_flush()`, `pte_needs_flush()`, `huge_pmd_needs_flush()`, and LAM state helpers.

Control flow: context switch updates loaded mm/ASID/PCID state and decides whether stale contexts require flush. Page-table changes increment mm TLB generations, collect affected CPUs, and issue local or remote flushes. Lazy TLB mode avoids unnecessary CR3 loads for kernel threads. CR4 helpers update shadow and hardware with interrupts disabled.

State and persistence: per-CPU TLB state tracks loaded mm, ASIDs, generation numbers, CR4 shadow, LAM mode, user PCID flush mask, lazy state, and invalidation flags. MM context stores TLB generation and optional global ASID transition state. Dependencies include mm, scheduler, SMP IPIs, PTI, PCID, INVPCID/INVLPGB, mmu notifiers, page-table flags, and address masking.

Risks: stale TLB entries can cause memory corruption or security bugs; loaded_mm inconsistency affects NMI uaccess; CR4 shadow races can corrupt CPU feature state; incorrect PTE flush decisions can miss permission demotions. Test signals include context-switch stress, fork/exec/mmap/munmap, PCID/PTI/LAM combinations, mmu notifier users, hugepage permission changes, NMI uaccess tests, and broadcast TLB flush capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbflush.h -->
