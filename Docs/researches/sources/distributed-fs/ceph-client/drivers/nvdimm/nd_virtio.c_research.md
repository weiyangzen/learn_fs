# sources/distributed-fs/ceph-client/drivers/nvdimm/nd_virtio.c

Purpose: Provides the virtio-pmem flush transport used by libnvdimm regions created by `virtio_pmem.c`. It translates NVDIMM flush requests into virtqueue commands and supports asynchronous bio chaining for block-layer flushes.

Important APIs and flow: `virtio_pmem_host_ack()` is the virtqueue callback. It drains completed request buffers, marks each request done, wakes waiters, and wakes one queued submitter waiting for descriptor space. `virtio_pmem_flush()` serializes device flushes with `flush_lock`, rejects devices needing reset, allocates a request, submits request/response scatterlists, waits for descriptor availability on `-ENOSPC`, kicks the queue, waits for host completion, and returns the host status. `async_pmem_flush()` either builds a child `REQ_PREFLUSH` bio chained to the parent or synchronously calls `virtio_pmem_flush()`.

State and persistence behavior: Per-request waitqueues and flags track completion and descriptor availability. `vpmem->req_list` holds blocked flush requests when the virtqueue is full; `pmem_lock` protects the virtqueue and wait list. Persistence is delegated to the host response for `VIRTIO_PMEM_REQ_TYPE_FLUSH`.

Dependencies and integration points: Uses `struct virtio_pmem` from `virtio_pmem.h`, virtqueue APIs, libnvdimm `nd_region->flush`, block bios, and the `virtio_pmem` platform registration path.

Risks and test signals: Flush requests use `GFP_ATOMIC` while holding a spinlock and wait outside the lock on descriptor exhaustion. Tests should cover queue-full wakeups, host error status propagation, child bio chaining, device reset status, remove/freeze while flushes are in flight, and multiple concurrent flush callers serialized by `flush_lock`.
