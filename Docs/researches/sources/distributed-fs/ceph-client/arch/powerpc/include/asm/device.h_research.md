## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/device.h

Purpose: defines PowerPC per-device architecture data embedded in Linux device structures.

Important APIs/types/functions: `struct dev_archdata` carries `dma_offset`, optional PPC64 IOMMU table and PCI device-node data, optional EEH device pointer, fail-IOMMU flag, and SR-IOV data. `struct pdev_archdata` stores platform-device DMA mask and private PMU cleanup data.

Control flow: no algorithms. Bus and DMA/IOMMU setup code initialize these fields; DMA and PCI paths later consume them.

State and persistence: per-device state persists for the device lifetime and controls DMA address translation, IOMMU association, EEH recovery, PCI data, and SR-IOV metadata.

Dependencies and integration: integrates with `dma-direct.h`, PPC64 IOMMU, PCI/pci_dn, EEH, fail-IOMMU fault injection, SR-IOV, and platform-device registration.

Risks and test signals: stale or missing archdata causes bad DMA addresses, lost EEH association, or SR-IOV cleanup bugs. Test signals include DMA mapping tests, PCI hotplug, EEH recovery, IOMMU fault injection, SR-IOV enable/disable, and platform PMU unregister paths.
