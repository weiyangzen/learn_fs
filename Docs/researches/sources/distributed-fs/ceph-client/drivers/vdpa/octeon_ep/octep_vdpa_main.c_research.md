<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_main.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_main.c

Purpose: Provides the Marvell Octeon PCI vDPA driver: PF SR-IOV setup, VF firmware readiness handling, vDPA management device registration, vDPA device creation, vDPA config ops, IRQ allocation, reset, and teardown.

Important APIs/types/functions: Defines `struct octep_pf`, `struct octep_vdpa`, and `struct octep_vdpa_mgmt_dev`. The `octep_vdpa_ops` table implements feature negotiation, status, reset, vq address/size/ready/state/callbacks, notification area, config reads, and device/vendor IDs. `octep_vdpa_probe_pf()` and `octep_vdpa_probe_vf()` split PF/VF lifecycle. `octep_vdpa_setup_task()` waits for firmware BAR initialization, maps caps, reads hardware capabilities, and registers `vdpa_mgmt_dev`. `octep_sriov_enable()` assigns VF BAR windows and signals ready signatures.

Control flow: PF probe enables PCI, maps the mailbox BAR, computes VF stride/device ID, shrinks the PF BAR resource window, and exposes SR-IOV configuration. Enabling VFs calls PCI SR-IOV, finds VFs by Cavium vendor/device, assigns BAR space out of the PF aperture, then writes per-VF ready signatures. VF probe enables DMA, maps mailbox BAR, allocates management state, and schedules setup work. The setup work waits up to 5 seconds for `OCTEP_DEV_READY_SIGNATURE`, maps caps, reads number of callback interrupts, calls `octep_hw_caps_read()`, then registers the management device. `dev_add` allocates `struct octep_vdpa`, filters provisioned features, validates mandatory features, names the device, and registers it with the vDPA bus.

State and persistence: Runtime state is in PCI driver data, `octep_hw`, per-VQ callbacks, IRQ vector arrays, atomic setup status, and firmware/MMIO. Reset clears callbacks and config callback, resets device status, and releases IRQs if the driver had reached `DRIVER_OK`.

Dependencies and integration points: Integrates with PCI core, SR-IOV, vDPA management bus, Octeon hardware helpers, virtio IDs, IOMMU/DMA mask, MSI-X interrupts, and kernel workqueues. Uses `_vdpa_register_device()` because management `dev_add` runs under vDPA's global device lock.

Risks: VF readiness is asynchronous; removal must cancel setup work before unregistering. PF BAR shrink/expand manipulates PCI resources and is platform-sensitive. IRQ handler maps shared interrupt vectors to queues by vector arithmetic and stops after first matching callback notification. `kick_vq` is intentionally unsupported; data-bearing kicks are required.

Test signals: Exercise PF probe, SR-IOV enable/disable, VF probe readiness timeout and success, netlink `vdpa dev add/del`, feature filtering, reset during setup, IRQ callback delivery, config change callback on ISR, and packed-ring vq state mailbox migration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_main.c -->
