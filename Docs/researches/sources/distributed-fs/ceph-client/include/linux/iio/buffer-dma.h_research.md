# `sources/distributed-fs/ceph-client/include/linux/iio/buffer-dma.h`

Purpose: reusable IIO DMA buffer queue framework for block-based DMA capture/output, file I/O, and DMABUF attachment/enqueue handling.

Important APIs/types/functions: `enum iio_block_state`, `struct iio_dma_buffer_block`, `struct iio_dma_buffer_queue_fileio`, `struct iio_dma_buffer_queue`, `struct iio_dma_buffer_ops`, block done/list abort, enable/disable/read/write/usage/update, bytes-per-datum/length setters, init/exit/release, DMABUF attach/detach/enqueue, queue lock/unlock, and DMA device getter.

Control flow and state: queue state embeds `struct iio_buffer`, device, ops, mutex for configuration/file I/O, spinlock for list changes in atomic context, incoming list, active flag, DMABUF count, and file-I/O double-buffer state. Blocks move through queued, active, done, and dead states with kref-managed lifetime and optional fences/sg tables.

Dependencies/integration: depends on IIO buffer internals, DMA/DMABUF/fence/sg types, mutex/spinlock/list/kref/atomic. DMA-capable IIO drivers supply submit/abort callbacks.

Risks: block state transitions cross mutex/spinlock contexts; fileio and DMABUF modes must not race; cyclic transfers and fences require correct completion signaling; DMA addresses and sg tables must match device DMA constraints; abort must drain active lists.

Test signals: enable/disable while queued, read/write fileio, block completion ordering, abort paths, DMABUF attach/enqueue/detach with fences, cyclic mode, length/BPD changes, and lockdep under IRQ completion.
