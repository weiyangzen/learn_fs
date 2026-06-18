# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-4k.h

Purpose: defines radix page-table index and fragment geometry for Book3S64 kernels using 4 KiB base pages.

Important APIs/types/functions: sets `RADIX_PTE_INDEX_SIZE`, `RADIX_PMD_INDEX_SIZE`, `RADIX_PUD_INDEX_SIZE`, `RADIX_PGD_INDEX_SIZE`, `RADIX_PTE_FRAG_SIZE_SHIFT`, `RADIX_PTE_FRAG_NR`, `RADIX_PMD_FRAG_SIZE_SHIFT`, and `RADIX_PMD_FRAG_NR`.

Control flow: declarative compile-time configuration only.

State and persistence: no private state. These constants determine runtime page-table sizes and address coverage.

Dependencies and integration points: included by `radix.h` when `CONFIG_PPC_64K_PAGES` is not set. It feeds pgtable geometry, pgalloc, and radix walk setup.

Risks: index sizes define a 4PB range with 64KB PGD pages; wrong values break hardware radix walks and allocation sizes.

Test signals: 4K radix boot, page-table allocation/free tests, mmap/fault coverage across high addresses, and process table root-size validation.
