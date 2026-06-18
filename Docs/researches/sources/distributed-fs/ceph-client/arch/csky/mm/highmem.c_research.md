# sources/distributed-fs/ceph-client/arch/csky/mm/highmem.c

Purpose: highmem/fixmap cache and TLB maintenance.

Important APIs/types/functions: functions: `kmap_flush_tlb`, `kmap_init`; exports: `kmap_flush_tlb`

Control flow: Runtime flow is organized around `kmap_flush_tlb`, `kmap_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/module.h`, `linux/highmem.h`, `linux/smp.h`, `linux/memblock.h`, `asm/fixmap.h`, `asm/tlbflush.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
