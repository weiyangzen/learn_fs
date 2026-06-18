<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/page.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/page.h

**Purpose:** Defines Alpha page primitives, strict page-table wrapper types, the kernel direct-map offset, and virtual/physical translation helpers. It anchors the architecture's 8 KiB page assumptions through `vdso/page.h`.

**Important APIs/types/functions:** `clear_page`, `copy_page`, `copy_user_page`, `pte_t`, `pmd_t`, `pgd_t`, `pgprot_t`, `pgtable_t`, `PAGE_OFFSET`, `__pa`, `__va`, `virt_to_page`, and `virt_addr_valid`.

**Control flow:** Most behavior is macro expansion. Callers convert between kernel virtual and physical addresses by adding/subtracting `PAGE_OFFSET`; copy/clear operations delegate to assembly routines.

**State and persistence behavior:** The file stores no mutable state. Its constants define address interpretation for every memory-management user, core-file helper, boot layout, and page-table routine.

**Dependencies and integration points:** Depends on `asm/pal.h`, `vdso/page.h`, generic memory model helpers, and Linux page allocator interfaces.

**Risks:** Wrong `PAGE_OFFSET` selection for 48-bit KSEG versus legacy layouts corrupts all address translation. Strict type wrappers catch some PTE/PMD/PGD mixups, while non-strict builds lose that safety.

**Test signals:** Compile with and without strict MM type checks, boot kernels using both KSEG choices, and run page allocator, high-memory, and virt-to-phys validation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/page.h -->
