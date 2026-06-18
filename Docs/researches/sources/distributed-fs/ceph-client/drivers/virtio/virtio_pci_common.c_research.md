# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.c

## Purpose
`virtio_pci_common.c` is the shared PCI transport driver for legacy and modern virtio-pci devices. It owns PCI probing/removal, common interrupt and virtqueue dispatch, MSI-X/INTx vector allocation policy, queue affinity, power-management reset handling, SR-IOV enablement, and PCI error reset callbacks.

## Important APIs, types, and functions
- `vp_find_vqs()`, `vp_del_vqs()`, `vp_notify()`, `vp_synchronize_vectors()`, `vp_bus_name()`, `vp_set_vq_affinity()`, and `vp_get_vq_affinity()` are shared `virtio_config_ops` helpers used by legacy and modern transports.
- `vp_request_msix_vectors()`, `vp_find_vqs_msix()`, `vp_find_vqs_intx()`, and `vp_find_one_vq_msix()` implement the vector fallback ladder.
- Interrupt handlers `vp_interrupt()`, `vp_config_changed()`, `vp_vring_interrupt()`, and `vp_vring_slow_path_interrupt()` route INTx/MSI-X events.
- `virtio_pci_probe()` chooses modern vs legacy probing, with `force_legacy` as an optional override.
- `virtio_pci_remove()`, PM callbacks, `virtio_pci_sriov_configure()`, and PCI reset handlers manage lifecycle beyond initial registration.
- `virtio_pci_vf_get_pf_dev()` exposes the PF virtio device for VF admin-command helpers.

## Control flow
Probe allocates `struct virtio_pci_device`, enables the PCI device, attempts modern or legacy transport setup, sets bus mastering, and registers the embedded virtio device. Modern setup is preferred unless `force_legacy` requests legacy first; transitional devices can fall back either way depending on capabilities and BAR availability. Removal marks the virtio device broken on surprise removal, disables SR-IOV, unregisters the virtio device, removes the selected transport, disables PCI, and releases the virtio device reference.

Virtqueue discovery first tries MSI-X with one vector per queue, then MSI-X with slow-path queues sharing the config vector, then MSI-X with one shared queue vector, then INTx. MSI-X setup always reserves a config vector first, optionally allocates a shared queue vector, and then creates requested virtqueues plus an admin virtqueue when the modern transport reports one. Queue info objects are linked onto normal or slow-path lists under `vp_dev->lock`, allowing interrupt handlers to iterate active callback queues safely. Teardown frees per-vq IRQs, config/shared IRQs, affinity masks, MSI-X allocations, queue info arrays, and transport-specific queue resources.

## State and persistence behavior
Persistent state is the `struct virtio_pci_device` allocated for each PCI function. It records whether legacy or modern transport is active, MMIO/PIO transport state in the union, ISR pointer, virtqueue lists, queue info array, admin VQ state, MSI-X names/masks/vector counts, INTx/MSI-X flags, and transport callbacks. The module parameter `force_legacy` is read-only after load. No disk persistence exists.

## Dependencies and integration points
This file depends on Linux PCI, MSI-X/IRQ APIs, virtio core, virtio ring, SR-IOV helpers, PM, and the legacy/modern transport-specific files. It is the actual `pci_driver` registered for Red Hat/Qumranet virtio PCI IDs and provides symbols consumed by admin legacy I/O and modern admin device-parts support.

## Risks and test signals
Risks include complex MSI-X fallback cleanup, queue list races with interrupts and queue reset, slow-path/admin queue vector sharing, affinity mask indexing, surprise removal, PM paths that skip reset when PCI PM reports no soft reset, and SR-IOV enablement while the virtio driver is not ready. Test signals include modern and legacy probe fallback, all MSI-X policy fallbacks, INTx operation, per-vq affinity changes, admin VQ creation, queue teardown with interrupts in flight, suspend/resume/freeze/thaw, PCI function reset, SR-IOV enable/disable gates, and surprise removal behavior.
