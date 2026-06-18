# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma-mapping.h

This header connects the generic DMA mapping API to Alpha's PCI DMA operations. It declares `alpha_pci_ops` and returns it from `get_arch_dma_ops`.

There is no internal state; DMA mapping state is managed by the implementation behind `alpha_pci_ops` and platform PCI/IOMMU code. Integration is broad across all DMA-capable drivers. Risks include selecting the wrong ops for systems with or without an IOMMU and stale assumptions in legacy ISA DMA paths. Tests include DMA API debug, PCI device I/O, and platforms with direct and translated DMA windows.
