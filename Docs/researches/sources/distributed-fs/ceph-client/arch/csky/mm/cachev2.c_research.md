# sources/distributed-fs/ceph-client/arch/csky/mm/cachev2.c

Purpose: newer C-SKY cache maintenance and SMP range flushing.

Important APIs/types/functions: functions: `local_icache_inv_all`, `icache_inv_range`, `cache_op_line`, `local_icache_inv_range`, `dcache_wb_line`, `dcache_wb_range`, `cache_wbinv_range`, `dma_wbinv_range`, `dma_inv_range`, `dma_wb_range`; types: `cache_range`; macros: `INS_CACHE`, `DATA_CACHE`, `CACHE_INV`, `CACHE_CLR`, `CACHE_OMS`; exports: `cache_wbinv_range`

Control flow: Runtime flow is organized around `local_icache_inv_all`, `icache_inv_range`, `cache_op_line`, `local_icache_inv_range`, `dcache_wb_line`, `dcache_wb_range`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/spinlock.h`, `linux/smp.h`, `linux/mm.h`, `asm/cache.h`, `asm/barrier.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
