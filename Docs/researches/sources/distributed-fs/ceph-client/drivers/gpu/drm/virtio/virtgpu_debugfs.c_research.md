<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_debugfs.c

## Purpose
`virtgpu_debugfs.c` exposes VirtIO GPU feature, fence, and host-visible memory information through DRM debugfs files.

## Important APIs, Types, and Functions
Key functions are `virtio_gpu_features()`, `virtio_gpu_debugfs_irq_info()`, `virtio_gpu_debugfs_host_visible_mm()`, and `virtio_gpu_debugfs_init()`. Helpers format booleans and integers. Debugfs entries are `virtio-gpu-features`, `virtio-gpu-irq-fence`, and `virtio-gpu-host-visible-mm`.

## Control Flow
DRM debugfs init registers the info files for a minor. Reads recover `virtio_gpu_device` from `minor->dev->dev_private`, print negotiated features, capsets/scanouts, last/current fence IDs, or dump the DRM MM allocator for the host-visible region.

## State and Persistence Behavior
The file exposes live driver state but owns none. Output reflects current feature flags, fence counters, and host-visible MM allocations.

## Dependencies and Integration Points
It depends on DRM debugfs, seq_file, string yes/no helpers, DRM printers, and `virtgpu_drv.h`. It is wired into `struct drm_driver` under `CONFIG_DEBUG_FS`.

## Risks
Debugfs reads are diagnostic and mostly lockless; host-visible MM dumping should be safe with DRM MM expectations but can race with allocations if not externally protected. Missing `dev_private` during teardown would be problematic if reads race unplug.

## Test Signals
Debugfs smoke tests should read all entries with virgl/blob/host-visible combinations and during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_debugfs.c -->
