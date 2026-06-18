<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-buf.h

## Purpose
Defines the DMA-BUF sharing framework API for exporting buffers as file descriptors and attaching devices for cross-driver DMA and CPU access.

## Important APIs, Types, And Functions
Key types are `struct dma_buf_ops`, `struct dma_buf`, `struct dma_buf_attach_ops`, `struct dma_buf_attachment`, and `struct dma_buf_export_info`. Export/import APIs include `dma_buf_export()`, `dma_buf_fd()`, `dma_buf_get()`, `dma_buf_put()`, `dma_buf_attach()`, `dma_buf_dynamic_attach()`, `dma_buf_detach()`, pin/unpin, map/unmap attachment, invalidate mappings, CPU-access bracketing, mmap, vmap/vunmap, unlocked helpers, and iteration over exported buffers.

## Control Flow
An exporter fills `dma_buf_export_info` and provides mandatory ops such as `map_dma_buf`, `unmap_dma_buf`, and `release`. Userspace receives an fd. Importers get the buffer, attach a device, map an attachment for a DMA direction, perform access while obeying implicit synchronization fences in `dmabuf->resv`, then unmap, detach, and put references. Dynamic importers use invalidate callbacks and reservation locking rather than permanent pinning.

## State And Persistence
`struct dma_buf` stores invariant size, file reference, attachment list protected by the reservation lock, ops, vmap refcount/cache, exporter name, optional userspace name, owner module, global list node, private data, reservation object, poll wait queue, and fence callbacks. State is refcounted runtime sharing state; persistence is only via open file descriptors.

## Dependencies And Integration Points
Depends on files, scatterlists, DMA mapping, DMA fences, DMA reservation objects, wait queues, iosys maps, P2P DMA, mmap, and module ownership. It is central to DRM, V4L2, media, accelerator, and heap exporters.

## Risks And Edge Cases
Exporter and importer locking rules are strict. Dynamic mapping callbacks are called with `dma_resv` locked; non-dynamic importers pin storage. Exporters must guarantee backing storage availability and zeroing for non-dynamic paths. CPU access must be bracketed for cache coherency. Mmap exporters may need private address-space handling to zap PTEs. Attachment invalidation can race with device access unless importers add fences for non-revocable work.

## Test Signals
Tests should cover export/fd/get/put reference lifetime, attach failures, dynamic and static map/unmap, pin/unpin, fence-based implicit sync, CPU begin/end access, mmap size rejection, vmap refcounting, poll readiness, buffer naming, P2P attachments, and module unload/refcount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf.h -->
