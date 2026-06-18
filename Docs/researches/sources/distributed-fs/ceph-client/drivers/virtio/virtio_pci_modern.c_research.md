# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern.c

## Purpose
`virtio_pci_modern.c` adapts virtio 1.x PCI capabilities to the generic virtio config API. It handles extended feature negotiation, modern config access, vring activation, queue reset, shared-memory capabilities, admin virtqueue initialization/execution, SR-IOV member admin commands, and installation of modern transport callbacks into `struct virtio_pci_device`.

## Important APIs, types, and functions
- `vp_get_features()`, `vp_finalize_features()`, `vp_transport_features()`, and `vp_check_common_size()` negotiate modern features and validate common config size for optional fields.
- `vp_get()`, `vp_set()`, `vp_generation()`, `vp_get_status()`, `vp_set_status()`, and `vp_reset()` implement modern config ops.
- `setup_vq()`, `vp_active_vq()`, `vp_modern_find_vqs()`, `del_vq()`, `vp_modern_disable_vq_and_reset()`, and `vp_modern_enable_vq_after_reset()` manage modern virtqueues.
- `vp_modern_avq_done()`, `virtqueue_exec_admin_cmd()`, `vp_modern_admin_cmd_exec()`, and admin initialization helpers implement the admin virtqueue.
- Exported admin helpers include `virtio_pci_admin_has_dev_parts()`, `virtio_pci_admin_mode_set()`, object create/destroy, metadata get, device-parts get, and device-parts set.
- `vp_get_shm_region()` exposes shared-memory capability regions.
- `virtio_pci_modern_probe()` and `virtio_pci_modern_remove()` connect to the low-level modern device layer.

## Control flow
Modern probe calls `vp_modern_probe()`, chooses config ops with or without device-specific config space, installs callbacks, copies ISR/id, and initializes the admin VQ lock. Feature finalization lets vring and PCI transport code consume features, requires `VIRTIO_F_VERSION_1`, validates optional common config fields for notification data, ring reset, and admin VQ, then writes the negotiated feature array. When DRIVER_OK is set, `vp_modern_avq_activate()` queries supported admin commands, negotiates the command subset the driver can use, queries supported capabilities, and enables device-parts object limits when available.

Queue setup validates queue index/availability, creates a vring, writes queue size and descriptor/driver/device addresses, programs MSI-X if used, maps the queue notification location, and delays queue-enable until all queues are created. Queue reset removes the queue from interrupt lists, optionally breaks hardened notifications, synchronizes exclusive IRQs, waits for hardware reset completion in the low-level helper, then reactivates and relinks the queue on enable. Device reset writes status 0, waits until the device reports 0, completes unused admin commands with `-EIO`, and synchronizes vectors.

Admin command execution builds a header scatterlist, optional data, status buffer, and optional result buffer, adds them to the admin virtqueue under a spinlock, kicks, waits for completion, and maps admin status to Linux errors. Device-parts exported helpers resolve a VF to its PF virtio device, construct SR-IOV group admin commands, manage resource object ids with an IDA, and copy returned sizes/results to callers.

## State and persistence behavior
Persistent state lives in `struct virtio_pci_device` and its `mdev`/`admin_vq` members: mapped capability windows, queue callbacks, admin command bitmaps, supported capability bitmap, device-parts object limit, and allocated object ids. Queue reset mutates `vq->reset` and queue list membership. Device-parts object ids persist in the IDA until destroy or failed create cleanup. No disk persistence exists.

## Dependencies and integration points
This file depends on the low-level modern capability helpers in `virtio_pci_modern_dev.c`, common PCI queue/vector code, virtio ring, admin command UAPI structures, scatterlists, completions, PCI SR-IOV helpers, and shared-memory capability definitions. It exports admin APIs consumed by other VF/PF management paths.

## Risks and test signals
Risks include admin virtqueue deadlock or starvation on `-ENOSPC`, completing commands during reset, optional common config fields shorter than negotiated features, queue notification mapping failures, queue reset/list races with interrupts, IDA leaks on object lifecycle errors, unsupported admin status propagation, and SR-IOV PF/VF lifetime assumptions. Test signals include modern-only and transitional probe, extended feature negotiation, missing `VERSION_1` rejection, notification-data and ring-reset paths, admin VQ command list negotiation, device-parts object create/get/set/destroy, shared-memory region validation, queue reset disable/enable, MSI-X and INTx queue creation, and reset with pending admin commands.
