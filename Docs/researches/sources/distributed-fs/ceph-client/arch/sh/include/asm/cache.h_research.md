# sources/distributed-fs/ceph-client/arch/sh/include/asm/cache.h



Source read size: 52 lines, 1343 bytes.



Purpose: SH cache geometry definitions.

Important APIs/types/functions: `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `struct cache_info`, `__read_mostly`.

Control flow: no flow; consumed by cache and DMA code.

State and persistence: boot CPU cache descriptors live elsewhere.

Dependencies and integration points: allocator alignment, DMA, cacheflush.

Risks and test signals: wrong line size or alias mask causes DMA/cache corruption. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
