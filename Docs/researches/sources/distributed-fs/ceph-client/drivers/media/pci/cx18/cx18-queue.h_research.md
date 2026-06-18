# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.h

Declares the cx18 queue API and inline helpers for DMA synchronization, MDL byte swapping, FIFO enqueue, and LIFO push. Key interfaces are `cx18_buf_sync_for_cpu`, `cx18_buf_sync_for_device`, `cx18_mdl_sync_for_device`, `cx18_mdl_swap`, `cx18_enqueue`, `cx18_push`, `cx18_dequeue`, `cx18_queue_get_mdl`, `cx18_load_queues`, and stream allocation/free.

The header integrates queue users with DMA ownership rules: buffers are synced for CPU after firmware completion and for device before submission. Single-buffer MDLs use fast inline paths while multi-buffer MDLs dispatch to implementation helpers.

State is not stored here, but the API mutates queue, MDL, and DMA state in callers. Risks are incorrect DMA direction/sync use, assuming immediate firmware ownership after enqueue, and byte-swapping the wrong stream type. Test signals are DMA-coherency capture tests, multi-buffer YUV/VBI paths, and compile coverage for all queue users.
