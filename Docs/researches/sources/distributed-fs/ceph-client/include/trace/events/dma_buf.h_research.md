<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_buf.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dma_buf.h

## Purpose
Provides tracepoints for dma-buf lifetime, mapping, file-descriptor export/import, and device attachment operations. It is aimed at shared-buffer debugging across graphics, media, and accelerator drivers.

## APIs, Control Flow, and State
Three event classes model common payloads: `dma_buf` records exporter name, size, and backing inode; `dma_buf_attach_dev` adds attachment pointer, dynamic-attach flag, and device name; `dma_buf_fd` adds the file descriptor. Instances include `dma_buf_export`, `dma_buf_mmap_internal`, `dma_buf_mmap`, `dma_buf_put`, `dma_buf_dynamic_attach`, `dma_buf_detach`, `dma_buf_fd`, and `dma_buf_get`. `dma_buf_fd` uses `DEFINE_EVENT_CONDITION()` so failed fd installation with negative descriptors is not emitted. No persistent state is created here; the tracepoint payload snapshots `struct dma_buf`, `struct dma_buf_attachment`, and `struct device` fields.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/dma-buf.h>`, inode access through `dmabuf->file`, device names, and tracepoint macros. Integration points are dma-buf export/import, mmap, reference dropping, attachment setup/teardown, and fd lookup/creation paths. Risks include dereferencing partially constructed dma-bufs, stale or null `dmabuf->file`, tracing attachment pointers that can be reused, and assuming fd traces include failed negative-fd attempts. Test signals include dma-buf selftests, GPU/media buffer sharing workloads, fd leak diagnosis, mmap tracing, and attach/detach pairing under dynamic attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_buf.h -->
