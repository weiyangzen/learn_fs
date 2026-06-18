# sources/distributed-fs/ceph-client/mm/memblock.c

## Purpose

This file implements Linux's early-boot memblock allocator and region database. It tracks usable physical memory, reserved allocations, and optionally the architecture physical memory map before slab and the buddy allocator are fully available. It is responsible for adding/removing memory ranges, reserving boot-time allocations, finding free physical ranges with NUMA/flag constraints, handing free memory to the buddy allocator during boot, exposing optional debugfs state, and supporting named `reserve_mem=` allocations including kexec handover preservation.

## Important APIs, types, and functions

The central state is the global `struct memblock memblock` with `memory` and `reserved` `struct memblock_type` arrays, plus optional `struct memblock_type physmem`. Region entries carry base, size, NUMA node, and `enum memblock_flags` such as `MEMBLOCK_HOTPLUG`, `MEMBLOCK_MIRROR`, `MEMBLOCK_NOMAP`, `MEMBLOCK_DRIVER_MANAGED`, `MEMBLOCK_RSRV_NOINIT`, `MEMBLOCK_RSRV_KERN`, and `MEMBLOCK_KHO_SCRATCH`.

Important mutators are `memblock_add()`, `memblock_add_node()`, `memblock_remove()`, `__memblock_reserve()`, `memblock_physmem_add()`, `memblock_set_node()`, `memblock_mark_hotplug()`, `memblock_clear_hotplug()`, `memblock_mark_mirror()`, `memblock_mark_nomap()`, `memblock_clear_nomap()`, `memblock_reserved_mark_noinit()`, `memblock_reserved_mark_kern()`, `memblock_mark_kho_scratch()`, and `memblock_clear_kho_scratch()`. They are built on `memblock_add_range()`, `memblock_isolate_range()`, `memblock_setclr_flag()`, `memblock_insert_region()`, `memblock_remove_region()`, and `memblock_merge_regions()`.

Allocation APIs include `memblock_alloc_range_nid()`, `memblock_phys_alloc_range()`, `memblock_phys_alloc_try_nid()`, `memblock_alloc_exact_nid_raw()`, `memblock_alloc_try_nid_raw()`, `memblock_alloc_try_nid()`, and `__memblock_alloc_or_panic()`. Allocation search flows through `memblock_find_in_range_node()`, `__memblock_find_range_bottom_up()`, and `__memblock_find_range_top_down()`, using `choose_memblock_flags()` for mirrored-memory and KHO scratch-only policy.

Iteration and query helpers include `__next_mem_range()`, `__next_mem_range_rev()`, `__next_mem_pfn_range()`, `memblock_addrs_overlap()`, `memblock_overlaps_region()`, `memblock_is_reserved()`, `memblock_is_memory()`, `memblock_is_map_memory()`, `memblock_search_pfn_nid()`, `memblock_is_region_memory()`, `memblock_is_region_reserved()`, `memblock_phys_mem_size()`, `memblock_reserved_size()`, `memblock_reserved_kern_size()`, `memblock_estimated_nr_free_pages()`, `memblock_start_of_DRAM()`, and `memblock_end_of_DRAM()`.

Boot handoff and cleanup are handled by `free_reserved_area()`, `memblock_free()`, `memblock_phys_free()`, `memblock_discard()`, `free_unused_memmap()`, `memmap_init_reserved_pages()`, `free_low_memory_core_early()`, `reset_all_zones_managed_pages()`, and `memblock_free_all()`. Named reservations use `reserve_mem()`, `reserved_mem_add()`, `reserve_mem_find_by_name()`, and `reserve_mem_release_by_name()`. Kexec handover support adds `reserved_mem_preserve()`, `prepare_kho_fdt()`, `reserve_mem_init()`, `reserve_mem_kho_retrieve_fdt()`, and `reserve_mem_kho_revive()`.

## Control flow

Architecture boot code populates memory with `memblock_add()` or `memblock_add_node()`, optionally records physical memory in `physmem`, and reserves early allocations through `memblock_alloc*()` or `__memblock_reserve()`. Range addition is a two-pass operation: `memblock_add_range()` first counts pieces not covered by existing sorted regions, resizes the array if needed, then inserts only uncovered spans and merges neighboring regions that have matching node and flags.

Removal and flag changes first call `memblock_isolate_range()` so target boundaries align with region boundaries, then remove regions or mutate flags, and finally merge compatible neighbors. This keeps `memory` and `reserved` sorted and minimally split. Array growth uses `memblock_double_array()`, which either uses slab when available or allocates from memblock while avoiding a soon-to-be-reserved range for the reserved-array case.

Allocation starts in `memblock_alloc_range_nid()`: it rejects late use once slab is available with a warning and `kzalloc_node()` fallback, validates alignment, searches the requested node and range, reserves the chosen address as `MEMBLOCK_RSRV_KERN`, optionally falls back to any node, optionally retries without the mirror flag, registers the allocation with kmemleak unless `MEMBLOCK_ALLOC_NOLEAKTRACE` was used, and calls `accept_memory()` for confidential-computing guests. The virtual-address wrappers cap `max_addr` by `memblock.current_limit`, retry without the preferred lower bound, and optionally zero memory.

The free-range iterators compute intersections of an include type and the holes before an exclude type, normally `memory` minus `reserved`. `should_skip_region()` filters only `memblock.memory` for NUMA, hotplug, mirror, nomap, driver-managed, and KHO scratch flags. The reverse iterator mirrors the same logic from high addresses downward, giving top-down allocation deterministic high-address selection.

At boot handoff, `memblock_free_all()` frees unused memmap holes, resets zone managed-page accounting, clears KHO scratch-only allocation mode, initializes PageReserved state for reserved and NOMAP ranges, frees all non-reserved low memory ranges to the buddy allocator, and updates total RAM pages. Unless `CONFIG_ARCH_KEEP_MEMBLOCK` is enabled, `memblock_discard()` later frees dynamically allocated memblock arrays and clears `memblock_memory`.

Named `reserve_mem=` parsing accepts `size:align:name`, validates capacity and name length, revives a prior KHO reservation if possible, otherwise allocates a physical memblock region, and stores it in a small fixed table. KHO preservation serializes named reservations into an FDT subtree and preserves the backing pages across kexec; revive validates compatibility, alignment, and size before reusing the old physical address.

## State and persistence behavior

Most state is early-boot global memory metadata in `memblock`, `physmem`, `max_low_pfn`, `min_low_pfn`, `max_pfn`, `max_possible_pfn`, resize/debug flags, and KHO scratch-only mode. Region arrays begin as static `__initdata_memblock` storage and may move to memblock-allocated pages or slab; `memblock_discard()` frees dynamic arrays when the architecture does not keep memblock data.

The allocator persists only until the buddy allocator takes ownership of free pages. The optional `CONFIG_ARCH_KEEP_MEMBLOCK` path keeps memblock arrays available for later debugfs and queries. Named `reserve_mem` entries persist in `reserved_mem_table` after boot and can be found or released by name. With `CONFIG_KEXEC_HANDOVER`, named reservations may persist across a kexec cycle through preserved pages and an FDT descriptor. Debug state is exposed under debugfs when enabled, including raw memblock arrays when memblock is kept and a `reserve_mem_param` listing when named reservations exist.

## Dependencies and integration points

The file depends on core kernel headers for init, slab, PFN conversion, kmemleak, debugfs, seq_file, mutexes, string formatting, and `linux/memblock.h`; it uses architecture hooks such as `__pa`, `__va`, `phys_to_virt`, `pfn_to_page`, `for_each_valid_pfn`, `memblock_free_pages`, `early_pfn_to_nid`, and `accept_memory()`. It integrates with NUMA, memory hotplug filtering, sparsemem/vmemmap behavior, deferred struct-page initialization, KASAN tag handling, kmemleak, confidential-computing memory acceptance, KHO/libfdt, debugfs, early parameters (`memblock=debug`), and boot command-line setup (`reserve_mem=`).

The allocator is used by architecture setup, early page-table/KASAN/initrd/reserved-memory code, zone/page allocator initialization, and subsystems needing physically contiguous boot memory before normal allocation is available. It also exports `contig_page_data` on non-NUMA builds and `reserve_mem_find_by_name()` for modules or built-in users of named reserved memory.

## Risks

The major correctness risk is corruption of sorted, non-overlapping memblock arrays: off-by-one errors in split/merge, address overflow around `base + size`, or incorrect resize reservations can leak, double reserve, or free boot-critical memory. Allocation policy is also delicate: `current_limit`, top-down/bottom-up mode, exact NUMA requests, mirror fallback, NOMAP/driver-managed filtering, and KHO scratch filtering all affect whether early allocations land in usable memory.

Late calls after slab is live are risky because memblock metadata may already be discarded, so the code warns and falls back only in `memblock_alloc_range_nid()`. `free_reserved_area()` refuses to operate with deferred page initialization, and misuse can release pages whose `struct page` state is not initialized. KHO and named reservation paths risk preserving stale or mis-sized memory if FDT validation or alignment checks miss a case. Debugfs array exposure depends on `CONFIG_ARCH_KEEP_MEMBLOCK`; without it, raw memory/reserved arrays are not valid after discard.

## Test signals

Useful test signals include early boot logs with `memblock=debug`, successful boot on NUMA and UMA machines, correct `/sys/kernel/debug/memblock/*` content when enabled, absence of memblock resize panics, no bootmem overlap with initrd/FDT/kernel image, stable `max_pfn` and zone managed-page accounting after `memblock_free_all()`, and kmemleak not reporting memblock allocations as leaks. Specific coverage should exercise memory limits (`mem=`, memblock cap/enforce paths), hotplug/movable-node memory, mirrored memory fallback, NOMAP reserved ranges, deferred struct-page init, confidential-computing memory acceptance, `reserve_mem=` find/release behavior, and KHO preserve/revive across kexec.
