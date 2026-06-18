# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-4k.h

Purpose: defines 64-bit Book3S hash MMU geometry and PTE/HPTE metadata for 4 KiB base-page kernels.

Important APIs/types/functions: defines hash index sizes, kernel virtual range constants, `H_MAX_PHYSMEM_BITS`, HPTE flag bits (`H_PAGE_F_SECOND`, `H_PAGE_F_GIX`, `H_PAGE_BUSY`, `H_PAGE_HASHPTE`), fragment sizes, pkey bit mappings, `remap_4k_pfn`, real-PTE helpers, `pte_iterate_hashed_subpages`, `pte_pagesize_index`, and THP stubs/externs.

Control flow: 4K real-PTE handling is mostly pass-through: one PTE maps one hashed subpage, iteration emits a single body, and `pte_set_hidx()` computes the hash slot bits to store. THP hash helpers mostly BUG or return unsupported for 4K hash.

State and persistence: state is encoded in PTE bits that remember HPTE slot/index metadata. No standalone state exists here.

Dependencies and integration points: included through 64-bit hash/radix page-table headers. It integrates hash fault insertion/removal with Linux PTE storage for 4K pages.

Risks: 4K hash lacks THP and combo-page support, so callers must not assume 64K behavior. HPTE slot bits are overloaded into pkey/RPN-reserved fields and must not collide with generic PTE bits.

Test signals: boot 4K-page hash kernels, run page fault/unmap/mprotect tests, verify no THP exposure in hash-4K mode, and inspect HPTE insertion/removal paths for correct slot tracking.
