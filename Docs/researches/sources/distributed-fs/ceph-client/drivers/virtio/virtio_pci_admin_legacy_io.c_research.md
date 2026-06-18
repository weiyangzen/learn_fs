# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_admin_legacy_io.c

## Purpose
`virtio_pci_admin_legacy_io.c` exports helper APIs that let callers access a VF's legacy virtio common/device configuration and notification information through the PF's modern virtio admin virtqueue. It is used when a modern SR-IOV PF supports admin commands that proxy legacy I/O semantics for member devices.

## Important APIs, types, and functions
- `virtio_pci_admin_has_legacy_io()` checks that the PF virtio device exists, negotiated `VIRTIO_F_ADMIN_VQ`, and advertised all legacy admin command bits.
- `virtio_pci_admin_legacy_common_io_write()` and `virtio_pci_admin_legacy_device_io_write()` wrap `virtio_pci_admin_legacy_io_write()` for common and device config writes.
- `virtio_pci_admin_legacy_common_io_read()` and `virtio_pci_admin_legacy_device_io_read()` wrap `virtio_pci_admin_legacy_io_read()` for reads.
- `virtio_pci_admin_legacy_io_notify_info()` requests legacy queue notify BAR/offset information matching caller-specified BAR flags.
- All exported functions are `EXPORT_SYMBOL_GPL` APIs for other virtio PCI/SR-IOV code.

## Control flow
Each operation starts from a VF `struct pci_dev`, resolves the owning PF's `struct virtio_device` via `virtio_pci_vf_get_pf_dev()`, obtains the VF group member id with `pci_iov_vf_id() + 1`, builds a `struct virtio_admin_cmd`, attaches data and/or result scatterlists, and executes the command through `vp_modern_admin_cmd_exec()`. Read commands use a small data descriptor for offset and a caller-provided result buffer. Write commands allocate a variable-sized payload containing offset plus register bytes. Notify-info parses returned entries until an END flag or a matching flag entry is found.

## State and persistence behavior
This file owns no persistent state. It allocates temporary command payload/result structures per call and depends on the PF admin virtqueue state stored in `struct virtio_pci_device`. The caller is explicitly responsible for serializing access for a given member device, so these helpers do not add per-VF locking.

## Dependencies and integration points
It depends on `linux/virtio_pci_admin.h`, SR-IOV PCI helpers, `virtio_pci_common.h`, and the modern admin command executor in `virtio_pci_modern.c`. It integrates PF-controlled admin virtqueue functionality with VF-oriented legacy configuration access.

## Risks and test signals
Risks include missing caller serialization, PF/VF lifetime races, unsupported command bitmaps, invalid VF ids, result parsing that returns `-ENOENT` if flags do not match, and propagation of admin command status values as negative errors. Test signals include positive/negative `virtio_pci_admin_has_legacy_io()`, read/write round trips for common and device config offsets, invalid VF handling, notify-info lookup for each BAR flag, unsupported command rejection, and concurrent caller behavior under external locking.
