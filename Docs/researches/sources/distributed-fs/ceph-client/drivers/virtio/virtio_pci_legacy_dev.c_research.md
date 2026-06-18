# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy_dev.c

## Purpose
`virtio_pci_legacy_dev.c` is the exported low-level access layer for legacy virtio PCI devices. It validates legacy PCI IDs/revision, maps BAR0, configures DMA masks, and exposes helpers for legacy feature, status, queue, and MSI-X registers.

## Important APIs, types, and functions
- `vp_legacy_probe()` validates device id range `0x1000..0x103f`, ABI revision, DMA masks, BAR0 ownership, and maps the legacy I/O region.
- `vp_legacy_remove()` unmaps BAR0 and releases the region.
- `vp_legacy_get_features()`, `vp_legacy_get_driver_features()`, and `vp_legacy_set_features()` access host/guest feature registers.
- `vp_legacy_get_status()` and `vp_legacy_set_status()` access the status register.
- `vp_legacy_queue_vector()` and `vp_legacy_config_vector()` program MSI-X vectors and read back the result.
- `vp_legacy_set_queue_address()`, `vp_legacy_get_queue_enable()`, and `vp_legacy_get_queue_size()` select a queue and access queue PFN/size registers.

## Control flow
Probe is called after PCI enablement by common code. It rejects non-legacy IDs or wrong ABI revision, tries a 64-bit DMA mask with a coherent mask constrained by the legacy queue PFN width, falls back to 32-bit DMA, requests BAR0, maps it, sets `isr`, and derives the virtio id from PCI subsystem ids. Register helpers all perform direct I/O to offsets from `ldev->ioaddr`, selecting a queue before queue-specific access.

## State and persistence behavior
Persistent state is limited to `struct virtio_pci_legacy_device`: PCI device pointer, mapped I/O base, ISR address, and virtio id. The hardware registers hold negotiated features, status, queue PFNs, and MSI-X vector assignments until reset/remove.

## Dependencies and integration points
It depends on Linux PCI, module APIs, public virtio PCI legacy definitions, and the legacy transport glue in `virtio_pci_legacy.c`. The helper symbols are exported GPL so other kernel code can use the same low-level legacy abstraction.

## Risks and test signals
Risks include BAR0 request conflicts, DMA mask warnings that continue despite possible runtime failure, queue selection races if callers do not serialize queue-specific register access, 32-bit PFN limits, and strict legacy revision filtering. Test signals include probe rejection for non-legacy IDs/revisions, BAR request/unmap cleanup, feature/status read-write, queue size and enable detection, queue PFN programming, MSI-X vector readback, and DMA mask fallback behavior.
