# sources/distributed-fs/ceph-client/arch/powerpc/mm/mem.c

Purpose: contains common PowerPC memory initialization, hotplug linear mapping hooks, zone setup, initmem freeing, system RAM resource registration, strict `/dev/mem`, and execmem layout.

Important APIs and control flow: hotplug paths serialize `create_section_mapping()`/`remove_section_mapping()` with `linear_mapping_mutex`, add/remove generic pages, update `max_pfn`/`high_memory`, and flush vmalloc aliases. `paging_init()` configures highmem fixmaps, prints RAM/hole data, sets DMA zone limits, and registers nosave holes. `arch_mm_preinit()` reserves CMA for fadump/kdump/KVM, initializes SWIOTLB bottom-up when needed, runs KASAN late init, and fixes e500 CAM indices. `execmem_arch_setup()` chooses executable allocation ranges and protections.

State and dependencies: state includes `memory_limit`, `zone_dma_limit`, max PFNs, highmem globals, iomem resources, and execmem info. Dependencies span memblock, NUMA, RTAS/fadump/kdump/KVM CMA, SWIOTLB, KASAN, ftrace, and generic memory hotplug. Risks include stale linear mappings during hot-remove, wrong DMA zone limits, `/proc/iomem` resource leaks, and executable memory range/protection mistakes. Test signals include memory hotplug, suspend nosave holes, strict devmem tests, module/kprobe allocation, and kdump/fadump reservations.
