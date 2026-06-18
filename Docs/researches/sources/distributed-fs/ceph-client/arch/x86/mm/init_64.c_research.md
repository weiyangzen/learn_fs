# sources/distributed-fs/ceph-client/arch/x86/mm/init_64.c

## Purpose
This file implements 64-bit x86 kernel memory initialization, direct-map population, page-table synchronization, hotplug add/remove, sparse vmemmap backing, vmalloc preallocation, rodata hardening, and memory block sizing. It is central to 4-level/5-level paging support and to keeping kernel mappings consistent across process page tables.

## Important APIs, Types, and Functions
- `arch_sync_kernel_mappings()` synchronizes newly populated top-level kernel mappings into all process PGDs using `sync_global_pgds_l5()` or `sync_global_pgds_l4()`.
- `set_pte_vaddr*()`, `populate_extra_pmd()`, and `populate_extra_pte()` create or update kernel mappings for fixmap/early users.
- `init_extra_mapping_wb()` and `init_extra_mapping_uc()` create early PMD-sized direct-map additions with explicit cache modes.
- `kernel_physical_mapping_init()` and `kernel_physical_mapping_change()` build or split direct mappings through `phys_p4d_init()`, `phys_pud_init()`, `phys_pmd_init()`, and `phys_pte_init()`.
- Hotplug APIs include `arch_add_memory()`, `add_pages()`, `arch_remove_memory()`, `vmemmap_free()`, and page-table removal helpers.
- Vmemmap APIs include `vmemmap_set_pmd()`, `vmemmap_check_pmd()`, `vmemmap_populate()`, `register_page_bootmem_memmap()`, and `vmemmap_populate_print_last()`.
- `memory_block_size_bytes()` probes hotplug granularity; `mark_rodata_ro()` hardens kernel mappings.

## Control Flow and State
Early boot creates missing page-table pages via `spp_getpage()`, using memblock before `after_bootmem` and atomic page allocation afterward. Direct-map creation descends from PGD to PTE, preserving existing Xen or early mappings when possible and choosing 1 GiB, 2 MiB, or 4 KiB mappings based on `page_size_mask`. When new top-level entries are installed, `sync_global_pgds()` propagates them. Memory hotplug first maps the physical range, adds struct pages, updates `max_pfn`, `max_low_pfn`, and `high_memory`, and later can tear down direct-map and vmemmap page tables with TLB flushes. Vmemmap state tracks unused sub-PMD ranges with `unused_pmd_start` and debug span globals.

## Dependencies and Integration Points
The implementation integrates with memblock, sparsemem/vmemmap, memory hotplug, NUMA, e820, kcore, bootmem info, ftrace rodata protection, Xen/PV expectations, and generic memory section registration. `mm_internal.h` exposes the direct-map creation and change routines to encryption and setup code. KASLR affects virtual base addresses through `__va()` and page-table layout.

## Risks
Top-level synchronization differs between 4-level and 5-level paging; using the wrong level can leave process page tables missing kernel mappings. Hot-remove must not free low identity mappings below 1 GiB and must coordinate altmap-backed vmemmap memory. Large-page splitting must preserve physical frame and attributes before changing page size. `preallocate_vmalloc_pages()` panics if synchronization-critical page-table levels cannot be allocated.

## Test Signals
Boot and hotplug logs show memory block size, vmemmap PMD spans, kcore vsyscall registration, rodata protection, and page-count updates. Test scenarios include 4-level and 5-level paging, memory hotplug add/remove, device-private `memremap_pages()`, vmemmap hugepage/altmap paths, KASLR direct-map bases, Xen/PV boot, and CPA debug rodata toggling.
