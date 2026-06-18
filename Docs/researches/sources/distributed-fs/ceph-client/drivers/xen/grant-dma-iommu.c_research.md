# sources/distributed-fs/ceph-client/drivers/xen/grant-dma-iommu.c

Purpose: registers a dummy IOMMU provider for device-tree nodes compatible with `xen,grant-dma`, enabling generic IOMMU bindings to describe Xen grant-DMA backend-domain relationships.

Important APIs/functions: implements `grant_dma_iommu_probe_device`, `grant_dma_iommu_probe`, `grant_dma_iommu_remove`, and `grant_dma_iommu_init`. Core type is `struct grant_dma_iommu_device`.

Control flow: init first searches the device tree for a matching node and registers the platform driver only when one exists. Probe allocates driver data, registers an `iommu_device` with a minimal `iommu_ops`, and stores it on the platform device. The only IOMMU callback, `probe_device`, returns `-ENODEV`, because real DMA translation is implemented by the Xen grant DMA ops layer rather than by an IOMMU domain.

State and persistence: one small device-managed object tracks the platform device and registered IOMMU device for the driver's lifetime. Remove unregisters the IOMMU device and clears drvdata.

Dependencies and integration: depends on OF matching, platform driver core, and Linux IOMMU registration. It complements `grant-dma-ops.c`, whose device-tree parser expects `xen,grant-dma` IOMMU nodes with backend domid cells.

Risks: this intentionally does not attach devices or provide translation domains; consumers must not mistake it for a functional IOMMU. If the DT binding is absent, the driver does nothing.

Test signals: boot a DT Xen guest with and without a `xen,grant-dma` node, verify platform driver registration, and verify virtio/grant DMA setup still comes from `grant-dma-ops.c`.
