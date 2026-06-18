# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_types.h

Purpose: provides common x86 page constants shared by 32-bit and 64-bit builds, including physical/virtual masks, huge-page sizes, page offset, kernel load address, ioremap maximum order, and architecture hooks for memory initialization and mapped PFN queries.

Important APIs, types, and functions: defines `__VIRTUAL_MASK`, `PHYSICAL_PAGE_MASK`, `PHYSICAL_PMD_PAGE_MASK`, `PHYSICAL_PUD_PAGE_MASK`, `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `HUGE_MAX_HSTATE`, `PAGE_OFFSET`, `LOAD_PHYSICAL_ADDR`, and `__START_KERNEL`. C-visible exports include `physical_mask` when dynamic, `devmem_is_allowed()`, `max_low_pfn_mapped`, `max_pfn_mapped`, `get_max_mapped()`, `pfn_range_is_mapped()`, and `initmem_init()`.

Control flow: compile-time architecture selection includes either `page_64_types.h` or `page_32_types.h`, and sets `IOREMAP_MAX_ORDER` to PUD or PMD scale. `get_max_mapped()` derives bytes from `max_pfn_mapped`.

State and persistence: state is external memory-map state initialized by boot code. No persistent storage is touched.

Dependencies and integration points: depends on generic page constants, `mem_encrypt.h`, vDSO page constants, `CONFIG_DYNAMIC_PHYSICAL_MASK`, and architecture-specific page type headers. It feeds devmem access checks, direct-map setup, ioremap, huge page definitions, and memory initialization.

Risks: mask calculations must handle 32-bit PAE sign-extension, SME/CoCo encryption masks, and dynamic physical address widths. Incorrect `LOAD_PHYSICAL_ADDR` or `__START_KERNEL` breaks decompressor/kernel relocation assumptions.

Test signals: build 32/64-bit, PAE, SME/SEV, and dynamic physical mask configurations; validate `/dev/mem` filtering, direct-map range detection, hugepage mapping attributes, boot-time memory initialization, and ioremap with large-order mappings.
