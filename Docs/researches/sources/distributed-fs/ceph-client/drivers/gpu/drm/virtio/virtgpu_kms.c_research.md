<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_kms.c

## Purpose
`virtgpu_kms.c` initializes and tears down per-device VirtIO GPU state, virtqueues, feature flags, host-visible memory, capsets, display info, workqueues, IDs, locks, KMS, and per-file virgl contexts.

## Important APIs, Types, and Functions
Public functions include `virtio_gpu_init()`, `virtio_gpu_deinit()`, `virtio_gpu_release()`, `virtio_gpu_driver_open()`, and `virtio_gpu_driver_postclose()`. Important helpers are `virtio_gpu_config_changed_work_func()`, `virtio_gpu_init_vq()`, `virtio_gpu_get_capsets()`, and `virtio_gpu_cleanup_cap_cache()`.

## Control Flow
Init requires VirtIO 1.0, allocates `virtio_gpu_device`, initializes locks/IDAs/waitqueues/works/fence driver/lists, records negotiated features, reserves host-visible shared memory and initializes `drm_mm` if present, finds control and cursor virtqueues, allocates vbuffers, reads scanout/capset counts, disables KMS if configured or no scanouts, initializes modeset, marks device ready, queries capsets, EDIDs, and display info, then returns. Deinit flushes works, resets the virtio device, and deletes vqs. Release frees KMS EDIDs, vbuffers, cap caches, and host-visible MM. Open allocates per-file virgl context IDs only when virgl is enabled; postclose destroys host context and frees the ID.

## State and Persistence Behavior
This file owns initialization of persistent `virtio_gpu_device` state: feature flags, queues, pending lists, capsets, display info, fence timeline, work items, host-visible allocator, and per-file contexts. Deinit stops transport; release cleans managed allocations after DRM references drain.

## Dependencies and Integration Points
It depends on virtio config/vqs/rings, DRM managed allocation, KMS display init, vbuffer allocation from `virtgpu_vq.c`, capset/display/EDID commands, dma-fence contexts, IDA, workqueues, and host-visible shared-memory regions.

## Risks
Error paths before/after vq creation must free the right subset. `capset_id_mask |= 1 << id` uses an int literal and should be reviewed for IDs near 63. Feature logging and KMS masking must match user-visible getparam behavior. Device reset during deinit must race safely with outstanding fences/works.

## Test Signals
Probe failure injection at each resource step, KMS disabled builds, host-visible region allocation conflicts, capset invalid ID/timeouts, display-info waits, open/postclose context lifecycle, and remove while commands are pending validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_kms.c -->
