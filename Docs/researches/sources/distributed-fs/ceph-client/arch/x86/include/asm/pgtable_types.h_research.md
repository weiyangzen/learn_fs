# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_types.h

Purpose: defines the common x86 page-table bit layout, protection constants, cache-mode encodings, page-table entry value wrappers, flag masks, table-level geometry includes, and kernel mapping helper declarations.

Important APIs, types, and functions: constants cover hardware bits (`_PAGE_PRESENT`, `_PAGE_RW`, `_PAGE_USER`, PWT/PCD/A/D/PSE/PAT/GLOBAL/NX), software bits (special, CPA test, UFFD-WP, soft-dirty, kernel-4K, saved-dirty, no-PTI-shadow), pkeys, PROT_NONE, cache modes, encryption/confidential-computing bits, user and kernel `PAGE_*` protections, identity mapping attributes, PFN/flags masks, `PGD_ALLOWED_BITS`, and `enum pg_level`. Types and helpers include `pgprot_t`, `pgd_t`, folded or real `p4d_t/pud_t/pmd_t`, `pte_t`, native make/value helpers, pfn/flag mask helpers, PAT conversion helpers, `pgtable_t`, supported/default PTE masks, `pgprot_writecombine()`, `pgprot_writethrough()`, `phys_mem_access_prot()`, `set_pte_vaddr()`, `native_pagetable_init`, page-count updating, lookup helpers, `slow_virt_to_phys()`, and kernel map/unmap helpers.

Control flow: mostly compile-time flag composition and inline value extraction. Cache-mode conversion maps software cache modes to PTE PAT/PWT/PCD bits. PAE masks top-level PGD values to architecturally allowed bits.

State and persistence: declares global supported/default PTE masks and page-count accounting. Entry values persist only in page tables.

Dependencies and integration points: depends on page masks, memory encryption, CoCo mask helpers, 32/64 page-table type headers, PAT/memtype, procfs page counts, and generic MM.

Risks: bit assignments are central ABI. Conflicts among soft-dirty, UFFD-WP, pkeys, saved dirty, PTI shadow bits, and swap encodings can corrupt memory semantics. Kernel protection constants control W^X, encryption, and cacheability.

Test signals: page protection selftests, PAT/cache-mode tests, pkeys, soft-dirty, uffd-wp, shadow stack write-protect behavior, SME/CoCo encrypted/decrypted mappings, `/proc` page counts, kernel address lookup, and PAE top-level reserved-bit validation.
