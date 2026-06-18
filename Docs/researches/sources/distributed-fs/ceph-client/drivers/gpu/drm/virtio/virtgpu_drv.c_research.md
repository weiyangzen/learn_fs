<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.c

## Purpose
`virtgpu_drv.c` is the VirtIO GPU module/virtio-driver entry point and DRM driver definition. It handles probe/remove/shutdown/config-change, PCI VGA quirks, feature negotiation table, module parameter modeset gating, and DRM driver callbacks.

## Important APIs, Types, and Functions
Important functions are `virtio_gpu_probe()`, `virtio_gpu_remove()`, `virtio_gpu_shutdown()`, `virtio_gpu_config_changed()`, `virtio_gpu_driver_init()`, and `virtio_gpu_driver_exit()`. It defines virtio ID/features tables, `virtio_gpu_driver`, DRM fops, and the `struct drm_driver driver`.

## Control Flow
Module init may acquire legacy VGA arbitration for virtio-vga, registers the virtio driver, then releases VGA resources. Probe rejects firmware-only or disabled modeset cases, allocates a DRM device on the parent DMA-capable device, applies PCI aperture quirks for virtio-vga, sets max DMA segment size, calls `virtio_gpu_init()`, registers DRM, and starts DRM clients. Remove unplugs DRM, atomic-shuts down, deinitializes virtio state, and drops the DRM reference. Config change schedules work in `virtgpu_kms.c`.

## State and Persistence Behavior
Module parameter `modeset` persists for module lifetime. The DRM device persists from probe until remove/release. Virtio feature bits are negotiated once per device and copied into `virtio_gpu_device` during init.

## Dependencies and Integration Points
The file integrates virtio core, PCI/VGA aperture handling, DRM core/client/fbdev shmem, atomic shutdown, debugfs, GEM object creation, PRIME import, ioctls, and lifecycle functions implemented in other VirtIO GPU files.

## Risks
Probe uses the parent device for DRM DMA behavior, which is intentional but sensitive to virtio transport assumptions. Feature table exposes virgl only on little-endian builds. Shutdown only unplugs DRM and stops further device talk; full cleanup happens on remove. Modeset gating must align with firmware-driver policy.

## Test Signals
Tests should cover virtio-gpu-pci and virtio-vga probe, aperture removal, modeset parameter values, feature negotiation, config-change work scheduling, remove/unplug races, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.c -->
