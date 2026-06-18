# sources/distributed-fs/ceph-client/arch/csky/mm/dma-mapping.c

Purpose: DMA cache synchronization for pages and scatterlists.

Important APIs/types/functions: functions: `cache_op`, `dma_wbinv_set_zero_range`, `arch_dma_prep_coherent`, `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`; types: `page`, `dma_data_direction`

Control flow: Runtime flow is organized around `cache_op`, `dma_wbinv_set_zero_range`, `arch_dma_prep_coherent`, `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/cache.h`, `linux/dma-map-ops.h`, `linux/genalloc.h`, `linux/highmem.h`, `linux/io.h`, `linux/mm.h`, `linux/scatterlist.h`, `linux/types.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
