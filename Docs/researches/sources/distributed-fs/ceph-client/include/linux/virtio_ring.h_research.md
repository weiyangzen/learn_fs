# sources/distributed-fs/ceph-client/include/linux/virtio_ring.h

## Purpose
This header declares virtio ring construction, DMA policy, and vring interrupt APIs shared by virtio transports and vring implementations.

## Important APIs, types, and functions
Important APIs include `vring_create_virtqueue()`, `vring_create_virtqueue_dma()`, `vring_new_virtqueue()`, `vring_del_virtqueue()`, `vring_transport_features()`, `vring_interrupt()`, `vring_use_dma_api()`, `virtio_has_iommu_quirk()`, and weak barriers for virtqueue memory ordering. It connects generic `virtqueue` objects with UAPI `vring` layouts.

## Control flow, state, and persistence
Transports create or wrap vrings with callback/name/context metadata, DMA device information, queue index, ring size/alignment, and weak-barrier policy. Runtime data path enqueues descriptors through virtqueue APIs and receives interrupts through `vring_interrupt()`. State is allocated descriptor/avail/used ring memory, DMA mappings, callback suppression state, and queue private data.

## Dependencies and integration points
It depends on scatterlists, DMA mapping, virtio core, and virtio ring UAPI. It integrates PCI/MMIO/CCW/vDPA/VDUSE transports with the generic virtqueue API and platform DMA/IOMMU policy.

## Risks and test signals
Risks include wrong DMA API decision for legacy quirks, alignment/size mismatches, missing memory barriers, interrupt handling for broken queues, and teardown with outstanding buffers. Tests should cover split/packed ring creation where supported by implementation, DMA and non-DMA paths, notification interrupts, feature filtering, delete cleanup, and IOMMU quirk behavior.
