# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgalloc.h

Purpose: provides x86 page-table allocation and population hooks layered on generic `pgalloc`, including PTI-aware PGD allocation order, paravirt notifications, and helpers for installing lower-level page-table pages.

Important APIs, types, and functions: defines `__HAVE_ARCH_PTE_ALLOC_ONE`, `__HAVE_ARCH_PGD_FREE`, `pgd_allocation_order()`, `pgd_alloc()`, `pgd_free()`, `pte_alloc_one()`, `___pte_free_tlb()`, `__pte_free_tlb()`, `pmd_populate_kernel()`, `pmd_populate_kernel_safe()`, `pmd_populate()`, and level-dependent `__pmd_free_tlb()`, `pud_populate()`, `pud_populate_safe()`, `p4d_populate()`, `p4d_populate_safe()`, `__pud_free_tlb()`, `pgd_populate()`, `pgd_populate_safe()`, and `__p4d_free_tlb()`.

Control flow: allocation order returns order-1 when PTI is enabled so each PGD has kernel and user halves. Populate helpers notify paravirt backends of page-table page allocation, then install entries with `_PAGE_TABLE` and physical addresses. Free helpers route through architecture TLB gather destructors.

State and persistence: page-table pages are allocated runtime memory attached to `mm_struct`s or kernel mappings. Paravirt hooks may maintain hypervisor shadow state.

Dependencies and integration points: depends on generic pgalloc, x86 page-table levels, `set_p*d()` helpers, `__pa()`, PTI feature detection, and paravirt XXL hooks.

Risks: missing paravirt notifications can desynchronize shadow page tables. Safe populate helpers must only be used when TLB flushing is unnecessary. PTI allocation order and 5-level folding must match top-level page-table layout.

Test signals: fork/exec/mmap page-table allocation, PTI on/off, Xen PV or other paravirt page-table tracking, THP/PUD/P4D allocation/free, TLB gather teardown, and debug page-table checks.
