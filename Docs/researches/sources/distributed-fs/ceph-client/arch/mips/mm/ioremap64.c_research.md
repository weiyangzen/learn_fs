# sources/distributed-fs/ceph-client/arch/mips/mm/ioremap64.c

Purpose: simplified 64-bit MIPS `ioremap_prot()`/`iounmap()` implementation using direct uncached or I/O base address translation unless a platform hook handles the mapping.

Important APIs/functions: `ioremap_prot(phys_addr_t offset, unsigned long size, pgprot_t prot)` chooses `IO_BASE` for uncached mappings and `UNCAC_BASE` otherwise, after trying `plat_ioremap()`. `iounmap()` only calls `plat_iounmap()`. Both are exported.

Control flow: no range validation or vmalloc page table mapping is performed here; the returned pointer is base plus physical offset when platform code does not override.

State and persistence: no global state and no generic mapping allocation.

Dependencies and integration: selected under `CONFIG_64BIT`; depends on MIPS direct map layout, platform ioremap hooks, and cache attribute bits.

Risks and test signals: correctness depends on 64-bit address-space layout and platform hook coverage. Test uncached versus cached attributes, high physical offsets, platform override/unmap behavior, and drivers expecting `iounmap()` to be a no-op for direct mappings.
