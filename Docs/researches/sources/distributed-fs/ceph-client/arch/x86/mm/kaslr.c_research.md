# sources/distributed-fs/ceph-client/arch/x86/mm/kaslr.c

## Purpose
This file randomizes x86_64 kernel virtual memory regions at boot: direct map, vmalloc, and vmemmap. It also prepares the real-mode trampoline mapping needed when the direct map base is randomized.

## Important APIs, Types, and Functions
- `kernel_randomize_memory()` computes randomized bases for `page_offset_base`, `vmalloc_base`, and `vmemmap_base`, and sets `direct_map_physmem_end`.
- `init_trampoline_kaslr()` builds a low-memory PGD entry for the real-mode trampoline that mirrors the direct-map PUD/P4D path for physical address 0.
- `struct kaslr_memory_region` records each randomized region's base pointer, optional end pointer, and size in TiB.
- `get_padding()` converts TiB-sized region slots into bytes.

## Control Flow and State
The algorithm starts at the configured 4-level or 5-level page-offset base and ends before `CPU_ENTRY_AREA_BASE`. It initializes the direct-map maximum to `(1 << MAX_PHYSMEM_BITS) - 1`, exits if memory KASLR is disabled, sizes the direct map from physical RAM plus configured padding, optionally shrinks it when `ZONE_DEVICE` is disabled, derives vmemmap size from the direct-map size, and distributes remaining entropy between ordered regions. Random entropy is PUD-aligned and order is preserved. `direct_map_physmem_end` is updated when the direct map is trimmed.

## Dependencies and Integration Points
The code depends on `kaslr_get_random_long()`, `prandom`, `max_pfn`, paging mode selection, global virtual base variables from x86 layout code, CPU entry area bounds, and `alloc_low_page()` from `mm_internal.h`. Direct-map sizing feeds later page-table initialization and hotplug limit checks.

## Risks
Virtual layout constants must remain ordered; BUILD_BUG_ON checks catch only some layout drift. Shrinking `direct_map_physmem_end` conflicts with `ZONE_DEVICE`, which may need arbitrary physical addresses mapped. Entropy arithmetic must leave enough room for all regions and maintain PUD alignment. The trampoline mapping must match the randomized direct map or secondary CPU real-mode entry can fail.

## Test Signals
Boot logs and page-table dumps should show randomized bases when memory KASLR is enabled and fixed bases when disabled. Tests should include 4-level/5-level paging, large RAM, `CONFIG_RANDOMIZE_MEMORY_PHYSICAL_PADDING`, `ZONE_DEVICE`, CPU bring-up after KASLR, and hotplug ranges checked against `DIRECT_MAP_PHYSMEM_END`.
