# sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.h

Purpose: Defines the shared data structures for the virtio-pmem discovery driver and the NVDIMM flush transport.

Important APIs and types: `struct virtio_pmem_request` wraps a virtio request/response pair, host-ack waitqueue, descriptor-availability waitqueue, completion flags, and queue list entry. `struct virtio_pmem` stores the virtio device, flush virtqueue, flush mutex, NVDIMM bus and descriptor, deferred request list, spinlock, and memory range start/size. It declares `virtio_pmem_host_ack()` and `async_pmem_flush()`.

State and persistence behavior: This header defines runtime synchronization and request state. No media metadata is stored here; the range fields describe the persistent region exposed by the host.

Dependencies and integration points: Depends on virtio PMEM UAPI, libnvdimm, mutexes, spinlocks, and module definitions. Used by both `virtio_pmem.c` and `nd_virtio.c`.

Risks and test signals: The request object is stack-independent heap state because virtqueue completion happens asynchronously. Tests should exercise list ownership, waitqueue wakeups, and lock ordering between `flush_lock` and `pmem_lock`.
