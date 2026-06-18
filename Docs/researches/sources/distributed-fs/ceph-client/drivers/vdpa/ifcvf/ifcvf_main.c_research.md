# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_main.c

Purpose: PCI and vDPA management glue for Intel IFC VF devices. It registers a management device at PCI probe time and creates actual vDPA devices through management operations.

Important APIs/types/functions: interrupt handlers dispatch config, per-vq, shared-vq, or fully shared device interrupts to vDPA callbacks. IRQ setup helpers allocate MSI-X vectors and program hardware vectors. `ifc_vdpa_ops` implements vDPA operations over `ifcvf_base.c`. `ifcvf_vdpa_dev_add()` allocates/registers the `vdpa_device` and applies provisioned features. `ifcvf_probe()` enables PCI, maps BARs 0/2/4, initializes hardware, reads features/config size, sets the mgmt id table, and registers `vdpa_mgmt_dev`.

Control flow: PCI probe creates a management device, not an immediate vDPA dataplane device. `dev_add` allocates the adapter, validates requested features against hardware, stores provisioned features, names the vDPA device, and registers it. Status transition to `DRIVER_OK` requests IRQs; reset stops callbacks, frees IRQs if needed, and resets hardware. Queue operations directly call low-level helpers.

State and persistence: `ifcvf_vdpa_mgmt_dev` owns the hardware object and current adapter. `ifcvf_adapter` owns the registered vDPA device. IRQ allocation mode is stored in `msix_vector_status`; callbacks live in vring/config callback fields.

Dependencies and integration: Linux PCI managed resources, DMA mask setup, vDPA mgmt API, modern virtio PCI register helpers, net/block virtio IDs, and MSI-X.

Risks: `ifcvf_vdpa_dev_add()` returns `-EINVAL` after adapter allocation on unsupported provisioned features without explicitly putting the allocated device in that branch. IRQ fallback to shared vectors reduces `get_vq_irq()` support because shared vq IRQ returns `-EINVAL`. No `set_map()` implementation because hardware lacks on-chip IOMMU.

Test signals: probe/remove for supported IDs, mgmt dev add/del, feature provisioning mask validation, per-vq versus shared IRQ modes, DRIVER_OK transitions, reset, queue state migration, and vq notification area reporting.
