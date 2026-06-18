# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_legacy.c

## Purpose
`virtio_pci_legacy.c` adapts legacy virtio PCI devices to the generic virtio config API. It wraps the low-level legacy register helpers, creates legacy vrings using a 32-bit queue PFN, handles legacy config/status operations, and installs legacy transport callbacks into `struct virtio_pci_device`.

## Important APIs, types, and functions
- `vp_get_features()` and `vp_finalize_features()` negotiate the legacy 32-bit feature word.
- `vp_get()` and `vp_set()` access byte-oriented device-specific config space at `VIRTIO_PCI_CONFIG_OFF(msix_enabled)`.
- `vp_get_status()`, `vp_set_status()`, and `vp_reset()` read/write legacy device status and flush reset effects.
- `setup_vq()` creates and activates one legacy virtqueue and programs optional MSI-X queue vectors.
- `del_vq()` disables the queue vector, clears queue address, and deletes the vring.
- `virtio_pci_legacy_probe()` and `virtio_pci_legacy_remove()` bridge common PCI code to low-level legacy probe/remove.

## Control flow
Legacy probe calls `vp_legacy_probe()`, copies the ISR pointer and virtio id, assigns legacy `virtio_config_ops`, installs queue/config-vector callbacks, and marks the device legacy. Queue setup checks queue availability and inactive status, creates a vring with legacy alignment, validates that the descriptor address fits in a 32-bit PFN, writes the queue address, stores the notify register in `vq->priv`, and programs MSI-X if requested. Reset writes status 0, reads status to flush, then synchronizes all vectors.

## State and persistence behavior
The file stores no independent global state. Per-device state lives in `vp_dev->ldev`, callback pointers, `is_legacy`, `isr`, and per-queue `virtio_pci_vq_info`. Legacy config offsets depend on whether MSI-X is enabled because the legacy ABI moves device config space when MSI-X registers are present.

## Dependencies and integration points
It depends on `virtio_pci_common.h`, public `linux/virtio_pci_legacy.h`, the low-level helper functions from `virtio_pci_legacy_dev.c`, and common queue/interrupt code from `virtio_pci_common.c`. Upper virtio drivers see it only through `virtio_config_ops`.

## Risks and test signals
Risks include the 32-bit PFN limitation, only 32 feature bits, byte-wise config accesses, config offset changes with MSI-X, legacy memory barrier assumptions, and cleanup after vector programming failure. Test signals include transitional legacy probe, feature negotiation rejecting high bits, queue setup below and above PFN limits, MSI-X and INTx operation, config get/set offsets with MSI-X enabled, reset flushing callbacks, and remove cleanup.
