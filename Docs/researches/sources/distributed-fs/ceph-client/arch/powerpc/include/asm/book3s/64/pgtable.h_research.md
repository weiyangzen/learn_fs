# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable.h

Purpose: defines the common Book3S64 Linux page-table format and dispatch layer for hash and radix MMUs, including PTE/PMD/PUD/P4D accessors, permission bits, virtual layout, swap encoding, cache attributes, hugepage helpers, and kernel mapping wrappers.

Important APIs/types/functions: key macros include `_PAGE_EXEC/WRITE/READ/PRIVILEGED`, `_PAGE_PRESENT`, `_PAGE_PTE`, `_PAGE_INVALID`, pkey/software bits, `PTE_RPN_MASK`, `PAGE_KERNEL*`, dynamic index/table-size globals, `VMALLOC_*`, IO layout, and swap encoders. Functions include `pte_update()`, `ptep_test_and_clear_young()`, `ptep_get_and_clear()`, `pte_clear()`, PTE accessors/modifiers, `pfn_pte()`, `check_pte_access()`, `__ptep_set_access_flags()`, `pte_same()`, `pte_none()`, `__set_pte_at()`, pgprot helpers, PMD/PUD/P4D accessors, `map_kernel_page()`, vmemmap mapping wrappers, hugepage update/get/clear/deposit/withdraw functions, and protection modification transactions.

Control flow: many helpers branch on `radix_enabled()` to call radix or hash implementations. PTE updates preserve hash HPTE flags where needed, radix can optimize full clears, and hugepage helpers route PMD/PUD operations to the active MMU. Access checks require present, user, read, optional write, and optional pkey permission.

State and persistence: page-table entries persist per mapping and encode hardware and Linux software state. Dynamic globals define table geometry and virtual regions for the boot mode. Hash mode also stores HPTE tracking bits in PTE fields.

Dependencies and integration points: includes generic folded P4D support, page-table checks, barrier, hash/radix headers, pkeys, THP, hugetlb, KASAN/fixmap/io mapping, vmemmap, and memory hotplug.

Risks: this is a high-blast-radius header. Hash/radix bit sharing must remain compatible; `_PAGE_PTE` distinguishes leafs from pointers; `_PAGE_INVALID` serializes THP splits. Soft-dirty and swap bits must not collide with HPTE flags. Missing TLB/HPTE flushes can leave stale translations.

Test signals: full mm selftests, `mprotect`, swap, soft-dirty, pkeys, THP split/collapse/migration, hugetlb, memory hotplug, vmemmap, ioremap, and both hash/radix 4K/64K build-and-boot matrices.
