<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dump.h

## Purpose
Defines the binary error-dump file format used by Lima to expose saved failed GPU tasks through sysfs.

## Important APIs, types, and functions
Constants include version numbers, magic `LIMA_DUMP_MAGIC`, task IDs for GP/PP, and chunk IDs for frame, buffer, process name, and process ID. Structures include `lima_dump_head`, `lima_dump_task`, `lima_dump_chunk`, `lima_dump_chunk_buffer`, and `lima_dump_chunk_pid`.

## Control flow
No executable flow. Scheduler error code serializes data using this layout; `lima_drv.c` reads and clears it through the binary sysfs attribute.

## State and persistence
Dump headers and task/chunk records persist in `lima_device` error-task storage until cleared or driver removal.

## Dependencies and integration points
Uses fixed-width Linux types to define a stable binary layout consumed by debugging tools.

## Risks
Changing structure layout or IDs breaks userspace dump decoders. Size fields must be validated by producers and readers to avoid truncated or malformed dumps.

## Test signals
Trigger GPU task errors, read `/sys/.../error`, validate magic/version/chunk layout, and clear by writing the sysfs file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dump.h -->
