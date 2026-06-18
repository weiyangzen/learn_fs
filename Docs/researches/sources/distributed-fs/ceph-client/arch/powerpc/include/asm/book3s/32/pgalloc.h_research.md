# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgalloc.h

Purpose: provides 32-bit Book3S page-table allocation and free helpers for the two-level Linux page table layout used over the hash MMU.

Important APIs/types/functions: implements `pgd_alloc()`, `pgd_free()`, `pmd_populate_kernel()`, `pmd_populate()`, `pgtable_free()`, `pgtable_free_tlb()`, `__tlb_remove_table()`, and `__pte_free_tlb()`. PMD freeing is a no-op because this configuration has no real PMD level.

Control flow: `pgd_alloc()` allocates from `PGT_CACHE(PGD_INDEX_SIZE)` and copies kernel mappings from `swapper_pg_dir` on 603. Free paths either free PTE fragments or cache-backed tables, with TLB-delayed removal encoding the table shift in low bits.

State and persistence: allocated page-table pages/fragments are owned by an `mm_struct` until freed through direct or TLB-deferred paths.

Dependencies and integration points: depends on slab, thread counts, `PGT_CACHE`, `pgtable_gfp_flags`, fragment allocators, and mmu_gather table removal.

Risks: low-bit shift encoding in `pgtable_free_tlb()` depends on alignment. Incorrect 603 kernel mapping copy would corrupt kernel/user split. No-op PMD frees rely on the folded PMD model remaining true.

Test signals: process creation/exit stress, fork/exec under 603 configs, memory reclaim with page-table freeing, and debug builds checking `BUG_ON(index_size > MAX_PGTABLE_INDEX_SIZE)`.
