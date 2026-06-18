# sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h` defines SPARC64 page and hugepage sizes, page-table scalar types, cache alias indicators, user address-hole policy, and virtual/physical conversion helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 161 lines, 4710 bytes. Primary surface: `HPAGE_*`, `REAL_HPAGE_*`, `HUGE_MAX_HSTATE`, `_clear_page`, `clear/copy_user_page`, `copy_highpage`, `pte_t/iopte_t/pmd_t/pud_t/pgd_t/pgprot_t`, `sparc64_va_hole_*`, `TASK_UNMAPPED_BASE`, `MAX_PHYS_ADDRESS_BITS`, `__pa`, `__va`, and `virt_addr_valid`. Symbol scan highlights: `_SPARC64_PAGE_H`, `DCACHE_ALIASING_POSSIBLE`, `HPAGE_SHIFT`, `REAL_HPAGE_SHIFT`, `HPAGE_16GB_SHIFT`, `HPAGE_2GB_SHIFT`, `HPAGE_256MB_SHIFT`, `HPAGE_64K_SHIFT`, `REAL_HPAGE_SIZE`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `HAVE_ARCH_HUGETLB_UNMAPPED_AREA`, `REAL_HPAGE_PER_HPAGE`, `HUGE_MAX_HSTATE`, `struct pt_regs`, `hugetlb_setup`, `WANT_PAGE_VIRTUAL`, `_clear_page`, `clear_page`, `struct page`, `clear_user_page`, `copy_page`, `copy_user_page`, and 31 more.

### Control Flow
MM code selects mmap bases around the VA hole, uses strict page-table wrapper types, handles hugepage sizing, and translates direct-map addresses through `PAGE_OFFSET`. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`PAGE_OFFSET` and VA-hole globals persist for the booted layout; page table objects persist in MM structures. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/const.h>`, `<vdso/page.h>`, `<asm-generic/memory_model.h>`, `<asm-generic/getorder.h>`. Integration dependencies: `linux/const.h`, `vdso/page.h`, generic memory model, hugepage/THP code, and SPARC64 cache/TLB code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
VA-hole bounds and hugepage shifts are ABI-sensitive; bad `__pa/__va` conversions break page allocator, DMA, and kernel direct map.

### Test Signals
SPARC64 boot, mmap layout tests for 32-bit and 64-bit tasks, hugetlb/THP tests, and virt/phys conversion sanity checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
