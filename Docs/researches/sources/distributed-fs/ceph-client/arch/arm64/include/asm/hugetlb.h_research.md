## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hugetlb.h

Purpose: provides arm64 hugepage page-table helpers.

Important APIs/types/functions: declares and defines huge PTE operations for hugepage lookup, clear, set, migration/special handling, contiguous PTE support, and architecture hooks used by hugetlbfs.

Control flow: memory-management code manipulates huge PTEs through these helpers, handling contiguous mappings and break-before-make requirements implemented in MM code.

State and persistence: modifies page tables and hugepage mapping metadata.

Dependencies and integration: depends on pgtable definitions, hugetlbfs, THP-adjacent page-table code, TLB invalidation, and mmu-gather paths.

Risks: hugepage PTE mistakes corrupt address spaces or violate arm64 TLB rules. Test signals are hugetlbfs tests, libhugetlbfs, mmap/mprotect/munmap stress, migration tests, and page-table debug.
