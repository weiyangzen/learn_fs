## sources/distributed-fs/ceph-client/arch/arm/mm/dma.h

### Purpose
Private ARM DMA-cache helper header that maps generic DMA maintenance names to either compile-time cache-specific symbols or runtime `cpu_cache` function pointers.

### Important APIs, Types, And Functions
Defines `dmac_map_area` and `dmac_unmap_area`. In non-`MULTI_CACHE` builds they glue to `_CACHE_dma_map_area`/`_CACHE_dma_unmap_area`; in `MULTI_CACHE` builds they resolve to `cpu_cache.dma_map_area` and `cpu_cache.dma_unmap_area`.

### Control Flow
No executable control flow. Inclusion controls whether callers bind statically or indirectly through the active cache vtable.

### State, Dependencies, And Integration
No private state. Depends on `<asm/glue-cache.h>` and `cpu_cache` definitions from cacheflush infrastructure. Integrated by `dma-mapping.c` and `dma-mapping-nommu.c`.

### Risks And Test Signals
Risks are using these private helpers outside DMA API ownership transitions or selecting the wrong cache backend. Build both `MULTI_CACHE` and single-cache configurations, then run DMA sync direction tests and symbol resolution checks.
