<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sysmem.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sysmem.h

Purpose: declares architecture memory initialization entry points `bootmem_init()` and `zones_init()`.

Control flow is implemented elsewhere in setup/mm code: early boot discovers/reserves memory, then initializes zones for the Linux page allocator. State includes memblock reservations, PFN ranges, zone layouts, and boot memory allocator metadata. Dependencies include `linux/memblock.h`. Integration points are `setup_arch`, boot parameter memory tags, device tree memory discovery, and the page allocator. Risks are mismatched prototypes with implementation, bad memory ranges causing allocator corruption, and missed reserved regions. Test signals include boot memblock logs, `/proc/zoneinfo`, memory hotplug or sparsemem build coverage where applicable, and boot with multiple memory regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/sysmem.h -->
