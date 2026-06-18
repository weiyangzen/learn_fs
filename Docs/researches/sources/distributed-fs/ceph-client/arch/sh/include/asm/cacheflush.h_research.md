# sources/distributed-fs/ceph-client/arch/sh/include/asm/cacheflush.h



Source read size: 126 lines, 4322 bytes.



Purpose: SH cache flush API declarations and helpers.

Important APIs/types/functions: flush-cache function pointers, `flush_cache_*`, `flush_dcache_folio`, `flush_icache_range/pages`, vmap helpers, kmap coherent APIs, CPU cache init hooks.

Control flow: callers route through CPU-selected local flush functions and alias-aware anon-page handling.

State and persistence: function pointers and page clean bits persist after CPU cache init.

Dependencies and integration points: MM, DMA, JIT/signal trampolines, vmalloc, kmap.

Risks and test signals: aliasing and 29-bit mapping errors corrupt data/instructions. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
