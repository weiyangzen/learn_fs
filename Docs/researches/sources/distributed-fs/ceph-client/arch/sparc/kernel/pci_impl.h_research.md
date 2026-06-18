# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_impl.h

## Purpose
Internal SPARC PCI PBM abstraction shared by all controller drivers. It centralizes PBM topology, resources, IOMMU/streaming-buffer state, MSI queue state, bus scan hooks, and config-space declarations.

## Important APIs, Types, and Functions
`struct pci_pbm_info` tracks root/sibling linkage, register bases, port/dev handles, chip identity, OF device, IO/MEM resources and offsets, config-space width/base, PCI bus and ops, NUMA node, streaming buffer, IOMMU pointer, and optional MSI fields. `struct sparc64_msiq_ops` abstracts controller-specific MSI queues. `struct sparc64_msiq_cookie` binds queue IRQs to PBM/queue ids. The header declares shared PBM property/resource helpers, bus scanning, error scanners, config accessors, and `sun4u_pci_ops` / `sun4v_pci_ops`.

## Control Flow
Controller probes allocate/fill `pci_pbm_info`, call shared helpers, and link PBMs into `pci_pbm_root`. PCI core reaches config operations through `pbm->pci_ops`; DMA and MSI paths reach `pbm->iommu` and `pbm->msi_ops`.

## State and Persistence
Defines runtime-only state. The PBM list and sibling fields establish boot-time topology; MSI bitmaps, IRQ tables, queue buffers, IOMMU tables, and streaming buffers are allocated elsewhere.

## Dependencies and Integration Points
Includes Linux PCI/MSI/spinlock types and SPARC IO/PROM/IOMMU definitions. Included by FIRE, PSYCHO, SABRE, SCHIZO, sun4v, common PCI, and MSI files.

## Risks and Test Signals
Field semantics vary by controller, especially shared versus per-PBM IOMMU and config register width. `CONFIG_PCI_MSI` ifdefs must match implementation files. Test with builds both with and without MSI and successful probes across supported controller drivers.
