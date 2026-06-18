# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sysfs.c

## Purpose

`v3d_sysfs.c` exposes a read-only `gpu_stats` sysfs attribute for V3D queue activity. It formats per-queue job counts and accumulated runtime so users and test tooling can inspect GPU scheduler utilization outside debugfs.

## Important APIs, Types, and Functions

- `gpu_stats_show`: sysfs show method that samples `local_clock`, iterates `V3D_MAX_QUEUES`, calls `v3d_get_stats`, and writes tab-separated lines with queue name, timestamp, completed jobs, and runtime.
- `DEVICE_ATTR_RO(gpu_stats)`: declares the read-only device attribute.
- `v3d_sysfs_init` and `v3d_sysfs_destroy`: create and remove the attribute group from the DRM device kobject.

## Control Flow

Driver setup calls `v3d_sysfs_init` with the device. Reads call `gpu_stats_show`, which obtains the DRM device from `dev_get_drvdata`, converts it to `struct v3d_dev`, emits a header, and emits one row per queue. Teardown calls `v3d_sysfs_destroy` to remove the group.

## State and Persistence Behavior

The file stores no independent state. It reads persistent queue stats maintained by scheduler code and reports a single timestamp for the whole sample. Runtime values include active in-flight time as of the sampled timestamp if `v3d_get_stats` accounts for active jobs.

## Dependencies and Integration Points

It depends on Linux sysfs, `local_clock`, `v3d_get_stats`, `v3d_queue_to_string`, and the V3D device model. It is an observability endpoint for the scheduler and complements tracepoints/debugfs.

## Risks and Edge Cases

- The fixed sysfs buffer is assumed large enough for all queue rows; adding many queues would require checking output length.
- Stats for uninitialized optional queues still rely on `v3d->queue[queue].stats` being valid.
- Timestamp is in local-clock nanoseconds, not wall time, which is correct for runtime correlation but may surprise scripts.

## Test Signals

Read `/sys/.../gpu_stats` after driver init, submit jobs to several queues, verify the header and queue names, confirm job counts/runtimes increase monotonically, and check that create/remove paths do not leave stale sysfs files across bind/unbind.
