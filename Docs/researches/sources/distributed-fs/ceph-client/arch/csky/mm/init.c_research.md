# sources/distributed-fs/ceph-client/arch/csky/mm/init.c

Purpose: physical memory, paging, zones, memblock handoff, and init-memory release.

Important APIs/types/functions: functions: `free_initmem`, `pgd_init`, `mmu_init`, `fixrange_init`, `fixaddr_init`; macros: `PTRS_KERN_TABLE`; exports: `invalid_pte_table`

Control flow: Runtime flow is organized around `free_initmem`, `pgd_init`, `mmu_init`, `fixrange_init`, `fixaddr_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/bug.h`, `linux/module.h`, `linux/init.h`, `linux/signal.h`, `linux/sched.h`, `linux/kernel.h`, `linux/errno.h`, `linux/string.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
