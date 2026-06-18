# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_9p.h

Purpose: defines the virtio 9P filesystem device configuration ABI.

Important APIs/types/functions: exports feature bit `VIRTIO_9P_MOUNT_TAG` and packed `virtio_9p_config`, which contains a little-endian tag length and a flexible, non-NUL-terminated mount tag byte array.

Control flow: a virtio 9P driver negotiates features through common virtio config mechanisms, reads the config space tag length and tag bytes, and uses that tag to select the exported 9P mount endpoint. Data-plane 9P requests are defined elsewhere; this header only covers the virtio-specific config surface.

State and persistence: persistent device state is the configuration-space mount tag. The tag length controls parsing and must be honored exactly because the byte array is not NUL-terminated.

Dependencies and integration: includes `linux/virtio_types.h`, `linux/virtio_ids.h`, and `linux/virtio_config.h`. It integrates with virtio transport, guest 9P clients, and host filesystem export implementations such as virtio-9p in VMMs.

Risks: length/tag parsing errors can cause overreads or incorrect mount selection. The flexible array means callers must allocate/read enough config bytes. The mount tag feature must be negotiated or otherwise treated according to virtio device behavior.

Test signals: virtio config layout checks, guest mount tests by tag, VMM/device tests with short and maximum tags, and negative tests for unterminated tag handling.
