## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fixmap.h

Purpose: defines PowerPC compile-time fixed virtual address slots and the architecture implementation of `__set_fixmap()`.

Important APIs/types/functions: `enum fixed_addresses`, early debug slots, highmem kmap slots, 8xx/83xx IMMR slots, boot-time bitmap slots, `FIXADDR_START`, `FIXMAP_PTE_SIZE`, `FIXMAP_PAGE_NOCACHE`, `FIXMAP_PAGE_IO`, `__set_fixmap()`, `__early_set_fixmap`, and `VIRT_IMMR_BASE`.

Control flow: `__set_fixmap()` validates the index at compile time or runtime, maps the physical address with `map_kernel_page()` when `flags` is nonzero, otherwise unmaps the fixed virtual address.

State and persistence: fixed mappings persist in kernel page tables until changed. Highmem and boot mappings use reserved ranges below `FIXADDR_TOP`.

Dependencies and integration: depends on page table APIs, generic fixmap, highmem, kmap sizing, and platform IMMR requirements for 8xx/83xx.

Risks and test signals: index arithmetic must avoid overlap with vmalloc and satisfy PPC64 size limits. Wrong IMMR alignment breaks early platform register access. Test signals include early ioremap/fixmap use, highmem kmap tests, 8xx/83xx boot, map/unmap assertions, and PPC64 `BUILD_BUG_ON` coverage.
