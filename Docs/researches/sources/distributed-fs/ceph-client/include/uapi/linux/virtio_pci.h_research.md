<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pci.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pci.h

Purpose: defines legacy and modern virtio PCI transport registers, PCI vendor capabilities, common configuration layout, and virtio admin command data structures.

Important APIs and types: legacy offsets include host/guest features, queue PFN, queue select/notify, status, ISR, MSI-X vectors, and config offset helpers. Modern capability types identify common config, notify config, ISR, device config, PCI config access, shared memory, and vendor data. `struct virtio_pci_common_cfg` and `struct virtio_pci_modern_common_cfg` hold feature selectors, queue configuration, notification data, queue reset, and admin queue info. Admin structures cover command headers/status, legacy register access, notify info, capability query/set, resource objects, device parts metadata/get/set, and device mode.

Control flow, state, and persistence: PCI enumeration discovers caps, driver negotiates features, configures queues, maps notify regions, and optionally uses admin queues for SR-IOV/member management. State is volatile PCI/device state.

Dependencies and integration points: used by virtio-pci, PCI core, MSI-X, SR-IOV, transitional devices, and user-space device models.

Risks and test signals: risks include using `sizeof` on extensible common cfg, wrong capability lengths, queue address ordering, MSI vector disable handling, and admin flexible-array parsing. Test legacy/modern/transitional devices, MSI-X on/off, queue reset, shared memory caps, and admin command error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pci.h -->
