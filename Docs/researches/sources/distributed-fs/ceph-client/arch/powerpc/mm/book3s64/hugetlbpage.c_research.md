# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hugetlbpage.c

Purpose: Implements hugeTLB support shared by Book3S64 hash/radix, with hash-specific HPTE insertion for explicit hugetlb mappings and common protection-change helpers.

Important APIs and functions: `__hash_page_huge()` hashes hugetlb PTEs when `CONFIG_PPC_64S_HASH_MMU` is enabled. `huge_ptep_modify_prot_start()` temporarily invalidates a huge PTE during protection changes. `huge_ptep_modify_prot_commit()` routes commit to radix or hash handling. `hugetlbpage_init_defaultsize()` selects the default large page size. Global `hpage_shift` is exported.

Control flow: `__hash_page_huge()` computes VPN, atomically sets `H_PAGE_BUSY`, accessed, and dirty bits, rejects THP PMDs, converts PTE flags to HPTE flags, derives the `real_pte_t` span (`PTRS_PER_PUD` for 16G, otherwise `PTRS_PER_PMD`), optionally applies lazy icache handling, updates an existing HPTE if present, or inserts a new repeating HPTE and stores slot metadata. Protection start clears `_PAGE_PRESENT` while preserving software present semantics via `_PAGE_INVALID`. Commit uses radix-specific flushing if radix is enabled, otherwise writes the huge PTE directly. Default size prefers 16M, then 1M, then 2M based on populated page-size definitions.

State and persistence: State is in hugetlb PTE flags, hash slot indexes, and exported `hpage_shift`. The protection-change window relies on the invalid-but-present PTE convention.

Dependencies and integration: Called from `hash_page_mm()` for non-THP huge mappings. Uses `htab_convert_pte_flags()`, `hash_page_do_lazy_icache()`, `hpte_insert_repeating()`, `pte_set_hidx()`, radix hugetlb commit helpers, and generic hugetlb hstate helpers.

Risks: 4K kernels bail out for young/dirty software management because hugepages span multiple contiguous upper-level entries. Hugepage shift must match `mmu_psize_defs[mmu_psize].shift` or `BUG_ON()` fires. Failed insertion restores the old PTE and propagates an error to the fault handler.

Test signals: Explicit hugeTLB faults for 16M/16G/1M/2M availability, mprotect on hugetlb VMAs, hash versus radix boot modes, and no-execute/lazy icache instruction faults provide coverage.
