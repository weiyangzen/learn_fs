# sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3dvma.c

## Purpose

implements the higher-level Sun-3 DVMA allocator and mapping layer used by bus-mastering devices

## Important APIs, Types, and Functions

Source read size: 359 lines, 6735 bytes. Includes: `linux/memblock.h`, `linux/init.h`,
`linux/module.h`, `linux/kernel.h`, `linux/gfp.h`, `linux/mm.h`, `linux/list.h`, `asm/page.h`,
`asm/dvma.h`. Defined functions: `print_use`, `print_holes`, `refill`, `list_for_each`, `get_baddr`,
`free_baddr`, `dvma_init`, `dvma_map_align`, `dvma_unmap`, `dvma_free`. Declared functions:
`pr_info`, `list_move`, `pr_crit`, `INIT_LIST_HEAD`, `pr_debug`, `free_baddr`, `free_pages`,
`dvma_unmap`. Key macros/defines: `dvma_index(baddr)`, `dvma_entry_use(baddr)`. Types visible in
this file: `hole`, `list_head`. Exported symbols: `dvma_map_align`, `dvma_unmap`,
`dvma_malloc_align`, `dvma_free`.

## Control Flow and Behavior

the code allocates DVMA virtual ranges, maps kernel pages into DVMA bus-visible space, tracks active
mappings, and tears them down for device drivers

## State and Persistence

persistent state includes DVMA region metadata, mapping lists, page-map entries, and allocated
bootmem/vmalloc backing areas

## Dependencies and Integration Points

integrates with asm/dvma.h, Sun-3 MMU page map routines, SCSI/Ethernet drivers, and generic DMA
expectations for cache-coherent device access

## Risks and Test Signals

leaked DVMA slots, wrong bus addresses, or missing cache maintenance break I/O; disk/network
transfers under memory pressure are the primary signals
