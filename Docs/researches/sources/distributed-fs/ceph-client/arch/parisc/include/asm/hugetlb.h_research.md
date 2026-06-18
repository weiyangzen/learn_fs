# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hugetlb.h

Purpose: supplies PA-RISC hugepage hooks to generic hugetlb code.

Important APIs/types/functions: defines architecture helpers for huge PTE access, hugepage flush/update behavior, and generic hugetlb integration points.

Control flow: hugetlb code allocates huge mappings, updates PTEs with PA-RISC flags, and flushes TLB/cache entries as required.

State and persistence: huge PTEs persist in process page tables and TLBs. Dependencies and integration: depends on `pgtable.h`, `page.h`, and generic hugetlb mm code.

Risks and test signals: flag conflicts with `_PAGE_HUGE` or special bits can corrupt mappings. Test with hugetlb selftests, mmap/munmap, fork, and page-fault handling on huge pages.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
