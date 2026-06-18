# sources/distributed-fs/ceph-client/include/linux/virtio_config.h

## Purpose
This header defines virtio transport configuration operations, DMA mapping operations, feature helpers, virtqueue discovery helpers, device-ready sequencing, endian-safe config accessors, and conditional feature reads.

## Important APIs, types, and functions
Key types are `virtio_shm_region`, `virtqueue_info`, `virtio_config_ops`, and `virtio_map_ops`. Important helpers include feature test/set/clear wrappers, `virtio_get_features()`, `virtio_has_dma_quirk()`, `virtio_find_vqs()`, `virtio_find_single_vq()`, `virtio_synchronize_cbs()`, `virtio_device_ready()`, bus name and affinity helpers, shared-memory lookup, endian conversions, `virtio_cread/cwrite` macros, little-endian config accessors, `__virtio_cread_many()`, byte/16/32/64 accessors, and feature-gated reads.

## Control flow, state, and persistence
Transports implement config ops for get/set/status/reset/find_vqs/features/shared memory/queue reset. Drivers use helpers to negotiate features, allocate queues, synchronize callbacks, set DRIVER_OK, and read/write config fields with generation-stable multi-byte reads. Runtime state is in `virtio_device`, transport config space, virtqueues, and mapping tokens. Nothing is persisted by this header.

## Dependencies and integration points
It depends on virtio core, byteorder helpers, compiler type checking, errno/bug helpers, and virtio UAPI config bits. It integrates every virtio transport and driver with feature negotiation, queue setup, DMA mapping, and config space access.

## Risks and test signals
Risks include sleeping config ops called from atomic context, missing generation retry for large fields, wrong endian accessor choice, feature checks for driver-unoffered bits, and queue reset callback synchronization. Tests should cover feature arrays, config read/write type checks, generation-change retry, DRIVER_OK sequencing, queue affinity, shared memory, DMA map ops, and feature-gated access.
