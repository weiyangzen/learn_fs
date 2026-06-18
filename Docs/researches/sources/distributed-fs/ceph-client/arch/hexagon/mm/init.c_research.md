# sources/distributed-fs/ceph-client/arch/hexagon/mm/init.c

## Purpose

`init.c` implements Hexagon memory initialization, boot memory sizing, DMA reservation, initial segment-table pruning, cache/page protection defaults, and zone limits. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs and state include `bootmem_lastpg`, `__phys_offset`, `_dflt_cache_att`, `sync_icache_dcache`, `arch_zone_limits_init`, `setup_arch_memory`, `hexagon_coherent_pool_size`, and `protection_map`. Concrete declarations observed in the file: Includes: `linux/init.h`, `linux/mm.h`, `linux/memblock.h`, `asm/atomic.h`, `linux/highmem.h`, `asm/tlb.h`, `asm/sections.h`, `asm/setup.h`, `asm/vm_mmu.h`. Macros: `bootmem_startpg`, `DMA_RESERVE`, `DMA_CHUNKSIZE`, `DMA_RESERVED_BYTES`. Types referenced or declared: `page`. Functions/syscalls: `sync_icache_dcache`, `arch_zone_limits_init`, `paging_init`, `early_mem`, `setup_arch_memory`.

## Control Flow, State, And Persistence

Boot flow parses `mem=`, adds/reserves memblock ranges, reserves the coherent DMA top-of-RAM pool, trims early segment-table entries past physical memory, initializes paging, and exposes page protection mapping.

## Dependencies And Integration Points

It integrates with `setup.c`, `vm_init_segtable.S`, memblock, generic MM, DMA setup, and cache synchronization.

## Risks And Test Signals

Risks are off-by-one PFNs, reserving too much/little DMA memory, invalidating required mappings, and wrong page protections. Test signals are boot memory logs, memblock debug, DMA coherent allocation, page-fault tests, and mmap permission tests.
 A local static signal for this file is that it has 245 lines and 7545 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
