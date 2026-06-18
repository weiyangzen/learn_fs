# sources/distributed-fs/ceph-client/include/linux/virtio_dma_buf.h

## Purpose
This header defines dma-buf integration for virtio exported objects identified by UUIDs.

## Important APIs, types, and functions
Key type is `virtio_dma_buf_ops`, embedding base `dma_buf_ops` plus optional `device_attach` and required `get_uuid`. APIs are `virtio_dma_buf_attach()`, `virtio_dma_buf_export()`, `is_virtio_dma_buf()`, and `virtio_dma_buf_get_uuid()`.

## Control flow, state, and persistence
Exporters provide virtio-aware dma-buf ops, export an object, and attach devices through `virtio_dma_buf_attach()` so virtio-specific attach validation can run. UUID lookup lets consumers identify shared objects. State is dma-buf lifetime and exporter private state.

## Dependencies and integration points
It depends on dma-buf, UUID, and virtio core APIs. It integrates virtio GPU or other virtio object exporters with generic dma-buf consumers.

## Risks and test signals
Risks include using the wrong attach op, missing UUID callbacks, and object identity collisions. Tests should cover export, attach success/failure, UUID retrieval, type detection, and dma-buf release paths.
