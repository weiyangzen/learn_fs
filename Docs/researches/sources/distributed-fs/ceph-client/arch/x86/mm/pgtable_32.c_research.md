# sources/distributed-fs/ceph-client/arch/x86/mm/pgtable_32.c

## Purpose
`pgtable_32.c` contains x86-32-specific page-table support for kernel virtual mappings, fixmap top placement, vmalloc sizing, and early reservation of top kernel address space.

## Important APIs, Types, and Functions
The important symbols are mutable `__VMALLOC_RESERVE`, `set_pte_vaddr()`, exported `__FIXADDR_TOP`, early-parameter handlers `parse_vmalloc()` and `parse_reservetop()`, and the `vmalloc=`/`reservetop=` command-line hooks.

## Control Flow and State
`set_pte_vaddr()` walks `swapper_pg_dir` down to the kernel PTE for a virtual address, installs or clears the PTE through `set_pte_at()`/`pte_clear()`, and flushes that single kernel TLB entry. `parse_vmalloc()` parses a requested vmalloc size and adds the guard-hole offset. `parse_reservetop()` reserves a top-of-address-space hole, relocates the fixmap via `reserve_top_address()`, and reinitializes early ioremap state.

## State and Persistence
The file persists boot-selected vmalloc reserve size and fixmap top address. It mutates kernel page tables and TLBs for fixed mappings, and the early parameters affect the whole 32-bit kernel virtual layout.

## Dependencies and Integration Points
It depends on x86-32 page-table layout, fixmap, early ioremap, E820/top reservation logic, vmalloc, and TLB flushing. `set_pte_vaddr()` is used by generic x86 fixmap code in `pgtable.c`.

## Risks and Test Signals
Risks include BUG-triggering missing upper-level entries, bad `vmalloc=` values crowding lowmem/fixmap areas, and reservetop relocation after fixmaps are already established. Test signals are 32-bit boot with `vmalloc=` and `reservetop=`, early ioremap users, fixmap setup, and single-entry TLB flush correctness.
