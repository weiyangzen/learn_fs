# sources/distributed-fs/ceph-client/include/linux/vmalloc.h

## Purpose
`vmalloc.h` declares the vmalloc/vmap subsystem interface for virtually contiguous kernel memory, ioremap bookkeeping, sparse vmap areas, user remapping of vmalloc memory, and low-level vmap area management. It exposes both driver-facing allocation APIs and lower-level memory-management hooks.

## Important APIs, Types, and Functions
Key flags include `VM_IOREMAP`, `VM_ALLOC`, `VM_MAP`, `VM_USERMAP`, `VM_DMA_COHERENT`, `VM_UNINITIALIZED`, `VM_NO_GUARD`, `VM_KASAN`, `VM_FLUSH_RESET_PERMS`, `VM_MAP_PUT_PAGES`, `VM_ALLOW_HUGE_VMAP`, `VM_DEFER_KMEMLEAK`, and `VM_SPARSE`. `struct vm_struct` records an allocated virtual range, backing pages, size, flags, optional huge-vmap page order, physical address, caller, and requested size. `struct vmap_area` records address-tree/list metadata and either free-tree max size or busy `vm_struct` pointer. High-level APIs include `vmalloc()`, `vzalloc()`, `vmalloc_user()`, `vmalloc_node()`, `vmalloc_32()`, `__vmalloc()`, `__vmalloc_node_range()`, `vmalloc_huge()`, array/calloc helpers, `vrealloc*()`, `vfree()`, `vfree_atomic()`, `vmap()`, `vmap_pfn()`, `vunmap()`, and `remap_vmalloc_range*()`. Low-level APIs include `get_vm_area*()`, `free_vm_area()`, `remove_vm_area()`, `find_vm_area()`, `find_vmap_area()`, `vm_area_map_pages()`, `vunmap_range()`, notifier registration, per-CPU vm area helpers, `vmalloc_dump_obj()`, and memory-allocation scope helpers.

## Control Flow
Allocation reserves a virtual address range, allocates or accepts backing pages, maps them with a selected `pgprot_t`, and records metadata in `vm_struct`/`vmap_area` structures. Driver callers use the high-level wrappers; mm internals use `get_vm_area*()` and mapping helpers to reserve and populate ranges explicitly. Freeing unmaps the virtual range, handles alias/TLB flushing, may asynchronously release memory on error paths, and returns pages when `VM_MAP_PUT_PAGES` is set. `remap_vmalloc_range()` maps vmalloc backing pages into user VMAs when the area is marked suitable.

## State and Persistence
State is in-memory kernel virtual address allocator metadata. Busy and free vmap areas are tracked in address-sorted trees/lists. Guard pages are part of `vm_struct->size` unless `VM_NO_GUARD` is set; `get_vm_area_size()` subtracts them for caller-visible size. There is no durable persistence, but mappings remain globally visible kernel virtual memory until explicitly unmapped.

## Dependencies and Integration Points
The header depends on page-table types, `struct page`, rbtrees, lists, llists, init annotations, overflow helpers, allocation tagging, KASAN, kmemleak, SMP/MMU config, architecture `asm/vmalloc.h`, and optional huge-vmap architecture callbacks. It integrates with module allocations, drivers needing large contiguous virtual buffers, ioremap, proc/kcore reads, per-CPU allocator setup, user `mmap` paths, and memory debugging.

## Risks
Misusing `VM_NO_GUARD` removes overflow protection. Callers must not use low-level APIs as driver conveniences because vmap metadata, TLB flushing, and page ownership are subtle. `find_vm_area(addr)` can return `NULL`; `is_vm_area_hugepages()` assumes a valid area. Huge-vmap support is architecture-conditional. `VM_FLUSH_RESET_PERMS` prevents freeing in atomic context. User remapping requires correct area bounds and page backing.

## Test Signals
Signals include vmalloc/vfree stress, large allocation fallback behavior, KASAN vmalloc coverage, huge-vmap mapping tests, `remap_vmalloc_range()` mmap tests, module load/unload, ioremap users, `vm_unmap_aliases()` behavior, TLB flush debugging, and leak detection for async/error paths.
