<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlbflush.h

Purpose: declares LoongArch TLB flush interfaces used by MM, vmalloc, and SMP code.
Important APIs and types: exposes `local_flush_tlb_all`, `local_flush_tlb_mm`, `local_flush_tlb_range`, `local_flush_tlb_kernel_range`, `flush_tlb_*` wrappers, and page/hugepage flush helpers.
Control flow: local helpers perform CSR/TLB invalidations; SMP wrappers choose local versus remote invalidation depending on CPU masks and mm activity.
State and persistence: flushes mutate hardware TLB state and synchronize it with page-table changes.
Dependencies and integration: depends on `mmu_context`, CPU masks, page-table bits, and generic MM invalidation hooks.
Risks and test signals: missed flushes expose stale permissions or mappings. Signals include mprotect, munmap, fork/exec, vmalloc module mapping, THP split/collapse, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlbflush.h -->
