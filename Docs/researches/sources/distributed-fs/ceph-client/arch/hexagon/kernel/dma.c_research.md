# sources/distributed-fs/ceph-client/arch/hexagon/kernel/dma.c

## Purpose

`dma.c` initializes Hexagon coherent DMA reservations by assigning `dma_direct_set_offset` from `memblock_start_of_DRAM()` to `__phys_offset` and registering `hexagon_dma_init` through `arch_initcall`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key API is `hexagon_dma_init`, which establishes direct-DMA address translation for the architecture. Concrete declarations observed in the file: Includes: `linux/dma-map-ops.h`, `linux/memblock.h`, `asm/page.h`. Types referenced or declared: `dma_data_direction`. Functions/syscalls: `arch_sync_dma_for_device`, `hexagon_dma_init`.

## Control Flow, State, And Persistence

It runs once during initcall processing after memblock setup; it does not allocate persistent state beyond DMA mapping metadata.

## Dependencies And Integration Points

It depends on memblock, DMA direct map ops, `asm/page.h`, and the physical offset exported by MM initialization.

## Risks And Test Signals

Risks are incorrect DMA offset for nonzero physical bases or coherent pool assumptions. Test signals are DMA-capable device probe, DMA API debug, and coherent allocation tests.
 A local static signal for this file is that it has 45 lines and 1046 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
