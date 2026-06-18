
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_common.h

Purpose: private shared header for virtio crypto core, manager, and algorithm implementations.

Important APIs, types, and functions: `struct data_queue` wraps a virtqueue, lock, queue name, crypto engine, and completion work. `struct virtio_crypto` stores the virtio device, control and data queues, config work, control lock, negotiated capability masks, size limits, status/refcount/list/owner/id, and affinity state. `struct virtio_crypto_ctrl_request` packages control operation, input/status, and completion. `struct virtio_crypto_request` is the common data-queue request envelope with status, request header, sg pointer array, queue pointer, and algorithm callback. Prototypes expose device-manager, algorithm registration, control request, request clear, and NUMA node helper APIs.

Control flow: no standalone runtime flow, but the header defines how core callbacks deliver completed virtqueue buffers to per-algorithm callbacks and how algorithm code finds devices and queues requests.

State and persistence: all state is in-memory kernel/module state. Device capability masks mirror virtio config space, while session ids are held by algorithm-specific contexts.

Dependencies and integration points: includes virtio, crypto, spinlock, workqueue, AES/AEAD, crypto engine, and `uapi/linux/virtio_crypto.h`. The inline NUMA helper briefly pins the current CPU to derive a node for device selection.

Risks and test signals: correctness depends on every data request setting `alg_cb`, `dataq`, `req_data`, and `sgs` consistently so `virtcrypto_clear_request()` can clean up. Capability masks are split into low/high fields for some services, so algorithm numbers above 31 need coverage. Test signals are sparse/clang builds across enabled algorithm subsets, hot-unplug with pending requests, and NUMA fallback device selection.
