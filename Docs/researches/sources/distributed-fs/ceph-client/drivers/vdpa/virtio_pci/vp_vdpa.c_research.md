# sources/distributed-fs/ceph-client/drivers/vdpa/virtio_pci/vp_vdpa.c

## Purpose

`vp_vdpa.c` exposes modern virtio-pci devices through the vDPA framework. It probes only dynamically matched PCI ids, wraps the `virtio_pci_modern_device` accessors in `vdpa_config_ops`, registers a vDPA management device, and lets userspace instantiate a vDPA device over hardware virtqueues and notification BARs.

## Important APIs, Types, and Functions

`struct vp_vdpa` stores the `vdpa_device`, modern virtio-pci device pointer, per-vring notification/IRQ state, config callback, cached provisioned device features, MSI-X vector counts, and queue count. `struct vp_vring` stores a notify pointer, physical notify address, callback, MSI-X name, and IRQ. `struct vp_vdpa_mgmtdev` binds one PCI device to a vDPA management device and its active vDPA instance.

The core vDPA callbacks are `vp_vdpa_get_device_features()`, `vp_vdpa_set_driver_features()`, `vp_vdpa_get_status()`, `vp_vdpa_set_status()`, `vp_vdpa_reset()`, queue address/size/ready callbacks, config read/write callbacks, notification/kick callbacks, and `vp_vdpa_get_vq_irq()`. `vp_vdpa_request_irq()` allocates MSI-X vectors after callbacks are known; `vp_vdpa_free_irq()` detaches vectors and frees IRQs.

## Control Flow

PCI probe allocates the management wrapper, a `virtio_pci_modern_device`, and a two-entry virtio id table, enables the PCI device, calls `vp_modern_probe()`, fills management-device ids/features/max-vqs, sets bus mastering, and registers the management device. `dev_add` allocates a `vp_vdpa`, assigns the PCI device as `vmap.dma_dev`, reads queue count and device features, optionally applies a user-provisioned feature subset, maps every queue notify area with `vp_modern_map_vq_notify()`, initializes IRQ fields to `VIRTIO_MSI_NO_VECTOR`, and registers the vDPA device.

Queue operations write directly to modern virtio-pci common/notify registers. Kicks write either 16-bit queue id or 32-bit notification data to the queue's notify area. Config reads loop on `config_generation` until stable. When the vDPA status transitions to `DRIVER_OK`, `vp_vdpa_request_irq()` counts queues with callbacks, allocates one MSI-X vector per such queue plus one config vector, requests IRQs, and programs queue/config vectors. Reset writes status zero and frees IRQ resources if the device had reached `DRIVER_OK`.

## State and Persistence Behavior

Runtime state is held in the PCI driver data and active `vp_vdpa` instance. Hardware state is in the virtio-pci registers: status, feature negotiation, queue size/address/enable, queue vectors, config vector, and notify BAR writes. `device_features` is cached so vDPA reports the provisioned subset rather than the raw hardware mask. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on the virtio-pci modern helper API, PCI MSI-X allocation, vDPA core, virtio ring/config definitions, and vDPA netlink management paths. It uses devres for IRQ-vector cleanup registration and devm allocations for vrings/IRQs. The PCI driver has a NULL static id table, so binding relies on dynamic ids or driver override.

## Risks and Edge Cases

Virtqueue state save is not supported by virtio-pci; `get_vq_state()` returns `-EOPNOTSUPP`, and `set_vq_state()` only accepts an initial split or packed state before a queue is enabled. This blocks live migration and start/stop semantics. IRQ allocation is deferred until `DRIVER_OK`, so callback registration order matters; failures in `vp_vdpa_request_irq()` leave status unchanged but emit `WARN_ON(1)`. `pci_alloc_irq_vectors()` is called with exact min/max; devices unable to provide the exact count fail. Config read bounds are assumed valid by callers.

## Test Signals

Test probe/remove with dynamic ids, feature-subset provisioning, queue notify mapping failures, `_vdpa_register_device()` failure, `DRIVER_OK` IRQ setup, reset IRQ teardown, queue callback and config callback delivery, notification-area reporting, packed and split initial state acceptance, and rejection of non-initial queue states. Build with `CONFIG_VP_VDPA=m` and exercise unbind/remove while a vDPA device is active.
