# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ropes.h

Purpose: describes PA-RISC SBA/Ike/Astro/Pluto IOMMU and LBA PCI host bridge data structures and register offsets, historically named around chipset ropes.

Important APIs/types/functions: defines `struct ioc`, `struct sba_device`, `struct lba_device`, chipset ID helpers `IS_ASTRO/IS_IKE/IS_PLUTO/IS_ELROY/IS_MERCURY/IS_QUICKSILVER`, IOMMU page-directory constants, IOC/LMMIO/rope register offsets, and IOSAPIC registration declarations.

Control flow: PCI/IOMMU setup identifies chipset type, maps SBA/LBA registers, initializes IOC page directories/resource maps, routes PCI ropes, registers IOSAPICs, and serves DMA map/unmap requests.

State and persistence: `sba_list`, IOC resource maps, page directories, delayed unmap queues, and host-bridge data persist for the life of the system. Dependencies and integration: used by `drivers/parisc/sba_iommu.c`, LBA PCI, IOSAPIC, DMA mapping, and PCI resource code.

Risks and test signals: IOMMU page-size/resource-map mistakes cause device DMA memory corruption. Test PCI DMA, IOMMU unmap flushes, AGP/Pluto paths, and multi-IOC systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
