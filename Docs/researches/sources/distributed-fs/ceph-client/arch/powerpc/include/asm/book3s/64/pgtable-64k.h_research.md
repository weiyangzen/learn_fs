# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable-64k.h

Purpose: provides 64 KiB page-size-specific Book3S64 page-table definitions included by the common pgtable header.

Important APIs/types/functions: bridges the common Book3S64 PTE layout with 64K-specific hash/radix fragment and index definitions selected in lower headers.

Control flow: declarative include-time configuration only.

State and persistence: no private state. It affects compile-time page-table layout and runtime table sizes through macros/globals initialized elsewhere.

Dependencies and integration points: only used under `CONFIG_PPC_64K_PAGES`; integrates with hash-64K, radix-64K, pgalloc, hugetlb, and vmemmap layout.

Risks: 64K page configurations have different PTE fragment sizes and subpage hash behavior. A mismatch with hash/radix geometry would corrupt page-table walks.

Test signals: 64K hash and radix boots, page fault/mprotect tests, hugepage tests, and page-table allocation/free stress.
