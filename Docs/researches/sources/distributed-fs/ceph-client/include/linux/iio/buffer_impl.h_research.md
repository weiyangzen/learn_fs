# `sources/distributed-fs/ceph-client/include/linux/iio/buffer_impl.h`

Purpose: internal IIO buffer implementation contract defining buffer access callbacks, core buffer state, update operations, refcounting, and DMABUF signaling when `CONFIG_IIO_BUFFER` is enabled.

Important APIs/types/functions: `INDIO_BUFFER_FLAG_FIXED_WATERMARK`, `struct iio_buffer_access_funcs`, `struct iio_buffer`, `iio_update_buffers`, `iio_buffer_init`, `iio_buffer_get`, `iio_buffer_put`, and `iio_buffer_signal_dmabuf_done`.

Control flow and state: `struct iio_buffer` persists length, flags, bytes-per-datum, direction, access ops, scan mask, demux list/bounce buffer, poll queue, watermark, sysfs attribute groups/lists, attached/current buffer list nodes, kref, and DMABUF list protected by mutex. `iio_update_buffers` tears down and rebuilds active buffering when inserting/removing buffers.

Dependencies/integration: depends on sysfs, kref, IIO public buffer API, UAPI buffer definitions, and optional DMABUF/DMA types. With buffers disabled, get/put stubs no-op.

Risks: implementation callbacks have strict context rules, especially `store_to`; enable/disable calls must balance; demux and scan masks must match channel layout; refcount release must free all resources; DMABUF queue locking must be respected.

Test signals: custom buffer implementation callback coverage, attach/update/detach active buffers, watermark behavior, poll/read/write, refcount release, DMABUF attach/enqueue/done, and builds with `CONFIG_IIO_BUFFER=n`.
