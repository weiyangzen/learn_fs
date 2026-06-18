<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.c

Purpose: Implements the PDS vDPA management-device callbacks and `vdpa_config_ops` for a virtio-net VF backed by PDS firmware/adminq and virtio PCI modern config space.

Important APIs/functions: `pds_vdpa_dev_add()` and `pds_vdpa_dev_del()` create/delete one vDPA device per VF. The `pds_vdpa_ops` table implements queue address/size/kick/callback/ready/state/notification/IRQ/group, feature negotiation, config callbacks, status/reset, config reads/writes, and identity. `pds_vdpa_get_mgmt_info()` retrieves firmware identity via DMA-mapped adminq output.

Control flow: `dev_add` rejects multiple devices per VF, allocates `struct pds_vdpa_device`, verifies PCI status, applies requested feature mask, resets and initializes firmware, calculates queue count from firmware max VQs and requested max VQ pairs, sets MAC, maps notification addresses, initializes VQ entries, registers PDS event notifier, registers the vDPA device, and creates debugfs. Status transition to `DRIVER_OK` allocates one MSI-X vector per supported VQ; transition to `FEATURES_OK` maps notify pages; status reset clears callbacks, resets hardware, zeroes indices, and restores MAC. Queue ready true sends VQ init adminq; false sends VQ reset and stores returned indices.

State and persistence: `struct pds_vdpa_device` stores supported/negotiated features, selected MAC, num_vqs, callbacks, notifier, and an array of `pds_vdpa_vq_info` with addresses, q length, IRQ, notify mapping, and migration indices. Firmware persists active VQ and device status until reset.

Dependencies and integration points: Uses PDS adminq wrappers, virtio PCI modern helpers, PCI MSI-X, vDPA bus, netlink-supplied `vdpa_dev_set_config`, PDS event notifier API, and debugfs. `vmap.dma_dev` points to the VF PCI device for DMA mapping.

Risks: Driver requires `VIRTIO_F_ACCESS_PLATFORM` when any features are negotiated. It advertises `VIRTIO_NET_F_MAC` even if hardware lacks it and strips the bit before writing features to hardware. VQ state get/set is forbidden while ready. Split rings lack a used index, so used is forced to avail for interoperability. IRQ allocation asks for `max_supported_vqs`, but only requests IRQ handlers for `num_vqs`.

Test signals: Netlink add with feature/MAC/max-vq-pair masks, invalid unsupported features, missing access-platform negotiation, queue ready toggles, packed and split state migration, PDS reset/link-change notifier triggering config callback, debugfs contents, and MSI-X allocation/release on DRIVER_OK transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.c -->
