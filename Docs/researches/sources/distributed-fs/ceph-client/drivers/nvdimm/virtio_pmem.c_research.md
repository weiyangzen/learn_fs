# sources/distributed-fs/ceph-client/drivers/nvdimm/virtio_pmem.c

Purpose: Implements virtio-pmem device discovery and libnvdimm region registration. It exposes a virtio-provided persistent memory range as an asynchronous-flush PMEM region.

Important APIs and flow: `init_vq()` creates the single flush virtqueue with `virtio_pmem_host_ack()`, initializes the spinlock, and initializes the pending request list. `virtio_pmem_validate()` verifies the shared-memory feature has a valid region and clears the feature if not. `virtio_pmem_probe()` allocates `struct virtio_pmem`, initializes flush locking and virtqueue state, reads start/size from a virtio shared-memory region or config space, registers an NVDIMM bus, fills an `nd_region_desc` with NUMA nodes, async flush callback, provider data, pagemap and async flags, marks the virtio device ready, and creates a PMEM region. Remove/freeze/restore unregister or reset queues and restore virtqueue readiness.

State and persistence behavior: Runtime state is `struct virtio_pmem` plus the registered NVDIMM bus. Persistent data is the host-backed memory range; persistence is guaranteed by virtio flush requests handled in `nd_virtio.c`.

Dependencies and integration points: Depends on virtio PMEM IDs/features, shared memory regions, libnvdimm bus/region creation, NUMA helpers, and the asynchronous flush callback exported by `nd_virtio.c`.

Risks and test signals: `virtio_device_ready()` is intentionally called before region creation because libnvdimm may expose the region immediately. Tests should cover config-space and shared-memory discovery, invalid shared-memory feature fallback, region creation failure cleanup, suspend/resume restore of virtqueues, reset-needed flush rejection, and remove while requests are pending.
