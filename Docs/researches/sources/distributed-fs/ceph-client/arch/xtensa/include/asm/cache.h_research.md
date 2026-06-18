<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cache.h

## Purpose
Defines Xtensa cache geometry constants and cache-alignment attributes used across memory management and DMA code.

## Important APIs, Types, And Functions
Key macros are `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `SMP_CACHE_BYTES`, `DCACHE_WAY_SIZE`, `ICACHE_WAY_SIZE`, `DCACHE_WAY_SHIFT`, `ICACHE_WAY_SHIFT`, `ARCH_DMA_MINALIGN`, and Xtensa's `__ro_after_init` mapping.

## Control Flow
No executable flow; constants are computed from variant `XCHAL_*` core definitions.

## State And Persistence
No state. It affects structure alignment, cache flush ranges, page coloring, and DMA buffer alignment.

## Dependencies And Integration Points
Depends on `asm/core.h` and variant cache geometry. Used by `page.h`, `cacheflush.h`, DMA, highmem, and allocator alignment logic.

## Risks And Edge Cases
Wrong cache line or way-size values cause aliasing bugs, data corruption, or inefficient flushing. `ARCH_DMA_MINALIGN` must be large enough for noncoherent DMA.

## Test Signals
Compile against multiple variants, run cache aliasing tests, DMA tests, and highmem/page-coloring paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cache.h -->
