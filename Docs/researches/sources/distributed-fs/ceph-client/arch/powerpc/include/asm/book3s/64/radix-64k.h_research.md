# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-64k.h

Purpose: defines radix page-table index and fragment geometry for Book3S64 kernels using 64 KiB base pages.

Important APIs/types/functions: sets 64K-specific `RADIX_PTE_INDEX_SIZE`, `RADIX_PMD_INDEX_SIZE`, `RADIX_PUD_INDEX_SIZE`, `RADIX_PGD_INDEX_SIZE`, `RADIX_PTE_FRAG_SIZE_SHIFT/NR`, and `RADIX_PMD_FRAG_SIZE_SHIFT/NR`.

Control flow: compile-time constants only.

State and persistence: no state beyond generated table geometry.

Dependencies and integration points: selected by `radix.h` under `CONFIG_PPC_64K_PAGES`; used by pgtable, pgalloc, process table setup, and vmemmap sizing.

Risks: 64K radix uses 256-byte PTE fragments. Fragment accounting and hardware walk geometry must match these constants exactly.

Test signals: 64K radix boot, page-table fragment stress, THP/hugetlb coverage, and memory hotplug/vmemmap tests.
