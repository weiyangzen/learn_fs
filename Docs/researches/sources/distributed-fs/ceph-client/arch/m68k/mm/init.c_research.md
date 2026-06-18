# sources/distributed-fs/ceph-client/arch/m68k/mm/init.c

## Purpose

provides the generic m68k memory initialization path for non-MMU or common-MMU builds, including
zone limits, node setup, paging initialization, initmem release, and final memory accounting

## Important APIs, Types, and Functions

Source read size: 118 lines, 2546 bytes. Includes: `linux/module.h`, `linux/signal.h`,
`linux/sched.h`, `linux/mm.h`, `linux/swap.h`, `linux/kernel.h`, `linux/string.h`, `linux/types.h`,
`linux/init.h`, `linux/memblock.h`, `linux/gfp.h`, `asm/setup.h`; plus 9 more. Defined functions:
`Copyright`, `m68k_setup_node`, `paging_init`, `free_initmem`, `init_pointer_tables`, `mem_init`.
Key macros/defines: `VECTORS`.

## Control Flow and Behavior

arch_zone_limits_init(), m68k_setup_node(), paging_init(), free_initmem(), init_pointer_tables(),
and mem_init() transition from boot memory descriptors to managed pages and initialize vector/page-
table areas as required by the selected CPU/MMU model

## State and Persistence

persistent state includes max_zone_pfns, pg_data_t node ranges, reserved vector pages, freed init
sections, totalram_pages, memblock reservations, and architecture page-table metadata

## Dependencies and Integration Points

integrates with memblock, sparse/contiguous memory models, m68k bootinfo, machdep hooks, TLB/page-
table setup, Atari ST-RAM handling, and generic mm initialization

## Risks and Test Signals

zone boundary or reservation errors can expose ROM, vectors, or page tables to the allocator; boot
logs, memblock debug, free_initmem accounting, and m68k defconfig boots are key signals
