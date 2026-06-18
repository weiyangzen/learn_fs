# sources/distributed-fs/ceph-client/include/uapi/linux/vhost_types.h

Purpose: defines the data structures and feature/backend flags used by vhost ioctls and vhost IOTLB messages.

Important APIs/types/functions: exports `vhost_vring_state`, `vhost_vring_file`, `vhost_vring_addr`, `vhost_worker_state`, `vhost_vring_worker`, `vhost_iotlb_msg`, `vhost_msg`, `vhost_msg_v2`, `vhost_features_array`, `vhost_memory_region`, `vhost_memory`, `vhost_scsi_target`, `vhost_vdpa_config`, and `vhost_vdpa_iova_range`. It defines access bits (`VHOST_ACCESS_RO/WO/RW`), IOTLB message types including miss/update/invalidate/access-fail and batch begin/end, memory page alignment via `VHOST_PAGE_SIZE`, SCSI ABI version, frontend feature bits such as `VHOST_F_LOG_ALL`, and backend feature bits such as `VHOST_BACKEND_F_IOTLB_MSG_V2`, `BATCH`, `ASID`, `SUSPEND`, `RESUME`, `DESC_ASID`, and `IOTLB_PERSIST`.

Control flow: these structs are passed to `vhost.h` ioctls or sent over vhost IOTLB message channels. Memory table setup passes a flexible `vhost_memory` array. Vring setup passes state, address, and eventfd structs. IOTLB backends send misses and receive mapping updates/invalidation, optionally with V2 ASIDs and batch hints. vDPA config reads/writes pass an offset/length/buffer descriptor.

State and persistence: the structures describe state installed in a vhost fd: guest memory map, vring addresses and bases, per-vring file descriptors, worker binding, backend IOTLB mappings, SCSI endpoint identity, vDPA config slices, and IOVA limits. Flexible arrays carry variable-sized state and must be sized exactly by userspace.

Dependencies and integration: includes `linux/types.h`, `linux/compiler.h`, `linux/virtio_config.h`, and `linux/virtio_ring.h`. It integrates with the vhost ioctl layer, virtqueue layout definitions, IOMMU/IOTLB handling, QEMU memory listeners, target SCSI WWPNs, and vDPA devices.

Risks: all region addresses and sizes must be 4K-aligned for memory tables. `vhost_vring_addr` alignment comments for descriptor/used/available/log addresses are ABI-relevant. IOTLB batching is only a hint and not guaranteed atomic. V2 IOTLB ASIDs require backend feature negotiation. Flexible arrays using `__counted_by` require careful allocation size calculation.

Test signals: compile/layout tests, vhost memory table alignment tests, IOTLB miss/update/invalidate tests, V2 ASID tests, SCSI ABI version tests, vDPA config range tests, and QEMU memory hotplug/migration paths that rebuild memory tables.
