# sources/distributed-fs/ceph-client/arch/mips/mm/ioremap.c

Purpose: 32-bit MIPS `ioremap_prot()`/`iounmap()` implementation for mapping physical I/O resources into kernel virtual address space.

Important APIs/functions: `ioremap_prot(phys_addr_t phys_addr, unsigned long size, pgprot_t prot)` supports platform overrides, big-phys fixups, low-512MB KSEG1 uncached shortcut, RAM remap rejection, vmalloc area allocation, and `ioremap_page_range()`. `iounmap()` delegates to platform unmap or vunmaps non-KSEG1 mappings.

Control flow: validates size/wraparound, uses KSEG1 for low uncached ranges, rejects early calls before slab, walks system RAM to avoid remapping allocatable RAM, aligns physical/virtual range, allocates `VM_IOREMAP`, maps pages with global/present/read/write cache flags, and returns offset-adjusted pointer.

State and persistence: creates/removes vmalloc mappings. No file-global state.

Dependencies and integration: depends on platform hooks, `fixup_bigphys_addr`, vmalloc, resource/RAM walking, cache attributes, and TLB/cache flush infrastructure.

Risks and test signals: test wraparound, zero size, RAM rejection, KSEG1 fast path, platform override paths, unaligned resources, and iounmap of platform/KSEG1/vmalloc mappings.
