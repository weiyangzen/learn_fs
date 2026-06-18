# sources/distributed-fs/ceph-client/drivers/xen/grant-dma-ops.c

Purpose: provides DMA mapping operations for Xen frontends, especially virtio, where DMA addresses are encoded grant references that a backend domain can map instead of host physical addresses.

Important APIs/functions: main exported integration is `xen_virtio_restricted_mem_acc`. Internal DMA ops implement allocation/free, page allocation/free, phys and sg mapping/unmapping, and mask support through `xen_grant_dma_ops`. State is tracked by `struct xen_grant_dma_data` in `xen_grant_dma_devices`.

Control flow: backend domid discovery first parses device-tree IOMMU bindings, including PCI `iommu-map`, and otherwise may force dom0 for non-initial PV or configured virtio grant mode. Setup stores per-device backend data and replaces `dev->dma_ops`. Allocation allocates exact pages, reserves a sequential grant-ref range, grants every page to the backend, and returns a DMA address with the high marker bit set. Map-phys creates grants over the target physical range and encodes the first ref plus offset. Unmap/free ends foreign access for every grant and frees the grant sequence; if the backend still holds a grant, the device is marked broken to prevent unsafe reuse.

State and persistence: per-device data stores backend domid and a `broken` flag. The xarray persists for device lifetime through devm allocation. Grant references are transient per DMA allocation or mapping.

Dependencies and integration: depends on DMA map ops, Xen grant table, OF/IOMMU bindings, PCI RID mapping, virtio restricted memory access hooks, and Xen mode checks.

Risks: grant reuse is disabled permanently for a device if a backend fails to release access; only a 64-bit DMA mask is supported; MMIO mappings are rejected; scatterlist failure unwinds previously mapped entries; address encoding depends on the high bit and page-shift layout.

Test signals: boot virtio devices with `xen,grant-dma` bindings, exercise coherent and streaming DMA, sg map failure unwinds, backend-domid parsing for PCI and platform devices, forced-grant fallback, and backend-not-releasing grants triggering `broken`.
