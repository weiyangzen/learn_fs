## sources/distributed-fs/ceph-client/mm/ioremap.c

Purpose: provides generic helpers for mapping physical IO memory into kernel virtual address space and unmapping it again.

Important APIs and functions: `generic_ioremap_prot()` allocates a VM area and maps physical pages with a supplied page protection. Weak-style wrappers `ioremap_prot()` and `iounmap()` are exported when not overridden by architecture macros. `generic_iounmap()` unmaps addresses inside the ioremap range.

Control flow: `generic_ioremap_prot()` rejects use before slab availability, rejects zero-size and physical wraparound, folds the physical page offset into the returned virtual address, page-aligns the mapping, obtains a `VM_IOREMAP` area within `IOREMAP_START..IOREMAP_END`, records `area->phys_addr`, and calls `ioremap_page_range()`. On mapping failure it frees the area. Unmap masks the supplied pointer down to the page base and calls `vunmap()` only if `is_ioremap_addr()` accepts it.

State and persistence: mapped state lives in vmalloc metadata (`struct vm_struct`) and kernel page tables until `iounmap()` removes it. No persistent storage exists.

Dependencies and integration: integrates with vmalloc area management, architecture page protections, IO memory mapping ranges, and exported driver-facing ioremap APIs.

Risks and test signals: risks include early-driver calls before slab, address overflow, leaking VM areas on failure, incorrect offset restoration, and arch-specific cacheability/protection mismatches. Tests should cover unaligned physical starts, zero and wrapping sizes, forced `ioremap_page_range()` failure, valid unmap, and arch override builds.
