# sources/distributed-fs/ceph-client/arch/s390/include/asm/pgtable.h

Purpose: This is the central s390 page-table header, defining page/segment/region entry encodings, ASCE layout, protection modes, folded table levels, PTE/PMD/PUD manipulation, TLB invalidation instruction wrappers, huge/THP support, swap encodings, vmem mapping hooks, and protected-guest page teardown behavior.

Important APIs/types/functions: It exports kernel page-table globals, direct-map counters, ZERO_PAGE selection, vmalloc/module/KMSAN layout, all hardware/software PTE/RSTE bit definitions, page protection constants, folding predicates, protected-mm and zeropage policy helpers, `cspg()`/`crdte()`, present/none/bad/leaf/query helpers, pte/pmd/pud modify and dirty/young/write helpers, IPTE/IDTE/RDP assembly helpers, `ptep_xchg_*`/`pmdp_xchg_*` declarations, access-flag and clear/flush overrides, THP helpers, swap-entry conversion helpers, vmem map functions, and unmapped-area declarations.

Control flow: Fault and mapping code construct entries from physical pages and protections, update entries with direct or lazy exchange helpers that also perform required TLB invalidation, use RDP for allowed read-only-to-writable protection resets, clear protected secure pages through UV conversion/destroy hooks, and traverse folded 3/4/5-level tables through lockless offset helpers.

State and persistence: Persistent state is every s390 page table, ASCE, direct-map accounting counter, no-execute mask, module/vmalloc layout value, and secure/protected page ownership. Swap entries encode type/offset differently for PTEs and RSTE huge entries, requiring conversion shims.

Dependencies and integration points: It depends on scheduler/MM types, CPU feature checks, page-table check, radix tree, mmap locks, control registers, UV protected-virtualization APIs, `page.h`, `mmu.h`, TLB flush code, hugepage/THP configs, NUMA balancing, soft-dirty, KMSAN, and KVM protected guest state.

Risks and test signals: This is high-risk MM code: bit patterns define present/none/swap semantics used locklessly, and TLB invalidation must happen at modification time on s390. Tests should include page fault/mprotect/munmap stress, fork/exit, GUP-fast bounds, THP and hugetlb, soft-dirty and swap, NUMA balancing, KMSAN vmalloc layout, protected guest memory conversion, page_table_check, and direct-map vmem add/remove.
