# sources/distributed-fs/ceph-client/arch/m68k/mm/memory.c

## Purpose

provides m68k cache maintenance exports for physical address ranges, especially 68040/060 cache-line
clear and push operations

## Important APIs, Types, and Functions

Source read size: 192 lines, 5121 bytes. Includes: `linux/module.h`, `linux/mm.h`, `linux/kernel.h`,
`linux/string.h`, `linux/types.h`, `linux/init.h`, `linux/pagemap.h`, `linux/gfp.h`, `asm/setup.h`,
`asm/page.h`, `asm/traps.h`, `asm/machdep.h`. Defined functions: `Copyright`, `cleari040`,
`push040`, `pushcl040`, `cache_clear`, `cache_push`. Declared functions: `volatile`,
`local_irq_save`, `pushcl040`, `clear040`, `push040`, `cache_clear`. Exported symbols:
`cache_clear`, `cache_push`.

## Control Flow and Behavior

cache_clear() and cache_push() choose CPU-specific operations and iterate over physical ranges using
inline assembly helpers for data/instruction cache lines

## State and Persistence

state changes are hardware cache contents and dirty-line writeback status; no durable software state
is kept

## Dependencies and Integration Points

depends on CPU type flags, cache line size assumptions, traps/machdep setup, and callers that need
coherent instruction, DMA, or aliasing behavior

## Risks and Test Signals

wrong line rounding or CPU selection leaves stale instructions or lost DMA data; module loading,
executable mmap, DMA drivers, and cacheflush selftests are signals
