# sources/distributed-fs/ceph-client/arch/s390/include/asm/page.h

Purpose: This header defines core s390 page constants, hugepage geometry, storage-key helpers, page copy/clear, strict MM type wrappers, physical/virtual translation, KASLR identity mapping, and architecture page allocation hooks.

Important APIs/types/functions: Important definitions include page access-key constants, `HPAGE_*`, hugepage capability macros, `storage_key_init_range()`, `copy_page()`, `pgprot_t/pte_t/pmd_t/pud_t/p4d_t/pgd_t` wrappers and value constructors, `page_set_storage_key()`, `page_get_storage_key()`, `page_reset_referenced()`, `split_pud_page()`, arch page alloc/free hooks, `arch_make_folio_accessible()`, `struct vm_layout`, `kaslr_offset()`, `kaslr_enabled()`, `__pa/__pa32/__va`, PFN/page conversion helpers, `AMODE31_SIZE`, kernel image bounds, and `TEXT_OFFSET`.

Control flow: Memory-management code uses these constants and helpers to create page-table entries, copy or clear pages, manipulate storage keys with SSKE/ISKE/RRBE instructions, translate addresses according to identity/KASLR layout, and validate direct-map addresses.

State and persistence: Persistent state includes storage keys on real pages and global `vm_layout`/KASLR fields. The type wrappers affect compile-time type safety rather than runtime state.

Dependencies and integration points: It depends on VDSO page size definitions, setup/KASLR data, generic memory model/getorder, and s390 storage-key instructions. It feeds nearly every MM, KVM, kexec, and I/O mapping header in this subset.

Risks and test signals: Address translation and storage-key mistakes are system-wide failures. Tests should include boot with/without KASLR and randomized identity base, storage-key operations, hugepage allocation, debug-virtual checks, page copy correctness, and protected/accessible folio paths.
