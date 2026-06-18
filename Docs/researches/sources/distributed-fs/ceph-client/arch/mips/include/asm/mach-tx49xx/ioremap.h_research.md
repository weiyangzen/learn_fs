# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/ioremap.h

Purpose: TX49xx platform hook for direct-mapping a small high physical address window instead of allocating a normal `ioremap` mapping.

Important APIs/types/functions: `plat_ioremap(offset, size, flags)` returns the direct-cast I/O pointer when `offset` falls inside `[TXX9_DIRECTMAP_BASE, TXX9_DIRECTMAP_BASE + 0x400000)`, with the base set to `0xfff000000ul` on 64-bit and `0xff000000ul` on 32-bit. `plat_iounmap(addr)` returns true for addresses in the direct-mapped region.

Control flow, state, and persistence: The functions are stateless. Control flow is a range check followed by either a cast or `NULL`, letting generic `ioremap` continue when the platform hook does not claim the address.

Dependencies and integration: Uses `phys_addr_t`, `__iomem`, and the MIPS `ioremap` platform hook mechanism. It aligns with TX49xx physical memory maps and fixed `FIXADDR_TOP` from `spaces.h`.

Risks and test signals: The `(unsigned long)(int)` casts intentionally preserve 32-bit direct-map forms but are easy to break during cleanup. Test by booting TX49xx, mapping board registers in the direct region, and ensuring `iounmap` does not free direct mappings.
