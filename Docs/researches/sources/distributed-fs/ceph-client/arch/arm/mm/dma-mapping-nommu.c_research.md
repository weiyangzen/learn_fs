## sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping-nommu.c

### Purpose
Implements minimal ARM DMA cache synchronization and coherency setup for NOMMU/MPU style builds.

### Important APIs, Types, And Functions
Key exported architecture hooks are `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`, and `arch_setup_dma_ops`. They use `dmac_map_area`, `dmac_unmap_area`, `outer_inv_range`, `outer_clean_range`, `cacheid`, and `get_cr()`.

### Control Flow
Device sync always performs inner-cache map maintenance and then invalidates outer cache for `DMA_FROM_DEVICE` or cleans it for other directions. CPU sync invalidates outer and inner caches for incoming or bidirectional DMA, skipping pure `DMA_TO_DEVICE`. DMA setup marks devices coherent when v7-M has no detected cache or when MMU/MPU is off; otherwise it follows the supplied firmware/bus coherency value.

### State, Dependencies, And Integration
No local persistent state beyond `dev->dma_coherent`. Depends on `dma.h`, cache type detection, CP15 control register state, and outer cache hooks. Integrates with generic DMA map ops for NOMMU ARM.

### Risks And Test Signals
Risks include treating cached systems as coherent too early, missing outer-cache maintenance, and direction-specific invalidation mistakes. Test NOMMU and v7-M builds, DMA_FROM_DEVICE data freshness, DMA_TO_DEVICE clean behavior, and boots with/without cache detection.
