# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue.c

Purpose: implements queue operations over local circular buffers and remote SP/HOST queue memory.

Important functions: local/remote init, uninit, enqueue, dequeue, full/empty checks, free/used space, peek, and get size.

Control flow: local paths call `ia_css_circbuf_*` directly. Remote paths load a circular-buffer descriptor with selected ignore flags, check full/empty/bounds, load/store an element when needed, update `start` or `end`, and store only changed descriptor fields. Size query can skip mutable indices and read descriptor size only.

State/persistence: local queue state lives in caller-provided descriptor/element buffers. Remote queue state persists in SP DMEM or HMM memory at addresses in the queue handle.

Dependencies/integration: `queue_access.c`, circular-buffer helpers, math support. Event/eventq and buffer queue code build on this layer.

Risks: remote operations are multi-step and not protected from concurrent writers. `ia_css_queue_peek` treats `offset > num_elems` as invalid, which allows `offset == num_elems` even though that is past the last valid element. `ia_css_queue_get_size` returns 0 for unknown queue type.

Test signals: wraparound enqueue/dequeue, remote descriptor zero-size `-EDOM`, peek offset boundary, unsupported ISP remote access, and consistency under producer/consumer sequencing.
