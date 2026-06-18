<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Kconfig

## Purpose
`virtio/Kconfig` declares VirtIO GPU support and the optional KMS modesetting subfeature. It controls build availability for virtual GPU devices used by QEMU/KVM/Xen-style VMMs.

## Important APIs, Types, and Functions
Symbols are `DRM_VIRTIO_GPU` and `DRM_VIRTIO_GPU_KMS`. The main driver depends on `DRM`, `VIRTIO_MENU`, and `MMU`, selects `VIRTIO`, DRM client/KMS/shmem helpers, and `VIRTIO_DMA_SHARED_BUFFER`. KMS depends on the main symbol and defaults to enabled.

## Control Flow
Kconfig decides whether the `virtio-gpu` object is built. If KMS is disabled, runtime init masks mode-setting/atomic features and operates as a render/headless device.

## State and Persistence Behavior
There is no runtime state in this file; configuration persists in kernel/module capabilities.

## Dependencies and Integration Points
The selections match runtime use of virtqueues, shmem GEM, dma-buf UUID sharing, DRM clients, and KMS helpers.

## Risks
Disabling KMS changes driver feature bits and userspace-visible behavior. Missing selected helpers would cause link failures. `MMU` is required for GEM mmap/shmem behavior.

## Test Signals
Builds with KMS enabled/disabled and module/built-in configurations validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Kconfig -->
