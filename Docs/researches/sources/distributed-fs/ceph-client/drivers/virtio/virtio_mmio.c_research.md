# sources/distributed-fs/ceph-client/drivers/virtio/virtio_mmio.c

## Purpose
`virtio_mmio.c` implements the memory-mapped virtio transport for platform devices. It maps a virtio-mmio register window, exposes it as a `struct virtio_device`, provides virtio config operations, creates vrings, handles the single transport interrupt, and supports device instantiation via platform resources, Device Tree, ACPI, or a command-line/module parameter.

## Important APIs, types, and functions
- `struct virtio_mmio_device` embeds `struct virtio_device` and stores the platform device, MMIO base, and transport version.
- `vm_get_features()`, `vm_finalize_features()`, `vm_get()`, `vm_set()`, `vm_generation()`, `vm_get_status()`, `vm_set_status()`, and `vm_reset()` implement config access.
- `vm_notify()` and `vm_notify_with_data()` write queue notifications.
- `vm_interrupt()` acknowledges config and vring interrupts and fans out to `virtio_config_changed()` and `vring_interrupt()`.
- `vm_setup_vq()`, `vm_find_vqs()`, `vm_del_vq()`, `vm_del_vqs()`, and `vm_synchronize_cbs()` manage virtqueues and IRQ lifetime.
- `vm_get_shm_region()` reads shared-memory region descriptors.
- `virtio_mmio_probe()` validates magic/version/device id, configures DMA masks, maps resources, and registers the virtio device.
- Optional `vm_cmdline_set()` and related helpers create platform devices from `virtio_mmio.device=`.

## Control flow
Probe allocates the transport wrapper, maps BAR-like platform resource 0, checks the magic value and version, rejects dummy device id 0, records vendor/device ids, initializes legacy guest page size for version 1, sets DMA masks, stores driver data, and calls `register_virtio_device()`. Feature negotiation reads high and low feature words, lets vring code consume transport features, enforces that version 2 devices negotiate `VIRTIO_F_VERSION_1`, and writes selected features back.

Queue discovery requests the platform IRQ once, optionally enables wakeup for Device Tree `wakeup-source`, then creates each named virtqueue in order. `vm_setup_vq()` selects the queue, rejects unavailable or already-active queues, creates a split vring, writes queue size and descriptor addresses, and activates either legacy `QUEUE_PFN` or modern descriptor/avail/used address registers. Interrupt handling reads and acknowledges the interrupt status before dispatching config and vring events.

## State and persistence behavior
State lasts for the platform device lifetime: MMIO base, transport version, registered virtio device, active vrings, and IRQ registration. No persistent storage exists. Command-line devices persist only as platform devices created under `vm_cmdline_parent` until module exit, where they are unregistered. Freeze/restore delegates to virtio core and rewrites version-1 guest page size on restore.

## Dependencies and integration points
The driver depends on platform resources, IRQ APIs, OF/ACPI matching, DMA masks, virtio core, virtio ring, and UAPI `virtio_mmio.h`. It is the transport used by virtio device drivers above it, and it must match the MMIO register ABI for legacy v1 and modern v2 devices.

## Risks and test signals
Risk areas include legacy v1 32-bit PFN limits, non-atomic 64-bit device config reads/writes split into two 32-bit accesses, missing or shared IRQ handling, dummy devices, bad command-line parsing, and devices that violate version/feature requirements. Test signals include DT/ACPI/cmdline probe, invalid magic/version rejection, v1 high-memory vring failure, v2 feature negotiation requiring `VERSION_1`, queue creation/deletion, config-change interrupts, vring interrupts, wakeup-source behavior, shared-memory region discovery, and freeze/restore.
