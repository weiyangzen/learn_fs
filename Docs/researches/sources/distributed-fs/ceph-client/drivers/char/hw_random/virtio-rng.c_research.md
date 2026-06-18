# sources/distributed-fs/ceph-client/drivers/char/hw_random/virtio-rng.c

Purpose: virtio RNG frontend that exposes host-provided entropy through `hwrng`.

Important APIs, types, and functions: `struct virtrng_info`, `random_recv_done()`, `request_entropy()`, `copy_data()`, `virtio_read()`, `virtio_cleanup()`, common probe/remove, scan, freeze, restore, and virtio ID table.

Control flow: probe allocates per-device state and IDA index, finds the input virtqueue, marks device ready, and posts an initial input buffer. The virtio driver's `scan` callback registers hwrng. Completion callback obtains a used buffer, stores available length with release ordering, and completes waiters. Reads copy existing data, optionally wait for completion, and repost a buffer when drained. Remove/freeze marks removed, wakes waiters, unregisters hwrng if needed, resets device, deletes queues, and frees state.

State and persistence: per-device state tracks virtqueue, registration/removal flags, completion, data buffer/index/available length, and IDA index. No persistence outside virtio device lifetime.

Dependencies and integration: virtio core, scatterlists, completions, hwrng, IDA, DMA cacheline grouping, and PM freeze/restore.

Risks and test signals: synchronization relies on hwrng serialization plus release/acquire for `data_avail`; remove must wake blocking reads. Tests should cover nonblocking reads, interruptible wait, spurious callbacks, remove/freeze while waiting, restore registration ordering, IDA cleanup, and buffer repost after partial reads.
