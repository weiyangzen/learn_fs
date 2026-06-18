## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_coredump.c

### Purpose
`ivpu_coredump.c` creates an Intel NPU device coredump containing a short header, firmware version, and firmware log buffers.

### Important APIs, Types, And Functions
`ivpu_dev_coredump()` computes a dump size from fixed header space, firmware version header size, and critical/verbose log BO sizes; fills a vmalloc buffer through a DRM coredump printer; prints firmware logs with `ivpu_fw_log_print()`; and submits the buffer through `dev_coredumpv()`.

### Control Flow
On failure paths such as firmware boot failure, callers invoke `ivpu_dev_coredump()`. It allocates the dump buffer, writes metadata/logs sequentially via `drm_printf()`, and hands ownership to devcoredump. Allocation failure silently skips dump generation.

### State, Persistence, And Dependencies
The dump is persistent through the devcoredump interface until consumed or expired. It depends on firmware BOs already existing and on firmware log buffer headers being parseable by `ivpu_fw_log_print()`.

### Integration Points
It integrates with firmware boot diagnostics, `CONFIG_DEV_COREDUMP`, DRM printers, firmware metadata, and log BOs allocated by `ivpu_fw_mem_init()`.

### Risks
The dump size is a worst-case allocation; log printer output may be smaller than allocated. If firmware log buffers are corrupted, log parsing can omit sections. Coredump generation must not be called after firmware BOs are freed.

### Test Signals
Force boot failure or recovery paths and verify devcoredump contains the header, firmware version, critical log, and verbose log without overrun or null dereference.
