## sources/distributed-fs/ceph-client/drivers/virtio/virtio_vdpa.c

Purpose: this file is the bridge that registers vDPA devices as virtio devices and implements virtio config operations on top of `vdpa_config_ops`.

Important APIs/types/functions: `struct virtio_vdpa_device` embeds `struct virtio_device` and points to the backing `vdpa_device`. Config operations include config get/set, generation, status, reset, feature retrieval/finalization, queue creation/deletion, bus name, and queue affinity. Queue setup is centered on `virtio_vdpa_setup_vq()`, with notification through `kick_vq` or `kick_vq_with_data`.

Control flow: probe allocates a virtio-vdPA wrapper, selects the parent DMA device or vDPA device, fills `virtio_config_ops`, reads device/vendor IDs, registers the virtio device, and stores driver data. `find_vqs` builds optional affinity masks, creates each named virtqueue with `vring_create_virtqueue_map()`, installs callbacks into the vDPA device, programs queue size, descriptor/driver/device addresses, initial state, and ready bit, then installs the config callback. Removal unregisters the virtio device; queue deletion clears ready and deletes vrings.

State and persistence behavior: state is kernel-memory only and tied to virtio/vDPA device lifetime. Queue readiness and addresses are stored in the vDPA device via config ops; virtqueue memory/state is owned by virtio ring code.

Dependencies and integration points: depends on vDPA bus APIs, virtio core, virtio ring exported APIs, CPU affinity helpers, and optional custom DMA maps from the vDPA device.

Risks: feature negotiation must clear `VIRTIO_F_NOTIFICATION_DATA` when no data-kick op exists. Queue index accounting skips unnamed queues but still uses sequential vDPA queue indexes. Error unwind must leave queues not ready. Affinity mask generation can fail under memory pressure.

Test signals: probe with valid/zero device ID, split and packed queues, notification-data feature with and without `kick_vq_with_data`, queue ready failure unwind, queue state programming, affinity callback behavior, and virtio feature finalization with `vring_transport_features()`.
