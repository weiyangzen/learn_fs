# sources/distributed-fs/ceph-client/arch/x86/kernel/pci-dma.c

## Purpose
Coordinates x86 PCI DMA/IOMMU initialization, command-line IOMMU options, SWIOTLB fallback, Xen DMA bounce buffering, and a VIA DAC workaround.

## APIs, Types, And Functions
Exports `dma_ops`; global knobs include `panic_on_overflow`, `force_iommu`, `iommu_merge`, `no_iommu`, `iommu_detected`, `x86_swiotlb_enable`, and `disable_dac_quirk`. Main functions are `pci_iommu_alloc()`, `iommu_setup()`, `pci_iommu_init()`, Xen/SWIOTLB helpers, and VIA PCI fixup callbacks.

## Control Flow
`iommu_setup()` parses `iommu=` early parameters such as `off`, `force`, `noforce`, `merge`, `nomerge`, `panic`, `soft`, `pt`, and `nopt`, while warning for ignored DAC-related options. `pci_iommu_alloc()` chooses Xen SWIOTLB for Xen PV domains, otherwise detects SWIOTLB need, GART, AMD IOMMU, Intel IOMMU, and initializes SWIOTLB. `pci_iommu_init()` later runs `x86_init.iommu.iommu_init()` and either prints SWIOTLB info or exits SWIOTLB if disabled.

## State And Persistence
Boot parameters set global policy for the rest of the system. SWIOTLB allocation and DMA ops persist after rootfs init. The VIA fixup sets `bus_dma_limit` on subordinate devices to 32-bit unless `iommu=usedac` disables that quirk.

## Dependencies And Integration
Depends on memblock PFN sizing, confidential-computing attributes, Xen SWIOTLB, AMD/Intel/GART IOMMU detection, generic DMA map ops, PCI fixup infrastructure, and x86 init hooks.

## Risks And Test Signals
The main risks are broken DMA on encrypted-memory guests, too-small DMA address limits, unexpected passthrough defaults, or SWIOTLB being disabled when needed. Test signals include boot logs showing detected IOMMU/SWIOTLB mode, DMA stress on >4G memory systems, Xen PV PCI tests, encrypted guest I/O, and VIA bridge regression coverage.
