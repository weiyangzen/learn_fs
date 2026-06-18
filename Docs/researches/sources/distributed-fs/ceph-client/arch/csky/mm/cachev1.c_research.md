# sources/distributed-fs/ceph-client/arch/csky/mm/cachev1.c

Purpose: first-generation C-SKY cache maintenance through cache control registers.

Important APIs/types/functions: functions: `cache_op_line`, `cache_op_all`, `cache_op_range`, `dcache_wb_line`, `icache_inv_range`, `icache_inv_all`, `local_icache_inv_all`, `dcache_wb_range`, `dcache_wbinv_all`, `cache_wbinv_range`, `cache_wbinv_all`, `dma_wbinv_range`, `dma_inv_range`, `dma_wb_range`; macros: `INS_CACHE`, `DATA_CACHE`, `CACHE_INV`, `CACHE_CLR`, `CACHE_OMS`, `CACHE_ITS`, `CACHE_LICF`, `CR22_LEVEL_SHIFT`, `CR22_SET_SHIFT`, `CR22_WAY_SHIFT`, `CR22_WAY_SHIFT_L2`, `CCR2_L2E`; exports: `cache_wbinv_range`

Control flow: Runtime flow is organized around `cache_op_line`, `cache_op_all`, `cache_op_range`, `dcache_wb_line`, `icache_inv_range`, `icache_inv_all`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/spinlock.h`, `asm/cache.h`, `abi/reg_ops.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
