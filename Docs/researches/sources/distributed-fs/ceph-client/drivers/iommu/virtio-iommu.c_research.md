# sources/distributed-fs/ceph-client/drivers/iommu/virtio-iommu.c

Purpose: Provides the paravirtualized virtio IOMMU driver. It translates Linux IOMMU domain operations into virtqueue requests, keeps a software shadow of mappings, probes endpoint reserved regions, supports identity/bypass domains, and handles virtio fault events.

Important APIs/types/functions: `struct viommu_dev`, `struct viommu_domain`, `struct viommu_endpoint`, `struct viommu_mapping`, `viommu_send_req_sync()`, `viommu_add_req()`, `viommu_replay_mappings()`, `viommu_probe_endpoint()`, `viommu_attach_dev()`, `viommu_map_pages()`, `viommu_unmap_pages()`, `viommu_get_resv_regions()`, `viommu_probe()`, and `viommu_remove()`.

Control flow: Probe verifies required virtio features, initializes request/event virtqueues, reads config ranges and page masks, reserves a bypass-domain ID when supported, fills event buffers, and registers the IOMMU device against the parent bus. Device probe resolves the virtio IOMMU by fwnode, allocates endpoint state, and optionally sends a PROBE request to populate reserved memory. Domain allocation gets an ID from `ida`, records geometry/map flags, and initializes an interval tree.

State and persistence: Mapping state persists in `vdomain->mappings`, an interval tree protected by `mappings_lock`. MAP/UNMAP requests are queued and synchronized by `iotlb_sync*`, while attach/probe/detach are synchronous. Domains with zero endpoints retain their shadow mappings so `viommu_replay_mappings()` can recreate device state on reattach.

Dependencies/integration: Integrates with virtio config/queues, Linux IOMMU core, OF fwspec IDs, PCI/generic IOMMU grouping, `dma-iommu` reserved regions, MSI reservation helpers, interval trees, and module virtio-driver registration.

Risks and test signals: Exercise queue-full retry, zero-length virtqueue completions, map flag validation, unmap attempts that split an existing MAP range, attach failure with `nr_endpoints` accounting, endpoint PROBE overflow checks, bypass identity behavior, event queue refilling, and removal while requests/events are outstanding.
