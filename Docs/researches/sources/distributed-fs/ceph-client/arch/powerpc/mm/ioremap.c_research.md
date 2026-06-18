# sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap.c

Purpose: provides architecture-generic PowerPC ioremap entry points and early page-by-page kernel mapping support shared by 32-bit and 64-bit implementations.

Important APIs and control flow: `ioremap()`, `ioremap_wc()`, `ioremap_coherent()`, and `ioremap_prot()` select cacheability protections and call `__ioremap_caller()`. `ioremap_prot()` marks writable kernel mappings dirty before mapping. `early_ioremap_range()` maps a physical range at a requested effective address using `map_kernel_page()` with NX protection.

State and dependencies: `ioremap_bot` tracks the early allocator frontier and is exported. The file depends on pgprot cacheability helpers, caller-address capture, `map_kernel_page()`, and platform-specific `__ioremap_caller()` definitions. Risks include wrong cache attributes for device memory, executable early I/O mappings if NX wrapping is broken, and early allocator overlap if `ioremap_bot` is misinitialized by arch init. Test signals include driver MMIO mappings, write-combining mappings, early console/boot ioremap users, and page-table attribute inspection.
