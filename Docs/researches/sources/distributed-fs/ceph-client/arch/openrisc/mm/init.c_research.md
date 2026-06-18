<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/init.c

## Purpose
Initializes OpenRISC paging, maps RAM, patches final TLB miss vectors, manages fixmap mappings, marks kernel RO pages, and defines vm protection mappings.

## Important APIs, Types, And Functions
`arch_zone_limits_init()`, `map_ram()`, `paging_init()`, `mem_init()`, `map_page()`, `__set_fixmap()`, `protection_map`, and `DECLARE_VM_GET_PAGE_PROT` are key. Global `mem_init_done` gates early PTE allocation elsewhere.

## Control Flow
`paging_init()` clears `swapper_pg_dir`, initializes `current_pgd`, maps all memblock ranges via two-level page tables, patches vector slots at `0x900` and `0xa00` to runtime TLB handlers, invalidates I-cache blocks, and flushes TLBs so new RO flags take effect.

## State And Persistence
Creates kernel page tables, maps physical memory, sets RO permissions for linker-defined kernel RO range, updates low exception vectors, sets `mem_init_done`, and manages fixmap PTEs.

## Dependencies And Integration Points
Depends on memblock, linker symbols, `swapper_pg_dir` from `head.S`, TLB miss handlers, cache/TLB flush APIs, fixmap, and generic VM protection code.

## Risks
Hardcoded two-level page table assumptions are enforced by panic. Vector self-modification before RO lockdown is delicate. Fixmap clearing uses `pgprot_val(prot) == 0` semantics.

## Test Signals
Boot through paging init, kernel text RO enforcement, fixmap users such as early console/text poke, RAM mapping across memblock ranges, and page protection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/init.c -->
