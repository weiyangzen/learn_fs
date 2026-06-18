# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-dma.c

Purpose: DMA address translation for SGI O2's split CPU/device memory view.

Important APIs and control flow: `phys_to_dma()` masks physical addresses to the low 1 GB window and adds `CRIME_HI_MEM_BASE` for non-PCI devices passed as `dev == NULL`. `dma_to_phys()` masks DMA addresses and maps addresses at or above 256 MB back into the high CRIME memory base.

State, persistence, and integration: no state; these are architecture DMA translation hooks used by DMA-direct. Dependencies include device callers distinguishing PCI devices from native MACE/CRIME devices by `dev` presence. Risks include subtle incorrect mappings if a non-PCI device passes a non-NULL device or if memory layout assumptions change. Test signals are successful PCI and MACE DMA to high memory, especially Ethernet/audio/SCSI transfers above 256 MB.
