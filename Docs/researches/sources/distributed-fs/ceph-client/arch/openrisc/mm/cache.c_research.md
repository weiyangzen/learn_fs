<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/cache.c

## Purpose
Implements OpenRISC cache presence checks, D-cache flush/invalidate, I-cache invalidate, and executable mapping cache synchronization.

## Important APIs, Types, And Functions
`cpu_cache_is_present()`, `local_dcache_page_flush()`, `local_icache_page_inv()`, `local_dcache_range_flush()`, `local_dcache_range_inv()`, `local_icache_range_inv()`, and `update_cache()` are central.

## Control Flow
Range helpers loop over cache-line-sized physical addresses and write cache-control SPRs. `update_cache()` marks folios clean using `PG_dc_clean`; for executable VMAs it synchronizes I-cache/D-cache for dirty folio pages.

## State And Persistence
Mutates hardware cache state and folio `PG_dc_clean` flag. No private global state.

## Dependencies And Integration Points
Depends on UPR cache bits, cache SPRs, `L1_CACHE_BYTES`, folio flags, and cacheflush APIs used by mmap, DMA, and text patching.

## Risks
Cache line size must match hardware. `PG_dc_clean` state controls whether executable mappings get synchronized. Physical address ranges must be line-aligned enough for hardware expectations.

## Test Signals
Executable mmap after writes, text patching, DMA coherency, cacheinfo consistency, and platforms with absent I-cache/D-cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/cache.c -->
