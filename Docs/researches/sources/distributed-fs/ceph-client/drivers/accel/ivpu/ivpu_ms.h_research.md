<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.h

### Purpose
`ivpu_ms.h` declares metric streamer instance state and ioctl/cleanup APIs for ivpu telemetry collection.

### Important APIs, Types, And Functions
`struct ivpu_ms_instance` stores the BO, list node, metric mask, buffer sizes, active/inactive VPU addresses and CPU pointers, and leftover copy bookkeeping. The header exports start/stop/get-data/get-info ioctl handlers and per-file/all-context cleanup.

### Control Flow
The header has no executable flow; it defines the state consumed under `file_priv->ms_lock`.

### State, Persistence, And Dependencies
Instances persist per open DRM file until stopped, file cleanup, or PM reset cleanup. Dependencies are list handling, ivpu BOs, and DRM device/file types.

### Integration Points
Used by ioctl registration, file cleanup, and PM reset recovery. Firmware metric payload layout is defined separately in `vpu_jsm_api.h`.

### Risks
The active/inactive pointer fields must remain synchronized with firmware buffer switching. Any consumer added outside the lock can race with cleanup.

### Test Signals
Build coverage plus stream lifecycle tests, reset cleanup tests, and leak checks after file close are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.h -->
