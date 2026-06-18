
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_core.c

Purpose: virtio device driver core for virtio crypto. It probes virtio crypto devices, reads capability/configuration, allocates queues and crypto engines, handles control/data virtqueue callbacks, config changes, remove, and suspend/resume.

Important APIs, types, and functions: `virtcrypto_clear_request()` frees common request allocations. `virtio_crypto_ctrl_vq_request()` submits synchronous control queue commands. `virtcrypto_done_work()` drains completed data-queue buffers and invokes algorithm callbacks. `virtcrypto_find_vqs()`, `virtcrypto_init_vqs()`, and `virtcrypto_del_vqs()` manage virtqueues and per-data-queue engines. `virtcrypto_update_status()` starts/stops algorithm registration based on `VIRTIO_CRYPTO_S_HW_READY`. `virtcrypto_probe()`, `virtcrypto_remove()`, `virtcrypto_freeze()`, and `virtcrypto_restore()` implement driver lifecycle.

Control flow: probe requires virtio 1.0 and config access, rejects bad NUMA placement, allocates `virtio_crypto`, reads config fields, adds the device to the manager, initializes data/control queues, starts per-queue crypto engines, marks the device ready, updates hardware status, and installs config work. Data queue interrupts schedule bottom-half work that drains virtqueue buffers under a queue lock. Control queue callbacks complete synchronous waiters. Config changes schedule work that reads status and registers/unregisters algorithms through the manager.

State and persistence: per-device state includes capability masks, queue arrays, per-queue crypto engines, current status bits, refcount, list node, and affinity hints. Pending request state remains attached to virtqueue buffers until completion or detach during reset/remove. No persistent storage exists outside virtio device state.

Dependencies and integration points: integrates with the virtio bus through `module_virtio_driver`, virtio config access, vring size, virtqueue affinity, CPU masks, system bottom-half workqueue, crypto engine framework, and manager/algorithm modules. Device ID is `VIRTIO_ID_CRYPTO`.

Risks and test signals: `virtio_crypto_ctrl_vq_request()` waits without a timeout, so a broken host can hang control operations. `virtcrypto_find_vqs()` failure after allocating some per-queue engines relies on later reset/free paths and should be audited for partial cleanup. Affinity hints lack CPU hotplug notifier support per TODO. Test signals include virtio feature negotiation, queue count 0 fallback to 1, host status unknown-bit handling, config change start/stop, unplug with pending requests, suspend/resume, control queue failure, and multiple data queue initialization.
