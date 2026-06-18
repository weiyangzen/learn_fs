<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_iommu.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_iommu.h

Purpose: defines virtio IOMMU configuration, request, response, probe, and fault structures for attaching endpoints to domains and mapping or unmapping IOVA ranges.

Important APIs and types: feature bits include input/domain ranges, map/unmap, bypass, probe, MMIO, and bypass config. `struct virtio_iommu_config` advertises page sizes, input range, domain range, probe size, and bypass state. Request types include `ATTACH`, `DETACH`, `MAP`, `UNMAP`, and `PROBE`; status values report OK, unsupported, invalid, range, fault, and memory errors. `struct virtio_iommu_fault` reports endpoint faults.

Control flow, state, and persistence: the guest attaches an endpoint to a domain, submits map/unmap requests, probes reserved-memory properties, and receives fault notifications. Mapping state persists in the device until detached or unmapped, but the header owns no storage.

Dependencies and integration points: integrates virtio with the kernel IOMMU subsystem, DMA API, PCI/platform endpoint enumeration, and reserved MSI/MMIO regions.

Risks and test signals: high-risk areas are inclusive range handling, page-size validation, reserved-region parsing, bypass semantics, and fault reporting. Test attach/detach, overlapping maps, unmap holes, MSI reserved memory, bypass modes, and DMA fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_iommu.h -->
