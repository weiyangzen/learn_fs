# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_fs.h

Purpose: defines the virtio-fs device configuration ABI for sharing a host filesystem with a guest.

Important APIs/types/functions: exports packed `virtio_fs_config`, containing a fixed 36-byte UTF-8 filesystem tag padded with NULs and little-endian `num_request_queues`. It also defines `VIRTIO_FS_SHMCAP_ID_CACHE` for identifying the DAX/cache shared-memory PCI capability.

Control flow: after virtio feature negotiation, the guest reads the tag to identify the mountable filesystem and reads `num_request_queues` to size request virtqueues. If shared memory capabilities are exposed through virtio-pci, the cache region is identified by `VIRTIO_FS_SHMCAP_ID_CACHE`.

State and persistence: config-space state is the filesystem tag and queue count. Data-plane filesystem state is handled by FUSE/virtiofs request queues and optional shared cache memory outside this header.

Dependencies and integration: includes Linux types and common virtio id/config/type headers. It integrates with virtio transport, virtiofs guest drivers, host virtiofsd/VMM implementations, FUSE protocol handling, and DAX shared-memory mappings.

Risks: the tag is fixed-size and not necessarily a conventional C string beyond NUL padding. Queue count must match device-provided virtqueues. Shared-memory capability IDs must be interpreted through the transport-specific capability table.

Test signals: virtio-fs mount tests by tag, queue count/config parsing tests, DAX cache shared-memory discovery tests, and VMM/virtiofsd integration tests.
