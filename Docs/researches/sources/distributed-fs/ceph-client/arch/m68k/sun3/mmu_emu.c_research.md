# sources/distributed-fs/ceph-client/arch/m68k/sun3/mmu_emu.c

## Purpose

emulates enough Sun-3 MMU behavior in software to support Linux page-table semantics on hardware
with a segmented PMEG MMU

## Important APIs, Types, and Functions

Source read size: 427 lines, 11915 bytes. Includes: `linux/init.h`, `linux/mman.h`, `linux/mm.h`,
`linux/kernel.h`, `linux/ptrace.h`, `linux/delay.h`, `linux/memblock.h`, `linux/bitops.h`,
`linux/module.h`, `linux/sched/mm.h`, `linux/string_choices.h`, `asm/setup.h`; plus 8 more. Defined
functions: `print_pte`, `print_pte_vaddr`, `mmu_emu_init`, `clear_context`, `get_free_context`,
`mmu_emu_map_pmeg`, `mmu_emu_handle_fault`. Declared functions: `pr_cont`, `memset`, `pr_info`,
`dvma_init`, `sun3_put_context`, `sun3_put_segmap`, `clear_context`, `sun3_put_pte`,
`str_read_write`, `mmu_emu_map_pmeg`, `pte_val`. Key macros/defines: `DEBUG_PROM_MAPS`,
`CONTEXTS_NUM`, `SEGMAPS_PER_CONTEXT_NUM`, `PAGES_PER_SEGMENT`, `PMEGS_NUM`, `PMEG_MASK`. Exported
symbols: `m68k_vmalloc_end`.

## Control Flow and Behavior

mmu_emu_init() builds software tables, mmu_emu_map_pmeg() assigns PMEGs to virtual segments,
mmu_emu_handle_fault() resolves faults by loading page map entries, and diagnostic helpers print
page-table state

## State and Persistence

persistent state includes PMEG allocation tables, context/segment mappings, software page-table
mirrors, and fault-time replacement metadata

## Dependencies and Integration Points

integrates with sun3mmu low-level map writes, Sun-3 fault handlers, sun3kmap/ioremap, and generic
m68k page-table state

## Risks and Test Signals

replacement policy, kernel/user context separation, and fault reentrancy are risky; Sun-3 multi-
process memory pressure, mmap/page-fault stress, and PMEG exhaustion tests are signals
