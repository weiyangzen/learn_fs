# sources/distributed-fs/ceph-client/arch/csky/mm/tcm.c

Purpose: tightly-coupled memory discovery, reservation, and setup.

Important APIs/types/functions: functions: `tcm_mapping_init`, `tcm_alloc`, `tcm_free`, `tcm_setup_pool`, `tcm_init`; exports: `tcm_alloc`, `tcm_free`

Control flow: Runtime flow is organized around `tcm_mapping_init`, `tcm_alloc`, `tcm_free`, `tcm_setup_pool`, `tcm_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/highmem.h`, `linux/genalloc.h`, `asm/tlbflush.h`, `asm/fixmap.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
