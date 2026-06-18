# sources/distributed-fs/ceph-client/drivers/virtio/virtio_dma_buf.c

## Purpose
`virtio_dma_buf.c` provides helpers for dma-bufs that represent virtio exported objects. It enforces a virtio-specific dma-buf ops wrapper so other virtio drivers can identify such buffers and query their exported object UUID.

## Important APIs, types, and functions
Exported functions are `virtio_dma_buf_export`, `virtio_dma_buf_attach`, `is_virtio_dma_buf`, and `virtio_dma_buf_get_uuid`. The implementation expects `struct virtio_dma_buf_ops`, whose embedded `dma_buf_ops` must use `virtio_dma_buf_attach` as `attach` and provide `get_uuid`; optional `device_attach` is called from the mandatory attach wrapper.

## Control flow
Export validates the ops shape and UUID callback before calling `dma_buf_export`. Attach recovers the virtio ops wrapper and delegates to optional device-specific attach logic. Type checking is implemented by comparing the dma-buf attach op pointer. UUID lookup first verifies the buffer is virtio-backed, then calls the ops `get_uuid`.

## State and persistence
This file owns no global state. State resides in the dma-buf object and exporter-provided private data/ops. UUID identity persists only as long as the dma-buf and underlying virtio object exist.

## Dependencies and integration points
It depends on the dma-buf framework and `linux/virtio_dma_buf.h`, imports the `DMA_BUF` namespace, and is intended for virtio devices such as GPU or media exporters/importers that need cross-device object identity.

## Risks and test signals
Risks include ops pointer spoofing assumptions, exporters bypassing the required attach wrapper, missing `get_uuid`, attach callback failures, and UUID lifetime mismatches with the underlying object. Test signals include valid export/import, invalid ops rejection, `is_virtio_dma_buf` on normal dma-bufs, UUID retrieval, optional `device_attach` failure propagation, and module namespace/build checks.
