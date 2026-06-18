# sources/distributed-fs/ceph-client/arch/arm64/mm/init.c

## Purpose
This file performs ARM64 early memory initialization. It selects the linear-map physical base, prunes memory that cannot be addressed, reserves kernel/initrd/crashkernel ranges, computes DMA zone limits, initializes SWIOTLB policy, marks page allocation availability, frees init memory, and configures executable memory allocation ranges for modules, kprobes, and BPF when `CONFIG_EXECMEM` is enabled.

## Important APIs, Types, and Functions
Exported or externally visible state includes `memstart_addr`, `arm64_dma_phys_limit`, `pfn_is_map_memory()`, `arch_zone_limits_init()`, `arm64_memblock_init()`, `bootmem_init()`, `arch_setup_zero_pages()`, `arch_mm_preinit()`, `page_alloc_available`, `mem_init()`, `free_initmem()`, `dump_mem_limit()`, and `execmem_arch_setup()`.

Key internal helpers include `arch_reserve_crashkernel()`, `max_zone_phys()`, `dma_limits_init()`, early parameter parser `early_mem()`, `random_bounding_box()`, and `module_init_limits()`. The file defines alignment policy through `ARM64_MEMSTART_SHIFT` and `ARM64_MEMSTART_ALIGN`, which are chosen from page granule and sparsemem constraints.

## Control Flow
The `mem=` early parameter sets `memory_limit`. `arm64_memblock_init()` then computes the usable linear region, caps it for 52-bit VA plus KVM nVHE constraints when needed, removes unsupported physical ranges above `PHYS_MASK_SHIFT`, aligns `memstart_addr`, removes memory outside the linear map, handles 52-bit VA fallback placement, applies `mem=`, restores mandatory kernel and initrd ranges, reserves the kernel image, converts initrd physical addresses to virtual addresses, and scans FDT reserved memory.

`bootmem_init()` derives min/max PFNs from memblock, runs early memory tests, initializes NUMA, reserves KVM hyp memory, initializes DMA limits, reserves CMA, reserves crashkernel memory, and dumps memblock. `arch_mm_preinit()` initializes SWIOTLB, forcing it for Realm guests and tuning it for unaligned kmalloc DMA bouncing. `mem_init()` marks `page_alloc_available` and updates SWIOTLB memory attributes. `free_initmem()` frees the linear-map alias of init sections and unmaps the virtual init range.

When executable memory support is built, `module_init_limits()` computes optional direct-branch and PLT-capable module windows, with KASLR-aware random bounding boxes. `execmem_arch_setup()` returns an `execmem_info` with ranges for modules, kprobes, and BPF.

## State and Persistence
`memstart_addr`, `arm64_dma_phys_limit`, `memory_limit`, `page_alloc_available`, `module_direct_base`, `module_plt_base`, and `execmem_info` are persistent boot-time state, mostly marked `__ro_after_init`. The memblock reservations and removals persist into the physical memory layout handed to the page allocator. The initrd virtual range and crashkernel reservations are globally visible to generic subsystems.

## Dependencies and Integration Points
The file integrates with memblock, DT/ACPI DMA discovery, NUMA, KVM hyp reservation, CMA, crashkernel, SWIOTLB, EFI/initrd, Realm services, and the generic execmem allocator. It relies on symbols from linker sections (`_text`, `_end`, `__init_begin`, etc.), ARM64 address translation helpers, and boot command line parsing.

## Risks
Incorrect linear-map sizing or `memstart_addr` alignment can make real RAM inaccessible or create invalid virtual-to-physical translations. Re-adding initrd or kernel ranges after memory limiting must avoid exceeding the linear-map window. DMA limit mistakes can break devices with restricted addressing. SWIOTLB policy is security-sensitive for Realm guests. Module range calculations must satisfy ARM64 relocation reach limits; otherwise modules may fail to load or require unnecessary PLTs.

## Test Signals
Boot logs for memory-limit warnings, SWIOTLB initialization, module range pages, crashkernel reservation, and initrd accessibility are primary signals. Kselftests or boot tests covering `mem=`, crashkernel, initrd placement, KASLR, memory hotplug baseline, DMA on limited devices, and module/BPF/kprobe allocation help validate this file. `pfn_is_map_memory()` correctness is indirectly tested by `/dev/mem`, ioremap, and pfn validation users.
