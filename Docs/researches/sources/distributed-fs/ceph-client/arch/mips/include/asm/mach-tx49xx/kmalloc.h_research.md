# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/kmalloc.h

Purpose: TX49xx allocation-alignment policy for DMA-safe `kmalloc` allocations.

Important APIs/types/functions: Defines `ARCH_DMA_MINALIGN` as `L1_CACHE_BYTES`, forcing allocations that may be used for DMA to align at least to a cache line.

Control flow, state, and persistence: No control flow or state; it affects allocator constants at compile time.

Dependencies and integration: Requires `L1_CACHE_BYTES` from cache geometry headers. It integrates with Linux slab/kmalloc alignment rules and TX49xx DMA/cache coherency behavior.

Risks and test signals: Too-small alignment can cause DMA cacheline sharing corruption; too-large alignment wastes memory. Test with TX49xx DMA-capable drivers, network/storage I/O, and cache coherency stress under small allocation sizes.
