# sources/distributed-fs/ceph-client/arch/powerpc/mm/pageattr.c

## Purpose
This file implements PowerPC `set_memory_*` style page attribute changes over existing kernel mappings. It updates PTE permission and presence bits atomically, performs required synchronization, and flushes kernel TLB entries.

## Important APIs, Types, And Functions
The main public API is `change_memory_attr()`, used by set-memory wrappers. `change_page_attr()` is the callback passed to `apply_to_existing_page_range()`. `pte_update_delta()` computes bit removals/additions around `pte_update()`. Under debug page allocation or KFENCE, `__kernel_map_pages()` toggles page presence for debug allocator poisoning.

## Control Flow
`change_memory_attr()` aligns the start address, rejects zero-page requests, rejects huge vmalloc/module mappings, and on Book3S hash rejects non-vmalloc/non-IO regions because linear mappings are not represented in Linux page tables. It then applies `change_page_attr()` over the existing range. The callback switches on action values such as `SET_MEMORY_RO`, `SET_MEMORY_ROX`, `SET_MEMORY_RW`, `SET_MEMORY_NX`, `SET_MEMORY_X`, `SET_MEMORY_NP`, and `SET_MEMORY_P`, updates PTE bits, issues `ptesync` for radix, and calls `flush_tlb_kernel_range()` for the page.

## State And Persistence
The persistent state is the modified kernel PTE attributes in `init_mm`. No separate cache is kept. For debug page allocation, page presence is toggled until the allocator re-enables it.

## Dependencies And Integration Points
It depends on generic `apply_to_existing_page_range()`, PowerPC PTE helpers, radix/hash selection, `is_vmalloc_or_module_addr()`, huge vmalloc detection, `hash__kernel_map_pages()`, and `flush_tlb_kernel_range()`. It is used by strict RWX, module permission changes, debug pagealloc, and KFENCE.

## Risks And Test Signals
Risks include changing unmapped or huge mappings, missing TLB flushes, incorrectly clearing dirty state, and unsupported Book3S hash linear-map updates. Tests should exercise module/text ROX changes, vmalloc permission changes, radix and hash builds, debug pagealloc/KFENCE toggles, and invalid huge-vmalloc requests returning `-EINVAL`.
