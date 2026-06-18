# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-64k.h

Purpose: defines 64-bit Book3S hash MMU page-table geometry and subpage/HPTE metadata for 64 KiB base-page kernels.

Important APIs/types/functions: defines 64K hash index sizes, physical/EA limits, kernel map ranges, combo and 4K-PFN flags, HPTE slot encodings, fragment sizes, pkey bit mapping, real-PTE composition, hashed-subpage iteration, `pte_pagesize_index()`, `pte_set_hidx()`, and hash THP helper declarations.

Control flow: helpers track multiple 4K hardware subpages inside a 64K Linux PTE when needed, including combo-page and hash-slot metadata. Iteration walks valid hashed subpages and passes index/shift to hash code.

State and persistence: PTE bits and companion slot arrays store subpage HPTE placement. Kernel virtual layout constants persist for the boot configuration.

Dependencies and integration points: used by hash fault, hugepage, and page-table code under `CONFIG_PPC_64K_PAGES`. It integrates with protection keys and subpage hash handling.

Risks: bit overloading is dense; RPN, pkey, combo, and HPTE metadata must not conflict. Cache-inhibited mapping restrictions can demote processes to 4K subpages. THP hash slot arrays must be kept in sync with HPTE invalidation.

Test signals: 64K hash boot, subpage protection tests, cache-inhibited user mappings, THP hash tests if enabled, hugepage mapping/unmapping, and pkey tests on hash MMU.
