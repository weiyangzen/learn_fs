# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/dma-octeon.c

Purpose: Octeon physical-to-DMA address translation and SWIOTLB setup for PCI generations and large memory layouts.

Important APIs and functions: `octeon_hole_phys_to_dma()` and `_dma_to_phys()` handle the platform memory hole. `octeon_gen1_*`, `octeon_gen2_*`, and `octeon_big_*` implement generation-specific DMA translation. `octeon_pci_dma_init()` selects translation mode from PCI type and memory layout. Exported `phys_to_dma()` and `dma_to_phys()` call the selected function pointers. `plat_swiotlb_setup()` reserves/initializes bounce buffering when needed.

Control flow: early boot chooses DMA translation callbacks based on Octeon PCI host mode and memory arrangement. Later DMA mapping code calls the exported translation hooks for devices.

State and persistence: global function pointers and SWIOTLB memory reservation are boot-time state. No disk persistence.

Dependencies and integration points: integrates Linux DMA direct mapping, memblock, SWIOTLB, PCI host setup, and Octeon NPI/PCI register definitions.

Risks and test signals: wrong translation corrupts DMA or makes PCI devices unusable above address windows. Test with PCI storage/network devices, high-memory DMA, SWIOTLB bounce stats, and data-integrity workloads under memory pressure.
