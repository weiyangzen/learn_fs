# sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_32.c

Purpose: implements 32-bit PowerPC `__ioremap_caller()` and `iounmap()`, including ISA address adjustment and early top-down ioremap allocation.

Important APIs and control flow: addresses below 16 MiB are treated as ISA memory and adjusted by `_ISA_MEM_BASE`. The mapping is page-aligned, normal RAM is rejected after slab/high_memory are available, existing BAT/LTLB/CAM block mappings are reused via `p_block_mapped()`, late mappings use `generic_ioremap_prot()`, and early mappings allocate downward from `ioremap_bot` through `early_ioremap_range()`. `iounmap()` ignores block-mapped addresses and otherwise calls `generic_iounmap()`.

State and dependencies: relies on `ioremap_bot`, high_memory, `page_is_ram()`, block mapping lookups from subarch MMU code, and vmalloc availability. Risks are accidentally remapping RAM as device memory, early mappings colliding with reserved ioremap space, incorrect ISA offset assumptions, and leaving early mappings permanent. Test signals include 32-bit PCI/ISA MMIO drivers, crash dump RAM remap exceptions, BAT/CAM reuse checks, and early boot warning coverage.
