# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.c

Purpose: low-level Intel IFC VF hardware access layer for modern virtio PCI capabilities, queue registers, live migration state, config space, and notification.

Important APIs/types/functions: `ifcvf_init_hw()` parses vendor PCI capabilities, maps common/notify/isr/device config regions, computes per-queue notify addresses, and initializes IRQ sentinels. `ifcvf_get_hw_features()`, `ifcvf_set_driver_features()`, and `ifcvf_get_driver_features()` access feature registers. `ifcvf_get_config_size()`, `ifcvf_read_dev_config()`, and `ifcvf_write_dev_config()` handle config space. Queue operations include size, address, ready, notify, and LM state access through `ifcvf_get_vq_state()`/`ifcvf_set_vq_state()`. `ifcvf_stop()` synchronizes IRQs and resets handlers/vectors.

Control flow: init scans PCI capabilities from the capability list, validates all required virtio modern regions, allocates `vring_info` for `num_queues`, and records notify offsets. Queue setters select `queue_select` before touching queue registers. Reset writes status 0 and polls until the device reports reset. Config reads retry if `config_generation` changes.

State and persistence: `struct ifcvf_hw` holds MMIO pointers, notify geometry, vring array, feature/config sizes, callbacks, IRQ state, and device type. State lives for the PCI device/mgmt-device lifetime.

Dependencies and integration: used by `ifcvf_main.c`; depends on modern virtio PCI register layout, BAR mappings from pcim, live migration BAR 4, and vDPA/vhost feature constants.

Risks: pointer arithmetic against `ifcvf_lm_cfg.vq_state_region` must match hardware layout. `ifcvf_verify_min_features()` requires `VIRTIO_F_ACCESS_PLATFORM` for nonzero features. Config size is limited to known net/block structs; other virtio IDs return size 0.

Test signals: capability parsing with missing regions, queue notify address calculation, feature read/write, reset completion, config generation retry, queue state save/restore, and invalid queue id returning zero size.
