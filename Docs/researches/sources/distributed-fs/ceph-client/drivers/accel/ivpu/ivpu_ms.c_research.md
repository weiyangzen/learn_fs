<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.c

### Purpose
`ivpu_ms.c` implements metric streamer ioctls for collecting firmware-generated telemetry samples into kernel-managed BO buffers and copying sample or descriptor data back to userspace.

### Important APIs, Types, And Functions
Public ioctl handlers are `ivpu_ms_start_ioctl()`, `ivpu_ms_get_data_ioctl()`, `ivpu_ms_stop_ioctl()`, and `ivpu_ms_get_info_ioctl()`. Cleanup helpers are `ivpu_ms_cleanup()` and `ivpu_ms_cleanup_all()`. Internal helpers find instances by metric mask, copy leftover bytes, swap active/inactive buffers, allocate a reusable info BO, and free streamer instances.

### Control Flow
Start validates metric mask, read-period samples, and a minimum sampling period, runtime-resumes the device, serializes on `file_priv->ms_lock`, rejects duplicate masks, queries sample size with JSM, computes a double-buffered BO size, allocates a global cached mappable BO, starts firmware collection, returns sample and max-data sizes, and links the instance into the file context. Data retrieval either queries bytes available or switches firmware to the inactive buffer, swaps active/inactive pointers, and copies buffered plus leftover data to userspace. Stop finds the instance, sends metric stop, frees the BO, and removes it from the list.

### State, Persistence, And Dependencies
Per-file state is `ms_instance_list`, `ms_lock`, and optional `ms_info_bo`. Each instance stores metric mask, global BO, buffer size, active/inactive VPU addresses and CPU pointers, and leftover copy position. Dependencies include runtime PM, `ivpu_bo_create_global()`, JSM metric commands, and DRM ioctl UAPI structures.

### Integration Points
PM reset cleanup calls `ivpu_ms_cleanup_all()` to stop streams and free BOs. Metric descriptors and sample streams are firmware ABI objects defined in `vpu_jsm_api.h`. Userspace discovers metric info through `get_info` and starts streams through UAPI ioctls.

### Risks
Metric masks uniquely identify instances, so overlapping domains are delegated to firmware validation. Buffer sizing multiplies user read period, sample size, multiplier, and buffer count; overflow is not explicit before `PAGE_ALIGN()`, so large inputs should be reviewed carefully. `ivpu_ms_get_info_ioctl()` does not runtime-resume before JSM calls, unlike start/data/stop, so callers rely on surrounding device state or JSM availability. Copying from cached BO memory assumes firmware coherency and JSM update ordering.

### Test Signals
Test invalid masks and sample periods, duplicate start, start/get-data/stop cycles, zero-size get-data availability queries, undersized descriptor buffers returning `-ENOSPC`, reset cleanup of active streams, large read-period rejection by global range size, and repeated partial reads that exercise leftover handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.c -->
