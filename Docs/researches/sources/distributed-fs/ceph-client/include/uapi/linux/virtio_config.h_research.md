# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_config.h

Purpose: defines common virtio configuration status bits and transport feature bit numbers shared by virtio device-specific UAPI headers.

Important APIs/types/functions: status bits include `VIRTIO_CONFIG_S_ACKNOWLEDGE`, `DRIVER`, `DRIVER_OK`, `FEATURES_OK`, `NEEDS_RESET`, and `FAILED`. Transport feature range is `VIRTIO_TRANSPORT_F_START` through `VIRTIO_TRANSPORT_F_END`. Feature bits include legacy `VIRTIO_F_NOTIFY_ON_EMPTY` and `VIRTIO_F_ANY_LAYOUT`, `VIRTIO_F_VERSION_1`, `VIRTIO_F_ACCESS_PLATFORM`/legacy alias `VIRTIO_F_IOMMU_PLATFORM`, packed rings, in-order use, platform ordering, SR-IOV, notification data/config data, per-queue reset, and admin virtqueue.

Control flow: virtio drivers use status bits to acknowledge, bind, negotiate features, confirm `FEATURES_OK`, set up queues/config, and finally set `DRIVER_OK`. Device reset/error paths use `NEEDS_RESET` and `FAILED`. Feature bits are negotiated before device-specific queues and config fields are consumed.

State and persistence: the header defines the status byte and feature bit meanings, but the transport stores them in device config space or transport-specific registers. Negotiated feature state persists until reset.

Dependencies and integration: includes `linux/types.h`. It is included by most virtio UAPI device headers and integrates with virtio-pci, MMIO, CCW, vDPA, vhost, and all virtio drivers.

Risks: `VIRTIO_F_ACCESS_PLATFORM` has reverse-polarity history and an old alias, so DMA isolation behavior must be interpreted carefully. Status transitions have ordering semantics; setting `DRIVER_OK` too early or ignoring `FEATURES_OK` failure breaks devices. Transport feature bits must not collide with device-specific feature spaces.

Test signals: virtio feature negotiation tests, status transition tests, packed-ring and ring-reset tests, platform DMA/IOMMU tests, and cross-header compile checks for shared feature definitions.
