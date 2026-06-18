# sources/distributed-fs/ceph-client/drivers/virtio/virtio_anchor.c

## Purpose
`virtio_anchor.c` provides a small anchor module and exported callback used to decide whether a virtio device must negotiate restricted memory access. It lets external code replace the global check while keeping a default no-restriction behavior.

## Important APIs, types, and functions
The exports are `virtio_require_restricted_mem_acc`, which always returns true, and `virtio_check_mem_acc_cb`, a function pointer initialized to `virtio_no_restricted_mem_acc`. `virtio.c` calls `virtio_check_mem_acc_cb` during feature validation.

## Control flow
By default, virtio feature validation does not require restricted memory access. If another subsystem assigns `virtio_check_mem_acc_cb` to a stricter callback, `virtio_features_ok` requires `VIRTIO_F_VERSION_1` and `VIRTIO_F_ACCESS_PLATFORM` for matching devices.

## State and persistence
The only state is the exported global callback pointer. It persists while the anchor object is loaded and affects all future virtio feature checks.

## Dependencies and integration points
The file depends on `linux/virtio.h` and `linux/virtio_anchor.h`. Its integration point is the virtio core feature negotiation path, especially platforms that require device DMA to go through restricted or translated memory access.

## Risks and test signals
Risks include unsynchronized callback replacement, global policy affecting unrelated devices, and failing legacy devices when a strict callback is installed. Test signals include booting with default callback, installing a restricted-memory callback, validating rejection of devices lacking `VERSION_1` or `ACCESS_PLATFORM`, and module dependency/load-order checks.
