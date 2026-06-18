<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbflush.h

Purpose: Declares and inlines local and remote RISC-V TLB flush operations.

Important APIs/types/functions: Key APIs are `local_flush_tlb_all()`, `local_flush_tlb_all_asid()`, `local_flush_tlb_page()`, `local_flush_tlb_page_asid()`, `flush_tlb_all()`, `flush_tlb_mm_range()`, `flush_tlb_page()`, `flush_tlb_kernel_range()`, hugepage range flushes, and tlbbatch hooks.

Control flow: Local helpers emit `sfence.vma` variants, optionally through errata wrappers; SMP implementations perform remote shootdowns and range/all selection.

State and persistence: No durable state here except `tlb_flush_all_threshold`; hardware TLBs are the target state.

Dependencies and integration points: Used by page-table updates, vmalloc, ioremap, ASID management, SBI/irq IPI backends, and errata code.

Risks: Under-flushing causes stale translations and memory corruption; over-flushing hurts performance.

Test signals: SMP shootdown tests, ASID rollover, mprotect/munmap, vmalloc/ioremap, THP, and errata-platform boot.

Source read size: 73 lines, 2245 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbflush.h -->
